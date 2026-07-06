# Chesssy Improvement Plan

This plan is based on the current codebase state before public release.

## 1. Public Repo Hygiene

- Keep `.env`, local caches, binaries, zips, ChromaDB data, and Firebase cache files out of git.
- Rotate the Qdrant keys that previously lived in local plaintext files.
- Add a license once the redistribution story for vendored Stockfish assets is final.
- Decide whether to keep vendored JS libraries or replace them with a build/install step.

## 2. Static App Cleanup

- Treat `index.html` + `static/js/main.js` as the canonical app path.
- Mark `static/js/app.js`, `templates/index.html`, and `app.py` as legacy/backend-prototype code, or remove them after equivalent functionality is confirmed in the static app.
- Move duplicated UI/analysis concepts into one documented flow.
- Add a short architecture diagram to the README once the final public shape is settled.

## 3. Security And Privacy

- Keep Qdrant admin keys server-side only.
- Ensure the Cloudflare Worker is read-only, rate-limited, and does not expose raw Qdrant credentials.
- Add an in-app note that LLM keys and Lichess tokens are stored in browser local storage.
- Consider session-only key storage for users who do not want persistence.
- Review Firebase Analytics events and document what is collected.

## 4. Testing

- Convert `tests/test_core_logic.py` from diagnostic print checks into assertions.
- Add deterministic tests for:
  - move quality thresholds
  - eval perspective handling
  - findability scoring
  - PGN/FEN import parsing
  - coach report summaries
- Add CI that runs linting and the non-engine unit tests first.
- Keep engine-dependent tests optional because Stockfish binaries are platform-specific.

## 5. Portability

- Remove the Windows-only Stockfish path assumption in `config.py`.
- Document static-only mode separately from Python backend mode.
- Add setup notes for macOS/Linux if the backend prototype remains public.
- Avoid committing large Stockfish zips/executables; link to official downloads instead.

## 6. Product Polish

- Add a few curated sample games so visitors can try the app without importing a PGN.
- Add a compact "why this move was hard" panel using the existing findability features.
- Make explanation lengths stricter: one short tactical reason, one practical takeaway.
- Improve empty/error states for missing Lichess tokens, Qdrant proxy failures, and LLM CORS issues.
- Add screenshots or a short GIF to the README.

## 7. RAG Pipeline

- Document the theory ingestion pipeline end to end.
- Move all Qdrant config to environment variables.
- Add a dry-run mode for embedding scripts.
- Add a small public seed dataset so contributors can test retrieval without private infrastructure.

## 8. Repo Visibility

- Pin this repo once the README has screenshots and the static app path is easy to run.
- Keep the project description focused: browser-first chess analysis, Stockfish WASM, RAG, BYOK LLM.
- Avoid overclaiming. This is a strong personal product/prototype, not a production SaaS backend.
