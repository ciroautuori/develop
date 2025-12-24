"""
LLM Service with Multi-Provider Fallback Chain - DICEMBRE 2025

UPDATED: Ollama PRIMARY + Cloud APIs fallback

Features:
- Ollama local (central-ollama:11434) - FREE, no rate limits
- Multiple Groq keys rotation (6 keys = 600k tokens/day)
- Google Gemini free (unlimited with soft rate limiting)
"""
import os
import httpx
from typing import List, Dict, Optional, Any
import asyncio
from enum import Enum

# LangChain imports
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI (Removed for lighter build)
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from src.infrastructure.config.settings import settings
from src.infrastructure.logging import get_logger

# CRITICAL: Resolve NameError: BaseTool/Runnable for LangChain introspection
import builtins
try:
    from langchain_core.tools import BaseTool, ToolCall
    from langchain_core.runnables import Runnable, RunnableSerializable
    from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
    builtins.BaseTool = BaseTool
    builtins.Runnable = Runnable
    builtins.BaseMessage = BaseMessage
    builtins.HumanMessage = HumanMessage
    builtins.SystemMessage = SystemMessage
    builtins.RunnableSerializable = RunnableSerializable
    builtins.ToolCall = ToolCall
except ImportError:
    pass

logger = get_logger(__name__)


class LLMProvider(Enum):
    """Available LLM providers - DICEMBRE 2025."""
    OLLAMA = "ollama"  # PRIMARY - Local, free
    GROQ = "groq"
    GOOGLE = "google"


from src.infrastructure.ai.tools import FatSecretTool, get_medical_rag_tool, get_training_rag_tool

from langchain_community.chat_models import ChatOllama

