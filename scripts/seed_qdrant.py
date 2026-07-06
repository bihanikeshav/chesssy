"""One-time script: upload chess theory docs to Qdrant cloud."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchAny,
)
from knowledge.seed_data import get_seed_documents

QDRANT_URL = os.getenv('QDRANT_URL', '')
QDRANT_KEY = os.getenv('QDRANT_KEY', '')
COLLECTION = 'chess_theory'

if not QDRANT_URL or not QDRANT_KEY:
    print('Set QDRANT_URL and QDRANT_KEY environment variables.')
    print('  export QDRANT_URL=https://xxx.qdrant.io:6333')
    print('  export QDRANT_KEY=your-admin-key')
    sys.exit(1)

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)

# Create collection with dummy 1-dim vector (filter-only queries)
try:
    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=1, distance=Distance.COSINE),
    )
    print(f'Created collection: {COLLECTION}')
except Exception as e:
    print(f'Collection creation: {e}')

# Upload documents
docs = get_seed_documents()
points = []
for i, doc in enumerate(docs):
    meta = doc.get('metadata', {})
    # Add tags from subcategory + category for filtering
    tags = []
    if meta.get('subcategory'):
        tags.append(meta['subcategory'])
    if meta.get('category'):
        tags.append(meta['category'])

    points.append(PointStruct(
        id=i,
        vector=[0.0],  # dummy vector
        payload={
            'title': meta.get('title', doc.get('id', '')),
            'content': doc.get('content', ''),
            'category': meta.get('category', ''),
            'subcategory': meta.get('subcategory', ''),
            'difficulty': meta.get('difficulty', ''),
            'tags': tags,
            'doc_id': doc.get('id', ''),
        }
    ))

client.upsert(collection_name=COLLECTION, points=points)
print(f'Uploaded {len(points)} documents to {COLLECTION}')

# Verify
info = client.get_collection(COLLECTION)
print(f'Collection has {info.points_count} points')
