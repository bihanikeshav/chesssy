"""5-layer prompt builder for chess move explanations."""
from typing import Optional


SYSTEM_PROMPTS = {
    "beginner": """You are a friendly chess coach explaining moves to a beginner (rated ~800-1200).
Use simple language. Avoid complex chess jargon — when you must use a term (like "pin" or "fork"), briefly explain it.
Use analogies when helpful. Focus on the most important point, don't overwhelm with details.
Keep sentences short and clear. Be encouraging but honest about mistakes.""",

    "intermediate": """You are a chess coach explaining moves to an intermediate player (rated ~1200-1600).
Use standard chess terminology (pins, forks, outposts, initiative, etc.) without over-explaining.
Include concrete variations when relevant (e.g., "after 5...Nxd5 6.c4 Nb6, White gains space").
Be direct and analytical. Focus on strategic and tactical nuances.""",
}

EXPLANATION_TEMPLATE = """Analyze this chess move and provide a structured explanation.

**Position:** {position_fen}
**Move played:** {played_move_san} ({move_quality})
**Game phase:** {position_type} (move {move_number})
**Side:** {side_to_move}

**Evaluation:**
- Before: {eval_before} | After: {eval_after}
- CP loss: {cp_loss}
{mate_info}

**Best move:** {best_move_san} (eval: {best_eval})
{best_findable_info}

**Move tags:** {played_tags}
**Findability:** {findability_info}

**Tactical features:**
{tactical_features}

**Engine lines:**
{engine_lines}

{rag_context}

---

{output_instruction}"""

DETAILED_OUTPUT = """Provide a 5-layer explanation:
1. **What the move does** — Describe the immediate effect on the board
2. **Strategic context** — Why this matters for the position's plans and structure
3. **Alternatives** — Compare with the best move, include a concrete variation if relevant
4. **Opponent's dilemma** — What problems does the opponent now face (or what problems were missed)?
5. **Reusable lesson** — One takeaway principle the player can apply in future games

Be thorough since this is a {quality_reason} move."""

BRIEF_OUTPUT = """Give a concise explanation (2-3 sentences):
- What the move achieves and why it's {quality_word}
- One key insight about the position

Keep it brief since this is a {quality_word} move — the player made the right choice."""


