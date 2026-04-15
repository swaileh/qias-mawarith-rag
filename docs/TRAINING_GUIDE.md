"""
Training and Testing Guide for QIAS RAG System
"""

# Training and Testing Guide

## Overview

The QIAS RAG system supports **two types of "training"**:

1. **RAG System Training** (No fine-tuning required) - Iterative improvement via feedback loop
2. **Model Fine-tuning** (Optional) - LoRA fine-tuning of Qwen3 on QIAS dataset

---

## 1. RAG System Training (Recommended)

### What is RAG Training?

RAG training **doesn't modify the model weights**. Instead, it:
- Analyzes errors in predictions
- Suggests improvements to prompts, retrieval, and knowledge base
- Iteratively refines the system configuration

### How to Train the RAG System

#### Step 1: Run Initial Evaluation

```python
from src.rag_pipeline import RAGPipeline
import json

# Initialize pipeline
pipeline = RAGPipeline()

# Build knowledge base (if not done)
pipeline.build_knowledge_base('data/pdfs')

# Load dev dataset
with open('path/to/qias_dev_set.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Run batch evaluation
results = pipeline.batch_query(dataset[:50], save_results=True)
```

#### Step 2: Analyze Errors with Feedback Loop

```python
from src.training.feedback_loop import FeedbackLoop

# Initialize feedback loop
feedback = FeedbackLoop()

# Analyze errors
error_analysis = feedback.analyze_errors(results, dataset[:50])

# Get improvement suggestions
suggestions = feedback.suggest_improvements(error_analysis)

# Print suggestions
for suggestion in suggestions:
    print(suggestion)

# Save error report
feedback.save_error_report(error_analysis)
```

#### Step 3: Apply Improvements

Based on suggestions, you might:

**If retrieval is poor:**
```python
# Add more PDFs to knowledge base
pipeline.build_knowledge_base('data/more_pdfs')

# Or adjust retrieval parameters in config/rag_config.yaml:
retrieval:
  top_k: 10  # Increase from 5
  semantic_weight: 0.8  # Adjust weights
  keyword_weight: 0.2
```

**If prompts need improvement:**
```python
# Edit prompt_builder.py to:
# - Add more few-shot examples
# - Refine structured output instructions
# - Emphasize specific Islamic law concepts
```

**If thinking quality is low:**
```python
# Add examples with better reasoning in prompt
# Increase temperature slightly: temperature: 0.1
```

#### Step 4: Iterative Improvement Loop

```python
# Run automatic iterative improvement
history = feedback.iterative_improvement(
    pipeline=pipeline,
    dataset=dataset[:50],
    max_iterations=3
)

print(f"Best score: {history['best_score']:.2%}")
print(f"Best iteration: {history['best_iteration']}")
```

---

## 2. Model Fine-tuning (Optional)

### When to Fine-tune?

Fine-tune only if:
- RAG system achieves >95% but you need >99%
- Specific error patterns persist despite RAG improvements
- You have sufficient GPU resources (A100 recommended)

### How to Fine-tune Qwen3

#### Step 1: Prepare Training Data

```python
from src.training.fine_tune import FineTuner
import json

# Load QIAS dataset
with open('path/to/qias_full_dataset.json', 'r', encoding='utf-8') as f:
    full_dataset = json.load(f)

# Initialize fine-tuner
tuner = FineTuner()

# Convert to training format
tuner.prepare_training_data(
    dataset=full_dataset,
    output_file='training_data.jsonl'
)
```

#### Step 2: Generate Training Script

```python
# Create training script
tuner.save_training_script('train_qwen3.py')
```

#### Step 3: Install Requirements

```bash
pip install unsloth
pip install trl
```

#### Step 4: Run Training

```bash
python train_qwen3.py
```

This will:
- Load Qwen2.5-7B-Instruct (smaller than 30B for training)
- Apply LoRA adapters
- Train for 100 steps (adjust based on dataset size)
- Save LoRA weights to `qwen3_qias_lora/`

#### Step 5: Use Fine-tuned Model

After training, modify `config/rag_config.yaml`:

```yaml
model:
  name: "path/to/qwen3_qias_lora"  # Point to fine-tuned model
  ollama_base_url: "http://localhost:11434"
```

**Note:** You'll need to convert LoRA to Ollama format or use Hugging Face inference.

---

## 3. Testing the System

### Unit Tests

Run all component tests:

```bash
# Run full test suite
pytest tests/test_pipeline.py -v

# Run specific test class
pytest tests/test_pipeline.py::TestOutputParser -v

# Run with coverage
pytest tests/test_pipeline.py --cov=src --cov-report=html
```

### Integration Testing

Test complete pipeline:

```python
from src.rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline()

# Test single question
question = "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"
result = pipeline.query(question)

# Verify
assert result['parsed_output']['validation_success']
assert result['thinking_quality']['quality_score'] > 0.5

print("✓ Integration test passed!")
```

### End-to-End Testing in Colab

1. Open `notebooks/QIAS_RAG_Colab.ipynb`
2. Run cells 1-9 (setup and initialization)
3. Run cell 9 (single question test)
4. Verify output is valid
5. Run cell 10 (batch evaluation on 10 cases)
6. Check success rate

---

## 4. Evaluation Metrics

### MIR-E Score

```python
from src.evaluation.mir_e_wrapper import MIREvaluator

evaluator = MIREvaluator()

# Evaluate predictions
results = evaluator.evaluate_predictions(
    predictions_file='results/rag_predictions.json',
    reference_file='path/to/reference.json'
)

print(f"MIR-E Score: {results['average_mir_e']:.4f}")
print(f"Heirs Subscore: {results['subscores']['heirs']:.4f}")
print(f"Shares Subscore: {results['subscores']['shares']:.4f}")
```

### Custom Metrics

```python
# Success rate
success_rate = sum(
    1 for r in results 
    if r['parsed_output']['validation_success']
) / len(results)

# Thinking quality
avg_thinking_quality = sum(
    r['thinking_quality']['quality_score']
    for r in results
    if r.get('thinking_quality')
) / len(results)

print(f"Success Rate: {success_rate:.2%}")
print(f"Avg Thinking Quality: {avg_thinking_quality:.2f}")
```

---

## Summary

**Recommended Workflow:**

1. ✅ **Build knowledge base** with PDFs
2. ✅ **Run initial evaluation** on dev set
3. ✅ **Analyze errors** with feedback loop
4. ✅ **Apply improvements** (add PDFs, adjust config, refine prompts)
5. ✅ **Iterate** until >99% precision
6. ⚠️ **Fine-tune** (only if needed and resources available)
7. ✅ **Test** on full test set
8. ✅ **Deploy** to production

**Key Files:**
- Training: `src/training/feedback_loop.py`
- Fine-tuning: `src/training/fine_tune.py`
- Testing: `tests/test_pipeline.py`
- Config: `config/rag_config.yaml`
