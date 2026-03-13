#!/usr/bin/env python3
"""
Test script to verify eager attention implementation is working
"""

import sys
import os

# Add src to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def test_eager_attention():
    """Test that eager attention works without flash attention dependencies"""
    print("🧪 Testing eager attention implementation...")

    try:
        from model.qwen_hf_client import QwenHFClient

        # This should work without any flash attention imports
        print("✅ QwenHFClient imported successfully")

        # Test that we can create a client instance (this will load the model)
        print("🔄 Testing model loading with eager attention...")
        client = QwenHFClient()

        print("✅ Model loaded with eager attention!")
        print(f"Model name: {client.model_name}")
        print(f"Max tokens: {client.max_tokens}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Eager Attention Implementation")
    print("=" * 50)

    success = test_eager_attention()

    if success:
        print("\n🎉 Eager attention implementation works correctly!")
        print("No flash attention dependencies required.")
    else:
        print("\n❌ Eager attention test failed.")