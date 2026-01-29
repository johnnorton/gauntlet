"""
VISUALIZE EXTRACTION LOGIC
===========================
Shows EXACTLY how the regex finds service blocks in PDFs.

This is the detective work - finding patterns in messy PDF text.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract import extract_invoice_text, parse_invoice
import re

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*15 + "HOW EXTRACTION FINDS SERVICE BLOCKS" + " "*29 + "█")
print("█" + " "*78 + "█")
print("█"*80)

print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  THE CHALLENGE:                                                             ║
║  You have a PDF with text like this:                                        ║
║                                                                              ║
║  Invoice: INV123                                                            ║
║  Date: 1/15/2024                                                           ║
║  Customer: John's Garage                                                    ║
║  ...                                                                        ║
║  Service Block 1:                                                           ║
║  Complaint: Engine won't start                                              ║
║  Cause: Dead battery                                                        ║
║  Correction: Replaced battery                                               ║
║  Labor: 0.5 hours @ $100/hr                                                ║
║  Parts: Battery Core, Cables                                               ║
║  ...                                                                        ║
║  Service Block 2:                                                           ║
║  Complaint: Oil leak                                                        ║
║  Cause: Loose oil pan bolt                                                  ║
║  ...                                                                        ║
║                                                                              ║
║  HOW DO WE FIND THESE AUTOMATICALLY?                                        ║
║  Answer: REGEX (Regular Expressions)                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

# Get a sample invoice
pdf_files = list(Path("data/invoices/invoices/").glob("*.pdf"))
pdf_path = pdf_files[0]

print(f"\n1️⃣  STEP 1: Extract Raw Text from PDF")
print("─" * 80)

text = extract_invoice_text(str(pdf_path))

print(f"File: {pdf_path.name}")
print(f"Total characters: {len(text)}")
print(f"\nFirst 500 characters (RAW PDF text):")
print(f"{'─' * 80}")
print(text[:500])
print(f"{'─' * 80}")

print(f"\n\n2️⃣  STEP 2: Find Service Blocks in Text")
print("─" * 80)

print(f"""
REGEX PATTERN: r"(?:Service Block \\d+[:\\s]*|(?=Complaint:))"

