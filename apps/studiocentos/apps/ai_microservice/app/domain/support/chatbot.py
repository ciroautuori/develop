"""
AI Customer Support Service
Multi-provider AI service with fallback support
"""

import os
import time
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class AICustomerSupport:
    """
    AI Customer Support Service
    Supports multiple AI providers with automatic fallback
    """

    def __init__(self):
        self.providers = {
            "groq": self._groq_response,  # PRIMARY - FREE and FAST!
            "gemini": self._gemini_response,
            "openrouter": self._openrouter_response,
            "huggingface": self._huggingface_response,
            "ollama": self._ollama_response,
        }
        # Priority: GROQ (FREE!) → HuggingFace (FREE) → Gemini → OpenRouter (paid) → Ollama (local)
        self.fallback_order = ["groq", "huggingface", "gemini", "openrouter", "ollama"]
        self._groq_key_index = 0  # For rotating GROQ keys

        # StudioCentOS specific context
        self.system_context = """Sei un assistente AI per StudioCentOS, software house specializzata in sviluppo applicazioni enterprise a Salerno e Campania.

INFORMAZIONI CHIAVE SU STUDIOCENTOS:
- Software house di riferimento per Salerno e Campania
- Sede: Via Francesco Vernieri 20, 84018 Scafati (SA) - Campania
- Telefono: +39 340 321 7806
- Email: info@studiocentos.it
- Sito web: https://studiocentos.it

SERVIZI PRINCIPALI:
1. **Sviluppo Web Enterprise**: React 19, FastAPI, PostgreSQL, AI integration
2. **App Mobile Native**: React Native per iOS e Android
3. **E-commerce Avanzato**: Soluzioni complete con gestione magazzino
4. **AI & Automazione**: Chatbot intelligenti, automazione processi
5. **Consulenza Tecnologica**: Architettura software, best practices

STACK TECNOLOGICO:
- Frontend: React 19, TypeScript, TailwindCSS, Vite
- Backend: FastAPI, Python, PostgreSQL 16, Redis
- Mobile: React Native, Expo
- AI: Google Gemini, OpenRouter, integrazione LLM
- Infrastructure: Docker, Nginx, SSL, Arch Linux

VANTAGGI STUDIOCENTOS:
✅ 850+ file di codice production-ready
✅ Time to market: 45 giorni per MVP
✅ Supporto tecnico locale in Campania
✅ Made in Italy 🇮🇹
✅ Esperienza con progetti enterprise

COME PRENOTARE:
- Vai alla sezione "Prenota" sul sito
- Scegli data e orario per consulenza gratuita
- Compila form con nome, email, telefono
- Ricevi conferma immediata via email con link Google Meet

CONTATTI:
- Telefono/WhatsApp: +39 340 321 7806
- Email: info@studiocentos.it
- Indirizzo: Via Francesco Vernieri 20, 84018 Scafati (SA)

RISPONDI SEMPRE:
- In italiano professionale ma friendly
- Conciso e chiaro
- Con esempi concreti quando possibile
- Se non sai qualcosa, suggerisci di contattare direttamente via telefono o email
- Promuovi la consulenza gratuita per approfondire

NON INVENTARE informazioni. Se non sei sicuro di qualcosa, dillo chiaramente e suggerisci il contatto diretto."""

    async def generate_response(
        self,
        message: str,
        context: Optional[str] = None,
        provider: str = "gemini",
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate AI response with fallback support

        Args:
            message: User message
            context: Optional conversation context
            provider: Preferred AI provider
            max_retries: Maximum retry attempts

        Returns:
            Dict with response, confidence, provider, etc.
        """
        start_time = time.time()

        # Try preferred provider first
        providers_to_try = [provider] + [p for p in self.fallback_order if p != provider]

        for current_provider in providers_to_try:
            try:
                logger.info(f"Trying AI provider: {current_provider}")

                provider_func = self.providers.get(current_provider)
                if not provider_func:
                    continue

                result = await provider_func(message, context)

                if result and "error" not in result:
                    processing_time = int((time.time() - start_time) * 1000)
                    result["processing_time"] = processing_time
                    result["provider"] = current_provider

                    logger.info(
                        f"AI response generated successfully with {current_provider} in {processing_time}ms"
                    )
                    return result

            except Exception as e:
                logger.warning(f"Provider {current_provider} failed: {str(e)}")
                continue

        # All providers failed - return fallback
        logger.error("All AI providers failed, returning fallback response")
        return {
            "response": "Mi dispiace, sto avendo difficoltà tecniche. Per favore riprova tra qualche istante o contatta il supporto umano.",
            "confidence": 0,
            "provider": "fallback",
            "sentiment": "neutral",
            "processing_time": int((time.time() - start_time) * 1000),
        }

    async def _groq_response(self, message: str, context: Optional[str]) -> Dict[str, Any]:
        """GROQ AI provider - FREE and FAST with Llama models!"""
        try:
            from app.core.llm.groq_client import GroqClient

            # Get GROQ API keys with rotation
            groq_keys = settings.groq_api_keys
            if not groq_keys:
                raise ValueError("No GROQ_API_KEY configured")

            # Rotate through keys for rate limiting
            api_key = groq_keys[self._groq_key_index % len(groq_keys)]
            self._groq_key_index += 1

            # Initialize GROQ client with Llama 3.3 70B (best model)
            client = GroqClient(
                api_key=api_key,
                model="llama-3.3-70b",
                temperature=0.7,
                max_tokens=500
            )

            # Build prompt
            full_prompt = message
            if context:
                full_prompt = f"Contesto precedente:\n{context}\n\nUtente: {message}"

            # Generate response
            ai_response = await client.generate(
                prompt=full_prompt,
                system_prompt=self.system_context
            )

            confidence = self._calculate_confidence(ai_response, message)
            sentiment = self._analyze_sentiment(message)

            return {
                "response": ai_response.strip(),
                "confidence": confidence,
                "sentiment": sentiment,
            }

        except Exception as e:
            logger.error(f"GROQ provider error: {str(e)}")
            raise

    async def _gemini_response(self, message: str, context: Optional[str]) -> Dict[str, Any]:
        """Google Gemini AI provider"""
        try:
            # Use resolved property with fallback to GOOGLE_API_KEY
            api_key = settings.google_api_key_resolved

            if not api_key:
                raise ValueError("GOOGLE_AI_API_KEY or GOOGLE_API_KEY not configured")

            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

            # Build prompt with context
            full_prompt = f"{self.system_context}\n\nUtente: {message}"
            if context:
                full_prompt = f"{self.system_context}\n\nContesto conversazione:\n{context}\n\nUtente: {message}"

            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500,
                    "topP": 0.8,
                    "topK": 40,
                },
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(api_url, json=payload)

                if response.status_code == 200:
                    data = response.json()

                    if "candidates" in data and len(data["candidates"]) > 0:
                        ai_response = data["candidates"][0]["content"]["parts"][0]["text"]

                        # Calculate confidence based on response quality
                        confidence = self._calculate_confidence(ai_response, message)
                        sentiment = self._analyze_sentiment(message)

                        return {
                            "response": ai_response.strip(),
                            "confidence": confidence,
                            "sentiment": sentiment,
                        }

                error_text = response.text
                raise Exception(f"Gemini API error: {response.status_code} - {error_text}")

        except Exception as e:
            logger.error(f"Gemini provider error: {str(e)}")
            raise

    async def _openrouter_response(self, message: str, context: Optional[str]) -> Dict[str, Any]:
        """OpenRouter provider (GPT access)"""
        try:
            from openai import AsyncOpenAI

            api_key = os.getenv("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)

            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not configured")

            # OpenRouter client
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )

            messages = [
                {"role": "system", "content": self.system_context},
                {"role": "user", "content": message},
            ]

            if context:
                messages.insert(1, {"role": "assistant", "content": f"Contesto: {context}"})

            response = await client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                extra_headers={
                    "HTTP-Referer": "https://studiocentos.it",
                    "X-Title": "StudioCentOS AI Support",
                },
            )

            ai_response = response.choices[0].message.content
            confidence = self._calculate_confidence(ai_response, message)
            sentiment = self._analyze_sentiment(message)

            return {
                "response": ai_response.strip(),
                "confidence": confidence,
                "sentiment": sentiment,
            }

        except Exception as e:
            logger.error(f"OpenRouter provider error: {str(e)}")
            raise

    async def _huggingface_response(self, message: str, context: Optional[str]) -> Dict[str, Any]:
        """HuggingFace Inference Providers API (NEW router.huggingface.co)"""
        try:
            # Try both environment variable names
            api_key = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_API_KEY") or settings.huggingface_token_resolved

            if not api_key:
                raise ValueError("HUGGINGFACE_TOKEN not configured")

            # Build messages in OpenAI format (new HuggingFace router is OpenAI-compatible)
            messages = [
                {"role": "system", "content": self.system_context}
            ]
            if context:
                messages.append({"role": "system", "content": f"Contesto: {context}"})
            messages.append({"role": "user", "content": message})

            # NEW HuggingFace Inference Providers endpoint (OpenAI-compatible)
            api_url = "https://router.huggingface.co/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "meta-llama/Llama-3.2-3B-Instruct",  # Free chat model
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(api_url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    ai_response = data["choices"][0]["message"]["content"]

                    confidence = self._calculate_confidence(ai_response, message)
                    sentiment = self._analyze_sentiment(message)

                    return {
                        "response": ai_response.strip(),
                        "confidence": confidence,
                        "sentiment": sentiment,
                    }

                error_text = response.text
                raise Exception(f"HuggingFace API error: {response.status_code} - {error_text}")

        except Exception as e:
            logger.error(f"HuggingFace provider error: {str(e)}")
            raise

    async def _ollama_response(self, message: str, context: Optional[str]) -> Dict[str, Any]:
        """Ollama local AI provider"""
        try:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

            full_prompt = f"{self.system_context}\n\nUtente: {message}"
            if context:
                full_prompt = f"{self.system_context}\n\nContesto: {context}\n\nUtente: {message}"

            payload = {
                "model": "llama2",
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 500},
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ollama_url}/api/generate",
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("response", "")

                    confidence = self._calculate_confidence(ai_response, message)
                    sentiment = self._analyze_sentiment(message)

                    return {
                        "response": ai_response.strip(),
                        "confidence": confidence,
                        "sentiment": sentiment,
                    }

                raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Ollama provider error: {str(e)}")
            raise

    def _calculate_confidence(self, response: str, question: str) -> int:
        """Calculate confidence score based on response quality"""
        confidence = 50  # Base confidence

        # Increase confidence for longer, detailed responses
        if len(response) > 100:
            confidence += 20

        # Increase if response contains specific StudioCentOS terms
        studiocentos_terms = ["react", "fastapi", "app mobile", "e-commerce", "consulenza", "prenotazione", "scafati", "salerno", "campania"]
        matches = sum(1 for term in studiocentos_terms if term.lower() in response.lower())
        confidence += min(matches * 5, 20)

        # Decrease if response is too short
        if len(response) < 50:
            confidence -= 20

        # Ensure confidence is between 0-100
        return max(0, min(100, confidence))

    def _analyze_sentiment(self, message: str) -> str:
        """Simple sentiment analysis"""
        message_lower = message.lower()

        negative_words = ["problema", "errore", "non funziona", "bug", "aiuto", "urgente"]
        positive_words = ["grazie", "ottimo", "perfetto", "bene", "funziona"]

        negative_count = sum(1 for word in negative_words if word in message_lower)
        positive_count = sum(1 for word in positive_words if word in message_lower)

        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
