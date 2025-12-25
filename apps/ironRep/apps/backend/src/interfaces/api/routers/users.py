"""
Users API Router

Endpoints for user management, onboarding, and profile.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from datetime import datetime
from src.infrastructure.persistence.database import get_db
from src.infrastructure.config.dependencies import get_user_repository, get_onboarding_use_case
from src.application.dtos.dtos import (
    UserDTO, 
    OnboardingRequestDTO,
    BiometricsUpdateDTO,
    MedicalUpdateDTO,
    GoalsUpdateDTO
)
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.ai.user_context_rag import get_user_context_rag
from src.infrastructure.external.google_fit_service import GoogleFitService
from src.infrastructure.external.google_oauth_service import google_oauth_service

router = APIRouter()


@router.post("/onboarding", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def onboard_user(
    request: OnboardingRequestDTO,
    db: Session = Depends(get_db)
):
    """
    Complete user onboarding.

    Creates new user profile with injury history, baseline strength, and preferences.
    """
    try:
        onboarding_usecase = get_onboarding_use_case(db)

        # Validate data
        errors = onboarding_usecase.validate_onboarding_data(request.dict())
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"validation_errors": errors}
            )

        # Execute onboarding
        user = await onboarding_usecase.execute(request.dict())

        return {
            "success": True,
            "user": user.to_dict(),
            "message": "Onboarding completato con successo"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante onboarding: {str(e)}"
        )


# NOTE: /me routes MUST be defined BEFORE /{user_id} routes
# otherwise FastAPI will match "me" as a user_id parameter

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_profile(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile.

    Returns complete user profile including baseline strength and preferences.
    """
    user_repo = get_user_repository(db)
    user_entity = user_repo.get_by_id(str(current_user.id))
    return {"success": True, "user": user_entity.to_dict() if user_entity else {"id": str(current_user.id)}}


@router.patch("/me/biometrics", response_model=Dict[str, Any])
async def update_biometrics(
    request: BiometricsUpdateDTO,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Update biometric data (age, weight, height, sex).
    """
    try:
        user_repo = get_user_repository(db)
        updates = request.dict(exclude_unset=True)
        
        if not updates:
             return {"success": True, "message": "No changes provided"}

        for key, value in updates.items():
            setattr(current_user, key, value)
            
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        # Update RAG
        rag = get_user_context_rag()
        rag.store_context(
            user_id=current_user.id,
            text=f"Updated Biometrics: {updates}",
            category="history",
            metadata={"source": "patch_biometrics"}
        )

        return {"success": True, "user": user_repo.get_by_id(str(current_user.id)).to_dict()}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating biometrics: {str(e)}"
        )

@router.patch("/me/medical", response_model=Dict[str, Any])
async def update_medical(
    request: MedicalUpdateDTO,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Update medical/injury status.
    """
    try:
        user_repo = get_user_repository(db)
        updates = request.dict(exclude_unset=True)
        
        for key, value in updates.items():
            setattr(current_user, key, value)
            
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        # Update RAG (Essential for Medical Agent)
        rag = get_user_context_rag()
        rag.store_context(
            user_id=current_user.id,
            text=f"Updated Medical Status: {updates}",
            category="medical", # Categorize strictly as medical
            metadata={"source": "patch_medical", "has_injury": request.has_injury}
        )

        return {"success": True, "user": user_repo.get_by_id(str(current_user.id)).to_dict()}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating medical data: {str(e)}"
        )

