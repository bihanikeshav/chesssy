"""LLM-based move explanation using Claude API."""
import chess
from typing import Optional, Generator

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from explainer.facts import MoveFacts
from explainer.claude_client import ClaudeClient
from explainer.prompt_builder import PromptBuilder
from config import SKILL_LEVELS


# Chess knowledge for rule-based fallback
OPENING_PRINCIPLES = """
Opening principles:
- Control the center with pawns (e4, d4, e5, d5)
- Develop knights before bishops
- Don't move the same piece twice without reason
- Castle early for king safety
- Don't bring the queen out too early
- Connect your rooks
- f2/f7 are the weakest squares (only king defends)
"""

COMMON_MISTAKES = {
    "f6": "weakens the kingside (e5 and h4-d8 diagonal), blocks the knight from its best square",
    "f3": "weakens the kingside, blocks the knight from f3, weakens e3",
    "h6": "wastes tempo, weakens g6 if bishop develops to g5 later",
    "a6": "wastes tempo unless preparing b5",
    "h3": "wastes tempo unless stopping a pin",
    "Qh5": "develops queen too early, can be attacked with tempo",
    "Qf3": "develops queen too early, blocks knight from f3",
}

GOOD_OPENING_MOVES = {
    "e4": "controls the center and opens lines for the queen and bishop",
    "d4": "controls the center and opens the diagonal for the dark-squared bishop",
    "c4": "the English Opening - controls d5 and prepares a flexible pawn structure",
    "Nf3": "develops the knight to its best square, controls e5 and d4",
    "Nc3": "develops the knight toward the center",
    "Bc4": "develops the bishop to an active diagonal targeting f7",
    "Bb5": "the Spanish/Ruy Lopez bishop, pins or pressures the knight",
    "d3": "solid setup, supports e4 and prepares piece development",
    "g3": "fianchetto setup, prepares Bg2 controlling the long diagonal",
    "e5": "fights for the center, classical response to e4",
    "d5": "fights for the center, solid and active",
    "c5": "the Sicilian Defense - fights for d4 control asymmetrically",
    "Nf6": "develops the knight and attacks e4",
    "Nc6": "develops the knight toward the center",
    "e6": "the French Defense setup - solid and prepares d5",
    "c6": "the Caro-Kann - solid, prepares d5",
    "O-O": "castles kingside for king safety and connects the rooks",
    "O-O-O": "castles queenside, often preparing a kingside attack",
}


