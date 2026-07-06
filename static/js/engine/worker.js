/**
 * Stockfish WASM Web Worker wrapper.
 *
 * stockfish.js v10 IS a Web Worker itself — it uses onmessage/postMessage
 * directly. This file is NOT used as a worker; instead, stockfish.js
 * is loaded directly as the worker from the main thread.
 *
 * This file exists as documentation. The actual worker is:
 *   new Worker('/static/lib/stockfish/stockfish-nnue-16-single.js')
 */
