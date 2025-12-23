"""
Unified LLM Service - Ollama Primary with API Fallbacks.

Priority Chain:
1. Ollama (central-ollama:11434) - FREE, local, no rate limits
2. Groq (cloud) - FREE, fast, 100k tokens/day per key
3. Google Gemini (cloud) - FREE, unlimited with soft limits
"""

import os
import logging
from typing import Optional, Dict, Any

from .ollama_client import OllamaClient, get_ollama_client
from .groq_client import GroqClient, get_groq_client

logger = logging.getLogger(__name__)


class UnifiedLLMService:
    """
    Unified LLM Service with Ollama Primary + API Fallbacks.
    
    Automatically tries Ollama first (free, local), then falls back
    to Groq if Ollama is unavailable or errors.
    """
    
    def __init__(
        self,
        use_ollama: bool = None,
        ollama_host: str = None,
        ollama_port: int = None,
        ollama_model: str = None,
        groq_api_key: str = None,
        groq_model: str = "llama-3.3-70b",
    ):
        """Initialize unified LLM service.
        
        Args:
            use_ollama: Force enable/disable Ollama (defaults to USE_OLLAMA env)
            ollama_host: Ollama host
            ollama_port: Ollama port
            ollama_model: Ollama model
            groq_api_key: Groq API key for fallback
            groq_model: Groq model for fallback
        """
        self.use_ollama = use_ollama if use_ollama is not None else (
            os.getenv("USE_OLLAMA", "true").lower() == "true"
        )
        
        # Initialize Ollama client (primary)
        if self.use_ollama:
            self.ollama = get_ollama_client(
                host=ollama_host,
                port=ollama_port,
                model=ollama_model,
            )
        else:
            self.ollama = None
            
        # Initialize Groq client (fallback)
        self.groq = get_groq_client(
            api_key=groq_api_key,
            model=groq_model,
        )
        
        logger.info(
            f"UnifiedLLMService initialized: "
            f"Ollama={'enabled' if self.use_ollama else 'disabled'}, "
            f"Groq={'ready' if self.groq.client else 'no-key'}"
        )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text using Ollama first, then fallback to Groq.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Max tokens
            
        Returns:
            Generated text
        """
        # Try Ollama first (if enabled)
        if self.use_ollama and self.ollama:
            try:
                if await self.ollama.is_available():
                    result = await self.ollama.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    logger.info("✅ Generated via Ollama")
                    return result
                else:
                    logger.warning("Ollama not available, trying fallback...")
            except Exception as e:
                logger.warning(f"Ollama error: {e}, trying Groq fallback...")
        
        # Fallback to Groq
        try:
            result = await self.groq.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            logger.info("✅ Generated via Groq (fallback)")
            return result
        except Exception as e:
            logger.error(f"All LLM providers failed: {e}")
            raise RuntimeError(f"All LLM providers failed: {e}")
    
    async def embeddings(self, text: str) -> list:
        """Generate embeddings using Ollama (or empty list if unavailable)."""
        if self.use_ollama and self.ollama:
            try:
                return await self.ollama.embeddings(text)
            except Exception as e:
                logger.warning(f"Ollama embeddings error: {e}")
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get current LLM service status."""
        return {
            "ollama_enabled": self.use_ollama,
            "ollama_model": self.ollama.model if self.ollama else None,
            "groq_available": bool(self.groq.client),
            "groq_model": self.groq.model,
            "priority": ["ollama", "groq"] if self.use_ollama else ["groq"],
        }


# Global instance
_unified_llm: Optional[UnifiedLLMService] = None


def get_unified_llm(**kwargs) -> UnifiedLLMService:
    """Get or create global unified LLM service."""
    global _unified_llm
    if _unified_llm is None:
        _unified_llm = UnifiedLLMService(**kwargs)
    return _unified_llm


def reset_unified_llm():
    """Reset global unified LLM service."""
    global _unified_llm
    _unified_llm = None
