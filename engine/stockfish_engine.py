"""
Fast Stockfish engine wrapper with progressive deepening and comprehensive analysis.
"""
import chess
from stockfish import Stockfish
from dataclasses import dataclass, field
from typing import Optional
import threading
import time

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from config import STOCKFISH_PATH, STOCKFISH_THREADS, STOCKFISH_HASH_MB


@dataclass
class EngineLine:
    """A single engine line (principal variation)."""
    moves: list[str]  # UCI moves
    moves_san: list[str]  # SAN moves with proper notation
    eval_cp: int
    eval_mate: Optional[int]
    depth: int
    rank: int  # 1 = best line

    def format_eval(self) -> str:
        """Format evaluation for display."""
        if self.eval_mate is not None:
            sign = "+" if self.eval_mate > 0 else "-"
            return f"{sign}M{abs(self.eval_mate)}"
        pawns = self.eval_cp / 100
        return f"{pawns:+.2f}"


@dataclass
class TacticalMotif:
    """A tactical pattern in the position."""
    type: str  # "pin", "fork", "skewer", "discovered_attack", "double_attack"
    description: str
    squares: list[str]  # Squares involved


@dataclass
class ThreatInfo:
    """Information about threats in the position."""
    hanging_pieces: list[str]  # e.g., ["Knight on f3", "Pawn on e4"]
    attacked_pieces: list[str]  # Pieces under attack
    checks_available: list[str]  # Moves that give check
    captures_available: list[str]  # Capture moves
    threats_to_king: bool  # Is the king in danger
    # New tactical patterns
    pins: list[str]  # Pinned pieces
    forks: list[str]  # Fork opportunities
    skewers: list[str]  # Skewer opportunities
    discovered_attacks: list[str]  # Discovered attack opportunities
    double_attacks: list[str]  # Double attack opportunities
    defending_pieces: list[str]  # Pieces that are defending others
    overloaded_pieces: list[str]  # Pieces defending multiple things


@dataclass
class PositionInfo:
    """Comprehensive position information."""
    fen: str
    turn: str  # "white" or "black"
    move_number: int
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    is_draw: bool
    legal_moves_count: int

    # Evaluation
    eval_cp: int
    eval_mate: Optional[int]
    depth: int

    # Top lines
    lines: list[EngineLine]

    # Threats
    threats: ThreatInfo

    # Material
    material_balance: int  # Positive = white ahead

    def format_eval(self) -> str:
        if self.eval_mate is not None:
            sign = "+" if self.eval_mate > 0 else "-"
            return f"{sign}M{abs(self.eval_mate)}"
        pawns = self.eval_cp / 100
        return f"{pawns:+.2f}"


