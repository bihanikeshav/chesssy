/**
 * Board UI — chessboard.js wrapper, drag/drop, promotion, arrows, tap-to-move.
 *
 * Tap-to-move strategy:
 *   - Own piece tap: detected via onDrop(source, source) — chessboard.js same-square
 *   - Destination tap: detected via touchend/click on empty squares or opponent pieces
 *     (chessboard.js doesn't start drag for these, so events propagate)
 *   - Opponent piece with selection: handled in onDragStart returning false
 */

let board = null;
let game = null;
let isFlipped = false;
let onMoveCallback = null;

// Arrow state
let currentArrow = null;

// Tap-to-move state
let selectedSquare = null;

/**
 * Initialize the board.
 * @param {function} onMove - callback({san, uci, fen}) when a move is made
 */
export function initBoard(onMove) {
    game = new Chess();
    onMoveCallback = onMove;

    board = Chessboard('board', {
        draggable: true,
        position: 'start',
        pieceTheme: '/img/chesspieces/wikipedia/{piece}.png',
        onDragStart,
        onDrop,
        onSnapEnd: () => board.position(game.fen()),
    });

    $(window).resize(() => {
        board.resize();
        if (currentArrow) redrawArrow();
    });

    const boardEl = document.getElementById('board');
    if (boardEl) {
        // Prevent page scroll when touching the board
        boardEl.style.touchAction = 'none';

        // Catch taps on empty squares & opponent pieces (chessboard.js won't drag these)
        // Use pointerup — works on both mobile and desktop, fires even when chessboard.js
        // doesn't start a drag (empty square, opponent piece, onDragStart returned false)
        boardEl.addEventListener('pointerup', onBoardPointerUp);
    }

    return { board, game };
}

// ===== Exports =====

export function getGame() { return game; }
export function getBoard() { return board; }
export function getFen() { return game.fen(); }
export function getFlipped() { return isFlipped; }

export function flipBoard() {
    board.flip();
    isFlipped = !isFlipped;
    const top = document.getElementById('player-top-name');
    const bot = document.getElementById('player-bottom-name');
    if (top && bot) {
        const t = top.textContent;
        top.textContent = bot.textContent;
        bot.textContent = t;
    }
    if (currentArrow) redrawArrow();
}

export function resetBoard() {
    game.reset();
    board.start();
    clearSelection();
}

export function setPosition(fen) {
    game.load(fen);
    board.position(fen);
    clearSelection();
}

export function undoMove() {
    const m = game.undo();
    if (m) board.position(game.fen());
    clearSelection();
    return m;
}

export function playUci(uci) {
    const from = uci.substring(0, 2);
    const to = uci.substring(2, 4);
    const promo = uci[4] || undefined;
    const m = game.move({ from, to, promotion: promo });
    if (m) {
        board.position(game.fen());
        clearSelection();
        return m;
    }
    return null;
}

export function playSan(san) {
    const m = game.move(san);
    if (m) {
        board.position(game.fen());
        clearSelection();
    }
    return m;
}

export function setPlayerNames(white, black) {
    const top = document.getElementById('player-top-name');
    const bot = document.getElementById('player-bottom-name');
    if (isFlipped) {
        if (top) top.textContent = white;
        if (bot) bot.textContent = black;
    } else {
        if (top) top.textContent = black;
        if (bot) bot.textContent = white;
    }
}

export function drawArrow(from, to) {
    currentArrow = { from, to };
    redrawArrow();
}

export function clearArrows() {
    currentArrow = null;
    const svg = document.getElementById('arrow-svg');
    if (svg) svg.remove();
}

// ===== Chessboard.js callbacks =====

function onDragStart(source, piece) {
    if (game.game_over()) return false;

    const turn = game.turn();
    const isOwn = (turn === 'w' && piece[0] === 'w') || (turn === 'b' && piece[0] === 'b');

    if (!isOwn) {
        // Opponent piece tapped — if we have selection, try capture
        if (selectedSquare) {
            tryMoveFromSelection(source);
        }
        return false;
    }

    // Own piece — allow drag. Clear selection (will be re-set in onDrop if same-square tap)
    clearSelection();
    return true;
}

