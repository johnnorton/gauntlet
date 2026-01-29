"""Query script to run the RAG pipeline."""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import run_rag_pipeline


def main():
    parser = argparse.ArgumentParser(description="Query the RAG pipeline")
    parser.add_argument("query", type=str, help="The question to ask")
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of chunks to retrieve (default: 5)"
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print("RAG QUERY")
    print("="*80 + "\n")

    print(f"Query: {args.query}\n")

    # Run pipeline
    result = run_rag_pipeline(args.query, k=args.k, persist_dir="data/chroma_db")

    # Print answer
    print("ANSWER:")
    print("-" * 80)
    print(result["answer"])
    print("-" * 80)

    # Print sources
    print(f"\nSOURCES ({len(result['source_invoices'])} invoices):")
    for invoice_id in result["source_invoices"]:
        print(f"  - {invoice_id}")

    # Print retrieved chunks
    print(f"\nRETRIEVED CHUNKS ({len(result['retrieved_chunks'])} total):")
    print("-" * 80)
    for i, chunk in enumerate(result["retrieved_chunks"], 1):
        print(f"\n[{i}] Invoice: {chunk['metadata'].get('invoice_id')}")
        print(f"    Similarity: {chunk['similarity']:.2f}")
        print(f"    Text: {chunk['text'][:150]}...")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
