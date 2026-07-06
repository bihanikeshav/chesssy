/**
 * Coach report generation — full game analysis summary.
 * Port of generateCoachReport() from app.js + app.py.
 */

import { extractFacts } from './facts.js';

/**
 * Analyze an entire game and produce a coach report.
 *
 * @param {object[]} pgnMoves - Array of {moveSan, moveUci, fenBefore, moveNumber, side}
 * @param {number} playerRating
 * @param {string} skillLevel
 * @param {function} onProgress - callback(current, total, data)
 * @returns {Promise<CoachReport>}
 */
export async function generateCoachReport(pgnMoves, playerRating, skillLevel, onProgress) {
    const results = [];
    const stats = { best: 0, good: 0, inaccuracy: 0, mistake: 0, blunder: 0 };
    const keyMoments = [];

    for (let i = 0; i < pgnMoves.length; i++) {
        const m = pgnMoves[i];
        try {
            const facts = await extractFacts(
                m.fenBefore, m.moveUci, m.moveNumber, playerRating, skillLevel
            );

            results.push(facts);
            stats[facts.moveQuality] = (stats[facts.moveQuality] || 0) + 1;

            // Track key moments (mistakes and worse)
            if (['inaccuracy', 'mistake', 'blunder'].includes(facts.moveQuality)) {
                const moment = {
                    index: i,
                    moveNumber: m.moveNumber,
                    side: m.side,
                    played: facts.playedMoveSan,
                    quality: facts.moveQuality,
                    cpLoss: facts.cpLoss,
                    bestMove: facts.bestMoveSan,
                    bestFindable: facts.isBestFindable,
                    findabilityScore: facts.findabilityScore,
                    bestFindabilityScore: facts.bestFindabilityScore,
                    bestFindableAlt: facts.bestFindableMoveSan,
                };

                // Build suggestion text
                if (facts.moveQuality === 'blunder') {
                    moment.suggestion = `${facts.playedMoveSan} loses ${(facts.cpLoss / 100).toFixed(1)} pawns.`;
                } else if (facts.moveQuality === 'mistake') {
                    moment.suggestion = `${facts.playedMoveSan} costs ${(facts.cpLoss / 100).toFixed(1)} pawns.`;
                } else {
                    moment.suggestion = `${facts.playedMoveSan} is slightly inaccurate.`;
                }

                if (facts.bestFindabilityScore >= 0.5) {
                    moment.suggestion += ` ${facts.bestMoveSan} was better and quite findable.`;
                } else {
                    moment.suggestion += ` Engine prefers ${facts.bestMoveSan}, but it's hard to find.`;
                    if (facts.bestFindableMoveSan && facts.bestFindableMoveSan !== facts.bestMoveSan) {
                        moment.suggestion += ` A good alternative: ${facts.bestFindableMoveSan}.`;
                    }
                }

                keyMoments.push(moment);
            }

            onProgress?.(i + 1, pgnMoves.length, facts);
        } catch (e) {
            console.error(`Error analyzing move ${i}:`, e);
            results.push(null);
            onProgress?.(i + 1, pgnMoves.length, null);
        }
    }

    const totalMoves = Object.values(stats).reduce((a, b) => a + b, 0);
    const accuracy = totalMoves > 0
        ? Math.round(((stats.best + stats.good) / totalMoves) * 100)
        : 0;

    // Detect patterns
    const patterns = [];
    if (stats.best + stats.good >= totalMoves * 0.7) {
        patterns.push({ text: 'Strong overall accuracy', type: 'strength' });
    }
    if (stats.blunder === 0 && totalMoves > 5) {
        patterns.push({ text: 'No blunders — good discipline', type: 'strength' });
    }
    if (stats.blunder >= 2) {
        patterns.push({ text: `${stats.blunder} blunders — slow down and double-check`, type: 'weakness' });
    }
    if (stats.mistake >= 3) {
        patterns.push({ text: `${stats.mistake} mistakes — consider each move carefully`, type: 'weakness' });
    }

    // Eval history for graph
    const evalHistory = results.map((r, i) => ({
        moveIndex: i,
        evalCp: r ? r.evalAfterCp : null,
        quality: r ? r.moveQuality : null,
    }));

    return {
        stats,
        accuracy,
        keyMoments,
        patterns,
        evalHistory,
        results,
    };
}
