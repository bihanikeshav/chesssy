"""Rating-parameterized findability scoring for chess moves."""
import math
import chess
from typing import Optional


# Base pattern findability scores at rating breakpoints
# Each pattern maps to {rating: probability}
PATTERN_SCORES = {
    "check":        {800: 0.95, 1200: 0.99, 1600: 1.0,  2000: 1.0},
    "capture":      {800: 0.90, 1200: 0.95, 1600: 0.99, 2000: 1.0},
    "recapture":    {800: 0.85, 1200: 0.95, 1600: 0.99, 2000: 1.0},
    "promotion":    {800: 0.90, 1200: 0.95, 1600: 0.99, 2000: 1.0},
    "castling":     {800: 0.70, 1200: 0.90, 1600: 0.98, 2000: 1.0},
    "central_pawn": {800: 0.50, 1200: 0.75, 1600: 0.90, 2000: 0.98},
    "development":  {800: 0.30, 1200: 0.65, 1600: 0.85, 2000: 0.95},
    "defense":      {800: 0.15, 1200: 0.40, 1600: 0.70, 2000: 0.90},
    "threat":       {800: 0.20, 1200: 0.50, 1600: 0.75, 2000: 0.90},
    "improvement":  {800: 0.10, 1200: 0.35, 1600: 0.60, 2000: 0.85},
    "sacrifice":    {800: 0.05, 1200: 0.15, 1600: 0.35, 2000: 0.65},
}

# Quiet move (no tags) baseline
QUIET_SCORES = {800: 0.02, 1200: 0.10, 1600: 0.25, 2000: 0.60}

# Tactical motif rating thresholds (rating at which player starts finding them)
TACTICAL_MOTIF_THRESHOLDS = {
    "fork":              {"threshold": 1200, "bonus": 0.15},
    "pin":               {"threshold": 1400, "bonus": 0.10},
    "skewer":            {"threshold": 1500, "bonus": 0.10},
    "discovered_attack": {"threshold": 1600, "bonus": 0.12},
    "double_attack":     {"threshold": 1300, "bonus": 0.12},
    "overloaded":        {"threshold": 1800, "bonus": 0.08},
}


def _sigmoid_interpolate(rating: int, breakpoints: dict[int, float]) -> float:
    """
    Interpolate between rating breakpoints using sigmoid-like curves.
    Returns a probability value between 0 and 1.
    """
    ratings = sorted(breakpoints.keys())

    # Clamp to range
    if rating <= ratings[0]:
        return breakpoints[ratings[0]]
    if rating >= ratings[-1]:
        return breakpoints[ratings[-1]]

    # Find surrounding breakpoints
    for i in range(len(ratings) - 1):
        if ratings[i] <= rating <= ratings[i + 1]:
            r_low, r_high = ratings[i], ratings[i + 1]
            v_low, v_high = breakpoints[r_low], breakpoints[r_high]

            # Sigmoid interpolation: map [r_low, r_high] -> [-4, 4] -> sigmoid -> [v_low, v_high]
            t = (rating - r_low) / (r_high - r_low)
            sigmoid_t = 1.0 / (1.0 + math.exp(-8 * (t - 0.5)))
            return v_low + (v_high - v_low) * sigmoid_t

    return 0.0


