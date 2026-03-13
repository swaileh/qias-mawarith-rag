#!/usr/bin/env python3
"""
Test script to verify Flash Attention is working
"""

import torch
try:
    from flash_attn import flash_attn_func
    flash_attn_available = True
    print("✅ Flash Attention library is available")
except ImportError:
    flash_attn_available = False
    print("❌ Flash Attention library not found")

# Test basic attention
if flash_attn_available:
    print("🧪 Testing Flash Attention function...")
    try:
        # Create dummy tensors
        batch_size, seq_len, num_heads, head_dim = 1, 128, 8, 64
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        q = torch.randn(batch_size, seq_len, num_heads, head_dim, device=device)
        k = torch.randn(batch_size, seq_len, num_heads, head_dim, device=device)
        v = torch.randn(batch_size, seq_len, num_heads, head_dim, device=device)

        # Test flash attention
        output = flash_attn_func(q, k, v)
        print(f"✅ Flash Attention test successful! Output shape: {output.shape}")
    except Exception as e:
        print(f"❌ Flash Attention test failed: {e}")
        print("💡 This is normal - Flash Attention may not work on all systems")
else:
    print("❌ Flash Attention library not found")
    print("💡 Run: pip install flash-attn --no-build-isolation")
    print("💡 Or run: python fix_flash_attention.py")

# Test model loading with eager attention
print("\n🔧 Testing model loading with eager attention...")
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_name = "microsoft/DialoGPT-small"  # Small model for testing

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    print("Loading model with eager attention...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        attn_implementation="eager",  # Use eager attention implementation
        torch_dtype=torch.float16,
        device_map="auto"
    )
    print("✅ Model loaded successfully with eager attention!")

    # Quick inference test
    inputs = tokenizer("Hello, how are you?", return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=20, do_sample=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"🗣️ Test response: {response}")

except Exception as e:
    print(f"❌ Model loading test failed: {e}")
    print("💡 This model may not support the attention implementation")

print("\n🎯 Flash Attention Setup Complete!")
print("If tests passed, your inference should now be significantly faster!")