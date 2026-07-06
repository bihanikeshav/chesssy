#!/usr/bin/env python3
"""
ChessCoach - Move Explanation Engine

Explains chess moves in human-learnable terms by combining
Stockfish analysis with LLM explanation generation.
"""
import argparse
import sys
import chess
import chess.pgn
import io

from engine.analyzer import StockfishAnalyzer
from engine.candidates import CandidateFilter
from explainer.facts import FactExtractor
from explainer.llm import LLMExplainer
from config import SKILL_LEVELS


def analyze_move(fen: str, move: str, skill_level: str = "intermediate", verbose: bool = False) -> dict:
    """
    Analyze a single move and return explanation.

    Args:
        fen: Position FEN string
        move: Move in UCI or SAN format
        skill_level: "beginner", "intermediate", or "advanced"
        verbose: Include detailed facts in output

    Returns:
        Dictionary with explanation and metadata
    """
    # Initialize components
    analyzer = StockfishAnalyzer()
    extractor = FactExtractor(analyzer, skill_level)
    explainer = LLMExplainer(skill_level=skill_level)

    try:
        # Extract facts
        facts = extractor.extract_facts(fen, move)

        # Generate explanation
        result = explainer.explain_with_alternative(facts)

        output = {
            "move": facts.played_move_san,
            "quality": facts.move_quality,
            "explanation": result["explanation"],
            "recommendation": result["recommendation"],
            "findability": result["difficulty"],
            "cp_loss": facts.cp_loss,
            "eval_before": facts.eval_before_cp / 100,
            "eval_after": facts.eval_after_cp / 100,
        }

        if verbose:
            output["facts"] = facts.to_dict()

        return output

    finally:
        analyzer.close()


def analyze_pgn(pgn_string: str, skill_level: str = "intermediate", annotate_all: bool = False) -> list[dict]:
    """
    Analyze all moves in a PGN game.

    Args:
        pgn_string: PGN formatted game string
        skill_level: Skill level for explanations
        annotate_all: If True, explain all moves. If False, only explain mistakes.

    Returns:
        List of move analyses
    """
    pgn_io = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_io)

    if game is None:
        raise ValueError("Could not parse PGN")

    analyzer = StockfishAnalyzer()
    extractor = FactExtractor(analyzer, skill_level)
    explainer = LLMExplainer(skill_level=skill_level)

    results = []
    board = game.board()
    move_number = 1

    try:
        for move in game.mainline_moves():
            fen = board.fen()
            san = board.san(move)

            # Extract facts
            facts = extractor.extract_facts(fen, move.uci(), move_number)

            # Decide whether to include explanation
            should_explain = annotate_all or facts.move_quality in ["inaccuracy", "mistake", "blunder"]

            if should_explain:
                result = explainer.explain_with_alternative(facts)
                results.append({
                    "move_number": move_number,
                    "side": "White" if board.turn == chess.WHITE else "Black",
                    "move": san,
                    "quality": facts.move_quality,
                    "explanation": result["explanation"],
                    "recommendation": result["recommendation"],
                    "cp_loss": facts.cp_loss,
                })
            else:
                results.append({
                    "move_number": move_number,
                    "side": "White" if board.turn == chess.WHITE else "Black",
                    "move": san,
                    "quality": facts.move_quality,
                    "explanation": None,
                    "recommendation": None,
                    "cp_loss": facts.cp_loss,
                })

            # Update for next move
            board.push(move)
            if board.turn == chess.WHITE:
                move_number += 1

    finally:
        analyzer.close()

    return results


