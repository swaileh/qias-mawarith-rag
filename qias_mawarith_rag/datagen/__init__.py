"""
QIAS 2026 Synthetic Data Generator

Generates training data for LLM fine-tuning on Islamic inheritance reasoning.
Uses the Mawarith calculator to produce correct answers, then generates
Arabic problem texts and Fiqh reasoning traces.
"""

from .generator import FiqhDataGenerator
from .arabic import ArabicProblemGenerator, ArabicReasoningGenerator
from .exporter import export_to_jsonl, export_to_hf_format, export_to_train_format
from .validator import validate_example, validate_file, validate_directory

__all__ = [
    "FiqhDataGenerator",
    "ArabicProblemGenerator", 
    "ArabicReasoningGenerator",
    "export_to_jsonl",
    "export_to_hf_format",
    "export_to_train_format",
    "validate_example",
    "validate_file",
    "validate_directory",
]
