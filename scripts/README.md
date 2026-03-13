# Scripts

Runnable entry points for the QIAS RAG project. **Always run from the project root**, e.g.:

```bash
cd /path/to/qias_rag_thinking
python scripts/train.py
python scripts/evaluation/evaluate_relevance.py
```

## Layout

| Path | Purpose |
|------|--------|
| `train.py`, `initialize_rag.py`, `download_*.py` | Main workflows: training, init, data download. |
| `colab/` | Colab-specific helpers (auth, flash attention, notebook generation). |
| `evaluation/` | Evaluation and report generation (relevance, multi-source, dev evaluation). |
| `dev/` | One-off or debug: verify_setup, quick tests, fixes. |

Scripts that need config or `src` resolve the project root via `Path(__file__).resolve().parent.parent` (and one more `.parent` when inside a subfolder).
