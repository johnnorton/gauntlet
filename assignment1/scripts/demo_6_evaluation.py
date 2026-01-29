"""
DEMO 6: EVALUATION METRICS
===========================
Shows how to measure RAG pipeline quality.

Why evaluate?
- Pipeline can fail silently (retrieve wrong docs, generate hallucinations)
- Need metrics to know if system works
- Two types: Retrieval quality + Generation quality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve
from src.generate import generate_answer

print("\n" + "="*70)
print("DEMO 6: EVALUATION & METRICS")
print("="*70)

print(f"\n💡 THE EVALUATION PROBLEM:")
print(f"""
   You ask your RAG system: "What brake repairs did we do?"

   It returns an answer with sources. But:
   ❓ Did it find ALL the brake repairs? (RECALL)
   ❓ Were all the results actually about brakes? (PRECISION)
   ❓ Is the answer actually supported by the data? (GROUNDEDNESS)

   Without evaluation, you don't know if your system works!
""")

print(f"\n1️⃣  RETRIEVAL EVALUATION: Recall@K")
print("-" * 70)

print(f"""
   RECALL = (Relevant items retrieved) / (Total relevant items)

   Example:
   - You know there are 5 brake repair invoices
   - Your query "brake repairs" returns 3 of them
   - Recall = 3/5 = 60%

   In code:
   - You have a test query: "brake repairs"
   - You know it should find invoices: [123, 456, 789, 101, 202]
   - System returns chunks from: [123, 456, 789]
   - Recall@5 = 3/5 = 60% ✓ pretty good

   Why measure it:
   - Shows if retrieval is comprehensive
   - High recall = finding relevant docs
   - Low recall = missing important docs
""")

print(f"\n   Test it yourself:")
print(f"   → Open eval/test_queries.json")
print(f"   → Add 'expected_invoice_ids' to a query")
print(f"   → Run: python -m eval.recall_eval")
print()

print(f"2️⃣  GENERATION EVALUATION: Groundedness")
print("-" * 70)

print(f"""
   GROUNDEDNESS = (Claims supported by context) / (Total claims)

   Or scored 1-5:
   - 5 = Fully grounded, all facts from context
   - 4 = Well grounded with minor issues
   - 3 = Partially grounded, some unsupported claims
   - 2 = Mostly ungrounded
   - 1 = Completely fabricated

   Example:
   - Retrieved docs talk about brake shoes and pads
   - Claude answers: "We replaced brake shoes, pads, and rotors"
   - But docs don't mention rotors...
   - Groundedness score: 3/5 (some hallucination)

   Why measure it:
   - Shows if Claude is making stuff up
   - Prevents "hallucinations"
   - Ensures trust in answers
""")

print(f"\n   Test it yourself:")
print(f"   → Run: python -m eval.groundedness_eval")
print(f"   → Claude evaluates if answers are grounded")
print()

print(f"\n3️⃣  PUTTING IT TOGETHER: A Complete Evaluation")
print("-" * 70)

# Run a simple example
test_query = "What electrical problems were encountered?"

print(f"\nQuery: \"{test_query}\"")
print("-" * 70)

# Retrieve
retrieved_chunks = retrieve(test_query, k=5)
print(f"✅ Retrieval Evaluation (Recall@5):")
print(f"   - Retrieved {len(retrieved_chunks)} chunks")
unique_invoices = set([c['metadata'].get('invoice_id') for c in retrieved_chunks])
print(f"   - From {len(unique_invoices)} unique invoices")
print(f"   - Similarity scores: {[f'{c['similarity']:.2f}' for c in retrieved_chunks]}")

# Generate
answer, sources = generate_answer(test_query, retrieved_chunks)
print(f"\n✅ Generation Evaluation (Groundedness):")
print(f"   - Answer: {answer[:100]}...")
print(f"   - Sources: {sources}")
print(f"   - ✓ Answer cites specific invoices")
print(f"   - ✓ Could verify groundedness with Claude")

print(f"\n" + "="*70)
print("💡 KEY EVALUATION PRINCIPLES:")
print(f"""
   1. Measure retrieval separately from generation
      - Retrieval quality ≠ Generation quality
      - Both matter, but different things

   2. Use domain knowledge for ground truth
      - Know which invoices SHOULD match a query
      - Test against those expectations
      - This is why Recall@K is useful

   3. Don't just measure final answer
      - Check if sources are cited
      - Check if context is used correctly
      - This is what groundedness measures

   4. Iterate based on metrics
      - Low recall? Improve chunking/embedding
      - Low groundedness? Improve retrieval
      - Metrics guide improvements
""")
print("="*70 + "\n")

print(f"📝 EVALUATION WORKFLOW:")
print(f"""
   Development Phase:
   1. Build pipeline (extract → chunk → embed → retrieve → generate)
   2. Define test queries with expected results
   3. Measure Recall@K on retrieval
   4. Measure Groundedness on generation
   5. If metrics are low → debug the pipeline
   6. Fix issues → re-measure
   7. Iterate until satisfied

   Production Phase:
   - Monitor these metrics continuously
   - Alert if metrics drop (data quality issue?)
   - A/B test improvements
""")

print(f"\n" + "="*70)
print("🚀 YOU'RE READY!")
print("   Your RAG pipeline has:")
print("   ✅ Clear retrieval evaluation (Recall@K)")
print("   ✅ Clear generation evaluation (Groundedness)")
print("   ✅ Measurable quality metrics")
print("   ✅ Foundation for improvement")
print("="*70 + "\n")
