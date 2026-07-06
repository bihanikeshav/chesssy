/**
 * Rating-parameterized findability scoring for chess moves.
 *
 * Combines two signals:
 * 1. Empirical popularity — what % of players at this rating actually play this move (Lichess data)
 * 2. Pattern-based scoring — heuristic based on move characteristics (checks, captures, etc.)
 *
 * When Lichess data is available, it's weighted heavily because it's literally
 * measuring "how many real players find this move." Pattern scoring fills in
 * when no database coverage exists (rare positions, middlegame, endgame).
 */

// ===== Pattern-based scoring (heuristic fallback) =====

const PATTERN_SCORES = {
    check:        { 800: 0.95, 1200: 0.99, 1600: 1.0,  2000: 1.0  },
    capture:      { 800: 0.90, 1200: 0.95, 1600: 0.99, 2000: 1.0  },
    recapture:    { 800: 0.85, 1200: 0.95, 1600: 0.99, 2000: 1.0  },
    promotion:    { 800: 0.90, 1200: 0.95, 1600: 0.99, 2000: 1.0  },
    castling:     { 800: 0.70, 1200: 0.90, 1600: 0.98, 2000: 1.0  },
    central_pawn: { 800: 0.50, 1200: 0.75, 1600: 0.90, 2000: 0.98 },
    development:  { 800: 0.30, 1200: 0.65, 1600: 0.85, 2000: 0.95 },
    defense:      { 800: 0.15, 1200: 0.40, 1600: 0.70, 2000: 0.90 },
    threat:       { 800: 0.20, 1200: 0.50, 1600: 0.75, 2000: 0.90 },
    improvement:  { 800: 0.10, 1200: 0.35, 1600: 0.60, 2000: 0.85 },
    sacrifice:    { 800: 0.05, 1200: 0.15, 1600: 0.35, 2000: 0.65 },
};

const QUIET_SCORES = { 800: 0.02, 1200: 0.10, 1600: 0.25, 2000: 0.60 };

const TACTICAL_MOTIF_THRESHOLDS = {
    fork:              { threshold: 1200, bonus: 0.15 },
    pin:               { threshold: 1400, bonus: 0.10 },
    skewer:            { threshold: 1500, bonus: 0.10 },
    discovered_attack: { threshold: 1600, bonus: 0.12 },
    double_attack:     { threshold: 1300, bonus: 0.12 },
    overloaded:        { threshold: 1800, bonus: 0.08 },
};

// ===== Opening principle conformity =====
// Moves that follow well-known opening principles get a bonus.
// These patterns are things chess teachers universally recommend.

const OPENING_PRINCIPLE_BONUS = {
    // Knights to natural squares
    'g1f3': 0.15, 'b1c3': 0.12, 'g8f6': 0.15, 'b8c6': 0.12,
    // Central pawns
    'e2e4': 0.18, 'd2d4': 0.18, 'e7e5': 0.15, 'd7d5': 0.15,
    'c2c4': 0.10, 'e7e6': 0.10, 'c7c5': 0.10, 'c7c6': 0.10,
    // Castling
    'e1g1': 0.20, 'e8g8': 0.20, 'e1c1': 0.12, 'e8c8': 0.12,
    // Bishop development
    'f1c4': 0.10, 'f1b5': 0.10, 'f1e2': 0.08, 'c1f4': 0.08, 'c1g5': 0.08,
    'f8c5': 0.10, 'f8b4': 0.10, 'f8e7': 0.08, 'c8f5': 0.08, 'c8g4': 0.08,
};

/**
 * Sigmoid interpolation between rating breakpoints.
 */
function sigmoidInterpolate(rating, breakpoints) {
    const ratings = Object.keys(breakpoints).map(Number).sort((a, b) => a - b);

    if (rating <= ratings[0]) return breakpoints[ratings[0]];
    if (rating >= ratings[ratings.length - 1]) return breakpoints[ratings[ratings.length - 1]];

    for (let i = 0; i < ratings.length - 1; i++) {
        if (rating >= ratings[i] && rating <= ratings[i + 1]) {
            const rLow = ratings[i], rHigh = ratings[i + 1];
            const vLow = breakpoints[rLow], vHigh = breakpoints[rHigh];

            const t = (rating - rLow) / (rHigh - rLow);
            const sigmoidT = 1.0 / (1.0 + Math.exp(-8 * (t - 0.5)));
            return vLow + (vHigh - vLow) * sigmoidT;
        }
    }

    return 0.0;
}

/**
 * Convert Lichess move popularity (0.0-1.0) to a findability score.
 *
 * Rationale: if 30% of players at your level play this move, it's clearly findable.
 * But even 2-3% popularity means it's a real candidate that some players spot.
 *
 * The curve is generous — chess players consider many moves even if they don't
 * all play the most popular one.
 */
