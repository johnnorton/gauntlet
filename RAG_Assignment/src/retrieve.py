"""Retrieval logic for querying the Chroma index."""

from typing import List, Dict, Any
from .embed import embed_single_chunk
from .index import get_collection


def retrieve(
    query: str,
    k: int = 50,
    persist_dir: str = "data/chroma_db",
    collection_name: str = "invoices"
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k chunks for a query.

    Returns list of chunks with metadata and similarity scores.
    """
    # Embed the query
    query_embedding = embed_single_chunk(query)

    # Get the collection
    collection = get_collection(persist_dir, collection_name)
    if collection is None:
        return []

    # Query the collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    # Format results
    retrieved_chunks = []
    if results and results["documents"] and len(results["documents"]) > 0:
        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
        distances = results["distances"][0] if results["distances"] else [0] * len(documents)

        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # Convert distance to similarity score (cosine distance -> similarity)
            # Chroma returns distances, so similarity ≈ 1 - distance for cosine
            similarity = 1 - distance if distance < 2 else 0

            retrieved_chunks.append({
                "text": doc,
                "metadata": metadata,
                "similarity": similarity,
                "rank": i + 1,
            })

    return retrieved_chunks
