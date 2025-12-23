"""
Streaming API Router - SSE Endpoints for Real-Time AI Responses.

Provides Server-Sent Events endpoints for streaming agent responses.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from src.infrastructure.config.dependencies import container
from src.infrastructure.persistence.database import get_db
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.ai.streaming_service import create_streaming_service
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/stream", tags=["streaming"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class StreamQuestionRequest(BaseModel):
    """Request for streaming a question to an agent."""
    question: str
    session_id: Optional[str] = None


# ============================================================================
# STREAMING ENDPOINTS
# ============================================================================

@router.get("/medical")
async def stream_medical_response(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    question: str = Query(..., description="Question for medical agent"),
    session_id: Optional[str] = Query(None),
):
    """
    Stream response from Medical Agent.

    Returns SSE stream with tokens as they're generated.

    Event types:
    - agent_start: Agent begins processing
    - start: LLM starts generating
    - token: Individual token
    - end: LLM finished
    - agent_end: Agent processing complete
    - error: Error occurred
    """
    try:
        # Get services
        llm_service = container.get_llm_service()
        streaming_service = create_streaming_service(llm_service)
        user_context_rag = container.get_user_context_rag()

        # Get user context
        context = await user_context_rag.get_user_profile_context(str(current_user.id))

        # Medical agent system prompt
        system_prompt = """You are an AI Medical Coach specialized in sports rehabilitation.
You help athletes recover from injuries safely.

GUIDELINES:
- Always prioritize safety
- Recommend professional consultation for serious issues
- Provide evidence-based advice
- Be encouraging but realistic

Respond in the user's language (Italian if the question is in Italian)."""

        # Create streaming generator
        async def event_generator():
            async for event in streaming_service.stream_agent_response(
                agent_name="medical",
                question=question,
                context={
                    "pain_level": context.get("current_pain_level"),
                    "phase": context.get("recovery_phase"),
                    "clearance": context.get("medical_clearance")
                },
                system_prompt=system_prompt
            ):
                yield event

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workout")
async def stream_workout_response(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    question: str = Query(..., description="Question for workout coach"),
    session_id: Optional[str] = Query(None),
):
    """
    Stream response from Workout Coach Agent.
    """
    try:
        llm_service = container.get_llm_service()
        streaming_service = create_streaming_service(llm_service)
        user_context_rag = container.get_user_context_rag()

        context = await user_context_rag.get_user_profile_context(str(current_user.id))

        system_prompt = """You are an AI Workout Coach specialized in CrossFit and strength training.
You create safe, effective training programs adapted to the user's condition.

GUIDELINES:
- Respect medical clearance and contraindications
- Scale exercises appropriately
- Focus on proper technique
- Progress gradually

Respond in the user's language."""

        async def event_generator():
            async for event in streaming_service.stream_agent_response(
                agent_name="workout",
                question=question,
                context={
                    "pain_level": context.get("current_pain_level"),
                    "phase": context.get("recovery_phase"),
                    "equipment": context.get("available_equipment", []),
                    "goal": context.get("primary_goal")
                },
                system_prompt=system_prompt
            ):
                yield event

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nutrition")
async def stream_nutrition_response(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    question: str = Query(..., description="Question for nutrition agent"),
    session_id: Optional[str] = Query(None),
):
    """
    Stream response from Nutrition Agent.
    """
    try:
        llm_service = container.get_llm_service()
        streaming_service = create_streaming_service(llm_service)
        user_context_rag = container.get_user_context_rag()

        context = await user_context_rag.get_user_profile_context(str(current_user.id))

        system_prompt = """You are an AI Sports Nutritionist specialized in athlete nutrition.
You provide personalized nutrition advice for performance and recovery.

GUIDELINES:
- Consider training load and recovery needs
- Provide practical, achievable recommendations
- Include macro guidance when relevant
- Suggest specific foods and recipes

Respond in the user's language."""

        async def event_generator():
            async for event in streaming_service.stream_agent_response(
                agent_name="nutrition",
                question=question,
                context={
                    "goal": context.get("nutrition_goal"),
                    "diet_type": context.get("diet_type"),
                    "activity_level": context.get("activity_level")
                },
                system_prompt=system_prompt
            ):
                yield event

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat")
async def stream_general_chat(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    question: str = Query(..., description="General question"),
    mode: str = Query("chat", description="Chat mode: chat, medical, workout, nutrition"),
    session_id: Optional[str] = Query(None),
):
    """
    Stream response with automatic agent routing based on mode.
    """
    # Route to appropriate agent
    if mode == "medical":
        return await stream_medical_response(current_user, db, question, session_id)
    elif mode == "workout":
        return await stream_workout_response(current_user, db, question, session_id)
    elif mode == "nutrition":
        return await stream_nutrition_response(current_user, db, question, session_id)
    else:
        # General chat - use workout coach as default
        return await stream_workout_response(current_user, db, question, session_id)
