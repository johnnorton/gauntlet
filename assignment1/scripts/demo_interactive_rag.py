"""
INTERACTIVE RAG PIPELINE DEMO
==============================
Step through the complete RAG process with pauses for narration.
Perfect for recording a video walkthrough!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve
from src.generate import generate_answer
from src.embed import embed_single_chunk
import time

def pause(message="Press ENTER to continue..."):
    """Pause execution and wait for user input"""
    print(f"\n{'─'*80}")
    input(f"\n⏸️  {message}\n")
    print(f"{'─'*80}\n")

def section(title):
    """Print a section header"""
    print(f"\n{'═'*80}")
    print(f"  {title}")
    print(f"{'═'*80}\n")

# ============================================================================
# DEMO STARTS HERE
# ============================================================================

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*10 + "COMPLETE RAG PIPELINE DEMONSTRATION" + " "*33 + "█")
print("█" + " "*10 + "(Step through with pauses for narration)" + " "*28 + "█")
print("█" + " "*78 + "█")
print("█"*80)

# STEP 1: INGESTION (show what was done)
section("STEP 1: DATA INGESTION (Already Completed)")

print("""
From our previous run, we extracted and processed:

📊 EXTRACTION PHASE
   ├─ Source: 1,000 PDF invoices
   ├─ Parsed with regex patterns
   ├─ Success rate: 97.2% (972 parsed correctly)
   └─ Result: Structured invoice data

📦 CHUNKING PHASE
   ├─ Strategy: Service-block level
   ├─ 1 chunk = 1 service repair + invoice context
   ├─ Total chunks: 1,564
   └─ From 813 unique invoices

⚡ EMBEDDING PHASE
   ├─ Model: sentence-transformers/all-MiniLM-L6-v2
   ├─ Each chunk → 384-dimensional vector
   ├─ 1,564 embeddings created (~2-3 seconds)
   └─ No API rate limits (local model)

🗄️  INDEXING PHASE
   ├─ Database: Chroma (with HNSW indexing)
   ├─ Storage: data/chroma_db/
   ├─ Total index size: ~15 MB
   └─ Persistent across runs
""")

pause("Review the ingestion process. Press ENTER to move to retrieval...")

# STEP 2: USER QUERY
section("STEP 2: USER QUERY")

query = "What electrical problems were found on Fords?"

print(f"""
User asks: "{query}"

This is a natural language question about the data in our invoices.
Our system must:
  1. Understand the meaning of this question
  2. Find relevant invoices about electrical problems
  3. Identify which ones mention Fords
  4. Pass the best matches to Claude
""")

pause("Ready to embed the query? Press ENTER...")

# STEP 3: EMBED QUERY
section("STEP 3: EMBED THE QUERY")

print(f"Embedding query: \"{query}\"\n")

start = time.time()
query_embedding = embed_single_chunk(query)
elapsed = time.time() - start

print(f"✅ Query embedded successfully!")
print(f"\nEmbedding details:")
print(f"  • Model: sentence-transformers/all-MiniLM-L6-v2")
print(f"  • Dimensions: 384")
print(f"  • Time: {elapsed:.3f} seconds")
print(f"\nFirst 10 dimensions of query vector:")
print(f"  {[round(x, 4) for x in query_embedding[:10]]}")
print(f"\nLast 10 dimensions of query vector:")
print(f"  {[round(x, 4) for x in query_embedding[-10:]]}")
print(f"\nVector statistics:")
print(f"  • Min: {min(query_embedding):.4f}")
print(f"  • Max: {max(query_embedding):.4f}")
print(f"  • Mean: {sum(query_embedding)/len(query_embedding):.6f}")
print(f"  • Magnitude (L2 norm): {sum(x*x for x in query_embedding)**0.5:.4f}")

pause("Query is now a 384-dimensional vector. Press ENTER to search...")

# STEP 4: RETRIEVAL
section("STEP 4: SEMANTIC SEARCH (RETRIEVAL)")

print(f"Searching 1,564 chunk vectors for matches...\n")

start = time.time()
retrieved_chunks = retrieve(query, k=50)
elapsed = time.time() - start

print(f"✅ Retrieval complete!")
print(f"  • Time: {elapsed:.3f} seconds")
print(f"  • Chunks retrieved: {len(retrieved_chunks)}")
print(f"  • From {len(set(c['metadata']['invoice_id'] for c in retrieved_chunks))} unique invoices")

print(f"\nHow retrieval works:")
print(f"  1. Compare query vector to all 1,564 chunk vectors")
print(f"  2. Calculate cosine similarity for each")
print(f"  3. Rank by similarity score (highest = most similar)")
print(f"  4. Return top-50 chunks")

print(f"\nTop 10 retrieved chunks:")
for i, chunk in enumerate(retrieved_chunks[:10], 1):
    invoice_id = chunk['metadata']['invoice_id']
    similarity = chunk['similarity']
    text_preview = chunk['text'][:60].replace('\n', ' ')
    print(f"  {i:2d}. Invoice {invoice_id:10s} (similarity: {similarity:.4f})")
    print(f"      {text_preview}...")

pause("We now have 50 relevant chunks. Press ENTER to see what goes to Claude...")

# STEP 5: CONTEXT PREPARATION
section("STEP 5: PREPARE CONTEXT FOR CLAUDE")

print(f"Building the prompt that will be sent to Claude API...\n")

context_parts = [chunk["text"] for chunk in retrieved_chunks]
context = "\n\n---\n\n".join(context_parts)

system_prompt = """You are a helpful assistant that answers questions about truck service invoices.
Answer questions based ONLY on the provided invoice context. If the answer is not in the context,
say "I cannot find this information in the provided invoices." Be specific and cite the invoices when relevant."""

user_prompt = f"""Based on the following invoice context, answer this question: {query}

