# Chesssy

Browser-first chess analysis and AI coaching with Stockfish WASM, game review, theory retrieval, and BYOK LLM explanations.

Live app: https://chesssy.web.app/

Chesssy is built around a simple idea: strong engine lines are useful, but most players need to know whether a move was human-findable, what pattern they missed, and what to try next. The app runs analysis in the browser, turns engine output into coaching signals, and can optionally use an OpenAI-compatible LLM for short explanations.

## What It Does

- Analyze live positions with Stockfish NNUE running in a Web Worker.
- Step through FEN, PGN, and imported games.
- Classify moves as best, good, inaccuracy, mistake, or blunder.
- Score how findable a candidate move is for different skill levels.
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

Most chess analysis tools explain what the engine wants. Chesssy tries to explain what a player could reasonably have found, why a move was hard, and what pattern to learn from it.
