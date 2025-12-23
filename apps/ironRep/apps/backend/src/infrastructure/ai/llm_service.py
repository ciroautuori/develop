"""
LLM Service with Multi-Provider Fallback Chain - NOVEMBRE 2025

ROLLBACK: Cloud APIs only (GROQ primary + OpenRouter fallback)

Features:
- Multiple Groq keys rotation (6 keys = 600k tokens/day)
- OpenRouter free models (unlimited with training opt-in)
- Google Gemini free (unlimited with soft rate limiting)
"""
import os
from typing import List, Dict, Optional, Any
import asyncio
from enum import Enum

# LangChain imports
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI (Removed for lighter build)
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from src.infrastructure.config.settings import settings
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class LLMProvider(Enum):
    """Available LLM providers - NOVEMBRE 2025."""
    GROQ = "groq"
    # OPENROUTER = "openrouter" (Removed)
    GOOGLE = "google"


class LLMService:
    """
    LLM Service with Multi-Provider Fallback Chain.

    FALLBACK CHAIN (in order):
    1. GROQ Llama 3.3 70B (6 keys rotation = 600k tokens/day)
    2. OpenRouter Free Models (unlimited)
    3. Google Gemini Free (unlimited)
    """

    def __init__(self):
        self.groq_api_keys = settings.get_groq_api_keys_list()
        self.openrouter_api_key = settings.openrouter_api_key
        self.google_api_key = settings.google_api_key

        self.current_groq_key_index = 0
        self.fallback_models = settings.get_fallback_models_list()

        # Initialize provider clients
        self._init_providers()

    def _init_providers(self):
        """Initialize all LLM provider clients - GROQ PRIMARY (Dec 2024)."""
        self.fallback_chain = []

        # =====================================================================
        # GROQ PRIMARY - Ultra-fast inference with Llama 3.3
        # =====================================================================
        primary_model = settings.primary_llm_model
        logger.info(f"🔵 Initializing GROQ as PRIMARY: {primary_model}")
        for i, key in enumerate(self.groq_api_keys):
            try:
                client = ChatGroq(
                    api_key=key,
                    model_name=primary_model,
                    temperature=0.7,
                    max_tokens=2048
                )
                self.fallback_chain.append(
                    (LLMProvider.GROQ, client, f"groq-key-{i+1}", primary_model)
                )
                logger.info(f"✅ GROQ key-{i+1} initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq key {i+1}: {e}")

        # =====================================================================
        # OPENROUTER FALLBACK - REMOVED for optimization
        # =====================================================================
        # (OpenRouter requires langchain_openai package which adds bloat)

        # =====================================================================
        # GOOGLE GEMINI - Last resort fallback
        # =====================================================================
        if self.google_api_key:
            try:
                google_client = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=self.google_api_key,
                    temperature=0.7,
                    max_output_tokens=2048,
                    convert_system_message_to_human=True
                )
                self.fallback_chain.append(
                    (LLMProvider.GOOGLE, google_client, "google-gemini", settings.gemini_model)
                )
                logger.info("🟢 Google Gemini 2.0 Flash initialized as last fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Gemini: {e}")

        logger.info(f"✅ Initialized {len(self.fallback_chain)} LLM providers in fallback chain")
        for i, (provider, _, name, model) in enumerate(self.fallback_chain):
            logger.info(f"   {i+1}. {name} ({model})")

    async def call_with_fallback(
        self,
        messages: List[BaseMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Call LLM with automatic fallback through entire provider chain.

        Args:
            messages: List of messages (system, human, ai)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            dict with 'content', 'provider', and metadata
        """
        last_error = None

        for provider, client, provider_name, model in self.fallback_chain:
            try:
                logger.debug(f"Trying {provider_name} ({model})...")

                # Call LLM
                response = await client.ainvoke(messages)

                logger.info(f"✅ Success with {provider_name}")

                return {
                    "content": response.content,
                    "provider": provider.value,
                    "provider_name": provider_name,
                    "model": model,
                    "success": True
                }

            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"{provider_name} failed: {error_msg[:150]}")

                # Continue to next provider on any error
                # (rate limit, auth error, etc.)
                continue

        # All providers failed
        raise Exception(
            f"All {len(self.fallback_chain)} LLM providers failed. Last error: {last_error}"
        )

    async def call_with_tools(
        self,
        messages: List[BaseMessage],
        tools: List[Any],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Call LLM with function calling tools.

        Args:
            messages: Conversation messages
            tools: LangChain tools for function calling
            temperature: Sampling temperature

        Returns:
            dict with response and potential tool calls
        """
        last_error = None

        for provider, client, provider_name, model in self.fallback_chain:
            try:
                logger.debug(f"Trying {provider_name} with tools...")

                # Bind tools to client
                llm_with_tools = client.bind_tools(tools)

                # Call LLM
                response = await llm_with_tools.ainvoke(messages)

                logger.info(f"Success with {provider_name}")

                return {
                    "content": response.content,
                    "tool_calls": response.tool_calls if hasattr(response, 'tool_calls') else [],
                    "provider": provider.value,
                    "provider_name": provider_name,
                    "success": True
                }

            except Exception as e:
                last_error = e
                logger.warning(f"{provider_name} failed: {str(e)[:150]}")
                continue

        raise Exception(
            f"All providers failed with tools. Last error: {last_error}"
        )

    def get_client_for_agent(self, prefer_provider: Optional[LLMProvider] = None):
        """
        Get LLM client for LangChain agent with configured fallbacks.

        Returns:
            LangChain chat model instance with fallbacks configured
        """
        if not self.fallback_chain:
             raise Exception("No LLM providers available")

        # Extract just the clients from the chain
        clients = [client for _, client, _, _ in self.fallback_chain]

        # If a specific provider is preferred and found, try to put it first
        # (Note: This simple logic just returns the first match,
        # but for true fallback we want the whole chain starting with preference)
        if prefer_provider:
            # Reorder clients to put preferred one first
            preferred_clients = [
                client for provider, client, _, _ in self.fallback_chain
                if provider == prefer_provider
            ]
            other_clients = [
                client for provider, client, _, _ in self.fallback_chain
                if provider != prefer_provider
            ]
            clients = preferred_clients + other_clients

        if not clients:
             raise Exception("No LLM clients available")

        # Primary is the first one
        primary = clients[0]

        # Fallbacks are the rest
        fallbacks = clients[1:]

        if not fallbacks:
            return primary

        # Return primary with fallbacks
        # We catch all exceptions to ensure rotation works
        return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Simple text generation from a prompt string.

        This is a convenience wrapper around call_with_fallback for simple
        prompt -> response use cases (like the Wizard agent).

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system prompt

        Returns:
            Generated text as string
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        result = await self.call_with_fallback(messages)
        return result["content"]
