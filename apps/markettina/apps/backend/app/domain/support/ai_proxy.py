"""
AI Support Proxy - Routes requests to AI Microservice
Replaces local AICustomerSupport with proxy to centralized AI service.
"""
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# AI Microservice configuration
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
AI_SERVICE_TIMEOUT = float(os.getenv("AI_SERVICE_TIMEOUT", "30.0"))


class AICustomerSupport:
    """
    AI Customer Support Proxy.
    Proxies requests to AI Microservice for centralized AI processing.
    Falls back to local simple response if microservice unavailable.
    """

    def __init__(self):
        self.service_url = AI_SERVICE_URL
        self.timeout = AI_SERVICE_TIMEOUT

    async def generate_response(
        self,
        message: str,
        context: str | None = None,
        provider: str = "groq",
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """
        Generate AI response via AI Microservice proxy.

        Args:
            message: User message
            context: Optional conversation context
            provider: AI provider (groq, gemini, huggingface, openrouter, ollama)
            max_retries: Retry attempts

        Returns:
            Dict with response, confidence, provider, processing_time, sentiment
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.service_url}/api/v1/support/chat",
                    json={
                        "message": message,
                        "context": context,
                        "provider": provider,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(
                        f"AI response via microservice: provider={data.get('provider')}, "
                        f"confidence={data.get('confidence')}, "
                        f"time={data.get('processing_time')}ms"
                    )
                    return data

                logger.warning(f"AI Microservice returned {response.status_code}")

        except httpx.TimeoutException:
            logger.warning("AI Microservice timeout, using fallback")
        except httpx.ConnectError:
            logger.warning("AI Microservice unavailable, using fallback")
        except Exception as e:
            logger.error(f"AI Microservice error: {e}")

        # Fallback response
        return self._fallback_response(message)

    def _fallback_response(self, message: str) -> dict[str, Any]:
        """Generate fallback response when AI Microservice unavailable."""
        msg_lower = message.lower()

        # Basic keyword matching for fallback
        if any(w in msg_lower for w in ["prezzo", "costo", "quanto"]):
            response = (
                "I nostri servizi partono da 990€ per un sito web vetrina. "
                "Per un preventivo personalizzato, contattaci a info@markettina.it "
                "o prenota una consulenza gratuita su markettina.it"
            )
        elif any(w in msg_lower for w in ["servizi", "cosa fate", "offrite"]):
            response = (
                "MARKETTINA offre: Sviluppo Web Enterprise, App Mobile, "
                "E-commerce, AI Integration, Automazione Processi. "
                "Visita markettina.it per maggiori dettagli."
            )
        elif any(w in msg_lower for w in ["contatt", "email", "telefono"]):
            response = (
                "Puoi contattarci: Email info@markettina.it | "
                "Tel: +39 340 321 7806 | Via Francesco Vernieri 20, Scafati (SA)"
            )
        elif any(w in msg_lower for w in ["ciao", "buongiorno", "salve"]):
            response = "Ciao! Come posso aiutarti oggi con il tuo progetto digitale?"
        else:
            response = (
                "Grazie per il tuo messaggio! Per una risposta più dettagliata, "
                "contattaci a info@markettina.it o prenota una consulenza gratuita "
                "su markettina.it. Ti risponderemo entro 24h."
            )

        return {
            "response": response,
            "confidence": 50,
            "provider": "fallback",
            "sentiment": "neutral",
            "processing_time": 0,
        }

    async def health_check(self) -> dict[str, Any]:
        """Check AI Microservice availability."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.service_url}/health")
                if response.status_code == 200:
                    return {
                        "status": "connected",
                        "service_url": self.service_url,
                        "microservice": response.json(),
                    }
        except Exception as e:
            logger.warning(f"AI Microservice health check failed: {e}")

        return {
            "status": "disconnected",
            "service_url": self.service_url,
            "fallback": "enabled",
        }
