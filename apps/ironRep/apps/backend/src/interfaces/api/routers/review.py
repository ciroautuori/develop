"""
Review API Router

Endpoints for weekly review and progression.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.infrastructure.persistence.database import get_db
from src.infrastructure.config.dependencies import (
    get_weekly_review_use_case,
    get_kpi_repository,
    container
)
from src.application.dtos.dtos import KPIDTO, WeeklyReviewResponseDTO
from src.infrastructure.security.security import CurrentUser

router = APIRouter()


@router.post("/weekly/{week}")
async def weekly_review(
    week: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Execute weekly review.

    Calculates KPIs, evaluates progression, generates next week plan.
    """
    try:
        # Get use case
        review_usecase = container.get_weekly_review_usecase(db, user_id=current_user.id)

        # Execute review
        result = await review_usecase.execute(week)

        return {
            "success": True,
            "week_number": result.week_number,
            "kpi": result.kpi.dict(),
            "progression_decision": result.progression_decision,
            "next_week_program": [w.dict() for w in result.next_week_program],
            "chart_data": result.chart_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing review: {str(e)}"
        )


@router.get("/kpis")
async def get_all_kpis(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get all KPIs for user."""
    try:
        kpi_repo = container.get_kpi_repository(db)
        kpis = kpi_repo.get_all_for_user(current_user.id)

        return {
            "success": True,
            "count": len(kpis),
            "kpis": [kpi.to_dict() for kpi in kpis]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching KPIs: {str(e)}"
        )
