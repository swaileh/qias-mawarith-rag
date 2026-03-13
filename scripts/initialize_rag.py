"""
Initialize RAG Pipeline for QIAS Islamic Law Reasoning
Local Windows version of the Colab initialization script
"""

import sys, os, yaml
from pathlib import Path

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def initialize_rag_pipeline():
    """Initialize the RAG pipeline with Qwen3.5-9B via HuggingFace"""

    config_path = PROJECT_ROOT / "config" / "rag_config.yaml"

    if not config_path.exists():
        print(f"ERROR: Config file not found at: {config_path}")
        return None

    print(f"Using config file: {config_path}")

    # Load and modify config for Qwen3.5 with thinking enabled
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Update model configuration
    config['model']['name'] = 'Qwen3.5-9B-HF'
    config['model']['hf_model_name'] = 'Qwen/Qwen3.5-9B'
    config['model']['client_type'] = 'huggingface'
    config['model']['enable_thinking'] = True

    # Save updated config
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print('Config updated: Qwen/Qwen3.5-9B via HuggingFace (thinking enabled)')

    # Add project root to Python path
    sys.path.insert(0, str(PROJECT_ROOT))

    try:
        from src.rag_pipeline import RAGPipeline

        print('\nLoading Qwen3.5 from HuggingFace...')
        pipeline = RAGPipeline(config_path=str(config_path))
        print('RAG Pipeline initialized successfully!')

        return pipeline

    except ImportError as e:
        print(f"ERROR: Failed to import RAG pipeline: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return None
    except Exception as e:
        print(f"ERROR: Failed to initialize RAG pipeline: {e}")
        return None

if __name__ == "__main__":
    pipeline = initialize_rag_pipeline()
    if pipeline:
        print("\nRAG Pipeline is ready for use!")
        print("You can now use pipeline.process_query() to ask questions about Islamic inheritance law.")
    else:
        print("\nFailed to initialize RAG pipeline. Check the errors above.")