# Complete Retrieval Flow: Query → Answer

## The 4-Step Process

### Step 1: User Query
```
User: "What electrical problems were found on Fords?"
```

### Step 2: Embed Query (Convert to Vector)
```python
query_embedding = embed_single_chunk(query)
# Result: 384-dimensional vector
# [-0.0547, 0.0037, 0.0323, 0.0888, ..., 0.0057]
```

### Step 3: Search Chroma Database
```python
results = collection.query(
    query_embeddings=[query_embedding],  # Your query as vector
    n_results=5,                           # Get top 5 matches
)
```

**What Chroma Does:**
1. Takes your query embedding (384 dimensions)
2. Compares it to all 1,564 chunk embeddings
3. Calculates cosine similarity for each
4. Sorts by similarity score (highest first)
5. Returns top 5

**Results:**
```
Rank 1: Invoice 26847505 (Similarity: 0.4639)
Rank 2: Invoice 5010     (Similarity: 0.4551)
Rank 3: Invoice DET      (Similarity: 0.4510)
Rank 4: Invoice 101      (Similarity: 0.4488)
Rank 5: Invoice 1115321  (Similarity: 0.4478)
```

### Step 4: Format for Claude & Generate Answer

#### What Gets Passed to Claude

```
SYSTEM PROMPT:
"You are a helpful assistant that answers questions about truck
service invoices. Answer questions based ONLY on the provided
invoice context. If the answer is not in the context, say
'I cannot find this information in the provided invoices.'"

USER PROMPT:
"Based on the following invoice context, answer this question:
What electrical problems were found on Fords?

INVOICE CONTEXT:
[5 chunks joined with "---" separator]

Invoice: 26847505
Date: 1/13/2025
Customer: PO Service Writer Unit #
...
Complaint: CUSTOMER STATES CHECK CHARGING SYSTEM LIGHT IS ON
Cause: Customer request
Correction: PULLED CODES FOR AIR DAM ACTIVE GRILL SHUTTER
AND ALTERNATOR COMMUNICATION FAULTS...
---

Invoice: 5010
Date: 3/15/2024
...
Complaint: Fix Wiring throughout box (trouble shoot)
---

[3 more chunks...]

Please provide a clear, concise answer based only on the
information above."
```

#### What Claude Sees
- **Model**: claude-sonnet-4-20250514
- **Max tokens**: 1024
- **Context**: 6,261 characters (5 invoice chunks)
- **Instructions**: Only use provided context

#### Claude's Response
```
Based on the provided invoices, electrical problems found on Fords
include:

1. Charging system light/Alternator communication faults
   (Invoice 26847505) - Resolved by checking active grill shutter
   and thawing ice buildup

2. Wiring issues throughout electrical box (Invoice 5010) -
   Repaired with wiring troubleshooting

3. Electrical system wiring damage (Invoice DET) - Repair behind
   left midturn marker with heat shrink connectors

4. ABS wiring problems (Invoice 1115321) - Passenger side wheel
   speed sensor wiring issues resolved
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER ENTERS QUERY                        │
│        "What electrical problems were found on Fords?"      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │   EMBED QUERY (src/embed.py)    │
        │   sentence-transformers model   │
        │   Model: all-MiniLM-L6-v2       │
        └──────────────┬───────────────────┘
                       │
                       ↓ 384-dimensional vector
                       │ [-0.0547, 0.0037, ...]
                       │
        ┌──────────────────────────────────┐
        │   CHROMA DATABASE (src/index.py) │
        │   1,564 chunks stored            │
        │   HNSW index for fast search     │
        │                                   │
        │   1. Load all 1,564 embeddings  │
        │   2. Calculate similarity        │
        │   3. Sort by score               │
        │   4. Return top 5                │
        └──────────────┬───────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │     TOP-5 RESULTS                │
        ├──────────────────────────────────┤
        │ Rank 1: Invoice 26847505 (0.464) │
        │ Rank 2: Invoice 5010 (0.455)     │
        │ Rank 3: Invoice DET (0.451)      │
        │ Rank 4: Invoice 101 (0.449)      │
        │ Rank 5: Invoice 1115321 (0.448)  │
        └──────────────┬───────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │   FORMAT FOR CLAUDE              │
        │   (src/generate.py)              │
        │                                   │
        │   - Join chunks with "---"      │
        │   - Add system prompt            │
        │   - Add user question            │
        │   - Create JSON for API          │
        └──────────────┬───────────────────┘
                       │
                       ↓ ~6,261 character prompt
                       │
        ┌──────────────────────────────────┐
        │   SEND TO CLAUDE API             │
        │   model: claude-sonnet-4         │
        │   max_tokens: 1024               │
        │                                   │
        │   System: "Answer based on..."  │
        │   User: "What electrical..."    │
        │   Context: [5 chunks]            │
        └──────────────┬───────────────────┘
                       │
                       ↓ ~600-1200ms processing
                       │
        ┌──────────────────────────────────┐
        │   CLAUDE'S RESPONSE              │
        │                                   │
        │   "Based on invoices, electrical │
        │    problems include:              │
        │                                   │
        │    1. Charging system light...  │
        │    2. Wiring issues...          │
        │    3. Electrical damage..."     │
        └──────────────┬───────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │   RETURN TO USER                 │
        │   + Extract source invoices      │
        │   + [26847505, 5010, DET, ...]  │
        └──────────────────────────────────┘
```

