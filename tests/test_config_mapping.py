#!/usr/bin/env python3
"""Test script to check if qwen3_5 is in CONFIG_MAPPING"""

try:
    from transformers.models.auto.configuration_auto import CONFIG_MAPPING
    print(f"Available model types in CONFIG_MAPPING: {len(CONFIG_MAPPING)} total")

    if "qwen3_5" in CONFIG_MAPPING:
        print("✓ qwen3_5 is supported in CONFIG_MAPPING!")
        print(f"Config class: {CONFIG_MAPPING['qwen3_5']}")
    else:
        print("✗ qwen3_5 not found in CONFIG_MAPPING")
        print("Available model types:")
        for key in sorted(CONFIG_MAPPING.keys()):
            if "qwen" in key.lower():
                print(f"  - {key}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()