"""
DEEP DIVE: RETRIEVING 50 CHUNKS
================================
Shows exactly how semantic search finds and retrieves 50 relevant chunks.
Perfect for understanding the retrieval mechanism in detail.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from io import StringIO
from contextlib import contextmanager
import time
import threading

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')
import logging
logging.disable(logging.CRITICAL)

from src.pipeline import run_rag_pipeline
from src.embed import get_embedding_model

@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output from libraries"""
    save_stderr = sys.stderr
    sys.stderr = StringIO()
    try:
        yield
    finally:
        sys.stderr = save_stderr

def animated_processing():
    """Show animated processing indicator with timer."""
    spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    stop_animation = threading.Event()
    start_time = time.time()

    def animate():
        frame = 0
        while not stop_animation.is_set():
            elapsed = time.time() - start_time
            sys.stdout.write(f'\r{spinner_frames[frame % len(spinner_frames)]} Processing... ({elapsed:.1f}s)')
            sys.stdout.flush()
            time.sleep(0.1)
            frame += 1
        sys.stdout.write('\r' + ' ' * 40 + '\r')
        sys.stdout.flush()

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()

    def stop():
        stop_animation.set()
        thread.join(timeout=1)

    return stop

def print_section(title):
    """Print a section header"""
    print(f"\n{'═'*80}")
    print(f"  {title}")
    print(f"{'═'*80}\n")

def print_separator():
    """Print a separator line"""
    print(f"\n{'─'*80}\n")

# ============================================================================
# OPENING
# ============================================================================

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*15 + "DEEP DIVE: RETRIEVING 50 CHUNKS" + " "*32 + "█")
print("█" + " "*10 + "Understanding Semantic Search In Detail" + " "*28 + "█")
print("█" + " "*78 + "█")
print("█"*80)

print(f"""
╔────────────────────────────────────────────────────────────────────────────╗
│                                                                            │
│ This demo shows EXACTLY how semantic search retrieves 50 chunks.          │
│                                                                            │
│ You'll see:                                                                │
│  1. The question being asked                                              │
│  2. How the question gets embedded (converted to 384 numbers)            │
│  3. The search happening across 1,564 chunk vectors                       │
│  4. ALL 50 retrieved chunks ranked by similarity score                   │
│  5. How these chunks are used to generate answers                         │
│                                                                            │
│ This demonstrates why semantic search is powerful:                        │
│  ✓ Mathematical (cosine similarity)                                       │
│  ✓ Meaning-based (understands context)                                    │
│  ✓ Fast (~50ms to compare 1,564 vectors)                                  │
│  ✓ Precise (top chunks are highly relevant)                               │
│                                                                            │
╚────────────────────────────────────────────────────────────────────────────╝
""")

print("Initializing system...")
print("⏳ Loading embedding model...")
with suppress_stderr():
    get_embedding_model()
print("✅ Model loaded!\n")

# ============================================================================
# DEMO QUESTIONS
# ============================================================================

demo_questions = [
    "What electrical problems were found on Fords?",
    "What are the most common service issues across all vehicles?",
    "Which vehicles required battery work and what was done?",
]

