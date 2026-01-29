"""
VISUALIZE CHROMA DATABASE
===========================
Shows what data looks like in the vector database.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.index import get_collection
import numpy as np

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*20 + "WHAT'S IN THE CHROMA VECTOR DATABASE?" + " "*24 + "█")
print("█" + " "*78 + "█")
print("█"*80)

# Get the Chroma collection
collection = get_collection()

print(f"\n1️⃣  DATABASE STATS")
print("─" * 80)

count = collection.count()
print(f"✅ Total chunks stored: {count}")
print(f"   Vector dimensions: 384 (sentence-transformers/all-MiniLM-L6-v2)")
print(f"   Database location: data/chroma_db/")
print(f"   Index type: HNSW (hierarchical navigable small world)")

print(f"\n\n2️⃣  DATA STRUCTURE - WHAT ONE CHUNK LOOKS LIKE")
print("─" * 80)

# Get first chunk to show structure
results = collection.get(limit=1)

if results and results['documents']:
    chunk_text = results['documents'][0]
    metadata = results['metadatas'][0]
    embedding = results['embeddings'][0] if results['embeddings'] else None
    chunk_id = results['ids'][0]

    print(f"\n📄 CHUNK ID: {chunk_id}\n")

    print(f"📝 TEXT CONTENT (what gets retrieved):")
    print(f"{'─'*80}")
    # Show first 500 chars of the text
    print(chunk_text[:500])
    if len(chunk_text) > 500:
        print(f"... ({len(chunk_text)} total characters)")
    print(f"{'─'*80}\n")

    print(f"🏷️  METADATA (searchable fields):")
    print(f"{'─'*80}")
    for key, value in sorted(metadata.items()):
        print(f"   {key:.<30} {str(value)[:50]}")
    print(f"{'─'*80}\n")

    if embedding:
        print(f"🔢 EMBEDDING VECTOR (384 dimensions):")
        print(f"{'─'*80}")
        print(f"   First 10 dimensions:    {[round(x, 4) for x in embedding[:10]]}")
        print(f"   Middle 10 dimensions:   {[round(x, 4) for x in embedding[187:197]]}")
        print(f"   Last 10 dimensions:     {[round(x, 4) for x in embedding[-10:]]}")

        # Calculate vector stats
        vec_array = np.array(embedding)
        print(f"")
        print(f"   Vector magnitude:       {np.linalg.norm(vec_array):.4f}")
        print(f"   Mean value:             {np.mean(vec_array):.4f}")
        print(f"   Min value:              {np.min(vec_array):.4f}")
        print(f"   Max value:              {np.max(vec_array):.4f}")
        print(f"{'─'*80}\n")

print(f"\n3️⃣  EXAMPLE - HOW CHROMA STORES DATA")
print("─" * 80)

print(f"""
Chroma stores each chunk like this:

{{"
  "id": "chunk_001_block_1",
  "document": "Invoice: INV001\\nDate: 1/15/2024\\nComplaint: Engine won't start...",
  "embedding": [0.0234, -0.0156, 0.0892, ...384 numbers total...],
  "metadata": {{
    "invoice_id": "INV001",
    "customer_name": "John's Garage",
    "vehicle_year": "2020",
    "vehicle_make": "Ford",
    "vehicle_model": "F-150",
    "service_block_num": "1",
    "complaint": "Engine won't start",
    "cause": "Dead battery",
    "correction": "Replaced battery",
    "labor_hours": "0.5",
    "labor_rate": "100.0"
  }}
}}

IMPORTANT: The embedding is what makes semantic search work!
- When you ask a question, it gets embedded to 384 dimensions
- Chroma compares your question embedding to all 1,564 chunk embeddings
- Returns chunks with HIGHEST similarity scores (0-1 scale)
- Typically returns top 5-10 most similar chunks
""")

print(f"\n4️⃣  HOW RETRIEVAL WORKS")
print("─" * 80)

print(f"""
Query Flow:
1. User asks: "What electrical problems were found?"
2. Query embedding: "What electrical problems were found?" → [0.045, -0.032, ...]
3. Similarity search: Compare query embedding to all 1,564 chunk embeddings
4. Score each chunk: cosine_similarity(query_embedding, chunk_embedding)
5. Sort by score (highest = most similar)
6. Return top K (usually K=5)

