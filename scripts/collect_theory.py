"""
Collect chess theory from Wikipedia and the existing seed_data.py.

Outputs: scripts/data/raw_theory.jsonl
Each line is a JSON object:
  {"id": "wiki_pin_1", "title": "...", "content": "...", "source": "wikipedia", "url": "..."}

Usage:
    pip install requests beautifulsoup4
    python scripts/collect_theory.py
"""

import json
import re
import sys
import time
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

# ---------------------------------------------------------------------------
# Add project root to path so we can import seed_data
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from knowledge.seed_data import get_seed_documents

# ---------------------------------------------------------------------------
# Wikipedia articles to scrape
# ---------------------------------------------------------------------------
WIKIPEDIA_ARTICLES = [
    ("Chess tactics",              "https://en.wikipedia.org/wiki/Chess_tactics"),
    ("Chess strategy",             "https://en.wikipedia.org/wiki/Chess_strategy"),
    ("Chess endgame",              "https://en.wikipedia.org/wiki/Chess_endgame"),
    ("Pawn structure",             "https://en.wikipedia.org/wiki/Pawn_structure"),
    ("King safety (chess)",        "https://en.wikipedia.org/wiki/King_safety_(chess)"),
    ("Rook endgames",              "https://en.wikipedia.org/wiki/Rook_(chess)#Endgames"),
    ("Bishop strategy",            "https://en.wikipedia.org/wiki/Bishop_(chess)#Strategy"),
    ("Knight strategy",            "https://en.wikipedia.org/wiki/Knight_(chess)#Strategy"),
    ("Queen strategy",             "https://en.wikipedia.org/wiki/Queen_(chess)#Strategy"),
    ("Zugzwang",                   "https://en.wikipedia.org/wiki/Zugzwang"),
    ("Tempo (chess)",              "https://en.wikipedia.org/wiki/Tempo_(chess)"),
    ("Opposition (chess)",         "https://en.wikipedia.org/wiki/Opposition_(chess)"),
    ("Triangulation (chess)",      "https://en.wikipedia.org/wiki/Triangulation_(chess)"),
    ("Decoy (chess)",              "https://en.wikipedia.org/wiki/Decoy_(chess)"),
    ("Pin (chess)",                "https://en.wikipedia.org/wiki/Pin_(chess)"),
    ("Fork (chess)",               "https://en.wikipedia.org/wiki/Fork_(chess)"),
    ("Skewer (chess)",             "https://en.wikipedia.org/wiki/Skewer_(chess)"),
    ("Discovered attack",          "https://en.wikipedia.org/wiki/Discovered_attack"),
    ("Double check",               "https://en.wikipedia.org/wiki/Double_check"),
    ("Zwischenzug",                "https://en.wikipedia.org/wiki/Zwischenzug"),
    ("Outpost (chess)",            "https://en.wikipedia.org/wiki/Outpost_(chess)"),
    ("Passed pawn",                "https://en.wikipedia.org/wiki/Passed_pawn"),
    ("Isolated pawn",              "https://en.wikipedia.org/wiki/Isolated_pawn"),
    ("Backward pawn",              "https://en.wikipedia.org/wiki/Backward_pawn"),
    ("Doubled pawns",              "https://en.wikipedia.org/wiki/Doubled_pawns"),
    ("Pawn majority",              "https://en.wikipedia.org/wiki/Pawn_majority"),
    ("Open file",                  "https://en.wikipedia.org/wiki/Open_file"),
    ("Half-open file",             "https://en.wikipedia.org/wiki/Half-open_file"),
    ("Fianchetto",                 "https://en.wikipedia.org/wiki/Fianchetto"),
    ("Initiative (chess)",         "https://en.wikipedia.org/wiki/Initiative_(chess)"),
    ("Prophylaxis (chess)",        "https://en.wikipedia.org/wiki/Prophylaxis_(chess)"),
    ("Compensation (chess)",       "https://en.wikipedia.org/wiki/Compensation_(chess)"),
    ("Exchange (chess)",           "https://en.wikipedia.org/wiki/Exchange_(chess)"),
    ("Endgame tablebase",          "https://en.wikipedia.org/wiki/Endgame_tablebase"),
    ("Lucena position",            "https://en.wikipedia.org/wiki/Lucena_position"),
    ("Philidor position",          "https://en.wikipedia.org/wiki/Philidor_position"),
    ("Rook and pawn vs rook endgame", "https://en.wikipedia.org/wiki/Rook_and_pawn_versus_rook_endgame"),
]

CHUNK_SIZE = 500       # target characters per chunk
CHUNK_OVERLAP = 100    # overlap between chunks

HEADERS = {
    "User-Agent": (
        "ChessCoachBot/1.0 (educational chess theory collection; "
        "contact: chesscoach@example.com)"
    )
}

OUTPUT_PATH = Path(__file__).parent / "data" / "raw_theory.jsonl"


# ---------------------------------------------------------------------------
# Scraping helpers
# ---------------------------------------------------------------------------

def _is_noise_element(tag: Tag) -> bool:
    """Return True for elements we want to skip."""
    if tag.name in ("table", "figure", "img", "style", "script"):
        return True
    classes = tag.get("class", [])
    if isinstance(classes, str):
        classes = [classes]
    noise_classes = {
        "reflist", "references", "navbox", "infobox", "hatnote",
        "mw-editsection", "mw-references-wrap", "thumb", "toc",
        "sistersitebox", "noprint", "mbox-small", "ambox",
    }
    if noise_classes & set(classes):
        return True
    return False


