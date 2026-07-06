"""Structured fact extraction from Stockfish analysis."""
import chess
from dataclasses import dataclass, field, asdict
from typing import Optional
import json

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from engine.stockfish_engine import FastStockfish, PositionInfo, ThreatInfo
from engine.candidates import CandidateFilter
from engine.findability import FindabilityCalculator
from config import SKILL_LEVELS, DEFAULT_PLAYER_RATING


@dataclass
class MoveFacts:
    """Structured facts about a move for LLM consumption."""
    # Position context
    position_fen: str
    side_to_move: str
    move_number: int

    # The move being analyzed
    played_move_uci: str
    played_move_san: str

    # Engine evaluation
    eval_before_cp: int
    eval_after_cp: int
    cp_loss: int

    # Best move comparison
    best_move_uci: str
    best_move_san: str
    best_move_eval_cp: int

    # Classification
    move_quality: str  # "best", "good", "inaccuracy", "mistake", "blunder"
    is_played_findable: bool
    played_move_tags: list[str]
    is_best_findable: bool
    best_move_tags: list[str]

    # Position characteristics
    position_type: str  # "opening", "middlegame", "endgame"
    is_tactical: bool
    position_fragility: float
    is_check: bool
    is_in_check: bool

    # Best findable alternative (if best move is unfindable)
    best_findable_move_uci: Optional[str]
    best_findable_move_san: Optional[str]
    best_findable_eval_cp: Optional[int]

    # Threats and tactics
    threats_created: list[str]
    threats_ignored: list[str]

    # Mate information
    mate_threat_before: Optional[int]
    mate_threat_after: Optional[int]

    # Enhanced tactical data from FastStockfish
    threats_before: Optional[dict] = None
    threats_after: Optional[dict] = None
    tactical_motifs: list[str] = field(default_factory=list)
    top_lines: list[dict] = field(default_factory=list)

    # Findability scores (rating-parameterized)
    findability_score: Optional[float] = None
    findability_label: Optional[str] = None
    best_findability_score: Optional[float] = None

    # Material and structure
    material_balance: int = 0
    pawn_structure_type: Optional[str] = None
    king_safety_concern: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def _threat_info_to_dict(threat: ThreatInfo) -> dict:
    """Convert ThreatInfo to serializable dict."""
    return {
        "hanging_pieces": threat.hanging_pieces,
        "attacked_pieces": threat.attacked_pieces,
        "checks_available": threat.checks_available,
        "captures_available": threat.captures_available,
        "threats_to_king": threat.threats_to_king,
        "pins": threat.pins,
        "forks": threat.forks,
        "skewers": threat.skewers,
        "discovered_attacks": threat.discovered_attacks,
        "double_attacks": threat.double_attacks,
        "overloaded_pieces": threat.overloaded_pieces,
    }


def _extract_tactical_motifs(threats: ThreatInfo) -> list[str]:
    """Extract named tactical motifs from threat info."""
    motifs = []
    if threats.pins:
        motifs.append("pin")
    if threats.forks:
        motifs.append("fork")
    if threats.skewers:
        motifs.append("skewer")
    if threats.discovered_attacks:
        motifs.append("discovered_attack")
    if threats.double_attacks:
        motifs.append("double_attack")
    if threats.overloaded_pieces:
        motifs.append("overloaded")
    return motifs


