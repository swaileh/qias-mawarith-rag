"""
Unsloth model client.
Uses Unsloth for efficient local inference with Qwen-style models.
"""

import time
from typing import Dict

import torch
import yaml


class UnslothClient:
    """Client for running inference via Unsloth."""

    def __init__(self, config_path: str = "config/rag_config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.model_config = self.config["model"]
        self.model_name = self.model_config.get(
            "unsloth_model_name",
            self.model_config.get("hf_model_name", "Qwen/Qwen3.5-9B"),
        )
        self.max_tokens = self.model_config.get("max_new_tokens", 1024)
        self.temperature = self.model_config.get("temperature", 0.0)
        self.repetition_penalty = self.model_config.get("repetition_penalty", 1.0)
        self.top_p = self.model_config.get("top_p", 1.0)
        self.context_window = self.model_config.get("context_window", 8192)
        self.load_in_4bit = self.model_config.get("unsloth_load_in_4bit", True)

        try:
            from unsloth import FastLanguageModel
        except ImportError as exc:
            raise ImportError(
                "Unsloth is not installed. Install with: pip install unsloth"
            ) from exc

        print(f"Loading {self.model_name} via Unsloth...")
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.model_name,
            max_seq_length=self.context_window,
            dtype=None,
            load_in_4bit=self.load_in_4bit,
        )
        FastLanguageModel.for_inference(self.model)
        print(f"Model loaded with Unsloth: {self.model_name}")

    def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        repetition_penalty: float = None,
        top_p: float = None,
    ) -> str:
        """Generate text from a full prompt string."""
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if repetition_penalty is None:
            repetition_penalty = self.repetition_penalty
        if top_p is None:
            top_p = self.top_p

        messages = [{"role": "user", "content": prompt}]
        return self._generate_from_messages(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            repetition_penalty=repetition_penalty,
            top_p=top_p,
        )

    def chat(
        self,
        messages: list[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        repetition_penalty: float = None,
        top_p: float = None,
    ) -> str:
        """Generate from chat messages."""
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if repetition_penalty is None:
            repetition_penalty = self.repetition_penalty
        if top_p is None:
            top_p = self.top_p

        return self._generate_from_messages(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            repetition_penalty=repetition_penalty,
            top_p=top_p,
        )

    def _generate_from_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        repetition_penalty: float,
        top_p: float,
    ) -> str:
        start_time = time.time()

        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt_text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            prompt_text = messages[-1]["content"]

        inputs = self.tokenizer(prompt_text, return_tensors="pt").to(self.model.device)

        gen_kwargs = {
            "max_new_tokens": max_tokens,
            "use_cache": True,
        }
        if temperature > 0:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = temperature
            gen_kwargs["top_p"] = top_p
            gen_kwargs["repetition_penalty"] = repetition_penalty
        else:
            gen_kwargs["do_sample"] = False
            gen_kwargs["repetition_penalty"] = repetition_penalty

        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)

        generated_ids = outputs[0][inputs.input_ids.shape[1] :]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=False)
        elapsed = time.time() - start_time
        print(f"Generated {len(response)} chars in {elapsed:.1f}s")
        return response
