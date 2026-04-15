# Quick Start Guide for Google Colab Training

## 📚 Two Notebooks Available

### 1. **QIAS_RAG_Colab.ipynb** - Full System Demo
- Complete RAG setup and inference
- Single question testing
- Batch evaluation
- 13 steps total
- **Use for**: Initial setup and testing

### 2. **QIAS_RAG_Training_Colab.ipynb** - Training Workflow ⭐
- Automated training loop
- Error analysis
- Iterative improvement
- Progress visualization
- 17 steps total
- **Use for**: Training and optimization to achieve >99%

---

## 🚀 Quick Start: Training in Google Colab

### Step 1: Prepare Your Files

Upload to Google Drive at `/MyDrive/QIAS_RAG/`:

```
QIAS_RAG/
├── qias_rag_thinking/          # This project folder
│   ├── src/
│   ├── config/
│   ├── requirements.txt
│   └── ...
├── data/
│   └── pdfs/                   # Your Islamic law PDF books
└── results/                    # Will be created automatically
```

### Step 2: Open Training Notebook

1. Go to Google Colab: https://colab.research.google.com/
2. Upload `notebooks/QIAS_RAG_Training_Colab.ipynb`
3. **Enable A100 GPU**: Runtime → Change runtime type → A100

### Step 3: Run All Cells

Click "Runtime → Run all" and wait. The notebook will:

1. ✅ Mount Google Drive
2. ✅ Install all dependencies
3. ✅ Install Ollama and download Qwen3-30B (~15 minutes)
4. ✅ Load your RAG system
5. ✅ Build knowledge base from PDFs
6. ✅ Run baseline evaluation
7. ✅ **Train iteratively** (3 iterations)
8. ✅ Show training progress charts
9. ✅ Run final test evaluation
10. ✅ Save all results to Drive

**Total time**: ~30-60 minutes (depending on dataset size)

---

## 📊 What Happens During Training?

### Iteration Loop (Automatic)

Each iteration:
1. **Run predictions** on training set
2. **Analyze errors**:
   - Parsing failures
   - Validation failures
   - Incorrect heirs
   - Poor retrieval
3. **Generate suggestions**:
   - Add more PDFs
   - Adjust retrieval parameters
   - Improve prompts
4. **Track improvement**

### After Training

You'll see:
- **Training progress chart**: Success rate over iterations
- **Error breakdown**: Types of errors reducing
- **Final metrics**: Test set performance
- **Next steps**: What to improve

---

## 📁 Output Files

Saved to `/MyDrive/QIAS_RAG/results/`:

```
results/
├── training_history.json          # Full training metrics
├── training_summary.json          # Quick summary
├── training_progress.png          # Visualization
├── error_analysis_iter_1.json     # Errors from iteration 1
├── error_analysis_iter_2.json     # Errors from iteration 2
├── error_analysis_iter_3.json     # Errors from iteration 3
├── rag_predictions.json           # Model predictions
└── evaluation_report.txt          # MIR-E evaluation
```

---

## 🎯 Achieving >99% Precision

### If Training Shows Low Success (<95%)

**Check** `error_analysis_iter_*.json` files:

1. **High parsing failures** → Check prompt formatting
2. **High validation failures** → Check JSON schema
3. **Incorrect heirs** → Add more Islamic law PDFs
4. **Poor retrieval** → Increase `top_k` or add PDFs

### Apply Improvements

**Option 1: Add More PDFs**
```python
# Upload more PDFs to Drive, then in notebook:
pipeline.build_knowledge_base('/content/drive/MyDrive/QIAS_RAG/data/pdfs')
```

**Option 2: Adjust Config**

Edit `config/rag_config.yaml` (upload modified version to Drive):

```yaml
retrieval:
  top_k: 10              # Increase from 5
  semantic_weight: 0.8   # Adjust weights
  keyword_weight: 0.2
  reranking:
    enabled: true
    top_k: 5
    min_score: 0.3       # Lower threshold
```

**Option 3: Improve Prompts**

Edit `src/retrieval/prompt_builder.py`:
- Add more few-shot examples
- Emphasize Islamic terminology
- Clarify JSON structure requirements

### Re-run Training

After improvements:
1. Reload notebook
2. Run all cells again
3. Compare new results with previous training_history.json

---

## 🔬 Optional: Model Fine-tuning

If RAG training alone doesn't achieve >99%, try fine-tuning:

### In the Training Notebook (Last cells):

```python
# Install fine-tuning dependencies
!pip install -q unsloth trl

# Prepare data and generate training script
from src.training.fine_tune import FineTuner
tuner = FineTuner()
tuner.prepare_training_data(full_dataset[:100])
tuner.save_training_script()

# Run training (takes ~1-2 hours)
!python train_qwen3.py
```

---

## 💡 Tips for Google Colab

### Memory Management
- Use A100 (40GB) for 30B model
- Or use T4 with 7B model: `qwen3:7b-thinking`
- Clear memory if needed: `torch.cuda.empty_cache()`

### Session Management
- Colab sessions timeout after 12 hours
- Save results to Drive frequently
- Can resume from any step

### Cost
- A100 requires Colab Pro (~$10/month)
- Or rent time on demand
- Free T4 available but slower

---

## 🆘 Troubleshooting

### "Ollama not found"
```bash
# In Colab cell:
!curl -fsSL https://ollama.com/install.sh | sh
!nohup ollama serve > ollama.log 2>&1 &
!sleep 5
```

### "Model download failed"
```bash
# Check Ollama status:
!ollama list

# Pull model manually:
!ollama pull qwen3:30b-thinking
```

### "Knowledge base empty"
Upload PDFs to exact Drive path:
`/content/drive/MyDrive/QIAS_RAG/data/pdfs/`

### "Out of memory"
Reduce model size or batch size:
```yaml
# In rag_config.yaml
model:
  name: "qwen3:7b-thinking"  # Smaller model
```

---

## ✅ Success Criteria

Your training is successful when:
- ✅ Success rate >99% on test set
- ✅ MIR-E score >0.99
- ✅ Avg thinking quality >0.7
- ✅ <1% parsing/validation failures

Then you're ready for full evaluation on the entire dataset!

---

## 📞 Support

- QIAS 2026 Task: https://sites.google.com/view/qias2026
- Issues: Check error_analysis_*.json files
- Questions: Review TRAINING_GUIDE.md

**Good luck achieving >99% precision! 🎯**
