/**
 * Analysis panel — displays move quality, eval change, best move info,
 * rule-based explanation, and AI analysis.
 */

import { formatEval } from '../engine/stockfish.js';

export function showAnalysisLoading() {
    hide('analysis-empty');
    hide('analysis-content');
    show('analysis-loading');
}

export function showAnalysisEmpty() {
    hide('analysis-loading');
    hide('analysis-content');
    show('analysis-empty');
}

/**
 * Display analysis results from MoveFacts.
 */
export function showAnalysisResult(facts) {
    hide('analysis-loading');
    hide('analysis-empty');
    show('analysis-content');

    // Move header + quality
    setText('move-san', facts.playedMoveSan);
    const pill = document.getElementById('quality-pill');
    if (pill) {
        pill.textContent = facts.moveQuality;
        pill.className = 'quality-pill ' + facts.moveQuality;
    }

    const isGood = ['best', 'good'].includes(facts.moveQuality);
    const isBad = ['inaccuracy', 'mistake', 'blunder'].includes(facts.moveQuality);

    // Findability inline (only for best/good moves)
    const findInline = document.getElementById('find-inline');
    if (findInline) {
        if (isGood && facts.findabilityScore != null) {
            renderFindability('find-inline-pct', 'find-inline-label', facts.findabilityScore, facts.findabilityLabel);
            findInline.style.display = '';
        } else {
            findInline.style.display = 'none';
        }
    }

    // Better moves (for mistakes/blunders/inaccuracies)
    const bestInfo = document.getElementById('best-move-info');
    if (bestInfo) {
        const alts = facts.topAlternatives || [];
        if (isBad && alts.length > 0) {
            bestInfo.innerHTML = '';
            renderMoveGroup(bestInfo, 'Better', alts.slice(0, 3));
            bestInfo.style.display = '';
        } else {
            bestInfo.innerHTML = '';
            bestInfo.style.display = 'none';
        }
    }

    // Eval change
    const evBefore = formatEval(facts.evalBeforeCp, facts.mateThreatBefore);
    const evAfter = formatEval(facts.evalAfterCp, facts.mateThreatAfter);

    const evalBeforeEl = document.getElementById('eval-before');
    const evalAfterEl = document.getElementById('eval-after');
    if (evalBeforeEl) {
        evalBeforeEl.textContent = evBefore;
        evalBeforeEl.className = 'eval-num ' + evalClass(facts.evalBeforeCp);
    }
    if (evalAfterEl) {
        evalAfterEl.textContent = evAfter;
        evalAfterEl.className = 'eval-num ' + evalClass(facts.evalAfterCp);
    }

    const cpLossEl = document.getElementById('cp-loss');
    if (cpLossEl) {
        if (facts.cpLoss > 0) {
            cpLossEl.textContent = `\u2212${(facts.cpLoss / 100).toFixed(1)}`;
            cpLossEl.style.display = '';
        } else {
            cpLossEl.style.display = 'none';
        }
    }

    // Threats
    renderThreatTags(facts);

    // Clear explanations (will be filled separately)
    setText('explanation', '');
    const aiText = document.getElementById('ai-analysis-text');
    if (aiText) aiText.innerHTML = '';
    hide('ai-analysis');
}

/**
 * Set the rule-based (non-LLM) explanation text.
 */
export function setExplanationText(text) {
    const el = document.getElementById('explanation');
    if (el) el.innerHTML = formatExplanation(text);
}

/**
 * Show the AI analysis section with loading state.
 */
export function showAiLoading() {
    const section = document.getElementById('ai-analysis');
    const bar = document.getElementById('ai-loading-bar');
    const text = document.getElementById('ai-analysis-text');
    if (section) section.style.display = '';
    if (bar) bar.style.display = '';
    if (text) text.innerHTML = '';
}

/**
 * Set streaming AI analysis text. Hides loading bar when text arrives.
 */
export function setAiAnalysisText(text) {
    const section = document.getElementById('ai-analysis');
    const bar = document.getElementById('ai-loading-bar');
    const textEl = document.getElementById('ai-analysis-text');
    if (section) section.style.display = '';
    if (bar) bar.style.display = text ? 'none' : '';
    if (textEl) textEl.innerHTML = formatExplanation(text);
}

// ===== Internal =====

const FIND_DESCS = {
    obvious: 'most players find this',
    natural: 'a natural candidate',
    findable: 'slightly tricky to find',
    difficult: 'hard to spot',
    'engine-only': 'very hard to find',
};

/**
 * Render a group of moves (Best / Findable) into a container.
 */
function renderMoveGroup(container, label, moves) {
    for (let i = 0; i < moves.length; i++) {
        const move = moves[i];
        const row = document.createElement('div');
        row.className = 'best-move-row';

        // Only show label on first row of each group
        const labelHtml = i === 0
            ? `<span class="best-move-label">${label}:</span>`
            : `<span class="best-move-label"></span>`;

        const sanClass = label === 'Findable' ? 'best-move-san findable' : 'best-move-san';

        let findHtml = '';
        if (move.findabilityScore != null) {
            const pct = Math.round(move.findabilityScore * 100);
            const cls = pct >= 70 ? 'easy' : pct >= 40 ? 'medium' : 'hard';
            const desc = FIND_DESCS[move.findabilityLabel] || '';
            findHtml = `<span class="find-inline"><span class="find-inline-pct ${cls}">${pct}%</span><span class="find-inline-label">${desc}</span></span>`;
        }

        row.innerHTML = `${labelHtml}<span class="${sanClass}">${move.san}</span>${findHtml}`;
        container.appendChild(row);
    }
}

function renderFindability(pctId, labelId, score, label) {
    const pct = Math.round(score * 100);
    const cls = pct >= 70 ? 'easy' : pct >= 40 ? 'medium' : 'hard';

    const pctEl = document.getElementById(pctId);
    if (pctEl) {
        pctEl.textContent = pct + '%';
        pctEl.className = 'find-inline-pct ' + cls;
    }

    const labelEl = document.getElementById(labelId);
    if (labelEl) labelEl.textContent = FIND_DESCS[label] || 'findable';
}

function getFindLabel(score) {
    if (score >= 0.85) return 'obvious';
    if (score >= 0.65) return 'natural';
    if (score >= 0.40) return 'findable';
    if (score >= 0.20) return 'difficult';
    return 'engine-only';
}

function renderThreatTags(facts) {
    const tags = [];
    if (facts.tacticalMotifs) {
        facts.tacticalMotifs.forEach(m => tags.push({ text: m, cls: 'tactic' }));
    }
    if (facts.threatsCreated) {
        facts.threatsCreated.forEach(t => tags.push({ text: t, cls: 'warning' }));
    }
    if (facts.threatsIgnored) {
        facts.threatsIgnored.forEach(t => tags.push({ text: '\u26a0 ' + t, cls: 'danger' }));
    }

    const area = document.getElementById('threats-area');
    const list = document.getElementById('threats-list');
    if (!area || !list) return;

    if (tags.length) {
        list.innerHTML = tags.slice(0, 6).map(t =>
            `<span class="threat-tag ${t.cls}">${t.text}</span>`
        ).join('');
        area.style.display = '';
    } else {
        area.style.display = 'none';
    }
}

function formatExplanation(text) {
    return text
        .replace(/<move>([^<]+)<\/move>/g, '<span class="clickable-move" data-san="$1">$1</span>')
        .replace(/<\/?move[^>]*>?/g, '')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

function evalClass(cp) {
    if (cp > 50) return 'positive';
    if (cp < -50) return 'negative';
    return 'neutral';
}

function show(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = '';
}

function hide(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}
