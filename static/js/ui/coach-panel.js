/**
 * Coach report panel — accuracy ring, stats, key moments, patterns.
 */

/**
 * Show coach loading state with progress.
 * @param {number} current
 * @param {number} total
 */
export function showCoachProgress(current, total) {
    hide('coach-empty');
    hide('coach-report');
    show('coach-loading');

    const pct = Math.round((current / total) * 100);
    const fill = document.getElementById('coach-progress-fill');
    const label = document.getElementById('coach-progress-label');
    if (fill) fill.style.width = pct + '%';
    if (label) label.textContent = `Analyzing move ${current} of ${total}...`;
}

/**
 * Display the coach report.
 * @param {object} report - from generateCoachReport()
 * @param {function} onClickMoment - callback(moveIndex)
 */
export function showCoachReport(report, onClickMoment) {
    hide('coach-loading');
    hide('coach-empty');
    show('coach-report');

    // Accuracy ring
    const pctEl = document.getElementById('accuracy-pct');
    if (pctEl) pctEl.textContent = report.accuracy + '%';

    const ringFg = document.getElementById('ring-fg');
    if (ringFg) {
        const circumference = 2 * Math.PI * 42;
        const offset = circumference - (report.accuracy / 100) * circumference;
        ringFg.style.strokeDasharray = circumference;
        ringFg.style.strokeDashoffset = offset;
        ringFg.style.stroke = report.accuracy >= 70 ? 'var(--green)'
            : report.accuracy >= 50 ? 'var(--orange)' : 'var(--red)';
    }

    // Stats
    for (const q of ['best', 'good', 'inaccuracy', 'mistake', 'blunder']) {
        const el = document.getElementById('stat-' + q);
        if (el) el.textContent = report.stats[q] || 0;
    }

    // Key moments
    const mc = document.getElementById('coach-moments');
    if (mc) {
        mc.innerHTML = '';
        if (report.keyMoments.length === 0) {
            mc.innerHTML = '<div class="empty-state" style="padding:20px"><p>No significant mistakes found!</p></div>';
        } else {
            mc.innerHTML = '<div style="margin-bottom:8px"><span class="section-label">Key Moments</span></div>';
            for (const m of report.keyMoments) {
                const moveLabel = m.side === 'white' ? `${m.moveNumber}. ${m.played}` : `${m.moveNumber}... ${m.played}`;
                const altHtml = m.bestMove ? `<div class="moment-alt">Better: <strong>${m.bestMove}</strong></div>` : '';

                const card = document.createElement('div');
                card.className = `moment-card ${m.quality}`;
                card.innerHTML = `
                    <div class="moment-header">
                        <span class="moment-move">${moveLabel}</span>
                        <span class="moment-quality ${m.quality}">${m.quality}</span>
                    </div>
                    <div class="moment-body">${m.suggestion}</div>
                    ${altHtml}
                    <div class="moment-click">Click to view position</div>
                `;
                card.querySelector('.moment-click').addEventListener('click', () => onClickMoment(m.index));
                mc.appendChild(card);
            }
        }
    }

    // Patterns
    const pc = document.getElementById('coach-patterns');
    if (pc) {
        pc.innerHTML = '';
        if (report.patterns.length) {
            pc.innerHTML = '<div style="margin-bottom:8px;margin-top:8px"><span class="section-label">Patterns</span></div>';
            for (const p of report.patterns) {
                const icon = p.type === 'strength' ? '\u2713' : '\u25b3';
                const tag = document.createElement('div');
                tag.className = `pattern-tag ${p.type}`;
                tag.innerHTML = `<span class="pattern-icon">${icon}</span>${p.text}`;
                pc.appendChild(tag);
            }
        }
    }
}

/** Show the empty state. */
export function showCoachEmpty() {
    hide('coach-loading');
    hide('coach-report');
    show('coach-empty');
}

function show(id) { const el = document.getElementById(id); if (el) el.style.display = ''; }
function hide(id) { const el = document.getElementById(id); if (el) el.style.display = 'none'; }
