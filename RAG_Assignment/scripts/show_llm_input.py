"""
WHAT GETS PASSED TO THE LLM
============================
Shows the exact data structure sent to Claude.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*20 + "EXACTLY WHAT GOES TO CLAUDE" + " "*32 + "█")
print("█" + " "*78 + "█")
print("█"*80)

# User asks a question
query = "What electrical problems were found on Fords?"

print(f"\n{'═'*80}")
print("STEP 1: USER QUERY")
print(f"{'═'*80}\n")
print(f'User: "{query}"\n')

# Retrieve chunks
print(f"{'═'*80}")
print("STEP 2: RETRIEVE TOP-5 CHUNKS FROM DATABASE")
print(f"{'═'*80}\n")

retrieved_chunks = retrieve(query, k=50)

print(f"✅ Retrieved {len(retrieved_chunks)} chunks")
print(f"   (These are the top-5 most similar chunks to your query)\n")

# Analyze what we got
invoices_found = {}
for i, chunk in enumerate(retrieved_chunks, 1):
    invoice_id = chunk['metadata']['invoice_id']
    if invoice_id not in invoices_found:
        invoices_found[invoice_id] = []
    invoices_found[invoice_id].append(i)

print(f"Invoices represented in the retrieved chunks:")
for invoice_id, ranks in invoices_found.items():
    print(f"  Invoice {invoice_id:.<30} appears in ranks {ranks}")

print()

# Show the exact structure
print(f"{'═'*80}")
print("STEP 3: EXACT DATA STRUCTURE OF RETRIEVED CHUNKS")
print(f"{'═'*80}\n")

print(f"Python structure (what retrieve() returns):\n")
print(f"""retrieved_chunks = [
  {{
    'text': 'Invoice: 26847505\\nDate: 1/13/2025\\n...',
    'metadata': {{
      'invoice_id': '26847505',
      'customer_name': 'PO Service Writer Unit #',
      'date': '1/13/2025',
      'vehicle_year': 'UNKNOWN',
      'vehicle_make': 'UNKNOWN',
      'vehicle_model': 'UNKNOWN',
      'vin': '1FTEX1EP4PKD78222',
      'mileage': 'UNKNOWN'
    }},
    'similarity': 0.4639,
    'rank': 1
  }},
  {{
    'text': 'Invoice: 5010\\nDate: 3/15/2024\\n...',
    'metadata': {{
      'invoice_id': '5010',
      'customer_name': 'PO Service Writer Unit #',
      ...
    }},
    'similarity': 0.4551,
    'rank': 2
  }},
  ... (3 more chunks)
]
""")

print()

# Show what gets passed to Claude
print(f"{'═'*80}")
print("STEP 4: WHAT GETS SENT TO CLAUDE (JSON)")
print(f"{'═'*80}\n")

# Recreate what generate.py does
context_parts = []
for chunk in retrieved_chunks:
    context_parts.append(chunk["text"])

context = "\n\n---\n\n".join(context_parts)

system_prompt = """You are a helpful assistant that answers questions about truck service invoices.
Answer questions based ONLY on the provided invoice context. If the answer is not in the context,
say "I cannot find this information in the provided invoices." Be specific and cite the invoices when relevant."""

user_prompt = f"""Based on the following invoice context, answer this question: {query}

INVOICE CONTEXT:
{context}

Please provide a clear, concise answer based only on the information above."""

print(f"Exact JSON sent to Claude API:\n")
print("""{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "system": "You are a helpful assistant that answers questions about truck service invoices. Answer questions based ONLY on the provided invoice context...",
  "messages": [
    {
      "role": "user",
      "content": "Based on the following invoice context, answer this question: What electrical problems were found on Fords?

INVOICE CONTEXT:
[{} chunks joined with --- separator]

Please provide a clear, concise answer based only on the information above."
    }
  ]
}""")

print()

# Show the context in detail
print(f"{'═'*80}")
print("STEP 5: THE CONTEXT (What goes between INVOICE CONTEXT and Please provide)")
print(f"{'═'*80}\n")

print(f"Total context size: {len(context)} characters (~{len(context)//4} words)\n")
print(f"Context preview (first 800 chars):\n")
print("─" * 80)
print(context[:800])
print("─" * 80)
print(f"\n... (full context is {len(context)} total characters) ...\n")

# Break down by chunk
print(f"{'═'*80}")
print("STEP 6: CONTEXT BREAKDOWN (Each of the 5 chunks)")
print(f"{'═'*80}\n")

for i, chunk in enumerate(retrieved_chunks, 1):
    text = chunk['text']
    meta = chunk['metadata']
    sim = chunk['similarity']

    # Extract key info
    invoice_id = meta['invoice_id']
    date = meta['date']
    customer = meta['customer_name']

    print(f"CHUNK {i} (Similarity: {sim:.4f})")
    print(f"├─ Invoice ID: {invoice_id}")
    print(f"├─ Date: {date}")
    print(f"├─ Customer: {customer}")
    print(f"├─ Text length: {len(text)} characters")
    print(f"└─ Text preview (first 150 chars):")
    print(f"   {text[:150]}...")
    print()

# Show the complete flow
print(f"{'═'*80}")
print("STEP 7: COMPLETE FLOW TO CLAUDE")
print(f"{'═'*80}\n")

print(f"""
WHAT CLAUDE RECEIVES:

