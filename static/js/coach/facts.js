/**
 * Fact extraction — structured analysis of a played move.
 * Port of facts.py. Uses Stockfish WASM + candidates + findability.
 */

import { analyzeInstant, calculateMaterial } from '../engine/analysis.js';
import { analyzeThreats, extractTacticalMotifs } from '../engine/threats.js';
import { getMoveTags, isFindable } from './candidates.js';
import { FindabilityCalculator } from './findability.js';
import { formatEval } from '../engine/stockfish.js';

/**
 * Extract all facts about a played move.
 *
 * @param {string} fen - Position before the move
 * @param {string} playedMove - UCI string (e.g., 'e2e4')
 * @param {number} moveNumber
 * @param {number} playerRating
 * @param {string} skillLevel
 * @returns {Promise<MoveFacts>}
 */
export async function extractFacts(fen, playedMove, moveNumber = 1, playerRating = 1200, skillLevel = 'intermediate') {
    const game = new Chess(fen);

    // Parse the move
    let moveObj = null;
    let moveUci = playedMove;
    let moveSan = '';

    const legalMoves = game.moves({ verbose: true });
    for (const m of legalMoves) {
        const uci = m.from + m.to + (m.promotion || '');
        if (uci === playedMove) {
            moveObj = m;
            moveSan = m.san;
            break;
        }
    }

    // Try SAN if UCI didn't match
    if (!moveObj) {
        for (const m of legalMoves) {
            if (m.san === playedMove) {
                moveObj = m;
                moveSan = m.san;
                moveUci = m.from + m.to + (m.promotion || '');
                break;
            }
        }
    }

    if (!moveObj) {
        throw new Error(`Invalid move: ${playedMove} in position ${fen}`);
    }

    const isWhite = game.turn() === 'w';

    // Analyze position before move (engine only — explorer queried separately in main.js)
    const infoBefore = await analyzeInstant(fen, 14, game);

    // Best move from engine
    const bestMoveUci = infoBefore.lines.length > 0 ? infoBefore.lines[0].moves[0] : '0000';
    let bestMoveSan = bestMoveUci;
    try {
        const from = bestMoveUci.substring(0, 2);
        const to = bestMoveUci.substring(2, 4);
        const promo = bestMoveUci[4] || undefined;
        const bm = game.move({ from, to, promotion: promo });
        if (bm) { bestMoveSan = bm.san; game.undo(); }
    } catch (e) { /* keep UCI */ }

    // Evals (all from White's perspective — engine already normalizes)
    const evalBefore = infoBefore.lines.length > 0 ? infoBefore.lines[0].evalCp : 0;
    const mateBefore = infoBefore.lines.length > 0 ? infoBefore.lines[0].evalMate : null;
    const bestEval = evalBefore;

    // Check if played move is in engine lines
    let evalAfter = null;
    let mateAfter = null;
    for (const line of infoBefore.lines) {
        if (line.moves.length > 0 && line.moves[0] === moveUci) {
            evalAfter = line.evalCp;
            mateAfter = line.evalMate;
            break;
        }
    }

    if (evalAfter === null) {
        // Move not in engine lines — analyze after position
        const gameAfter = new Chess(fen);
        gameAfter.move(moveSan);
        const infoAfter = await analyzeInstant(gameAfter.fen(), 12, gameAfter);
        evalAfter = infoAfter.lines.length > 0 ? infoAfter.lines[0].evalCp : 0;
        mateAfter = infoAfter.lines.length > 0 ? infoAfter.lines[0].evalMate : null;
    }

    // CP loss
    let cpLoss = 0;
    if (mateBefore !== null && mateAfter === null) {
        cpLoss = 500; // Had mate, lost it
    } else if (mateBefore === null) {
        if (isWhite) {
            cpLoss = Math.max(0, bestEval - evalAfter);
        } else {
            cpLoss = Math.max(0, evalAfter - bestEval);
        }
    }

    // Threats
    const threatsBefore = analyzeThreats(game);
    const tacticalMotifs = extractTacticalMotifs(threatsBefore);

    // Classify move quality
    const moveQuality = classifyMove(cpLoss, threatsBefore, infoBefore);

    // Position type
    const positionType = determinePositionType(game, moveNumber);

    // Findability (with explorer data)
    const playedFindability = isFindable(game, moveUci);
    const bestFindability = isFindable(game, bestMoveUci);

    const findCalc = new FindabilityCalculator(playerRating);
    const numLegal = legalMoves.length;

    const findabilityScore = findCalc.scoreMove(
        playedFindability.tags, tacticalMotifs, numLegal,
        null, moveUci, positionType
    );
    const findabilityLabel = findCalc.getLabel(findabilityScore);

    const bestFindabilityScore = findCalc.scoreMove(
        bestFindability.tags, tacticalMotifs, numLegal,
        null, bestMoveUci, positionType
    );

    // Move tags for played move
    const playedTags = getMoveTags(game, moveObj);

    // Gives check?
    game.move(moveSan);
    const givesCheck = game.in_check();
    const threatsAfter = analyzeThreats(game);
    game.undo();

    // Is in check before move?
    const isInCheck = game.in_check();

    // Top lines
    const topLines = infoBefore.lines.slice(0, 3).map(line => ({
        rank: line.rank,
        movesSan: line.movesSan.slice(0, 10),
        evalCp: line.evalCp,
        evalMate: line.evalMate,
        eval: line.eval || formatEval(line.evalCp, line.evalMate),
    }));

    // Material
    const materialBalance = calculateMaterial(game);

    // Detect threats created/ignored
    const threatsCreated = detectThreatsCreated(game, moveObj);
    const threatsIgnored = detectThreatsIgnored(game, threatsBefore);

    // Find best findable alternative
    let bestFindableUci = null, bestFindableSan = null, bestFindableEval = null;
    for (const line of infoBefore.lines) {
        if (line.moves.length > 0) {
            const { findable } = isFindable(game, line.moves[0]);
            if (findable) {
                bestFindableUci = line.moves[0];
                bestFindableEval = line.evalCp;
                try {
                    const from = line.moves[0].substring(0, 2);
                    const to = line.moves[0].substring(2, 4);
                    const promo = line.moves[0][4] || undefined;
                    const bfm = game.move({ from, to, promotion: promo });
                    if (bfm) { bestFindableSan = bfm.san; game.undo(); }
                } catch (e) { bestFindableSan = bestFindableUci; }
                break;
            }
        }
    }

    // Top alternative moves from engine lines (for multi-move display)
    const topAlternatives = [];
    for (const line of infoBefore.lines) {
        if (line.moves.length === 0) continue;
        const uci = line.moves[0];
        if (uci === moveUci) continue; // skip the played move
        let san = uci;
        try {
            const from = uci.substring(0, 2);
            const to = uci.substring(2, 4);
            const promo = uci[4] || undefined;
            const m = game.move({ from, to, promotion: promo });
            if (m) { san = m.san; game.undo(); }
        } catch (e) {}
        const finfo = isFindable(game, uci);
        const fScore = findCalc.scoreMove(finfo.tags, tacticalMotifs, numLegal, null, uci, positionType);
        const fLabel = findCalc.getLabel(fScore);
        topAlternatives.push({ san, uci, evalCp: line.evalCp, findabilityScore: fScore, findabilityLabel: fLabel, findable: finfo.findable });
    }

    return {
        positionFen: fen,
        sideToMove: isWhite ? 'white' : 'black',
        moveNumber,
        playedMoveUci: moveUci,
        playedMoveSan: moveSan,
        evalBeforeCp: evalBefore,
        evalAfterCp: evalAfter,
        cpLoss,
        bestMoveUci: bestMoveUci,
        bestMoveSan: bestMoveSan,
        bestMoveEvalCp: bestEval,
        moveQuality,
        isPlayedFindable: playedFindability.findable,
        playedMoveTags: playedTags,
        isBestFindable: bestFindability.findable,
        bestMoveTags: bestFindability.tags,
        positionType,
        isTactical: tacticalMotifs.length > 0 || threatsBefore.threatsToKing,
        isCheck: givesCheck,
        isInCheck,
        bestFindableMoveUci: bestFindableUci,
        bestFindableMoveSan: bestFindableSan,
        bestFindableEvalCp: bestFindableEval,
        topAlternatives,
        threatsCreated,
        threatsIgnored,
        mateThreatBefore: mateBefore,
        mateThreatAfter: mateAfter,
        threatsBefore,
        threatsAfter,
        tacticalMotifs,
        topLines,
        findabilityScore,
        findabilityLabel,
        bestFindabilityScore,
        materialBalance,
        explorerPopularity: null,
        explorerTotalGames: null,
    };
}

