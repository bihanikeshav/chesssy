"""
Classify/label raw chess theory documents.

Reads:  scripts/data/raw_theory.jsonl
Writes: scripts/data/classified_theory.jsonl

Each output doc gets:
  - category    (tactics | endgames | strategy | opening | psychology)
  - subcategory (most-specific matched concept)
  - difficulty  (beginner | intermediate | advanced)
  - tags        (list of matched chess terms)

Usage:
    python scripts/classify_theory.py
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Classification rules
# ---------------------------------------------------------------------------

CATEGORY_RULES: dict[str, list[str]] = {
    "tactics": [
        "pin", "fork", "skewer", "discovered", "double check",
        "zwischenzug", "decoy", "deflection", "overloaded", "hanging",
        "sacrifice", "combination", "tactic", "checkmate", "mate in",
        "back rank", "smothered", "cross-pin", "removing the defender",
        "in-between move", "intermezzo", "windmill", "x-ray",
    ],
    "endgames": [
        "endgame", "rook ending", "pawn ending", "king and pawn",
        "opposition", "triangulation", "zugzwang", "lucena", "philidor",
        "tablebase", "passed pawn", "promotion", "king activity",
        "pawn promotion", "queening", "rook endgame", "rook and pawn",
        "distant opposition", "rook vs", "fortress",
    ],
    "strategy": [
        "outpost", "pawn structure", "weak square", "isolated",
        "backward", "doubled", "pawn majority", "open file", "half-open",
        "initiative", "prophylaxis", "compensation", "bishop pair",
        "good bishop", "bad bishop", "piece activity", "exchange",
        "fianchetto", "pawn chain", "minority attack", "space advantage",
        "piece coordination", "weak pawn", "pawn island",
    ],
    "opening": [
        "opening", "development", "center", "castling", "tempo",
        "gambit", "italian", "sicilian", "french", "caro", "english",
        "queen's gambit", "king's indian", "nimzo", "ruy lopez",
        "spanish", "vienna", "scotch", "four knights", "london system",
        "slav", "dutch", "grunfeld", "benoni", "alekhine",
    ],
    "psychology": [
        "time trouble", "blunder", "psychology", "practical",
        "competitive", "clock", "pressure", "tournament", "nerves",
        "confidence", "concentration",
    ],
}

# Ordered by priority (first match wins for ties)
CATEGORY_ORDER = ["tactics", "endgames", "strategy", "opening", "psychology"]

# Subcategory rules: category -> {subcategory: keywords}
SUBCATEGORY_RULES: dict[str, dict[str, list[str]]] = {
    "tactics": {
        "pin":               ["pin", "absolute pin", "relative pin"],
        "fork":              ["fork", "double attack"],
        "skewer":            ["skewer"],
        "discovered_attack": ["discovered attack", "discovered check"],
        "double_check":      ["double check"],
        "zwischenzug":       ["zwischenzug", "in-between move", "intermezzo"],
        "decoy":             ["decoy", "deflection", "removing the defender"],
        "sacrifice":         ["sacrifice", "gambit"],
        "checkmate":         ["checkmate", "mate in", "back rank", "smothered"],
        "combination":       ["combination"],
    },
    "endgames": {
        "rook_endgame":      ["rook ending", "rook endgame", "rook and pawn", "lucena", "philidor"],
        "pawn_endgame":      ["pawn ending", "king and pawn", "opposition", "triangulation", "passed pawn"],
        "zugzwang":          ["zugzwang"],
        "tablebase":         ["tablebase"],
        "promotion":         ["promotion", "queening", "pawn promotion"],
        "king_activity":     ["king activity", "king centralisation"],
    },
    "strategy": {
        "outpost":           ["outpost"],
        "pawn_structure":    ["pawn structure", "pawn chain", "pawn island"],
        "weak_squares":      ["weak square"],
        "isolated_pawn":     ["isolated pawn"],
        "backward_pawn":     ["backward pawn"],
        "doubled_pawns":     ["doubled pawns", "doubled pawn"],
        "open_file":         ["open file", "half-open file"],
        "bishop_pair":       ["bishop pair", "good bishop", "bad bishop"],
        "fianchetto":        ["fianchetto"],
        "initiative":        ["initiative"],
        "prophylaxis":       ["prophylaxis"],
        "compensation":      ["compensation"],
        "exchange":          ["exchange"],
        "pawn_majority":     ["pawn majority", "minority attack"],
    },
    "opening": {
        "development":       ["development", "develop"],
        "center_control":    ["center", "central pawn", "central control"],
        "castling":          ["castling", "castle"],
        "tempo":             ["tempo"],
        "gambit":            ["gambit"],
        "specific_opening":  [
            "sicilian", "french", "caro", "english", "queen's gambit",
            "king's indian", "nimzo", "ruy lopez", "italian", "spanish",
            "vienna", "scotch", "london system", "slav", "dutch",
            "grunfeld", "benoni", "alekhine",
        ],
    },
    "psychology": {
        "time_management":   ["time trouble", "clock", "time pressure"],
        "competitive":       ["tournament", "practical", "competitive"],
        "mental_game":       ["psychology", "nerves", "confidence", "concentration"],
    },
}

DIFFICULTY_RULES: dict[str, list[str]] = {
    "beginner": [
        "basic", "simple", "fundamental", "beginner", "elementary",
        "key principle", "first", "introduction", "basics",
        "must know", "essential", "easy",
    ],
    "advanced": [
        "advanced", "complex", "subtle", "deep", "grandmaster",
        "calculation", "prophylaxis", "zugzwang", "triangulation",
        "nuanced", "sophisticated", "expert", "master level",
        "theoretical", "precise", "difficult",
    ],
}

# Tags to extract: term -> canonical tag name
TAG_PATTERNS: list[tuple[str, str]] = [
    ("pin",                "pin"),
    ("fork",               "fork"),
    ("skewer",             "skewer"),
    ("discovered attack",  "discovered_attack"),
    ("double check",       "double_check"),
    ("zwischenzug",        "zwischenzug"),
    ("decoy",              "decoy"),
    ("deflection",         "deflection"),
    ("sacrifice",          "sacrifice"),
    ("checkmate",          "checkmate"),
    ("combination",        "combination"),
    ("endgame",            "endgame"),
    ("pawn ending",        "pawn_endgame"),
    ("rook ending",        "rook_endgame"),
    ("rook endgame",       "rook_endgame"),
    ("opposition",         "opposition"),
    ("triangulation",      "triangulation"),
    ("zugzwang",           "zugzwang"),
    ("lucena",             "lucena"),
    ("philidor",           "philidor"),
    ("passed pawn",        "passed_pawn"),
    ("outpost",            "outpost"),
    ("pawn structure",     "pawn_structure"),
    ("isolated pawn",      "isolated_pawn"),
    ("backward pawn",      "backward_pawn"),
    ("doubled pawn",       "doubled_pawns"),
    ("open file",          "open_file"),
    ("half-open",          "half_open_file"),
    ("fianchetto",         "fianchetto"),
    ("initiative",         "initiative"),
    ("prophylaxis",        "prophylaxis"),
    ("compensation",       "compensation"),
    ("exchange",           "exchange"),
    ("bishop pair",        "bishop_pair"),
    ("bad bishop",         "bad_bishop"),
    ("good bishop",        "good_bishop"),
    ("king safety",        "king_safety"),
    ("castling",           "castling"),
    ("development",        "development"),
    ("tempo",              "tempo"),
    ("gambit",             "gambit"),
    ("promotion",          "promotion"),
    ("pawn majority",      "pawn_majority"),
    ("tablebase",          "tablebase"),
    ("center",             "center_control"),
]


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def _lower(text: str) -> str:
    return text.lower()


def _count_keywords(text_lower: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if kw in text_lower)


def classify_category(text_lower: str) -> str:
    """Return the best matching category, or 'strategy' as default."""
    scores: dict[str, int] = {}
    for cat in CATEGORY_ORDER:
        scores[cat] = _count_keywords(text_lower, CATEGORY_RULES[cat])

    best_cat = max(CATEGORY_ORDER, key=lambda c: scores[c])
    if scores[best_cat] == 0:
        return "strategy"
    return best_cat


def classify_subcategory(category: str, text_lower: str) -> str:
    """Return the best subcategory for the given category."""
    rules = SUBCATEGORY_RULES.get(category, {})
    if not rules:
        return ""

    best_sub = ""
    best_score = 0
    for sub, keywords in rules.items():
        score = _count_keywords(text_lower, keywords)
        if score > best_score:
            best_score = score
            best_sub = sub

    return best_sub


def classify_difficulty(text_lower: str, title_lower: str) -> str:
    """Return difficulty: beginner | intermediate | advanced."""
    combined = title_lower + " " + text_lower

    beg_score = _count_keywords(combined, DIFFICULTY_RULES["beginner"])
    adv_score = _count_keywords(combined, DIFFICULTY_RULES["advanced"])

    if adv_score > beg_score:
        return "advanced"
    if beg_score > adv_score:
        return "beginner"
    return "intermediate"


def extract_tags(text_lower: str, category: str, subcategory: str) -> list[str]:
    """Extract specific chess term tags from the content."""
    tags: list[str] = []
    for pattern, tag in TAG_PATTERNS:
        if pattern in text_lower:
            tags.append(tag)

    # Always include category and subcategory as tags
    if category and category not in tags:
        tags.append(category)
    if subcategory and subcategory not in tags:
        tags.append(subcategory)

    return list(dict.fromkeys(tags))  # deduplicate, preserve order


def classify_doc(doc: dict) -> dict:
    """Add category, subcategory, difficulty, tags to a raw doc."""
    content = doc.get("content", "")
    title = doc.get("title", "")
    text_lower = _lower(content)
    title_lower = _lower(title)

    # Seed docs may carry pre-assigned metadata from their source — use as hints
    # but still run full classification so Wikipedia chunks are handled uniformly.
    category = classify_category(text_lower + " " + title_lower)

    # If title gives a strong direct hint, prefer it
    for cat in CATEGORY_ORDER:
        if _count_keywords(title_lower, CATEGORY_RULES[cat]) > 0:
            category = cat
            break

    subcategory = classify_subcategory(category, text_lower + " " + title_lower)
    difficulty = classify_difficulty(text_lower, title_lower)
    tags = extract_tags(text_lower, category, subcategory)

    result = dict(doc)
    result["category"] = category
    result["subcategory"] = subcategory
    result["difficulty"] = difficulty
    result["tags"] = tags
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

INPUT_PATH = Path(__file__).parent / "data" / "raw_theory.jsonl"
OUTPUT_PATH = Path(__file__).parent / "data" / "classified_theory.jsonl"


def main():
    print("=== Chess Theory Classifier ===\n")

    if not INPUT_PATH.exists():
        print(f"ERROR: {INPUT_PATH} not found. Run collect_theory.py first.")
        return

    docs: list[dict] = []
    with open(INPUT_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))

    print(f"Loaded {len(docs)} documents from {INPUT_PATH}")

    classified: list[dict] = []
    category_counts: dict[str, int] = {}
    for doc in docs:
        result = classify_doc(doc)
        classified.append(result)
        cat = result["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for doc in classified:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(classified)} classified documents to {OUTPUT_PATH}")
    print("\nCategory distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:15s}: {count}")
    print("\nDone.")


if __name__ == "__main__":
    main()
