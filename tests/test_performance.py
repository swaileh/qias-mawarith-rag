#!/usr/bin/env python3
"""
Quick performance test to measure generation speed improvements
"""

import time
import torch
from src.model.qwen_hf_client import QwenHFClient

def test_generation_speed():
    print("🚀 Testing generation speed with optimized settings...")
    print("=" * 60)

    # Check GPU
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print()

    client = QwenHFClient()

    # Test prompt
    test_prompt = "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"

    print("📝 Test Prompt:"    print(f"   {test_prompt}")
    print("\n⚙️  Settings: max_tokens=1024, thinking=False, 8-bit quantization")

    print("\n⏳ Generating response...")
    start_time = time.time()
    response = client.generate(test_prompt, max_tokens=1024, enable_thinking=False)
    elapsed = time.time() - start_time

    chars_generated = len(response)
    chars_per_sec = chars_generated / elapsed

    print(f"\n📊 Results:")
    print(f"   Characters generated: {chars_generated:,}")
    print(f"   Time taken: {elapsed:.2f}s")
    print(f"   Speed: {chars_per_sec:.1f} chars/sec")

    # Estimate tokens (rough approximation for Arabic text)
    tokens_approx = chars_generated / 3.5  # Better estimate for Arabic
    tokens_per_sec = tokens_approx / elapsed
    print(f"   Estimated tokens/sec: {tokens_per_sec:.1f}")

    print("\n🎯 Performance Rating:")
    if tokens_per_sec > 100:
        print("   ✅ Excellent! (>100 tokens/sec)")
    elif tokens_per_sec > 50:
        print("   ✅ Good! (50-100 tokens/sec)")
    elif tokens_per_sec > 20:
        print("   ⚠️  Acceptable (20-50 tokens/sec)")
    else:
        print("   ❌ Still slow (<20 tokens/sec) - needs more optimization")

    print("\n💡 Expected improvement over old settings:")
    print("   Before: ~7 tokens/sec (431s for 12K chars)")
    print(f"   After:  ~{tokens_per_sec:.0f} tokens/sec (estimated)")

    # Show sample output
    print(f"\n📄 Sample output (first 200 chars):")
    print("-" * 40)
    print(response[:200] + "..." if len(response) > 200 else response)

if __name__ == "__main__":
    test_generation_speed()