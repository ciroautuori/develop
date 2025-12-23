"""
Streaming SSE Service - Server-Sent Events for Real-Time LLM Responses.

Provides streaming capabilities for AI agent responses using SSE.
"""
import json
import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.callbacks import AsyncCallbackHandler

from src.infrastructure.config.settings import settings
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM tokens."""

    def __init__(self):
        self.tokens: asyncio.Queue = asyncio.Queue()
        self.done = False
        self.error: Optional[Exception] = None

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated."""
        await self.tokens.put(token)

    async def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM finishes."""
        self.done = True
        await self.tokens.put(None)  # Signal end

    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called on LLM error."""
        self.error = error
        self.done = True
        await self.tokens.put(None)


class StreamingLLMService:
    """
    Streaming LLM Service using SSE.

    Wraps the main LLMService to provide streaming capabilities.
    """

    def __init__(self, llm_service):
        """
        Initialize with existing LLM service.

        Args:
            llm_service: The main LLMService instance
        """
        self.llm_service = llm_service

    async def stream_response(
        self,
        messages: List[BaseMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """
        Stream LLM response token by token.

        Args:
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Max tokens

        Yields:
            SSE formatted events with tokens
        """
        callback = StreamingCallbackHandler()

        # Try each provider in the fallback chain
        for provider, client, provider_name, model in self.llm_service.fallback_chain:
            try:
                logger.debug(f"Streaming with {provider_name}...")

                # Send start event
                yield self._format_sse({
                    "type": "start",
                    "provider": provider_name,
                    "model": model,
                    "timestamp": datetime.now().isoformat()
                })

                # Stream tokens
                full_response = ""
                async for chunk in client.astream(messages, config={"callbacks": [callback]}):
                    if hasattr(chunk, 'content') and chunk.content:
                        token = chunk.content
                        full_response += token
                        yield self._format_sse({
                            "type": "token",
                            "content": token
                        })

                # Send end event
                yield self._format_sse({
                    "type": "end",
                    "full_response": full_response,
                    "provider": provider_name,
                    "timestamp": datetime.now().isoformat()
                })

                logger.info(f"Streaming complete with {provider_name}")
                return

            except Exception as e:
                logger.warning(f"{provider_name} streaming failed: {str(e)[:100]}")
                yield self._format_sse({
                    "type": "error",
                    "provider": provider_name,
                    "message": f"Switching provider: {str(e)[:50]}"
                })
                continue

        # All providers failed
        yield self._format_sse({
            "type": "error",
            "message": "All providers failed",
            "fatal": True
        })

    async def stream_agent_response(
        self,
        agent_name: str,
        question: str,
        context: Dict[str, Any],
        system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from a specific agent.

        Args:
            agent_name: Name of the agent (medical, workout, nutrition)
            question: User question
            context: Context dict (pain_level, phase, etc.)
            system_prompt: System prompt for the agent

        Yields:
            SSE formatted events
        """
        # Build messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=self._build_context_message(question, context))
        ]

        # Send agent info
        yield self._format_sse({
            "type": "agent_start",
            "agent": agent_name,
            "question": question,
            "timestamp": datetime.now().isoformat()
        })

        # Stream the response
        async for event in self.stream_response(messages):
            yield event

        # Send agent complete
        yield self._format_sse({
            "type": "agent_end",
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        })

    def _build_context_message(self, question: str, context: Dict[str, Any]) -> str:
        """Build context-enhanced message."""
        context_parts = []

        if context.get("pain_level") is not None:
            context_parts.append(f"Current pain level: {context['pain_level']}/10")

        if context.get("phase"):
            context_parts.append(f"Recovery phase: {context['phase']}")

        if context.get("clearance"):
            context_parts.append(f"Medical clearance: {context['clearance']}")

        if context.get("equipment"):
            context_parts.append(f"Available equipment: {', '.join(context['equipment'])}")

        context_str = "\n".join(context_parts) if context_parts else "No additional context"

        return f"""User Context:
{context_str}

User Question: {question}"""

    def _format_sse(self, data: Dict[str, Any]) -> str:
        """Format data as SSE event."""
        return f"data: {json.dumps(data)}\n\n"


def create_streaming_service(llm_service) -> StreamingLLMService:
    """Factory function to create streaming service."""
    return StreamingLLMService(llm_service)
