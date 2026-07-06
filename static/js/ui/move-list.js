/**
 * PGN move list rendering and navigation.
 */

let moveListEl = null;
let onNavigate = null;
let moves = []; // [{moveSan, moveUci, fenBefore, moveNumber, side, quality}]
let currentIndex = -1;

/**
 * Initialize the move list.
 * @param {HTMLElement} el - Container element
 * @param {function} navCallback - called with (index) on click
 */
export function initMoveList(el, navCallback) {
    moveListEl = el;
    onNavigate = navCallback;
}

/**
 * Set moves and render the list.
 * @param {object[]} newMoves
 */
export function setMoves(newMoves) {
    moves = newMoves;
    currentIndex = -1;
    render();
}

/** Get current moves array. */
export function getMoves() {
    return moves;
}

/**
 * Set the active move index and highlight it.
 * @param {number} idx
 */
export function setActiveIndex(idx) {
    currentIndex = idx;
    highlightActive();
}

/**
 * Update quality class on a specific move cell.
 * @param {number} idx
 * @param {string} quality
 */
export function setMoveQuality(idx, quality) {
    if (moves[idx]) moves[idx].quality = quality;
    const cell = moveListEl?.querySelector(`[data-idx="${idx}"]`);
    if (cell) {
        cell.classList.remove('best', 'good', 'inaccuracy', 'mistake', 'blunder');
        if (quality) cell.classList.add(quality);
    }
}

function render() {
    if (!moveListEl) return;
    moveListEl.innerHTML = '';

    let num = 0;
    moves.forEach((m, i) => {
        if (m.side === 'white') {
            num++;
            const numSpan = document.createElement('span');
            numSpan.className = 'move-num';
            numSpan.textContent = num + '.';
            moveListEl.appendChild(numSpan);
        }

        const cell = document.createElement('span');
        cell.className = 'move-cell';
        if (m.quality) cell.classList.add(m.quality);
        cell.dataset.idx = i;
        cell.textContent = m.moveSan;
        cell.addEventListener('click', () => onNavigate?.(i));
        moveListEl.appendChild(cell);
    });
}

function highlightActive() {
    if (!moveListEl) return;
    moveListEl.querySelectorAll('.move-cell').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.idx) === currentIndex);
    });

    // Scroll into view
    const active = moveListEl.querySelector('.move-cell.active');
    if (active) active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}
