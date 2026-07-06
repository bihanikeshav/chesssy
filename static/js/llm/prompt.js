/**
 * 5-layer prompt builder for chess move explanations.
 * Port of prompt_builder.py.
 */

const EVAL_LANGUAGE_RULE = `
CRITICAL RULE: NEVER use numerical evaluations in your response (no "+0.3", "0.00", "-1.5", "evaluation of 0.00" etc.).
Instead, describe the position in natural language:
- Within ±0.3: "equal position", "roughly balanced", "dead even"
- ±0.3 to ±1.0: "slight edge for White/Black", "small advantage"
- ±1.0 to ±2.5: "clear advantage for White/Black", "solidly better"
- ±2.5 to ±5.0: "large advantage", "close to winning"
- Beyond ±5.0: "winning position", "decisive advantage"
- Mate threats: "checkmate is near", "forced mate in N"
The evaluation data is provided for YOUR analysis only — translate it to human language for the player.`;

const PRACTICAL_CONTEXT_RULE = `
IMPORTANT — PRACTICAL VALUE: Consider whether the move has practical merit at this player's level, even if the engine disagrees. Gambits, aggressive openings, and trappy lines often score well at lower ratings because opponents struggle to refute them. If a "mistake" is actually a known gambit or aggressive choice, acknowledge the practical upside (initiative, development lead, complexity) alongside the engine assessment. Don't just parrot the engine — coach the human in front of you.`;

const MOVE_TAG_RULE = `
MOVE FORMATTING: When mentioning specific chess moves in your response, wrap them in <move> tags like <move>Nf3</move> or <move>O-O</move>. This makes them clickable for the student to see on the board. Apply this to ALL concrete moves you mention (played move, best move, alternatives, variations).`;

const SYSTEM_PROMPTS = {
    beginner: `You are a friendly chess coach explaining moves to a complete beginner (rated under 1000).
Use very simple language. Avoid chess jargon entirely — when you must use a term (like "pin" or "fork"), explain it with an analogy.
Focus on the single most important point. Keep sentences short and clear. Be encouraging but honest about mistakes.
Think of explaining to someone who just learned how the pieces move.
At this level, practical considerations matter more than engine perfection — gambits and aggressive play often work great because opponents won't find the precise refutation. Emphasize what the move DOES (gains time, opens lines, creates threats) not just what the engine thinks.
${EVAL_LANGUAGE_RULE}
${PRACTICAL_CONTEXT_RULE}
${MOVE_TAG_RULE}`,

    novice: `You are a friendly chess coach explaining moves to a novice player (rated ~1000-1400).
Use simple language. When using chess terms (like "pin", "fork", "development"), briefly explain them.
Use analogies when helpful. Focus on 1-2 key points, don't overwhelm with details.
Keep sentences short and clear. Be encouraging but honest about mistakes.
At this level, gambits and sharp play can be very effective practically — opponents often don't know the refutations. Balance the engine's verdict with practical advice for their rating range.
${EVAL_LANGUAGE_RULE}
${PRACTICAL_CONTEXT_RULE}
${MOVE_TAG_RULE}`,

    intermediate: `You are a chess coach explaining moves to an intermediate player (rated ~1400-1800).
Use standard chess terminology (pins, forks, outposts, initiative, etc.) without over-explaining.
Include concrete variations when relevant (e.g., "after 5...Nxd5 6.c4 Nb6, White gains space").
Be direct and analytical. Focus on strategic and tactical nuances.
At this level, the player should start understanding why the engine prefers certain moves, but practical considerations still matter — a theoretically dubious gambit can still be a reasonable weapon if they know the resulting positions well.
${EVAL_LANGUAGE_RULE}
${PRACTICAL_CONTEXT_RULE}
${MOVE_TAG_RULE}`,

    expert: `You are a chess coach explaining moves to a strong player (rated 1800+).
Use advanced chess terminology freely. Include deep variations and discuss positional subtleties.
Discuss pawn structures, piece activity, prophylaxis, and long-term plans.
Be concise and analytical — this player understands chess well and wants insight, not basics.
At this level, engine accuracy matters more. If a move is objectively dubious, say so clearly. Practical tricks are less reliable against strong opposition.
${EVAL_LANGUAGE_RULE}
${MOVE_TAG_RULE}`,
};

