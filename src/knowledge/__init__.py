"""Package initialization for knowledge module"""
from .pdf_processor import PDFProcessor, Document
from .vector_store import VectorStore
from .web_search import WebSearch

__all__ = ['PDFProcessor', 'Document', 'VectorStore', 'WebSearch']
