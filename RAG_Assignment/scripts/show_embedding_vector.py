"""
SHOW COMPLETE EMBEDDING VECTOR
================================
Display all 384 dimensions of the query embedding.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embed import embed_single_chunk
import json

print("\n" + "█"*80)
print("█" + " "*78 + "█")
print("█" + " "*15 + "COMPLETE EMBEDDING VECTOR: ALL 384 DIMENSIONS" + " "*19 + "█")
print("█" + " "*78 + "█")
print("█"*80)

query = "What electrical problems were found on Fords?"

print(f"\n{'═'*80}")
print("QUESTION")
print(f"{'═'*80}\n")
print(f'"{query}"\n')
print(f"Length: {len(query)} characters")
print(f"Words: {len(query.split())} words")

# Get embedding
print(f"\nEmbedding the question using sentence-transformers/all-MiniLM-L6-v2...")
embedding = embed_single_chunk(query)

print(f"\n✅ Embedding created!")
print(f"   Type: List of floats")
print(f"   Dimensions: {len(embedding)}")

# DISPLAY 1: All 384 values
print(f"\n{'═'*80}")
print("FORMAT 1: ALL 384 DIMENSIONS (Raw Values)")
print(f"{'═'*80}\n")

print("embedding = [")
for i, val in enumerate(embedding):
    # Every 8 values per line
    if i % 8 == 0:
        print(f"  {i:3d}: ", end="")
    print(f"{val:8.4f}", end="")
    if (i + 1) % 8 == 0:
        print(",")
    else:
        print(", ", end="")

print("]\n")

# DISPLAY 2: Dimensions grouped
print(f"{'═'*80}")
print("FORMAT 2: GROUPED BY 10 DIMENSIONS")
print(f"{'═'*80}\n")

for group in range(0, len(embedding), 10):
    end = min(group + 10, len(embedding))
    dims = embedding[group:end]
    print(f"Dimensions {group:3d}-{end-1:3d}: {[round(x, 4) for x in dims]}")

print()

# DISPLAY 3: Specific dimension ranges
print(f"{'═'*80}")
print("FORMAT 3: KEY DIMENSION RANGES")
print(f"{'═'*80}\n")

ranges = [
    ("First 10", 0, 10),
    ("Dimensions 50-60", 50, 60),
    ("Dimensions 100-110", 100, 110),
    ("Dimensions 190-200 (middle)", 190, 200),
    ("Dimensions 300-310", 300, 310),
    ("Last 10", 374, 384),
]

for name, start, end in ranges:
    dims = embedding[start:end]
    print(f"{name:.<30} {[round(x, 4) for x in dims]}")

print()

# DISPLAY 4: Statistics
print(f"{'═'*80}")
print("FORMAT 4: VECTOR STATISTICS")
print(f"{'═'*80}\n")

import numpy as np

arr = np.array(embedding)
print(f"Min value:             {np.min(arr):10.4f}")
print(f"Max value:             {np.max(arr):10.4f}")
print(f"Mean value:            {np.mean(arr):10.4f}")
print(f"Median value:          {np.median(arr):10.4f}")
print(f"Std deviation:         {np.std(arr):10.4f}")
print(f"Vector magnitude:      {np.linalg.norm(arr):10.4f}")
print(f"Sum of all values:     {np.sum(arr):10.4f}")
print()

# Count positive/negative
positive = sum(1 for x in embedding if x > 0)
negative = sum(1 for x in embedding if x < 0)
zero = sum(1 for x in embedding if x == 0)

print(f"Positive values:       {positive:3d} ({100*positive/len(embedding):.1f}%)")
print(f"Negative values:       {negative:3d} ({100*negative/len(embedding):.1f}%)")
print(f"Zero values:           {zero:3d} ({100*zero/len(embedding):.1f}%)")

# Distribution
ranges_count = [
    ("< -0.1", sum(1 for x in embedding if x < -0.1)),
    ("-0.1 to -0.05", sum(1 for x in embedding if -0.1 <= x < -0.05)),
    ("-0.05 to 0", sum(1 for x in embedding if -0.05 <= x < 0)),
    ("0 to 0.05", sum(1 for x in embedding if 0 <= x < 0.05)),
    ("0.05 to 0.1", sum(1 for x in embedding if 0.05 <= x < 0.1)),
    ("> 0.1", sum(1 for x in embedding if x > 0.1)),
]

print(f"\nValue distribution:")
for range_name, count in ranges_count:
    bar_length = int(count / 2)
    print(f"  {range_name:.<15} {count:3d} {'█' * bar_length}")

print()

# DISPLAY 5: JSON format
print(f"{'═'*80}")
print("FORMAT 5: JSON FORMAT")
print(f"{'═'*80}\n")

print(json.dumps({
    "query": query,
    "embedding": [round(x, 6) for x in embedding],
    "dimensions": len(embedding),
    "stats": {
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "mean": round(float(np.mean(arr)), 4),
        "magnitude": round(float(np.linalg.norm(arr)), 4),
    }
}, indent=2))

print()

# DISPLAY 6: Python list format
print(f"{'═'*80}")
print("FORMAT 6: PYTHON LIST (Copy-Paste Ready)")
print(f"{'═'*80}\n")

print("embedding_vector = [")
for i in range(0, len(embedding), 8):
    batch = embedding[i:i+8]
    line = ", ".join([f"{x:.6f}" for x in batch])
    print(f"    {line},")
print("]")

print()

# DISPLAY 7: Comparison visualization
print(f"{'═'*80}")
print("FORMAT 7: VISUAL DISTRIBUTION (ASCII Histogram)")
print(f"{'═'*80}\n")

print("Distribution of values across the 384 dimensions:\n")

# Create histogram
hist, bin_edges = np.histogram(embedding, bins=20)
bin_width = (bin_edges[1] - bin_edges[0])

for i, (count, edge) in enumerate(zip(hist, bin_edges[:-1])):
    bar = "█" * int(count / 3)
    print(f"{edge:7.3f}: {bar} ({count})")

print()

# DISPLAY 8: High and low values
print(f"{'═'*80}")
print("FORMAT 8: HIGHEST AND LOWEST VALUES")
print(f"{'═'*80}\n")

indexed = [(i, v) for i, v in enumerate(embedding)]
indexed.sort(key=lambda x: x[1], reverse=True)

print("TOP 10 HIGHEST VALUES:")
for rank, (idx, val) in enumerate(indexed[:10], 1):
    print(f"  {rank:2d}. Dimension {idx:3d}: {val:8.4f}")

print("\nTOP 10 LOWEST VALUES:")
for rank, (idx, val) in enumerate(indexed[-10:], 1):
    print(f"  {rank:2d}. Dimension {idx:3d}: {val:8.4f}")

print()

# DISPLAY 9: What this vector represents
print(f"{'═'*80}")
print("FORMAT 9: WHAT THIS VECTOR REPRESENTS")
print(f"{'═'*80}\n")

print(f"""
This 384-dimensional vector is a SEMANTIC REPRESENTATION of:
  "{query}"