const DETAILED_OUTPUT = `This is {qualityReason} move — explain why in 4-6 sentences total. No bullet points. No numbered lists.
Cover: what went wrong, what was better and why, and one takeaway lesson.
Be direct and concise. Use natural language for evaluations, NEVER numbers.`;

const BRIEF_OUTPUT = `Reply in EXACTLY 2-3 sentences. No more. No bullet points. No headers.
Say what the move achieves and one key insight. This is a {qualityWord} move — keep it short.
Use natural language for any eval references, not numbers.`;

const HINT_SYSTEM = `You give 1-sentence chess hints. You NEVER name a specific move or square. You NEVER analyze the full position. You NEVER use bullet points, lists, or headers. You NEVER output more than 2 sentences.

Your ENTIRE response must be a single short nudge like:
- "One of your minor pieces could be much more active."
- "There's an undefended piece you could target."
- "Your king could use some shelter."
- "Look at piece development — not all your pieces are in the game yet."
- "There's a forcing move available if you look at checks."

Respond with ONLY the hint. Nothing else.`;

export { HINT_SYSTEM };

export class PromptBuilder {
    constructor(skillMode = 'intermediate') {
        this.skillMode = skillMode;
    }

    setSkillMode(mode) {
        if (SYSTEM_PROMPTS[mode]) this.skillMode = mode;
    }

    /**
     * Build system + user prompts from move facts.
     * @param {object} facts - MoveFacts from extractFacts()
     * @param {object} [options]
     * @param {object[]} [options.ragPassages]
     * @param {object} [options.explorerData] - Lichess explorer data for the position
     * @returns {{system: string, user: string}}
     */
    build(facts, options = {}) {
        const playerRating = options.playerRating || 1400;
        const system = SYSTEM_PROMPTS[this.skillMode] || SYSTEM_PROMPTS.intermediate;

        const evalBefore = formatEvalPrompt(facts.evalBeforeCp, facts.mateThreatBefore);
        const evalAfter = formatEvalPrompt(facts.evalAfterCp, facts.mateThreatAfter);
        const bestEval = formatEvalPrompt(facts.bestMoveEvalCp, null);

        // Mate info
        let mateInfo = '';
        if (facts.mateThreatBefore != null) mateInfo += `- Mate threat before: M${facts.mateThreatBefore}\n`;
        if (facts.mateThreatAfter != null) mateInfo += `- Mate threat after: M${facts.mateThreatAfter}\n`;

        // Best findable alternative
        let bestFindableInfo = '';
        if (facts.bestFindableMoveSan && facts.bestFindableMoveSan !== facts.bestMoveSan) {
            bestFindableInfo = `**Best findable alternative:** ${facts.bestFindableMoveSan} (eval: ${formatEvalPrompt(facts.bestFindableEvalCp, null)})`;
        }

        // Findability info
        let findabilityInfo;
        if (facts.findabilityScore != null) {
            findabilityInfo = `${Math.round(facts.findabilityScore * 100)}% (${facts.findabilityLabel || 'unknown'})`;
        } else {
            findabilityInfo = facts.isPlayedFindable ? 'findable' : 'requires calculation';
        }

        // Explorer popularity info
        let popularityInfo = '';
        if (facts.explorerPopularity != null) {
            const pct = Math.round(facts.explorerPopularity * 100);
            popularityInfo = `**Move popularity:** ${pct}% of players at this level play this move (${facts.explorerTotalGames || 0} games in database)`;
        }

        // Tactical features
        const tacticalFeatures = formatTacticalFeatures(facts);

        // Engine lines
        const engineLines = formatEngineLines(facts.topLines);

        // RAG context
        const ragContext = formatRagContext(options.ragPassages);

        // Output instruction
        const outputInstruction = getOutputInstruction(facts.moveQuality);

        // CP loss display (for LLM's internal use)
        const cpLossStr = facts.cpLoss ? `${(facts.cpLoss / 100).toFixed(2)} pawns` : '0';

        // Eval context description (natural language for the LLM to use as reference)
        const evalContext = describeEvalContext(facts.evalBeforeCp, facts.evalAfterCp, facts.cpLoss);

        const user = `Analyze this chess move and provide a structured explanation.

**Position:** ${facts.positionFen}
**Move played:** ${facts.playedMoveSan} (${facts.moveQuality})
**Game phase:** ${facts.positionType} (move ${facts.moveNumber})
**Side:** ${facts.sideToMove}
**Player rating:** ~${playerRating} (tailor your advice to this level)

**Evaluation (for your analysis — do NOT cite these numbers to the player):**
- Before: ${evalBefore} | After: ${evalAfter}
- CP loss: ${cpLossStr}
- In plain terms: ${evalContext}
${mateInfo}

**Best move:** ${facts.bestMoveSan} (eval: ${bestEval})
${bestFindableInfo}
${popularityInfo}

**Move tags:** ${facts.playedMoveTags?.length ? facts.playedMoveTags.join(', ') : 'quiet move'}
**Findability:** ${findabilityInfo}

**Tactical features:**
${tacticalFeatures}

**Engine lines:**
${engineLines}

${ragContext}

---

${outputInstruction}`;

        return { system, user };
    }
}

