#!/usr/bin/env python3
"""Debug script to test Qwen3.5 model loading step by step"""

import sys
print(f"Python version: {sys.version}")

try:
    import transformers
    print(f"Transformers version: {transformers.__version__}")
except ImportError as e:
    print(f"Failed to import transformers: {e}")
    sys.exit(1)

try:
    from transformers.models.auto.configuration_auto import CONFIG_MAPPING
    print(f"CONFIG_MAPPING has {len(CONFIG_MAPPING)} model types")

    if "qwen3_5" in CONFIG_MAPPING:
        print("✓ qwen3_5 found in CONFIG_MAPPING!")
        print(f"Config class: {CONFIG_MAPPING['qwen3_5']}")
    else:
        print("✗ qwen3_5 NOT found in CONFIG_MAPPING")
        qwen_types = [k for k in CONFIG_MAPPING.keys() if 'qwen' in k.lower()]
        print(f"Available Qwen types: {qwen_types}")

except Exception as e:
    print(f"Error checking CONFIG_MAPPING: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nTrying to load AutoConfig...")
    from transformers import AutoConfig
    config = AutoConfig.from_pretrained('Qwen/Qwen3.5-9B', trust_remote_code=True)
    print(f"✓ Config loaded! Model type: {config.model_type}")
except Exception as e:
    print(f"✗ Failed to load config: {e}")
    import traceback
    traceback.print_exc()