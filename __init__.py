"""Package initialization for qias_rag_thinking"""

__version__ = "1.0.0"
__author__ = "QIAS 2026 Team"
__description__ = "RAG System for Islamic Inheritance Reasoning with Qwen3 Thinking Model"

from .src.rag_pipeline import RAGPipeline

__all__ = ['RAGPipeline']
