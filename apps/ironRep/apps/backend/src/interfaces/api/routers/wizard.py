"""
Wizard API Router

Endpoints for conversational onboarding wizard.
Integrates with AgentOrchestrator to initialize all agents after completion.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
import uuid
import logging

from src.infrastructure.persistence.database import get_db
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.config.dependencies import get_wizard_agent as get_wizard_from_container
from src.infrastructure.ai.user_context_rag import get_user_context_rag

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wizard", tags=["wizard"])


# Request models
class WizardMessageRequest(BaseModel):
    """Request model for wizard message."""
    session_id: str
    message: str


class StartWizardRequest(BaseModel):
    """Request model for starting wizard."""
    biometrics: Dict[str, Any] = None


@router.post("/start", response_model=Dict[str, Any])
async def start_wizard_interview(
    request: StartWizardRequest = None,
    current_user: CurrentUser = None,
    db: Session = Depends(get_db)
):

    """
    Start a new wizard interview session.

    User is already authenticated - we have their email and ID.

    Returns:
        dict with session_id and initial greeting
    """
    try:
        wizard = get_wizard_from_container(db, str(current_user.id))
        session_id = str(uuid.uuid4())

        # Pass user info to wizard - no need to ask for email!
        result = await wizard.start_interview(
            user_id=str(current_user.id),
            session_id=session_id,
            user_email=current_user.email,
            user_name=getattr(current_user, 'name', None),
            biometrics=request.biometrics
        )

        return result

    except Exception as e:
        logger.error(f"Error starting wizard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting wizard: {str(e)}"
        )


@router.post("/message", response_model=Dict[str, Any])
async def send_wizard_message(
    request: WizardMessageRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Send message to wizard and get response.

    When wizard completes:
    - Creates/updates user in DB
    - Triggers AgentOrchestrator to initialize all agents
    - Returns initial plans (medical, workout, nutrition)

    Args:
        request: Contains session_id and user message

    Returns:
        dict with wizard response, interview status, and initialization result
    """
    try:
        wizard = get_wizard_from_container(db, str(current_user.id))

        result = await wizard.process_message(
            session_id=request.session_id,
            user_message=request.message
        )

        # Log completion
        if result.get("completed"):
            logger.info(f"Wizard completed for user {current_user.id}")
            if result.get("initialization"):
                logger.info(f"Agents initialized: {result['initialization'].get('success')}")

        return result

    except Exception as e:
        logger.error(f"Error processing wizard message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing wizard message: {str(e)}"
        )


@router.get("/status/{session_id}", response_model=Dict[str, Any])
async def get_wizard_status(
    session_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get status of wizard interview session.

    Args:
        session_id: Wizard session ID

    Returns:
        dict with session status and collected data
    """
    try:
        wizard = get_wizard_from_container(db, str(current_user.id))
        status = wizard.get_session_status(session_id)

        return {
            "success": True,
            **status
        }

    except Exception as e:
        logger.error(f"Error fetching wizard status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching wizard status: {str(e)}"
        )


@router.get("/context-summary", response_model=Dict[str, Any])
async def get_user_context_summary(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get summary of stored user context from RAG.

    Returns:
        dict with context counts per category
    """
    try:
        rag = get_user_context_rag()
        summary = rag.get_context_summary(str(current_user.id))

        return {
            "success": True,
            "user_id": str(current_user.id),
            **summary
        }

    except Exception as e:
        logger.error(f"Error fetching context summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching context summary: {str(e)}"
        )
