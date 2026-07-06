# Third-Party Notices

This repository includes or integrates with third-party software and services.

## Bundled Runtime Assets

- `static/lib/stockfish/stockfish-nnue-16-single.js`
- `static/lib/stockfish/stockfish-nnue-16-single.wasm`

These files are Stockfish/stockfish.js assets. The bundled JavaScript header states that Stockfish is released under the GNU General Public License v3 and that the JavaScript/WebAssembly build was compiled by Niklas Fiekas using Emscripten and Binaryen.

Upstream references:

- https://stockfishchess.org/
- https://github.com/official-stockfish/Stockfish
- https://github.com/niklasf/stockfish.js

Review GPL obligations before redistributing modified binaries or before choosing a top-level project license.

## Bundled UI Libraries

- `static/lib/chessboard-1.0.0.min.js`
- `static/lib/chessboard-1.0.0.min.css`

The bundled header identifies chessboard.js v1.0.0 as MIT licensed.

- `static/lib/chess.min.js`

This is a minified chess.js build. Verify the exact upstream version before publishing a formal release.

- `static/lib/jquery-3.7.1.min.js`

jQuery is distributed under the MIT license.

## Services And APIs

Chesssy can integrate with:

- Firebase Hosting / Analytics
- Lichess APIs
- Qdrant Cloud through a Cloudflare Worker proxy
- User-configured OpenAI-compatible LLM providers

Service credentials and tokens should not be committed to this repository.