def interactive_mode(skill_level: str = "intermediate"):
    """Run interactive analysis session."""
    print("\n=== ChessCoach Interactive Mode ===")
    print(f"Skill level: {skill_level}")
    print("Commands:")
    print("  fen <FEN>     - Set position")
    print("  move <MOVE>   - Analyze move (UCI or SAN)")
    print("  show          - Show current position")
    print("  level <LEVEL> - Change skill level")
    print("  quit          - Exit")
    print()

    current_fen = chess.STARTING_FEN
    current_level = skill_level

    analyzer = StockfishAnalyzer()
    extractor = FactExtractor(analyzer, current_level)
    explainer = LLMExplainer(skill_level=current_level)

    try:
        while True:
            try:
                cmd = input("chess> ").strip()
            except EOFError:
                break

            if not cmd:
                continue

            parts = cmd.split(maxsplit=1)
            command = parts[0].lower()

            if command == "quit" or command == "exit":
                break

            elif command == "fen":
                if len(parts) < 2:
                    print("Usage: fen <FEN>")
                    continue
                try:
                    chess.Board(parts[1])  # Validate
                    current_fen = parts[1]
                    print(f"Position set: {current_fen}")
                except ValueError as e:
                    print(f"Invalid FEN: {e}")

            elif command == "show":
                board = chess.Board(current_fen)
                print(board)
                print(f"\nFEN: {current_fen}")
                print(f"Side to move: {'White' if board.turn else 'Black'}")

            elif command == "move":
                if len(parts) < 2:
                    print("Usage: move <MOVE>")
                    continue

                move_str = parts[1]
                try:
                    facts = extractor.extract_facts(current_fen, move_str)
                    result = explainer.explain_with_alternative(facts)

                    print(f"\n--- Analysis of {facts.played_move_san} ---")
                    print(f"Quality: {facts.move_quality.upper()}")
                    print(f"Eval: {facts.eval_before_cp/100:+.2f} -> {facts.eval_after_cp/100:+.2f}")
                    if facts.cp_loss > 0:
                        print(f"CP Loss: {facts.cp_loss}")
                    print()
                    print(f"Explanation: {result['explanation']}")
                    if result['recommendation']:
                        print(f"Recommendation: {result['recommendation']}")
                    print()

                except Exception as e:
                    print(f"Error analyzing move: {e}")

            elif command == "level":
                if len(parts) < 2:
                    print(f"Current level: {current_level}")
                    print(f"Available: {', '.join(SKILL_LEVELS.keys())}")
                    continue

                new_level = parts[1].lower()
                if new_level in SKILL_LEVELS:
                    current_level = new_level
                    extractor = FactExtractor(analyzer, current_level)
                    explainer = LLMExplainer(skill_level=current_level)
                    print(f"Level set to: {current_level}")
                else:
                    print(f"Unknown level. Available: {', '.join(SKILL_LEVELS.keys())}")

            else:
                print(f"Unknown command: {command}")

    finally:
        analyzer.close()

    print("\nGoodbye!")


def main():
    parser = argparse.ArgumentParser(
        description="ChessCoach - Explain chess moves in human terms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single move
  python main.py --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3" --move "e5"

  # Analyze with beginner-level explanations
  python main.py --fen "..." --move "Qh5" --level beginner

  # Analyze a PGN game
  python main.py --pgn game.pgn --level intermediate

  # Interactive CLI mode
  python main.py --interactive

  # Web UI (recommended)
  python app.py
  # Then open http://localhost:5050 in your browser
        """
    )

    parser.add_argument("--fen", type=str, help="Position in FEN format")
    parser.add_argument("--move", type=str, help="Move to analyze (UCI or SAN)")
    parser.add_argument("--pgn", type=str, help="Path to PGN file to analyze")
    parser.add_argument("--level", type=str, default="intermediate",
                        choices=["beginner", "intermediate", "advanced"],
                        help="Skill level for explanations")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Include detailed facts in output")
    parser.add_argument("--all-moves", action="store_true",
                        help="In PGN mode, explain all moves (not just mistakes)")

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        interactive_mode(args.level)
        return

    # Single move analysis
    if args.fen and args.move:
        result = analyze_move(args.fen, args.move, args.level, args.verbose)

        print(f"\n=== Move Analysis: {result['move']} ===")
        print(f"Quality: {result['quality'].upper()}")
        print(f"Eval: {result['eval_before']:+.2f} -> {result['eval_after']:+.2f}")
        if result['cp_loss'] > 0:
            print(f"CP Loss: {result['cp_loss']}")
        print()
        print(f"Explanation:\n{result['explanation']}")
        if result['recommendation']:
            print(f"\nRecommendation: {result['recommendation']}")

        if args.verbose and 'facts' in result:
            print("\n--- Detailed Facts ---")
            import json
            print(json.dumps(result['facts'], indent=2))

        return

    # PGN analysis
    if args.pgn:
        try:
            with open(args.pgn, 'r') as f:
                pgn_content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.pgn}")
            sys.exit(1)

        results = analyze_pgn(pgn_content, args.level, args.all_moves)

        print(f"\n=== Game Analysis ({args.level} level) ===\n")
        for r in results:
            side = r['side']
            move_num = r['move_number']
            move = r['move']
            quality = r['quality']

            if r['explanation']:
                print(f"{move_num}. {side}: {move} ({quality.upper()})")
                print(f"   {r['explanation']}")
                if r['recommendation']:
                    print(f"   -> {r['recommendation']}")
                print()
            elif quality in ["mistake", "blunder"]:
                print(f"{move_num}. {side}: {move} ({quality.upper()}) - CP loss: {r['cp_loss']}")

        return

    # No valid arguments
    parser.print_help()


if __name__ == "__main__":
    main()
