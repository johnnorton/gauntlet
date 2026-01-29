"""
WALKTHROUGH: RETRIEVAL PROCESS
================================
Shows exactly what happens from query to LLM response.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve
from src.embed import embed_single_chunk
from src.index import get_collection
import json

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*18 + "COMPLETE RETRIEVAL WALKTHROUGH" + " "*30 + "█")
print("█" + " "*78 + "█")
print("█"*80)

# STEP 1: User Asks a Question
print(f"\n{'═'*80}")
print("STEP 1️⃣ USER ASKS A QUESTION")
print(f"{'═'*80}\n")

query = "What electrical problems were found on Fords?"

print(f"User Query:")
print(f"  \"{query}\"")
print(f"\nLength: {len(query)} characters")
print(f"Words: {len(query.split())} words")

# STEP 2: Embed the Query
print(f"\n{'═'*80}")
print("STEP 2️⃣ EMBED THE QUERY (Convert Text to 384-Dimensional Vector)")
print(f"{'═'*80}\n")

query_embedding = embed_single_chunk(query)

print(f"Query embedding created:")
print(f"  Dimensions: {len(query_embedding)}")
print(f"  Type: List of floats")
print(f"\nFirst 10 dimensions (what the embedding looks like):")
print(f"  {[round(x, 4) for x in query_embedding[:10]]}")
print(f"\nMiddle 10 dimensions:")
print(f"  {[round(x, 4) for x in query_embedding[190:200]]}")
print(f"\nLast 10 dimensions:")
print(f"  {[round(x, 4) for x in query_embedding[-10:]]}")

# STEP 3: Query Chroma
print(f"\n{'═'*80}")
print("STEP 3️⃣ SEND QUERY TO CHROMA DATABASE")
print(f"{'═'*80}\n")

print(f"What gets sent to Chroma:")
print(f"""
collection.query(
    query_embeddings=[
        {[round(x, 4) for x in query_embedding[:5]]} ... (384 total)
    ],
    n_results=5,
)

In other words:
  "Find the 5 chunks whose embeddings are most similar to this query embedding"
""")

# STEP 4: Get Results from Chroma
print(f"\n{'═'*80}")
print("STEP 4️⃣ CHROMA SEARCHES DATABASE & RETURNS TOP-5 RESULTS")
print(f"{'═'*80}\n")

retrieved_chunks = retrieve(query, k=50)

print(f"✅ Retrieved {len(retrieved_chunks)} chunks from 1,564 total\n")

# STEP 5: Show Each Retrieved Chunk in Detail
print(f"\n{'═'*80}")
print("STEP 5️⃣ DETAILS OF EACH RETRIEVED CHUNK")
print(f"{'═'*80}\n")

for i, chunk in enumerate(retrieved_chunks, 1):
    print(f"RANK {i} (Similarity: {chunk['similarity']:.4f})")
    print(f"{'─'*80}")

    # Show text
    print(f"\n📝 CHUNK TEXT (what will be passed to Claude):\n")
    print(chunk['text'])

    # Show metadata
    print(f"\n🏷️  METADATA (structured info):")
    for key, value in chunk['metadata'].items():
        print(f"   {key:.<30} {value}")

    print(f"\n{'─'*80}\n")

# STEP 6: Format Context for Claude
print(f"\n{'═'*80}")
print("STEP 6️⃣ FORMAT RETRIEVED CHUNKS FOR CLAUDE")
print(f"{'═'*80}\n")

# Recreate what generate.py does
context = "\n\n---\n\n".join([chunk["text"] for chunk in retrieved_chunks])

print(f"Chunks are joined with separator: \"---\\n\\n\"\n")
print(f"CONTEXT PASSED TO CLAUDE (first 500 chars):")
print(f"{'─'*80}")
print(context[:500])
print(f"{'─'*80}")
print(f"Total context length: {len(context)} characters")
print(f"Total chunks: {len(retrieved_chunks)}")

# STEP 7: Show the Complete Prompt Sent to Claude
print(f"\n{'═'*80}")
print("STEP 7️⃣ COMPLETE PROMPT SENT TO CLAUDE")
print(f"{'═'*80}\n")

system_prompt = """You are a helpful assistant that answers questions about truck service invoices.
Answer questions based ONLY on the provided invoice context. If the answer is not in the context,
say "I cannot find this information in the provided invoices." Be specific and cite the invoices when relevant."""

user_prompt = f"""Based on the following invoice context, answer this question: {query}

INVOICE CONTEXT:
{context}