---

## Code Flow (From src/retrieve.py → src/generate.py)

### retrieve.py
```python
def retrieve(query: str, k: int = 5):
    # 1. Embed the query
    query_embedding = embed_single_chunk(query)

    # 2. Get Chroma collection
    collection = get_collection()

    # 3. Query Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    # 4. Format results with similarity scores
    retrieved_chunks = []
    for doc, metadata, distance in zip(...):
        similarity = 1 - distance  # Convert distance to similarity
        retrieved_chunks.append({
            "text": doc,
            "metadata": metadata,
            "similarity": similarity,
        })

    return retrieved_chunks  # List of dicts with text + metadata
```

### generate.py
```python
def generate_answer(query: str, retrieved_chunks: List[Dict]):
    # 1. Join chunks into context
    context = "\n\n---\n\n".join([
        chunk["text"] for chunk in retrieved_chunks
    ])

    # 2. Create system prompt
    system_prompt = """You are a helpful assistant..."""

    # 3. Create user prompt with context
    user_prompt = f"""Based on the following invoice context,
    answer this question: {query}

    INVOICE CONTEXT:
    {context}

    Please provide a clear, concise answer..."""

    # 4. Call Claude API
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    # 5. Return answer + source invoices
    answer = response.content[0].text
    source_invoices = [chunk["metadata"]["invoice_id"]
                       for chunk in retrieved_chunks]

    return answer, source_invoices
```

---

## Key Numbers

| Step | Time | Data Size |
|------|------|-----------|
| Embed query | ~1-2 ms | 384 floats |
| Load 1,564 embeddings | ~5-10 ms | 1,564 × 384 = 600KB |
| HNSW search | <1 ms | Negligible |
| Format results | <1 ms | ~500 chars per chunk |
| **Retrieval Total** | **~10-15 ms** | |
| Send to Claude | ~50-100 ms | ~6KB (prompt) |
| Claude processes | ~500-1000 ms | ~ 1KB (response) |
| **Total End-to-End** | **~600-1200 ms** | |

---

## What's Actually Passed to Claude

### The Full Prompt Structure
```
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "system": "You are a helpful assistant...",
  "messages": [
    {
      "role": "user",
      "content": "Based on the following invoice context, answer this
      question: What electrical problems were found on Fords?

      INVOICE CONTEXT:
      [6,261 characters of 5 invoice chunks]

      Please provide a clear, concise answer based only on the
      information above."
    }
  ]
}
```

### What Claude Receives
- **System instructions**: How to behave (answer from context only)
- **User question**: "What electrical problems were found on Fords?"
- **Context**: 5 most relevant invoice chunks (by similarity)
- **Constraints**: Can't make up info, must cite sources

### What Claude Returns
- **Answer**: Grounded in the provided context
- **Sources**: Invoice IDs extracted from metadata

---

## The RAG Promise

**Without Retrieval:**
```
Claude: "Ford F-150s are known to have electrical issues with..."
(Claude is guessing/hallucinating)
```

**With Retrieval:**
```
Claude: "Based on Invoices 26847505, 5010, and DET, Ford electrical
problems found include charging system faults, wiring damage, and
alternator communication issues."
(Claude is citing actual invoice data)
```

---

## Summary

1. **User asks**: "What electrical problems were found on Fords?"
2. **Embed**: Convert to 384-dim vector (-0.0547, 0.0037, ...)
3. **Search**: Find 5 most similar chunks in Chroma (0.4639, 0.4551, ...)
4. **Format**: Join chunks with "---" separator
5. **Send to Claude**: System prompt + question + 5 chunks (~6KB)
6. **Claude generates**: Answer based ONLY on provided context
7. **Return**: Answer + source invoice IDs

**Total time**: ~600-1200 ms (0.6-1.2 seconds)
**Total tokens**: ~1500-2000 tokens (retrieved + response)
**Success**: Answer is grounded in real data, not hallucinated!