Similarity scores are between 0 and 1:
  1.0 = Perfect match (identical embeddings)
  0.8+ = Highly relevant
  0.6-0.7 = Somewhat relevant
  <0.5 = Not very relevant
""")

print(f"\n5️⃣  EXAMPLE RETRIEVAL - SEARCH IN ACTION")
print("─" * 80)

# Do a real search
from src.embed import embed_single_chunk

query = "What electrical problems were found?"
query_embedding = embed_single_chunk(query)

print(f"\nQuery: \"{query}\"")
print(f"Query embedding (first 10 dimensions): {[round(x, 4) for x in query_embedding[:10]]}\n")

# Search Chroma
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)

print(f"✅ Found {len(results['documents'][0])} results:\n")

for i, (doc, meta, distance) in enumerate(zip(
    results['documents'][0],
    results['metadatas'][0],
    results['distances'][0]
), 1):
    # Convert distance to similarity (Chroma returns distance, not similarity)
    similarity = 1 - (distance / 2)  # Approximate similarity

    complaint = meta.get('complaint') or "N/A"
    if complaint != "N/A":
        complaint = complaint[:60] + "..."

    print(f"Result {i}:")
    print(f"  Similarity score: {similarity:.4f} (0-1 scale, higher = better)")
    print(f"  Invoice: {meta.get('invoice_id')}")
    print(f"  Customer: {meta.get('customer_name')}")
    print(f"  Complaint: {complaint}")
    print(f"  Text preview: {doc[:70]}...")
    print()

print(f"\n6️⃣  DATABASE ARCHITECTURE")
print("─" * 80)

print(f"""
Chroma Database Structure:

data/chroma_db/
├── index.bin          # HNSW index (for fast similarity search)
├── metadata.db        # SQLite database (stores metadata)
├── data.db            # Embeddings and documents
└── tenant-data.db     # Collection info

Why HNSW index?
  • Hierarchical Navigable Small World algorithm
  • Fast approximate nearest neighbor search
  • <1ms query time for 1,564 vectors
  • Much faster than brute-force search (which would be O(n))

Vector Storage:
  • Format: 384-dimensional float32 vectors
  • Size per vector: 384 × 4 bytes = 1,536 bytes
  • Total storage: 1,564 × 1,536 bytes ≈ 2.4 MB
  • Metadata: Additional ~5-10 MB (depends on text length)
  • Total database size: ~10-15 MB (very lightweight!)
""")

print(f"\n7️⃣  METADATA FIELDS (What Gets Indexed)")
print("─" * 80)

# Get all unique metadata fields
all_data = collection.get()
if all_data['metadatas']:
    all_keys = set()
    for metadata in all_data['metadatas']:
        all_keys.update(metadata.keys())

    print(f"\nSearchable metadata fields:\n")
    for i, key in enumerate(sorted(all_keys), 1):
        print(f"  {i:2d}. {key}")

print(f"\n\n8️⃣  WHY THIS MATTERS FOR RAG")
print("─" * 80)

print(f"""
The vector database is the CORE of your RAG system:

Query → Embed → 🔍 SEARCH IN DATABASE → Retrieve Top-K → Generate Answer
                  ↑
                  You are here!

Without good vectors and storage:
  ❌ Can't find relevant chunks
  ❌ Get irrelevant context
  ❌ Claude generates bad answers

With Chroma database:
  ✅ Fast semantic search (<1ms per query)
  ✅ Stores 1,564 chunks compactly (~15 MB)
  ✅ Easy retrieval with similarity scoring
  ✅ Perfect for production RAG systems

Your setup:
  • 1,564 service block chunks
  • 384-dimensional embeddings
  • HNSW indexing for fast search
  • Local persistent storage (no API calls needed)
  • ~15 MB total database size
""")

print(f"\n{'═'*80}\n")

print(f"💡 TRY THIS:")
print(f"""
1. Open data/chroma_db/ to see the actual database files
2. Run: python scripts/query.py "electrical problem"
3. See what gets retrieved and why!
""")

print(f"\n{'═'*80}\n")
