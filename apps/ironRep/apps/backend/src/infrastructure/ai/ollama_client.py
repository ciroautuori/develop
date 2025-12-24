"""
Ollama LLM Client - Centralized integration with local Ollama service.

OLLAMA is PRIMARY for:
- Zero cost (local)
- No rate limits
- Privacy (data stays local)

Falls back to Groq if Ollama unavailable.
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, AsyncIterator

logger = logging.getLogger(__name__)


class OllamaClient:
    """Centralized Ollama client - Primary LLM provider."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """Initialize Ollama client.
        
        Args:
            host: Ollama host (defaults to OLLAMA_HOST env var or 'central-ollama')
            port: Ollama port (defaults to OLLAMA_PORT env var or 11434)
            model: Model to use (defaults to OLLAMA_MODEL env var or 'llama3.2:latest')
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
        """
        self.host = host or os.getenv("OLLAMA_HOST", "central-ollama")
        self.port = int(port or os.getenv("OLLAMA_PORT", "11434"))
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b-instruct")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = f"http://{self.host}:{self.port}"
        
        logger.info(f"Ollama client initialized: {self.base_url} ({self.model})")

    async def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text completion using Ollama.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens,
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                content = data.get("message", {}).get("content", "")
                
                logger.info(
                    "ollama_generation_success",
                    extra={
                        "model": self.model,
                        "prompt_length": len(prompt),
                        "response_length": len(content),
                    }
                )
                
                return content
                
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise RuntimeError(f"Ollama generation failed: {e}")

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming text completion using Ollama."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens,
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    import json
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                content = data.get("message", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            yield f"[Ollama error: {e}]"

    async def embeddings(self, text: str) -> list:
        """Generate embeddings using Ollama."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": os.getenv("OLLAMA_EMBED_MODEL", "all-minilm"),
                        "prompt": text
                    }
                )
                response.raise_for_status()
                return response.json().get("embedding", [])
        except Exception as e:
            logger.error(f"Ollama embeddings error: {e}")
            return []

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model."""
        return {
            "provider": "Ollama",
            "host": self.host,
            "port": self.port,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "features": ["chat", "streaming", "embeddings", "local", "free"],
        }


# Global instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client(**kwargs) -> OllamaClient:
    """Get or create global Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient(**kwargs)
    return _ollama_client


def reset_ollama_client():
    """Reset global Ollama client instance."""
    global _ollama_client
    _ollama_client = None
