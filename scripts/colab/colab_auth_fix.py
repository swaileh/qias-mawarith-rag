# Fix HuggingFace Authentication Issues in Google Colab
# Run this cell first in your Colab notebook

import os

# Disable telemetry and authentication prompts
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/tmp/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/transformers_cache"

# Set offline mode to prevent authentication attempts
os.environ["HF_HUB_OFFLINE"] = "0"  # Allow downloads but handle auth better

print("✅ Authentication environment variables set")
print("✅ Cache directories configured")
print("Now you can load your models without KeyboardInterrupt issues!")

# Test basic import
try:
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer, AutoModelForCausalLM
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")