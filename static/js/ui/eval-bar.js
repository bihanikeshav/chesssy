/**
 * Eval bar rendering.
 */

import { formatEval } from '../engine/stockfish.js';

let currentEvalCp = 0;
let targetEvalCp = 0;
let animFrame = null;

/**
 * Update the eval bar with new evaluation.
 * @param {number} cp - Centipawns from White's perspective
 * @param {number|null} mate
 */
export function updateEvalBar(cp, mate) {
    const fill = document.getElementById('eval-fill');
    const label = document.getElementById('eval-label');
    if (!fill || !label) return;

    let pct;
    if (mate != null) {
        pct = mate > 0 ? 95 : 5;
    } else {
        const clamped = Math.max(-500, Math.min(500, cp || 0));
        pct = 50 + (clamped / 500) * 45;
    }

    fill.style.height = pct + '%';
    label.textContent = formatEval(cp, mate);

    // Color class
    label.className = 'eval-label';
    if (mate != null) {
        label.classList.add(mate > 0 ? 'positive' : 'negative');
    } else if (cp > 50) {
        label.classList.add('positive');
    } else if (cp < -50) {
        label.classList.add('negative');
    }
}
