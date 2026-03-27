"""
QIAS Mawarith RAG — RAG-Guided LLM Reasoning for Islamic Inheritance

A retrieval-augmented, schema-constrained pipeline for Islamic inheritance
(al-Mawarith) reasoning, as described in:

  Swaileh et al., "CVPD at QIAS 2026: RAG-Guided LLM Reasoning for
  Al-Mawarith Share Computation and Heir Allocation", 2026.
  https://arxiv.org/abs/2603.24012

Main entry points:
  - RAGPipeline: end-to-end RAG inference (requires GPU dependencies)
  - MiraathCase: deterministic symbolic calculator (no GPU needed)
  - FiqhDataGenerator: rule-based synthetic data generation
"""

__version__ = "2.0.0"
__author__ = "Wassim Swaileh, Mohammed-En-Nadhir Zighem, Hichem Telli, Salah Eddine Bekhouche, Abdellah Zakaria Sellam, Fadi Dornaika, Dimitrios Kotzinos"

# Lazy imports — heavy dependencies (torch, sentence-transformers) are only
# loaded when RAGPipeline is actually accessed, not on package import.
from qias_mawarith_rag.calculator import MiraathCase


def __getattr__(name):
    if name == "RAGPipeline":
        from qias_mawarith_rag.pipeline import RAGPipeline
        return RAGPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["RAGPipeline", "MiraathCase"]