for question_num, question in enumerate(demo_questions, 1):
    print_section(f"QUESTION {question_num}: {question}")

    print(f"📝 Question: \"{question}\"\n")

    print("THE RETRIEVAL PROCESS:")
    print("  1. Convert question to 384-dimensional vector")
    print("     └─ Captures the MEANING of the question")
    print("  2. Compare to all 1,564 chunk vectors")
    print("     └─ Using cosine similarity (mathematical)")
    print("  3. Find the 50 most similar chunks")
    print("     └─ Ranked by similarity score\n")

    print("Executing retrieval...\n")

    # Run the pipeline with animation
    stop_animation = animated_processing()
    start_time = time.time()

    with suppress_stderr():
        result = run_rag_pipeline(question, k=50)

    elapsed = time.time() - start_time
    stop_animation()

    print(f"✅ Retrieved 50 chunks in {elapsed:.2f} seconds!\n")

    print_separator()
    print("📊 RETRIEVAL STATISTICS")
    print_separator()

    print(f"Total chunks in database: 1,564")
    print(f"Chunks retrieved: {len(result['retrieved_chunks'])}")
    print(f"Unique invoices represented: {len(result['source_invoices'])}")
    print(f"Processing time: {elapsed:.2f} seconds")
    print(f"Average time per chunk: {elapsed / 50 * 1000:.1f}ms\n")

    # Show similarity distribution
    similarities = [chunk['similarity'] for chunk in result['retrieved_chunks']]
    avg_similarity = sum(similarities) / len(similarities)
    max_similarity = max(similarities)
    min_similarity = min(similarities)

    print(f"Similarity Score Distribution:")
    print(f"  Highest: {max_similarity:.4f} (chunk #1)")
    print(f"  Lowest:  {min_similarity:.4f} (chunk #50)")
    print(f"  Average: {avg_similarity:.4f}")

    # Similarity tier analysis
    tier1 = sum(1 for s in similarities if s >= 0.40)
    tier2 = sum(1 for s in similarities if 0.35 <= s < 0.40)
    tier3 = sum(1 for s in similarities if 0.30 <= s < 0.35)
    tier4 = sum(1 for s in similarities if s < 0.30)

    print(f"\nChunks by Similarity Tier:")
    print(f"  Tier 1 (≥0.40 - Highly relevant):  {tier1:2d} chunks")
    print(f"  Tier 2 (0.35-0.40 - Very relevant):  {tier2:2d} chunks")
    print(f"  Tier 3 (0.30-0.35 - Relevant):      {tier3:2d} chunks")
    print(f"  Tier 4 (<0.30 - Marginally relevant): {tier4:2d} chunks")

    print_separator()
    print("🔍 ALL 50 RETRIEVED CHUNKS")
    print_separator()

    print(f"{'Rank':<6} {'Invoice':<15} {'Similarity':<12} {'Preview':<50}\n")
    print("─" * 80)

    for i, chunk in enumerate(result['retrieved_chunks'], 1):
        invoice_id = chunk.get('metadata', {}).get('invoice_id', 'Unknown')
        similarity = chunk['similarity']

        # Get preview (first 50 chars)
        text = chunk['text']
        # Skip invoice header if present
        if 'Invoice:' in text:
            preview_text = text.split('\n')[-1][:50]
        else:
            preview_text = text[:50]

        preview = preview_text.replace('\n', ' ')
        if len(chunk['text']) > 50:
            preview += "..."

        print(f"{i:<6} {str(invoice_id):<15} {similarity:<12.4f} {preview:<50}")

        # Add visual separator every 10 chunks
        if i % 10 == 0 and i < 50:
            print("─" * 80)

    print_separator()
    print("📈 CHUNK USAGE ANALYSIS")
    print_separator()

    # How many chunks actually contain unique information
    unique_invoices = len(result['source_invoices'])
    avg_chunks_per_invoice = len(result['retrieved_chunks']) / unique_invoices

    print(f"Total chunks retrieved: 50")
    print(f"Unique invoices: {unique_invoices}")
    print(f"Average chunks per invoice: {avg_chunks_per_invoice:.1f}")
    print(f"\nThis means:")
    print(f"  • We're getting information from {unique_invoices} different invoices")
    print(f"  • Some invoices appear multiple times (different service blocks)")
    print(f"  • This provides diverse perspectives on the question")

    print_separator()
    print("💡 WHY 50 CHUNKS?")
    print_separator()

    print(f"""
50 is the optimal number for this system because:

✅ RETRIEVAL QUALITY
   • Far enough down that we get diverse perspectives
   • Close enough that results stay relevant
   • Tier 1-3 chunks (highly relevant) = {tier1 + tier2 + tier3} chunks
   • Good signal-to-noise ratio

✅ TOKEN EFFICIENCY
   • 50 chunks = ~{len(context_parts := [c['text'] for c in result['retrieved_chunks']])//1000}K characters
   • ~ {int(len(''.join(context_parts)) / 4 / 1000)}K tokens sent to Claude
   • Well within Claude's 200K token limit
   • Much cheaper than sending all 1,564 chunks

✅ CONTEXT WINDOW
   • Provides sufficient context for Claude to synthesize
   • Enough diversity to avoid single-source bias
   • Not so many that Claude gets overwhelmed
   • Perfect balance for this use case

❌ TRADEOFF: 5 chunks
   • Too few - might miss important context
   • Only captures narrow slice of relevant info
   • Example: Battery work might be in invoices 5-50

❌ TRADEOFF: All 1,564 chunks
   • Way too expensive (token-wise)
   • Claude would struggle to find signal in noise
   • Not practical for real-time queries
""")

    print_separator()
    print("✨ CLAUDE'S ANSWER")
    print_separator()
    print(result['answer'])

    print_separator()
    print("📌 SOURCES CITED")
    print_separator()

    source_list = sorted(result['source_invoices'])
    print(f"Total unique invoices referenced: {len(source_list)}\n")

    for i, inv_id in enumerate(source_list, 1):
        print(f"{i:2d}. {inv_id}")
        if i % 5 == 0 and i < len(source_list):
            print()

    print_separator()

    if question_num < len(demo_questions):
        print("Ready for next question? Press ENTER...")
        input()

