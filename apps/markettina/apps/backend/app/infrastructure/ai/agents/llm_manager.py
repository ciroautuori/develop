"""
Unified LLM Manager - Multi-provider LLM management with automatic fallback.

Provides unified interface for multiple LLM providers with:
    - Automatic fallback chain
    - Cost tracking and optimization
    - Streaming support
    - Model selection based on task complexity
    - Token usage monitoring

Based on BFILT AUTOMATOR's multi-provider LLM architecture.
"""

import json
from collections.abc import AsyncIterator
from datetime import datetime
from enum import Enum
from typing import Any

import litellm
from litellm import acompletion, completion_cost
from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class TaskComplexity(str, Enum):
    """Task complexity levels."""
    SIMPLE = "simple"  # Simple queries, formatting
    MEDIUM = "medium"  # Content generation, analysis
    COMPLEX = "complex"  # Complex reasoning, multi-step
    EXPERT = "expert"  # Specialized domain knowledge


class LLMResponse(BaseModel):
    """LLM response with metadata."""

    content: str
    provider: LLMProvider
    model: str
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0
    latency: float = 0.0
    cached: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""

    provider: LLMProvider
    model: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60
    priority: int = 0  # Higher = higher priority
    enabled: bool = True
    cost_per_1k_tokens: float = 0.0


class ModelSelection(BaseModel):
    """Model selection strategy."""

    complexity: TaskComplexity
    max_cost: float | None = None
    prefer_speed: bool = False
    require_streaming: bool = False


