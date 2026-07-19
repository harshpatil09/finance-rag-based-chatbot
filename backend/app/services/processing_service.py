import os
import uuid
from sqlalchemy.orm import Session

from app.cores.config import settings
from app.models.report import Report, ReportStatus
from app.models.chunk import DocumentChunk
from app.services.pdf_parser import parse_pdf
from app.services.chunker import split_chunks
from app.services.embedding_service import embed_batch
from app.services.vector_service import ensure_collection_exists, upsert_chunks
from app.services.insights_service import extract_insights


def process_report(report_id: str, db: Session) -> dict:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise ValueError(f"Report {report_id} not found")

    report.status = ReportStatus.processing
    db.commit()

    try:
        pdf_path = os.path.join(settings.UPLOAD_DIR, report.stored_filename)
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Step 1 — Parse PDF into raw chunks
        raw_chunks = parse_pdf(pdf_path)

        # Step 2 — Split large chunks into smaller pieces
        chunks = split_chunks(raw_chunks)

        # Step 3 — Save text chunks to MySQL first (get stable IDs)
        db.query(DocumentChunk).filter(
            DocumentChunk.report_id == report_id
        ).delete()

        db_chunks = []
        chunk_ids = []
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)
            db_chunks.append(DocumentChunk(
                id=chunk_id,
                report_id=report_id,
                content=chunk.content,
                chunk_type=chunk.chunk_type,
                section=chunk.section,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                token_count=len(chunk.content.split())
            ))

        db.bulk_save_objects(db_chunks)
        db.commit()

        # Step 4 — Generate embeddings for all chunks in one batch call
        # Batch is much faster than embedding one by one
        print(f"Generating embeddings for {len(chunks)} chunks...")
        texts = [c.content for c in chunks]
        embeddings = embed_batch(texts)

        # Step 5 — Store vectors in Qdrant with metadata payload
        ensure_collection_exists()

        qdrant_points = []
        for i, (chunk, chunk_id, embedding) in enumerate(
            zip(chunks, chunk_ids, embeddings)
        ):
            qdrant_points.append({
                "id": chunk_id,
                "vector": embedding,
                "payload": {
                    # Metadata stored in Qdrant alongside the vector.
                    # This lets us filter searches by report, section, type
                    # without needing to join back to MySQL for basic filtering.
                    "report_id": report_id,
                    "company": report.company_name,
                    "quarter": report.quarter,
                    "section": chunk.section,
                    "chunk_type": chunk.chunk_type,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content   # store content here too for fast retrieval
                }
            })

        upserted = upsert_chunks(qdrant_points)
        print(f"Stored {upserted} vectors in Qdrant")

        # Step 6 — Mark report as ready
        report.status = ReportStatus.ready
        db.commit()

        text_count = sum(1 for c in chunks if c.chunk_type == "text")
        table_count = sum(1 for c in chunks if c.chunk_type == "table")
        
        # Step 7 — Extract insights (non-critical — don't fail pipeline if this fails)
        try:
            print(f"Extracting financial insights for report {report_id}...")
            extract_insights(report_id, db)
            print("Insights extracted successfully")
        except Exception as insight_error:
            print(f"Insights extraction failed (non-critical): {insight_error}")

        return {
            "report_id": report_id,
            "total_chunks": len(chunks),
            "text_chunks": text_count,
            "table_chunks": table_count,
            "vectors_stored": upserted,
            "status": "ready"
        }

    except Exception as e:
        report.status = ReportStatus.failed
        db.commit()
        raise e