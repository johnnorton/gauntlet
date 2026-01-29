"""
DEMO 2: CHUNKING
================
Shows how to split data into chunks for embedding.

Think of chunking as: Structured Data → Meaningful Pieces → Ready to embed

Why chunk?
- Embeddings have token limits
- Smaller pieces = more precise retrieval
- One chunk per service block = you can find specific repairs

This is a critical design decision for RAG quality!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract import extract_and_parse_invoice
from src.chunk import create_chunks_from_invoice

print("\n" + "="*70)
print("DEMO 2: CHUNKING STRATEGY")
print("="*70)

# Get a sample invoice
pdf_files = list(Path("data/invoices/invoices/").glob("*.pdf"))[:1]
pdf_path = pdf_files[0]

print(f"\n1️⃣  STEP 1: Extract and parse invoice")
print(f"   File: {pdf_path.name}")
print("-" * 70)

invoice = extract_and_parse_invoice(str(pdf_path))

if not invoice:
    print("❌ Failed to extract invoice")
    sys.exit(1)

print(f"✅ Extracted invoice {invoice.get('invoice_id')}")
print(f"   Service blocks: {len(invoice.get('service_blocks', []))}")

print(f"\n2️⃣  STEP 2: Create chunks from invoice")
print("-" * 70)

chunks = create_chunks_from_invoice(invoice)

print(f"✅ Created {len(chunks)} chunks\n")

print(f"📝 CHUNKING STRATEGY EXPLANATION:")
print(f"""
   Why one chunk per service block?

   ✓ Each service block is a complete story:
     - What was wrong (complaint)
     - Why it was wrong (cause)
     - How we fixed it (correction)
     - What parts we used (parts)
     - How long it took (labor)

   ✓ This makes retrieval precise:
     - Query: "What transmission issues?"
     - We find the transmission repair chunk, not the whole invoice

   ✓ Context is preserved:
     - Each chunk includes invoice ID, date, customer, vehicle
     - So we know WHO, WHEN, WHAT, and WHERE
""")

print(f"🔍 EXAMPLE CHUNKS:")
print("-" * 70)

for i, chunk in enumerate(chunks[:2], 1):  # Show first 2 chunks
    print(f"\nChunk {i}:")
    print(f"┌─ TEXT:")
    print(f"│\n")
    for line in chunk["text"].split("\n"):
        print(f"│  {line}")
    print(f"│\n└─ METADATA:")
    for key, value in chunk["metadata"].items():
        print(f"   {key}: {value}")
    print()

print("="*70)
print("💡 KEY INSIGHT:")
print("   Chunking is a design decision that affects everything downstream.")
print("   - Too big: lose precision (retrieve irrelevant docs)")
print("   - Too small: lose context (can't understand the repair)")
print("   - Our choice: one chunk per service = perfect balance")
print("="*70 + "\n")
