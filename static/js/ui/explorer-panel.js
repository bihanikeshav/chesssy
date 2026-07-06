/**
 * Opening explorer panel — shows game counts and popular moves.
 */

/**
 * Show loading state while waiting for explorer data.
 */
export function showExplorerLoading() {
    const container = document.getElementById('explorer-area');
    if (!container) return;

    container.style.display = '';

    const movesEl = document.getElementById('explorer-moves');
    if (movesEl) {
        movesEl.innerHTML = '<div class="explorer-loading"><span class="dot-loader"><span></span></span></div>';
    }

    const countEl = document.getElementById('explorer-count');
    if (countEl) countEl.textContent = '';

    const nameEl = document.getElementById('opening-name');
    if (nameEl) nameEl.style.display = 'none';
}

/**
 * Render explorer data below engine lines.
 * @param {object|null} data - from queryExplorer()
 */
export function renderExplorer(data) {
    const container = document.getElementById('explorer-area');
    if (!container) return;

    if (!data || !data.moves.length) {
        container.style.display = 'none';
        return;
    }

    container.style.display = '';

    // Opening name
    const nameEl = document.getElementById('opening-name');
    if (nameEl) {
        if (data.opening) {
            nameEl.textContent = `${data.opening.eco} ${data.opening.name}`;
            nameEl.style.display = '';
        } else {
            nameEl.style.display = 'none';
        }
    }

    // Game count
    const countEl = document.getElementById('explorer-count');
    if (countEl) {
        countEl.textContent = `${formatCount(data.totalGames)} games`;
    }

    // Top moves
    const movesEl = document.getElementById('explorer-moves');
    if (!movesEl) return;

    movesEl.innerHTML = '';
    const topMoves = data.moves.slice(0, 5);
    const maxTotal = Math.max(1, ...topMoves.map(m => m.total));

    for (const m of topMoves) {
        const total = m.total;
        const wPct = total > 0 ? Math.round((m.white / total) * 100) : 0;
        const dPct = total > 0 ? Math.round((m.draws / total) * 100) : 0;
        const bPct = total > 0 ? Math.round((m.black / total) * 100) : 0;

        const row = document.createElement('div');
        row.className = 'explorer-row';
        row.innerHTML = `
            <span class="explorer-move">${m.san}</span>
            <div class="explorer-bar-wrap">
                <div class="explorer-bar">
                    <div class="explorer-w" style="width:${wPct}%"></div>
                    <div class="explorer-d" style="width:${dPct}%"></div>
                    <div class="explorer-b" style="width:${bPct}%"></div>
                </div>
            </div>
            <span class="explorer-games">${formatCount(total)}</span>
        `;
        movesEl.appendChild(row);
    }
}

/**
 * Update the opening name in the toolbar.
 * @param {object|null} opening - {eco, name}
 */
export function updateOpeningName(opening) {
    const el = document.getElementById('toolbar-opening');
    if (!el) return;
    if (opening) {
        el.textContent = `${opening.eco} ${opening.name}`;
        el.style.display = '';
    } else {
        el.style.display = 'none';
    }
}

function formatCount(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
    return String(n);
}
