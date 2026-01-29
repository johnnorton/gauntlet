# RAG Pipeline for Truck Service Invoices

A Naive RAG (Retrieval-Augmented Generation) pipeline that indexes truck service invoices and answers natural language questions about service history, complaints, repairs, and parts.

## What This Project Does

This system builds a searchable knowledge base from truck service invoices (PDFs) and answers questions using a combination of retrieval and generation:

1. **Extraction**: Parses PDF invoices to extract structured data (invoice ID, customer, vehicle, service blocks)
2. **Chunking**: Splits invoices by service block, each chunk contains full context
3. **Embedding**: Uses Voyage AI to create vector embeddings of chunks
4. **Indexing**: Stores chunks and embeddings in Chroma (local vector database)
5. **Retrieval**: Finds relevant chunks for user queries
6. **Generation**: Uses Claude to synthesize answers from retrieved context

## RAG Pattern: Why Naive RAG?

This project uses **Naive RAG** (also called "basic RAG"):
- Query → Embed → Retrieve → Generate
- No reranking, filtering, or iteration
- No complex query expansion or decomposition
- Simple, effective, and fast to implement

**Why this approach?** For this use case (truck service invoices), a straightforward retrieval + generation approach is sufficient:
- Invoices are self-contained documents
- Questions are domain-specific
- No need for complex retrieval logic
- Focus is on getting working code quickly

## Chunking Strategy

Chunks are created **by service block**, not by full invoice:

```
Invoice: INV17981
Date: 7/19/2016
Customer: Junior Bloodworth
Vehicle: 2009 International Prostar Premium
VIN: 2HSCUAPR19C697882
Mileage: 699,550

Complaint: check and replace batteries
Cause: replace batteries (Service Request)
Correction: replace all batteries
Parts Used: GP-31 Battery Core (4x)
Labor: 0.25 hours
```

**Why?** This approach:
- Creates multiple chunks per invoice (one per service)
- Preserves full context (customer, vehicle, date)
- Allows fine-grained retrieval
- Handles multi-service invoices well

## Project Structure

```
invoice-rag/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env                        # API keys (not in repo)
├── .env.example                # Template for .env
├── src/
│   ├── extract.py              # PDF extraction and parsing
│   ├── chunk.py                # Service block chunking
│   ├── embed.py                # Voyage AI embeddings
│   ├── index.py                # Chroma indexing
│   ├── retrieve.py             # Similarity search
│   ├── generate.py             # Claude generation
│   └── pipeline.py             # End-to-end orchestration
├── eval/
│   ├── test_queries.json       # Test queries and ground truth
│   ├── recall_eval.py          # Recall@k evaluation
│   └── groundedness_eval.py    # Groundedness evaluation
├── scripts/
│   ├── ingest.py               # Bulk ingestion pipeline
│   └── query.py                # Interactive query script
└── data/
    ├── invoices/               # Extracted PDF files
    └── chroma_db/              # Vector database (persistent)
```

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

The `.env` file should already have your API keys:
```bash
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa_...
```

## Usage

### Ingest Invoices

Extract, chunk, embed, and index 100 invoices:

```bash
python scripts/ingest.py --zip-path invoices.zip --sample 100
```

**Options:**
- `--zip-path`: Path to invoices.zip (default: invoices.zip)
- `--sample`: Limit to N invoices (default: all)
- `--output`: Directory to extract to (default: data/invoices)

**Output:** Indexed data in `data/chroma_db/`

### Query the System

Ask a question about the invoices:

```bash
python scripts/query.py "What jobs involved electrical issues?"
```

**Output:**
- Generated answer based on retrieved context
- Source invoice IDs
- Retrieved chunks with similarity scores

### Run Evaluations

#### Recall@k Evaluation

Measures: _Of the relevant invoices, how many did we retrieve?_

```bash
python -m eval.recall_eval
```

Evaluates:
- All test queries with ground truth labels
- Default k=5 (top 5 chunks)
- Reports average recall across queries

#### Groundedness Evaluation

Measures: _Is the answer supported by the retrieved context?_

```bash
python -m eval.groundedness_eval
```

Evaluates:
- All test queries
- Claude judges if answer is grounded (1-5 scale)
- Reports average groundedness score

### Evaluation Metrics Explained

**Recall@k:**
- Definition: `(relevant docs retrieved) / (total relevant docs)`
- Range: 0-1 (higher is better)
- Measures retrieval effectiveness
- Must have ground truth labels in `eval/test_queries.json`

**Groundedness:**
- Definition: How well the answer is supported by retrieved context
- Scale: 1-5 (5 is fully grounded)
- Measures generation quality
- Higher score = fewer hallucinations

## Implementation Details

### Embedding
- **Model**: Voyage AI `voyage-3-lite` (fast, high quality)
- **Batch size**: 128 chunks per batch
- **Dimension**: 1024-dimensional vectors

### Vector Database
- **Tool**: Chroma (local, no setup needed)
- **Similarity metric**: Cosine distance
- **Persistence**: Local disk storage

### Generation
- **Model**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Max tokens**: 1024
- **System prompt**: Instructs Claude to answer only from context

## Key Design Decisions

1. **Chunk by service block**: Allows multiple chunks per invoice while maintaining context
2. **Voyage AI embeddings**: Recommended by Anthropic, high quality
3. **Chroma persistence**: Local DB, no cloud dependencies
4. **Naive RAG**: Simple, effective, easy to debug
5. **Both eval metrics**: Recall measures retrieval, groundedness measures generation

## Example Queries

Try these after ingestion:

```bash
python scripts/query.py "What jobs involved oil pressure problems?"
python scripts/query.py "Battery replacements on International trucks"
python scripts/query.py "What repairs were done for warning lights?"
python scripts/query.py "Jobs involving brake repairs"
python scripts/query.py "Transmission problems"
```

## Troubleshooting

**No results from queries?**
- Ensure ingestion completed successfully
- Check that `data/chroma_db/` exists and contains data
- Verify API keys are set

**Embedding errors?**
- Check VOYAGE_API_KEY is set
- Verify API key is valid

**Generation errors?**
- Check ANTHROPIC_API_KEY is set
- Verify API key is valid

**Low recall scores?**
- Increase k (retrieve more chunks)
- Update test_queries.json with real invoice IDs from ingestion
- Check chunking strategy captures relevant information

## Next Steps / Improvements

- Implement advanced RAG (reranking, multi-hop queries)
- Add metadata filtering (by date, customer, vehicle type)
- Implement query expansion with Claude
- Add ablation studies
- Optimize embedding batch size
- Add semantic search explanations
