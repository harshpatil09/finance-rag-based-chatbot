import os
from sqlalchemy.orm import Session

from app.cores.config import settings
from app.models.report import Report, ReportStatus
from app.models.chunk import DocumentChunk
from app.services.pdf_parser import parse_pdf
from app.services.chunker import split_chunks


def process_report(report_id: str, db: Session) -> dict:
    """
    Full pipeline: PDF → parse → chunk → save chunks to MySQL → update status.
    Called after a successful upload.

    Returns a summary dict: { total_chunks, text_chunks, table_chunks }
    """
    # 1. Fetch report from DB
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise ValueError(f"Report {report_id} not found")

    # 2. Mark as processing so the FE can show a spinner
    report.status = ReportStatus.processing
    db.commit()

    try:
        # 3. Build the file path
        pdf_path = os.path.join(settings.UPLOAD_DIR, report.stored_filename)

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # 4. Parse — extract text + tables
        raw_chunks = parse_pdf(pdf_path)

        # 5. Chunk — split large text blocks, keep tables whole
        chunks = split_chunks(raw_chunks)

        # 6. Save all chunks to MySQL
        # Delete any existing chunks for this report (idempotent — safe to re-run)
        db.query(DocumentChunk).filter(
            DocumentChunk.report_id == report_id
        ).delete()

        db_chunks = []
        for chunk in chunks:
            db_chunk = DocumentChunk(
                report_id=report_id,
                content=chunk.content,
                chunk_type=chunk.chunk_type,
                section=chunk.section,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                token_count=len(chunk.content.split())  # rough word count
            )
            db_chunks.append(db_chunk)

        db.bulk_save_objects(db_chunks)  # single INSERT for all chunks — much faster than looping

        # 7. Update report status to ready
        report.status = ReportStatus.ready
        db.commit()

        # Return summary
        text_count = sum(1 for c in chunks if c.chunk_type == "text")
        table_count = sum(1 for c in chunks if c.chunk_type == "table")

        return {
            "report_id": report_id,
            "total_chunks": len(chunks),
            "text_chunks": text_count,
            "table_chunks": table_count,
            "status": "ready"
        }

    except Exception as e:
        # If anything fails, mark report as failed so user knows
        report.status = ReportStatus.failed
        db.commit()
        raise e