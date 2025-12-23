"""
Exercises API Router
Endpoints for exercise library
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models import ExerciseModel
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


class ExerciseResponse(BaseModel):
    id: str
    name: str
    category: str
    difficulty: str
    phases: Optional[List[str]] = []
    equipment: Optional[List[str]] = []
    target_muscles: Optional[List[str]] = []
    coaching_cues: Optional[List[str]] = []
    sets_range_min: Optional[int] = None
    sets_range_max: Optional[int] = None
    reps_range_min: Optional[int] = None
    reps_range_max: Optional[int] = None
    rest_seconds: Optional[int] = None
    video_url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ExerciseResponse])
def get_all_exercises(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all exercises with optional filters"""
    try:
        query = db.query(ExerciseModel).filter(ExerciseModel.is_active == True)

        if category:
            query = query.filter(ExerciseModel.category == category)

        if difficulty:
            query = query.filter(ExerciseModel.difficulty == difficulty)

        exercises = query.offset(offset).limit(limit).all()

        # Convert to response format
        result = []
        for ex in exercises:
            result.append({
                "id": ex.id,
                "name": ex.name,
                "category": ex.category,
                "difficulty": ex.difficulty,
                "phases": ex.phases or [],
                "equipment": [e for e in (ex.equipment or []) if e is not None],
                "target_muscles": [],  # Not in model
                "coaching_cues": ex.coaching_cues or [],
                "sets_range_min": ex.sets_range_min,
                "sets_range_max": ex.sets_range_max,
                "reps_range_min": ex.reps_range_min,
                "reps_range_max": ex.reps_range_max,
                "rest_seconds": ex.rest_seconds,
                "video_url": ex.video_url,
                "description": ex.description
            })

        return result
    except Exception as e:
        logger.error(f"Error fetching exercises: {str(e)}")
        # Return empty array instead of crashing
        return []


@router.get("/phase/{phase_name}", response_model=List[ExerciseResponse])
def get_exercises_by_phase(
    phase_name: str,
    db: Session = Depends(get_db)
):
    """Get exercises for a specific phase"""
    # Query exercises where phase_name is in the phases JSON array
    exercises = db.query(ExerciseModel).filter(
        ExerciseModel.is_active == True
    ).all()

    # Filter in Python for JSON array contains
    filtered = [ex for ex in exercises if phase_name in (ex.phases or [])]

    result = []
    for ex in filtered:
        result.append({
            "id": ex.id,
            "name": ex.name,
            "category": ex.category,
            "difficulty": ex.difficulty,
            "phases": ex.phases or [],
            "equipment": ex.equipment or [],
            "target_muscles": [],
            "coaching_cues": ex.coaching_cues or [],
            "sets_range_min": ex.sets_range_min,
            "sets_range_max": ex.sets_range_max,
            "reps_range_min": ex.reps_range_min,
            "reps_range_max": ex.reps_range_max,
            "rest_seconds": ex.rest_seconds,
            "video_url": ex.video_url,
            "description": ex.description
        })

    return result


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise_by_id(
    exercise_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific exercise by ID"""
    exercise = db.query(ExerciseModel).filter(
        ExerciseModel.id == exercise_id,
        ExerciseModel.is_active == True
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    return {
        "id": exercise.id,
        "name": exercise.name,
        "category": exercise.category,
        "difficulty": exercise.difficulty,
        "phases": exercise.phases or [],
        "equipment": exercise.equipment or [],
        "target_muscles": [],
        "coaching_cues": exercise.coaching_cues or [],
        "sets_range_min": exercise.sets_range_min,
        "sets_range_max": exercise.sets_range_max,
        "reps_range_min": exercise.reps_range_min,
        "reps_range_max": exercise.reps_range_max,
        "rest_seconds": exercise.rest_seconds,
        "video_url": exercise.video_url,
        "description": exercise.description
    }
