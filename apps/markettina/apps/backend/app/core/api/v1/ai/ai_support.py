"""
MARKETTINA v2.0 - AI Customer Support API Endpoints
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import get_api_key_header
from app.domain.ai_support.service import SupportService

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(get_api_key_header())])

# Pydantic Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    context: str | None = Field(None, description="Conversation context", max_length=5000)
    provider: str = Field(default="groq", description="AI provider (groq [FREE], huggingface, gemini, openrouter, ollama)")

class ChatResponse(BaseModel):
    response: str
    confidence: int
    sentiment: str
    provider: str
    processing_time: int

# Service instance
support_service = SupportService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate AI support response for customer query

    - **message**: Customer message/question
    - **context**: Optional conversation history
    - **provider**: Preferred AI provider (groq [FREE primary], huggingface, gemini, openrouter, ollama)

    **Provider Priority**: GROQ (FREE!) → HuggingFace → Gemini → OpenRouter → Ollama (local)
    """
    try:
        result = await support_service.chat(
            message=request.message,
            context=request.context,
            provider=request.provider
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error("chat_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {e!s}"
        )


@router.get("/providers")
async def get_providers():
    """
    Get available AI providers and their status
    """
    try:
        health = await support_service.health_check()
        return health
    except Exception as e:
        logger.error("providers_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check providers: {e!s}"
        )


@router.get("/")
async def support_root():
    """Support service root endpoint"""
    return {
        "service": "support",
        "status": "available",
        "endpoints": [
            "/chat - POST - Generate AI support response",
            "/providers - GET - Check provider availability"
        ]
    }
