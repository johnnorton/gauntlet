"""Groundedness evaluation for RAG generation."""

import json
import sys
from pathlib import Path
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import run_rag_pipeline


def load_test_queries(filepath: str = "eval/test_queries.json"):
    """Load test queries."""
    with open(filepath) as f:
        return json.load(f)


def evaluate_groundedness(answer: str, context: str) -> dict:
    """
    Use Claude to evaluate groundedness of an answer against context.

    Returns a dict with groundedness_score (1-5) and explanation.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")

    client = Anthropic(api_key=api_key)

    prompt = f"""You are evaluating the groundedness of an AI-generated answer based on provided context.

CONTEXT (from invoices):
{context}

ANSWER TO EVALUATE:
{answer}

Please evaluate if the answer is grounded in the provided context. Consider:
1. Does the answer stay true to the facts in the context?
2. Are there any claims in the answer not supported by the context?
3. Does the answer appropriately acknowledge limitations when information is not in context?

Provide:
1. A groundedness score from 1-5 where:
   - 1 = Completely ungrounded / contains false claims
   - 2 = Mostly ungrounded with some correct elements
   - 3 = Partially grounded but has unsupported claims
   - 4 = Well grounded with minor issues
   - 5 = Fully grounded and accurate

2. A brief explanation (1-2 sentences)

Format your response as:
SCORE: [1-5]
EXPLANATION: [your explanation]"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse response
    response_text = response.content[0].text
    lines = response_text.strip().split("\n")

    score = None
    explanation = ""

    for line in lines:
        if line.startswith("SCORE:"):
            try:
                score = int(line.split(":"))[1].strip()
            except:
                score = None
        elif line.startswith("EXPLANATION:"):
            explanation = line.split(":", 1)[1].strip()

    return {
        "score": score,
        "explanation": explanation,
    }


def run_groundedness_eval(persist_dir: str = "data/chroma_db"):
    """Run groundedness evaluation on test queries."""
    test_queries = load_test_queries()

    results = []
    scores = []

    print(f"\n{'='*80}")
    print("GROUNDEDNESS EVALUATION")
    print(f"{'='*80}\n")

    for i, test in enumerate(test_queries, 1):
        query = test["query"]

        # Run RAG pipeline
        rag_result = run_rag_pipeline(query, k=5, persist_dir=persist_dir)
        answer = rag_result["answer"]
        context = "\n\n---\n\n".join([
            chunk["text"] for chunk in rag_result["retrieved_chunks"]
        ])

        # Evaluate groundedness
        groundedness = evaluate_groundedness(answer, context)
        score = groundedness.get("score")

        if score:
            scores.append(score)

        print(f"[{i}] Query: {query}")
        print(f"    Answer: {answer[:100]}...")
        print(f"    Groundedness Score: {score}/5" if score else "    Groundedness Score: N/A")
        if groundedness.get("explanation"):
            print(f"    Explanation: {groundedness['explanation']}")
        print()

        results.append({
            "query": query,
            "answer": answer,
            "groundedness_score": score,
            "explanation": groundedness.get("explanation", ""),
        })

    # Summary statistics
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"{'='*80}")
        print(f"Average Groundedness Score: {avg_score:.2f}/5")
        print(f"Queries evaluated: {len(scores)}/{len(test_queries)}")
        print(f"{'='*80}\n")
    else:
        print("Could not evaluate groundedness for any queries.")

    return results


if __name__ == "__main__":
    run_groundedness_eval()
