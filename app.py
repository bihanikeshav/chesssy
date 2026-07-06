#!/usr/bin/env python3
"""
ChessCoach - Unified Web UI
Interactive chess analysis with move explanations, streaming LLM, and progressive analysis.
"""
import os
import json
import re
import chess
import chess.pgn
import io
import time
import threading
import requests
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit

from engine.stockfish_engine import FastStockfish, PositionInfo
from engine.candidates import CandidateFilter
from engine.findability import FindabilityCalculator
from explainer.facts import FactExtractor
from explainer.llm import LLMExplainer
from config import SKILL_LEVELS, DEFAULT_PLAYER_RATING

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-only-change-me')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
engine: FastStockfish = None
extractor: FactExtractor = None
explainer: LLMExplainer = None
candidate_filter: CandidateFilter = None
findability: FindabilityCalculator = None
rag = None  # ChessTheoryRAG, loaded lazily

current_skill_level = "intermediate"
current_player_rating = DEFAULT_PLAYER_RATING
current_analysis_fen = None
engine_lock = threading.Lock()
last_move_facts = None  # Cache facts from analyze_move for explain_stream


def get_engine() -> FastStockfish:
    """Lazy initialization of engine."""
    global engine
    if engine is None:
        engine = FastStockfish(num_lines=5)
    return engine


def get_components():
    """Lazy initialization of all components."""
    global engine, extractor, explainer, candidate_filter, findability
    if engine is None:
        engine = FastStockfish(num_lines=5)
    if extractor is None:
        extractor = FactExtractor(engine, current_skill_level, current_player_rating)
    if explainer is None:
        explainer = LLMExplainer(skill_level=current_skill_level)
    if candidate_filter is None:
        candidate_filter = CandidateFilter(current_skill_level)
    if findability is None:
        findability = FindabilityCalculator(current_player_rating)
    return engine, extractor, explainer, candidate_filter, findability


def get_rag():
    """Lazy initialization of RAG knowledge base."""
    global rag
    if rag is None:
        try:
            from knowledge.rag import ChessTheoryRAG
            rag = ChessTheoryRAG()
        except Exception as e:
            print(f"RAG unavailable: {e}")
    return rag


def position_to_dict(info: PositionInfo) -> dict:
    """Convert PositionInfo to JSON-serializable dict."""
    return {
        'fen': info.fen,
        'turn': info.turn,
        'move_number': info.move_number,
        'is_check': info.is_check,
        'is_checkmate': info.is_checkmate,
        'is_stalemate': info.is_stalemate,
        'is_draw': info.is_draw,
        'legal_moves_count': info.legal_moves_count,
        'eval': info.format_eval(),
        'eval_cp': info.eval_cp,
        'eval_mate': info.eval_mate,
        'depth': info.depth,
        'material_balance': info.material_balance,
        'lines': [
            {
                'rank': line.rank,
                'eval': line.format_eval(),
                'eval_cp': line.eval_cp,
                'eval_mate': line.eval_mate,
                'moves_san': line.moves_san,
                'moves_uci': line.moves,
                'depth': line.depth
            }
            for line in info.lines
        ],
        'threats': {
            'hanging_pieces': info.threats.hanging_pieces,
            'attacked_pieces': info.threats.attacked_pieces,
            'checks_available': info.threats.checks_available,
            'captures_available': info.threats.captures_available,
            'threats_to_king': info.threats.threats_to_king,
            'pins': info.threats.pins,
            'forks': info.threats.forks,
            'skewers': info.threats.skewers,
            'discovered_attacks': info.threats.discovered_attacks,
            'double_attacks': info.threats.double_attacks,
            'overloaded_pieces': info.threats.overloaded_pieces
        }
    }


# ----- Routes -----

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_position():
    """Position analysis — returns PositionInfo + threats as JSON."""
    data = request.json
    fen = data.get('fen', chess.STARTING_FEN)
    depth = data.get('depth', 12)

    try:
        eng = get_engine()
        with engine_lock:
            info = eng.analyze_instant(fen, depth)
        return jsonify(position_to_dict(info))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/analyze_move', methods=['POST'])
