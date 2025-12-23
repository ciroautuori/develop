"""
Custom Model Service per StudioCentOS AI.

Versione PRODUCTION: usa HuggingFace Inference API invece di caricare il modello localmente.
Questo permette di usare il modello senza torch nel container Docker.
"""

import os
import httpx
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CustomModelService:
    """
    Servizio per gestire il modello custom HuggingFace via Inference API.

    In produzione usa l'Inference API per evitare di caricare il modello
    direttamente nel container (richiede ~16GB RAM + torch).
    """

    _instance: Optional['CustomModelService'] = None
    _client: Optional[httpx.AsyncClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Inizializza il servizio."""
        # Get config from env
        self.model_name = os.getenv("HUGGINGFACE_MODEL_NAME", "autuoriciro/studiocentos-ai-qwen-3b")
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN", "")
        self.use_custom = os.getenv("USE_CUSTOM_MODEL", "false").lower() == "true"

        # Inference API base URL (updated Dec 2024)
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model_name}"

        logger.info(f"CustomModelService initialized: use_custom={self.use_custom}, model={self.model_name}")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def generate_async(
        self,
        prompt: str,
        system_message: str = "Sei un esperto di content creation e social media strategy per StudioCentOS.",
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Genera contenuto usando HuggingFace Inference API (async).

        Args:
            prompt: Il prompt dell'utente
            system_message: Il messaggio di sistema
            max_new_tokens: Numero massimo di token da generare
            temperature: Temperatura per la generazione
            top_p: Top-p per nucleus sampling

        Returns:
            Il testo generato
        """
        if not self.use_custom:
            logger.warning("Custom model not enabled, returning empty")
            return ""

        if not self.hf_token:
            logger.error("HuggingFace token not configured")
            return ""

        # Format come durante il training (ChatML format per Qwen)
        formatted_prompt = (
            f"<|im_start|>system\n{system_message}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": True,
                "return_full_text": False,
            },
            "options": {
                "wait_for_model": True,  # Wait if model is loading
                "use_cache": False,
            }
        }

        try:
            client = await self._get_client()
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )

            if response.status_code == 503:
                # Model is loading, retry after a delay
                logger.info("Model is loading, waiting...")
                import asyncio
                await asyncio.sleep(20)
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )

            response.raise_for_status()
            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
            else:
                generated_text = str(result)

            # Clean up response
            if "<|im_end|>" in generated_text:
                generated_text = generated_text.split("<|im_end|>")[0].strip()

            logger.info(f"Generated {len(generated_text)} chars via Inference API")
            return generated_text

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Inference API: {e.response.status_code} - {e.response.text}")
            return ""
        except Exception as e:
            logger.error(f"Error calling Inference API: {e}")
            return ""

    def generate(
        self,
        prompt: str,
        system_message: str = "Sei un esperto di content creation e social media strategy per StudioCentOS.",
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Genera contenuto (versione sincrona).

        Per retrocompatibilità - chiama la versione async.
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In contesto async, crea nuovo task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.generate_async(prompt, system_message, max_new_tokens, temperature, top_p)
                    )
                    return future.result(timeout=120)
            else:
                return loop.run_until_complete(
                    self.generate_async(prompt, system_message, max_new_tokens, temperature, top_p)
                )
        except Exception as e:
            logger.error(f"Sync generate error: {e}")
            return ""

    async def close(self):
        """Chiudi client HTTP."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def is_available(self) -> bool:
        """Check if custom model is available and configured."""
        return self.use_custom and bool(self.hf_token) and bool(self.model_name)


# Singleton instance
custom_model_service = CustomModelService()
