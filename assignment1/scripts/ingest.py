"""Main ingestion script: extract, chunk, embed, and index invoices."""

import argparse
import sys
import zipfile
from pathlib import Path
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract import extract_and_parse_invoice
from src.chunk import create_chunks_from_invoice
from src.embed import embed_chunks
from src.index import index_chunks


def unzip_invoices(zip_path: str, extract_to: str = "data/invoices"):
    """Unzip the invoice files."""
    print(f"Extracting invoices from {zip_path} to {extract_to}...")

    Path(extract_to).mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    # Find all PDF files
    pdf_files = list(Path(extract_to).glob("**/*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")
    return pdf_files


def run_ingestion(zip_path: str, sample: int = None, extract_to: str = "data/invoices"):
    """Run the full ingestion pipeline."""
    print("\n" + "="*80)
    print("RAG PIPELINE INGESTION")
    print("="*80 + "\n")

    # 1. Unzip
    pdf_files = unzip_invoices(zip_path, extract_to)

    # Limit to sample if specified
    if sample:
        pdf_files = pdf_files[:sample]
        print(f"Limiting to {sample} invoices")

    print(f"Processing {len(pdf_files)} invoices...\n")

    # 2. Extract and chunk
    all_chunks = []
    successful_invoices = 0

    print("Step 1: Extracting and chunking invoices...")
    for pdf_path in tqdm(pdf_files, desc="Extracting"):
        invoice = extract_and_parse_invoice(pdf_path)
        if invoice and invoice.get("invoice_id"):
            chunks = create_chunks_from_invoice(invoice)
            if chunks:
                all_chunks.extend(chunks)
                successful_invoices += 1
        # If extraction fails, skip gracefully

    print(f"✓ Extracted {successful_invoices}/{len(pdf_files)} invoices")
    print(f"✓ Created {len(all_chunks)} chunks")

    if not all_chunks:
        print("No chunks created. Exiting.")
        return

    # 3. Embed
    print(f"\nStep 2: Embedding {len(all_chunks)} chunks...")
    chunk_texts = [chunk["text"] for chunk in all_chunks]

    try:
        embeddings = embed_chunks(chunk_texts)
        print(f"✓ Created {len(embeddings)} embeddings")
    except Exception as e:
        print(f"Error embedding chunks: {e}")
        return

    # 4. Index
    print("\nStep 3: Indexing into Chroma...")
    try:
        index_chunks(all_chunks, embeddings, persist_dir="data/chroma_db")
        print("✓ Indexed successfully")
    except Exception as e:
        print(f"Error indexing: {e}")
        return

    # Print summary
    print(f"\n{'='*80}")
    print("INGESTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total invoices processed: {successful_invoices}")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Chroma DB location: data/chroma_db")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest invoices into RAG pipeline")
    parser.add_argument(
        "--zip-path",
        type=str,
        default="invoices.zip",
        help="Path to the invoices.zip file"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Limit to N invoices (for testing)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/invoices",
        help="Directory to extract invoices to"
    )

    args = parser.parse_args()

    run_ingestion(args.zip_path, args.sample, args.output)
