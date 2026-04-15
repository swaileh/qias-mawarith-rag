# Project organization

This document explains how the QIAS RAG workspace is organized and the principles used.

## Principles

1. **Root stays clean** – Only a few top-level items: `README.md`, `requirements.txt`, config, data, source code, and high-level folders. No loose scripts or one-off files at root.
2. **Scripts by purpose** – All runnable entry points live under `scripts/`, grouped by role (main, colab, evaluation, dev).
3. **Docs in one place** – All extra documentation (Colab guides, training, reports) lives in `docs/` so the root README stays the main entry.
4. **Generated outputs separate** – Evaluation results, reports, and other artifacts go under `outputs/` so they are easy to find, ignore in git if needed, and don’t clutter `data/` or root.
5. **Tests in `tests/`** – Every `test_*.py` lives in `tests/` and uses the project root for imports so they run consistently (e.g. `pytest tests/` or `python -m pytest`).
6. **Notebooks in `notebooks/`** – All `.ipynb` files (Colab and local) live in `notebooks/` for a single place to run experiments and demos.

## Layout

| Folder / file   | Purpose |
|-----------------|--------|
| `config/`       | YAML and other config; single source of truth for model, retrieval, paths. |
| `data/`         | Inputs only: PDFs, JSON datasets, vector DB. Not for generated outputs. |
| `docs/`         | All extra docs (Colab, training, evaluation, organization). |
| `notebooks/`    | All Jupyter notebooks. |
| `outputs/`      | Generated files: evaluation JSON/TXT, reports, run artifacts. |
| `scripts/`      | Runnable Python scripts; run from **project root**. |
| `src/`          | Core library (RAG pipeline, model, retrieval, evaluation). |
| `tests/`        | All tests; import via project root. |

## How to run scripts

Always run from the **project root**:

```bash
cd qias_rag_thinking

# Main entry points
python scripts/train.py
python scripts/initialize_rag.py
python scripts/download_arabic_pdfs.py

# Evaluation
python scripts/evaluation/evaluate_relevance.py
python scripts/evaluation/run_multi_source_evaluation.py

# Colab helpers (or run from Colab)
python scripts/colab/create_colab_notebook.py

# Dev / verification
python scripts/dev/verify_setup.py
```

Scripts that need the project root (e.g. for `config/` or `src/`) resolve it via `Path(__file__).resolve().parent.parent` (or one more `.parent` when inside `scripts/colab/` or `scripts/dev/`).

## How this was done

1. **Created directories**: `scripts/` (with `colab/`, `evaluation/`, `dev/`), `docs/`, `outputs/` (with `evaluation/`, `reports/`).
2. **Moved scripts** into `scripts/` by role; moved Colab docs and other `.md`/report files into `docs/`; moved result JSON/TXT and `val_results_*` into `outputs/`.
3. **Moved notebooks** from root into `notebooks/`.
4. **Moved tests** from root into `tests/` and fixed `sys.path` so they use the project root (e.g. `Path(__file__).resolve().parent.parent`).
5. **Adjusted path logic** in scripts that use `__file__` (e.g. `initialize_rag.py`, `train.py`, `verify_setup.py`) so they work from their new locations.
6. **Updated README** with the new structure and a short “how to run” section, and added this doc in `docs/`.

You can reuse this approach in other repos: define a small set of top-level folders, group by purpose, keep root minimal, and fix imports/paths so everything is run from the project root.
