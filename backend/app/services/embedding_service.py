from sentence_transformers import SentenceTransformer
from app.cores.config import settings

# Load model once at module level — loading it per-request would be
# extremely slow (several seconds each time). Module-level = loaded once
# when the app starts, reused for every embedding request.
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    Lazy singleton — loads the model only on first call, then reuses it.
    First call will download the model (~80MB) if not already cached.
    Subsequent calls return the already-loaded model instantly.
    """
    global _model
    if _model is None:
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("Embedding model loaded successfully")
    return _model


def embed_text(text: str) -> list[float]:
    """
    Convert a single text string into a vector embedding.
    Returns a list of floats (length = EMBEDDING_DIM = 384).
    """
    model = get_embedding_model()
    # encode() returns a numpy array — .tolist() converts to plain Python list
    # normalize_embeddings=True makes vectors unit length (required for cosine similarity)
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple texts in one call — much faster than calling embed_text()
    in a loop because the model processes them in parallel batches internally.
    Use this when embedding all chunks of a document.
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=32,        # process 32 texts at a time
        show_progress_bar=True
    )
    return embeddings.tolist()