class FastStockfish:
    """
    Fast Stockfish wrapper with progressive deepening.

    Usage:
        engine = FastStockfish()

        # Instant analysis (depth 6)
        info = engine.analyze_instant(fen)

        # Start background deep analysis
        engine.analyze_progressive(fen, callback=on_update, max_depth=20)
    """

    PIECE_VALUES = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    def __init__(self, num_lines: int = 3):
        self.path = str(STOCKFISH_PATH)
        self.num_lines = num_lines
        self._engine = None
        self._analysis_thread = None
        self._stop_analysis = False
        self._current_fen = None  # Track current position being analyzed
        self._lock = threading.Lock()

    def _get_engine(self) -> Stockfish:
        if self._engine is None:
            self._engine = Stockfish(
                path=self.path,
                depth=6,  # Start shallow
                parameters={
                    "Threads": STOCKFISH_THREADS,
                    "Hash": STOCKFISH_HASH_MB,
                    "MultiPV": self.num_lines
                }
            )
        return self._engine

    def analyze_instant(self, fen: str, depth: int = 6) -> PositionInfo:
        """
        Instant analysis at low depth.
        Returns within ~50-100ms.
        """
        return self._analyze_at_depth(fen, depth)

    def analyze_progressive(self, fen: str, callback, max_depth: int = 20,
                           start_depth: int = 8, step: int = 4):
        """
        Progressive deepening analysis.
        Calls callback(PositionInfo) at each depth level.
        Runs in background thread.
        """
        with self._lock:
            # Stop any existing analysis
            self._stop_analysis = True
            self._current_fen = fen

        # Wait briefly for previous thread to notice stop flag
        if self._analysis_thread and self._analysis_thread.is_alive():
            self._analysis_thread.join(timeout=0.5)

        with self._lock:
            self._stop_analysis = False
            analysis_fen = self._current_fen  # Capture the FEN we're analyzing

        def run_progressive():
            for depth in range(start_depth, max_depth + 1, step):
                # Check if we should stop or if position changed
                with self._lock:
                    if self._stop_analysis or self._current_fen != analysis_fen:
                        return
                try:
                    info = self._analyze_at_depth(analysis_fen, depth)
                    # Double-check position hasn't changed before sending
                    with self._lock:
                        if self._stop_analysis or self._current_fen != analysis_fen:
                            return
                        callback(info)
                except Exception as e:
                    print(f"Analysis error at depth {depth}: {e}")
                    return

        self._analysis_thread = threading.Thread(target=run_progressive, daemon=True)
        self._analysis_thread.start()

    def stop_analysis(self):
        """Stop any running background analysis."""
        self._stop_analysis = True

    def _analyze_at_depth(self, fen: str, depth: int) -> PositionInfo:
        """Analyze position at specific depth using raw UCI output for full PVs."""
        engine = self._get_engine()
        engine.set_fen_position(fen)

        board = chess.Board(fen)
        is_white = board.turn == chess.WHITE

        # Parse raw UCI output for full principal variations
        lines = self._parse_raw_analysis(engine, board, depth, is_white)

        # Position eval comes from the best line (NOT get_evaluation which is
        # unreliable in multi-PV mode — it may return the eval of any PV, not PV1)
        if lines:
            main_eval_cp = lines[0].eval_cp
            main_eval_mate = lines[0].eval_mate
        else:
            main_eval_cp = 0
            main_eval_mate = None

        # Get threats
        threats = self._analyze_threats(board)

        # Get material balance
        material = self._calculate_material(board)

        return PositionInfo(
            fen=fen,
            turn="white" if is_white else "black",
            move_number=board.fullmove_number,
            is_check=board.is_check(),
            is_checkmate=board.is_checkmate(),
            is_stalemate=board.is_stalemate(),
            is_draw=board.is_insufficient_material() or board.can_claim_draw(),
            legal_moves_count=len(list(board.legal_moves)),
            eval_cp=main_eval_cp,
            eval_mate=main_eval_mate,
            depth=depth,
            lines=lines,
            threats=threats,
            material_balance=material
        )

    def _parse_raw_analysis(self, engine, board: chess.Board, depth: int,
                            is_white: bool) -> list:
        """Parse raw UCI output to get full PVs and consistent evals.

        All evals are normalized to WHITE's perspective (positive = White ahead).
        """
        engine._put(f"go depth {depth}")

        # Collect all UCI info lines
        raw_lines = []
        while True:
            line = engine._read_line()
            if line.startswith("bestmove"):
                break
            raw_lines.append(line)

        # Parse the highest-depth info line for each multipv
        pv_data = {}  # multipv_num -> parsed data
        for line in raw_lines:
            if not line.startswith("info") or " pv " not in line:
                continue
            parsed = self._parse_uci_info(line)
            if parsed and parsed.get("depth", 0) >= depth - 2:
                mpv = parsed.get("multipv", 1)
                # Keep the deepest line for each multipv
                if mpv not in pv_data or parsed["depth"] > pv_data[mpv]["depth"]:
                    pv_data[mpv] = parsed

        # Build EngineLine objects, sorted by multipv rank
        lines = []
        for rank in sorted(pv_data.keys()):
            data = pv_data[rank]
            pv_uci = data.get("pv", [])
            if not pv_uci:
                continue

            pv_san = self._format_line(board, pv_uci)

            # Normalize eval to White's perspective
            eval_cp = data.get("cp", 0)
            eval_mate = data.get("mate")

            if not is_white:
                eval_cp = -eval_cp
                if eval_mate is not None:
                    eval_mate = -eval_mate

            if eval_mate is not None:
                eval_cp = 10000 - abs(eval_mate) * 10 if eval_mate > 0 else -10000 + abs(eval_mate) * 10

            lines.append(EngineLine(
                moves=pv_uci,
                moves_san=pv_san,
                eval_cp=eval_cp,
                eval_mate=eval_mate,
                depth=data.get("depth", depth),
                rank=len(lines) + 1
            ))

        return lines

    @staticmethod
    def _parse_uci_info(line: str) -> dict:
        """Parse a UCI info line into a dict.

        Example: 'info depth 14 multipv 1 score cp 181 ... pv d2d4 d7d5 e4d5'
        """
        result = {}
        tokens = line.split()
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == "depth" and i + 1 < len(tokens):
                result["depth"] = int(tokens[i + 1])
                i += 2
            elif token == "multipv" and i + 1 < len(tokens):
                result["multipv"] = int(tokens[i + 1])
                i += 2
            elif token == "score" and i + 2 < len(tokens):
                if tokens[i + 1] == "cp":
                    result["cp"] = int(tokens[i + 2])
                    i += 3
                elif tokens[i + 1] == "mate":
                    result["mate"] = int(tokens[i + 2])
                    i += 3
                else:
                    i += 1
            elif token == "pv":
                result["pv"] = tokens[i + 1:]
                break
            else:
                i += 1
        return result

    def _format_line(self, board: chess.Board, uci_moves: list[str]) -> list[str]:
        """
        Format a line of moves with proper chess notation.
        e.g., "1. e4 e5 2. Nf3" or "6... Nxd5 7. c4"
        """
        result = []
        temp_board = board.copy()

        for i, uci in enumerate(uci_moves):
            try:
                move = temp_board.parse_uci(uci)
                san = temp_board.san(move)

                move_num = temp_board.fullmove_number
                is_white = temp_board.turn == chess.WHITE

                if is_white:
                    result.append(f"{move_num}. {san}")
                else:
                    # For first move of a line by black, use "6... Nxd5" notation
                    if i == 0:
                        result.append(f"{move_num}... {san}")
                    else:
                        result.append(san)

                temp_board.push(move)
            except Exception:
                result.append(uci)  # Fallback to UCI

        return result

    def _analyze_threats(self, board: chess.Board) -> ThreatInfo:
        """Analyze threats and tactical patterns in the position."""
        hanging = []
        attacked = []
        checks = []
        captures = []
        pins = []
        forks = []
        skewers = []
        discovered_attacks = []
        double_attacks = []
        defending_pieces = []
        overloaded_pieces = []

        us = board.turn
        them = not us

        # Track what each piece defends
        defense_count = {}

        # Find hanging pieces and attacked pieces
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == us:
                attackers = board.attackers(them, sq)
                defenders = board.attackers(us, sq)

                # Track defenders
                for def_sq in defenders:
                    if def_sq not in defense_count:
                        defense_count[def_sq] = []
                    defense_count[def_sq].append(sq)

                if attackers:
                    piece_name = chess.piece_name(piece.piece_type).capitalize()
                    sq_name = chess.square_name(sq)

                    if not defenders:
                        hanging.append(f"{piece_name} on {sq_name} (undefended)")
                    else:
                        attacked.append(f"{piece_name} on {sq_name}")

        # Find overloaded pieces (defending 2+ pieces)
        for def_sq, defended_sqs in defense_count.items():
            if len(defended_sqs) >= 2:
                defender = board.piece_at(def_sq)
                if defender:
                    defender_name = chess.piece_name(defender.piece_type).capitalize()
                    defended_names = []
                    for sq in defended_sqs[:3]:
                        p = board.piece_at(sq)
                        if p:
                            defended_names.append(chess.square_name(sq))
                    overloaded_pieces.append(f"{defender_name} on {chess.square_name(def_sq)} defends {', '.join(defended_names)}")

        # Find pins we create against opponent
        pins = self._find_pins(board, us)

        # Find our pieces that are pinned
        our_pinned = self._find_our_pinned_pieces(board, us)

        # Find checks, captures, and tactical opportunities
        for move in board.legal_moves:
            san = board.san(move)

            # Check if capture
            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    cap_name = chess.piece_name(captured.piece_type).capitalize()
                    captures.append(f"{san} wins {cap_name}")

            # Make move temporarily
            board.push(move)

            # Check if gives check
            if board.is_check():
                checks.append(san)

            # Check for forks after this move
            fork = self._check_fork(board, move.to_square, us)
            if fork:
                forks.append(f"{san} forks {fork}")

            # Check for discovered attacks
            disc = self._check_discovered_attack(board, move, us)
            if disc:
                discovered_attacks.append(f"{san} discovers attack on {disc}")

            # Check for double attacks (attack + check, or attack two pieces)
            double = self._check_double_attack(board, move, us)
            if double:
                double_attacks.append(f"{san}: {double}")

            board.pop()

        # Find skewer opportunities
        skewers = self._find_skewers(board, us)

        # Is their king in danger?
        king_danger = len(checks) > 0 or board.is_check()

        return ThreatInfo(
            hanging_pieces=hanging[:5],
            attacked_pieces=attacked[:5],
            checks_available=checks[:8],
            captures_available=captures[:5],
            threats_to_king=king_danger,
            pins=pins[:5] + our_pinned[:3],  # Both pins we create and pins against us
            forks=forks[:5],
            skewers=skewers[:3],
            discovered_attacks=discovered_attacks[:3],
            double_attacks=double_attacks[:3],
            defending_pieces=defending_pieces[:5],
            overloaded_pieces=overloaded_pieces[:3]
        )

    def _find_pins(self, board: chess.Board, us: bool) -> list[str]:
        """Find pins we create against opponent."""
        pins = []
        them = not us
        their_king_sq = board.king(them)

        if their_king_sq is None:
            return pins

        # Check all our sliding pieces for pins
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == us and piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                # Check if there's a pin along this piece's attack line to enemy king
                pin_info = self._check_pin_from(board, sq, their_king_sq, them)
                if pin_info:
                    pins.append(pin_info)

        return pins

    def _find_our_pinned_pieces(self, board: chess.Board, us: bool) -> list[str]:
        """Find our pieces that are pinned to our king."""
        pins = []
        them = not us
        our_king_sq = board.king(us)

        if our_king_sq is None:
            return pins

        # Check all enemy sliding pieces for pins against our king
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == them and piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                pin_info = self._check_pin_from(board, sq, our_king_sq, us)
                if pin_info:
                    # Reformat to show it's our piece that's pinned
                    pins.append(pin_info.replace("pinned by", "(pinned by enemy"))
                    if not pins[-1].endswith(")"):
                        pins[-1] += ")"

        return pins

    def _check_pin_from(self, board: chess.Board, attacker_sq: int, king_sq: int, pinned_color: bool) -> str:
        """Check if attacker pins a piece to the king."""
        attacker = board.piece_at(attacker_sq)
        if not attacker:
            return None

        # Get direction from attacker to king
        attacker_file, attacker_rank = chess.square_file(attacker_sq), chess.square_rank(attacker_sq)
        king_file, king_rank = chess.square_file(king_sq), chess.square_rank(king_sq)

        file_diff = king_file - attacker_file
        rank_diff = king_rank - attacker_rank

        # Must be on same line (diagonal for bishop/queen, straight for rook/queen)
        is_diagonal = abs(file_diff) == abs(rank_diff) and file_diff != 0
        is_straight = (file_diff == 0 or rank_diff == 0) and (file_diff != 0 or rank_diff != 0)

        if attacker.piece_type == chess.BISHOP and not is_diagonal:
            return None
        if attacker.piece_type == chess.ROOK and not is_straight:
            return None
        if attacker.piece_type == chess.QUEEN and not (is_diagonal or is_straight):
            return None

        # Normalize direction
        step_file = 0 if file_diff == 0 else (1 if file_diff > 0 else -1)
        step_rank = 0 if rank_diff == 0 else (1 if rank_diff > 0 else -1)

        # Walk from attacker toward king, find pieces in between
        pieces_between = []
        current_file, current_rank = attacker_file + step_file, attacker_rank + step_rank

        while (current_file, current_rank) != (king_file, king_rank):
            if not (0 <= current_file <= 7 and 0 <= current_rank <= 7):
                break
            sq = chess.square(current_file, current_rank)
            piece = board.piece_at(sq)
            if piece:
                pieces_between.append((sq, piece))
            current_file += step_file
            current_rank += step_rank

        # Pin exists if exactly one enemy piece between attacker and king
        if len(pieces_between) == 1:
            pinned_sq, pinned_piece = pieces_between[0]
            if pinned_piece.color == pinned_color:
                attacker_name = chess.piece_name(attacker.piece_type).capitalize()
                pinned_name = chess.piece_name(pinned_piece.piece_type).capitalize()
                return f"{pinned_name} on {chess.square_name(pinned_sq)} pinned by {attacker_name}"

        return None

    def _check_fork(self, board: chess.Board, sq: int, us: bool) -> str:
        """Check if piece on sq is forking valuable pieces."""
        piece = board.piece_at(sq)
        if not piece or piece.color != us:
            return None

        them = not us
        attacked_valuable = []

        # Get all squares this piece attacks
        attacks = board.attacks(sq)

        for target_sq in attacks:
            target = board.piece_at(target_sq)
            if target and target.color == them:
                # Consider valuable targets (not pawns, unless it's the king)
                if target.piece_type >= chess.KNIGHT or target.piece_type == chess.KING:
                    attacked_valuable.append((target_sq, target))

        if len(attacked_valuable) >= 2:
            names = [chess.piece_name(p.piece_type).capitalize() for _, p in attacked_valuable[:3]]
            return " and ".join(names)

        return None

    def _check_discovered_attack(self, board: chess.Board, move: chess.Move, us: bool) -> str:
        """Check if move creates a discovered attack."""
        # After the move, check if any of our sliding pieces now attack enemy pieces
        # that they couldn't attack before because the moved piece was blocking

        # This is a simplified check - look for newly attacked valuable pieces
        from_sq = move.from_square

        # Check if moving piece was blocking any of our sliding pieces
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == us and piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                if sq == move.to_square:
                    continue
                # Check if this piece now attacks something valuable through where the piece was
                attacks = board.attacks(sq)
                for target_sq in attacks:
                    target = board.piece_at(target_sq)
                    if target and target.color != us and target.piece_type >= chess.ROOK:
                        # Check if from_sq is between sq and target_sq
                        if self._is_between(sq, from_sq, target_sq):
                            return chess.piece_name(target.piece_type).capitalize()

        return None

    def _is_between(self, a: int, b: int, c: int) -> bool:
        """Check if b is on the line between a and c."""
        af, ar = chess.square_file(a), chess.square_rank(a)
        bf, br = chess.square_file(b), chess.square_rank(b)
        cf, cr = chess.square_file(c), chess.square_rank(c)

        # Check if collinear
        cross = (bf - af) * (cr - ar) - (br - ar) * (cf - af)
        if cross != 0:
            return False

        # Check if b is between a and c
        return min(af, cf) <= bf <= max(af, cf) and min(ar, cr) <= br <= max(ar, cr)

    def _check_double_attack(self, board: chess.Board, move: chess.Move, us: bool) -> str:
        """Check for double attacks (check + attack, or attacking two pieces)."""
        # If it's check, see what else is attacked
        if board.is_check():
            to_sq = move.to_square
            piece = board.piece_at(to_sq)
            if piece:
                attacks = board.attacks(to_sq)
                for target_sq in attacks:
                    target = board.piece_at(target_sq)
                    if target and target.color != us and target.piece_type >= chess.KNIGHT:
                        if target.piece_type != chess.KING:
                            return f"Check + attacks {chess.piece_name(target.piece_type).capitalize()}"
        return None

    def _find_skewers(self, board: chess.Board, us: bool) -> list[str]:
        """Find skewer opportunities."""
        skewers = []
        them = not us

        # Look for enemy pieces in line with more valuable pieces behind them
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == us and piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                # Check along attack lines
                skewer = self._check_skewer_from(board, sq, them)
                if skewer:
                    skewers.append(skewer)

        return skewers

    def _check_skewer_from(self, board: chess.Board, attacker_sq: int, them: bool) -> str:
        """Check for skewer from attacker position."""
        attacker = board.piece_at(attacker_sq)
        if not attacker:
            return None

        attacks = board.attacks(attacker_sq)

        for first_sq in attacks:
            first_piece = board.piece_at(first_sq)
            if not first_piece or first_piece.color != them:
                continue
            if first_piece.piece_type < chess.KNIGHT:
                continue

            # Check if there's a less valuable piece behind
            direction = self._get_direction(attacker_sq, first_sq)
            if not direction:
                continue

            current = first_sq
            while True:
                next_file = chess.square_file(current) + direction[0]
                next_rank = chess.square_rank(current) + direction[1]
                if not (0 <= next_file <= 7 and 0 <= next_rank <= 7):
                    break
                next_sq = chess.square(next_file, next_rank)
                next_piece = board.piece_at(next_sq)
                if next_piece:
                    if next_piece.color == them:
                        # Found piece behind - check if it's a valid skewer
                        # Skewer: attacking valuable piece with less valuable piece behind
                        if first_piece.piece_type > next_piece.piece_type:
                            first_name = chess.piece_name(first_piece.piece_type).capitalize()
                            second_name = chess.piece_name(next_piece.piece_type).capitalize()
                            return f"{first_name} to {second_name}"
                    break
                current = next_sq

        return None

    def _get_direction(self, from_sq: int, to_sq: int) -> tuple:
        """Get direction vector from one square to another."""
        from_file, from_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
        to_file, to_rank = chess.square_file(to_sq), chess.square_rank(to_sq)

        file_diff = to_file - from_file
        rank_diff = to_rank - from_rank

        if file_diff == 0 and rank_diff == 0:
            return None

        step_file = 0 if file_diff == 0 else (1 if file_diff > 0 else -1)
        step_rank = 0 if rank_diff == 0 else (1 if rank_diff > 0 else -1)

        return (step_file, step_rank)

    def _calculate_material(self, board: chess.Board) -> int:
        """Calculate material balance (positive = white ahead)."""
        balance = 0
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece:
                value = self.PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    balance += value
                else:
                    balance -= value
        return balance

    def get_best_move(self, fen: str, depth: int = 10) -> str:
        """Get just the best move."""
        engine = self._get_engine()
        engine.set_depth(depth)
        engine.set_fen_position(fen)
        return engine.get_best_move()

    def close(self):
        """Clean up."""
        self.stop_analysis()
        if self._engine:
            del self._engine
            self._engine = None
