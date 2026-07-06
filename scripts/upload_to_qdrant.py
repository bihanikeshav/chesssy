"""
Standalone: embed all seed docs with all-MiniLM-L6-v2 and upload to Qdrant.
Bypasses knowledge/__init__.py (chromadb incompatible with Python 3.14).

Usage:
    python scripts/upload_to_qdrant.py
"""
import importlib.util, os, uuid, sys
from pathlib import Path

# Load seed_data.py directly without triggering knowledge/__init__.py
spec = importlib.util.spec_from_file_location(
    "seed_data",
    Path(__file__).parent.parent / "knowledge" / "seed_data.py",
)
seed_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed_module)
get_seed_documents = seed_module.get_seed_documents

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_KEY = os.getenv("QDRANT_KEY", "")
COLLECTION  = os.getenv("QDRANT_COLLECTION", "chess_theory")
MODEL_NAME  = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_SIZE = 384
BATCH_SIZE  = 64

def main():
    if not QDRANT_URL or not QDRANT_KEY:
        raise SystemExit(
            "Set QDRANT_URL and QDRANT_KEY before uploading to Qdrant. "
            "See .env.example for the expected variables."
        )

    docs = get_seed_documents()
    print(f"Loaded {len(docs)} seed documents")

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)

    # Recreate collection with 384-dim vectors
    try:
        client.delete_collection(COLLECTION)
        print(f"Deleted existing collection: {COLLECTION}")
    except Exception:
        pass

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection: {COLLECTION} (size={VECTOR_SIZE}, distance=COSINE)")

    # Build texts and metadata
    texts = []
    metas = []
    for doc in docs:
        meta = doc.get("metadata", {})
        content = doc.get("content", "")
        # Prepend title to improve embedding quality
        title = meta.get("title", "")
        texts.append(f"{title}. {content}" if title else content)
        metas.append({
            "doc_id":      doc.get("id", ""),
            "title":       title,
            "content":     content,
            "category":    meta.get("category", ""),
            "subcategory": meta.get("subcategory", ""),
            "difficulty":  meta.get("difficulty", "intermediate"),
            "tags":        [meta.get("subcategory", ""), meta.get("category", "")],
        })

    # Embed all at once
    print(f"Embedding {len(texts)} documents...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    # Build points
    points = []
    for i, (meta, vec) in enumerate(zip(metas, embeddings)):
        points.append(PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, meta["doc_id"] or str(i))),
            vector=vec.tolist(),
            payload=meta,
        ))

    # Upload in batches
    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i : i + BATCH_SIZE]
        client.upsert(collection_name=COLLECTION, points=batch)
        print(f"  Uploaded {min(i + BATCH_SIZE, len(points))}/{len(points)}")

    info = client.get_collection(COLLECTION)
    print(f"\nDone! {info.points_count} points in '{COLLECTION}'")

if __name__ == "__main__":
    main()
