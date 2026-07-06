# Qdrant Worker Gateway

Chesssy uses a Cloudflare Worker as a read-only gateway between the browser and Qdrant Cloud.

The browser should never receive a Qdrant API key. Instead, it sends search requests to the Worker, and the Worker forwards only the allowed read routes to Qdrant.

## Routes

```text
POST /collections/chess_theory/points/query
POST /collections/chess_theory/points/scroll
OPTIONS *
```

## Environment Variables

Set these as Cloudflare Worker secrets or environment variables:

```text
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=<read-only-qdrant-key>
QDRANT_COLLECTION=chess_theory
```

Use a read-only key. Do not use an admin/write key for the public Worker.

## Example Request

```bash
curl -X POST "https://<your-worker>.workers.dev/collections/chess_theory/points/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "text": "rook endgame active king",
      "model": "sentence-transformers/all-minilm-l6-v2"
    },
    "limit": 3,
    "with_payload": true
  }'
```

The response is Qdrant's normal JSON response. The app maps `result.points[*].payload` into short theory snippets.

## Security Notes

- Keep CORS open only if the Worker exposes read-only search.
- Prefer rate limiting before sharing the Worker widely.
- Never add write/update/delete Qdrant routes to this Worker.
- Rotate any key that was previously stored in plaintext before deploying.
