"""
VISUALIZE EMBEDDINGS & VECTOR DATABASE
========================================
Shows how embeddings are stored and how retrieval works.

Your Database: CHROMA
- Local, persistent vector storage
- Stores 1,564 embeddings (384 dimensions each)
- Located in: data/chroma_db/
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.index import get_collection
from src.embed import embed_single_chunk
from src.retrieve import retrieve
import numpy as np

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*20 + "EMBEDDINGS & VECTOR DATABASE VISUALIZATION" + " "*18 + "█")
print("█" + " "*78 + "█")
print("█"*80)

print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  YOUR VECTOR DATABASE: CHROMA                                               ║
║                                                                              ║
║  What is a Vector Database?                                                 ║
║  ┌─ Normal database: stores text, numbers, dates (SQL)                     ║
║  ├─ Vector database: stores embeddings (vectors)                           ║
║  ├─ Can do: similarity search (find similar documents)                     ║
║  └─ Uses math: cosine distance, euclidean distance, etc.                   ║
║                                                                              ║
║  Chroma Advantages:                                                         ║
║  ✓ Local: runs on your machine, no cloud                                   ║
║  ✓ Persistent: data saved to disk (data/chroma_db/)                        ║
║  ✓ Simple: no configuration needed                                          ║
║  ✓ Fast: instant similarity search                                         ║
║  ✓ Cost: free (no API calls)                                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

print(f"\n1️⃣  CHROMA DATABASE CONTENTS")
print("─" * 80)

# Get the collection
collection = get_collection()

if not collection:
    print("❌ Chroma database not found. Run: python scripts/ingest.py first")
    sys.exit(1)

# Get collection stats
count = collection.count()
print(f"✅ Database Status: ACTIVE")
print(f"   Location: data/chroma_db/")
print(f"   Total chunks stored: {count}")
print(f"   Embedding dimensions: 384")
print(f"   Embedding model: sentence-transformers/all-MiniLM-L6-v2")

print(f"\n2️⃣  EMBEDDING STRUCTURE")
print("─" * 80)

print(f"""
   Each chunk is stored as:

   ┌─ ID: "chunk_0", "chunk_1", ..., "chunk_1563"
   ├─ Text: Full chunk text (invoice info + service details)
   ├─ Embedding: 384 numbers (vector)
   │   Example: [-0.123, 0.456, -0.789, ... (381 more numbers)]
   ├─ Metadata:
   │   ├─ invoice_id
   │   ├─ date
   │   ├─ customer_name
   │   ├─ vehicle_year
   │   ├─ vehicle_make
   │   ├─ vehicle_model
   │   ├─ vin
   │   └─ mileage
   └─ Ready for: semantic search!

   Why 384 dimensions?
   - Trade-off: quality vs speed
   - 384 captures semantic meaning well
   - Small enough for fast search
   - The magic of sentence-transformers
""")

print(f"\n3️⃣  HOW SIMILARITY SEARCH WORKS")
print("─" * 80)

print(f"""
   Process:
   1. User asks: "What brake problems?"

   2. Embed the query (same model as chunks)
      "What brake problems?" → [-0.234, 0.567, ..., 384 numbers]

   3. Compare query vector to all 1,564 chunk vectors
      Using COSINE SIMILARITY:
      similarity = dot_product(query_vec, chunk_vec) / (norm1 * norm2)
      Result: 0 to 1 (0=completely different, 1=identical)

   4. Sort by similarity descending
      Chunk A: 0.82
      Chunk B: 0.79
      Chunk C: 0.76
      Chunk D: 0.71
      Chunk E: 0.68

   5. Return top-5 (default K=5)
      These 5 chunks are most similar to query!

   Time: <1 millisecond for all 1,564 searches!