class LLMExplainer:
    """Generates human-readable explanations from structured facts."""

    def __init__(self, skill_level: str = "intermediate"):
        self.skill_level = skill_level
        self.config = SKILL_LEVELS.get(skill_level, SKILL_LEVELS["intermediate"])
        self.claude = ClaudeClient()
        self.prompt_builder = PromptBuilder(skill_level)
        self._api_available = None

    def _check_api(self) -> bool:
        """Check API availability (retry on failure)."""
        if self._api_available is not True:
            self._api_available = self.claude.is_available()
        return self._api_available

    def set_skill_level(self, level: str):
        self.skill_level = level
        self.config = SKILL_LEVELS.get(level, SKILL_LEVELS["intermediate"])
        self.prompt_builder.set_skill_mode(level)

    def explain(self, facts: MoveFacts, rag_passages: list = None) -> str:
        """Generate a human-readable explanation for the move."""
        # Try Claude API first
        if self._check_api():
            try:
                system, user = self.prompt_builder.build(
                    facts,
                    findability_score=facts.findability_score,
                    findability_label=facts.findability_label,
                    engine_lines=facts.top_lines,
                    threats_before=_dict_to_threat_proxy(facts.threats_before) if facts.threats_before else None,
                    threats_after=_dict_to_threat_proxy(facts.threats_after) if facts.threats_after else None,
                    tactical_motifs=facts.tactical_motifs,
                    rag_passages=rag_passages,
                )
                response = self.claude.generate(system, user)
                if response and len(response) > 20:
                    return response
            except Exception:
                self._api_available = None  # Reset to retry next time

        # Fallback to rule-based
        return self._generate_chess_explanation(facts)

    def explain_stream(self, facts: MoveFacts, rag_passages: list = None) -> Generator[str, None, None]:
        """Stream explanation tokens via SSE."""
        if not self._check_api():
            yield self._generate_chess_explanation(facts)
            return

        try:
            system, user = self.prompt_builder.build(
                facts,
                findability_score=facts.findability_score,
                findability_label=facts.findability_label,
                engine_lines=facts.top_lines,
                threats_before=_dict_to_threat_proxy(facts.threats_before) if facts.threats_before else None,
                threats_after=_dict_to_threat_proxy(facts.threats_after) if facts.threats_after else None,
                tactical_motifs=facts.tactical_motifs,
                rag_passages=rag_passages,
            )
            for chunk in self.claude.stream(system, user):
                yield chunk
        except Exception:
            self._api_available = None  # Reset to retry next time
            yield self._generate_chess_explanation(facts)

    def _generate_chess_explanation(self, facts: MoveFacts) -> str:
        """Generate explanation using chess knowledge rules (fallback)."""
        move_san = facts.played_move_san
        best_san = facts.best_move_san
        cp_loss = facts.cp_loss

        # Check for known good opening moves
        if move_san in GOOD_OPENING_MOVES and facts.move_quality in ["best", "good"]:
            explanation = GOOD_OPENING_MOVES[move_san]
            if facts.move_quality == "best":
                return f"{move_san} {explanation}. Excellent choice!"
            else:
                return f"{move_san} {explanation}. {best_san} was slightly more precise."

        parts = []

        # Quality assessment
        if facts.move_quality == "best":
            if move_san in GOOD_OPENING_MOVES:
                return f"{move_san} {GOOD_OPENING_MOVES[move_san]}."
            return f"{move_san} is the best move in this position."
        elif facts.move_quality == "good":
            if move_san in GOOD_OPENING_MOVES:
                return f"{move_san} {GOOD_OPENING_MOVES[move_san]}. {best_san} was marginally better."
            return f"{move_san} is a solid move. {best_san} was slightly more accurate."

        # For suboptimal moves, explain WHY it's bad
        specific_problem = None
        for pattern, problem in COMMON_MISTAKES.items():
            if pattern in move_san:
                specific_problem = problem
                break

        if facts.position_type == "opening":
            if move_san.startswith("f") and "x" not in move_san:
                parts.append(f"{move_san} weakens the kingside and blocks the knight from developing to f6.")
            elif move_san.startswith("h") and "x" not in move_san:
                parts.append(f"{move_san} wastes time in the opening without developing a piece.")
            elif move_san.startswith("a") and "x" not in move_san:
                parts.append(f"{move_san} doesn't help with development or center control.")
            elif move_san.startswith("Q") and facts.move_number <= 5:
                parts.append(f"{move_san} brings the queen out too early, where it can be attacked.")
            elif specific_problem:
                parts.append(f"{move_san} {specific_problem}.")
            else:
                parts.append(f"{move_san} is not the most effective move here.")

        # Explain what the best move achieves
        if facts.best_move_tags:
            if "development" in facts.best_move_tags:
                parts.append(f"{best_san} develops a piece actively.")
            elif "central_pawn" in facts.best_move_tags:
                parts.append(f"{best_san} controls the center.")
            elif "castling" in facts.best_move_tags:
                parts.append(f"{best_san} secures the king.")
            elif "threat" in facts.best_move_tags:
                parts.append(f"{best_san} creates immediate threats.")
            else:
                parts.append(f"{best_san} was the better choice.")
        else:
            parts.append(f"{best_san} was stronger.")

        # Add severity
        if facts.move_quality == "blunder":
            parts.insert(0, f"Blunder! This loses {cp_loss/100:.1f} pawns.")
        elif facts.move_quality == "mistake":
            parts.insert(0, f"Mistake losing {cp_loss/100:.1f} pawns.")

        return " ".join(parts) if parts else f"{move_san} is a suboptimal choice. {best_san} was better."

    def explain_with_alternative(self, facts: MoveFacts, rag_passages: list = None) -> dict:
        """Generate explanation with recommendation."""
        explanation = self.explain(facts, rag_passages)

        result = {
            "explanation": explanation,
            "recommendation": None,
            "difficulty": facts.findability_label or ("findable" if facts.is_best_findable else "requires_calculation"),
            "findability_score": facts.findability_score,
        }

        if facts.move_quality in ["inaccuracy", "mistake", "blunder"]:
            if facts.is_best_findable:
                result["recommendation"] = f"Better was {facts.best_move_san}"
            elif facts.best_findable_move_san:
                result["recommendation"] = f"A good alternative was {facts.best_findable_move_san}"
            else:
                result["recommendation"] = f"Engine prefers {facts.best_move_san}, but this requires deep calculation"

        return result


class _DictProxy:
    """Proxy to access dict keys as attributes for prompt_builder compatibility."""
    def __init__(self, d):
        self._d = d or {}
    def __getattr__(self, name):
        return self._d.get(name, [])


def _dict_to_threat_proxy(d):
    return _DictProxy(d) if d else None


def quick_explain(fen: str, move: str, skill_level: str = "intermediate") -> str:
    """Convenience function for quick move explanation."""
    from explainer.facts import FactExtractor
    extractor = FactExtractor(skill_level=skill_level)
    facts = extractor.extract_facts(fen, move)
    explainer = LLMExplainer(skill_level=skill_level)
    return explainer.explain(facts)
