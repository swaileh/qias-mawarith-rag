#!/usr/bin/env python3
"""
Test script to verify model loading works without authentication issues
"""

import sys
import os

# Add src to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def test_vector_store():
    """Test vector store initialization"""
    print("🧪 Testing Vector Store initialization...")

    try:
        from knowledge.vector_store import VectorStore

        print("Creating VectorStore...")
        vector_store = VectorStore()

        print("✅ VectorStore initialized successfully!")
        print(f"   Embedding model: {vector_store.vs_config['embedding_model']}")
        print(f"   Collection: {vector_store.collection_name}")

        return True

    except Exception as e:
        print(f"❌ VectorStore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reranker():
    """Test reranker initialization"""
    print("\n🧪 Testing Reranker initialization...")

    try:
        from retrieval.reranker import Reranker

        print("Creating Reranker...")
        reranker = Reranker()

        print("✅ Reranker initialized successfully!")
        print(f"   Enabled: {reranker.enabled}")
        if reranker.enabled:
            print(f"   Model: {reranker.retrieval_config.get('reranker_model', 'default')}")

        return True

    except Exception as e:
        print(f"❌ Reranker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Testing Model Loading Without Authentication Issues")
    print("=" * 60)

    all_good = True

    # Test vector store
    if not test_vector_store():
        all_good = False

    # Test reranker
    if not test_reranker():
        all_good = False

    print("\n" + "=" * 60)

    if all_good:
        print("🎉 All model loading tests passed!")
        print("Your RAG pipeline should now initialize without authentication issues.")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()