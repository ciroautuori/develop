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
from src.application.dtos.dtos import UserDTO, OnboardingRequestDTO
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.ai.user_context_rag import get_user_context_rag

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


@router.put("/me", response_model=Dict[str, Any])
async def update_user_profile(
    updates: Dict[str, Any],
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Update current user profile.

    Allows updating personal info, goals, equipment, and preferences.
    """
    try:
        # Update allowed fields - comprehensive list for all wizard data
        allowed_fields = [
            # Basic info
            'name', 'age', 'weight_kg', 'height_cm', 'sex',
            # Goals
            'target_return_date', 'primary_goal', 'goals_description',
            # Equipment & Preferences
            'equipment_available', 'preferred_training_time', 'session_duration_minutes',
            # Training Goals (from TrainingGoalsStep)
            'training_experience', 'training_years', 'secondary_goals',
            'available_days', 'preferred_time', 'intensity_preference',
            # Lifestyle (from LifestyleStep)
            'activity_level', 'work_type', 'work_hours_per_day', 'commute_active',
            'stress_level', 'stress_sources', 'sleep_hours', 'sleep_quality',
            'sleep_schedule', 'recovery_capacity', 'health_conditions', 'supplements_used',
            # Nutrition Goals (from NutritionGoalsStep)
            'nutrition_goal', 'diet_type', 'calorie_preference', 'custom_calories',
            'manual_target_calories', 'manual_target_protein_g', 'manual_target_carbs_g', 'manual_target_fat_g',
            'protein_priority', 'macro_preference', 'meal_frequency', 'meal_timing',
            'intermittent_window', 'budget_preference', 'cooking_skill', 'meal_prep_available',
            'supplements_interest',
            # Allergies & Restrictions
            'allergies', 'intolerances', 'dietary_restrictions',
            # Food Preferences
            'favorite_foods', 'disliked_foods',
            # Injury details
            'injury_date', 'diagnosis', 'injury_description', 'pain_locations',
            # Baseline strength
            'baseline_deadlift_1rm', 'baseline_squat_1rm', 'baseline_front_squat_1rm',
            'baseline_bench_press_1rm', 'baseline_shoulder_press_1rm',
            'baseline_snatch_1rm', 'baseline_clean_jerk_1rm', 'baseline_pullups_max',
        ]

        for field, value in updates.items():
            if field in allowed_fields and hasattr(current_user, field):
                setattr(current_user, field, value)

        # Persist updates (CurrentUser is an ORM model bound to the session)
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        user_repo = get_user_repository(db)
        updated_entity = user_repo.get_by_id(str(current_user.id))

        # Update RAG context with new profile data
        try:
            rag = get_user_context_rag()

            # Create context text based on updates
            context_text = "Aggiornamento profilo utente:\n"
            for k, v in updates.items():
                context_text += f"- {k}: {v}\n"

            # Store in 'preference' category (general profile info)
            rag.store_context(
                user_id=current_user.id,
                text=context_text,
                category="preference",
                metadata={
                    "type": "profile_update",
                    "timestamp": datetime.now().isoformat(),
                    "updates": updates
                }
            )
        except Exception as e:
            print(f"⚠️ Failed to update RAG context: {e}")

        return {
            "success": True,
            "user": updated_entity.to_dict() if updated_entity else {"id": str(current_user.id)}
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore aggiornamento profilo: {str(e)}"
        )


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
