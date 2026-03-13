#!/usr/bin/env python3
"""Test script to replicate the RAG pipeline initialization"""

import sys
import os
from pathlib import Path

# Project root (parent of tests/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    print("Testing RAG Pipeline initialization...")
    from src.rag_pipeline import RAGPipeline

    config_path = PROJECT_ROOT / "config" / "rag_config.yaml"
    print(f"Loading config from: {config_path}")

    pipeline = RAGPipeline(config_path=str(config_path))
    print("✓ RAG Pipeline initialized successfully!")

except Exception as e:
    print(f"✗ Error initializing RAG Pipeline: {e}")
    import traceback
    traceback.print_exc()