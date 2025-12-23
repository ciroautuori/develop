"""
Workouts API Router

Endpoints for retrieving workout sessions.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from src.infrastructure.persistence.database import get_db
from src.infrastructure.config.dependencies import container
from src.infrastructure.security.security import CurrentUser

router = APIRouter()


@router.get("/today")
async def get_todays_workout(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get the workout for the current day.
    """
    try:
        workout_repo = container.get_workout_repository(db)
        today = datetime.now()

        workout = workout_repo.get_for_date(current_user.id, today)

        if not workout:
            return {
                "success": True,
                "workout": None,
                "message": "No workout found for today"
            }

        return {
            "success": True,
            "workout": workout.to_dict()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching today's workout: {str(e)}"
        )


@router.get("/{workout_id}")
async def get_workout_by_id(
    workout_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get a specific workout by ID.
    """
    try:
        workout_repo = container.get_workout_repository(db)
        workout = workout_repo.get_by_id(workout_id)

        if not workout:
            raise HTTPException(status_code=404, detail="Workout not found")
            
        if workout.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to access this workout")

        return {
            "success": True,
            "workout": workout.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching workout: {str(e)}"
        )


@router.patch("/{workout_id}/exercises")
async def update_exercise_status(
    workout_id: str,
    payload: Dict[str, Any],
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Toggle completion status of an exercise.
    Payload: {"exercise_name": "Name"}
    """
    try:
        workout_repo = container.get_workout_repository(db)
        workout = workout_repo.get_by_id(workout_id)

        if not workout:
            raise HTTPException(status_code=404, detail="Workout not found")

        if workout.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to modify this workout")

        exercise_name = payload.get("exercise_name")
        if not exercise_name:
            raise HTTPException(status_code=400, detail="exercise_name required")

        found = workout.toggle_exercise_completion(exercise_name)
        if not found:
            raise HTTPException(status_code=404, detail="Exercise not found in workout")

        workout_repo.update(workout)

        return {
            "success": True,
            "workout": workout.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating exercise: {str(e)}"
        )


@router.post("/{workout_id}/complete")
async def complete_workout(
    workout_id: str,
    payload: Dict[str, Any],
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Mark workout as completed.
    Payload: {"pain_impact": 5, "feedback": "Good"}
    """
    try:
        workout_repo = container.get_workout_repository(db)
        workout = workout_repo.get_by_id(workout_id)

        if not workout:
            raise HTTPException(status_code=404, detail="Workout not found")

        if workout.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to complete this workout")

        pain_impact = payload.get("pain_impact", 0)
        feedback = payload.get("feedback", "")

        workout.mark_completed(pain_impact, feedback)
        workout_repo.update(workout)

        return {
            "success": True,
            "workout": workout.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error completing workout: {str(e)}"
        )
