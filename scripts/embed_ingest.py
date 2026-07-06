"""
Embed chess theory docs with all-MiniLM-L6-v2 and upload to Qdrant.

Reads:  scripts/data/classified_theory.jsonl
Writes: Qdrant collection 'chess_theory' (384-dim Cosine vectors)

Usage:
    pip install sentence-transformers qdrant-client
    export QDRANT_URL=https://xxx.qdrant.io:6333
    export QDRANT_KEY=your-admin-key
    python scripts/embed_ingest.py
"""

import json
import os
import uuid
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

QDRANT_URL  = os.getenv("QDRANT_URL", "")
QDRANT_KEY  = os.getenv("QDRANT_KEY", "")
COLLECTION  = "chess_theory"
MODEL_NAME  = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_SIZE = 384
BATCH_SIZE  = 64

INPUT_PATH  = Path(__file__).parent / "data" / "classified_theory.jsonl"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_docs() -> list[dict]:
    if not INPUT_PATH.exists():
        print(f"ERROR: {INPUT_PATH} not found. Run classify_theory.py first.")
        return []
    docs: list[dict] = []
    with open(INPUT_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def doc_uuid(doc_id: str) -> str:
    """Stable UUID derived from doc id string."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))


def build_points(docs: list[dict], embeddings) -> list[PointStruct]:
    points: list[PointStruct] = []
    for doc, vec in zip(docs, embeddings):
        points.append(PointStruct(
            id=doc_uuid(doc["id"]),
            vector=vec.tolist(),
            payload={
                "title":       doc.get("title", ""),
                "content":     doc.get("content", ""),
                "category":    doc.get("category", ""),
                "subcategory": doc.get("subcategory", ""),
                "difficulty":  doc.get("difficulty", "intermediate"),
                "tags":        doc.get("tags", []),
                "source":      doc.get("source", ""),
                "url":         doc.get("url", ""),
                "doc_id":      doc.get("id", ""),
            },
        ))
    return points


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Chess Theory Embedder & Ingestion ===\n")

    if not QDRANT_URL or not QDRANT_KEY:
        print("ERROR: Set QDRANT_URL and QDRANT_KEY environment variables.")
        print("  export QDRANT_URL=https://xxx.qdrant.io:6333")
        print("  export QDRANT_KEY=your-admin-key")
        return

    # --- Load docs -----------------------------------------------------------
    docs = load_docs()
    if not docs:
        return
    print(f"Loaded {len(docs)} documents from {INPUT_PATH}")

    # --- Load model ----------------------------------------------------------
    print(f"\nLoading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded.")

    # --- Embed ---------------------------------------------------------------
    texts = [doc["content"] for doc in docs]
    print(f"\nEmbedding {len(texts)} documents (batch_size={BATCH_SIZE})...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,   # L2-normalise for Cosine similarity
    )
    print(f"Embedding complete. Shape: {embeddings.shape}")

    # --- Qdrant setup --------------------------------------------------------
    print(f"\nConnecting to Qdrant: {QDRANT_URL}")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)

    # (Re)create collection with proper 384-dim vectors
    try:
        client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION} (size={VECTOR_SIZE}, distance=Cosine)")
    except Exception as exc:
        print(f"Collection setup: {exc}")
        # Collection may already exist — proceed to upsert
        pass

    # --- Build PointStructs --------------------------------------------------
    points = build_points(docs, embeddings)

    # --- Upload in batches ---------------------------------------------------
    print(f"\nUploading {len(points)} points in batches of {BATCH_SIZE}...")
    total_uploaded = 0
    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i : i + BATCH_SIZE]
        client.upsert(collection_name=COLLECTION, points=batch)
        total_uploaded += len(batch)
        print(f"  Uploaded {total_uploaded}/{len(points)}")

    # --- Verify --------------------------------------------------------------
    info = client.get_collection(COLLECTION)
    print(f"\nDone! {info.points_count} points in collection '{COLLECTION}'.")


if __name__ == "__main__":
    main()