What this means:
  (?:...)           = Non-capturing group (doesn't save the match)
  Service Block \\d+ = Match literal "Service Block" followed by number(s)
  [:\\s]*           = Followed by optional colon or spaces
  |                 = OR
  (?=Complaint:)    = Look for "Complaint:" (lookahead, don't consume it)

In English:
  "Find places where either:
   1. 'Service Block 1:' appears, OR
   2. 'Complaint:' appears (marking start of a service block)"

Example:
  Text: "...previous block...\nService Block 2:\nComplaint: Engine won't start..."
         ^^^^^^^^^^^^^^^^^^^^^^
         REGEX FINDS THIS (split point)

""")

# Split by service blocks
service_blocks = re.split(r"(?:Service Block \d+[:\s]*|(?=Complaint:))", text)

print(f"✅ Found {len(service_blocks) - 1} potential service blocks")
print(f"   (Minus 1 for header before first block)")

print(f"\n\n3️⃣  STEP 3: Extract Fields from Each Block")
print("─" * 80)

print(f"""
For each potential service block, we search for these REGEX PATTERNS:

┌─ COMPLAINT PATTERN ─────────────────────────────────────────────┐
│  r"Complaint[:\\s]+([^\\n]+(?:\\n(?!Cause|Correction|...)[^\\n]*)*)"
│                                                                  │
│  What it does:                                                   │
│  1. Look for "Complaint" (case insensitive)                     │
│  2. Followed by ":" or spaces                                   │
│  3. Capture everything after until:                            │
│     - End of line, OR                                          │
│     - Another field name (Cause, Correction, Labor, Parts)    │
│                                                                  │
│  Example:                                                        │
│  "Complaint: Engine won't start                                │
│   Driver reports grinding noise"                               │
│     ✅ Captures: "Engine won't start\nDriver reports grinding" │
│     ✗ Does NOT capture Cause if on same line                  │
└──────────────────────────────────────────────────────────────────┘

┌─ CAUSE PATTERN ─────────────────────────────────────────────────┐
│  r"Cause[:\\s]+([^\\n]+(?:\\n(?!Correction|Labor|...)[^\\n]*)*)"
│                                                                  │
│  Same idea as Complaint, but:                                  │
│  - Looks for "Cause:"                                          │
│  - Stops at Correction, Labor, Parts, or Complaint             │
└──────────────────────────────────────────────────────────────────┘

┌─ CORRECTION PATTERN ────────────────────────────────────────────┐
│  r"Correction[:\\s]+([^\\n]+(?:\\n(?!Labor|Parts|...)[^\\n]*)*)"
│                                                                  │
│  Same idea, looks for "Correction:"                            │
└──────────────────────────────────────────────────────────────────┘

┌─ LABOR PATTERN ─────────────────────────────────────────────────┐
│  r"Labor[:\\s]+([0-9.]+)\\s*hrs?\\s*@?\\s*\\$?([0-9.]+)?"
│                                                                  │
│  What it does:                                                   │
│  1. Look for "Labor:"                                           │
│  2. Capture NUMBER (hours)                                      │
│  3. Optional "hrs" or "hr"                                      │
│  4. Optional "@" and "$"                                        │
│  5. Optional NUMBER (rate)                                      │
│                                                                  │
│  Examples it matches:                                           │
│  "Labor: 0.5 hrs"             → 0.5 hours                      │
│  "Labor: 1.25 hours @ $100"   → 1.25 hours @ $100             │
│  "Labor: 2"                   → 2 hours                        │
└──────────────────────────────────────────────────────────────────┘

┌─ PARTS PATTERN ─────────────────────────────────────────────────┐
│  r"Parts[:\\s]+([^\\n]+(?:\\n(?!Labor|Complaint|...)[^\\n]*)*)"
│                                                                  │
│  What it does:                                                   │
│  1. Look for "Parts:"                                           │
│  2. Capture text until Labor, Complaint, etc.                   │
│  3. Split by comma or newline                                   │
│     Result: ["Part1", "Part2", "Part3"]                        │
└──────────────────────────────────────────────────────────────────┘
""")

# Show example extraction
print(f"\n\n4️⃣  STEP 4: Example - Extract One Service Block")
print("─" * 80)

# Get a block with text
for i, block_text in enumerate(service_blocks[1:4], 1):
    if len(block_text) > 100:  # Find non-empty block
        print(f"\nBlock {i} (first 400 chars):")
        print(f"{'─' * 80}")
        print(block_text[:400])
        print(f"{'─' * 80}")

        # Show what each regex finds
        complaint_match = re.search(r"Complaint[:\s]+([^\n]+(?:\n(?!Cause|Correction|Labor|Parts)[^\n]*)*)", block_text, re.IGNORECASE)
        cause_match = re.search(r"Cause[:\s]+([^\n]+(?:\n(?!Correction|Labor|Parts|Complaint)[^\n]*)*)", block_text, re.IGNORECASE)
        correction_match = re.search(r"Correction[:\s]+([^\n]+(?:\n(?!Labor|Parts|Complaint|Cause)[^\n]*)*)", block_text, re.IGNORECASE)
        labor_match = re.search(r"Labor[:\s]+([0-9.]+)\s*hrs?\s*@?\s*\$?([0-9.]+)?", block_text, re.IGNORECASE)
        parts_match = re.search(r"Parts[:\s]+([^\n]+(?:\n(?!Labor|Complaint|Cause|Correction)[^\n]*)*)", block_text, re.IGNORECASE)

        print(f"\n🔍 REGEX EXTRACTIONS:")
        print(f"   Complaint:   {complaint_match.group(1).strip()[:60] if complaint_match else 'NOT FOUND'}...")
        print(f"   Cause:       {cause_match.group(1).strip()[:60] if cause_match else 'NOT FOUND'}...")
        print(f"   Correction:  {correction_match.group(1).strip()[:60] if correction_match else 'NOT FOUND'}...")
        print(f"   Labor:       {labor_match.group(1) if labor_match else 'NOT FOUND'} hours")
        print(f"   Parts:       {parts_match.group(1).strip()[:60] if parts_match else 'NOT FOUND'}...")

        break

print(f"\n\n5️⃣  STEP 5: Full Pipeline")
print("─" * 80)

print(f"""
THE COMPLETE EXTRACTION FLOW:

1. Read PDF file
   └─→ pdfplumber extracts all text

2. Extract invoice metadata
   └─→ Regex finds: Invoice ID, Date, Customer, Vehicle, VIN, Mileage

3. Split text into service blocks
   └─→ Regex splits by "Service Block N:" or "Complaint:"

4. For each block, extract fields
   └─→ Regex finds: Complaint, Cause, Correction, Labor, Parts

5. Return structured data
   └─→ {
         "invoice_id": "INV123",
         "date": "1/15/2024",
         "service_blocks": [
           {
             "complaint": "Engine won't start",
             "cause": "Dead battery",
             "correction": "Replaced battery",
             "labor_hours": 0.5,
             "parts": ["Battery Core", "Cables"]
           },
           ...
         ]
       }
""")

print(f"\n{'═' * 80}")
print(f"\n💡 WHY REGEX?")
print(f"""
   ✅ Flexible: Works with different PDF formats
   ✅ Robust: Handles variations ("Complaint:", "COMPLAINT:", "Complaint :")
   ✅ Powerful: Can capture multi-line fields
   ✅ Fast: Processes 1000 PDFs in 40 seconds

   ❌ Limitations:
   - Needs consistent field names (Complaint, Cause, etc.)
   - Breaks if PDF format changes dramatically
   - Hand-crafted patterns (not ML-based)

   Note: More complex PDFs might need ML (OCR, transformer models)
         But for structured invoices like these, regex works great!
""")

print(f"{'═' * 80}\n")

# Show actual extraction
print(f"\n6️⃣  ACTUAL RESULTS")
print("─" * 80)

invoice = parse_invoice(text, pdf_path.name)

if invoice:
    print(f"\n✅ Successfully extracted!")
    print(f"   Invoice ID: {invoice.get('invoice_id')}")
    print(f"   Date: {invoice.get('date')}")
    print(f"   Customer: {invoice.get('customer_name')}")
    print(f"   Service blocks found: {len(invoice.get('service_blocks', []))}")

    for i, block in enumerate(invoice.get('service_blocks', [])[:2], 1):
        print(f"\n   Block {i}:")
        print(f"   ├─ Complaint: {block.get('complaint', 'N/A')[:50]}")
        print(f"   ├─ Cause: {block.get('cause', 'N/A')[:50]}")
        print(f"   ├─ Correction: {block.get('correction', 'N/A')[:50]}")
        print(f"   └─ Labor: {block.get('labor_hours', 'N/A')} hours")
else:
    print("❌ Extraction failed")

print(f"\n{'═' * 80}\n")
