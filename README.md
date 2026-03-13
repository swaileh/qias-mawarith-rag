# QIAS 2026 RAG System with Qwen3.5

**Islamic Inheritance Reasoning with Retrieval Augmented Generation**

A complete RAG (Retrieval-Augmented Generation) system for the QIAS 2026 shared task, using Qwen3.5 via HuggingFace Transformers for Islamic inheritance law (علم المواريث) reasoning.

## Features

- **Qwen3.5-9B-Instruct** via HuggingFace Transformers (no Ollama needed)
- **4-bit quantization** for efficient GPU memory usage (~6.6GB)
- **ChromaDB** vector store with Arabic embeddings
- **Hybrid retrieval** (semantic + BM25 keyword search)
- **Thinking mode** for step-by-step reasoning
- **MIR-E evaluation** framework support

## Quick Start

### Google Colab (Recommended)

1. **Upload project to Google Drive**:
   ```
   MyDrive/QIAS26/
   └── qias_rag_thinking/
       ├── src/
       ├── config/
       ├── notebooks/
       └── data/pdfs/
   ```

2. **Open the notebook**:
   - Use `notebooks/QIAS_RAG_HF.ipynb` (HuggingFace version)

3. **Set GPU runtime**:
   - Runtime → Change runtime type → A100 GPU (or T4)

4. **Set up HuggingFace authentication** (optional but recommended):
   - Get token from: https://huggingface.co/settings/tokens
   - Add to Colab secrets: `HF_TOKEN` = your_token
   - Or use `.env` file for local development

5. **Run cells sequentially**:
   - Install dependencies
   - Mount Drive
   - Authenticate with HuggingFace
   - Initialize pipeline (downloads Qwen3.5 automatically)
   - Run evaluation

### Local Installation

```bash
# Clone repository
git clone https://github.com/your-repo/qias_rag_thinking.git
cd qias_rag_thinking

# Set up HuggingFace authentication (recommended)
cp .env.example .env
# Edit .env and set HF_TOKEN=your_huggingface_token

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python -m notebooks.QIAS_RAG_HF
```

## Project Structure

```
qias_rag_thinking/
├── config/                 # Configuration
│   └── rag_config.yaml
├── data/                   # PDFs, JSON datasets, vector DB
│   └── pdfs/
├── docs/                   # Additional documentation
│   ├── COLAB_*.md, TRAINING_GUIDE.md, etc.
│   └── PROJECT_ORGANIZATION.md  # How this repo is organized
├── notebooks/              # Jupyter notebooks (Colab & local)
│   ├── QIAS_RAG_HF.ipynb
│   ├── QIAS_RAG_Colab.ipynb
│   └── Multi_Source_RAG_Evaluation_*.ipynb
├── outputs/                # Generated artifacts (results, reports)
│   ├── evaluation/
│   └── reports/
├── scripts/                # Runnable entry points (run from project root)
│   ├── train.py, initialize_rag.py, download_*.py
│   ├── colab/              # Colab-specific helpers
│   ├── evaluation/         # Evaluation & report scripts
│   └── dev/                # Debug, one-off, verification scripts
├── src/                    # Core library code
│   ├── rag_pipeline.py
│   ├── model/, knowledge/, retrieval/, evaluation/, training/
│   └── ...
├── tests/                  # Unit and integration tests
├── requirements.txt
└── README.md
```

**Run any script from the project root**, e.g.:
```bash
python scripts/train.py
python scripts/initialize_rag.py
python scripts/evaluation/evaluate_relevance.py
python scripts/dev/verify_setup.py
```

## Configuration

Edit `config/rag_config.yaml`:

```yaml
model:
  client_type: "huggingface"          # Use HuggingFace (not Ollama)
  hf_model_name: "Qwen/Qwen3.5-9B-Instruct"
  max_new_tokens: 4096
  temperature: 0.0
  enable_thinking: true                 # Enable step-by-step reasoning

vector_store:
  embedding_model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  chunk_size: 512
  chunk_overlap: 128
```