class LLMService:
    """
    LLM Service with Multi-Provider Fallback Chain AND Agentic Capabilities.
    
    AGENTIC CAPABILITIES:
    - FatSecret Tool: Verified nutrition data
    - Medical RAG: Verified rehab protocols
    - Training RAG: Verified CrossFit/Standards
    """

    def __init__(self):
        self.groq_api_keys = settings.get_groq_api_keys_list()
        self.openrouter_api_key = settings.openrouter_api_key
        self.google_api_key = settings.google_api_key
        
        self.current_groq_key_index = 0
        self.fallback_models = settings.get_fallback_models_list()
        
        # Tools Initialization
        logger.info("🛠️ Initializing AI Tools...")
        self.tools = {}
        try:
            self.tools["nutrition"] = FatSecretTool()
            self.tools["medical"] = get_medical_rag_tool()
            self.tools["training"] = get_training_rag_tool()
            logger.info("✅ Tools initialized: Nutrition, Medical, Training")
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")

        # Initialize provider clients
        self._init_providers()

    async def _check_ollama_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                ollama_host = os.getenv("OLLAMA_HOST", "central-ollama")
                ollama_port = os.getenv("OLLAMA_PORT", "11434")
                response = await client.get(f"http://{ollama_host}:{ollama_port}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    def _init_providers(self):
        """Initialize all LLM providers - OLLAMA PRIMARY (Dec 2025)."""
        self.fallback_chain = []
        
        # Ollama config
        self.ollama_host = os.getenv("OLLAMA_HOST", "central-ollama")
        self.ollama_port = os.getenv("OLLAMA_PORT", "11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b-instruct")
        self.use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"

        # =====================================================================
        # OLLAMA PRIMARY - FREE, local, no rate limits
        # =====================================================================
        if self.use_ollama:
            logger.info(f"🟣 Initializing OLLAMA as PRIMARY: {self.ollama_model}")
            
            # Initialize properly for Agents that need LangChain interface
            try:
                ollama_client = ChatOllama(
                    base_url=f"http://{self.ollama_host}:{self.ollama_port}",
                    model=self.ollama_model,
                    temperature=0.7
                )
            except Exception as e:
                logger.warning(f"Failed to initialize ChatOllama client: {e}")
                ollama_client = None

            self.fallback_chain.append(
                (LLMProvider.OLLAMA, ollama_client, "ollama-local", self.ollama_model)
            )
            logger.info(f"✅ OLLAMA initialized at {self.ollama_host}:{self.ollama_port}")

        # =====================================================================
        # GROQ FALLBACK - Ultra-fast inference with Llama 3.3
        # =====================================================================
        primary_model = settings.primary_llm_model
        logger.info(f"🔵 Initializing GROQ as FALLBACK: {primary_model}")
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
        # (OpenRouter REMOVED for optimization)
        # =====================================================================

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

    async def _route_query(self, query: str) -> str:
        """
        Determine intent of query to select tool.
        Simple zero-shot classification via LLM.
        """
        system_prompt = """
        Analyze the user query and classify it into one of these categories:
        - NUTRITION: asking about calories, macros, ingredients, food values.
        - MEDICAL: asking about injuries, rehab, pain, physical therapy.
        - TRAINING: asking about exercises, WODs, form, standards.
        - CHITCHAT: general conversation, greeting, philosophy.
        
        Return ONLY the category name.
        """
        
        try:
            # Use Ollama/Groq to classify
            response = await self.generate(query, system_prompt=system_prompt)
            category = response.strip().upper()
            
            # Basic cleanup
            for cat in ["NUTRITION", "MEDICAL", "TRAINING", "CHITCHAT"]:
                if cat in category:
                    return cat
            return "CHITCHAT"
        except Exception:
            return "CHITCHAT"

    async def run_agent(self, query: str, user_context: Optional[str] = None) -> str:
        """
        Execute Agentic Loop:
        1. Route query (Think)
        2. Execute tool (Act)
        3. Generate response (Observe & Answer)
        """
        category = await self._route_query(query)
        logger.info(f"🧠 Agent routed query to: {category}")
        
        tool_result = None
        tool_name = None
        
        if category == "NUTRITION" and "nutrition" in self.tools:
            tool_name = "FatSecret API"
            # Extract food name heuristic or just pass valid query part
            # For simplicity in V1, pass full query
            tool_result = await self.tools["nutrition"].execute(query)
            
        elif category == "MEDICAL" and "medical" in self.tools:
            tool_name = "IronRep Medical Doc"
            tool_result = await self.tools["medical"].execute(query)
            
        elif category == "TRAINING" and "training" in self.tools:
            tool_name = "IronRep Training Doc"
            tool_result = await self.tools["training"].execute(query)
            
        # Final Generation
        if tool_result:
            system_prompt = f"""
            You are IronRep AI, an expert coach. 
            Use the following VERIFIED DATA from {tool_name} to answer the user.
            
            VERIFIED DATA:
            {tool_result}
            
            If the data contains calories/macros, cite it explicitly (e.g. "According to FatSecret...").
            If it contains medical protocols, be precise and add a disclaimer.
            Do not invent information outside the provided data.
            """
        else:
            system_prompt = "You are IronRep AI, an expert coach. Answer helpful and motivating."
            
        if user_context:
            system_prompt += f"\nUser Context: {user_context}"
            
        return await self.generate(query, system_prompt=system_prompt)

    async def _call_ollama(
        self,
        messages: List[BaseMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Call Ollama API directly."""
        # Convert LangChain messages to Ollama format
        ollama_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                ollama_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                ollama_messages.append({"role": "user", "content": msg.content})
            else:
                ollama_messages.append({"role": "assistant", "content": msg.content})
        
        payload = {
            "model": self.ollama_model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"http://{self.ollama_host}:{self.ollama_port}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

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

                # Handle Ollama separately (no LangChain client)
                if provider == LLMProvider.OLLAMA:
                    if await self._check_ollama_available():
                        content = await self._call_ollama(messages, temperature, max_tokens)
                        logger.info(f"✅ Success with {provider_name}")
                        return {
                            "content": content,
                            "provider": provider.value,
                            "provider_name": provider_name,
                            "model": model,
                            "success": True
                        }
                    else:
                        logger.warning("Ollama not available, trying next provider...")
                        continue

                # Call LangChain client for other providers
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
