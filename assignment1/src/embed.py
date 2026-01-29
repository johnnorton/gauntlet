"""Embedding chunks using sentence-transformers (local, no API calls)."""

from typing import List
from sentence_transformers import SentenceTransformer

# Load model once at module import time and cache it
_model = None

def get_embedding_model():
    """Get or initialize the embedding model (cached)."""
    global _model
    if _model is None:
        # Using all-MiniLM-L6-v2: small, fast, high-quality
        # Downloads on first use (~80MB), then cached locally
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def initialize_embedding_model():
    """Initialize local embedding model (legacy function, uses cached model)."""
    return get_embedding_model()


def embed_chunks(chunks: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Embed a list of chunks using local sentence-transformers model.

    Fast, no API calls, no rate limits.
    """
    model = get_embedding_model()
    embeddings = model.encode(chunks, batch_size=batch_size, show_progress_bar=True)
    return embeddings.tolist()


def embed_single_chunk(chunk: str) -> List[float]:
    """Embed a single chunk."""
    model = get_embedding_model()
    embedding = model.encode([chunk])
    return embedding[0].tolist()