system_prompt:
  {len(system_prompt)} characters
  "You are a helpful assistant that answers questions about truck service invoices..."

user_message:
  {len(user_prompt)} characters total

  Breakdown:
    Question: "What electrical problems were found on Fords?"
    Context: {len(context)} characters (5 chunks from database)
    Instructions: "Please provide a clear, concise answer..."

WHAT CLAUDE DOES:

1. Reads system prompt → Understands: "Only answer from provided context"
2. Reads user message
   ├─ Sees question: "What electrical problems..."
   ├─ Reads all 5 chunks
   ├─ Identifies chunks from invoices: {', '.join(invoices_found.keys())}
   ├─ Finds mentions of electrical problems
   └─ Extracts relevant info
3. Generates response based ONLY on those 5 chunks
4. Returns answer

KEY INSIGHT: Claude doesn't know about the other 1,559 chunks!
             It only sees these 5 most relevant ones.
""")

# Show potential multiple invoices
print(f"{'═'*80}")
print("STEP 8: MULTIPLE INVOICES IN ONE QUERY")
print(f"{'═'*80}\n")

if len(invoices_found) > 1:
    print(f"✅ YES! This query retrieved chunks from {len(invoices_found)} different invoices:\n")
    for invoice_id in sorted(invoices_found.keys()):
        print(f"   • Invoice {invoice_id}")
else:
    print(f"In this case, all 5 chunks came from the same invoice.")
    print(f"But this is NOT always the case!\n")

print(f"""
Why multiple invoices?
  ├─ Each chunk is a SERVICE BLOCK (one repair)
  ├─ One invoice can have multiple service blocks
  ├─ Top-5 similar chunks may come from:
  │  ├─ Different service blocks of same invoice
  │  └─ Service blocks from different invoices
  └─ All the chunks are relevant to the query!

Example with different invoices:
  Chunk 1: Invoice 26847505 - Charging system problem
  Chunk 2: Invoice 5010 - Wiring problem
  Chunk 3: Invoice DET - Electrical system wiring
  Chunk 4: Invoice 101 - General labor
  Chunk 5: Invoice 1115321 - ABS wiring problem

All 5 are about electrical issues, but from 5 different invoices!
Claude sees all 5 and can answer based on all of them.
""")

# Show what Claude needs to do
print(f"{'═'*80}")
print("STEP 9: HOW CLAUDE USES THE CONTEXT")
print(f"{'═'*80}\n")

print(f"""
Claude's job:

1. PARSE the context
   └─ Extract all chunks separated by "---"

2. IDENTIFY relevant information
   └─ Find all mentions of "electrical" + "problems"

3. ORGANIZE by invoice (optional)
   └─ Group findings by invoice ID for clarity

4. GENERATE answer
   └─ "Based on invoices X, Y, Z, the electrical problems are..."

5. CITE sources
   └─ Return which invoices the answer came from

Claude CANNOT:
  ❌ Access chunks outside the 5 provided
  ❌ Make up information not in the chunks
  ❌ Access metadata fields not shown
  ❌ Know how many total invoices exist (only sees 5!)
""")

# The key point
print(f"{'═'*80}")
print("KEY INSIGHT: RETRIEVAL, THEN AUGMENTATION, THEN GENERATION")
print(f"{'═'*80}\n")

print(f"""
RETRIEVAL PHASE:
  Question → Embed → Search 1,564 chunks → Find top-5 → Return

AUGMENTATION PHASE:
  System Prompt + Question + [Top-5 chunks] → Combined prompt

GENERATION PHASE:
  Claude reads combined prompt → Generates answer

THREE PHASES = RAG (Retrieval-Augmented Generation)

Claude ONLY SEES what you give it in the prompt!
It's completely blind to the other 1,559 chunks in the database.
""")

print(f"\n{'═'*80}\n")

# Summary table
print(f"{'═'*80}")
print("STEP 10: SUMMARY TABLE")
print(f"{'═'*80}\n")

print(f"""
Metric                          Value
────────────────────────────────────────────────────
Total chunks in database        1,564
Chunks retrieved per query      5 (top-k similarity)
Chunks passed to Claude         5
Chunks Claude can see           5
Chunks Claude can't see         1,559
Total invoices in database      813
Invoices in this result         {len(invoices_found)}
System prompt size              {len(system_prompt)} characters
User prompt size                {len(user_prompt)} characters
Total prompt to Claude          {len(system_prompt) + len(user_prompt)} characters
Claude model                    claude-sonnet-4-20250514
Max tokens for response         1024
────────────────────────────────────────────────────
""")

print()
