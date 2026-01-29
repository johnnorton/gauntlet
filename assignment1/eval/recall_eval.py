"""Recall@k evaluation for RAG retrieval."""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieve import retrieve


def load_test_queries(filepath: str = "eval/test_queries.json"):
    """Load test queries with expected invoice IDs."""
    with open(filepath) as f:
        return json.load(f)


def calculate_recall_at_k(retrieved_ids: list, expected_ids: list) -> float:
    """Calculate recall@k for a single query."""
    if not expected_ids:
        # If no expected IDs, can't calculate recall
        return None

    expected_set = set(expected_ids)
    retrieved_set = set(retrieved_ids)
    intersection = expected_set & retrieved_set
    recall = len(intersection) / len(expected_set) if expected_set else 0
    return recall


def run_recall_eval(k: int = 5, persist_dir: str = "data/chroma_db"):
    """Run recall@k evaluation on test queries."""
    test_queries = load_test_queries()

    results = []
    recalls = []

    print(f"\n{'='*80}")
    print(f"RECALL@{k} EVALUATION")
    print(f"{'='*80}\n")

    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected_ids = test.get("expected_invoice_ids", [])

        if not expected_ids:
            print(f"[{i}] Skipping (no ground truth): {query}")
            continue

        # Retrieve top-k
        retrieved_chunks = retrieve(query, k=k, persist_dir=persist_dir)
        retrieved_ids = list(set([
            chunk["metadata"].get("invoice_id")
            for chunk in retrieved_chunks
        ]))

        # Calculate recall
        recall = calculate_recall_at_k(retrieved_ids, expected_ids)

        if recall is not None:
            recalls.append(recall)

        print(f"[{i}] Query: {query}")
        print(f"    Expected IDs: {expected_ids}")
        print(f"    Retrieved IDs: {retrieved_ids}")
        print(f"    Recall@{k}: {recall:.2f}" if recall is not None else "    Recall: N/A")
        print()

        results.append({
            "query": query,
            "expected_ids": expected_ids,
            "retrieved_ids": retrieved_ids,
            "recall": recall,
        })

    # Summary statistics
    if recalls:
        avg_recall = sum(recalls) / len(recalls)
        print(f"{'='*80}")
        print(f"Average Recall@{k}: {avg_recall:.2f}")
        print(f"Queries evaluated: {len(recalls)}/{len(test_queries)}")
        print(f"{'='*80}\n")
    else:
        print(f"No queries with ground truth found to evaluate.")

    return results


if __name__ == "__main__":
    run_recall_eval()