function classifyMove(cpLoss, threats, info) {
    const fragility = estimateFragility(threats, info);

    let thresholds;
    if (fragility > 0.7) {
        thresholds = { good: 10, inaccuracy: 30, mistake: 80 };
    } else if (fragility > 0.4) {
        thresholds = { good: 20, inaccuracy: 50, mistake: 150 };
    } else {
        thresholds = { good: 30, inaccuracy: 80, mistake: 200 };
    }

    if (cpLoss <= 5) return 'best';
    if (cpLoss <= thresholds.good) return 'good';
    if (cpLoss <= thresholds.inaccuracy) return 'inaccuracy';
    if (cpLoss <= thresholds.mistake) return 'mistake';
    return 'blunder';
}

function estimateFragility(threats, info) {
    let score = 0;
    if (threats.hangingPieces?.length) score += 0.3;
    if (threats.threatsToKing) score += 0.3;
    if (threats.forks?.length || threats.pins?.length) score += 0.2;
    if (info && info.lines && info.lines.length >= 2) {
        const spread = Math.abs(info.lines[0].evalCp - info.lines[1].evalCp);
        if (spread > 100) score += 0.2;
    }
    return Math.min(1.0, score);
}

function determinePositionType(game, moveNumber) {
    let pieceCount = 0;
    'abcdefgh'.split('').forEach(f => {
        for (let r = 1; r <= 8; r++) {
            if (game.get(f + r)) pieceCount++;
        }
    });

    if (moveNumber <= 10 && pieceCount >= 28) return 'opening';
    if (pieceCount <= 14) return 'endgame';
    return 'middlegame';
}

function detectThreatsCreated(game, move) {
    const threats = [];
    game.move(move.san);
    game.undo();
    return threats.slice(0, 3);
}

function detectThreatsIgnored(game, threats) {
    const ignored = [];
    for (const h of (threats.hangingPieces || [])) {
        ignored.push(h);
    }
    return ignored.slice(0, 3);
}
