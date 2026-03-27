# QIAS Mawarith RAG

**RAG-Guided LLM Reasoning for Al-Mawarith Share Computation and Heir Allocation**

[![Paper](https://img.shields.io/badge/arXiv-2603.24012-b31b1b.svg)](https://arxiv.org/abs/2603.24012)
[![Rank](https://img.shields.io/badge/QIAS%202026-🏆%20Rank%201-gold.svg)](#)
[![MIR-E](https://img.shields.io/badge/MIR--E-0.935-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)

> **1st place** on the [QIAS 2026](https://sites.google.com/view/qias2026/) blind-test leaderboard for Islamic Inheritance Reasoning.

---

## Overview

A retrieval-augmented, schema-constrained pipeline for Islamic inheritance (Ilm al-Mawarith) reasoning. The system combines:

1. **Symbolic Calculator & Rule-Based Generator** (§3.2) — A deterministic inheritance calculator that generates ~100K synthetic training cases with full stage-wise reasoning traces.

2. **Hybrid Retrieval with Cross-Encoder Reranking** (§3.3.1) — Dense semantic search + BM25 lexical search, fused via weighted Reciprocal Rank Fusion and reranked by a cross-encoder.

3. **Constrained LLM Decoding & Validation** (§3.3.2–3.3.3) — Qwen3.5-9B with structured `<think>`/`<answer>` generation and a multi-stage output parser enforcing schema, type, label, and share-coherence constraints.

## Project Structure

```
qias-mawarith-rag/
├── pyproject.toml                # Package metadata & dependencies
├── CITATION.cff                  # Paper citation
├── config/
│   └── rag_config.yaml           # Pipeline configuration
│
├── qias_mawarith_rag/            # Main package
│   ├── pipeline.py               # RAGPipeline orchestrator
│   ├── workers.py                # Multi-GPU inference workers
│   ├── calculator/               # Symbolic inheritance calculator
│   ├── datagen/                  # Rule-based synthetic data generator
│   ├── knowledge/                # PDF processing & vector store
│   ├── retrieval/                # Hybrid retriever & reranker
│   ├── generation/               # LLM client, output parser, thinking extractor
│   ├── evaluation/               # MIR-E wrapper & relevance metrics
│   └── training/                 # Feedback loop & fine-tuning
│
├── scripts/                      # CLI entry points
│   ├── run_pipeline.py           # Main inference & evaluation
│   ├── build_prediction.py       # Build submission JSON
│   └── verify_setup.py           # Environment verification
│
├── tests/                        # Pytest test suite
├── notebooks/                    # Jupyter notebooks (Colab & local)
└── data/                         # PDFs, datasets, vector DB
```

## Installation

### Option 1: Conda (Recommended)

Create a ready-to-use environment from the provided `environment.yaml`:

```bash
# Clone the repository
git clone https://github.com/swaileh/qias-mawarith-rag.git
cd qias-mawarith-rag

# Create and activate the conda environment
conda env create -f environment.yaml
conda activate qias
```

### Option 2: Manual Install

```bash
# Clone the repository
git clone https://github.com/swaileh/qias-mawarith-rag.git
cd qias-mawarith-rag

# Create a conda environment (or use virtualenv)
conda create -n qias python=3.11 -y
conda activate qias

# Install with GPU support
pip install -e ".[gpu,dev]"

# Or CPU-only (for the symbolic calculator and data generation)
pip install -e ".[dev]"
```

**Requirements:** Python ≥ 3.10, CUDA GPU recommended for LLM inference.

Set up your HuggingFace token for model access:
```bash
export HF_TOKEN="your-huggingface-token"
```

## Quick Start

### Symbolic Calculator (no GPU needed)

```python
from qias_mawarith_rag.calculator import MiraathCase

# One-liner for simple cases
result = MiraathCase.quick(["زوج", "أم", ("بنت", 2)])
print(result)

# Full API with method chaining
case = MiraathCase(madhab="shafii")
case.add_heir("زوجة", count=2)
case.add_heir("ابن")
case.add_heir("بنت", count=3)
result = case.calculate()
```

### RAG Pipeline (GPU required)

```python
from qias_mawarith_rag.pipeline import RAGPipeline

pipeline = RAGPipeline(config_path="config/rag_config.yaml")

# Build knowledge base
pipeline.build_knowledge_base(pdf_directory="data/pdfs")

# Query
result = pipeline.query("مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟")
print(result["parsed_output"]["structured_output"])
```

### Batch Inference

```bash
# Dev evaluation (with ground truth)
python scripts/run_pipeline.py --batch --dev-dir /path/to/dev/

# Test inference (submission format)
python scripts/run_pipeline.py --test --test-file /path/to/test.json

# Multi-GPU acceleration
python scripts/run_pipeline.py --test --num-gpus 2

# Build submission JSON
python scripts/build_prediction.py --results-dir ./results
```

## Configuration

All settings are in [`config/rag_config.yaml`](config/rag_config.yaml):

| Parameter | Default | Description |
|---|---|---|
| `model.name` | `Qwen/Qwen3.5-9B` | LLM model (HuggingFace) |
| `model.quantization` | `8bit` | BitsAndBytes quantization |
| `retrieval.semantic_weight` | `0.7` | Semantic search weight in RRF |
| `retrieval.keyword_weight` | `0.3` | BM25 keyword weight in RRF |
| `retrieval.top_k` | `5` | Number of retrieved documents |
| `retrieval.rerank` | `true` | Enable cross-encoder reranking |
| `vector_store.chunk_size` | `512` | Document chunk size (tokens) |

## Testing

```bash
python -m pytest tests/ -v
```

## Citation

If you use this code, please cite:

```bibtex
@misc{swaileh2026cvpdqias2026ragguided,
  title     = {CVPD at QIAS 2026: RAG-Guided LLM Reasoning for Al-Mawarith
               Share Computation and Heir Allocation},
  author    = {Wassim Swaileh and Mohammed-En-Nadhir Zighem and Hichem Telli
               and Salah Eddine Bekhouche and Abdellah Zakaria Sellam
               and Fadi Dornaika and Dimitrios Kotzinos},
  year      = {2026},
  eprint    = {2603.24012},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url       = {https://arxiv.org/abs/2603.24012},
}
```

## License

This project is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
