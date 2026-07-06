"""Candidate move filter - identifies 'findable' moves."""
import chess
from dataclasses import dataclass
from typing import Optional

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from config import SKILL_LEVELS


@dataclass
class CandidateMove:
    """A move that passes the findability filter."""
    move: chess.Move
    uci: str
    san: str
    tags: list[str]  # Why this move is findable
    is_forcing: bool


class CandidateFilter:
    """Filters moves to those a human might plausibly find."""

    # Piece development squares (simplified heuristic)
    GOOD_KNIGHT_SQUARES = {chess.C3, chess.F3, chess.C6, chess.F6,
                           chess.D4, chess.E4, chess.D5, chess.E5}
    GOOD_BISHOP_SQUARES = {chess.C4, chess.F4, chess.B5, chess.G5,
                           chess.C5, chess.F5, chess.B4, chess.G4}

    def __init__(self, skill_level: str = "intermediate"):
        self.skill_level = skill_level
        self.config = SKILL_LEVELS.get(skill_level, SKILL_LEVELS["intermediate"])

    def get_findable_moves(self, board: chess.Board) -> list[CandidateMove]:
        """
        Return list of moves a human at this skill level might consider.
        Uses binary inclusion filters, not scoring.
        """
        candidates = []

        for move in board.legal_moves:
            tags = self._get_move_tags(board, move)

            # Include if move has any findable tag
            if tags:
                candidates.append(CandidateMove(
                    move=move,
                    uci=move.uci(),
                    san=board.san(move),
                    tags=tags,
                    is_forcing=self._is_forcing(board, move)
                ))

        return candidates

    def _get_move_tags(self, board: chess.Board, move: chess.Move) -> list[str]:
        """Get tags explaining why this move might be found by a human."""
        tags = []

        # 1. Checks - always findable
        board.push(move)
        gives_check = board.is_check()
        board.pop()
        if gives_check:
            tags.append("check")

        # 2. Captures - always findable
        if board.is_capture(move):
            if self._is_sacrifice(board, move):
                tags.append("sacrifice")
            else:
                tags.append("capture")
            # Recaptures are especially findable
            if self._is_recapture(board, move):
                tags.append("recapture")

        # 3. Castling - obvious
        if board.is_castling(move):
            tags.append("castling")

        # 4. Pawn promotion
        if move.promotion:
            tags.append("promotion")

        # 5. Development moves (opening/early middlegame)
        if self._is_development_move(board, move):
            tags.append("development")

        # 6. Defends attacked piece
        if self._defends_attacked_piece(board, move):
            tags.append("defense")

        # 7. Creates direct threat (attacks undefended piece)
        if self._creates_threat(board, move):
            tags.append("threat")

        # 8. Central pawn moves (opening)
        if self._is_central_pawn_move(board, move):
            tags.append("central_pawn")

        # 9. Improves worst piece (simplified)
        if self._improves_piece(board, move):
            tags.append("improvement")

        return tags

    def _is_forcing(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move is forcing (check, capture, or major threat)."""
        board.push(move)
        gives_check = board.is_check()
        board.pop()

        return gives_check or board.is_capture(move)

    def _is_recapture(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if this is recapturing on a square where we just lost material."""
        if not board.is_capture(move):
            return False

        # Check if opponent just captured on this square
        if board.move_stack:
            last_move = board.peek()
            if last_move.to_square == move.to_square and board.is_capture(last_move):
                return True

        return False

    def _is_development_move(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move develops a piece from back rank."""
        piece = board.piece_at(move.from_square)
        if piece is None:
            return False

        # Only minor pieces and queens
        if piece.piece_type not in [chess.KNIGHT, chess.BISHOP, chess.QUEEN]:
            return False

        # From back rank
        from_rank = chess.square_rank(move.from_square)
        back_rank = 0 if piece.color == chess.WHITE else 7

        if from_rank != back_rank:
            return False

        # Knights: moving to good squares
        if piece.piece_type == chess.KNIGHT:
            return move.to_square in self.GOOD_KNIGHT_SQUARES

        # Bishops: moving to known good development squares
        if piece.piece_type == chess.BISHOP:
            return move.to_square in self.GOOD_BISHOP_SQUARES

        return False

    def _defends_attacked_piece(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move defends an attacked piece.

        Covers: moving the attacked piece to safety, capturing the attacker,
        interposing/blocking, or adding a new defender to the attacked square.
        """
        us = board.turn

        # Case 1: Moving an attacked piece to a safe square
        moved_piece = board.piece_at(move.from_square)
        if moved_piece is not None and moved_piece.color == us:
            attackers = board.attackers(not us, move.from_square)
            if attackers:
                # The piece we're moving is under attack - check if destination is safe
                board.push(move)
                new_attackers = board.attackers(not us, move.to_square)
                board.pop()
                if not new_attackers:
                    return True

        # Case 2: Capturing an attacker of one of our pieces
        if board.is_capture(move):
            # Check if the square we're capturing on has a piece that attacks one of ours
            target_sq = move.to_square
            target_piece = board.piece_at(target_sq)
            if target_piece and target_piece.color != us:
                # See what our pieces this target was attacking
                target_attacks = board.attacks(target_sq)
                for sq in target_attacks:
                    our_piece = board.piece_at(sq)
                    if our_piece and our_piece.color == us and our_piece.piece_type != chess.KING:
                        return True

        # Case 3: Interposing or adding a defender to an attacked friendly piece
        for sq in chess.SQUARES:
            our_piece = board.piece_at(sq)
            if our_piece is None or our_piece.color != us or our_piece.piece_type == chess.KING:
                continue
            if sq == move.from_square:
                continue

            enemy_attackers_before = board.attackers(not us, sq)
            if not enemy_attackers_before:
                continue

            defenders_before = board.attackers(us, sq)
            # Only care if piece is insufficiently defended (more attackers than defenders)
            if len(defenders_before) >= len(enemy_attackers_before):
                continue

            board.push(move)
            enemy_attackers_after = board.attackers(not us, sq)
            defenders_after = board.attackers(us, sq)
            board.pop()

            # Did we reduce attackers (interpose/block) or increase defenders?
            if len(enemy_attackers_after) < len(enemy_attackers_before):
                return True
            if len(defenders_after) > len(defenders_before):
                return True

        return False

    def _creates_threat(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move attacks an undefended or higher-value piece."""
        board.push(move)

        piece = board.piece_at(move.to_square)
        if piece is None:
            board.pop()
            return False

        # Check squares attacked by moved piece
        attacks = board.attacks(move.to_square)

        for sq in attacks:
            target = board.piece_at(sq)
            if target is None or target.color == piece.color:
                continue

            # Check if target is defended
            defenders = board.attackers(target.color, sq)

            # Undefended piece = threat
            if not defenders:
                board.pop()
                return True

            # Attacking higher value piece
            if self._piece_value(target) > self._piece_value(piece):
                board.pop()
                return True

        board.pop()
        return False

    def _is_central_pawn_move(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if this is a central or semi-central pawn move."""
        piece = board.piece_at(move.from_square)
        if piece is None or piece.piece_type != chess.PAWN:
            return False

        # Central squares (e4, d4, e5, d5) and semi-central (c4, c5, f4, f5)
        central_squares = {chess.E4, chess.D4, chess.E5, chess.D5,
                          chess.C4, chess.C5}  # c4/c5 are key opening moves
        return move.to_square in central_squares

    def _improves_piece(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if piece is moving to a more active square."""
        piece = board.piece_at(move.from_square)
        if piece is None:
            return False

        us = piece.color

        # Rooks to open files
        if piece.piece_type == chess.ROOK:
            to_file = chess.square_file(move.to_square)
            # Check if file is open (no pawns)
            for rank in range(8):
                sq = chess.square(to_file, rank)
                p = board.piece_at(sq)
                if p and p.piece_type == chess.PAWN:
                    return False
            return True

        # Knights to outpost squares (central squares where no enemy pawn can attack)
        if piece.piece_type == chess.KNIGHT:
            to_sq = move.to_square
            to_rank = chess.square_rank(to_sq)
            to_file = chess.square_file(to_sq)
            # Must be on ranks 4-6 for white (3-5 for black) and files c-f
            if 2 <= to_file <= 5:
                outpost_ranks = range(3, 6) if us == chess.WHITE else range(2, 5)
                if to_rank in outpost_ranks:
                    # Check no enemy pawn can attack this square
                    enemy = not us
                    # Enemy pawns would need to be on adjacent files, one rank behind
                    # (from the enemy's perspective, one rank forward for attack)
                    adj_files = [f for f in [to_file - 1, to_file + 1] if 0 <= f <= 7]
                    can_be_attacked = False
                    for f in adj_files:
                        # Check if an enemy pawn exists that could advance to attack
                        if us == chess.WHITE:
                            # Enemy (black) pawns attack from ranks above; check ranks above to_rank
                            for r in range(to_rank + 1, 7):
                                sq = chess.square(f, r)
                                p = board.piece_at(sq)
                                if p and p.piece_type == chess.PAWN and p.color == enemy:
                                    can_be_attacked = True
                                    break
                        else:
                            # Enemy (white) pawns attack from ranks below; check ranks below to_rank
                            for r in range(0, to_rank):
                                sq = chess.square(f, r)
                                p = board.piece_at(sq)
                                if p and p.piece_type == chess.PAWN and p.color == enemy:
                                    can_be_attacked = True
                                    break
                        if can_be_attacked:
                            break
                    if not can_be_attacked:
                        return True

        # Bishops to long diagonals or active central squares
        if piece.piece_type == chess.BISHOP:
            to_sq = move.to_square
            to_rank = chess.square_rank(to_sq)
            to_file = chess.square_file(to_sq)
            # Long diagonals: a1-h8 and h1-a8
            on_long_diagonal = (to_rank == to_file) or (to_rank + to_file == 7)
            # Active central squares (ranks 3-6, files c-f)
            on_active_square = (2 <= to_file <= 5) and (2 <= to_rank <= 5)
            if on_long_diagonal or on_active_square:
                return True

        # Queen centralizing in the middlegame (not too early)
        if piece.piece_type == chess.QUEEN:
            # Only consider this after some development (move 10+)
            total_moves = len(board.move_stack)
            if total_moves >= 18:  # ~move 10 for each side
                to_rank = chess.square_rank(move.to_square)
                to_file = chess.square_file(move.to_square)
                # Central squares (ranks 3-6, files c-f)
                if 2 <= to_file <= 5 and 2 <= to_rank <= 5:
                    return True

        return False

    def _is_sacrifice(self, board: chess.Board, move: chess.Move) -> bool:
        """Detect when a capture loses material - piece value of captured < capturer.

        This distinguishes tactical sacrifices from simple winning/equal captures.
        En passant captures are never sacrifices (pawn takes pawn).
        """
        if not board.is_capture(move):
            return False

        capturer = board.piece_at(move.from_square)
        if capturer is None:
            return False

        # En passant: pawn takes pawn, never a sacrifice
        if board.is_en_passant(move):
            return False

        captured = board.piece_at(move.to_square)
        if captured is None:
            return False

        capturer_val = self._piece_value(capturer)
        captured_val = self._piece_value(captured)

        # Sacrifice: we're giving up more material than we're taking
        return capturer_val > captured_val

    def _piece_value(self, piece: Optional[chess.Piece]) -> int:
        """Simple piece values for comparison."""
        if piece is None:
            return 0
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # Can't capture king
        }
        return values.get(piece.piece_type, 0)

    def is_findable(self, board: chess.Board, move_uci: str) -> tuple[bool, list[str]]:
        """
        Check if a specific move would be findable.
        Returns (is_findable, tags).
        """
        try:
            move = board.parse_uci(move_uci)
        except ValueError:
            move = board.parse_san(move_uci)

        tags = self._get_move_tags(board, move)
        return bool(tags), tags

    def filter_to_findable(self, board: chess.Board, moves_uci: list[str]) -> list[str]:
        """Filter a list of moves to only findable ones."""
        findable = []
        for move_uci in moves_uci:
            is_find, _ = self.is_findable(board, move_uci)
            if is_find:
                findable.append(move_uci)
        return findable
