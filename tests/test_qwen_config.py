#!/usr/bin/env python3
"""Test script to check Qwen3.5 model configuration loading"""

from transformers import AutoConfig

try:
    print("Testing Qwen3.5 config loading...")
    config = AutoConfig.from_pretrained('Qwen/Qwen3.5-9B', trust_remote_code=True)
    print(f"✓ Config loaded successfully! Model type: {config.model_type}")
    print(f"✓ Model config: {config}")
except Exception as e:
    print(f"✗ Error loading config: {e}")
    raise