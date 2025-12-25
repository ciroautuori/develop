"""
AI Support Proxy - Routes requests to AI Microservice.

Uses centralized AI client for all AI microservice communication.
"""
import logging
from typing import Dict, Any, Optional

from app.infrastructure.ai import ai_client, AIServiceError
from app.core.config import get_fallback_chat_response

logger = logging.getLogger(__name__)


class AICustomerSupport:
    """
    AI Customer Support Proxy.
    Uses centralized AI client for consistent error handling and retries.
    """

    async def generate_response(
        self,
        message: str,
        context: Optional[str] = None,
        provider: str = "groq",
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate AI response via centralized AI client.

        Args:
            message: User message
            context: Optional conversation context
            provider: AI provider (groq, gemini, huggingface, openrouter, ollama)
            max_retries: Retry attempts (handled by AI client)

        Returns:
            Dict with response, confidence, provider, processing_time, sentiment
        """
        try:
            data = await ai_client.chat(
                message=message,
                context=context,
                provider=provider
            )
            logger.info(
                f"AI response: provider={data.get('provider')}, "
                f"confidence={data.get('confidence')}, "
                f"time={data.get('processing_time')}ms"
            )
            return data

        except AIServiceError as e:
            logger.warning(f"AI Microservice error, using fallback: {e}")
            return self._fallback_response(message)

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Generate fallback response when AI Microservice unavailable."""
        return {
            "response": get_fallback_chat_response(message),
            "confidence": 50,
            "provider": "fallback",
            "sentiment": "neutral",
            "processing_time": 0,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check AI Microservice availability."""
        return await ai_client.health_check()
