"""Chess theory knowledge base module."""
try:
    from .rag import ChessTheoryRAG
except ImportError:
    ChessTheoryRAG = None

__all__ = ["ChessTheoryRAG"]
