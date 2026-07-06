"""ChromaDB-based RAG module for chess theory knowledge."""

import sys

sys.path.insert(0, str(__file__).rsplit("\\", 2)[0])

import chromadb
from config import CHROMADB_PATH, CHROMADB_COLLECTION


class ChessTheoryRAG:
    """Retrieval-Augmented Generation wrapper around ChromaDB for chess theory."""

    # Mapping from game phase / position type to categories
    _PHASE_CATEGORY_MAP = {
        "opening": ["opening"],
        "middlegame": ["middlegame", "tactic", "strategy"],
        "endgame": ["endgame"],
        "tactic": ["tactic"],
        "strategy": ["strategy"],
        "pawn_structure": ["strategy"],
    }

    def __init__(self):
        self._client = chromadb.PersistentClient(path=CHROMADB_PATH)
        self._collection = self._client.get_or_create_collection(
            name=CHROMADB_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        # Auto-seed on first use
        if self._collection.count() == 0:
            self._seed()

    def _seed(self):
        """Populate the collection with seed data."""
        from knowledge.seed_data import get_seed_documents

        docs = get_seed_documents()
        ids = [d["id"] for d in docs]
        contents = [d["content"] for d in docs]
        metadatas = [d["metadata"] for d in docs]
        self._collection.add(ids=ids, documents=contents, metadatas=metadatas)

    def query(
        self,
        fen: str | None = None,
        position_type: str | None = None,
        tags: list[str] | None = None,
        k: int = 3,
    ) -> list[dict]:
        """Query the knowledge base for relevant chess theory passages.

        Args:
            fen: FEN string of the current position (used for context, not
                 directly embedded).
            position_type: Game phase or position category, e.g.
                           'opening', 'middlegame', 'endgame', 'tactic',
                           'strategy'.
            tags: Additional keywords describing the position, e.g.
                  ['pin', 'king_safety', 'pawn_structure'].
            k: Number of results to return.

        Returns:
            List of dicts with keys: title, content, category, difficulty.
        """
        # Build query text from position_type and tags
        query_parts: list[str] = []
        if position_type:
            query_parts.append(position_type.replace("_", " "))
        if tags:
            query_parts.extend(tag.replace("_", " ") for tag in tags)
        if not query_parts:
            query_parts.append("chess strategy")

        query_text = " ".join(query_parts)

        # Build metadata filter based on game phase
        where_filter = None
        if position_type:
            categories = self._PHASE_CATEGORY_MAP.get(
                position_type.lower(), []
            )
            if len(categories) == 1:
                where_filter = {"category": categories[0]}
            elif len(categories) > 1:
                where_filter = {
                    "$or": [{"category": cat} for cat in categories]
                }

        query_kwargs: dict = {
            "query_texts": [query_text],
            "n_results": k,
        }
        if where_filter:
            query_kwargs["where"] = where_filter

        results = self._collection.query(**query_kwargs)

        # Unpack ChromaDB results into clean dicts
        documents: list[dict] = []
        if results and results["documents"]:
            for i, doc_text in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                documents.append(
                    {
                        "title": meta.get("title", ""),
                        "content": doc_text,
                        "category": meta.get("category", ""),
                        "difficulty": meta.get("difficulty", ""),
                    }
                )

        return documents