function onDrop(source, target) {
    if (source === target) {
        // Same square = tap. Toggle selection.
        if (selectedSquare === source) {
            clearSelection();
        } else {
            clearSelection();
            selectSquare(source);
        }
        return 'snapback';
    }

    // Actual drag to different square
    const piece = game.get(source);

    // Promotion check
    if (piece && piece.type === 'p') {
        const rank = target[1];
        if ((piece.color === 'w' && rank === '8') || (piece.color === 'b' && rank === '1')) {
            const test = game.move({ from: source, to: target, promotion: 'q' });
            if (!test) return 'snapback';
            game.undo();
            showPromoDialog(source, target, piece.color);
            return;
        }
    }

    const move = game.move({ from: source, to: target, promotion: 'q' });
    if (!move) return 'snapback';
    clearSelection();
    emitMove(move);
}

// ===== Pointer handler for empty squares / opponent pieces =====

function onBoardPointerUp(e) {
    if (!selectedSquare) return;

    // Find which square was tapped
    const el = document.elementFromPoint(e.clientX, e.clientY);
    if (!el) return;
    const squareEl = el.closest('[data-square]');
    if (!squareEl) return;

    const sq = squareEl.dataset.square;
    if (!sq || sq === selectedSquare) return;

    const piece = game.get(sq);
    const turn = game.turn();

    // If tapping own piece, reselect (handled by onDragStart/onDrop)
    if (piece && piece.color === turn) return;

    // Empty square or opponent piece — try the move
    tryMoveFromSelection(sq);
}

// ===== Tap-to-move logic =====

function tryMoveFromSelection(targetSq) {
    if (!selectedSquare) return;

    const from = selectedSquare;
    const to = targetSq;
    const movingPiece = game.get(from);

    // Promotion check
    if (movingPiece && movingPiece.type === 'p') {
        const rank = to[1];
        if ((movingPiece.color === 'w' && rank === '8') || (movingPiece.color === 'b' && rank === '1')) {
            const test = game.move({ from, to, promotion: 'q' });
            if (test) {
                game.undo();
                clearSelection();
                showPromoDialog(from, to, movingPiece.color);
                return;
            }
        }
    }

    const move = game.move({ from, to, promotion: 'q' });
    if (move) {
        clearSelection();
        board.position(game.fen());
        emitMove(move);
    } else {
        clearSelection();
    }
}

function selectSquare(sq) {
    selectedSquare = sq;
    highlightSquare(sq, 'selected');

    const moves = game.moves({ square: sq, verbose: true });
    for (const m of moves) {
        highlightSquare(m.to, game.get(m.to) ? 'capture-hint' : 'move-hint');
    }
}

function clearSelection() {
    selectedSquare = null;
    document.querySelectorAll('.square-highlight').forEach(el => el.remove());
}

function highlightSquare(sq, type) {
    const squareEl = document.querySelector(`[data-square="${sq}"]`);
    if (!squareEl) return;

    const dot = document.createElement('div');
    dot.className = 'square-highlight ' + type;
    squareEl.style.position = 'relative';
    squareEl.appendChild(dot);
}

// ===== Promotion =====

function showPromoDialog(source, target, color) {
    const pieces = ['q', 'r', 'b', 'n'];
    const prefix = color === 'w' ? 'w' : 'b';
    const names = { q: 'Q', r: 'R', b: 'B', n: 'N' };
    const container = document.getElementById('promotion-pieces');
    if (!container) return;

    container.innerHTML = '';
    for (const p of pieces) {
        const img = document.createElement('img');
        img.className = 'promotion-piece';
        img.src = `/img/chesspieces/wikipedia/${prefix}${names[p]}.png`;
        img.addEventListener('click', () => {
            const m = game.move({ from: source, to: target, promotion: p });
            if (m) {
                document.getElementById('promotion-overlay').classList.remove('active');
                board.position(game.fen());
                emitMove(m);
            }
        });
        container.appendChild(img);
    }
    document.getElementById('promotion-overlay').classList.add('active');
}

