"""
Core logic tests for ChessCoach analysis pipeline.

Tests eval consistency, move quality classification, findability scoring,
and the data that gets passed to the LLM for explanation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess
from engine.stockfish_engine import FastStockfish
from engine.candidates import CandidateFilter
from engine.findability import FindabilityCalculator
from explainer.facts import FactExtractor, MoveFacts


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_facts(facts: MoveFacts):
    """Print key facts in a readable format."""
    print(f"  Move: {facts.played_move_san} ({facts.played_move_uci})")
    print(f"  Quality: {facts.move_quality}")
    print(f"  Eval before: {facts.eval_before_cp/100:+.2f}")
    print(f"  Eval after:  {facts.eval_after_cp/100:+.2f}")
    print(f"  Best eval:   {facts.best_move_eval_cp/100:+.2f}")
    print(f"  CP loss: {facts.cp_loss}")
    print(f"  Best move: {facts.best_move_san}")
    print(f"  Findability: {facts.findability_score:.0%} ({facts.findability_label})")
    print(f"  Tags: {facts.played_move_tags}")
    print(f"  Tactical motifs: {facts.tactical_motifs}")
    if facts.top_lines:
        print(f"  Top engine lines:")
        for line in facts.top_lines[:3]:
            moves = " ".join(line["moves_san"])
            print(f"    [{line['eval']}] {moves}")


def test_eval_consistency():
    """
    TEST 1: Eval Consistency

    When you play the engine's best move, the eval_before and eval_after
    should be approximately equal. A big discrepancy indicates a bug.

    Position: After 1.e4 e5 2.Nf3 f6? (White to play)
    Best move: Nxe5 (engine says ~+2.0)

    BUG: eval_before is analyzed at depth 12, eval_after at depth 10.
    For tactical positions, different depths can give wildly different evals.
    If Nxe5 is the best move, we should NOT see a big eval jump.
    """
    print_header("TEST 1: Eval Consistency - Playing the best move")

    fen = "rnbqkbnr/pppp2pp/5p2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"

    engine = FastStockfish(num_lines=5)
    ext = FactExtractor(engine, player_rating=1200)

    # First, check what the engine thinks is the best move
    info = engine.analyze_instant(fen, depth=18)
    print(f"\n  Position: After 1.e4 e5 2.Nf3 f6? (White to play)")
    print(f"  Engine eval at d18: {info.eval_cp/100:+.2f}")
    print(f"  Best move: {info.lines[0].moves_san[0] if info.lines else 'N/A'}")
    print(f"  Top line: {' '.join(info.lines[0].moves_san[:8])}")

    # Extract facts for the best move (Nxe5)
    best_uci = info.lines[0].moves[0]
    facts = ext.extract_facts(fen, best_uci, move_number=3)

    print(f"\n  --- Playing the best move: {facts.played_move_san} ---")
    print_facts(facts)

    # Check for eval consistency bug
    eval_diff = abs(facts.eval_after_cp - facts.best_move_eval_cp)
    print(f"\n  EVAL CONSISTENCY CHECK:")
    print(f"    best_move_eval (from before analysis): {facts.best_move_eval_cp/100:+.2f}")
    print(f"    eval_after (from after analysis):      {facts.eval_after_cp/100:+.2f}")
    print(f"    Difference: {eval_diff} centipawns")

    if eval_diff > 50:
        print(f"    ❌ FAIL: Eval difference is {eval_diff}cp for BEST move!")
        print(f"       Before/after analysis depths disagree significantly.")
        print(f"       This makes cp_loss unreliable and confuses the user.")
    else:
        print(f"    ✓ OK: Evals are consistent (diff={eval_diff}cp)")

    return facts


def test_suboptimal_move_detection():
    """
    TEST 2: Suboptimal Move Detection

    After 1.e4 e5 2.Nf3, Black plays f6? (a known mistake).
    The system should classify this as a mistake/inaccuracy.
    """
    print_header("TEST 2: Suboptimal Move Detection - 2...f6?")

    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"

    engine = FastStockfish(num_lines=5)
    ext = FactExtractor(engine, player_rating=1200)

    facts = ext.extract_facts(fen, "f7f6", move_number=2)

    print(f"\n  Position: After 1.e4 e5 2.Nf3 (Black to play)")
    print_facts(facts)

    if facts.move_quality in ["mistake", "blunder"]:
        print(f"\n    ✓ OK: f6 correctly classified as {facts.move_quality}")
    else:
        print(f"\n    ❌ FAIL: f6 classified as {facts.move_quality}, expected mistake/blunder")

    return facts


def test_scholars_mate_blunder():
    """
    TEST 3: Scholar's Mate Blunder

    After 1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6?? (hangs f7 mate)
    This should be a clear blunder.
    """
    print_header("TEST 3: Scholar's Mate Blunder - 3...Nf6??")

    board = chess.Board()
    for move in ["e4", "e5", "Bc4", "Nc6", "Qh5"]:
        board.push_san(move)
    fen = board.fen()

    engine = FastStockfish(num_lines=5)
    ext = FactExtractor(engine, player_rating=1200)

    facts = ext.extract_facts(fen, "g8f6", move_number=3)

    print(f"\n  Position: After 1.e4 e5 2.Bc4 Nc6 3.Qh5 (Black to play)")
    print_facts(facts)

    if facts.move_quality == "blunder":
        print(f"\n    ✓ OK: Nf6?? correctly classified as blunder")
    else:
        print(f"\n    ❌ FAIL: Nf6?? classified as {facts.move_quality}, expected blunder")

    # Check that the system sees the mate threat
    print(f"\n  Mate threat after: {facts.mate_threat_after}")

    return facts


def test_good_opening_move():
    """
    TEST 4: Good Opening Move

    From starting position, 1.e4 should be "best" or "good".
    """
    print_header("TEST 4: Good Opening Move - 1.e4")

    fen = chess.STARTING_FEN

    engine = FastStockfish(num_lines=5)
    ext = FactExtractor(engine, player_rating=1200)

    facts = ext.extract_facts(fen, "e2e4", move_number=1)

    print(f"\n  Position: Starting position (White to play)")
    print_facts(facts)

    if facts.move_quality in ["best", "good"]:
        print(f"\n    ✓ OK: e4 classified as {facts.move_quality}")
    else:
        print(f"\n    ❌ FAIL: e4 classified as {facts.move_quality}")

    return facts


def test_findability_ratings():
    """
    TEST 5: Findability at Different Ratings

    Same move (Nxe5 capture in tactical position) should have
    different findability at different ratings.
    """
    print_header("TEST 5: Findability at Different Ratings")

    fen = "rnbqkbnr/pppp2pp/5p2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"

    engine = FastStockfish(num_lines=5)
    board = chess.Board(fen)
    move_uci = "f3e5"

    info = engine.analyze_instant(fen, depth=12)
    tactical_motifs = []
    if info.threats.pins: tactical_motifs.append("pin")
    if info.threats.forks: tactical_motifs.append("fork")

    cand = CandidateFilter("intermediate")
    is_findable, tags = cand.is_findable(board, move_uci)

    print(f"\n  Move: Nxe5 (capture)")
    print(f"  Tags: {tags}")
    print(f"  Tactical motifs in position: {tactical_motifs}")
    print(f"  Legal moves: {info.legal_moves_count}")

    for rating in [800, 1000, 1200, 1400, 1600, 1800, 2000]:
        calc = FindabilityCalculator(rating)
        score = calc.score_move(tags, tactical_motifs, info.legal_moves_count)
        label = calc.get_findability_label(score)
        print(f"    Rating {rating}: {score:.0%} ({label})")

    # Now test a quiet move
    print(f"\n  Move: d3 (quiet pawn push)")
    _, quiet_tags = cand.is_findable(board, "d2d3")
    print(f"  Tags: {quiet_tags}")

    for rating in [800, 1200, 1600, 2000]:
        calc = FindabilityCalculator(rating)
        score = calc.score_move(quiet_tags, [], info.legal_moves_count)
        label = calc.get_findability_label(score)
        print(f"    Rating {rating}: {score:.0%} ({label})")


def test_engine_line_data_for_llm():
    """
    TEST 6: Engine Line Data Quality

    The engine lines passed to the LLM should contain full PV continuations
    (multiple moves, not just the first move). This is critical because the
    LLM uses these lines to explain WHY a move is good/bad.

    Note: For Nxe5 in the f6 position, Stockfish prefers Nxe5 Qe7 (not fxe5).
    The Qh5+ trick only works if Black recaptures with fxe5, which is suboptimal.
    """
    print_header("TEST 6: Engine Line Data for LLM")

    fen = "rnbqkbnr/pppp2pp/5p2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"

    engine = FastStockfish(num_lines=5)
    ext = FactExtractor(engine, player_rating=1200)

    facts = ext.extract_facts(fen, "f3e5", move_number=3)

    print(f"\n  Top lines passed to LLM:")
    for i, line in enumerate(facts.top_lines):
        moves = " ".join(line["moves_san"])
        print(f"    Line {i+1} [{line['eval']}]: {moves}")

    # Check that lines have multiple moves (full PV, not just first move)
    top_line_moves = facts.top_lines[0]["moves_san"] if facts.top_lines else []
    if len(top_line_moves) >= 4:
        print(f"\n    ✓ OK: Top line has {len(top_line_moves)} moves (full PV)")
    else:
        print(f"\n    ❌ FAIL: Top line only has {len(top_line_moves)} moves (LLM needs full continuation)")

    # Check all lines have reasonable data
    all_ok = True
    for i, line in enumerate(facts.top_lines):
        if len(line["moves_san"]) < 2:
            print(f"    ❌ FAIL: Line {i+1} has < 2 moves")
            all_ok = False
        if line.get("eval") is None:
            print(f"    ❌ FAIL: Line {i+1} missing eval")
            all_ok = False
    if all_ok:
        print(f"    ✓ OK: All {len(facts.top_lines)} lines have moves and evals")

    # Also check what threats are detected
    print(f"\n  Threats before:")
    for key, val in facts.threats_before.items():
        if val:
            print(f"    {key}: {val}")
    print(f"\n  Threats after (post-Nxe5):")
    for key, val in facts.threats_after.items():
        if val:
            print(f"    {key}: {val}")


def test_perspective_handling():
    """
    TEST 7: Perspective Handling

    Evals should always be from WHITE's perspective.
    When Black makes a move, eval_before and eval_after should both
    be from White's perspective for consistent display.

    Note: Uses positions after several moves to avoid Stockfish 17 FEN bug
    that affects the specific position after 1.e4 when set via FEN.
    """
    print_header("TEST 7: Perspective Handling")

    engine = FastStockfish(num_lines=5)
    ext = FactExtractor(engine, player_rating=1200)

    # Black makes a neutral move: 1.e4 e5 2.Nf3 Nc6 (well-known good response)
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
    facts = ext.extract_facts(fen, "b8c6", move_number=2)

    print(f"\n  Black plays 2...Nc6 (good developing move)")
    print(f"  Eval before (from White's perspective): {facts.eval_before_cp/100:+.2f}")
    print(f"  Eval after (from White's perspective):  {facts.eval_after_cp/100:+.2f}")
    print(f"  Quality: {facts.move_quality}")

    # The evals should be similar (both slightly + for White)
    eval_diff = abs(facts.eval_after_cp - facts.eval_before_cp)
    if eval_diff < 50:
        print(f"  ✓ OK: Evals consistent, diff={eval_diff}cp")
    else:
        print(f"  ❌ ISSUE: Eval jump of {eval_diff}cp for a neutral move")

    # Verify evals are from White's perspective (positive = White advantage)
    if facts.eval_before_cp > -100 and facts.eval_before_cp < 200:
        print(f"  ✓ OK: Eval before is reasonable for equal position")
    else:
        print(f"  ❌ ISSUE: Eval before = {facts.eval_before_cp}cp, expected roughly equal")

    # Black makes a blunder: 1.e4 e5 2.Nf3 f6?
    fen2 = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
    facts2 = ext.extract_facts(fen2, "f7f6", move_number=2)

    print(f"\n  Black plays 2...f6? (mistake)")
    print(f"  Eval before: {facts2.eval_before_cp/100:+.2f}")
    print(f"  Eval after: {facts2.eval_after_cp/100:+.2f}")
    print(f"  CP loss: {facts2.cp_loss}")
    print(f"  Quality: {facts2.move_quality}")

    # After f6, White's advantage should INCREASE (eval should go UP for White)
    if facts2.eval_after_cp > facts2.eval_before_cp:
        print(f"  ✓ OK: White's advantage increased after Black's mistake")
    else:
        print(f"  ❌ ISSUE: White's advantage didn't increase after f6?")


def test_cp_loss_for_non_top_moves():
    """
    TEST 8: CP Loss for moves outside top engine lines

    If the player's move is NOT in the top 5 engine lines,
    the system must analyze the after position separately.
    The cp_loss should reflect the actual quality difference.
    """
    print_header("TEST 8: CP Loss for Non-Top Moves")

    # After 1.e4 e5 2.Nf3, Black plays h6? (waste of tempo, not in top lines)
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"

    engine = FastStockfish(num_lines=5)
    ext = FactExtractor(engine, player_rating=1200)

    facts = ext.extract_facts(fen, "h7h6", move_number=2)

    print(f"\n  Black plays 2...h6? (time waste)")
    print_facts(facts)

    if facts.move_quality in ["inaccuracy", "mistake"]:
        print(f"\n    ✓ OK: h6 classified as {facts.move_quality}")
    elif facts.move_quality == "good":
        print(f"\n    ⚠ WARN: h6 classified as 'good' (might be OK if loss is small)")
    else:
        print(f"\n    ❌ FAIL: h6 classified as {facts.move_quality}")


def test_capture_vs_sacrifice_findability():
    """
    TEST 9: Findability - Simple Capture vs Complex Sacrifice

    A simple recapture should be more findable than a positional sacrifice.
    The findability system should distinguish between:
    - Obvious captures (take back what was taken)
    - Tactical captures (sacrifice with hidden follow-up)
    """
    print_header("TEST 9: Capture vs Sacrifice Findability")

    board = chess.Board()
    cand = CandidateFilter("intermediate")

    # Simple recapture: after 1.e4 d5 2.exd5
    fen1 = "rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"
    board1 = chess.Board(fen1)
    _, recapture_tags = cand.is_findable(board1, "d8d5")  # Qxd5

    # Knight sacrifice: Nxe5 in f6 position
    fen2 = "rnbqkbnr/pppp2pp/5p2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"
    board2 = chess.Board(fen2)
    _, sacrifice_tags = cand.is_findable(board2, "f3e5")  # Nxe5

    print(f"\n  Recapture (Qxd5): tags={recapture_tags}")
    print(f"  Sacrifice (Nxe5): tags={sacrifice_tags}")

    calc = FindabilityCalculator(1200)
    score_recapture = calc.score_move(recapture_tags, [], 30)
    score_sacrifice = calc.score_move(sacrifice_tags, [], 30)

    print(f"\n  At rating 1200:")
    print(f"    Qxd5 (recapture): {score_recapture:.0%}")
    print(f"    Nxe5 (sacrifice): {score_sacrifice:.0%}")

    if score_recapture >= score_sacrifice:
        print(f"    ✓ OK: Recapture >= sacrifice in findability")
    else:
        print(f"    ⚠ NOTE: Sacrifice rated higher (both are 'captures' to the system)")

    print(f"\n  NOTE: The findability system treats ALL captures equally.")
    print(f"  Nxe5 gets 'capture' tag because it captures a pawn,")
    print(f"  even though its VALUE comes from the Qh5+ follow-up.")
    print(f"  This is a fundamental limitation - findability measures")
    print(f"  'would the player consider this move?' not 'would they")
    print(f"  see the full reason why it's good?'")


def test_played_move_in_engine_lines():
    """
    TEST 10: Does the played move appear in engine lines?

    When the player plays the best move, we should be able to find
    it in the engine lines and use its eval directly, instead of
    doing a separate (potentially inconsistent) analysis.
    """
    print_header("TEST 10: Played Move in Engine Lines")

    fen = "rnbqkbnr/pppp2pp/5p2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"

    engine = FastStockfish(num_lines=5)
    info = engine.analyze_instant(fen, depth=14)

    played_uci = "f3e5"  # Nxe5

    print(f"\n  Looking for {played_uci} in engine lines:")
    found = False
    for line in info.lines:
        first_move = line.moves[0] if line.moves else ""
        match = "←← MATCH" if first_move == played_uci else ""
        moves_str = " ".join(line.moves_san[:6])
        print(f"    [{line.eval_cp/100:+.2f}] {moves_str}  {match}")
        if first_move == played_uci:
            found = True
            print(f"    → Line eval: {line.eval_cp/100:+.2f}")

    if found:
        print(f"\n    ✓ Played move found in engine lines")
        print(f"    → Can use this eval directly instead of separate analysis")
    else:
        print(f"\n    ✗ Played move NOT in engine lines (need separate analysis)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  CHESSCOACH CORE LOGIC TEST SUITE")
    print("="*70)

    test_eval_consistency()
    test_suboptimal_move_detection()
    test_scholars_mate_blunder()
    test_good_opening_move()
    test_findability_ratings()
    test_engine_line_data_for_llm()
    test_perspective_handling()
    test_cp_loss_for_non_top_moves()
    test_capture_vs_sacrifice_findability()
    test_played_move_in_engine_lines()

    print("\n" + "="*70)
    print("  ALL TESTS COMPLETE")
    print("="*70 + "\n")
