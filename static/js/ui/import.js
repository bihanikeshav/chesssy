/**
 * Game import — PGN, FEN, Lichess/Chess.com URLs.
 * Client-side only (no backend).
 */

import { toast } from './toast.js';

/**
 * Parse import input and return game data.
 * @param {string} input - URL, PGN, or FEN
 * @returns {Promise<{type: string, moves?: object[], headers?: object, fen?: string, error?: string}>}
 */
export async function parseImport(input) {
    input = input.trim();
    if (!input) return { type: 'error', error: 'Empty input' };

    // Lichess URL
    if (input.includes('lichess.org')) {
        return importFromLichess(input);
    }

    // Chess.com URL
    if (input.includes('chess.com')) {
        return { type: 'error', error: 'Chess.com URLs may not work due to CORS. Paste the PGN directly instead.' };
    }

    // PGN (contains move list or headers)
    if (input.includes('[') || input.match(/1\.\s*\w/)) {
        return importPgn(input);
    }

    // FEN (contains / which is typical)
    if (input.includes('/')) {
        return importFen(input);
    }

    return { type: 'error', error: 'Paste a Lichess URL, PGN, or FEN' };
}

async function importFromLichess(url) {
    try {
        // Extract game ID
        const match = url.match(/lichess\.org\/(?:game\/)?([a-zA-Z0-9]{8,12})/);
        if (!match) return { type: 'error', error: 'Invalid Lichess URL' };

        const gameId = match[1].substring(0, 8); // First 8 chars are the game ID
        const res = await fetch(`https://lichess.org/game/export/${gameId}`, {
            headers: { 'Accept': 'application/x-chess-pgn' },
            signal: AbortSignal.timeout(10000),
        });

        if (!res.ok) return { type: 'error', error: `Lichess returned ${res.status}` };

        const pgn = await res.text();
        return importPgn(pgn);
    } catch (e) {
        return { type: 'error', error: `Lichess import failed: ${e.message}` };
    }
}

function importPgn(pgnText) {
    const game = new Chess();

    // Try loading PGN
    const loaded = game.load_pgn(pgnText);
    if (!loaded) {
        return { type: 'error', error: 'Invalid PGN format' };
    }

    // Extract headers
    const headers = {};
    const headerRegex = /\[(\w+)\s+"([^"]*)"]/g;
    let hm;
    while ((hm = headerRegex.exec(pgnText)) !== null) {
        headers[hm[1]] = hm[2];
    }

    // Extract moves with FEN-before for each
    const history = game.history({ verbose: true });
    const tempGame = new Chess();
    const moves = [];

    for (let i = 0; i < history.length; i++) {
        const fenBefore = tempGame.fen();
        const h = history[i];
        const moveNumber = Math.ceil((i + 1) / 2);
        const side = h.color === 'w' ? 'white' : 'black';

        moves.push({
            moveSan: h.san,
            moveUci: h.from + h.to + (h.promotion || ''),
            fenBefore,
            moveNumber,
            side,
        });

        tempGame.move(h.san);
    }

    // Result
    const result = headers.Result || game.header()?.Result || '*';

    return {
        type: 'pgn',
        moves,
        headers,
        result,
    };
}

function importFen(fen) {
    const game = new Chess();
    const valid = game.load(fen);
    if (!valid) {
        return { type: 'error', error: 'Invalid FEN' };
    }
    return { type: 'fen', fen };
}
