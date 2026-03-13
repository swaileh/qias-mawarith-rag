#!/usr/bin/env python3
"""
Test script to verify model loading works without Flash Attention
"""

import sys
import os

# Add src to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model.qwen_hf_client import QwenHFClient

def test_model_loading():
    print("🔧 Testing QwenHFClient initialization...")

    try:
        client = QwenHFClient()
        print("✅ QwenHFClient initialized successfully!")
        print(f"Model name: {client.model_name}")
        print(f"Thinking mode: {'Enabled' if client.enable_thinking else 'Disabled'}")
        print(f"Max tokens: {client.max_tokens}")
        print(f"Temperature: {client.temperature}")

        # Quick test generation
        print("\n🧪 Testing quick generation...")
        test_prompt = "ما هو نصيب الأم من الميراث؟"
        response = client.generate(test_prompt, max_tokens=100)
        print(f"✅ Generation successful! Response length: {len(response)} chars")
        print(f"Response preview: {response[:200]}...")

        return True

    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Model Loading")
    print("=" * 40)

    success = test_model_loading()

    if success:
        print("\n🎉 All tests passed! Your model is ready to use.")
    else:
        print("\n❌ Tests failed. Check the error messages above.")