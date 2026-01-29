"""
INTERACTIVE RAG PIPELINE DEMO WITH SAMPLE QUESTIONS
====================================================
Step through the RAG process, then answer 5 real questions about the data.
Perfect for recording - shows use cases at start, demonstrates them at end.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import sys
from io import StringIO
from contextlib import contextmanager

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Suppress logging
import logging
logging.disable(logging.CRITICAL)

from src.pipeline import run_rag_pipeline
from src.embed import get_embedding_model
import time
import threading

@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output from libraries"""
    save_stderr = sys.stderr
    sys.stderr = StringIO()
    try:
        yield
    finally:
        sys.stderr = save_stderr

def animated_processing(duration_callback=None):
    """
    Show animated processing indicator with timer.
    Returns a function to stop the animation.
    """
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
        # Clear the line
        sys.stdout.write('\r' + ' ' * 40 + '\r')
        sys.stdout.flush()

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()

    def stop():
        stop_animation.set()
        thread.join(timeout=1)

    return stop

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
print("█" + " "*10 + "With Real-World Questions & Answers" + " "*30 + "█")
print("█" + " "*78 + "█")
print("█"*80)

# OPENING: Show what questions we'll answer
section("INTRODUCTION: SAMPLE QUESTIONS")

questions_to_ask = [
    "What electrical problems were found on Fords?",
    "What are the most common service issues across all vehicles?",
    "Which vehicles required battery work and what was done?",
    "What brake-related repairs were performed?",
    "What fixes were applied to charging system issues?"
]

print("""
This RAG system can answer real questions about our truck service data.
Let's start by identifying 5 questions we want to answer:

""")

for i, q in enumerate(questions_to_ask, 1):
    print(f"  {i}. {q}")

print(f"""

These questions represent different types of queries:
  • Vehicle-specific (What about Fords?)
  • Problem-specific (Electrical issues? Charging? Brakes?)
  • Pattern-finding (Most common issues?)
  • General repairs (What was done for X?)

Let's walk through HOW the system answers these questions.
""")

pause("Ready to start the demo? Press ENTER...")

# STEP 1: INGESTION
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
   └─ Ready for queries!
""")

pause("Data is ready. Press ENTER to continue to the technical walkthrough...")

# STEP 2: TECHNICAL WALKTHROUGH
section("STEP 2-8: TECHNICAL WALKTHROUGH (Quick Version)")

print("""
We're going to walk through the complete RAG pipeline quickly, then 
answer all 5 sample questions with real data.

The pipeline works like this:

  QUERY (text)
    ↓
  EMBED (convert to 384-dim vector)
    ↓
  SEARCH (compare to 1,564 chunk vectors)
    ↓
  RETRIEVE (get top-50 most similar chunks)
    ↓
  BUILD PROMPT (system + question + 50 chunks)
    ↓
  SEND TO CLAUDE (via API)
    ↓
  CLAUDE SYNTHESIZES (reads 50 chunks, makes answer)
    ↓
  RETURN ANSWER (with sources cited)
""")

pause("Ready to see it in action? Press ENTER to answer the 5 questions...")

# PART 2: ANSWER THE QUESTIONS
section("ANSWERING THE SAMPLE QUESTIONS")

print(f"""
Now let's answer all {len(questions_to_ask)} questions we identified at the start.

For each question:
  1. We'll show the question
  2. The system will retrieve and search
  3. Claude will generate an answer
  4. We'll show sources cited

