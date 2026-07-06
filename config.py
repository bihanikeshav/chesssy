"""Configuration for ChessCoach."""
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
STOCKFISH_PATH = PROJECT_ROOT / "stockfish" / "stockfish-windows-x86-64-avx2.exe"

# Stockfish settings
STOCKFISH_DEPTH = 12
STOCKFISH_DEPTH_QUICK = 8
STOCKFISH_DEPTH_DEEP = 20
STOCKFISH_THREADS = 4
STOCKFISH_HASH_MB = 256

# Analysis settings
TOP_MOVES_COUNT = 5
MULTIPV = 3

# Skill level thresholds (centipawns)
SKILL_LEVELS = {
    "beginner": {
        "cp_loss_tolerance": 150,
        "max_line_depth": 2,
        "explanation_style": "simple"
    },
    "intermediate": {
        "cp_loss_tolerance": 80,
        "max_line_depth": 3,
        "explanation_style": "tactical"
    }
}

# Claude API settings (OpenAI-compatible local wrapper)
CLAUDE_API_BASE = os.getenv("CLAUDE_API_BASE", "http://localhost:8000")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
CLAUDE_MAX_TOKENS = 800
CLAUDE_TEMPERATURE = 0.3

# ChromaDB settings
CHROMADB_PATH = str(PROJECT_ROOT / "data" / "chromadb")
CHROMADB_COLLECTION = "chess_theory"

# Player rating defaults
DEFAULT_PLAYER_RATING = 1200
MIN_RATING = 800
MAX_RATING = 2000
