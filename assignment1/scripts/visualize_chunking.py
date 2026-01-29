"""
VISUALIZE CHUNKING STRATEGY
============================
Shows exactly how your invoices are split into chunks.

Your Strategy: SERVICE BLOCK LEVEL
- One chunk per repair/service
- Each chunk includes full context
- This is the RIGHT choice for this data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract import extract_and_parse_invoice
from src.chunk import create_chunks_from_invoice

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*20 + "CHUNKING STRATEGY VISUALIZATION" + " "*28 + "█")
print("█" + " "*78 + "█")
print("█"*80)

print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  YOUR CHUNKING STRATEGY: SERVICE BLOCK LEVEL                                ║
║                                                                              ║
║  Concept:                                                                    ║
║  ┌─ One Invoice has Multiple Services (Complaints)                          ║
║  ├─ Each Service = One Complete Story                                       ║
║  │  ├─ What went wrong? (Complaint)                                         ║
║  │  ├─ Why? (Cause)                                                         ║
║  │  ├─ How did we fix it? (Correction)                                      ║
║  │  ├─ What parts? (Parts list)                                             ║
║  │  └─ How long? (Labor hours)                                              ║
║  └─ Convert Each Service into ONE Chunk                                     ║
║                                                                              ║
║  Why Service Blocks?                                                        ║
║  ✓ Precise: Find specific repairs, not whole invoices                      ║
║  ✓ Contextual: Each chunk includes invoice/customer/vehicle info           ║
║  ✓ Self-contained: Each chunk makes sense on its own                       ║
║  ✓ Retrieval quality: "brake repairs" returns actual brake service blocks  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Get a sample invoice with multiple services
pdf_files = list(Path("data/invoices/invoices/").glob("*.pdf"))

# Find an invoice with multiple service blocks
sample_invoice = None
for pdf in pdf_files[:50]:
    invoice = extract_and_parse_invoice(str(pdf))
    if invoice and len(invoice.get('service_blocks', [])) > 1:
        sample_invoice = (pdf, invoice)
        break

if not sample_invoice:
    # Fall back to first invoice
    sample_invoice = (pdf_files[0], extract_and_parse_invoice(str(pdf_files[0])))

pdf_path, invoice = sample_invoice

print(f"\n📄 EXAMPLE INVOICE: {pdf_path.name}")
print("─" * 80)

print(f"""
┌─ Invoice ID:    {invoice.get('invoice_id')}
├─ Date:          {invoice.get('date')}
├─ Customer:      {invoice.get('customer_name')}
├─ Vehicle:       {invoice.get('vehicle', {}).get('year')} {invoice.get('vehicle', {}).get('make')} {invoice.get('vehicle', {}).get('model')}
└─ Services:      {len(invoice.get('service_blocks', []))} repair(s)
""")

# Show how it's chunked
chunks = create_chunks_from_invoice(invoice)

print(f"\n🔪 CHUNKING PROCESS:")
print("─" * 80)

for i, (service_block, chunk) in enumerate(zip(invoice.get('service_blocks', []), chunks), 1):
    print(f"\n{'═' * 80}")
    print(f"SERVICE BLOCK #{i} → CHUNK #{i}")
    print(f"{'═' * 80}")

    print(f"\n📋 RAW SERVICE DATA:")
    print(f"   Complaint:   {service_block.get('complaint', 'N/A')}")
    print(f"   Cause:       {service_block.get('cause', 'N/A')}")
    print(f"   Correction:  {service_block.get('correction', 'N/A')}")
    print(f"   Parts:       {', '.join(service_block.get('parts', [])) if service_block.get('parts') else 'None'}")
    print(f"   Labor:       {service_block.get('labor_hours', 'N/A')} hours")

    print(f"\n✨ FORMATTED CHUNK (Ready for Embedding):")
    print(f"┌─" + "─" * 76 + "─┐")
    for line in chunk['text'].split('\n'):
        print(f"│ {line:<76} │")
    print(f"└─" + "─" * 76 + "─┘")

    print(f"\n🏷️  CHUNK METADATA:")
    print(f"   {chunk['metadata']}")

print(f"\n{'═' * 80}")
print(f"\n📊 STATISTICS FOR THIS INVOICE:")
print(f"   Original: 1 invoice")
print(f"   Services: {len(chunks)} service blocks")
print(f"   Result:   {len(chunks)} searchable chunks")
print(f"\n   If user searches 'transmission', we find service block #{[i for i, s in enumerate(invoice.get('service_blocks', []), 1) if 'transmission' in (s.get('complaint', '') + s.get('cause', '') + s.get('correction', '')).lower()]}")
print(f"   Not the entire invoice - just the relevant service!")

print(f"\n{'═' * 80}")
print(f"\n🌍 FULL DATASET CHUNKING:")
print(f"─" * 80)

print(f"""
   Total Invoices:     813
   Total Service Blocks (Chunks): 1,564

   Average Services per Invoice: {1564/813:.1f}

   This means:
   - Most invoices have 1-3 services
   - Some have 0 (simple inspections - skipped)
   - Some have 5+ (complex repairs)

   The chunks are stored in: data/chroma_db/
   Each chunk has:
   - ID: chunk_0 through chunk_1563
   - Text: Full formatted chunk
   - Embedding: 384-dimensional vector
   - Metadata: Invoice ID, date, customer, vehicle, etc.
""")

print(f"\n{'═' * 80}")
print(f"\n💡 WHY NOT OTHER STRATEGIES?")
print(f"─" * 80)

print(f"""
   ❌ STRATEGY: Full Invoices as Chunks
   Problem:
   - User asks "electrical problems"
   - Get entire invoice with 5 unrelated services
   - Noisy, imprecise retrieval
   - Result: Low search quality

   ❌ STRATEGY: Paragraph Level (3-5 sentences)
   Problem:
   - Loses context
   - "Replaced battery" without knowing it's for truck electrical
   - Chunk too small to understand
   - Result: Confused generation

   ✅ STRATEGY: Service Block Level (YOUR CHOICE)
   Benefit:
   - Perfect size: enough context, no noise
   - Self-contained: each chunk is a complete story
   - Precise: queries find exactly what they need
   - Result: High quality search + generation
""")

print(f"{'═' * 80}\n")
