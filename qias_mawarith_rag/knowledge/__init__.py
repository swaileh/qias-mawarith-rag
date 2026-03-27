"""Knowledge module — PDF processing, vector store, web search, and synthetic data ingestion."""

__all__ = ['PDFProcessor', 'Document', 'VectorStore', 'WebSearch', 'SyntheticIngester']


def __getattr__(name):
    """Lazy imports to avoid loading heavy dependencies (chromadb, sentence-transformers)
    until they are actually needed."""
    if name in ("PDFProcessor", "Document"):
        from .pdf_processor import PDFProcessor, Document
        return {"PDFProcessor": PDFProcessor, "Document": Document}[name]
    if name == "VectorStore":
        from .vector_store import VectorStore
        return VectorStore
    if name == "WebSearch":
        from .web_search import WebSearch
        return WebSearch
    if name == "SyntheticIngester":
        from .synthetic_ingester import SyntheticIngester
        return SyntheticIngester
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