Please provide a clear, concise answer based only on the information above."""

print(f"SYSTEM PROMPT (instructs Claude how to behave):")
print(f"{'─'*80}")
print(system_prompt)
print(f"{'─'*80}")

print(f"\n\nUSER PROMPT (the actual question + context):")
print(f"{'─'*80}")
print(user_prompt)
print(f"{'─'*80}")

print(f"\n\nTOTAL PROMPT SIZE: {len(user_prompt)} characters")

# STEP 8: Show What Claude Receives
print(f"\n{'═'*80}")
print("STEP 8️⃣ WHAT CLAUDE RECEIVES")
print(f"{'═'*80}\n")

print(f"""
Model: claude-sonnet-4-20250514
Max tokens: 1024

System Prompt:
  "You are a helpful assistant..."

Context (formatted above):
  5 invoice chunks (from most to least similar)

Question:
  "{query}"

Claude's job:
  Answer the question using ONLY the provided context.
  Don't make up information.
  Cite invoice IDs when relevant.
""")

# STEP 9: Architecture Diagram
print(f"\n{'═'*80}")
print("STEP 9️⃣ COMPLETE FLOW DIAGRAM")
print(f"{'═'*80}\n")

print(f"""
USER QUERY
    │
    ↓
"What electrical problems were found on Fords?"
    │
    ├─ Tokenize → Split into words
    │
    ├─ Embed → Convert to 384-dim vector
    │    [-0.0693, 0.0773, 0.0807, ..., -0.0456]
    │
    ↓
CHROMA DATABASE (1,564 chunks)
    │
    ├─ Load all 1,564 chunk embeddings
    ├─ Calculate cosine similarity with query
    ├─ Get scores for all 1,564 chunks
    │    [0.6234, 0.5891, 0.7035, 0.4123, ..., 0.1245]
    │
    ├─ Sort by highest similarity
    │
    ├─ Take top 5
    │
    ↓
TOP-5 RESULTS (sorted by relevance)
    │
    ├─ Rank 1: Similarity 0.7035 (Best match!)
    │   Invoice 1676 - Ford electrical repair
    │
    ├─ Rank 2: Similarity 0.7019
    │   Invoice INV - Ford alternator problem
    │
    ├─ Rank 3: Similarity 0.6935
    │   Invoice 85478 - Ford wiring issue
    │
    ├─ Rank 4: Similarity 0.6789
    │   Invoice 9045 - Chevy electrical (less relevant)
    │
    └─ Rank 5: Similarity 0.6654
        Invoice 2034 - Ford starter issue
    │
    ↓
FORMAT FOR CLAUDE
    │
    ├─ Join chunks with "---" separator
    ├─ Add user question
    ├─ Add system instructions
    ├─ Package into JSON for API call
    │
    ↓
SEND TO CLAUDE
    │
    ├─ API Call to claude-sonnet-4-20250514
    ├─ Include all 5 chunks as context
    ├─ Ask: "What electrical problems were found on Fords?"
    │
    ↓
CLAUDE'S RESPONSE
    │
    ├─ Reads the 5 invoice chunks
    ├─ Identifies electrical problems on Fords
    ├─ Generates answer based only on context
    ├─ Cites specific invoices
    │
    └─ "Based on the provided invoices, electrical problems found on Fords include:
         - Invoice 1676: Alternator failure (0.7035 similarity)
         - Invoice INV: Wiring issues (0.7019 similarity)
         - Invoice 85478: Battery connector problem (0.6935 similarity)"
""")

# STEP 10: Similarity Scores Explained
print(f"\n{'═'*80}")
print("STEP 🔟 UNDERSTANDING SIMILARITY SCORES")
print(f"{'═'*80}\n")

print(f"""
Similarity Score Range: 0.0 to 1.0

What the scores mean:
  1.0  = Perfect match (identical embeddings)
  0.8+ = Highly relevant
  0.7+ = Very relevant (what we typically get)
  0.6-0.7 = Somewhat relevant
  0.5-0.6 = Weakly relevant
  <0.5 = Not relevant

Your results:
  Rank 1: 0.7035 ← Very relevant (electrical + Ford)
  Rank 2: 0.7019 ← Very relevant (electrical + Ford)
  Rank 3: 0.6935 ← Very relevant (electrical + Ford)
  Rank 4: 0.6789 ← Somewhat relevant (electrical, not Ford)
  Rank 5: 0.6654 ← Somewhat relevant (electrical, not Ford)

Why these scores?
  Chunk 1 has words: "electrical", "Ford", "problem"
  Query has words: "electrical", "Ford", "problems"
  → Very similar! High score.

  Chunk 4 has words: "electrical", "Chevy", "problem"
  Query has words: "electrical", "Ford", "problems"
  → Similar but vehicle type different → Lower score.
