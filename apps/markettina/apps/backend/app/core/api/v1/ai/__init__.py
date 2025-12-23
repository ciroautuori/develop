"""
MARKETTINA v2.0 - AI API Routes

Unified AI endpoints for:
- AI Marketing (content generation, image generation, etc.)
- RAG (Retrieval Augmented Generation)
- AI Support (chatbot)
"""

from .ai_marketing import router as ai_marketing_router
from .ai_support import router as ai_support_router
from .rag import router as rag_router

__all__ = [
    "ai_marketing_router",
    "ai_support_router",
    "rag_router",
]
