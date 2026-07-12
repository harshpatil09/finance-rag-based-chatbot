import ollama
from app.cores.config import settings


def embed_text(text: str) -> list[float]:
    """
    Convert a single text string into a vector using Ollama.
    Ollama must be running locally (it starts automatically with the desktop app).
    nomic-embed-text produces 768-dimensional vectors.
    """
    response = ollama.embeddings(
        model=settings.EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple texts by calling Ollama sequentially.
    Ollama doesn't have a native batch endpoint so we loop —
    still fast since it's a local API call with no network latency.
    """
    embeddings = []
    total = len(texts)
    for i, text in enumerate(texts):
        print(f"Embedding chunk {i+1}/{total}...")
        embedding = embed_text(text)
        embeddings.append(embedding)
    return embeddings