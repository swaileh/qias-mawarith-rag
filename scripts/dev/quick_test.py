#!/usr/bin/env python3
"""Quick test - just check if qwen3_5 is in CONFIG_MAPPING"""

import transformers
print(f"Transformers: {transformers.__version__}")

from transformers.models.auto.configuration_auto import CONFIG_MAPPING
print(f"qwen3_5 in mapping: {'qwen3_5' in CONFIG_MAPPING}")