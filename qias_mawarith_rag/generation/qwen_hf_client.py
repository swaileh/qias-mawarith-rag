"""
Qwen3.5 HuggingFace Client
Uses Qwen/Qwen3.5-9B with native thinking mode
"""

import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from typing import Dict
import yaml


class QwenHFClient:
    """Client for Qwen3.5 using HuggingFace Transformers directly"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.model_config = self.config['model']
        self.model_name = self.model_config.get('hf_model_name', 'Qwen/Qwen3.5-9B')
        self.max_tokens = self.model_config.get('max_new_tokens', 4096)
        self.temperature = self.model_config.get('temperature', 0.0)
        self.repetition_penalty = self.model_config.get('repetition_penalty', 1.0)
        self.top_p = self.model_config.get('top_p', 1.0)
        self.enable_thinking = self.model_config.get('enable_thinking', True)
        
        print(f"Loading {self.model_name} from HuggingFace...")
        print(f"Thinking mode: {'Enabled' if self.enable_thinking else 'Disabled'}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            padding_side="left"
        )
        
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,  # Changed from 4bit to 8bit for faster inference
            bnb_8bit_compute_dtype=torch.float16,  # Changed to float16 to avoid casting warning
            bnb_8bit_use_double_quant=True
        )
        
        # Load model with eager attention implementation (standard attention)
        print("🔄 Loading model with eager attention implementation...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            trust_remote_code=True,
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
            attn_implementation="eager",  # Use eager attention implementation
        )
        print("✅ Model loaded with eager attention")
        
        self.model.eval()
        print(f"✓ Model loaded: {self.model_name}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        repetition_penalty: float = None,
        top_p: float = None,
        enable_thinking: bool = None
    ) -> str:
        """Generate response. The prompt from rag_pipeline already contains
        system instructions, context, and format requirements in Arabic.
        We pass it as a single user message to preserve the full prompt structure."""
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if repetition_penalty is None:
            repetition_penalty = self.repetition_penalty
        if top_p is None:
            top_p = self.top_p
        if enable_thinking is None:
            enable_thinking = self.enable_thinking

        # The RAG pipeline's prompt_builder already includes all necessary instructions:
        # - Arabic system message with detailed expert context
        # - Retrieved context in Arabic
        # - Structured output instructions with exact JSON template
        # - Step-by-step thinking instructions
        # - The question
        # So we pass it as a single user message without overriding
        messages = [
            {"role": "user", "content": prompt}
        ]

        return self._generate_from_messages(messages, temperature, max_tokens, repetition_penalty, top_p, enable_thinking)
    
    def chat(
        self,
        messages: list[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        repetition_penalty: float = None,
        top_p: float = None,
        enable_thinking: bool = None
    ) -> str:
        """Chat-style generation"""
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if repetition_penalty is None:
            repetition_penalty = self.repetition_penalty
        if top_p is None:
            top_p = self.top_p
        if enable_thinking is None:
            enable_thinking = self.enable_thinking

        return self._generate_from_messages(messages, temperature, max_tokens, repetition_penalty, top_p, enable_thinking)
    
    def _generate_from_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        repetition_penalty: float,
        top_p: float,
        enable_thinking: bool
    ) -> str:
        """Core generation logic"""
        start_time = time.time()

        # Apply chat template with thinking mode enabled
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=self.enable_thinking
        )
        
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        gen_kwargs = {
            "max_new_tokens": max_tokens,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "use_cache": True,  # Enable KV cache
        }

        if temperature > 0:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = temperature
            gen_kwargs["top_p"] = top_p
            gen_kwargs["repetition_penalty"] = repetition_penalty
        else:
            gen_kwargs["do_sample"] = False
            gen_kwargs["repetition_penalty"] = repetition_penalty

        # Note: Thinking mode is enabled via chat template, but we'll also ensure tags in post-processing

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        generated_ids = outputs[0][inputs.input_ids.shape[1]:]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=False)

        elapsed = time.time() - start_time
        print(f"Generated {len(response)} chars in {elapsed:.1f}s")

        return response


if __name__ == "__main__":
    client = QwenHFClient()
    response = client.generate(
        "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟",
        max_tokens=500,
        enable_thinking=True
    )
    print(f"\nResponse:\n{response}")
