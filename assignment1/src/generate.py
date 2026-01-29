"""Generation using Claude API."""

import os
from typing import List, Dict, Any, Tuple
from anthropic import Anthropic


def initialize_claude_client():
    """Initialize Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    return Anthropic(api_key=api_key)


def generate_answer(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
) -> Tuple[str, List[str]]:
    """
    Generate an answer using Claude based on retrieved context.

    Returns the answer text and list of source invoice IDs.
    """
    client = initialize_claude_client()

    # Format retrieved chunks for the prompt
    context = "\n\n---\n\n".join([chunk["text"] for chunk in retrieved_chunks])

    system_prompt = """You are a helpful assistant that answers questions about truck service invoices.
Answer questions based ONLY on the provided invoice context. If the answer is not in the context,
say "I cannot find this information in the provided invoices." Be specific and cite the invoices when relevant."""

    user_prompt = f"""Based on the following invoice context, answer this question: {query}

INVOICE CONTEXT:
{context}

Please provide a clear, concise answer based only on the information above."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    answer = response.content[0].text

    # Extract unique invoice IDs from sources
    source_invoices = list(set([
        chunk["metadata"].get("invoice_id", "UNKNOWN")
        for chunk in retrieved_chunks
    ]))

    return answer, source_invoices
