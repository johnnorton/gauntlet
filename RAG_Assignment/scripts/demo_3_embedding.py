"""
DEMO 3: EMBEDDING
=================
Shows how to convert text into vectors (numbers) for semantic search.

Think of embedding as: Text → Vector (384 numbers) → Searchable

Why embeddings?
- Computers can't search text directly
- But they CAN compare vectors mathematically
- Similar meaning = similar vectors = we can find related documents

This is the "search engine" of RAG.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract import extract_and_parse_invoice
from src.chunk import create_chunks_from_invoice
from src.embed import embed_chunks, embed_single_chunk

print("\n" + "="*70)
print("DEMO 3: EMBEDDINGS & VECTORIZATION")
print("="*70)

# Get a sample invoice
pdf_files = list(Path("data/invoices/invoices/").glob("*.pdf"))[:1]
pdf_path = pdf_files[0]

print(f"\n1️⃣  STEP 1: Extract, parse, and chunk")
print("-" * 70)

invoice = extract_and_parse_invoice(str(pdf_path))
chunks = create_chunks_from_invoice(invoice)

print(f"✅ Created {len(chunks)} chunks from invoice\n")

print(f"2️⃣  STEP 2: Convert chunks to embeddings")
print("-" * 70)

chunk_texts = [chunk["text"] for chunk in chunks]
embeddings = embed_chunks(chunk_texts)

print(f"✅ Embedded {len(embeddings)} chunks\n")

print(f"📊 EMBEDDING DETAILS:")
print(f"   Model: sentence-transformers/all-MiniLM-L6-v2")
print(f"   - Small & fast (runs locally)")
print(f"   - Creates 384-dimensional vectors")
print(f"   - Good for semantic search")
print(f"\n   Output format: List of numbers (vector)")
print(f"   Example vector for first chunk:")
print(f"   {embeddings[0][:10]}... (showing first 10 of 384)")
print()

print(f"3️⃣  STEP 3: Demonstrate semantic similarity")
print("-" * 70)

# Create some test queries
test_queries = [
    "What electrical problems were fixed?",
    "Brake repairs and maintenance",
    "How much labor was required?",
]

print(f"\n💡 SEMANTIC SEARCH EXPLANATION:\n")
print(f"""
   Embeddings allow SEMANTIC search:
   - Not keyword matching (find words)
   - But MEANING matching (find concepts)

   Example:
   Query: "electrical issues"

   ✗ Keyword search would miss:
     - "lighting problems" (different words, same meaning)
     - "short circuit" (different words, same meaning)

   ✓ Semantic search FINDS both:
     - Compares vector similarity
     - Even if words are different, meaning is similar
""")

print(f"Testing semantic similarity:")
print("-" * 70)

for query in test_queries:
    print(f"\nQuery: \"{query}\"")
    query_embedding = embed_single_chunk(query)

    # Calculate similarity with first chunk
    # Cosine similarity: dot product of normalized vectors
    import numpy as np
    chunk_vec = np.array(embeddings[0])
    query_vec = np.array(query_embedding)

    # Normalize vectors
    chunk_vec = chunk_vec / np.linalg.norm(chunk_vec)
    query_vec = query_vec / np.linalg.norm(query_vec)

    # Cosine similarity
    similarity = np.dot(chunk_vec, query_vec)

    print(f"  Similarity to first chunk: {similarity:.3f}")
    print(f"  (0 = completely different, 1 = identical)")

print("\n" + "="*70)
print("💡 KEY INSIGHTS:")
print("   1. Embeddings are LOCAL - no API calls, no rate limits")
print("   2. Similarity search is FAST - just vector math")
print("   3. This is what enables semantic search in RAG")
print("="*70 + "\n")
