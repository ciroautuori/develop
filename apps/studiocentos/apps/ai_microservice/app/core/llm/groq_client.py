"""
Groq LLM Client - Centralized integration with Groq API using Llama models.

GROQ is FAST and FREE with powerful Llama models!

Migrated from legacy components/ directory to proper location.
"""

import os
import logging
from typing import Dict, Any, List, Optional, AsyncIterator

try:
    from groq import AsyncGroq
except ImportError:
    AsyncGroq = None

logger = logging.getLogger(__name__)


class GroqClient:
    """Centralized Groq client for all LLM operations."""

    # Available Groq models (all FREE and FAST!) - Updated 2025-10-29
    MODELS = {
        # Meta Llama - Latest & Best
        "llama-3.3-70b": "llama-3.3-70b-versatile",  # Best for complex tasks
        "llama-3.1-8b": "llama-3.1-8b-instant",      # Fastest for simple tasks
        "llama3-70b": "llama3-70b-8192",             # Alternative 70B
        "llama3-8b": "llama3-8b-8192",               # Alternative 8B
        "llama-guard": "llama-guard-3-8b",           # Content moderation

        # Vision Models (Multimodal)
        "llama-vision": "llama-3.2-11b-vision-preview",  # Vision capable
        "llama4-scout": "meta-llama/llama-4-scout-17b-16e-instruct",  # Latest Llama 4

        # Tool Use / Function Calling
        "llama-tool-70b": "llama-3-groq-70b-tool-use",  # Best for tools
        "llama-tool-8b": "llama-3-groq-8b-tool-use",    # Fast tools

        # Reasoning Models
        "deepseek-r1": "deepseek-r1-distill-llama-70b",  # Reasoning champion

        # Other Models
        "gemma2": "gemma2-9b-it",                    # Google Gemma
        "mixtral": "mixtral-8x7b-32768",             # Mixtral MoE

        # Aliases for backwards compatibility
        "llama-3.1-70b": "llama-3.3-70b-versatile",
        "llama-3.2-90b": "llama-3.2-11b-vision-preview",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        enable_cache: bool = False  # Disabled by default in microservice
    ):
        """Initialize Groq client.

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model to use
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            enable_cache: Enable response caching (disabled by default)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            logger.warning("GROQ_API_KEY not set! Get free key at: https://console.groq.com")

        self.model = self.MODELS.get(model, self.MODELS["llama-3.3-70b"])
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize Groq client
        if AsyncGroq:
            self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None
        else:
            logger.error("groq package not installed. Install with: uv add groq")
            self.client = None

        # Cache disabled in microservice context
        self.cache = None

        logger.info(f"Groq client initialized with model: {self.model}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text completion using Groq.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional Groq API parameters

        Returns:
            Generated text
        """
        if not self.client:
            logger.error("Groq client not initialized - missing API key or package")
            return self._fallback_response(prompt)

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )

            content = response.choices[0].message.content

            logger.info(
                "groq_generation_success",
                extra={
                    "model": self.model,
                    "prompt_length": len(prompt),
                    "response_length": len(content),
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            )

            return content

        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            # Raise exception to allow fallback to other providers
            raise RuntimeError(f"Groq generation failed: {e}")

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming text completion using Groq.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional Groq API parameters

        Yields:
            Generated text chunks
        """
        if not self.client:
            logger.error("Groq client not initialized - missing API key")
            yield self._fallback_response(prompt)
            return

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            yield self._fallback_response(prompt)

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate JSON response using Groq.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional Groq API parameters

        Returns:
            Parsed JSON response
        """
        import json

        if not system_prompt:
            system_prompt = "You are a helpful assistant that responds in valid JSON format."

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )

        try:
            # Try to parse JSON from response
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Invalid JSON response", "raw": response}

    def _fallback_response(self, prompt: str) -> str:
        """Generate fallback response when Groq is unavailable."""
        return f"[Groq unavailable - fallback response for: {prompt[:100]}...]"

    async def count_tokens(self, text: str) -> int:
        """Estimate token count (approximate for Llama models).

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 chars per token for Llama
        return len(text) // 4

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model."""
        return {
            "provider": "Groq",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "features": ["chat", "streaming", "json", "fast", "free"],
            "context_window": 32768 if "mixtral" in self.model else 8192
        }


# Global instance
_groq_client: Optional[GroqClient] = None


def get_groq_client(
    api_key: Optional[str] = None,
    model: str = "llama-3.3-70b",
    **kwargs
) -> GroqClient:
    """Get or create global Groq client instance.

    Args:
        api_key: Groq API key
        model: Model to use
        **kwargs: Additional client parameters

    Returns:
        Groq client instance
    """
    global _groq_client

    if _groq_client is None:
        _groq_client = GroqClient(api_key=api_key, model=model, **kwargs)

    return _groq_client


def reset_groq_client():
    """Reset global Groq client instance."""
    global _groq_client
    _groq_client = None