// ===== Arrow drawing =====

function redrawArrow() {
    const oldSvg = document.getElementById('arrow-svg');
    if (oldSvg) oldSvg.remove();

    if (!currentArrow) return;

    const boardEl = document.getElementById('board');
    if (!boardEl) return;

    const rect = boardEl.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;
    if (w === 0 || h === 0) return;

    const sqSize = w / 8;

    // Append SVG directly to the board element for perfect alignment
    boardEl.style.position = 'relative';

    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.id = 'arrow-svg';
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    svg.style.cssText = `position:absolute;top:0;left:0;width:${w}px;height:${h}px;pointer-events:none;z-index:10;`;

    const from = squareToCoords(currentArrow.from, rect);
    const to = squareToCoords(currentArrow.to, rect);

    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len < 1) return;

    const ux = dx / len;
    const uy = dy / len;
    const px = -uy; // perpendicular
    const py = ux;

    // Arrow proportions (Lichess-like)
    const sw = sqSize * 0.15;       // shaft width (thin)
    const hw = sqSize * 0.42;       // head width
    const hl = sqSize * 0.32;       // head length

    // Start: offset from source center so it doesn't overlap the piece
    const sx = from.x + ux * sqSize * 0.32;
    const sy = from.y + uy * sqSize * 0.32;

    // Tip: slightly before target center
    const tx = to.x - ux * sqSize * 0.12;
    const ty = to.y - uy * sqSize * 0.12;

    // Head base (where triangle starts / shaft ends)
    const bx = tx - ux * hl;
    const by = ty - uy * hl;

    // Draw as single polygon: combined shaft + arrowhead shape
    // This avoids overlap artifacts between separate shaft and head
    const pts = [
        `${sx + px * sw / 2},${sy + py * sw / 2}`,
        `${bx + px * sw / 2},${by + py * sw / 2}`,
        `${bx + px * hw / 2},${by + py * hw / 2}`,
        `${tx},${ty}`,
        `${bx - px * hw / 2},${by - py * hw / 2}`,
        `${bx - px * sw / 2},${by - py * sw / 2}`,
        `${sx - px * sw / 2},${sy - py * sw / 2}`,
    ];

    const poly = document.createElementNS(ns, 'polygon');
    poly.setAttribute('points', pts.join(' '));
    poly.setAttribute('fill', 'rgba(100, 180, 80, 0.7)');
    svg.appendChild(poly);

    boardEl.appendChild(svg);
}

function emitMove(move) {
    if (onMoveCallback) {
        onMoveCallback({
            san: move.san,
            uci: move.from + move.to + (move.promotion || ''),
            fen: game.fen(),
            move,
        });
    }
}

function squareToCoords(sq, boardRect) {
    // Use actual DOM element positions for pixel-perfect centering
    const squareEl = document.querySelector(`[data-square="${sq}"]`);
    if (squareEl) {
        const r = squareEl.getBoundingClientRect();
        return {
            x: r.left - boardRect.left + r.width / 2,
            y: r.top - boardRect.top + r.height / 2,
        };
    }
    // Fallback
    const sqSize = boardRect.width / 8;
    const file = sq.charCodeAt(0) - 'a'.charCodeAt(0);
    const rank = parseInt(sq[1]) - 1;
    const x = isFlipped ? (7 - file) * sqSize + sqSize / 2 : file * sqSize + sqSize / 2;
    const y = isFlipped ? rank * sqSize + sqSize / 2 : (7 - rank) * sqSize + sqSize / 2;
    return { x, y };
}
