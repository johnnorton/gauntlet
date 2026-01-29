"""
DEMO 4: RETRIEVAL
=================
Shows how to find relevant chunks from a database using semantic search.

Think of retrieval as: Query → Vector → Database Search → Top K Results

This is where the "R" in RAG happens!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve

print("\n" + "="*70)
print("DEMO 4: SEMANTIC RETRIEVAL")
print("="*70)

print(f"\n💡 RETRIEVAL EXPLANATION:")
print(f"""
   Given 1,564 indexed chunks, how do we find the RELEVANT ones?

   Process:
   1. Take user query: "What electrical problems?"
   2. Convert to embedding (same model as chunks)
   3. Compare query vector to all chunk vectors
   4. Find top-50 most similar (optimal balance)
   5. Return those chunks with similarity scores

   Why 50 chunks?
   - Enough for diverse perspective
   - Close enough to stay relevant
   - ~17K tokens (efficient)
   - Optimal signal-to-noise ratio

   Why this works:
   - Embeddings capture MEANING
   - Similar queries have similar vectors
   - Similar vectors → similar documents
""")

print(f"\n1️⃣  STEP 1: Define test queries")
print("-" * 70)

test_queries = [
    "What electrical problems were fixed?",
    "Tell me about brake repairs",
    "Transmission issues and fixes",
]

for i, q in enumerate(test_queries, 1):
    print(f"   {i}. {q}")

print(f"\n2️⃣  STEP 2: Retrieve top-50 chunks for each query")
print("-" * 70)

for query in test_queries:
    print(f"\nQuery: \"{query}\"")
    print(f"{'─' * 70}")

    results = retrieve(query, k=50)

    if not results:
        print("  ❌ No results found")
        continue

    print(f"  ✅ Found {len(results)} relevant chunks:\n")

    for i, chunk in enumerate(results, 1):
        print(f"  [{i}] Invoice: {chunk['metadata'].get('invoice_id')}")
        print(f"      Similarity: {chunk['similarity']:.2f} (0-1 scale)")
        print(f"      Date: {chunk['metadata'].get('date')}")
        print(f"      Vehicle: {chunk['metadata'].get('vehicle_make')} {chunk['metadata'].get('vehicle_model')}")
        print(f"      Text preview: {chunk['text'][:80]}...")
        print()

print("="*70)
print("💡 KEY METRICS:")
print("   - RECALL: Did we find ALL relevant documents?")
print("     Formula: (relevant found) / (total relevant)")
print("     Example: found 3 out of 5 brake repairs = 60% recall")
print()
print("   - PRECISION: Were the results actually relevant?")
print("     Formula: (relevant found) / (total returned)")
print("     Example: returned 5, and 4 were relevant = 80% precision")
print("="*70 + "\n")