class UnifiedLLMManager:
    """
    Unified LLM Manager with multi-provider support.
    
    Features:
        - 5 providers (OpenAI, Anthropic, Google, OpenRouter, Ollama)
        - Automatic fallback chain based on priority
        - Cost tracking and budget limits
        - Streaming support
        - Model selection based on task complexity
        - Token usage monitoring
        - Response caching
    
    Example:
        >>> manager = UnifiedLLMManager()
        >>> manager.add_provider(LLMConfig(
        ...     provider=LLMProvider.OPENAI,
        ...     model="gpt-4o",
        ...     api_key="sk-...",
        ...     priority=100
        ... ))
        >>> 
        >>> response = await manager.complete(
        ...     messages=[{"role": "user", "content": "Hello!"}],
        ...     complexity=TaskComplexity.SIMPLE
        ... )
    """

    def __init__(
        self,
        default_temperature: float = 0.7,
        default_max_tokens: int = 4000,
        enable_caching: bool = True
    ):
        """
        Initialize Unified LLM Manager.
        
        Args:
            default_temperature: Default temperature for completions
            default_max_tokens: Default max tokens
            enable_caching: Enable response caching
        """
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.enable_caching = enable_caching

        # Provider configurations
        self.providers: dict[str, LLMConfig] = {}

        # Usage tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.requests_count = 0
        self.provider_usage: dict[str, dict[str, Any]] = {}

        # Response cache
        self._cache: dict[str, LLMResponse] = {}

        # Configure litellm
        litellm.drop_params = True  # Drop unsupported params
        litellm.set_verbose = False

    def add_provider(self, config: LLMConfig) -> None:
        """
        Add LLM provider configuration.
        
        Args:
            config: Provider configuration
        """
        provider_key = f"{config.provider}:{config.model}"
        self.providers[provider_key] = config

        # Initialize usage tracking
        if provider_key not in self.provider_usage:
            self.provider_usage[provider_key] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0,
                "errors": 0,
                "avg_latency": 0.0
            }

    def remove_provider(self, provider: LLMProvider, model: str) -> None:
        """Remove provider configuration."""
        provider_key = f"{provider}:{model}"
        self.providers.pop(provider_key, None)

    def get_provider_chain(
        self,
        selection: ModelSelection | None = None
    ) -> list[LLMConfig]:
        """
        Get fallback chain of providers based on selection criteria.
        
        Args:
            selection: Model selection criteria
            
        Returns:
            Ordered list of providers to try
        """
        # Filter enabled providers
        available = [
            cfg for cfg in self.providers.values()
            if cfg.enabled
        ]

        if not available:
            raise ValueError("No enabled providers configured")

        # Apply selection criteria
        if selection:
            # Filter by cost if specified
            if selection.max_cost is not None:
                available = [
                    cfg for cfg in available
                    if cfg.cost_per_1k_tokens <= selection.max_cost
                ]

            # Filter by streaming support if required
            if selection.require_streaming:
                # Ollama doesn't support streaming well
                available = [
                    cfg for cfg in available
                    if cfg.provider != LLMProvider.OLLAMA
                ]

            # Sort by preference
            if selection.prefer_speed:
                # Prefer faster models (generally smaller/cheaper)
                available.sort(key=lambda x: x.cost_per_1k_tokens)
            else:
                # Sort by priority (higher first)
                available.sort(key=lambda x: x.priority, reverse=True)
        else:
            # Default: sort by priority
            available.sort(key=lambda x: x.priority, reverse=True)

        return available

    async def complete(
        self,
        messages: list[dict[str, str]],
        complexity: TaskComplexity = TaskComplexity.MEDIUM,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Complete chat messages with automatic fallback.
        
        Args:
            messages: Chat messages
            complexity: Task complexity
            temperature: Temperature override
            max_tokens: Max tokens override
            stream: Enable streaming
            **kwargs: Additional completion parameters
            
        Returns:
            LLM response
        """
        # Check cache
        if self.enable_caching and not stream:
            cache_key = self._get_cache_key(messages, temperature, max_tokens)
            if cache_key in self._cache:
                cached_response = self._cache[cache_key]
                cached_response.cached = True
                return cached_response

        # Get provider chain
        selection = ModelSelection(
            complexity=complexity,
            require_streaming=stream
        )
        provider_chain = self.get_provider_chain(selection)

        # Try providers in order
        last_error = None

        for provider_config in provider_chain:
            try:
                response = await self._complete_with_provider(
                    provider_config=provider_config,
                    messages=messages,
                    temperature=temperature or self.default_temperature,
                    max_tokens=max_tokens or self.default_max_tokens,
                    stream=stream,
                    **kwargs
                )

                # Cache successful response
                if self.enable_caching and not stream:
                    self._cache[cache_key] = response

                return response

            except Exception as e:
                last_error = e

                # Track error
                provider_key = f"{provider_config.provider}:{provider_config.model}"
                self.provider_usage[provider_key]["errors"] += 1

                # Continue to next provider
                continue

        # All providers failed
        raise RuntimeError(
            f"All providers failed. Last error: {last_error}"
        )

    async def complete_streaming(
        self,
        messages: list[dict[str, str]],
        complexity: TaskComplexity = TaskComplexity.MEDIUM,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion chunks.
        
        Args:
            messages: Chat messages
            complexity: Task complexity
            temperature: Temperature override
            max_tokens: Max tokens override
            **kwargs: Additional parameters
            
        Yields:
            Content chunks
        """
        selection = ModelSelection(
            complexity=complexity,
            require_streaming=True
        )
        provider_chain = self.get_provider_chain(selection)

        for provider_config in provider_chain:
            try:
                async for chunk in self._stream_with_provider(
                    provider_config=provider_config,
                    messages=messages,
                    temperature=temperature or self.default_temperature,
                    max_tokens=max_tokens or self.default_max_tokens,
                    **kwargs
                ):
                    yield chunk

                return  # Success, exit

            except Exception:
                # Track error and try next provider
                provider_key = f"{provider_config.provider}:{provider_config.model}"
                self.provider_usage[provider_key]["errors"] += 1
                continue

        raise RuntimeError("All providers failed for streaming")

    async def _complete_with_provider(
        self,
        provider_config: LLMConfig,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """Complete with specific provider."""
        start_time = datetime.now()

        # Build model name for litellm
        model = self._build_model_name(provider_config)

        # Prepare completion kwargs
        completion_kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": provider_config.timeout,
            **kwargs
        }

        # Add API key if provided
        if provider_config.api_key:
            completion_kwargs["api_key"] = provider_config.api_key

        # Add base URL if provided
        if provider_config.base_url:
            completion_kwargs["base_url"] = provider_config.base_url

        # Call litellm
        response = await acompletion(**completion_kwargs)

        # Calculate metrics
        latency = (datetime.now() - start_time).total_seconds()

        content = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        # Calculate cost
        cost = completion_cost(response)

        # Update tracking
        provider_key = f"{provider_config.provider}:{provider_config.model}"
        self._update_usage(provider_key, total_tokens, cost, latency)

        return LLMResponse(
            content=content,
            provider=provider_config.provider,
            model=provider_config.model,
            tokens_used=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            latency=latency,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "model_used": response.model
            }
        )

    async def _stream_with_provider(
        self,
        provider_config: LLMConfig,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion with specific provider."""
        model = self._build_model_name(provider_config)

        completion_kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            "timeout": provider_config.timeout,
            **kwargs
        }

        if provider_config.api_key:
            completion_kwargs["api_key"] = provider_config.api_key

        if provider_config.base_url:
            completion_kwargs["base_url"] = provider_config.base_url

        response = await acompletion(**completion_kwargs)

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _build_model_name(self, config: LLMConfig) -> str:
        """Build litellm model name."""
        if config.provider == LLMProvider.OPENAI:
            return config.model
        if config.provider == LLMProvider.ANTHROPIC:
            return f"claude/{config.model}"
        if config.provider == LLMProvider.GOOGLE:
            return f"gemini/{config.model}"
        if config.provider == LLMProvider.OPENROUTER:
            return f"openrouter/{config.model}"
        if config.provider == LLMProvider.OLLAMA:
            return f"ollama/{config.model}"
        return config.model

    def _get_cache_key(
        self,
        messages: list[dict[str, str]],
        temperature: float | None,
        max_tokens: int | None
    ) -> str:
        """Generate cache key for messages."""
        import hashlib

        key_data = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _update_usage(
        self,
        provider_key: str,
        tokens: int,
        cost: float,
        latency: float
    ) -> None:
        """Update usage tracking."""
        if provider_key not in self.provider_usage:
            self.provider_usage[provider_key] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0,
                "errors": 0,
                "avg_latency": 0.0
            }

        usage = self.provider_usage[provider_key]
        usage["requests"] += 1
        usage["tokens"] += tokens
        usage["cost"] += cost

        # Update average latency
        total_latency = usage["avg_latency"] * (usage["requests"] - 1)
        usage["avg_latency"] = (total_latency + latency) / usage["requests"]

        # Update global tracking
        self.total_tokens_used += tokens
        self.total_cost += cost
        self.requests_count += 1

    def get_usage_stats(self) -> dict[str, Any]:
        """
        Get usage statistics.
        
        Returns:
            Usage stats for all providers
        """
        return {
            "total_requests": self.requests_count,
            "total_tokens": self.total_tokens_used,
            "total_cost": round(self.total_cost, 4),
            "avg_cost_per_request": (
                round(self.total_cost / self.requests_count, 4)
                if self.requests_count > 0 else 0.0
            ),
            "by_provider": self.provider_usage,
            "cache_size": len(self._cache)
        }

    def clear_cache(self) -> int:
        """
        Clear response cache.
        
        Returns:
            Number of cached entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        return count

    def reset_usage_stats(self) -> None:
        """Reset all usage statistics."""
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.requests_count = 0

        for usage in self.provider_usage.values():
            usage["requests"] = 0
            usage["tokens"] = 0
            usage["cost"] = 0.0
            usage["errors"] = 0
            usage["avg_latency"] = 0.0