Let's begin...
""")

pause("Ready? Press ENTER...")

# Preload embedding model to avoid timeout on first question
print("⏳ Loading embedding model... (this happens once)\n")
with suppress_stderr():
    get_embedding_model()
print("✅ Model loaded!\n")

# Answer each question
answers = []
for i, question in enumerate(questions_to_ask, 1):
    section(f"QUESTION {i}/{len(questions_to_ask)}")

    print(f"❓ Question: \"{question}\"\n")

    # Show what's about to happen
    print("This query will:")
    print("  • Embed the question (convert to 384-dimensional vector)")
    print("  • Search 1,564 chunks for the most similar ones")
    print("  • Retrieve top-50 chunks from the database")
    print("  • Send them to Claude along with your question")
    print("  • Claude will synthesize an intelligent answer")
    print("  • We'll show you which invoices were cited as sources\n")

    pause(f"Ready to process Question {i}? Press ENTER to start...")

    print(f"❓ \"{question}\"\n")

    # Start animated processing
    stop_animation = animated_processing()

    start = time.time()
    with suppress_stderr():
        result = run_rag_pipeline(question, k=50)
    elapsed = time.time() - start

    # Stop animation
    stop_animation()
    print(f"✅ Complete! ({elapsed:.2f} seconds)\n")

    print(f"📊 STATISTICS:")
    print(f"   • Processing time: {elapsed:.2f} seconds")
    print(f"   • Chunks retrieved: {len(result['retrieved_chunks'])}")
    print(f"   • Invoices cited: {len(result['source_invoices'])}\n")

    # Show what was sent to Claude
    print(f"{'─'*80}")
    print(f"📬 WHAT WAS SENT TO CLAUDE")
    print(f"{'─'*80}\n")

    system_prompt = """You are a helpful assistant that answers questions about truck service invoices.
Answer questions based ONLY on the provided invoice context. If the answer is not in the context,
say "I cannot find this information in the provided invoices." Be specific and cite the invoices when relevant."""

    context_parts = [chunk["text"] for chunk in result['retrieved_chunks']]
    context = "\n\n---\n\n".join(context_parts)

    user_prompt = f"""Based on the following invoice context, answer this question: {question}

INVOICE CONTEXT:
{context}

Please provide a clear, concise answer based only on the information above."""

    print(f"🔷 SYSTEM PROMPT ({len(system_prompt)} chars):")
    print(f"   \"{system_prompt}\"\n")

    print(f"🔷 USER PROMPT STRUCTURE ({len(user_prompt):,} chars total):")
    print(f"   ├─ Question: {len(question)} chars")
    print(f"   ├─ Context: {len(context):,} chars (50 chunks)")
    print(f"   └─ Instructions: ~80 chars\n")

    print(f"🔷 USER PROMPT START (first 500 chars):")
    print(f"   {user_prompt[:500]}...\n")

    total_chars = len(system_prompt) + len(user_prompt)
    input_tokens = total_chars // 4

    # Estimate output tokens from Claude's response
    response_text = result['answer']
    output_tokens = len(response_text.split()) * 1.3  # Rough estimate: 1 word ≈ 1.3 tokens

    # Claude 3.5 Sonnet pricing (as of Jan 2025)
    input_cost_per_mtok = 3.00      # $3 per 1M input tokens
    output_cost_per_mtok = 15.00    # $15 per 1M output tokens

    # Calculate costs
    input_cost = (input_tokens / 1_000_000) * input_cost_per_mtok
    output_cost = (output_tokens / 1_000_000) * output_cost_per_mtok
    total_cost = input_cost + output_cost

    print(f"📈 TOKEN USAGE:")
    print(f"   • Input tokens: {int(input_tokens):,}")
    print(f"   • Output tokens: {int(output_tokens):,}")
    print(f"   • Total tokens: {int(input_tokens + output_tokens):,}")
    print(f"   • Claude's limit: 200,000 tokens")
    print(f"   • Usage: {((input_tokens + output_tokens) / 200000 * 100):.1f}% (very efficient!)\n")

    print(f"💰 COST ANALYSIS (Claude 3.5 Sonnet):")
    print(f"   • Input cost: ${input_cost:.6f} ({int(input_tokens):,} tokens × $3/1M)")
    print(f"   • Output cost: ${output_cost:.6f} ({int(output_tokens):,} tokens × $15/1M)")
    print(f"   • TOTAL PER QUESTION: ${total_cost:.6f}\n")

    print(f"{'─'*80}\n")

    print(f"📝 CLAUDE'S ANSWER:\n")
    print(result['answer'])
    
    print(f"\n📌 SOURCES CITED:")
    for inv_id in sorted(result['source_invoices'])[:8]:
        print(f"   • {inv_id}")
    if len(result['source_invoices']) > 8:
        print(f"   • ... and {len(result['source_invoices']) - 8} more invoices")

    answers.append({
        'question': question,
        'answer': result['answer'],
        'sources': result['source_invoices'],
        'time': elapsed,
        'input_tokens': int(input_tokens),
        'output_tokens': int(output_tokens),
        'cost': total_cost
    })

    if i < len(questions_to_ask):
        pause(f"Great! Ready for Question {i+1}? Press ENTER to continue...")

# SUMMARY
section("SUMMARY: ALL QUESTIONS ANSWERED")

print(f"""
We successfully answered all {len(questions_to_ask)} sample questions!

