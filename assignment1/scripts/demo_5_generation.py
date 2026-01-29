"""
DEMO 5: GENERATION
==================
Shows how Claude uses retrieved context to generate answers.

Think of generation as: Retrieved Chunks + Query → Claude → Smart Answer

This is where the "G" in RAG happens!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve
from src.generate import generate_answer

print("\n" + "="*70)
print("DEMO 5: GENERATIVE AI WITH CONTEXT")
print("="*70)

print(f"\n💡 GENERATION EXPLANATION:")
print(f"""
   Problem with LLMs without context:
   - They can HALLUCINATE (make up false information)
   - They don't know about YOUR company data
   - They're out of date (trained on old data)

   Solution: RAG (Retrieval-Augmented Generation)
   - Step 1: Retrieve relevant documents
   - Step 2: Give those documents to Claude
   - Step 3: Claude answers ONLY using those documents
   - Result: Accurate, grounded, company-specific answers

   Key principle: "Stay grounded in context"
   - If the answer isn't in retrieved docs, Claude says so
   - No hallucination = trustworthy answers
""")

print(f"\n1️⃣  STEP 1: Define a question")
print("-" * 70)

query = "What electrical issues were found and how were they fixed?"
print(f"Question: \"{query}\"")

print(f"\n2️⃣  STEP 2: Retrieve relevant context")
print("-" * 70)

retrieved_chunks = retrieve(query, k=50)

print(f"✅ Retrieved {len(retrieved_chunks)} chunks:")
for i, chunk in enumerate(retrieved_chunks, 1):
    print(f"   [{i}] Invoice {chunk['metadata'].get('invoice_id')} - Similarity: {chunk['similarity']:.2f}")

print(f"\n3️⃣  STEP 3: Generate answer using Claude")
print("-" * 70)

answer, source_invoices = generate_answer(query, retrieved_chunks)

print(f"✅ Generated answer:\n")
print(f"{'─' * 70}")
print(answer)
print(f"{'─' * 70}")

print(f"\n4️⃣  STEP 4: Show sources")
print("-" * 70)

print(f"✅ Answer was based on {len(source_invoices)} invoices:")
for inv_id in source_invoices:
    print(f"   - {inv_id}")

print(f"\n" + "="*70)
print("💡 KEY INSIGHTS:")
print(f"""
   What just happened (Naive RAG):
   1. Query came in: "What electrical issues?"
   2. We embedded it
   3. We searched vector database
   4. We got 5 relevant chunks
   5. We gave those chunks to Claude
   6. Claude read the context and answered ONLY from that

   Why this works:
   - Specificity: Claude knows YOUR data
   - Grounding: Can cite sources
   - Accuracy: Reduced hallucination
   - Freshness: Uses current documents

   Limitations:
   - Only knows what's in retrieved chunks
   - If we retrieve wrong docs, answer is wrong
   - (This is why retrieval quality is critical!)

   This is why we evaluate retrieval separately from generation.
""")
print("="*70 + "\n")