function formatEvalPrompt(cp, mate) {
    if (mate != null) {
        const sign = mate > 0 ? '+' : '-';
        return `${sign}M${Math.abs(mate)}`;
    }
    if (cp == null) return '0.00';
    return (cp / 100).toFixed(2);
}

/**
 * Describe the eval change in natural language for the LLM to reference.
 */
function describeEvalContext(evalBefore, evalAfter, cpLoss) {
    const parts = [];

    // Describe position before
    const absBefore = Math.abs(evalBefore || 0);
    if (absBefore < 30) parts.push('Position was roughly equal before the move');
    else if (absBefore < 100) parts.push(`${evalBefore > 0 ? 'White' : 'Black'} had a slight edge`);
    else if (absBefore < 250) parts.push(`${evalBefore > 0 ? 'White' : 'Black'} had a clear advantage`);
    else parts.push(`${evalBefore > 0 ? 'White' : 'Black'} had a large advantage`);

    // Describe change
    if (cpLoss <= 5) parts.push('The move maintains the position perfectly');
    else if (cpLoss <= 30) parts.push('Very minor inaccuracy, barely changes things');
    else if (cpLoss <= 80) parts.push('The position shifted noticeably');
    else if (cpLoss <= 200) parts.push('A significant amount of advantage was given away');
    else parts.push('A major amount of advantage was lost');

    return parts.join('. ') + '.';
}

function formatTacticalFeatures(facts) {
    const parts = [];
    const tb = facts.threatsBefore;
    if (tb) {
        if (tb.hangingPieces?.length) parts.push(`- Hanging pieces (before): ${tb.hangingPieces.slice(0, 3).join(', ')}`);
        if (tb.pins?.length) parts.push(`- Pins: ${tb.pins.slice(0, 3).join(', ')}`);
        if (tb.forks?.length) parts.push(`- Fork opportunities: ${tb.forks.slice(0, 3).join(', ')}`);
        if (tb.checksAvailable?.length) parts.push(`- Available checks: ${tb.checksAvailable.slice(0, 3).join(', ')}`);
    }
    if (facts.tacticalMotifs?.length) {
        parts.push(`- Tactical motifs: ${facts.tacticalMotifs.join(', ')}`);
    }
    return parts.length ? parts.join('\n') : '- No significant tactical features';
}

function formatEngineLines(topLines) {
    if (!topLines?.length) return '- Not available';
    return topLines.map(line => {
        const moves = (line.movesSan || []).slice(0, 8).join(' ');
        return `- Line ${line.rank}: ${moves} (${line.eval || '?'})`;
    }).join('\n');
}

function formatRagContext(passages) {
    if (!passages?.length) return '';
    const parts = ['**Relevant chess theory:**'];
    for (const p of passages.slice(0, 3)) {
        if (typeof p === 'string') {
            parts.push(`- ${p.slice(0, 200)}`);
        } else {
            const title = p.title || '';
            const content = p.content || p.document || '';
            parts.push(title ? `- *${title}*: ${content.slice(0, 200)}` : `- ${content.slice(0, 200)}`);
        }
    }
    return parts.join('\n');
}

function getOutputInstruction(quality) {
    if (quality === 'best' || quality === 'good') {
        return BRIEF_OUTPUT.replace(/\{qualityWord\}/g, quality);
    }
    const reasons = { inaccuracy: 'an inaccuracy', mistake: 'a mistake', blunder: 'a blunder' };
    return DETAILED_OUTPUT.replace('{qualityReason}', reasons[quality] || 'a suboptimal');
}