class PromptBuilder:
    """Builds structured prompts for Claude with all available data."""

    def __init__(self, skill_mode: str = "intermediate"):
        self.skill_mode = skill_mode

    def set_skill_mode(self, mode: str):
        if mode in SYSTEM_PROMPTS:
            self.skill_mode = mode

    def build(self, facts, findability_score: float = None,
              findability_label: str = None, engine_lines: list = None,
              threats_before=None, threats_after=None,
              tactical_motifs: list = None, rag_passages: list = None) -> tuple[str, str]:
        """
        Build system + user prompts from all available data.

        Returns:
            (system_prompt, user_prompt) tuple
        """
        system = SYSTEM_PROMPTS.get(self.skill_mode, SYSTEM_PROMPTS["intermediate"])

        # Format eval values
        eval_before = self._format_eval(facts.eval_before_cp, facts.mate_threat_before)
        eval_after = self._format_eval(facts.eval_after_cp, facts.mate_threat_after)
        best_eval = self._format_eval(facts.best_move_eval_cp, None)

        # Mate info
        mate_info = ""
        if facts.mate_threat_before is not None:
            mate_info += f"- Mate threat before: M{facts.mate_threat_before}\n"
        if facts.mate_threat_after is not None:
            mate_info += f"- Mate threat after: M{facts.mate_threat_after}\n"

        # Best findable alternative
        best_findable_info = ""
        if facts.best_findable_move_san and facts.best_findable_move_san != facts.best_move_san:
            best_findable_info = f"**Best findable alternative:** {facts.best_findable_move_san} (eval: {self._format_eval(facts.best_findable_eval_cp, None)})"

        # Findability info
        if findability_score is not None:
            findability_info = f"{int(findability_score * 100)}% ({findability_label or 'unknown'})"
        else:
            findability_info = "findable" if facts.is_played_findable else "requires calculation"

        # Tactical features
        tactical_features = self._format_tactical_features(threats_before, threats_after, tactical_motifs)

        # Engine lines
        engine_lines_str = self._format_engine_lines(engine_lines)

        # RAG context
        rag_context = self._format_rag_context(rag_passages)

        # Output instruction (adaptive depth)
        output_instruction = self._get_output_instruction(facts.move_quality)

        user = EXPLANATION_TEMPLATE.format(
            position_fen=facts.position_fen,
            played_move_san=facts.played_move_san,
            move_quality=facts.move_quality,
            position_type=facts.position_type,
            move_number=facts.move_number,
            side_to_move=facts.side_to_move,
            eval_before=eval_before,
            eval_after=eval_after,
            cp_loss=f"{facts.cp_loss / 100:.2f} pawns" if facts.cp_loss else "0",
            mate_info=mate_info,
            best_move_san=facts.best_move_san,
            best_eval=best_eval,
            best_findable_info=best_findable_info,
            played_tags=", ".join(facts.played_move_tags) if facts.played_move_tags else "quiet move",
            findability_info=findability_info,
            tactical_features=tactical_features,
            engine_lines=engine_lines_str,
            rag_context=rag_context,
            output_instruction=output_instruction
        )

        return system, user

    def _format_eval(self, cp: int, mate: Optional[int]) -> str:
        if mate is not None:
            sign = "+" if mate > 0 else "-"
            return f"{sign}M{abs(mate)}"
        if cp is None:
            return "0.00"
        return f"{cp / 100:+.2f}"

    def _format_tactical_features(self, threats_before, threats_after, tactical_motifs) -> str:
        parts = []

        if threats_before:
            if hasattr(threats_before, 'hanging_pieces') and threats_before.hanging_pieces:
                parts.append(f"- Hanging pieces (before): {', '.join(threats_before.hanging_pieces[:3])}")
            if hasattr(threats_before, 'pins') and threats_before.pins:
                parts.append(f"- Pins: {', '.join(threats_before.pins[:3])}")
            if hasattr(threats_before, 'forks') and threats_before.forks:
                parts.append(f"- Fork opportunities: {', '.join(threats_before.forks[:3])}")
            if hasattr(threats_before, 'skewers') and threats_before.skewers:
                parts.append(f"- Skewers: {', '.join(threats_before.skewers[:3])}")
            if hasattr(threats_before, 'discovered_attacks') and threats_before.discovered_attacks:
                parts.append(f"- Discovered attacks: {', '.join(threats_before.discovered_attacks[:3])}")
            if hasattr(threats_before, 'overloaded_pieces') and threats_before.overloaded_pieces:
                parts.append(f"- Overloaded pieces: {', '.join(threats_before.overloaded_pieces[:3])}")
            if hasattr(threats_before, 'checks_available') and threats_before.checks_available:
                parts.append(f"- Available checks: {', '.join(threats_before.checks_available[:3])}")

        if threats_after:
            if hasattr(threats_after, 'hanging_pieces') and threats_after.hanging_pieces:
                parts.append(f"- Hanging pieces (after move): {', '.join(threats_after.hanging_pieces[:3])}")

        if tactical_motifs:
            parts.append(f"- Tactical motifs in position: {', '.join(tactical_motifs[:5])}")

        return "\n".join(parts) if parts else "- No significant tactical features"

    def _format_engine_lines(self, engine_lines) -> str:
        if not engine_lines:
            return "- Not available"

        parts = []
        for line in engine_lines[:3]:
            if hasattr(line, 'moves_san') and line.moves_san:
                moves_str = " ".join(line.moves_san[:8])
                eval_str = line.format_eval() if hasattr(line, 'format_eval') else str(line.eval_cp)
                parts.append(f"- Line {line.rank}: {moves_str} ({eval_str})")
            elif isinstance(line, dict):
                moves_str = " ".join(line.get("moves_san", [])[:8])
                eval_str = line.get("eval", "?")
                parts.append(f"- Line {line.get('rank', '?')}: {moves_str} ({eval_str})")

        return "\n".join(parts) if parts else "- Not available"

    def _format_rag_context(self, rag_passages) -> str:
        if not rag_passages:
            return ""

        parts = ["**Relevant chess theory:**"]
        for passage in rag_passages[:3]:
            if isinstance(passage, dict):
                title = passage.get("title", "")
                content = passage.get("content", passage.get("document", ""))
                if title:
                    parts.append(f"- *{title}*: {content[:200]}")
                else:
                    parts.append(f"- {content[:200]}")
            elif isinstance(passage, str):
                parts.append(f"- {passage[:200]}")

        return "\n".join(parts)

    def _get_output_instruction(self, move_quality: str) -> str:
        if move_quality in ["best", "good"]:
            return BRIEF_OUTPUT.format(quality_word=move_quality)
        else:
            quality_reason = {
                "inaccuracy": "an inaccuracy",
                "mistake": "a mistake",
                "blunder": "a blunder"
            }.get(move_quality, "suboptimal")
            return DETAILED_OUTPUT.format(quality_reason=quality_reason)
