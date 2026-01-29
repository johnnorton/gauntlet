"""
THE COMPLETENESS PROBLEM
=========================
Shows the trade-off between getting complete answers vs token limits.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*20 + "THE COMPLETENESS PROBLEM" + " "*34 + "█")
print("█" + " "*78 + "█")
print("█"*80)

query = "What electrical problems were found on Fords?"

print(f"\n{'═'*80}")
print("THE PROBLEM")
print(f"{'═'*80}\n")

print(f"""
Question: "{query}"

Your database has:
  • 1,564 total chunks
  • 813 invoices
  • Many service blocks about Fords
  • Many about electrical problems

What we retrieve with k=5:
  • Only the TOP-5 most similar chunks
  • Claude only sees these 5

What Claude DOESN'T see:
  • Chunks ranked 6-1,564
  • Potentially many more Ford electrical problems
  • Incomplete answer!
""")

# Show with different k values
print(f"{'═'*80}")
print("WHAT IF WE CHANGE K?")
print(f"{'═'*80}\n")

k_values = [5, 10, 20, 50]

for k in k_values:
    print(f"\nk = {k} (Return top-{k} chunks)")
    print(f"{'─'*80}")

    retrieved = retrieve(query, k=k)

    # Calculate total context size
    total_chars = sum(len(chunk['text']) for chunk in retrieved)
    total_words = total_chars // 4

    # Get unique invoices
    invoices = set(chunk['metadata']['invoice_id'] for chunk in retrieved)

    print(f"  Chunks retrieved:        {len(retrieved)}")
    print(f"  Unique invoices:         {len(invoices)}")
    print(f"  Total context size:      {total_chars:,} characters (~{total_words:,} words)")
    print(f"  Invoices: {', '.join(sorted(invoices)[:5])}{' ...' if len(invoices) > 5 else ''}")

print()

# Show the token limit issue
print(f"{'═'*80}")
print("TOKEN LIMIT CONSTRAINT")
print(f"{'═'*80}\n")

print(f"""
Claude API Limits:
  • Max input tokens: ~200,000 (for claude-sonnet-4)
  • But we limit to: ~6,500 characters (system + question + context)

Word count estimate:
  • 1 token ≈ 4 characters
  • 6,500 characters ÷ 4 ≈ 1,625 tokens for context + prompt

Current usage with k=5:
  • System prompt: 290 characters
  • Question: 45 characters
  • 5 chunks: 6,058 characters
  • Total: 6,393 characters (~1,600 tokens)
  ✅ Comfortable, within limits

With k=50:
  • System prompt: 290 characters
  • Question: 45 characters
  • 50 chunks: ~30,000+ characters (estimated)
  • Total: ~30,000+ characters (~7,500 tokens)
  ✅ Still within limits, but getting large

With k=100:
  • System prompt: 290 characters
  • Question: 45 characters
  • 100 chunks: ~60,000+ characters (estimated)
  • Total: ~60,000+ characters (~15,000 tokens)
  ✅ Still OK but getting expensive

With k=500:
  • System prompt: 290 characters
  • Question: 45 characters
  • 500 chunks: ~300,000+ characters (estimated)
  • Total: ~300,000+ characters (~75,000 tokens)
  ⚠️ Getting too large, dilutes signal with noise
""")

# Show the trade-off
print(f"{'═'*80}")
print("THE TRADE-OFF")
print(f"{'═'*80}\n")

print(f"""
k = 5 (Current)
├─ ✅ Pros:
│  ├─ Fast retrieval
│  ├─ Small context (6 KB)
│  ├─ Only MOST relevant chunks
│  └─ Claude focuses on best matches
│
└─ ❌ Cons:
   ├─ Incomplete answer
   ├─ Misses relevant chunks ranked 6+
   └─ If true answer is in chunk 27, Claude never sees it