def analyze_move():
    """Move analysis Phase 1 — facts + quality + findability (fast)."""
    data = request.json
    fen = data.get('fen')
    move_uci = data.get('move')
    move_number = data.get('move_number', 1)
    player_rating = data.get('player_rating', current_player_rating)

    try:
        eng, ext, expl, cand, find = get_components()

        # Stop any running deep analysis to free the engine
        global current_analysis_fen
        current_analysis_fen = None
        eng.stop_analysis()

        # Update rating if provided
        ext.set_player_rating(player_rating)

        board = chess.Board(fen)
        try:
            chess_move = board.parse_uci(move_uci)
            move_san = board.san(chess_move)
        except Exception:
            return jsonify({'error': f'Invalid move: {move_uci}'}), 400

        # Extract facts (includes findability scoring)
        with engine_lock:
            facts = ext.extract_facts(fen, move_uci, move_number)

        # Cache facts for explain_stream
        global last_move_facts
        last_move_facts = facts

        # Make the move to get new position
        board.push(chess_move)
        new_fen = board.fen()

        return jsonify({
            'error': None,
            'move_san': move_san,
            'move_uci': move_uci,
            'new_fen': new_fen,
            'quality': facts.move_quality,
            'cp_loss': facts.cp_loss,
            'eval_before': facts.eval_before_cp,
            'eval_after': facts.eval_after_cp,
            'best_move_san': facts.best_move_san,
            'best_move_uci': facts.best_move_uci,
            'is_findable': facts.is_played_findable,
            'findability_tags': facts.played_move_tags,
            'findability_score': facts.findability_score,
            'findability_label': facts.findability_label,
            'best_findability_score': facts.best_findability_score,
            'threats_created': facts.threats_created,
            'threats_ignored': facts.threats_ignored,
            'tactical_motifs': facts.tactical_motifs,
            'material_balance': facts.material_balance,
            'position_type': facts.position_type,
            'is_tactical': facts.is_tactical,
            'is_check': facts.is_check,
            'mate_threat_before': facts.mate_threat_before,
            'mate_threat_after': facts.mate_threat_after,
            'top_lines': facts.top_lines,
            'game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None,
            # Rule-based explanation as immediate fallback
            'explanation_fallback': expl._generate_chess_explanation(facts),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/explain_stream')
def explain_stream():
    """SSE streaming of LLM explanation."""
    fen = request.args.get('fen')
    move = request.args.get('move')
    move_number = int(request.args.get('move_number', 1))
    player_rating = int(request.args.get('player_rating', current_player_rating))

    def generate():
        try:
            eng, ext, expl, cand, find = get_components()
            ext.set_player_rating(player_rating)

            # Use cached facts from analyze_move if available (avoids engine lock contention)
            global last_move_facts
            if last_move_facts and last_move_facts.played_move_uci == move:
                facts = last_move_facts
            else:
                with engine_lock:
                    facts = ext.extract_facts(fen, move, move_number)

            # Query RAG for context
            rag_passages = None
            rag_instance = get_rag()
            if rag_instance:
                try:
                    rag_passages = rag_instance.query(
                        fen=fen,
                        position_type=facts.position_type,
                        tags=facts.played_move_tags + facts.tactical_motifs,
                        k=3
                    )
                except Exception:
                    pass

            # Stream explanation
            for chunk in expl.explain_stream(facts, rag_passages):
                yield f"data: {json.dumps({'text': chunk})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route('/api/load_pgn', methods=['POST'])
def load_pgn():
    """Parse PGN, return moves."""
    data = request.json
    pgn_text = data.get('pgn', '')

    try:
        pgn_io = io.StringIO(pgn_text)
        game = chess.pgn.read_game(pgn_io)

        if game is None:
            return jsonify({'error': 'Could not parse PGN'}), 400

        headers = dict(game.headers)
        moves = []
        board = game.board()
        move_number = 1

        for move in game.mainline_moves():
            fen_before = board.fen()
            san = board.san(move)
            uci = move.uci()

            moves.append({
                'move_number': move_number,
                'side': 'white' if board.turn == chess.WHITE else 'black',
                'fen_before': fen_before,
                'move_san': san,
                'move_uci': uci
            })

            board.push(move)
            if board.turn == chess.WHITE:
                move_number += 1

        return jsonify({
            'error': None,
            'headers': headers,
            'moves': moves,
            'final_fen': board.fen(),
            'result': game.headers.get('Result', '*')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/set_config', methods=['POST'])
def set_config():
    """Set skill mode + player rating."""
    global current_skill_level, current_player_rating, extractor, explainer, candidate_filter, findability

    data = request.json
    level = data.get('skill_level', current_skill_level)
    rating = data.get('player_rating', current_player_rating)

    if level not in SKILL_LEVELS:
        return jsonify({'error': f'Invalid level. Choose from: {list(SKILL_LEVELS.keys())}'}), 400

    current_skill_level = level
    current_player_rating = max(800, min(2000, int(rating)))

    # Update components
    if extractor:
        extractor.skill_level = level
        extractor.candidate_filter = CandidateFilter(level)
        extractor.config = SKILL_LEVELS[level]
        extractor.set_player_rating(current_player_rating)
    if explainer:
        explainer.set_skill_level(level)
    if candidate_filter:
        candidate_filter = CandidateFilter(level)
    if findability:
        findability.set_rating(current_player_rating)

    return jsonify({'success': True, 'skill_level': level, 'player_rating': current_player_rating})


@app.route('/api/legal_moves', methods=['POST'])
def legal_moves():
    """Legal moves with annotations."""
    data = request.json
    fen = data.get('fen', chess.STARTING_FEN)

    try:
        board = chess.Board(fen)
        cand = CandidateFilter(current_skill_level)
        find = FindabilityCalculator(current_player_rating)

        moves = []
        for move in board.legal_moves:
            _, tags = cand.is_findable(board, move.uci())
            score = find.score_move(tags, num_legal_moves=board.legal_moves.count())
            moves.append({
                'uci': move.uci(),
                'san': board.san(move),
                'from': chess.square_name(move.from_square),
                'to': chess.square_name(move.to_square),
                'is_capture': board.is_capture(move),
                'is_check': board.gives_check(move),
                'tags': tags,
                'findability': score,
            })

        return jsonify({'moves': moves, 'count': len(moves)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ----- Game Import & Coach Report -----

@app.route('/api/import_game', methods=['POST'])
def import_game():
    """Import a game from a chess.com or lichess URL and return PGN + parsed moves."""
    data = request.json
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    pgn_text = None
    source_platform = None

    try:
        # --- Lichess ---
        # Matches: https://lichess.org/{gameId}  or  https://lichess.org/{gameId}/white
        lichess_match = re.match(
            r'https?://lichess\.org/([A-Za-z0-9]{8})(?:/(?:white|black))?(?:\?.*)?$', url
        )
        if lichess_match:
            game_id = lichess_match.group(1)
            source_platform = 'lichess'
            resp = requests.get(
                f'https://lichess.org/game/export/{game_id}',
                headers={'Accept': 'application/x-chess-pgn'},
                params={'pgnInJson': 'false', 'clocks': 'false', 'evals': 'false'},
                timeout=10,
            )
            if resp.status_code != 200:
                return jsonify({'error': f'Lichess returned status {resp.status_code}'}), 400
            pgn_text = resp.text

        # --- Chess.com ---
        # Matches: https://www.chess.com/game/live/{gameId}
        #          https://www.chess.com/game/daily/{gameId}
        #          https://www.chess.com/game/{gameId}
        if pgn_text is None:
            chesscom_match = re.match(
                r'https?://(?:www\.)?chess\.com/game/(?:live|daily)?/?(\d+)(?:\?.*)?$', url
            )
            if chesscom_match:
                game_id = chesscom_match.group(1)
                source_platform = 'chess.com'
                resp = requests.get(
                    f'https://www.chess.com/callback/live/game/{game_id}',
                    headers={
                        'User-Agent': 'ChessCoach/1.0',
                        'Accept': 'application/json',
                    },
                    timeout=10,
                )
                if resp.status_code != 200:
                    return jsonify({'error': f'Chess.com returned status {resp.status_code}'}), 400
                try:
                    game_data = resp.json()
                    pgn_text = game_data.get('pgn') or game_data.get('game', {}).get('pgn')
                    if not pgn_text:
                        return jsonify({'error': 'Could not extract PGN from Chess.com response'}), 400
                except (ValueError, KeyError) as exc:
                    return jsonify({'error': f'Failed to parse Chess.com response: {exc}'}), 400

        if pgn_text is None:
            return jsonify({
                'error': 'Unrecognized URL. Supported formats: '
                         'lichess.org/{gameId}, chess.com/game/live/{gameId}, '
                         'chess.com/game/daily/{gameId}'
            }), 400

        # Parse PGN using existing logic
        pgn_io = io.StringIO(pgn_text)
        game = chess.pgn.read_game(pgn_io)

        if game is None:
            return jsonify({'error': 'Could not parse PGN from imported game'}), 400

        headers = dict(game.headers)
        moves = []
        board = game.board()
        move_number = 1

        for move in game.mainline_moves():
            fen_before = board.fen()
            san = board.san(move)
            uci = move.uci()

            moves.append({
                'move_number': move_number,
                'side': 'white' if board.turn == chess.WHITE else 'black',
                'fen_before': fen_before,
                'move_san': san,
                'move_uci': uci
            })

            board.push(move)
            if board.turn == chess.WHITE:
                move_number += 1

        return jsonify({
            'error': None,
            'source_platform': source_platform,
            'source_url': url,
            'pgn': pgn_text,
            'headers': headers,
            'moves': moves,
            'final_fen': board.fen(),
            'result': game.headers.get('Result', '*')
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out while fetching game'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Could not connect to game server'}), 502
    except Exception as e:
        return jsonify({'error': f'Import failed: {str(e)}'}), 400


def _detect_move_pattern(board, move_uci):
    """Classify a move into pattern categories for strength/weakness tracking."""
    patterns = []
    try:
        move = board.parse_uci(move_uci)
    except Exception:
        return patterns

    piece = board.piece_at(move.from_square)

    if board.is_capture(move):
        patterns.append('capture')
    board.push(move)
    if board.is_check():
        patterns.append('check')
    board.pop()
    if board.is_castling(move):
        patterns.append('castling')
    if move.promotion:
        patterns.append('promotion')

    # Defense: moving a piece that is attacked
    if piece:
        attackers = board.attackers(not piece.color, move.from_square)
        if attackers:
            patterns.append('defense')

    # Development: minor piece from back rank
    if piece and piece.piece_type in (chess.KNIGHT, chess.BISHOP):
        from_rank = chess.square_rank(move.from_square)
        back_rank = 0 if piece.color == chess.WHITE else 7
        if from_rank == back_rank:
            patterns.append('development')

    if not patterns:
        patterns.append('quiet')

    return patterns


def _generate_strengths_weaknesses(pattern_stats):
    """Derive coaching strengths and weaknesses from pattern statistics."""
    strengths = []
    weaknesses = []

    for pattern, stats in pattern_stats.items():
        total = stats['total']
        found = stats['found']
        if total == 0:
            continue
        pct = found / total

        label_map = {
            'capture': ('tactical awareness (captures)', 'finding captures'),
            'check': ('finding checks', 'check awareness'),
            'defense': ('defensive awareness', 'defensive awareness'),
            'development': ('piece development', 'piece development'),
            'quiet': ('positional play', 'positional play'),
            'castling': ('king safety awareness', 'king safety'),
            'promotion': ('pawn promotion awareness', 'pawn promotion'),
        }
        strength_label, weakness_label = label_map.get(pattern, (pattern, pattern))

        if pct >= 0.9 and total >= 2:
            strengths.append(f"Good {strength_label} ({found}/{total} correct)")
        elif pct < 0.5 and total >= 2:
            weaknesses.append(f"Work on {weakness_label} ({total - found}/{total} missed)")
        elif pct < 0.7 and total >= 3:
            weaknesses.append(f"Inconsistent {weakness_label} ({total - found}/{total} missed)")

    return strengths, weaknesses


@app.route('/api/coach_report', methods=['POST'])
def coach_report():
    """Analyze all moves in a game and produce a coaching report."""
    data = request.json
    moves = data.get('moves', [])
    player_color = data.get('player_color', 'white')
    player_rating = data.get('player_rating', current_player_rating)

    if not moves:
        return jsonify({'error': 'No moves provided'}), 400

    try:
        eng, ext, expl, cand, find = get_components()

        # Stop any running analysis
        global current_analysis_fen
        current_analysis_fen = None
        eng.stop_analysis()

        # Update rating for this analysis session
        ext.set_player_rating(player_rating)

        # Tallies
        quality_counts = {'best': 0, 'good': 0, 'inaccuracy': 0, 'mistake': 0, 'blunder': 0}
        key_moments = []
        total_player_moves = 0
        total_cp_loss = 0

        # Pattern tracking: {pattern: {total: N, found: N}}
        pattern_stats = {}

        for move_data in moves:
            side = move_data.get('side', '')
            if side != player_color:
                continue

            fen_before = move_data.get('fen_before')
            move_uci = move_data.get('move_uci')
            move_number = move_data.get('move_number', 1)

            if not fen_before or not move_uci:
                continue

            total_player_moves += 1
            board = chess.Board(fen_before)

            # Detect patterns for this move
            move_patterns = _detect_move_pattern(board, move_uci)

            # Extract facts (engine analysis at depth 14)
            with engine_lock:
                facts = ext.extract_facts(fen_before, move_uci, move_number)

            quality = facts.move_quality
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            total_cp_loss += facts.cp_loss

            # Track pattern stats: did the player find the best/good move?
            move_was_good = quality in ('best', 'good')
            for pat in move_patterns:
                if pat not in pattern_stats:
                    pattern_stats[pat] = {'total': 0, 'found': 0}
                pattern_stats[pat]['total'] += 1
                if move_was_good:
                    pattern_stats[pat]['found'] += 1

            # Record key moments (only suboptimal moves)
            if quality in ('inaccuracy', 'mistake', 'blunder'):
                best_findable = facts.best_findability_score is not None and facts.best_findability_score >= 0.5
                suggestion = _build_coaching_suggestion(facts, best_findable)

                # Find a findable alternative if best move is not findable
                findable_alt = None
                if not best_findable:
                    findable_alt = _find_findable_alternative(
                        board, facts, cand, find
                    )

                try:
                    played_san = board.san(board.parse_uci(move_uci))
                except Exception:
                    played_san = move_uci

                key_moments.append({
                    'move_number': move_number,
                    'side': side,
                    'played_san': played_san,
                    'played_uci': move_uci,
                    'quality': quality,
                    'cp_loss': facts.cp_loss,
                    'best_move_san': facts.best_move_san,
                    'best_findable': best_findable,
                    'findability_score': facts.best_findability_score,
                    'suggestion': suggestion,
                    'findable_alternative': findable_alt,
                })

        # Accuracy: percentage of moves that are best or good
        accuracy = 0.0
        if total_player_moves > 0:
            accuracy = round(
                (quality_counts['best'] + quality_counts['good']) / total_player_moves * 100, 1
            )

        # Strengths and weaknesses
        strengths, weaknesses = _generate_strengths_weaknesses(pattern_stats)

        # Average centipawn loss
        avg_cp_loss = round(total_cp_loss / total_player_moves, 1) if total_player_moves > 0 else 0.0

        report = {
            'player_color': player_color,
            'total_moves': total_player_moves,
            'accuracy': accuracy,
            'avg_cp_loss': avg_cp_loss,
            'summary': quality_counts,
            'key_moments': key_moments,
            'strengths': strengths,
            'weaknesses': weaknesses,
        }

        return jsonify({'error': None, 'report': report})

    except Exception as e:
        return jsonify({'error': f'Coach report failed: {str(e)}'}), 400


def _build_coaching_suggestion(facts, best_findable):
    """Build a human-readable coaching suggestion for a suboptimal move."""
    quality = facts.move_quality
    played = facts.played_move_san
    best = facts.best_move_san
    cp_loss = facts.cp_loss

    # Severity prefix
    if quality == 'blunder':
        severity = 'Blunder!'
    elif quality == 'mistake':
        severity = 'Mistake.'
    else:
        severity = 'Inaccuracy.'

    if best_findable:
        # Best move was findable — player should have found it
        suggestion = f"{severity} You played {played} (lost ~{cp_loss}cp). " \
                     f"The best move was {best} — this was a natural move you could have found."
    else:
        # Best move was hard to find
        if facts.best_findable_move_san:
            alt = facts.best_findable_move_san
            suggestion = f"{severity} You played {played} (lost ~{cp_loss}cp). " \
                         f"The engine wants {best} (hard to find). " \
                         f"A more practical choice was {alt}."
        else:
            suggestion = f"{severity} You played {played} (lost ~{cp_loss}cp). " \
                         f"The best move was {best}, but this was a difficult position."

    return suggestion


def _find_findable_alternative(board, facts, cand, find):
    """
    Among the engine's top lines, find the move with the highest
    findability score that is >= 0.5 (excluding the played move).
    Returns a dict with the alternative, or None.
    """
    best_alt = None
    best_alt_score = -1.0

    for line in facts.top_lines:
        moves_san = line.get('moves_san', [])
        # top_lines store moves_uci under different keys; check what's available
        # In the facts dataclass, top_lines contain 'moves_san' as list
        if not moves_san:
            continue

        # The first move in each line
        first_san = moves_san[0]

        # We need the UCI to check findability
        try:
            chess_move = board.parse_san(first_san)
            first_uci = chess_move.uci()
        except Exception:
            continue

        # Skip if it's the same as the played move
        if first_uci == facts.played_move_uci:
            continue

        # Skip if it's the best move (we already know it's not findable)
        if first_uci == facts.best_move_uci:
            continue

        _, tags = cand.is_findable(board, first_uci)
        score = find.score_move(tags, facts.tactical_motifs,
                                board.legal_moves.count())

        if score >= 0.5 and score > best_alt_score:
            best_alt_score = score
            best_alt = {
                'move_san': first_san,
                'findability_score': score,
                'eval_cp': line.get('eval_cp'),
            }

    return best_alt


# ----- WebSocket: Progressive Analysis -----

@socketio.on('connect')
def handle_connect():
    print(f"[WS] Client connected: {request.sid}", flush=True)
    emit('connected', {'status': 'ok'})


@socketio.on('start_analysis')
def handle_start_analysis(data):
    """Analyze position — instant response, then deeper in background."""
    global current_analysis_fen

    fen = data.get('fen', chess.STARTING_FEN)
    current_analysis_fen = fen
    print(f"[WS] start_analysis from {request.sid}, fen={fen[:30]}...", flush=True)

    try:
        eng = get_engine()
        eng.stop_analysis()

        # Quick analysis (depth 8)
        with engine_lock:
            quick = eng.analyze_instant(fen, 8)
        if current_analysis_fen == fen:
            emit('analysis_update', position_to_dict(quick))
            socketio.start_background_task(run_deep_analysis, fen)
    except Exception as e:
        print(f"[WS] Analysis error: {e}", flush=True)
        emit('analysis_error', {'error': str(e)})


def run_deep_analysis(fen):
    """Background task for deeper analysis."""
    global current_analysis_fen

    try:
        socketio.sleep(0.3)
        if current_analysis_fen != fen:
            return

        eng = get_engine()
        for depth in [14, 18, 22]:
            if current_analysis_fen != fen:
                return
            with engine_lock:
                if current_analysis_fen != fen:
                    return
                result = eng.analyze_instant(fen, depth)
            if current_analysis_fen != fen:
                return
            socketio.emit('analysis_update', position_to_dict(result))
    except Exception as e:
        print(f"Deep analysis error: {e}")


@socketio.on('stop_analysis')
def handle_stop_analysis():
    eng = get_engine()
    eng.stop_analysis()


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5050
    print("Starting ChessCoach...")
    print(f"Open http://localhost:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