class FactExtractor:
    """Extracts structured facts from position and move using FastStockfish."""

    def __init__(self, engine: FastStockfish = None, skill_level: str = "intermediate",
                 player_rating: int = None):
        self.engine = engine or FastStockfish()
        self.skill_level = skill_level
        self.candidate_filter = CandidateFilter(skill_level)
        self.findability = FindabilityCalculator(player_rating or DEFAULT_PLAYER_RATING)
        self.config = SKILL_LEVELS.get(skill_level, SKILL_LEVELS["intermediate"])

    def set_player_rating(self, rating: int):
        self.findability.set_rating(rating)

    def extract_facts(self, fen: str, played_move: str, move_number: int = 1) -> MoveFacts:
        """
        Extract all relevant facts about a move for explanation.

        Args:
            fen: Position before the move (FEN string)
            played_move: The move played (UCI or SAN format)
            move_number: Move number in the game

        Returns:
            MoveFacts with all structured data for LLM
        """
        board = chess.Board(fen)

        # Parse the move
        try:
            move = board.parse_uci(played_move)
            move_uci = played_move
        except ValueError:
            move = board.parse_san(played_move)
            move_uci = move.uci()

        move_san = board.san(move)

        # Analyze position before move with FastStockfish
        # All evals from engine are now normalized to WHITE's perspective
        info_before = self.engine.analyze_instant(fen, depth=14)

        # Best move from engine lines
        best_move_uci = info_before.lines[0].moves[0] if info_before.lines else "0000"
        try:
            best_move_san = board.san(board.parse_uci(best_move_uci))
        except Exception:
            best_move_san = best_move_uci

        # All evals are from White's perspective (positive = White advantage)
        eval_before = info_before.eval_cp
        mate_before = info_before.eval_mate
        best_eval = info_before.lines[0].eval_cp if info_before.lines else 0

        # For eval_after: check if played move is in the engine lines first
        # (avoids inconsistency from separate analysis at different depth)
        eval_after = None
        mate_after = None
        for line in info_before.lines:
            if line.moves and line.moves[0] == move_uci:
                eval_after = line.eval_cp
                mate_after = line.eval_mate
                break

        if eval_after is None:
            # Move not in engine lines — analyze after position separately
            board_after = board.copy()
            board_after.push(move)
            fen_after = board_after.fen()
            info_after = self.engine.analyze_instant(fen_after, depth=12)
            # info_after evals are already from White's perspective (engine normalizes)
            eval_after = info_after.eval_cp
            mate_after = info_after.eval_mate

        # CP loss: how much worse is the played move vs the best move?
        # Both evals are from White's perspective.
        # For White: cp_loss = best_eval - eval_after (White wants higher eval)
        # For Black: cp_loss = eval_after - best_eval (Black wants lower eval)
        is_white = board.turn == chess.WHITE
        if mate_before is not None and mate_after is None:
            # Had a mate, lost it
            cp_loss = 500
        elif mate_before is None:
            if is_white:
                cp_loss = max(0, best_eval - eval_after)
            else:
                cp_loss = max(0, eval_after - best_eval)
        else:
            cp_loss = 0

        # Classify move quality
        move_quality = self._classify_move(cp_loss, info_before)

        # Check findability (binary tags)
        is_played_findable, played_tags = self.candidate_filter.is_findable(board, move_uci)
        is_best_findable, best_tags = self.candidate_filter.is_findable(board, best_move_uci)

        # Rating-based findability scores
        tactical_motifs = _extract_tactical_motifs(info_before.threats)
        num_legal = info_before.legal_moves_count
        findability_score = self.findability.score_move(played_tags, tactical_motifs, num_legal)
        findability_label = self.findability.get_findability_label(findability_score)
        best_findability_score = self.findability.score_move(best_tags, tactical_motifs, num_legal)

        # Find best findable alternative
        best_findable = self._find_best_findable(board, info_before)

        # Determine position type
        position_type = self._determine_position_type(board, move_number)

        # Check for threats
        threats_created = self._detect_threats_created(board, move)
        threats_ignored = self._detect_threats_ignored(board, info_before)

        # Check states
        is_in_check = board.is_check()
        board.push(move)
        gives_check = board.is_check()
        board.pop()

        # Tactical status
        is_tactical = bool(tactical_motifs) or info_before.threats.threats_to_king
        position_fragility = self._estimate_fragility(info_before)

        # Top lines for LLM — include full PV (up to 10 moves)
        top_lines = []
        for line in info_before.lines[:3]:
            top_lines.append({
                "rank": line.rank,
                "moves_san": line.moves_san[:10],
                "eval_cp": line.eval_cp,
                "eval_mate": line.eval_mate,
                "eval": line.format_eval()
            })

        # Get threats for the after-position (for LLM context)
        board_after = board.copy()
        board_after.push(move)
        threats_after_info = self.engine._analyze_threats(board_after)

        # Pawn structure
        pawn_structure = self._classify_pawn_structure(board)

        # King safety
        king_safety = info_before.threats.threats_to_king

        return MoveFacts(
            position_fen=fen,
            side_to_move=info_before.turn,
            move_number=move_number,
            played_move_uci=move_uci,
            played_move_san=move_san,
            eval_before_cp=eval_before,
            eval_after_cp=eval_after,
            cp_loss=cp_loss,
            best_move_uci=best_move_uci,
            best_move_san=best_move_san,
            best_move_eval_cp=best_eval,
            move_quality=move_quality,
            is_played_findable=is_played_findable,
            played_move_tags=played_tags,
            is_best_findable=is_best_findable,
            best_move_tags=best_tags,
            position_type=position_type,
            is_tactical=is_tactical,
            position_fragility=position_fragility,
            is_check=gives_check,
            is_in_check=is_in_check,
            best_findable_move_uci=best_findable[0] if best_findable else None,
            best_findable_move_san=best_findable[1] if best_findable else None,
            best_findable_eval_cp=best_findable[2] if best_findable else None,
            threats_created=threats_created,
            threats_ignored=threats_ignored,
            mate_threat_before=mate_before,
            mate_threat_after=mate_after,
            threats_before=_threat_info_to_dict(info_before.threats),
            threats_after=_threat_info_to_dict(threats_after_info),
            tactical_motifs=tactical_motifs,
            top_lines=top_lines,
            findability_score=findability_score,
            findability_label=findability_label,
            best_findability_score=best_findability_score,
            material_balance=info_before.material_balance,
            pawn_structure_type=pawn_structure,
            king_safety_concern=king_safety,
        )

    def _classify_move(self, cp_loss: int, info: PositionInfo) -> str:
        """Classify move quality based on centipawn loss."""
        fragility = self._estimate_fragility(info)

        if fragility > 0.7:
            thresholds = {"good": 10, "inaccuracy": 30, "mistake": 80}
        elif fragility > 0.4:
            thresholds = {"good": 20, "inaccuracy": 50, "mistake": 150}
        else:
            thresholds = {"good": 30, "inaccuracy": 80, "mistake": 200}

        if cp_loss <= 5:
            return "best"
        elif cp_loss <= thresholds["good"]:
            return "good"
        elif cp_loss <= thresholds["inaccuracy"]:
            return "inaccuracy"
        elif cp_loss <= thresholds["mistake"]:
            return "mistake"
        else:
            return "blunder"

    def _estimate_fragility(self, info: PositionInfo) -> float:
        """Estimate position fragility from engine data."""
        score = 0.0
        threats = info.threats
        if threats.hanging_pieces:
            score += 0.3
        if threats.threats_to_king:
            score += 0.3
        if threats.forks or threats.pins:
            score += 0.2
        if threats.discovered_attacks or threats.skewers:
            score += 0.2
        # Spread between top lines
        if len(info.lines) >= 2:
            spread = abs(info.lines[0].eval_cp - info.lines[1].eval_cp)
            if spread > 100:
                score += 0.2
        return min(1.0, score)

    def _determine_position_type(self, board: chess.Board, move_number: int) -> str:
        piece_count = len(board.piece_map())
        if move_number <= 10 and piece_count >= 28:
            return "opening"
        elif piece_count <= 14:
            return "endgame"
        else:
            return "middlegame"

    def _find_best_findable(self, board: chess.Board, info: PositionInfo) -> Optional[tuple[str, str, int]]:
        """Find the best engine move that is also findable."""
        for line in info.lines:
            if line.moves:
                move_uci = line.moves[0]
                is_findable, _ = self.candidate_filter.is_findable(board, move_uci)
                if is_findable:
                    try:
                        san = board.san(board.parse_uci(move_uci))
                    except Exception:
                        san = move_uci
                    return (move_uci, san, line.eval_cp)
        return None

    def _detect_threats_created(self, board: chess.Board, move: chess.Move) -> list[str]:
        threats = []
        board.push(move)
        piece = board.piece_at(move.to_square)
        if piece:
            attacks = board.attacks(move.to_square)
            for sq in attacks:
                target = board.piece_at(sq)
                if target and target.color != piece.color:
                    defenders = board.attackers(target.color, sq)
                    piece_name = chess.piece_name(target.piece_type)
                    square_name = chess.square_name(sq)
                    if not defenders:
                        threats.append(f"attacks undefended {piece_name} on {square_name}")
                    elif self._piece_value(target) > self._piece_value(piece):
                        threats.append(f"attacks {piece_name} on {square_name}")
        board.pop()
        return threats[:3]

    def _detect_threats_ignored(self, board: chess.Board, info: PositionInfo) -> list[str]:
        threats = []
        side = board.turn
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == side:
                attackers = board.attackers(not side, sq)
                if attackers:
                    defenders = board.attackers(side, sq)
                    piece_name = chess.piece_name(piece.piece_type)
                    square_name = chess.square_name(sq)
                    if not defenders:
                        threats.append(f"{piece_name} on {square_name} is hanging")
                    elif len(attackers) > len(defenders):
                        threats.append(f"{piece_name} on {square_name} is under attack")
        return threats[:3]

    def _classify_pawn_structure(self, board: chess.Board) -> Optional[str]:
        """Simple pawn structure classification."""
        white_pawns = set()
        black_pawns = set()
        for sq in chess.SQUARES:
            p = board.piece_at(sq)
            if p and p.piece_type == chess.PAWN:
                f = chess.square_file(sq)
                if p.color == chess.WHITE:
                    white_pawns.add(f)
                else:
                    black_pawns.add(f)

        # IQP detection: isolated d-pawn
        if 3 in white_pawns and 2 not in white_pawns and 4 not in white_pawns:
            return "IQP"
        if 3 in black_pawns and 2 not in black_pawns and 4 not in black_pawns:
            return "IQP"

        # Check for doubled pawns
        all_pawns = []
        for sq in chess.SQUARES:
            p = board.piece_at(sq)
            if p and p.piece_type == chess.PAWN:
                all_pawns.append((chess.square_file(sq), p.color))
        file_counts_w = {}
        file_counts_b = {}
        for f, c in all_pawns:
            if c == chess.WHITE:
                file_counts_w[f] = file_counts_w.get(f, 0) + 1
            else:
                file_counts_b[f] = file_counts_b.get(f, 0) + 1
        if any(v > 1 for v in file_counts_w.values()) or any(v > 1 for v in file_counts_b.values()):
            return "doubled_pawns"

        return None

    def _piece_value(self, piece) -> int:
        if piece is None:
            return 0
        values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
        }
        return values.get(piece.piece_type, 0)
