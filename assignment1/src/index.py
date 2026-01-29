"""Chroma indexing for chunks."""

import os
from typing import List, Dict, Any
import chromadb


def get_chroma_client(persist_dir: str = "data/chroma_db"):
    """Get or create a Chroma client with persistent storage."""
    # Create directory if it doesn't exist
    os.makedirs(persist_dir, exist_ok=True)

    # Try new API first, fall back to old API
    try:
        return chromadb.PersistentClient(path=persist_dir)
    except (AttributeError, TypeError):
        # Old Chroma API
        return chromadb.Client(
            settings=chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            )
        )


def initialize_collection(client, collection_name: str = "invoices"):
    """Initialize or get a Chroma collection."""
    # Delete existing collection if it exists to start fresh
    try:
        client.delete_collection(collection_name)
    except:
        pass

    return client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


def index_chunks(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    persist_dir: str = "data/chroma_db",
    collection_name: str = "invoices"
) -> None:
    """Index chunks and their embeddings into Chroma."""
    client = get_chroma_client(persist_dir)
    collection = initialize_collection(client, collection_name)

    # Prepare data for insertion
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    # Persist for old API
    try:
        client.persist()
    except AttributeError:
        pass  # New API persists automatically

    print(f"Indexed {len(chunks)} chunks into Chroma")


def get_collection(persist_dir: str = "data/chroma_db", collection_name: str = "invoices"):
    """Get an existing Chroma collection."""
    client = get_chroma_client(persist_dir)
    try:
        return client.get_collection(collection_name)
    except:
        return None