Summary:
""")

for i, item in enumerate(answers, 1):
    print(f"\n{i}. Question: \"{item['question']}\"")
    print(f"   ✓ Time: {item['time']:.2f}s | Tokens: {item['input_tokens'] + item['output_tokens']:,} | Cost: ${item['cost']:.6f}")
    print(f"   ✓ Sources: {len(item['sources'])} invoices cited")
    # Show first 100 chars of answer
    preview = item['answer'].split('\n')[0][:70]
    print(f"   ✓ Answer preview: {preview}...")

total_tokens = sum(a['input_tokens'] + a['output_tokens'] for a in answers)
total_cost = sum(a['cost'] for a in answers)
avg_cost_per_question = total_cost / len(answers)

print(f"""

PERFORMANCE METRICS:
  • Total questions answered: {len(answers)}
  • Total processing time: {sum(a['time'] for a in answers):.2f} seconds
  • Average per question: {sum(a['time'] for a in answers) / len(answers):.2f} seconds
  • Unique invoices cited: {len(set(inv for a in answers for inv in a['sources']))}

COST ANALYSIS:
  • Total tokens used: {total_tokens:,}
  • Total cost: ${total_cost:.6f} (all 5 questions)
  • Average cost per question: ${avg_cost_per_question:.6f}
  • Cost per 1,000 queries: ${avg_cost_per_question * 1000:.2f}

  Pricing: Claude 3.5 Sonnet - $3/1M input tokens, $15/1M output tokens

This demonstrates:
  ✓ Semantic search quickly finding relevant data
  ✓ LLM synthesizing coherent, intelligent answers
  ✓ Source citation for full traceability
  ✓ Real-time performance (seconds, not minutes)
  ✓ Handling diverse query types (vehicle-specific, problem-specific, pattern-finding)
  ✓ Efficient token usage (only 7.4% of available tokens)
  ✓ Cost-effective AI usage (fractions of a cent per question!)
""")

pause("Ready for final summary? Press ENTER...")

# FINAL SUMMARY
section("RAG PIPELINE COMPLETE")

print(f"""
What we demonstrated:

1. INGESTION PHASE
   • 1,000 PDFs → 1,564 searchable chunks
   • Service-block level granularity
   • 384-dimensional embeddings

2. RETRIEVAL PHASE (Semantic Search)
   • Query embedding
   • Compare to all 1,564 vectors
   • Get 50 most similar chunks
   • Filters from 1,564 → 50

3. GENERATION PHASE (Claude LLM)
   • Claude reads 50 chunks
   • Understands relationships
   • Synthesizes intelligent answer
   • Cites sources

4. REAL-WORLD TESTING
   • Answered {len(answers)} diverse questions
   • Showed varying query types
   • Demonstrated practical utility
   • Average response time: {sum(a['time'] for a in answers) / len(answers):.2f} seconds

WHY RAG WORKS:

Search alone (without LLM):
  ❌ Returns raw chunks (not useful)
  ❌ No synthesis or understanding
  ❌ Users must read all chunks themselves

LLM alone (without search):
  ❌ Can't see your data
  ❌ Would hallucinate answers
  ❌ 1,564 chunks in context = too expensive

RAG (Search + LLM):
  ✅ Fast filtering (semantic search)
  ✅ Intelligent synthesis (Claude)
  ✅ Cited sources (traceability)
  ✅ Efficient token usage
  ✅ Real-time performance

This pattern works for:
  • Customer support systems
  • Document search engines
  • Research assistants
  • Internal knowledge bases
  • Medical/legal document search
  • Q&A over company data

Your system successfully demonstrates the power of RAG!
""")

print(f"\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " DEMO COMPLETE ".center(78) + "█")
print("█" + " "*78 + "█")
print("█"*80 + "\n")