## Model Details

- **Model**: Qwen/Qwen3.5-9B-Instruct
- **Size**: ~6.6GB (4-bit quantized)
- **Context**: 32K tokens
- **Features**: Thinking mode, Arabic support, Vision capability
- **Loading**: Downloads automatically from HuggingFace Hub on first run

## Authentication Setup

For optimal performance and higher rate limits, set up HuggingFace authentication:

### Google Colab
1. Go to `Runtime > Secrets`
2. Add secret: `HF_TOKEN` = your_token
3. The notebook will automatically use this token

### Local Development
1. Copy `.env.example` to `.env`
2. Set `HF_TOKEN=your_huggingface_token_here`
3. Or run: `export HF_TOKEN=your_token`

### Manual Setup
- Run `huggingface-cli login` in terminal
- Or paste token directly in the notebook

**Get your token from**: https://huggingface.co/settings/tokens

*Note: Without authentication, you'll have lower rate limits but can still use the models.*

## Requirements

- Python 3.10+
- CUDA-capable GPU (recommended: A100, minimum: T4)
- 10GB+ GPU memory
- ~50GB Google Drive storage (for Colab)

## Dependencies

Key packages:
- `transformers>=5.0.0` - HuggingFace transformers
- `bitsandbytes>=0.45.0` - 4-bit quantization
- `accelerate>=1.0.0` - Model loading
- `chromadb>=1.5.0` - Vector database
- `sentence-transformers>=5.0.0` - Embeddings

See `requirements.txt` for complete list.

## Usage

### Basic Query

```python
from src.rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline(config_path="config/rag_config.yaml")

# Build knowledge base
pipeline.build_knowledge_base("./data/pdfs")

# Query
result = pipeline.query(
    "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟",
    top_k=5
)

# View thinking process
print(result['parsed_output']['thinking'])

# View structured answer
print(result['parsed_output']['structured_output'])
```

### Training Workflow

See `scripts/colab/colab_training.py` or `notebooks/QIAS_RAG_Training_Colab.ipynb` for complete training workflow.

## Evaluation

The system supports MIR-E evaluation framework:

```python
from src.evaluation.mir_e_wrapper import MIREvaluator

evaluator = MIREvaluator()
results = evaluator.evaluate_predictions(
    predictions_file="results/rag_predictions.json",
    reference_file="data/qias_dataset.json"
)

print(f"MIR-E Score: {results['average_mir_e']:.4f}")
```

## Troubleshooting

### Authentication Issues
- **"HF_TOKEN timed out"**: You're not in actual Colab UI - use manual token input or `.env` file
- **"No HF_TOKEN found"**: Set up authentication using one of the methods above
- **Rate limits exceeded**: Set up HuggingFace token for higher limits

### Model Loading Issues
- **Out of memory**: Reduce `max_new_tokens` or use smaller model
- **Slow loading**: First download takes 5-10 minutes, subsequent loads are faster
- **Download fails**: Check HuggingFace Hub access and internet connection

### GPU Issues
- **CUDA out of memory**: Enable 4-bit quantization (already default)
- **No GPU detected**: Check CUDA installation and GPU availability

### Performance Issues
- **Slow inference**: Use A100 GPU instead of T4
- **Low accuracy**: Add more PDF books to knowledge base

## Documentation

- `docs/COLAB_TRAINING_USAGE.md` - Colab usage guide
- `docs/TRAINING_GUIDE.md` - Complete training workflow
- `docs/QIAS_TRAIN_SET_ENHANCEMENT_REPORT.md` - Dataset enhancement report
- `docs/PROJECT_ORGANIZATION.md` - How the workspace is organized

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**. You may use, share, and adapt it for non-commercial purposes with attribution. Commercial use is not permitted. See the [LICENSE](LICENSE) file for the full text.

## Contact

**Wassim Swaileh**
- `web page:` https://swaileh.github.io/index.html
---


