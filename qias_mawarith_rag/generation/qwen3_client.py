"""
Qwen3/3.5 Model Client
Interface for interacting with Qwen3/3.5 thinking models via Ollama
"""

import yaml
import json
import requests
from typing import Dict, Any, Generator
import time


class Qwen3Client:
    """Client for Qwen3/3.5 thinking models via Ollama"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize Qwen3 client"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.model_config = self.config['model']
        self.model_name = self.model_config.get('name', 'qwen3.5:9b')
        self.base_url = self.model_config.get('ollama_base_url', 'http://localhost:11434')
        self.max_tokens = self.model_config.get('max_new_tokens', 4096)
        self.temperature = self.model_config.get('temperature', 0.0)
        self.context_window = self.model_config.get('context_window', 32768)
        # Enable thinking mode by default for Qwen3.5 models
        self.think = self.model_config.get('think', True)
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model_name in model_names:
                    print(f"✓ Connected to Ollama. Model {self.model_name} available.")
                    return True
                else:
                    print(f"⚠ Ollama connected but {self.model_name} not found.")
                    print(f"Available models: {model_names}")
                    return False
            else:
                print("⚠ Ollama server not responding properly")
                return False
        except Exception as e:
            print(f"⚠ Cannot connect to Ollama: {e}")
            print(f"Make sure Ollama is running on {self.base_url}")
            return False
    
    def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
        think: bool = None
    ) -> str:
        """Generate response from Qwen3/3.5 model
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (default from config)
            max_tokens: Maximum tokens to generate (default from config)
            stream: Whether to stream output
            think: Enable thinking mode (default from config)
        
        Returns:
            Generated text
        """
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if think is None:
            think = self.think
        
        # Prepare request
        # Note: Qwen3.5 thinking is enabled via system prompt or /think tag, not API option
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": self.context_window
            }
        }
        
        try:
            if stream:
                return self._generate_stream(payload)
            else:
                return self._generate_sync(payload)
        except Exception as e:
            print(f"Generation error: {e}")
            raise
    
    def _generate_sync(self, payload: Dict[str, Any]) -> str:
        """Synchronous generation"""
        start_time = time.time()
        
        print(f"  → Sending request to Ollama ({payload['model']})...")
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        result = response.json()
        generated_text = result.get('response', '')
        
        # Debug: Show raw response info
        elapsed = time.time() - start_time
        done_reason = result.get('done_reason', 'unknown')
        print(f"  ← Response received: {len(generated_text)} chars in {elapsed:.2f}s (done_reason: {done_reason})")
        
        if not generated_text:
            print("  ⚠ Warning: Empty response from model")
            print(f"  Debug: {result}")
        
        return generated_text
    
    def _generate_stream(self, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """Streaming generation"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=True,
            timeout=300
        )
        
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'response' in chunk:
                    yield chunk['response']
                
                if chunk.get('done', False):
                    break
    
    def chat(
        self,
        messages: list[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        think: bool = None
    ) -> str:
        """Chat-style generation
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            think: Enable thinking mode (default from config)
        
        Returns:
            Generated response
        """
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
        if think is None:
            think = self.think
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": self.context_window
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.text}")
            
            result = response.json()
            return result['message']['content']
        
        except Exception as e:
            print(f"Chat error: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.model_name},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"Error getting model info: {e}")
            return {}


if __name__ == "__main__":
    # Test the client
    client = Qwen3Client()
    
    # Test with simple prompt
    test_prompt = "اشرح مفهوم الفرائض في الإسلام بإيجاز."
    
    try:
        response = client.generate(test_prompt, max_tokens=200)
        print(f"\nTest response:\n{response[:500]}")
    except Exception as e:
        print(f"Test failed: {e}")