k = 50 (Comprehensive)
├─ ✅ Pros:
│  ├─ More complete answer
│  ├─ Captures more electrical problems
│  └─ Less likely to miss relevant info
│
└─ ❌ Cons:
   ├─ Larger context (30+ KB)
   ├─ More noise mixed with signal
   ├─ Claude might get confused with conflicting info
   └─ Slower retrieval

k = 100 (Very Comprehensive)
├─ ✅ Pros:
│  ├─ Very comprehensive
│  └─ Unlikely to miss anything
│
└─ ❌ Cons:
   ├─ Very large context (60+ KB)
   ├─ Lots of noise/irrelevant chunks
   ├─ Claude might hallucinate trying to reconcile conflicts
   └─ Token costs increase
""")

# Show what a better approach might be
print(f"{'═'*80}")
print("BETTER APPROACHES")
print(f"{'═'*80}\n")

print(f"""
Option 1: Increase k (Simple)
  • Change: retrieve(query, k=50) instead of k=5
  • Pro: More complete answers
  • Con: Larger prompts, more noise
  • Implementation: Change 1 line of code

Option 2: Re-Rank (Better)
  • Step 1: Retrieve k=100 from semantic search
  • Step 2: Re-rank top-100 using an LLM
  • Step 3: Take top-20 after re-ranking
  • Pro: Gets completeness AND quality
  • Con: More expensive (extra API call)
  • Implementation: Add re-ranking function

Option 3: Iterate (Multiple Queries)
  • Step 1: Get answer with k=5
  • Step 2: Claude says "based on chunks found..."
  • Step 3: User can ask "Show me more"
  • Step 4: System retrieves chunks 6-20
  • Pro: User controls completeness
  • Con: Multiple API calls needed
  • Implementation: Add conversation loop

Option 4: Use Metadata Filtering
  • Step 1: User asks about Fords
  • Step 2: Filter to only Ford invoices first
  • Step 3: Then retrieve from filtered set
  • Pro: More targeted, fewer irrelevant chunks
  • Con: Requires good metadata
  • Implementation: Add filter before retrieve()

Option 5: Hybrid (Recommended)
  • Use k=20 instead of k=5 (4x more context)
  • Filter by vehicle type if possible
  • Accept that some edge cases will be missed
  • Pro: Balance completeness and quality
  • Con: Slightly larger prompts
  • Implementation: Small parameter change
""")

# Show the actual issue with current approach
print(f"{'═'*80}")
print("WHAT COULD GO WRONG")
print(f"{'═'*80}\n")

print(f"""
Scenario 1: Relevant chunk is ranked 6th
  User asks: "What electrical problems on Fords?"
  System retrieves: Top-5 chunks (most similar)
  Problem: Best answer is in chunk 6, Claude never sees it
  Result: Incomplete answer

Scenario 2: Many electrical problems exist
  User asks: "What electrical problems on Fords?"
  Database has: 47 different Ford electrical problems
  System retrieves: Top-5 chunks
  Problem: Claude only knows about top-5, misses 42 others
  Result: Very incomplete answer

Scenario 3: Edge case problems are less similar
  User asks: "What electrical problems on Fords?"
  Database has:
    - 5 common problems (high similarity) ← Retrieved
    - 10 rare problems (lower similarity) ← NOT retrieved
  Problem: Rare but important problems missed
  Result: Biased toward common cases
""")

# Show the question for the user
print(f"{'═'*80}")
print("THE QUESTION")
print(f"{'═'*80}\n")

print(f"""
Your system uses k=5 because:
  1. Retrieval is fast
  2. Context is small (6 KB)
  3. Claude gets focused, relevant chunks
  4. Works well for most queries

But this means:
  ❌ You get the TOP-5 most similar chunks
  ❌ NOT all electrical problems on Fords
  ❌ Just the ones that best match the query

This is a DESIGN CHOICE, not a bug.

The real question for your system:
  "Is this good enough for the use case?"

  If you're doing research/reporting: ❌ No, need completeness
  If you're answering quick questions: ✅ Yes, k=5 is fine
  If you're building a production system: ⚠️ Depends on requirements
""")

print(f"\n{'═'*80}\n")