What it captures:
  ✓ Meaning: "electrical" (similar to wiring, circuits, power)
  ✓ Context: "problems" (similar to issues, faults, damage)
  ✓ Domain: "Fords" (similar to vehicles, trucks, cars)
  ✓ Intent: Looking for service issues on Ford vehicles

How it's used:
  1. Compared to all 1,564 chunk embeddings
  2. Cosine similarity calculated for each
  3. Top-5 most similar chunks returned
  4. Those chunks sent to Claude

Why 384 dimensions?
  - Model: sentence-transformers/all-MiniLM-L6-v2
  - Architecture: 6-layer BERT
  - Output: 384-dimensional dense vector
  - Trade-off: Small enough to be fast, large enough to capture meaning

The numbers themselves don't have direct interpretations.
They're abstract learned representations from training on millions of texts.
But together, they capture semantic similarity!
""")

# DISPLAY 10: Chroma query format
print(f"{'═'*80}")
print("FORMAT 10: HOW THIS IS SENT TO CHROMA")
print(f"{'═'*80}\n")

print(f"""
collection.query(
    query_embeddings=[
        {embedding}
    ],
    n_results=5,
)

Or in API form:

POST /query
{{
  "query_embeddings": [[
    {", ".join([f"{x:.6f}" for x in embedding[:10]])}...
  ]],
  "n_results": 5
}}
""")

print(f"\n{'═'*80}\n")

# DISPLAY 11: File output
print(f"{'═'*80}")
print("FORMAT 11: SAVE TO FILE")
print(f"{'═'*80}\n")

# Save to JSON file
output_file = "data/query_embedding.json"
Path("data").mkdir(exist_ok=True)

with open(output_file, "w") as f:
    json.dump({
        "query": query,
        "embedding": [round(x, 6) for x in embedding],
        "dimensions": len(embedding),
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "statistics": {
            "min": round(float(np.min(arr)), 6),
            "max": round(float(np.max(arr)), 6),
            "mean": round(float(np.mean(arr)), 6),
            "magnitude": round(float(np.linalg.norm(arr)), 6),
            "positive_count": int(positive),
            "negative_count": int(negative),
        }
    }, f, indent=2)

print(f"✅ Saved embedding to: {output_file}")

print(f"\n{'═'*80}\n")