class FindabilityCalculator:
    """Rating-parameterized probability scoring for move findability."""

    def __init__(self, player_rating: int = 1200):
        self.player_rating = max(800, min(2000, player_rating))

    def set_rating(self, rating: int):
        self.player_rating = max(800, min(2000, rating))

    def score_move(self, tags: list[str], tactical_motifs: Optional[list[str]] = None,
                   num_legal_moves: int = 30) -> float:
        """
        Calculate findability probability for a move.

        P(find | rating) = max(base_pattern_scores) * complexity_penalty * forcing_bonus

        Args:
            tags: Move tags from CandidateFilter (check, capture, etc.)
            tactical_motifs: Tactical motifs involved (fork, pin, etc.)
            num_legal_moves: Number of legal moves in position (affects complexity)

        Returns:
            Probability 0.0 - 1.0 that the player would find this move
        """
        if not tags:
            # Quiet move with no tags
            base = _sigmoid_interpolate(self.player_rating, QUIET_SCORES)
        else:
            # Take the max pattern score (most findable characteristic wins)
            scores = []
            for tag in tags:
                if tag in PATTERN_SCORES:
                    scores.append(_sigmoid_interpolate(self.player_rating, PATTERN_SCORES[tag]))
            base = max(scores) if scores else _sigmoid_interpolate(self.player_rating, QUIET_SCORES)

        # Complexity penalty: more legal moves = harder to find the right one
        complexity_penalty = 1.0
        if num_legal_moves > 35:
            complexity_penalty = max(0.7, 1.0 - (num_legal_moves - 35) * 0.008)
        elif num_legal_moves < 10:
            # Fewer choices = easier
            complexity_penalty = min(1.1, 1.0 + (10 - num_legal_moves) * 0.02)

        # Forcing bonus: checks and captures are naturally considered first
        forcing_bonus = 1.0
        if "check" in tags:
            forcing_bonus = 1.05
        elif "capture" in tags or "recapture" in tags:
            forcing_bonus = 1.03

        # Tactical motif overlay
        motif_bonus = 0.0
        if tactical_motifs:
            for motif in tactical_motifs:
                motif_key = motif.lower().replace(" ", "_")
                for key, info in TACTICAL_MOTIF_THRESHOLDS.items():
                    if key == motif_key:
                        # Sigmoid ramp: 0 below threshold, ramps up over ~200 rating points
                        distance = self.player_rating - info["threshold"]
                        if distance > -200:
                            ramp = 1.0 / (1.0 + math.exp(-0.02 * distance))
                            motif_bonus = max(motif_bonus, info["bonus"] * ramp)
                        break

        result = base * complexity_penalty * forcing_bonus + motif_bonus
        return round(min(1.0, max(0.0, result)), 3)

    def score_position_moves(self, board: chess.Board, move_tags_map: dict[str, list[str]],
                             tactical_motifs: Optional[list[str]] = None) -> dict[str, float]:
        """
        Score findability for multiple moves in a position.

        Args:
            board: Chess board position
            move_tags_map: {move_uci: [tags]} from CandidateFilter
            tactical_motifs: Global tactical motifs in position

        Returns:
            {move_uci: findability_score}
        """
        num_legal = len(list(board.legal_moves))
        scores = {}
        for move_uci, tags in move_tags_map.items():
            scores[move_uci] = self.score_move(tags, tactical_motifs, num_legal)
        return scores

    def get_findability_label(self, score: float) -> str:
        """Human-readable findability label."""
        if score >= 0.90:
            return "obvious"
        elif score >= 0.70:
            return "natural"
        elif score >= 0.45:
            return "findable"
        elif score >= 0.20:
            return "difficult"
        else:
            return "engine-only"

    def format_score(self, score: float) -> str:
        """Format score for display."""
        label = self.get_findability_label(score)
        pct = int(score * 100)
        return f"{pct}% ({label})"

    def find_best_findable_move(self, board: chess.Board, engine_lines: list[dict],
                                tactical_motifs: Optional[list[str]] = None,
                                num_legal: int = 30) -> Optional[dict]:
        """Find the best-scoring engine move that a human could plausibly find.

        Selects the highest-ranked engine move whose findability >= 0.5.
        If no move reaches 0.5, returns the move with the highest findability
        score among all engine lines.

        Args:
            board: Current board position.
            engine_lines: Engine analysis lines, each a dict with at least
                          'move' (uci string) and 'tags' (list of str).
                          Lines are assumed ordered best-first (index 0 = best).
            tactical_motifs: Tactical motifs present in the position.
            num_legal: Number of legal moves in the position.

        Returns:
            The selected engine line dict augmented with 'findability' score,
            or None if engine_lines is empty.
        """
        if not engine_lines:
            return None

        best_findable = None  # best line with score >= 0.5
        best_overall = None   # highest findability regardless of threshold
        best_overall_score = -1.0

        for line in engine_lines:
            tags = line.get("tags", [])
            score = self.score_move(tags, tactical_motifs, num_legal)
            line_with_score = {**line, "findability": score}

            if score > best_overall_score:
                best_overall_score = score
                best_overall = line_with_score

            if score >= 0.5 and best_findable is None:
                best_findable = line_with_score

        return best_findable if best_findable is not None else best_overall
