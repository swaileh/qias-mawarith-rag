# QIAS RAG Training - Colab Usage Guide

This guide explains how to execute the TRAINING_GUIDE.md steps using Google Colab.

## Overview

The training workflow consists of **6 main steps** following the TRAINING_GUIDE.md:

1. **Build Knowledge Base** - Process PDFs into vector embeddings
2. **Run Initial Evaluation** - Establish baseline metrics
3. **Analyze Errors** - Use feedback loop to identify issues
4. **Apply Improvements** - Adjust config and prompts
5. **Iterative Improvement** - Run multiple training iterations
6. **Final Evaluation** - Test on held-out dataset

---

## Option 1: Using the Colab Notebook (Recommended)

### Step-by-Step Instructions

1. **Open the Training Notebook**
   - File: `notebooks/QIAS_RAG_Training_Colab.ipynb`
   - Or use `colab_training.py` as a standalone script

2. **Upload Project to Google Drive**
   ```
   MyDrive/QIAS_RAG/
   ├── qias_rag_thinking/     # Copy entire project here
   │   ├── src/
   │   ├── config/
   │   └── ...
   ├── data/
   │   └── pdfs/              # PDF files (already have 3 books)
   └── results/               # Will be created automatically
   ```

3. **Open in Google Colab**
   - Go to [Google Colab](https://colab.research.google.com)
   - Upload the notebook file
   - Change runtime to A100 GPU: `Runtime → Change runtime type → A100`

4. **Run Cells Sequentially**

   | Cell | Step | Purpose |
   |------|------|---------|
   | 1-2 | Setup | Verify GPU, mount Drive |
   | 3-5 | Install | Install dependencies |
   | 6-7 | Ollama | Start Ollama server |
   | 8-9 | Load | Import RAG components |
   | 10-11 | Step 1 | **Initialize Pipeline** |
   | 12-13 | Step 1 | **Build Knowledge Base** |
   | 14-15 | Load Data | Load QIAS dataset |
   | 16-17 | Step 2 | **Baseline Evaluation** |
   | 18-19 | Step 3 | **Initialize Feedback Loop** |
   | 20-21 | Step 3 | **Error Analysis** |
   | 22-23 | Step 3 | **Get Suggestions** |
   | 24-25 | Step 5 | **Iterative Training** |
   | 26-27 | Visualize | Plot training progress |
   | 28-29 | Step 6 | **Final Evaluation** |
   | 30-31 | Step 6 | **MIR-E Evaluation** |
   | 32-35 | Save | Save results to Drive |

---

## Option 2: Using the Python Script

### Local Usage

```bash
# Install dependencies first
pip install -r requirements.txt

# Run training workflow
python colab_training.py
```

### Colab Usage

```python
# In a Colab cell:
!git clone https://github.com/your-repo/qias_rag_thinking.git
%cd qias_rag_thinking
!python colab_training.py
```

---

## Training Workflow Summary

### Step 1: Build Knowledge Base ✅
**Files Generated:**
- Vector database in `data/vector_db/`
- BM25 index for hybrid search

**What it does:**
- Processes 3 PDF books (already available):
  - `03_matn_ar_rahabiyyah.pdf` - Shafi'i text (222 KB)
  - `07_mukhtasar_al_wasit.pdf` - Maliki text (502 KB)
  - `arabic_talkhis_fiqh_al_fraid.pdf` - Ibn Uthaymeen
- Creates embeddings for semantic search
- Builds BM25 keyword index

### Step 2: Initial Evaluation ✅
**Metrics Calculated:**
- Parsing success rate
- Validation success rate
- Average thinking quality score

**Expected Output:**
```
BASELINE RESULTS:
  Success Rate: XX.XX%
  Avg Thinking Quality: X.XX/1.0
```

### Step 3: Error Analysis ✅
**Analyzes:**
- Parsing failures
- Validation failures
- Low thinking quality cases
- Incorrect heir identification
- Retrieval issues

**Output Files:**
- `error_analysis_baseline.json`

### Step 4: Apply Improvements ✅
**Automated Suggestions For:**
- **Retrieval issues** → Increase top_k, adjust weights
- **Parsing failures** → Add few-shot examples
- **Low thinking quality** → Adjust temperature
- **Incorrect heirs** → Add more PDFs on heir rules

### Step 5: Iterative Improvement ✅
**Runs 3 iterations by default:**
- Evaluates on training set
- Analyzes errors each iteration
- Tracks best score
- Saves error reports

**Output Files:**
- `error_analysis_iter_1.json`
- `error_analysis_iter_2.json`
- `error_analysis_iter_3.json`

### Step 6: Final Evaluation ✅
**Evaluates on held-out test set**

**Expected Results:**
- Target: >99% success rate
- Great: >95% success rate
- Needs work: <95% success rate

**Output Files:**
- `rag_predictions.json`
- `training_history.json`
- `training_summary.json`

---

## Expected Training Outcomes

### Success Metrics
| Metric | Baseline | After Training | Target |
|--------|----------|----------------|--------|
| Success Rate | ~60-80% | ~90-99% | >99% |
| Thinking Quality | ~0.5 | ~0.7-0.9 | >0.8 |
| Parsing Success | ~80% | ~95%+ | >99% |

### When to Stop Training
- ✅ Success rate >99%: Ready for production
- ⭐ Success rate >95%: Good, minor tweaks needed
- 📋 Success rate <95%: Continue iterating

---

## Files Available in Your Project

### PDF Books (data/pdfs/)
1. `03_matn_ar_rahabiyyah.pdf` - Shafi'i classical text
2. `07_mukhtasar_al_wasit.pdf` - Maliki inheritance summary
3. `arabic_talkhis_fiqh_al_fraid.pdf` - Modern explanation

### Notebooks
- `QIAS_RAG_Colab.ipynb` - Basic setup and testing
- `QIAS_RAG_Training_Colab.ipynb` - **Full training workflow**
- `QIAS_RAG_Training_Local.ipynb` - Local training

### Scripts
- `colab_training.py` - Standalone training script (just created)
- `download_arabic_pdfs.py` - Download more Arabic books

---

## Next Steps

1. **Upload to Google Drive** (if using Colab)
2. **Open `QIAS_RAG_Training_Colab.ipynb`**
3. **Run all cells sequentially**
4. **Review error analysis files**
5. **Apply manual improvements if needed**
6. **Re-run training until >99% success**

## Troubleshooting

### Low Success Rate
- Check PDF files are loaded correctly
- Verify Ollama and Qwen3 are running
- Review `error_analysis_*.json` files

### Out of Memory
- Reduce batch size in `config/rag_config.yaml`
- Use smaller model: `qwen3:7b-thinking` instead of `30b`
- Clear GPU: `torch.cuda.empty_cache()`

### Parsing Failures
- Add more few-shot examples in `src/retrieval/prompt_builder.py`
- Adjust temperature: `0.0 → 0.1` in config
- Improve JSON schema instructions

---

## Summary

You now have:
- ✅ 3 Arabic PDF books on Islamic inheritance
- ✅ Complete RAG pipeline with Qwen3
- ✅ Training notebook ready for Colab
- ✅ Python script for local/Colab training
- ✅ Step-by-step guide following TRAINING_GUIDE.md

**Ready to start training!** 🚀
