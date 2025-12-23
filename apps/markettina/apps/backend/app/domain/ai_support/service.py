"""
Support Service Wrapper
Provides structured interface to AI Customer Support
"""

import logging

from app.domain.ai_support.chatbot import AICustomerSupport

logger = logging.getLogger(__name__)


class SupportService:
    """Support service with logging and error handling"""

    def __init__(self):
        self.ai_support = AICustomerSupport()

    async def chat(
        self,
        message: str,
        context: str | None = None,
        provider: str = "groq"  # Default to GROQ (FREE!)
    ) -> dict:
        """
        Handle customer support chat request

        Args:
            message: User message
            context: Optional conversation context
            provider: AI provider to use (gemini, openai, ollama)

        Returns:
            Dict with response, confidence, sentiment, provider, processing_time
        """
        try:
            logger.info(
                "support_chat_request",
                provider=provider,
                message_length=len(message)
            )

            result = await self.ai_support.generate_response(
                message=message,
                context=context,
                provider=provider
            )

            logger.info(
                "support_chat_success",
                provider=result.get("provider"),
                confidence=result.get("confidence"),
                processing_time=result.get("processing_time")
            )

            return result

        except Exception as e:
            logger.error(
                "support_chat_error",
                error=str(e),
                provider=provider,
                exc_info=True
            )
            raise

    async def health_check(self) -> dict:
        """Check availability of AI providers"""
        from app.core.config import settings

        groq_keys_count = len(settings.groq_api_keys)

        status = {
            "groq": f"available ({groq_keys_count} keys)" if groq_keys_count > 0 else "not_configured",
            "huggingface": "available" if settings.huggingface_token_resolved else "not_configured",
            "gemini": "available" if settings.google_api_key_resolved else "not_configured",
            "openrouter": "available" if settings.OPENROUTER_API_KEY else "not_configured",
            "ollama": "available",  # Always available (local)
        }

        return {
            "service": "support",
            "providers": status,
            "fallback_order": ["groq", "huggingface", "gemini", "openrouter", "ollama"],
            "primary": "groq (FREE & FAST!)",
            "groq_keys_available": groq_keys_count
        }
