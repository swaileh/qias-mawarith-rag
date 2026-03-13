#!/usr/bin/env python3
"""
Quick test for the optimized Qwen3.5 HF client
"""

import time
from src.model.qwen_hf_client import QwenHFClient

print("🔧 Testing optimized Qwen3.5 HF client...")
client = QwenHFClient()

prompt = "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"
print(f"📝 Prompt: {prompt}")
print("⚙️  Settings: max_tokens=1024, thinking=False")

start_time = time.time()
response = client.generate(prompt, max_tokens=1024, enable_thinking=False)
elapsed = time.time() - start_time

chars_per_sec = len(response) / elapsed
tokens_per_sec = len(response) / 3.5 / elapsed  # Rough Arabic token estimate

print(f"\n📊 Performance:")
print(f"   Time: {elapsed:.2f}s")
print(f"   Speed: {chars_per_sec:.1f} chars/sec, {tokens_per_sec:.1f} tokens/sec")
print(f"   Length: {len(response)} characters")

print(f"\n📄 Response (first 300 chars):")
print("-" * 50)
print(response[:300] + "..." if len(response) > 300 else response)

if tokens_per_sec > 20:
    print("\n✅ Performance looks good!")
else:
    print("\n⚠️  Still slow - may need further optimization")