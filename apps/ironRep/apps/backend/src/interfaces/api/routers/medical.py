"""
Medical Agent API Router

Endpoints for medical monitoring and check-in.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from src.infrastructure.config.dependencies import container
from src.infrastructure.persistence.database import get_db
from src.infrastructure.security.security import CurrentUser


router = APIRouter(prefix="/api/medical", tags=["medical"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class MedicalQuestionRequest(BaseModel):
    """Request model for medical question."""
    question: str
    session_id: str | None = None


class CheckInMessageRequest(BaseModel):
    """Request model for check-in conversation message."""
    session_id: str
    message: str


class PainCheckinRequest(BaseModel):
    """Request model for pain assessment check-in."""
    pain_level: int  # 0-10
    pain_locations: list[str]
    notes: str = ""
    # message: str # Removing message as it is not part of pain assessment data structure usually, 
                  # but looking at usage it seems distinct from checkin message.
                  # If this endpoint is purely for pain logging, message might be redundant or misplaced.
                  # However, if it's used to "chat" while logging pain, we need to check usage.
                  # The audit said "PainCheckinRequest has extra field mobility_score".
                  # Domain entity PainAssessment has mobility_score? Let's check usage in line 245.
                  # "mobility_score=request.mobility_score" -> It IS used.
                  # So the audit might be wrong or referring to an older version of domain entity.
                  # I will make mobility_score optional to be safe, but keep it.
                  # I will remove 'message' if it's unused in submit_pain_checkin. 
                  # Line 232 submit_pain_checkin does NOT use request.message.
                  # So I will remove `message: str` from here.


# ============================================================================
# MEDICAL CHAT ENDPOINTS
# ============================================================================

@router.post("/ask", response_model=Dict[str, Any])
async def ask_medical_agent(
    request: MedicalQuestionRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Ask medical agent a question about recovery/symptoms.

    Args:
        request: Contains question and optional session_id

    Returns:
        dict with answer, session_id, suggested_actions
    """
    try:
        # Get medical use case
        usecase = container.get_ask_medical_usecase(
            db,
            user_id=current_user.id,
            session_id=request.session_id
        )

        # Execute
        response = await usecase.execute(request.question)

        return {
            "success": True,
            "answer": response.answer,
            "session_id": usecase.get_session_id(),
            "suggested_actions": response.suggested_actions,
            "timestamp": response.timestamp.isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error asking medical agent: {str(e)}"
        )


# ============================================================================
# MEDICAL CHECK-IN ENDPOINTS (Conversational)
# ============================================================================

@router.post("/checkin/start", response_model=Dict[str, Any])
async def start_medical_checkin(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Start conversational medical check-in.

    Returns:
        dict with session_id and initial greeting
    """
    try:
        usecase = container.get_checkin_conversational_usecase(db, user_id=current_user.id)
        result = await usecase.start_checkin()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting medical check-in: {str(e)}"
        )


@router.post("/checkin/message", response_model=Dict[str, Any])
async def send_checkin_message(
    request: CheckInMessageRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Send message in ongoing medical check-in.

    Args:
        request: Contains session_id and user message

    Returns:
        dict with agent response and completion status
    """
    try:
        usecase = container.get_checkin_conversational_usecase(db, user_id=current_user.id)
        result = await usecase.continue_conversation(
            session_id=request.session_id,
            user_message=request.message
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing check-in message: {str(e)}"
        )


@router.get("/checkin/status/{session_id}", response_model=Dict[str, Any])
async def get_checkin_status(
    session_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get status of medical check-in session.

    Args:
        session_id: Check-in session ID

    Returns:
        dict with session status and extracted data
    """
    try:
        usecase = container.get_checkin_conversational_usecase(db, user_id=current_user.id)
        result = usecase.get_session_status(session_id)

        return {
            "success": True,
            **result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching check-in status: {str(e)}"
        )


# ============================================================================
# MEDICAL HISTORY ENDPOINTS
# ============================================================================

@router.get("/history/{session_id}", response_model=Dict[str, Any])
async def get_medical_history(
    session_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get medical conversation history.

    Args:
        session_id: Session ID

    Returns:
        dict with conversation history
    """
    try:
        usecase = container.get_ask_medical_usecase(
            db,
            user_id=current_user.id,
            session_id=session_id
        )

        history = usecase.get_chat_history()

        return {
            "success": True,
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
                }
                for msg in history
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching medical history: {str(e)}"
        )


@router.post("/pain-checkin", response_model=Dict[str, Any])
async def submit_pain_checkin(
    request: PainCheckinRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Submit daily pain assessment check-in."""
    try:
        from datetime import datetime
        from src.domain.entities.pain_assessment import PainAssessment

        pain_repo = container.get_pain_repository(db)

        if request.pain_level < 0 or request.pain_level > 10:
            raise HTTPException(status_code=422, detail="pain_level must be between 0 and 10")

        if not request.pain_locations:
            raise HTTPException(status_code=422, detail="pain_locations must not be empty")

        # Create pain assessment
        assessment = PainAssessment(
            user_id=current_user.id,
            date=datetime.now(),
            pain_level=request.pain_level,
            pain_locations=request.pain_locations,
            notes=request.notes
        )

        # Save to database
        saved = pain_repo.save(assessment)

        return {
            "success": True,
            "status": "pain_logged",
            "message": f"Pain check-in salvato: livello {request.pain_level}/10",
            "assessment": saved.to_dict()
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving pain check-in: {str(e)}"
        )


@router.get("/pain-history/{days}", response_model=Dict[str, Any])
async def get_pain_history(
    days: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get pain history for last N days."""
    try:
        pain_repo = container.get_pain_repository(db)
        assessments = pain_repo.get_last_n_days(current_user.id, days)

        return {
            "success": True,
            "count": len(assessments),
            "assessments": [a.to_dict() for a in assessments]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching pain history: {str(e)}"
        )
