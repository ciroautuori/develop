"""
Exercise Preferences API Router

Endpoints for managing user exercise likes/dislikes/ratings.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models import ExercisePreferenceModel
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/exercises/preferences", tags=["exercise_preferences"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExercisePreferenceCreate(BaseModel):
    """Request model for creating/updating exercise preference."""
    exercise_id: str = Field(..., description="Exercise ID from database")
    exercise_name: str = Field(..., description="Exercise name")
    preference: str = Field(..., pattern="^(like|dislike|neutral)$", description="Preference type")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    reason: Optional[str] = Field(None, description="Reason for preference")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class ExercisePreferenceResponse(BaseModel):
    """Response model for exercise preference."""
    id: str
    user_id: str
    exercise_id: str
    exercise_name: str
    preference: str
    rating: Optional[int]
    reason: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExercisePreferencesSummary(BaseModel):
    """Summary of user's exercise preferences."""
    total: int
    liked: int
    disliked: int
    neutral: int
    average_rating: Optional[float]
    top_liked: List[dict]
    top_disliked: List[dict]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("", response_model=ExercisePreferenceResponse)
async def set_exercise_preference(
    preference: ExercisePreferenceCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Set or update preference for an exercise.

    Creates new preference or updates existing one.
    """
    try:
        # Check if preference exists
        existing = db.query(ExercisePreferenceModel).filter(
            and_(
                ExercisePreferenceModel.user_id == str(current_user.id),
                ExercisePreferenceModel.exercise_id == preference.exercise_id
            )
        ).first()

        if existing:
            # Update existing
            existing.preference = preference.preference
            existing.rating = preference.rating
            existing.reason = preference.reason
            existing.metadata = preference.metadata
            existing.updated_at = datetime.now()
            db.commit()
            db.refresh(existing)

            logger.info(f"Updated preference for {preference.exercise_name}: {preference.preference}")
            return existing
        else:
            # Create new
            new_pref = ExercisePreferenceModel(
                id=str(uuid.uuid4()),
                user_id=str(current_user.id),
                exercise_id=preference.exercise_id,
                exercise_name=preference.exercise_name,
                preference=preference.preference,
                rating=preference.rating,
                reason=preference.reason,
                metadata=preference.metadata
            )
            db.add(new_pref)
            db.commit()
            db.refresh(new_pref)

            logger.info(f"Created preference for {preference.exercise_name}: {preference.preference}")
            return new_pref

    except Exception as e:
        db.rollback()
        logger.error(f"Error setting preference: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{exercise_id}/like")
async def like_exercise(
    exercise_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    exercise_name: str = Query(..., description="Exercise name"),
    rating: Optional[int] = Query(None, ge=1, le=5),
    reason: Optional[str] = Query(None),
):
    """Quick endpoint to like an exercise."""
    return await set_exercise_preference(
        ExercisePreferenceCreate(
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            preference="like",
            rating=rating,
            reason=reason
        ),
        current_user,
        db
    )


@router.post("/{exercise_id}/dislike")
async def dislike_exercise(
    exercise_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    exercise_name: str = Query(..., description="Exercise name"),
    reason: Optional[str] = Query(None),
):
    """Quick endpoint to dislike an exercise."""
    return await set_exercise_preference(
        ExercisePreferenceCreate(
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            preference="dislike",
            reason=reason
        ),
        current_user,
        db
    )


@router.get("", response_model=List[ExercisePreferenceResponse])
async def get_exercise_preferences(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    preference_filter: Optional[str] = Query(None, pattern="^(like|dislike|neutral)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Get user's exercise preferences.

    Optionally filter by preference type (like/dislike/neutral).
    """
    query = db.query(ExercisePreferenceModel).filter(
        ExercisePreferenceModel.user_id == str(current_user.id)
    )

    if preference_filter:
        query = query.filter(ExercisePreferenceModel.preference == preference_filter)

    preferences = query.order_by(
        ExercisePreferenceModel.updated_at.desc()
    ).offset(offset).limit(limit).all()

    return preferences


@router.get("/summary", response_model=ExercisePreferencesSummary)
async def get_preferences_summary(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get summary of user's exercise preferences."""
    preferences = db.query(ExercisePreferenceModel).filter(
        ExercisePreferenceModel.user_id == str(current_user.id)
    ).all()

    liked = [p for p in preferences if p.preference == "like"]
    disliked = [p for p in preferences if p.preference == "dislike"]
    neutral = [p for p in preferences if p.preference == "neutral"]

    # Calculate average rating
    ratings = [p.rating for p in preferences if p.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else None

    # Top liked/disliked
    top_liked = sorted(liked, key=lambda x: x.rating or 0, reverse=True)[:5]
    top_disliked = disliked[:5]

    return ExercisePreferencesSummary(
        total=len(preferences),
        liked=len(liked),
        disliked=len(disliked),
        neutral=len(neutral),
        average_rating=round(avg_rating, 2) if avg_rating else None,
        top_liked=[{"id": p.exercise_id, "name": p.exercise_name, "rating": p.rating} for p in top_liked],
        top_disliked=[{"id": p.exercise_id, "name": p.exercise_name, "reason": p.reason} for p in top_disliked]
    )


@router.get("/{exercise_id}", response_model=Optional[ExercisePreferenceResponse])
async def get_exercise_preference(
    exercise_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get preference for a specific exercise."""
    preference = db.query(ExercisePreferenceModel).filter(
        and_(
            ExercisePreferenceModel.user_id == str(current_user.id),
            ExercisePreferenceModel.exercise_id == exercise_id
        )
    ).first()

    return preference


@router.delete("/{exercise_id}")
async def delete_exercise_preference(
    exercise_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Delete preference for an exercise."""
    preference = db.query(ExercisePreferenceModel).filter(
        and_(
            ExercisePreferenceModel.user_id == str(current_user.id),
            ExercisePreferenceModel.exercise_id == exercise_id
        )
    ).first()

    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    db.delete(preference)
    db.commit()

    return {"message": "Preference deleted", "exercise_id": exercise_id}


@router.get("/liked/ids")
async def get_liked_exercise_ids(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get list of liked exercise IDs (for filtering in workout generation)."""
    liked = db.query(ExercisePreferenceModel.exercise_id).filter(
        and_(
            ExercisePreferenceModel.user_id == str(current_user.id),
            ExercisePreferenceModel.preference == "like"
        )
    ).all()

    return {"liked_ids": [l[0] for l in liked]}


@router.get("/disliked/ids")
async def get_disliked_exercise_ids(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get list of disliked exercise IDs (for filtering in workout generation)."""
    disliked = db.query(ExercisePreferenceModel.exercise_id).filter(
        and_(
            ExercisePreferenceModel.user_id == str(current_user.id),
            ExercisePreferenceModel.preference == "dislike"
        )
    ).all()

    return {"disliked_ids": [d[0] for d in disliked]}