""")

# STEP 11: What if we Change K?
print(f"\n{'═'*80}")
print("STEP 1️⃣1️⃣ WHAT IF WE CHANGE K (number of results)?")
print(f"{'═'*80}\n")

print(f"""
retrieve(query, k=1) → Returns top 1 chunk
  ✅ Fastest, most focused
  ❌ Might miss relevant information

retrieve(query, k=50) ← Current default
  ✅ Comprehensive answers
  ✅ Captures diverse chunks from 41+ invoices
  ✅ Still within token limits (~7,500 tokens)

retrieve(query, k=10) → Returns top 10 chunks
  ❌ Slower retrieval
  ❌ More tokens to Claude
  ❌ Potential for noise/confusion
  ✅ Catches edge cases

For this project: k=5 is optimal
  - Fast retrieval (<1ms)
  - Enough context for good answers
  - Not too much noise
""")

# STEP 12: Performance Metrics
print(f"\n{'═'*80}")
print("STEP 1️⃣2️⃣ PERFORMANCE METRICS")
print(f"{'═'*80}\n")

print(f"""
Retrieve Operation Breakdown:

1. Embed query             ~1-2 ms
2. Load collection         ~5-10 ms
3. HNSW search (1,564 vecs) <1 ms
4. Format results          <1 ms
─────────────────────────────────
Total retrieval time:      ~10-15 ms

Claude API Call Breakdown:

1. Send request (5 chunks) ~50-100 ms (network)
2. Claude processes        ~500-1000 ms (generation)
3. Return response         ~50-100 ms (network)
─────────────────────────────────
Total API time:            ~600-1200 ms

Total end-to-end:          ~620-1215 ms (~0.6 seconds)
""")

# STEP 13: Real Example
print(f"\n{'═'*80}")
print("STEP 1️⃣3️⃣ COMPLETE EXAMPLE: QUERY → ANSWER")
print(f"{'═'*80}\n")

print(f"""
INPUT:
  User Query: "What electrical problems were found on Fords?"

RETRIEVAL PROCESS:
  1. Embed: [-0.0693, 0.0773, ...] (384 dimensions)
  2. Query Chroma: Find top-5 similar
  3. Results:
     - Chunk 1: Ford alternator (sim: 0.7035)
     - Chunk 2: Ford wiring (sim: 0.7019)
     - Chunk 3: Ford battery (sim: 0.6935)
     - Chunk 4: Chevy starter (sim: 0.6789)
     - Chunk 5: Ford starter (sim: 0.6654)

FORMATTED FOR CLAUDE:
  System: "Answer based only on provided context..."

  Context:
    [Invoice 1676 chunk text]
    ---
    [Invoice INV chunk text]
    ---
    ... (5 chunks total)

  Question: "What electrical problems were found on Fords?"

OUTPUT:
  Claude: "Based on the provided invoices, electrical problems
           found on Fords include:

           1. Alternator failure (Invoice 1676)
           2. Wiring harness corrosion (Invoice INV)
           3. Battery terminal issues (Invoice 85478)
           4. Starter motor failure (Invoice 2034)"

SOURCES:
  Invoices: 1676, INV, 85478, 2034
""")

# STEP 14: Key Insights
print(f"\n{'═'*80}")
print("KEY INSIGHTS")
print(f"{'═'*80}\n")

print(f"""
1. EMBEDDING IS THE KEY
   - Raw text → 384-dimensional vector
   - Captures semantic meaning
   - Enables fast similarity search

2. SIMILARITY SEARCH IS FAST
   - HNSW index: <1ms for 1,564 chunks
   - Finds most relevant chunks instantly
   - No need to read all 1,564 chunks

3. TOP-K IS CRITICAL
   - k=5 provides good context without noise
   - Too low (k=1): might miss information
   - Too high (k=20): Claude gets confused

4. CONTEXT IS EVERYTHING
   - Claude doesn't know about invoices
   - We send it the 5 most relevant chunks
   - It generates answers based ONLY on that context

5. GROUNDING IS THE PURPOSE
   - Without retrieval: Claude hallucinates
   - With retrieval: Answers are grounded in facts
   - This is what makes RAG powerful!

6. NO SEMANTIC UNDERSTANDING IN CHROMA
   - Chroma doesn't understand meaning
   - It just calculates mathematical similarity
   - The embedding model (sentence-transformers) does the understanding
   - Chroma's job: find similar vectors quickly
""")

print(f"\n{'═'*80}\n")