function popularityToFindability(popularity) {
    if (popularity >= 0.30) return 0.95;  // top choice — obvious
    if (popularity >= 0.15) return 0.85;  // popular alternative — natural
    if (popularity >= 0.08) return 0.70;  // well-known option — findable
    if (popularity >= 0.03) return 0.50;  // occasional choice — requires thought
    if (popularity >= 0.01) return 0.30;  // rare but played — hard to find
    if (popularity > 0)     return 0.15;  // almost never played — very hard
    return 0.05;                           // not in database — engine-only territory
}

export class FindabilityCalculator {
    constructor(playerRating = 1200) {
        this.playerRating = Math.max(800, Math.min(2000, playerRating));
    }

    setRating(rating) {
        this.playerRating = Math.max(800, Math.min(2000, rating));
    }

    /**
     * Calculate findability probability for a move.
     *
     * @param {string[]} tags - Move tags from CandidateFilter
     * @param {string[]} [tacticalMotifs] - Tactical motifs
     * @param {number} [numLegalMoves=30]
     * @param {object} [explorerPopularity] - {popularity, totalGames, moveGames} from Lichess
     * @param {string} [moveUci] - UCI string for opening principle matching
     * @param {string} [positionType] - 'opening', 'middlegame', 'endgame'
     * @returns {number} 0.0 - 1.0
     */
    scoreMove(tags, tacticalMotifs = null, numLegalMoves = 30, explorerPopularity = null, moveUci = null, positionType = null) {
        // === 1. Pattern-based score (heuristic) ===
        const patternScore = this._patternScore(tags, tacticalMotifs, numLegalMoves);

        // === 2. Empirical popularity score (from Lichess) ===
        let empiricalScore = null;
        let confidence = 0;

        if (explorerPopularity && explorerPopularity.totalGames >= 20) {
            empiricalScore = popularityToFindability(explorerPopularity.popularity);

            // Confidence scales with sample size:
            // 20 games → ~0.04 confidence, 200 → ~0.40, 500 → 0.70, 1000+ → ~0.90
            confidence = Math.min(0.90, explorerPopularity.totalGames / 1100);
        }

        // === 3. Opening principle bonus ===
        let principleBonus = 0;
        if (moveUci && positionType === 'opening' && OPENING_PRINCIPLE_BONUS[moveUci]) {
            principleBonus = OPENING_PRINCIPLE_BONUS[moveUci];
        }

        // === 4. Blend empirical + pattern ===
        let score;
        if (empiricalScore !== null) {
            // Weighted blend: more Lichess data → more trust in empirical score
            score = confidence * empiricalScore + (1 - confidence) * patternScore;
        } else {
            score = patternScore;
        }

        // Add opening principle bonus (capped contribution)
        score = Math.min(1.0, score + principleBonus * 0.5);

        return Math.round(Math.min(1.0, Math.max(0.0, score)) * 1000) / 1000;
    }

    /**
     * Pure pattern-based scoring (original heuristic approach).
     */
    _patternScore(tags, tacticalMotifs, numLegalMoves) {
        let base;

        if (!tags || !tags.length) {
            base = sigmoidInterpolate(this.playerRating, QUIET_SCORES);
        } else {
            const scores = [];
            for (const tag of tags) {
                if (PATTERN_SCORES[tag]) {
                    scores.push(sigmoidInterpolate(this.playerRating, PATTERN_SCORES[tag]));
                }
            }
            base = scores.length ? Math.max(...scores) : sigmoidInterpolate(this.playerRating, QUIET_SCORES);
        }

        // Complexity penalty
        let complexityPenalty = 1.0;
        if (numLegalMoves > 35) {
            complexityPenalty = Math.max(0.7, 1.0 - (numLegalMoves - 35) * 0.008);
        } else if (numLegalMoves < 10) {
            complexityPenalty = Math.min(1.1, 1.0 + (10 - numLegalMoves) * 0.02);
        }

        // Forcing bonus
        let forcingBonus = 1.0;
        if (tags && tags.includes('check')) {
            forcingBonus = 1.05;
        } else if (tags && (tags.includes('capture') || tags.includes('recapture'))) {
            forcingBonus = 1.03;
        }

        // Tactical motif overlay
        let motifBonus = 0.0;
        if (tacticalMotifs) {
            for (const motif of tacticalMotifs) {
                const key = motif.toLowerCase().replace(/ /g, '_');
                const info = TACTICAL_MOTIF_THRESHOLDS[key];
                if (info) {
                    const distance = this.playerRating - info.threshold;
                    if (distance > -200) {
                        const ramp = 1.0 / (1.0 + Math.exp(-0.02 * distance));
                        motifBonus = Math.max(motifBonus, info.bonus * ramp);
                    }
                }
            }
        }

        return Math.min(1.0, base * complexityPenalty * forcingBonus + motifBonus);
    }

    /**
     * Get human-readable findability label.
     */
    getLabel(score) {
        if (score >= 0.90) return 'obvious';
        if (score >= 0.70) return 'natural';
        if (score >= 0.45) return 'findable';
        if (score >= 0.20) return 'difficult';
        return 'engine-only';
    }

    /**
     * Format score for display.
     */
    formatScore(score) {
        return `${Math.round(score * 100)}% (${this.getLabel(score)})`;
    }
}
