"""Stockfish analysis wrapper."""
import chess
from stockfish import Stockfish
from typing import Optional
from dataclasses import dataclass

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from config import STOCKFISH_PATH, STOCKFISH_DEPTH, STOCKFISH_DEPTH_QUICK, STOCKFISH_THREADS, STOCKFISH_HASH_MB, MULTIPV


@dataclass
class MoveAnalysis:
    """Analysis result for a single move."""
    move: str
    eval_cp: int  # centipawns, from side to move's perspective
    eval_mate: Optional[int]  # mate in N, None if not mate
    pv: list[str]  # principal variation
    is_best: bool
    rank: int  # 1 = best, 2 = second best, etc.


@dataclass
class PositionAnalysis:
    """Full analysis of a position."""
    fen: str
    eval_cp: int
    eval_mate: Optional[int]
    best_move: str
    top_moves: list[MoveAnalysis]
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    side_to_move: str  # "white" or "black"


class StockfishAnalyzer:
    """Wrapper around Stockfish for position analysis."""

    def __init__(self, path: str = None, depth: int = None):
        self.path = path or str(STOCKFISH_PATH)
        self.depth = depth or STOCKFISH_DEPTH
        self._engine = None

    def _get_engine(self) -> Stockfish:
        """Lazy initialization of Stockfish."""
        if self._engine is None:
            self._engine = Stockfish(
                path=self.path,
                depth=self.depth,
                parameters={
                    "Threads": STOCKFISH_THREADS,
                    "Hash": STOCKFISH_HASH_MB,
                    "MultiPV": MULTIPV
                }
            )
        return self._engine

    def analyze_position_quick(self, fen: str) -> PositionAnalysis:
        """Quick analysis for real-time UI feedback."""
        return self._analyze_position_at_depth(fen, STOCKFISH_DEPTH_QUICK)

    def analyze_position(self, fen: str) -> PositionAnalysis:
        """Standard analysis."""
        return self._analyze_position_at_depth(fen, self.depth)

    def _analyze_position_at_depth(self, fen: str, depth: int) -> PositionAnalysis:
        """Analyze a position and return top moves with evaluations."""
        engine = self._get_engine()
        engine.set_depth(depth)  # Set analysis depth
        engine.set_fen_position(fen)

        board = chess.Board(fen)

        # Get top moves
        top_moves_raw = engine.get_top_moves(MULTIPV)

        top_moves = []
        for i, move_data in enumerate(top_moves_raw):
            move_str = move_data.get("Move", "")

            # Parse centipawn or mate score
            eval_cp = 0
            eval_mate = None

            if "Centipawn" in move_data:
                eval_cp = move_data["Centipawn"]
            if "Mate" in move_data and move_data["Mate"] is not None:
                eval_mate = move_data["Mate"]
                # Convert mate to large centipawn value for comparison
                eval_cp = 10000 - abs(eval_mate) * 10 if eval_mate > 0 else -10000 + abs(eval_mate) * 10

            top_moves.append(MoveAnalysis(
                move=move_str,
                eval_cp=eval_cp,
                eval_mate=eval_mate,
                pv=move_data.get("Line", "").split() if move_data.get("Line") else [move_str],
                is_best=(i == 0),
                rank=i + 1
            ))

        # Get overall evaluation
        eval_dict = engine.get_evaluation()
        main_eval_cp = 0
        main_eval_mate = None

        if eval_dict["type"] == "cp":
            main_eval_cp = eval_dict["value"]
        elif eval_dict["type"] == "mate":
            main_eval_mate = eval_dict["value"]
            main_eval_cp = 10000 - abs(eval_dict["value"]) * 10 if eval_dict["value"] > 0 else -10000 + abs(eval_dict["value"]) * 10

        return PositionAnalysis(
            fen=fen,
            eval_cp=main_eval_cp,
            eval_mate=main_eval_mate,
            best_move=top_moves[0].move if top_moves else "",
            top_moves=top_moves,
            is_check=board.is_check(),
            is_checkmate=board.is_checkmate(),
            is_stalemate=board.is_stalemate(),
            side_to_move="white" if board.turn == chess.WHITE else "black"
        )

    def analyze_move(self, fen: str, move: str) -> tuple[int, Optional[int]]:
        """
        Analyze a specific move and return (eval_cp, eval_mate) after the move.
        Move should be in UCI format (e.g., 'e2e4').
        """
        engine = self._get_engine()
        board = chess.Board(fen)

        # Parse move
        try:
            chess_move = board.parse_uci(move)
        except ValueError:
            # Try SAN format
            chess_move = board.parse_san(move)

        # Make the move
        board.push(chess_move)
        new_fen = board.fen()

        # Analyze new position
        engine.set_fen_position(new_fen)
        eval_dict = engine.get_evaluation()

        eval_cp = 0
        eval_mate = None

        if eval_dict["type"] == "cp":
            # Negate because we want eval from original side's perspective
            eval_cp = -eval_dict["value"]
        elif eval_dict["type"] == "mate":
            mate_value = eval_dict["value"]
            # mate=0 means the side to move is already mated
            # Since we just moved, opponent is mated = good for us = +10000
            if mate_value == 0:
                eval_cp = 10000  # We delivered checkmate
                eval_mate = 0
            elif mate_value > 0:
                # Opponent has mate in N = bad for us
                eval_mate = -mate_value
                eval_cp = -10000 + mate_value * 10
            else:
                # Opponent getting mated in N = good for us
                eval_mate = -mate_value
                eval_cp = 10000 - abs(mate_value) * 10

        return eval_cp, eval_mate

    def get_cp_loss(self, fen: str, played_move: str) -> int:
        """
        Calculate centipawn loss for a move.
        Returns positive value = move is worse than best.
        """
        # Get eval before
        analysis = self.analyze_position(fen)
        eval_before = analysis.eval_cp
        best_move = analysis.best_move

        # Get eval after played move
        eval_after, _ = self.analyze_move(fen, played_move)

        # Get eval after best move for comparison
        best_eval_after, _ = self.analyze_move(fen, best_move)

        # CP loss = how much worse than best
        cp_loss = best_eval_after - eval_after

        return max(0, cp_loss)

    def is_tactical_position(self, fen: str) -> bool:
        """Check if position has tactical tension (captures, checks available)."""
        board = chess.Board(fen)

        # Check for forcing moves
        has_captures = any(board.is_capture(m) for m in board.legal_moves)
        is_in_check = board.is_check()

        # Check for checks available
        has_checks = False
        for move in board.legal_moves:
            board.push(move)
            if board.is_check():
                has_checks = True
            board.pop()
            if has_checks:
                break

        return has_captures or is_in_check or has_checks

    def get_position_fragility(self, fen: str) -> float:
        """
        Estimate position fragility (0-1).
        High fragility = mistakes are costly.
        """
        analysis = self.analyze_position(fen)

        # Factors that increase fragility
        fragility = 0.0

        # Mate threats
        if analysis.eval_mate is not None:
            return 1.0

        # Large eval swings between top moves
        if len(analysis.top_moves) >= 2:
            swing = abs(analysis.top_moves[0].eval_cp - analysis.top_moves[1].eval_cp)
            if swing > 200:
                fragility += 0.4
            elif swing > 100:
                fragility += 0.2

        # Tactical position
        if self.is_tactical_position(fen):
            fragility += 0.3

        # In check
        if analysis.is_check:
            fragility += 0.2

        return min(1.0, fragility)

    def close(self):
        """Clean up Stockfish process."""
        if self._engine:
            del self._engine
            self._engine = None