def _clean_text(text: str) -> str:
    """Normalise whitespace and remove citation markers like [1]."""
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_article_text(title: str, url: str) -> list[str]:
    """
    Fetch a Wikipedia article and return a list of paragraph strings.
    Handles fragment URLs (e.g. #Endgames) by scanning only the section.
    """
    # Separate base URL from fragment
    if "#" in url:
        base_url, fragment = url.split("#", 1)
    else:
        base_url, fragment = url, None

    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  WARNING: could not fetch {url}: {exc}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", {"id": "mw-content-text"})
    if not content_div:
        return []

    paragraphs: list[str] = []

    if fragment:
        # Find the heading that matches the fragment, then collect paragraphs
        # until the next same-or-higher level heading.
        target_heading = None
        for heading in content_div.find_all(["h2", "h3", "h4"]):
            span = heading.find("span", {"id": fragment})
            if span:
                target_heading = heading
                break

        if target_heading is None:
            # Fall back to scanning everything
            fragment = None
        else:
            level = int(target_heading.name[1])  # e.g. 2 for h2
            sibling = target_heading.find_next_sibling()
            section_paragraphs: list[str] = []
            while sibling:
                if sibling.name and sibling.name[0] == "h":
                    sib_level = int(sibling.name[1])
                    if sib_level <= level:
                        break
                if isinstance(sibling, Tag) and sibling.name == "p":
                    if not _is_noise_element(sibling):
                        text = _clean_text(sibling.get_text())
                        if len(text) > 40:
                            section_paragraphs.append(text)
                sibling = sibling.find_next_sibling()
            paragraphs = section_paragraphs

    if not fragment:
        # Collect all non-noise <p> tags across the article
        # Cap at first ~80 paragraphs to avoid enormous articles
        for p in content_div.find_all("p"):
            if _is_noise_element(p):
                continue
            # Skip if inside a noise parent
            parent = p.parent
            skip = False
            while parent and parent != content_div:
                if isinstance(parent, Tag) and _is_noise_element(parent):
                    skip = True
                    break
                parent = parent.parent if parent else None
            if skip:
                continue
            text = _clean_text(p.get_text())
            if len(text) > 40:
                paragraphs.append(text)
            if len(paragraphs) >= 80:
                break

    return paragraphs


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks on sentence/word boundaries."""
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Try to break at a sentence boundary (. ! ?) within last 60 chars
        if end < len(text):
            best = end
            for sep in (". ", "! ", "? ", ".\n", "!\n", "?\n"):
                idx = text.rfind(sep, start + overlap, end)
                if idx != -1:
                    best = idx + 1
                    break
            else:
                # Fall back to last space
                idx = text.rfind(" ", start + overlap, end)
                if idx != -1:
                    best = idx + 1
            end = best

        chunks.append(text[start:end].strip())
        # Move forward, keeping overlap
        start = end - overlap if end - overlap > start else end

    return [c for c in chunks if len(c) > 20]


def make_id(prefix: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", prefix.lower()).strip("_")
    return f"{slug}_{index}"


# ---------------------------------------------------------------------------
# Main collection logic
# ---------------------------------------------------------------------------

def collect_wikipedia() -> list[dict]:
    docs: list[dict] = []
    for title, url in WIKIPEDIA_ARTICLES:
        print(f"  Fetching: {title}")
        paragraphs = fetch_article_text(title, url)
        if not paragraphs:
            print(f"    (no paragraphs found)")
            continue

        # Join all paragraphs, then chunk the whole article
        full_text = " ".join(paragraphs)
        chunks = chunk_text(full_text)

        prefix = "wiki_" + re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        for i, chunk in enumerate(chunks):
            docs.append({
                "id": f"{prefix}_{i + 1}",
                "title": title,
                "content": chunk,
                "source": "wikipedia",
                "url": url,
            })

        print(f"    -> {len(chunks)} chunks")
        # Be polite to Wikipedia servers
        time.sleep(0.5)

    return docs


def collect_seed_data() -> list[dict]:
    """Convert existing hand-written docs to the raw_theory format."""
    docs: list[dict] = []
    for doc in get_seed_documents():
        meta = doc.get("metadata", {})
        docs.append({
            "id": doc.get("id", f"seed_{len(docs)}"),
            "title": meta.get("title", doc.get("id", "")),
            "content": doc.get("content", ""),
            "source": "seed_data",
            "url": "",
        })
    return docs


def write_jsonl(docs: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(docs)} documents to {path}")


def main():
    print("=== Chess Theory Collector ===\n")

    print("[1/2] Collecting seed data...")
    seed_docs = collect_seed_data()
    print(f"  -> {len(seed_docs)} seed documents")

    print("\n[2/2] Scraping Wikipedia articles...")
    wiki_docs = collect_wikipedia()
    print(f"  -> {len(wiki_docs)} Wikipedia chunks")

    all_docs = seed_docs + wiki_docs
    write_jsonl(all_docs, OUTPUT_PATH)
    print("Done.")


if __name__ == "__main__":
    main()
