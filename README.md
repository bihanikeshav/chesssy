# Chesssy

Browser-first chess analysis and AI coaching with Stockfish WASM, game review, theory retrieval, and BYOK LLM explanations.

Live app: https://chesssy.web.app/

I built the first version of Chesssy in early 2025 because engine analysis kept answering a slightly wrong question for me.

When I was learning chess more seriously, Stockfish would often suggest a move that was technically best but impossible for me to understand in a real game. I would click through the next few moves, try to reverse-engineer the idea, and still end up wondering: was this move actually findable for someone around my level, or was it just an engine-only resource?

Chesssy tries to answer the question behind the eval bar: why did the engine want this, what pattern was hidden, and what practical alternative could I have found over the board?

## What It Does

- Analyze live positions with Stockfish NNUE running in a Web Worker.
- Step through FEN, PGN, and imported games.
- Classify moves as best, good, inaccuracy, mistake, or blunder.
- Score how findable a candidate move is for different skill levels.
- Suggest more practical alternatives when the engine's top move is too hard to find.
- Generate full-game coach reports with key moments, quality distribution, and an eval graph.
- Show Lichess opening explorer data when a token is configured.
- Retrieve chess theory context from Qdrant through a Cloudflare Worker proxy.
- Explain positions with either rule-based fallbacks or a bring-your-own-key LLM.

## Architecture

The current product is the static browser app:

```text
index.html
  -> static/js/main.js
  -> static/js/board.js
  -> static/js/engine/*       Stockfish WASM orchestration
  -> static/js/coach/*        move facts, findability, reports
  -> static/js/llm/*          BYOK OpenAI-compatible streaming
  -> static/js/knowledge/*    Lichess + Qdrant theory lookup
```

There is also an older Flask/Socket.IO backend prototype in `app.py`, `engine/`, `explainer/`, and `knowledge/`. It is kept as local reference code for the Python analysis pipeline, but the Firebase-hosted app uses the static browser path.

## Quick Start

Serve the static app locally:

```bash
python serve.py
```

Then open:

```text
http://localhost:8000
```

For the optional Python backend prototype:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend path expects a local Stockfish binary and may need path changes outside Windows.

## Optional Integrations

### LLM Explanations

The app supports OpenAI-compatible endpoints. You can use local providers like Ollama or LM Studio, or configure a cloud provider from the settings panel. API keys are stored locally in the browser.

### Lichess

Opening explorer features can use a Lichess token or OAuth flow. Tokens are stored in browser local storage.

### Qdrant Theory Search

The static app talks to Qdrant through a Cloudflare Worker proxy configured in `static/js/knowledge/qdrant.js`. Admin keys should never be placed in browser code. The ingestion scripts use environment variables:

```bash
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_KEY=your-admin-key
QDRANT_COLLECTION=chess_theory
python scripts/upload_to_qdrant.py
```

See `.env.example` for local configuration names.

The repo includes a Cloudflare Worker gateway in `cloudflare/qdrant-worker.js`. It can expose a small read-only chess theory search API:

```text
POST https://<your-worker>.workers.dev/collections/chess_theory/points/query
```

Example request:

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

The browser uses this to pull small theory snippets into the explanation context. The Worker handles CORS and keeps the Qdrant key off the client.

See `cloudflare/README.md` for the Worker contract and deployment notes.

## Security Notes

- Do not commit `.env` or real Qdrant keys.
- Rotate any Qdrant key that has been stored in plaintext before publishing a fork.
- Firebase client config is public client configuration, not a server secret, but Firebase rules and allowed domains should still be reviewed.
- BYOK LLM keys and Lichess tokens live in browser local storage, so this is best treated as a personal/local tool unless hardened further.
- The Qdrant Worker should expose read-only search behavior and should never leak admin credentials to the browser.

## Project Status

This is a working personal product/prototype, not a polished library. The strongest path is the static browser app. The Python backend and scripts are useful references for the analysis and RAG pipeline, but they need cleanup before being treated as production backend code.

## Third-Party Pieces

Chesssy uses:

- Stockfish NNUE / WASM engine assets
- chess.js and chessboard.js
- jQuery
- Firebase Hosting / Analytics
- Lichess APIs
- Qdrant Cloud
- Optional OpenAI-compatible LLM providers

Review third-party licenses before redistributing binaries or vendored assets.

## Why This Exists

Most chess analysis tools explain what the engine wants. That is useful, but it is not always how humans improve.

When you are learning openings, middlegames, or endgames, you need more than `+0.7` and a principal variation. You need to know the reason behind the move, the idea hidden two moves later, and whether the move was realistically visible from your current strength.

Chesssy is built for that gap. It separates engine-best from human-findable, then uses tactical tags, theory retrieval, and short explanations to answer:

- Why did the engine choose this?
- What was the actual idea?
- Could I have found this in a real game?
- If not, what was a more practical move I could have played?

The goal is not to replace strong engines. The goal is to make engine analysis feel more like a coach: still accurate, but aware of the player sitting in front of it.
