"""
DEMO 1: EXTRACTION
==================
Shows how to read a PDF and extract text and structure.

Think of extraction as: PDF → Raw Text → Structured Data

This is the foundation - if we can't extract the data, we can't build the RAG system.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract import extract_invoice_text, parse_invoice

print("\n" + "="*70)
print("DEMO 1: PDF EXTRACTION & PARSING")
print("="*70)

# Pick a PDF file to demonstrate with
pdf_files = list(Path("data/invoices/invoices/").glob("*.pdf"))[:1]

if not pdf_files:
    print("❌ No PDFs found in data/invoices/invoices/")
    sys.exit(1)

pdf_path = pdf_files[0]
print(f"\n1️⃣  STEP 1: Extract Raw Text from PDF")
print(f"   File: {pdf_path.name}")
print("-" * 70)

# Extract raw text
text = extract_invoice_text(str(pdf_path))

if not text:
    print("❌ Failed to extract text")
    sys.exit(1)

print(f"✅ Extracted {len(text)} characters of text")
print(f"\nFirst 300 characters:")
print(f"{'─' * 70}")
print(text[:300])
print(f"{'─' * 70}\n")

print(f"2️⃣  STEP 2: Parse Text into Structured Data")
print("-" * 70)

# Parse the text into structured format
result = parse_invoice(text, pdf_path.name)

if not result:
    print("❌ Failed to parse invoice")
    sys.exit(1)

print(f"✅ Successfully parsed!\n")

print(f"📋 EXTRACTED FIELDS:")
print(f"   Invoice ID:     {result.get('invoice_id', 'N/A')}")
print(f"   Date:          {result.get('date', 'N/A')}")
print(f"   Customer:      {result.get('customer_name', 'N/A')}")
print(f"   Vehicle:       {result.get('vehicle', {}).get('year', 'N/A')} {result.get('vehicle', {}).get('make', '')} {result.get('vehicle', {}).get('model', '')}")
print(f"   VIN:           {result.get('vehicle', {}).get('vin', 'N/A')}")
print(f"   Mileage:       {result.get('vehicle', {}).get('mileage', 'N/A')}")
print(f"   Service Blocks: {len(result.get('service_blocks', []))}")

# Show service blocks
service_blocks = result.get('service_blocks', [])
if service_blocks:
    print(f"\n🔧 SERVICE BLOCKS (repairs/services):")
    for i, block in enumerate(service_blocks, 1):
        print(f"\n   Block {i}:")
        print(f"   ├─ Complaint: {block.get('complaint', 'N/A')[:60]}...")
        print(f"   ├─ Cause:     {block.get('cause', 'N/A')[:60]}...")
        print(f"   ├─ Correction: {block.get('correction', 'N/A')[:60]}...")
        if block.get('parts'):
            print(f"   ├─ Parts:     {', '.join(block.get('parts', [])[:2])}")
        if block.get('labor_hours'):
            print(f"   └─ Labor:     {block.get('labor_hours')} hours")

print("\n" + "="*70)
print("💡 KEY INSIGHT:")
print("   Extraction turns unstructured PDFs into structured data we can work with.")
print("   This is the foundation of the entire RAG pipeline.")
print("="*70 + "\n")
