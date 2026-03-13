#!/usr/bin/env python3
"""
Test the model without Flash Attention to ensure basic functionality works
"""

import time
from src.model.qwen_hf_client import QwenHFClient

def test_basic_inference():
    print("🧪 Testing basic model inference (without Flash Attention)")
    print("=" * 60)

    try:
        print("🔧 Loading Qwen model...")
        client = QwenHFClient()

        print("📝 Testing with sample question...")
        test_prompt = "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"

        print(f"Question: {test_prompt}")

        start_time = time.time()
        response = client.generate(test_prompt, max_tokens=256, enable_thinking=False)
        elapsed = time.time() - start_time

        chars_per_sec = len(response) / elapsed
        tokens_per_sec = len(response) / 3.5 / elapsed  # Rough Arabic token estimate

        print("
📊 Performance:"        print(".2f"        print(".1f"        print(".1f"
        print(f"📄 Response length: {len(response)} characters")

        print("
📝 Sample response:"        print("-" * 40)
        print(response[:300] + "..." if len(response) > 300 else response)

        if tokens_per_sec > 10:
            print("
✅ Basic inference working well!"        elif tokens_per_sec > 5:
            print("
⚠️ Basic inference working (acceptable speed)"        else:
            print("
❌ Basic inference is very slow - check setup"
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_inference()
    if success:
        print("
🎉 Your RAG system should work now!"        print("💡 If you want faster inference, try installing Flash Attention later")
    else:
        print("
❌ Basic inference failed - check your setup"        print("🔍 Check that all dependencies are installed correctly")