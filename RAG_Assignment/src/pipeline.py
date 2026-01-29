"""End-to-end RAG pipeline orchestration."""

from typing import Dict, Any, List
from .retrieve import retrieve
from .generate import generate_answer


def run_rag_pipeline(
    query: str,
    k: int = 50,
    persist_dir: str = "data/chroma_db",
) -> Dict[str, Any]:
    """
    Run the complete RAG pipeline: query -> retrieve -> generate.

    Returns:
        Dictionary with keys:
        - answer: str - The generated answer
        - retrieved_chunks: List - Retrieved chunks with metadata and scores
        - source_invoices: List - Invoice IDs used in the answer
    """
    # Retrieve relevant chunks
    retrieved_chunks = retrieve(
        query=query,
        k=k,
        persist_dir=persist_dir,
    )

    # Generate answer
    answer, source_invoices = generate_answer(query, retrieved_chunks)

    return {
        "query": query,
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
        "source_invoices": source_invoices,
        "num_sources": len(retrieved_chunks),
    }
