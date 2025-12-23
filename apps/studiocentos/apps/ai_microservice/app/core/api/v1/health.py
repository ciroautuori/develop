"""
Health Check Endpoint
"""

from fastapi import APIRouter
from datetime import datetime
import time

from app.core.config import settings

router = APIRouter()

_startup_time = time.time()


@router.get("/health")
async def health_check():
    """Health check endpoint - no authentication required"""
    uptime_seconds = int(time.time() - _startup_time)

    groq_keys_count = len(settings.groq_api_keys)

    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.AI_SERVICE_ENV,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.utcnow().isoformat(),
        "providers": {
            "groq": f"available ({groq_keys_count} keys)" if groq_keys_count > 0 else "not_configured",
            "huggingface": "available" if settings.huggingface_token_resolved else "not_configured",
            "gemini": "available" if settings.google_api_key_resolved else "not_configured",
            "openrouter": "available" if settings.OPENROUTER_API_KEY else "not_configured",
            "ollama": "available",
            "chromadb": "configured",
        },
        "priority": "groq (FREE & FAST!)",
        "fallback_order": ["groq", "huggingface", "gemini", "openrouter", "ollama"]
    }