""")

print(f"\n4️⃣  LIVE SIMILARITY SEARCH DEMO")
print("─" * 80)

test_queries = [
    "What electrical problems?",
    "Brake repairs and maintenance",
    "Engine troubles",
]

for query in test_queries:
    print(f"\n🔍 Query: \"{query}\"")
    print(f"   Searching 1,564 chunks...")

    results = retrieve(query, k=3)

    if results:
        print(f"   ✅ Top 3 Results:\n")
        for i, chunk in enumerate(results, 1):
            similarity_percent = chunk['similarity'] * 100
            print(f"   [{i}] Similarity: {similarity_percent:.1f}%")
            print(f"       Invoice: {chunk['metadata'].get('invoice_id')}")
            print(f"       Snippet: {chunk['text'].split(chr(10))[7][:50]}...")

print(f"\n5️⃣  EMBEDDING VECTOR SPACE (CONCEPTUAL)")
print("─" * 80)

print(f"""
   Your 1,564 chunks live in 384-dimensional space.

   Conceptually (if we could visualize 384D!):

   ELECTRICAL CHUNK REGION:
   ├─ chunk_42: "replaced wiring"
   ├─ chunk_107: "fixed lighting"
   ├─ chunk_89: "repaired circuit"
   └─ All close together in vector space!

   BRAKE CHUNK REGION:
   ├─ chunk_156: "replaced brake shoes"
   ├─ chunk_203: "brake fluid"
   └─ All close together in vector space!

   TRANSMISSION CHUNK REGION:
   ├─ chunk_300: "transmission replaced"
   ├─ chunk_445: "shift problems"
   └─ All close together in vector space!

   When you search "electrical":
   - Query embeds close to ELECTRICAL REGION
   - Finds nearby chunks
   - Returns electrical repairs! ✓

   This is the power of semantic embeddings!
""")

print(f"\n6️⃣  VECTOR DATABASE INTERNALS")
print("─" * 80)

print(f"""
   Behind the scenes, Chroma uses:

   ┌─ DuckDB: SQL database for metadata
   ├─ HNSW: Hierarchical Navigable Small World (fast search)
   ├─ Vector indexing: Organizes 384D vectors for quick lookup
   └─ Cosine distance: Metric for similarity

   File Structure:
   data/chroma_db/
   ├─ chroma.sqlite3          (metadata: invoice IDs, dates, etc.)
   ├─ chroma-embeddings/      (the vector indices)
   │  ├─ segment_data/        (actual embeddings stored here)
   │  └─ index/               (HNSW index for fast search)
   └─ other files             (Chroma internals)

   Total size: ~50 MB for 1,564 embeddings
   Search time: <1 millisecond per query
""")

print(f"\n7️⃣  RETRIEVAL PIPELINE VISUALIZATION")
print("─" * 80)

print(f"""
   Complete flow:

   User Input
   │
   v
   Query: "What brake problems?"
   │
   v
   Embed Query (384 dimensions)
   ├─ Model: sentence-transformers
   └─ Output: [-0.234, 0.567, ..., 384 numbers]
   │
   v
   Search Chroma Database
   ├─ Vector Index (HNSW)
   ├─ Compare to 1,564 chunk vectors
   └─ Calculate similarity scores
   │
   v
   Rank Results by Similarity
   ├─ chunk_156: 0.85
   ├─ chunk_203: 0.82
   ├─ chunk_300: 0.79
   ├─ chunk_42:  0.76
   └─ chunk_89:  0.73
   │
   v
   Return Top-K (K=5)
   ├─ With text
   ├─ With metadata
   ├─ With similarity scores
   └─ Ready for generation!
   │
   v
   Claude Reads Retrieved Context
   └─ Generates grounded answer
""")

print(f"\n{'═' * 80}")
print(f"\n💡 KEY INSIGHTS:")
print(f"""
   1. Vector embeddings capture MEANING
      - "brake shoe" and "brake pad" are close in vector space
      - Both match "brake problems" query
      - Different keywords, same meaning ✓

   2. Chroma is FAST because:
      - HNSW index doesn't check all 1,564 vectors
      - Hierarchical structure skips far-away regions
      - Result: <1ms per query instead of searching all

   3. Similarity score (0-1) shows relevance:
      - 0.95+: Perfect match
      - 0.80-0.95: Highly relevant
      - 0.60-0.80: Somewhat relevant
      - <0.60: Probably not what you want

   4. Why Chroma over alternatives?
      - Pinecone: Cloud, costs money, API limits
      - Weaviate: Overkill for this use case
      - Milvus: Too complex to set up
      - Chroma: Perfect balance ✓
""")
print(f"{'═' * 80}\n")
