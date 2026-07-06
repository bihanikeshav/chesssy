/**
 * Rule-based explanation fallback when no LLM is configured.
 * Port of llm.py:_generate_chess_explanation().
 */

const GOOD_OPENING_MOVES = {
    'e4':  'controls the center and opens lines for the queen and bishop',
    'd4':  'controls the center and opens the diagonal for the dark-squared bishop',
    'c4':  'the English Opening — controls d5 and prepares a flexible pawn structure',
    'Nf3': 'develops the knight to its best square, controls e5 and d4',
    'Nc3': 'develops the knight toward the center',
    'Bc4': 'develops the bishop to an active diagonal targeting f7',
    'Bb5': 'the Spanish/Ruy Lopez bishop, pins or pressures the knight',
    'd3':  'solid setup, supports e4 and prepares piece development',
    'g3':  'fianchetto setup, prepares Bg2 controlling the long diagonal',
    'e5':  'fights for the center, classical response to e4',
    'd5':  'fights for the center, solid and active',
    'c5':  'the Sicilian Defense — fights for d4 control asymmetrically',
    'Nf6': 'develops the knight and attacks e4',
    'Nc6': 'develops the knight toward the center',
    'e6':  'the French Defense setup — solid and prepares d5',
    'c6':  'the Caro-Kann — solid, prepares d5',
    'O-O': 'castles kingside for king safety and connects the rooks',
    'O-O-O': 'castles queenside, often preparing a kingside attack',
};

const COMMON_MISTAKES = {
    'f6':  'weakens the kingside, blocks the knight from its best square',
    'f3':  'weakens the kingside, blocks the knight from f3',
    'h6':  'wastes tempo, weakens g6 if bishop develops later',
    'a6':  'wastes tempo unless preparing b5',
    'h3':  'wastes tempo unless stopping a pin',
    'Qh5': 'develops queen too early, can be attacked with tempo',
    'Qf3': 'develops queen too early, blocks knight from f3',
};

// Known gambits/aggressive openings that are "mistakes" by engine but practical at lower levels
const KNOWN_GAMBITS = {
    'e5':  { after: ['d4'], note: 'the Englund Gambit — sacrifices a pawn for quick development and initiative' },
    'f5':  { after: ['e4'], note: 'the Latvian Gambit — risky but creates sharp play' },
    'Bc4': { after: [], note: null },
    'd4':  { after: ['e4', 'e5'], note: 'the Center Game — directly challenges the center' },
    'Nf6': { after: ['e4'], note: "Alekhine's Defense — invites White to overextend" },
    'b5':  { after: [], note: null },
    'f4':  { after: ['e4', 'e5'], note: "the King's Gambit — sacrifices a pawn for rapid development and attack" },
};

/**
 * Check if a move is a known gambit in context.
 */
function isKnownGambit(moveSan, moveNumber, positionType) {
    if (positionType !== 'opening' || moveNumber > 5) return null;
    const entry = KNOWN_GAMBITS[moveSan];
    return entry?.note || null;
}

/**
 * Generate a rule-based explanation for a move.
 * @param {object} facts - MoveFacts
 * @param {number} [playerRating] - Player rating for context
 * @returns {string}
 */
export function generateFallbackExplanation(facts, playerRating = 1400) {
    const moveSan = facts.playedMoveSan;
    const bestSan = facts.bestMoveSan;
    const cpLoss = facts.cpLoss;

    // Known good opening moves
    if (GOOD_OPENING_MOVES[moveSan] && (facts.moveQuality === 'best' || facts.moveQuality === 'good')) {
        const desc = GOOD_OPENING_MOVES[moveSan];
        if (facts.moveQuality === 'best') {
            return `**${moveSan}** ${desc}. Excellent choice!`;
        }
        return `**${moveSan}** ${desc}. ${bestSan} was slightly more precise.`;
    }

    // Best move — simple acknowledgment
    if (facts.moveQuality === 'best') {
        if (GOOD_OPENING_MOVES[moveSan]) {
            return `**${moveSan}** ${GOOD_OPENING_MOVES[moveSan]}.`;
        }
        return `**${moveSan}** is the best move in this position.`;
    }

    if (facts.moveQuality === 'good') {
        if (GOOD_OPENING_MOVES[moveSan]) {
            return `**${moveSan}** ${GOOD_OPENING_MOVES[moveSan]}. ${bestSan} was marginally better.`;
        }
        return `**${moveSan}** is a solid move. ${bestSan} was slightly more accurate.`;
    }

    // Suboptimal moves
    const parts = [];

    // Check if this is a known gambit
    const gambitNote = isKnownGambit(moveSan, facts.moveNumber, facts.positionType);

    if (gambitNote && cpLoss < 300) {
        // It's a gambit, not a pure blunder — explain with practical context
        parts.push(`**${moveSan}** — ${gambitNote}.`);
        if (playerRating < 1400) {
            parts.push('At your level this is a solid practical choice — the initiative and sharp play often outweigh the material cost, since opponents rarely find the precise refutation.');
        } else if (playerRating < 1800) {
            parts.push(`The engine prefers ${bestSan}, but this is a reasonable practical weapon if you know the resulting positions.`);
        } else {
            parts.push(`Objectively ${bestSan} is more accurate, and at your level opponents are more likely to punish inaccuracies.`);
        }
        return parts.join(' ');
    }

    // Severity prefix (natural language, no eval numbers)
    if (facts.moveQuality === 'blunder') {
        const severity = cpLoss >= 500 ? 'a huge amount of the advantage' :
                         cpLoss >= 300 ? 'a significant advantage' : 'substantial ground';
        parts.push(`**Blunder!** This gives away ${severity}.`);
    } else if (facts.moveQuality === 'mistake') {
        const severity = cpLoss >= 200 ? 'a clear advantage' : 'some advantage';
        parts.push(`**Mistake** — this costs ${severity}.`);
    }

    // Check for known problem patterns
    let specific = null;
    for (const [pattern, problem] of Object.entries(COMMON_MISTAKES)) {
        if (moveSan.includes(pattern)) {
            specific = problem;
            break;
        }
    }

    if (facts.positionType === 'opening') {
        if (specific) {
            parts.push(`${moveSan} ${specific}.`);
        } else if (moveSan.startsWith('Q') && facts.moveNumber <= 5) {
            parts.push(`${moveSan} brings the queen out too early.`);
        } else {
            parts.push(`${moveSan} is not the most effective move here.`);
        }
    } else if (specific) {
        parts.push(`${moveSan} ${specific}.`);
    } else {
        parts.push(`${moveSan} is inaccurate in this position.`);
    }

    // What the best move achieves
    const bt = facts.bestMoveTags || [];
    if (bt.includes('development')) {
        parts.push(`${bestSan} develops a piece actively.`);
    } else if (bt.includes('central_pawn')) {
        parts.push(`${bestSan} controls the center.`);
    } else if (bt.includes('castling')) {
        parts.push(`${bestSan} secures the king.`);
    } else if (bt.includes('threat')) {
        parts.push(`${bestSan} creates immediate threats.`);
    } else {
        parts.push(`${bestSan} was the better choice.`);
    }

    return parts.join(' ') || `${moveSan} is suboptimal. ${bestSan} was better.`;
}