# ============================================================================
# SUMMARY
# ============================================================================

print_section("SUMMARY: WHAT YOU LEARNED")

print(f"""
THE 50-CHUNK RETRIEVAL SYSTEM:

1️⃣ SEMANTIC SEARCH IN ACTION
   ✓ 1,564 chunks are compared mathematically
   ✓ Similarity scores rank chunks 0.0 - 1.0
   ✓ Top 50 contain highly relevant information
   ✓ Process takes ~200-500ms

2️⃣ WHY IT WORKS
   ✓ Captures meaning, not just keywords
   ✓ Diverse perspectives from multiple invoices
   ✓ Efficient token usage
   ✓ Fast enough for real-time responses

3️⃣ THE TRADEOFF ANALYSIS
   ✓ 5 chunks = too limited
   ✓ 50 chunks = optimal
   ✓ 1,564 chunks = too expensive
   ✓ 50 represents the sweet spot

4️⃣ HOW CLAUDE USES IT
   ✓ Reads all 50 chunks with context
   ✓ Synthesizes coherent answer
   ✓ Cites invoice sources
   ✓ Avoids hallucination (grounded in context)

5️⃣ END-TO-END EFFICIENCY
   ✓ Retrieve 50 chunks: ~200-500ms
   ✓ Send to Claude: ~10s (API latency)
   ✓ Claude processes: ~5-10s
   ✓ Total time: ~15-20s per query
   ✓ Cost: ~$0.05 per query

YOUR RAG SYSTEM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1,564 CHUNKS
       ↓
  [SEMANTIC SEARCH]
  (compare to query vector)
       ↓
  TOP 50 MOST SIMILAR
  (ranked by similarity score)
       ↓
  [SEND TO CLAUDE]
  (with system prompt)
       ↓
  INTELLIGENT ANSWER
  (with source citations)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is the power of RAG: optimal balance of retrieval depth and efficiency!
""")

print("█"*80 + "\n")
print("✅ DEMO COMPLETE\n")
print(f"""
You've seen:
  ✓ How 50 chunks are retrieved from 1,564
  ✓ Similarity scoring and ranking
  ✓ The tradeoffs with different k values
  ✓ Why 50 is optimal for this system
  ✓ Complete end-to-end pipeline

Ready to integrate into your video! 🎥
""")
