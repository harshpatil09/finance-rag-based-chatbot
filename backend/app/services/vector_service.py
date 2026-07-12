from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)
from app.cores.config import settings


def get_qdrant_client() -> QdrantClient:
    """
    Create a fresh Qdrant client on each call.
    File-based Qdrant handles concurrent access safely,
    so no need for a singleton — avoids closed-client errors on reload.
    """
    return QdrantClient(path=settings.QDRANT_PATH)


def ensure_collection_exists():
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )
        print(f"Created Qdrant collection: {settings.QDRANT_COLLECTION}")
    client.close()


def upsert_chunks(chunks_with_embeddings: list[dict]):
    client = get_qdrant_client()
    points = [
        PointStruct(
            id=item["id"],
            vector=item["vector"],
            payload=item["payload"]
        )
        for item in chunks_with_embeddings
    ]

    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=batch
        )

    client.close()
    return len(points)


def search_similar(
    query_vector: list[float],
    report_id: str,
    top_k: int = 20
) -> list[dict]:
    client = get_qdrant_client()

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="report_id",
                    match=MatchValue(value=report_id)
                )
            ]
        ),
        limit=top_k,
        with_payload=True
    )

    client.close()

    return [
        {
            "chunk_id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in results.points
    ]


def delete_report_vectors(report_id: str):
    client = get_qdrant_client()
    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="report_id",
                    match=MatchValue(value=report_id)
                )
            ]
        )
    )
    client.close()