@router.patch("/me/goals", response_model=Dict[str, Any])
async def update_goals(
    request: GoalsUpdateDTO,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Update training goals and preferences.
    """
    try:
        user_repo = get_user_repository(db)
        updates = request.dict(exclude_unset=True)
        
        for key, value in updates.items():
            setattr(current_user, key, value)
            
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        # Update RAG
        rag = get_user_context_rag()
        rag.store_context(
            user_id=current_user.id,
            text=f"Updated Goals: {updates}",
            category="goal",
            metadata={"source": "patch_goals"}
        )

        return {"success": True, "user": user_repo.get_by_id(str(current_user.id)).to_dict()}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating goals: {str(e)}"
        )


@router.get("/me/sync-fit", response_model=Dict[str, Any])
async def sync_user_google_fit(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Sync biometric data from Google Fit to user profile.
    """
    if not current_user.google_account:
        return {
            "success": False,
            "message": "Nessun account Google collegato"
        }

    try:
        # Get credentials
        creds = google_oauth_service.get_credentials(
            access_token=current_user.google_account.access_token,
            refresh_token=current_user.google_account.refresh_token,
            expires_at=current_user.google_account.token_expires_at
        )

        # Update tokens if refreshed
        if creds.token != current_user.google_account.access_token:
            current_user.google_account.access_token = creds.token
            current_user.google_account.token_expires_at = creds.expiry
            db.add(current_user.google_account)
            db.commit()

        # Sync data
        fit_service = GoogleFitService(creds)
        fit_data = fit_service.sync_all_biometrics(days=30)

        updates = {}
        
        # Extract latest weight
        if fit_data.get("weight") and len(fit_data["weight"]) > 0:
            latest_weight = fit_data["weight"][0]["weight_kg"]
            current_user.weight_kg = latest_weight
            updates["weight_kg"] = latest_weight

        # Extract latest height
        if fit_data.get("height"):
            latest_height = fit_data["height"]
            current_user.height_cm = latest_height
            updates["height_cm"] = latest_height

        # Infer activity level from average steps
        avg_steps = fit_data.get("avg_steps", 0)
        activity_level = "sedentary"
        if avg_steps >= 12000:
            activity_level = "active"
        elif avg_steps >= 8000:
            activity_level = "moderate"
        elif avg_steps >= 5000:
            activity_level = "light"
        
        current_user.activity_level = activity_level
        updates["activity_level"] = activity_level

        # Update profile
        if updates:
            db.add(current_user)
            db.commit()

        return {
            "success": True,
            "message": "Sincronizzazione completata",
            "updates": updates,
            "fit_summary": {
                "weight_records": len(fit_data.get("weight", [])),
                "height": fit_data.get("height"),
                "avg_steps": avg_steps,
                "activity_level": activity_level,
                "steps_today": fit_data.get("steps", [{}])[0].get("steps", 0) if fit_data.get("steps") else 0
            }
        }

    except Exception as e:
        logger.error(f"Google Fit sync failed: {e}")
        return {
            "success": False,
            "message": f"Sincronizzazione fallita: {str(e)}"
        }


# Dynamic user_id routes - these must come AFTER static routes like /me

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID.

    Returns complete user profile including baseline strength and preferences.
    """
    try:
        user_repo = get_user_repository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )

        return {
            "success": True,
            "user": user.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero profilo: {str(e)}"
        )


@router.get("/{user_id}/stats", response_model=Dict[str, Any])
async def get_user_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user statistics and progress summary.

    Returns weeks in program, current phase, baseline vs current strength, etc.
    """
    try:
        user_repo = get_user_repository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )

        return {
            "user_id": user.id,
            "name": user.name,
            "weeks_in_program": user.get_weeks_in_program(),
            "current_phase": user.current_phase,
            "weeks_in_current_phase": user.weeks_in_current_phase,
            "has_baseline_data": user.has_baseline_strength_data(),
            "baseline_strength": {
                "deadlift_1rm": user.baseline_deadlift_1rm,
                "squat_1rm": user.baseline_squat_1rm,
                "snatch_1rm": user.baseline_snatch_1rm,
                "clean_jerk_1rm": user.baseline_clean_jerk_1rm,
                "pullups_max": user.baseline_pullups_max
            },
            "equipment_available": user.get_available_equipment_list(),
            "is_onboarded": user.is_onboarded
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero statistiche: {str(e)}"
        )


from src.domain.entities.workout_session import WorkoutPhase

@router.post("/{user_id}/phase/advance", response_model=Dict[str, Any])
async def advance_phase(
    user_id: str,
    new_phase: str,
    db: Session = Depends(get_db)
):
    """
    Manually advance user to next phase.

    Used by admin or after weekly review approval.
    """
    try:
        user_repo = get_user_repository(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )

        # Validate phase
        valid_phases = [phase.value for phase in WorkoutPhase]

        if new_phase not in valid_phases:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fase non valida. Fasi disponibili: {', '.join(valid_phases)}"
            )

        user.update_phase(new_phase)
        updated_user = user_repo.update(user)

        return {
            "success": True,
            "user_id": user_id,
            "new_phase": new_phase,
            "weeks_in_current_phase": 0,
            "message": f"Utente avanzato a {new_phase}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore avanzamento fase: {str(e)}"
        )
