"""
Workout Coach API Router

Endpoints for training programming and workout advice.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from src.infrastructure.config.dependencies import container
from src.infrastructure.persistence.database import get_db
from src.infrastructure.security.security import CurrentUser


router = APIRouter(prefix="/api/workout-coach", tags=["workout_coach"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class CoachQuestionRequest(BaseModel):
    """Request model for workout coach question."""
    question: str
    session_id: str | None = None


class GenerateProgramRequest(BaseModel):
    """Request model for weekly program generation."""
    training_days: int = 4
    focus: str | None = None  # e.g., "strength", "conditioning", "technique"


# ============================================================================
# WORKOUT COACH CHAT ENDPOINTS
# ============================================================================

@router.post("/ask", response_model=Dict[str, Any])
async def ask_workout_coach(
    request: CoachQuestionRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Ask workout coach a question about training/programming.

    Args:
        request: Contains question and optional session_id

    Returns:
        dict with answer, session_id, suggested_actions
    """
    try:
        # Get workout coach use case
        usecase = container.get_ask_workout_coach_usecase(
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
            detail=f"Error asking workout coach: {str(e)}"
        )


# ============================================================================
# PROGRAM GENERATION ENDPOINTS
# ============================================================================

@router.post("/generate-program", response_model=Dict[str, Any])
async def generate_weekly_program(
    request: GenerateProgramRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Generate weekly training program.

    Args:
        request: Contains training_days and optional focus

    Returns:
        dict with weekly program
    """
    try:
        # Get workout coach agent
        workout_coach = container.get_workout_coach(db, user_id=current_user.id)

        # Get medical clearance
        pain_repo = container.get_pain_repository(db)
        recent_pain = pain_repo.get_last_n_days(current_user.id, days=7)

        medical_clearance = {}
        if recent_pain:
            latest = recent_pain[0]
            avg_pain = sum(a.pain_level for a in recent_pain) / len(recent_pain)

            medical_clearance = {
                "pain_level": latest.pain_level,
                "phase": _determine_phase(avg_pain),
                "contraindications": _get_contraindications(latest.pain_locations)
            }

        # Generate program
        result = await workout_coach.generate_weekly_program(
            user_id=current_user.id,
            medical_clearance=medical_clearance,
            training_days=request.training_days
        )

        return {
            "success": result["success"],
            "program": result["program"],
            "training_days": request.training_days,
            "medical_clearance": medical_clearance
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating program: {str(e)}"
        )


# ============================================================================
# WORKOUT HISTORY ENDPOINTS
# ============================================================================

@router.get("/history/{session_id}", response_model=Dict[str, Any])
async def get_coach_history(
    session_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get workout coach conversation history.

    Args:
        session_id: Session ID

    Returns:
        dict with conversation history
    """
    try:
        usecase = container.get_ask_workout_coach_usecase(
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
            detail=f"Error fetching coach history: {str(e)}"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _determine_phase(avg_pain: float) -> str:
    """Determine recovery phase based on pain."""
    if avg_pain >= 7:
        return "phase_1"
    elif avg_pain >= 5:
        return "phase_2"
    elif avg_pain >= 3:
        return "phase_3"
    else:
        return "phase_4"


def _get_contraindications(pain_locations: list) -> list:
    """Get contraindicated movements based on pain locations."""
    contraindications = []

    for location in pain_locations:
        if "lombare" in location.lower() or "schiena" in location.lower():
            contraindications.extend(["flexion_under_load", "heavy_deadlifts"])
        elif "spalla" in location.lower():
            contraindications.extend(["overhead_pressing", "kipping_pullups"])
        elif "ginocchio" in location.lower():
            contraindications.extend(["running", "box_jumps"])
        elif "anca" in location.lower():
            contraindications.extend(["deep_squats", "running"])

    return list(set(contraindications))