INVOICE CONTEXT:
{context}

Please provide a clear, concise answer based only on the information above."""

print(f"📝 SYSTEM PROMPT ({len(system_prompt)} characters):")
print(f"─" * 80)
print(system_prompt)
print(f"─" * 80)

print(f"\n📝 USER PROMPT ({len(user_prompt)} characters):")
print(f"─" * 80)
print(f"Based on the following invoice context, answer this question: {query}")
print(f"\nINVOICE CONTEXT:")
print(f"[50 chunks joined with '---' separator]")
print(f"\nChunk 1 (first 200 chars):")
print(context[:200])
print(f"\n... [chunks 2-50] ...")
print(f"\nLast chunk (last 200 chars):")
print(f"{context[-200:]}")
print(f"─" * 80)

print(f"\n📊 PROMPT STATISTICS:")
print(f"  • System prompt: {len(system_prompt):,} characters")
print(f"  • User prompt: {len(user_prompt):,} characters")
print(f"  • Total: {len(system_prompt) + len(user_prompt):,} characters")
print(f"  • Estimated tokens: {(len(system_prompt) + len(user_prompt)) // 4:,} tokens")
print(f"  • Claude max tokens: 200,000")
print(f"  • Usage: {((len(system_prompt) + len(user_prompt)) // 4) / 200000 * 100:.1f}% ✅")

pause("This is exactly what Claude will receive. Press ENTER to send it...")

# STEP 6: CALL CLAUDE
section("STEP 6: SEND TO CLAUDE (GENERATION)")

print(f"Sending to Claude API...\n")
print(f"Request details:")
print(f"  • Model: claude-sonnet-4-20250514")
print(f"  • Max tokens: 1024")
print(f"  • Temperature: default")

start = time.time()
answer, source_invoices = generate_answer(query, retrieved_chunks)
elapsed = time.time() - start

print(f"\n✅ Claude responded!")
print(f"  • Response time: {elapsed:.3f} seconds")
print(f"  • Sources cited: {len(source_invoices)} invoices")

pause("Claude has generated the answer. Press ENTER to see it...")

# STEP 7: DISPLAY ANSWER
section("STEP 7: CLAUDE'S ANSWER")

print(answer)

print(f"\n📌 SOURCES CITED:")
for inv_id in sorted(source_invoices):
    print(f"  • {inv_id}")

pause("This is the final answer. Press ENTER for summary...")

# STEP 8: SUMMARY
section("COMPLETE RAG PIPELINE SUMMARY")

print(f"""
What just happened:

1️⃣  INGESTION (Previously completed)
    1,000 PDFs → 1,564 chunks → Embedded & indexed

2️⃣  EMBEDDING QUERY
    "{query}"
    → 384-dimensional vector

3️⃣  SEMANTIC SEARCH (Retrieval)
    Query vector vs 1,564 chunk vectors
    → Found top-50 most similar chunks

4️⃣  AUGMENTATION
    System prompt + User query + 50 chunks
    → Combined prompt ({len(system_prompt) + len(user_prompt):,} chars)

5️⃣  GENERATION (Claude)
    Claude reads prompt
    → Synthesizes answer
    → Cites sources

6️⃣  RESULT
    {len(answer.split())} word answer citing {len(source_invoices)} sources

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY INSIGHTS:

✓ Phase 1 (Semantic Search):
  - Filters 1,564 chunks → 50 candidates
  - Mathematical, meaning-based
  - Fast: {elapsed:.3f}ms

✓ Phase 2 (LLM Generation):
  - Reads 50 chunks
  - Understands relationships
  - Synthesizes coherent answer
  - Time: {elapsed:.0f}ms

✓ Two phases work together:
  - Search: "Which chunks are relevant?"
  - LLM: "What's the best answer from these?"

This is RAG: Retrieval-Augmented Generation
""")

print(f"\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " DEMO COMPLETE ".center(78) + "█")
print("█" + " "*78 + "█")
print("█"*80 + "\n")
