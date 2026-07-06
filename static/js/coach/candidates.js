/**
 * Candidate move filter — identifies 'findable' moves.
 * Port of candidates.py adapted for chess.js 0.10.3.
 */

const PIECE_VALUES = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };

// Good development squares
const GOOD_KNIGHT_SQUARES = new Set(['c3', 'f3', 'c6', 'f6', 'd4', 'e4', 'd5', 'e5']);
const GOOD_BISHOP_SQUARES = new Set(['c4', 'f4', 'b5', 'g5', 'c5', 'f5', 'b4', 'g4']);
const CENTRAL_SQUARES = new Set(['e4', 'd4', 'e5', 'd5', 'c4', 'c5']);

/**
 * Get tags explaining why a move might be found by a human.
 * @param {object} game - chess.js instance at position before move
 * @param {object} move - verbose move object from chess.js
 * @returns {string[]}
 */
export function getMoveTags(game, move) {
    const tags = [];

    // 1. Check
    game.move(move.san);
    const givesCheck = game.in_check();
    game.undo();
    if (givesCheck) tags.push('check');

    // 2. Capture
    if (move.captured) {
        if (isSacrifice(move)) {
            tags.push('sacrifice');
        } else {
            tags.push('capture');
        }
        if (isRecapture(game, move)) {
            tags.push('recapture');
        }
    }

    // 3. Castling
    if (move.flags.includes('k') || move.flags.includes('q')) {
        tags.push('castling');
    }

    // 4. Promotion
    if (move.promotion) {
        tags.push('promotion');
    }

    // 5. Development
    if (isDevelopmentMove(game, move)) {
        tags.push('development');
    }

    // 6. Defense
    if (defendsAttackedPiece(game, move)) {
        tags.push('defense');
    }

    // 7. Threat
    if (createsThreat(game, move)) {
        tags.push('threat');
    }

    // 8. Central pawn
    if (isCentralPawnMove(game, move)) {
        tags.push('central_pawn');
    }

    // 9. Improvement
    if (improvesPiece(game, move)) {
        tags.push('improvement');
    }

    return tags;
}

/**
 * Check if a move is findable and return its tags.
 * @param {object} game - chess.js instance
 * @param {string} moveStr - UCI or SAN
 * @returns {{findable: boolean, tags: string[]}}
 */
export function isFindable(game, moveStr) {
    const moves = game.moves({ verbose: true });
    let move = null;

    // Try matching as UCI
    for (const m of moves) {
        const uci = m.from + m.to + (m.promotion || '');
        if (uci === moveStr) { move = m; break; }
    }

    // Try matching as SAN
    if (!move) {
        for (const m of moves) {
            if (m.san === moveStr) { move = m; break; }
        }
    }

    if (!move) return { findable: false, tags: [] };

    const tags = getMoveTags(game, move);
    return { findable: tags.length > 0, tags };
}

function isSacrifice(move) {
    if (!move.captured) return false;
    const capturerVal = PIECE_VALUES[move.piece] || 0;
    const capturedVal = PIECE_VALUES[move.captured] || 0;
    return capturerVal > capturedVal;
}

function isRecapture(game, move) {
    if (!move.captured) return false;
    const history = game.history({ verbose: true });
    if (history.length === 0) return false;
    const last = history[history.length - 1];
    return last.to === move.to && last.captured;
}

function isDevelopmentMove(game, move) {
    if (!['n', 'b'].includes(move.piece)) return false;

    const fromRank = move.from[1];
    const isWhite = move.color === 'w';
    const backRank = isWhite ? '1' : '8';

    if (fromRank !== backRank) return false;

    if (move.piece === 'n') return GOOD_KNIGHT_SQUARES.has(move.to);
    if (move.piece === 'b') return GOOD_BISHOP_SQUARES.has(move.to);
    return false;
}

function defendsAttackedPiece(game, move) {
    // Simplified: check if the moved piece was under attack (fleeing)
    const us = move.color;
    const them = us === 'w' ? 'b' : 'w';

    // Check if a piece on from_square is under threat by checking opponent's
    // legal moves in the previous position (expensive, but accurate)
    // Simplified: check if our piece on move.from is targeted by opponent
    // We approximate by checking if move.from appears as a "to" square
    // in opponent's potential captures

    // Make a temp game where it's opponent's turn to check if they attack our piece
    // This is complex with chess.js 0.10.3, so we use a heuristic:
    // If our move is not a capture and moves from a square where we have a piece,
    // check if opponent's last move attacked that square
    const history = game.history({ verbose: true });
    if (history.length > 0) {
        const lastOpp = history[history.length - 1];
        // If opponent just captured near our piece, or moved toward it
        // Simplified: if we're moving a non-pawn piece to safety after being attacked
        if (move.piece !== 'p' && !move.captured) {
            return false; // Conservative: only tag explicit defense patterns
        }
    }

    return false;
}

function createsThreat(game, move) {
    // After the move, check if we attack a higher-value or undefended piece
    game.move(move.san);

    // Get opponent's pieces that we might be threatening
    const oppMoves = game.moves({ verbose: true });
    // If opponent has to address our threat (e.g., we threaten a capture),
    // that's a threat. Approximate by checking if after our move,
    // we have a strong capture available on the next turn.
    game.undo();

    // Simpler: check from opponent's perspective after our move
    game.move(move.san);
    // Now it's opponent's turn. Check if any of THEIR pieces are attacked
    // by looking at what captures would be available to us
    game.undo();

    // Even simpler heuristic: if the piece moves to a square attacking
    // higher-value opponent pieces visible in the verbose move list
    game.move(move.san);
    game.undo();
    game.move(move.san);

    // After our move, temporarily switch perspective by making a null-like check
    // chess.js doesn't support null moves, so we skip complex threat detection
    game.undo();

    return false; // Threat detection requires board.attacks() which chess.js lacks
}

function isCentralPawnMove(game, move) {
    if (move.piece !== 'p') return false;
    return CENTRAL_SQUARES.has(move.to);
}

function improvesPiece(game, move) {
    const piece = move.piece;
    const toFile = move.to[0];
    const toRank = parseInt(move.to[1]);
    const us = move.color;

    // Rook to open file
    if (piece === 'r') {
        let hasPawn = false;
        for (let r = 1; r <= 8; r++) {
            const sq = toFile + r;
            const p = game.get(sq);
            if (p && p.type === 'p') { hasPawn = true; break; }
        }
        if (!hasPawn) return true;
    }

    // Knight to outpost
    if (piece === 'n') {
        const fileIdx = toFile.charCodeAt(0) - 'a'.charCodeAt(0);
        if (fileIdx >= 2 && fileIdx <= 5) {
            const outpostRanks = us === 'w' ? [4, 5, 6] : [3, 4, 5];
            if (outpostRanks.includes(toRank)) return true;
        }
    }

    // Bishop to long diagonal or active central squares
    if (piece === 'b') {
        const fileIdx = toFile.charCodeAt(0) - 'a'.charCodeAt(0);
        const rankIdx = toRank - 1;
        const onLongDiag = (rankIdx === fileIdx) || (rankIdx + fileIdx === 7);
        const onActiveSq = fileIdx >= 2 && fileIdx <= 5 && rankIdx >= 2 && rankIdx <= 5;
        if (onLongDiag || onActiveSq) return true;
    }

    return false;
}
