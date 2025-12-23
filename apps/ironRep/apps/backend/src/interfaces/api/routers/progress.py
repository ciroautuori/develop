"""
Progress API Router

Endpoints for progress dashboard data.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.infrastructure.persistence.database import get_db
from src.infrastructure.config.dependencies import container
from src.infrastructure.security.security import CurrentUser

router = APIRouter()


@router.get("/kpis")
async def get_kpis(
    current_user: CurrentUser,
    days: int = Query(14, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get KPIs for last N days.

    Returns compliance rate, workouts completed/scheduled, avg pain, etc.
    """
    try:
        # Get repositories
        workout_repo = container.get_workout_repository(db)
        pain_repo = container.get_pain_repository(db)

        # Get workouts for period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Calculate compliance
        # Assuming 3 workouts per week as scheduled
        weeks = days / 7
        workouts_scheduled = int(weeks * 3)

        completed_workouts = workout_repo.get_completed_workouts(current_user.id)
        recent_completed = [w for w in completed_workouts
                          if w.date and w.date >= start_date]
        workouts_completed = len(recent_completed)

        compliance_rate = (workouts_completed / workouts_scheduled * 100) if workouts_scheduled > 0 else 0

        # Get pain data
        pain_assessments = pain_repo.get_last_n_days(current_user.id, days)
        avg_pain = sum(a.pain_level for a in pain_assessments) / len(pain_assessments) if pain_assessments else 0

        # Determine trend
        if len(pain_assessments) >= 2:
            recent_pain = sum(a.pain_level for a in pain_assessments[:len(pain_assessments)//2]) / (len(pain_assessments)//2)
            older_pain = sum(a.pain_level for a in pain_assessments[len(pain_assessments)//2:]) / (len(pain_assessments)//2)
            pain_trend = "improving" if recent_pain < older_pain else "stable" if recent_pain == older_pain else "worsening"
        else:
            pain_trend = "stable"

        return {
            "success": True,
            "kpis": [{
                "date": datetime.now().isoformat(),
                "compliance_rate": round(compliance_rate, 1),
                "workouts_completed": workouts_completed,
                "workouts_scheduled": workouts_scheduled,
                "avg_pain_level": round(avg_pain, 1),
                "pain_trend": pain_trend
            }]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching KPIs: {str(e)}"
        )


@router.get("/workout-history")
async def get_workout_history(
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get workout history for user.
    """
    try:
        workout_repo = container.get_workout_repository(db)
        completed_workouts = workout_repo.get_completed_workouts(current_user.id)

        # Sort by date desc
        completed_workouts.sort(key=lambda w: w.date, reverse=True)

        # Apply limit
        recent = completed_workouts[:limit]

        return {
            "success": True,
            "workouts": [w.to_dict() for w in recent]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching workout history: {str(e)}"
        )


@router.get("/dashboard")
async def get_dashboard_data(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get all data for progress dashboard.

    Returns KPIs, pain history, workout completion, etc.
    """
    try:
        # Get repositories
        pain_repo = container.get_pain_repository(db)
        kpi_repo  = container.get_kpi_repository(db)
        workout_repo = container.get_workout_repository(db)

        # Fetch data
        recent_pain = pain_repo.get_last_n_days(current_user.id, 30)
        kpis = kpi_repo.get_all_for_user(current_user.id)
        completed_workouts = workout_repo.get_completed_workouts(current_user.id)

        # Calculate stats
        total_assessments = len(recent_pain)
        avg_pain = sum(a.pain_level for a in recent_pain) / total_assessments if total_assessments > 0 else 0

        # Calculate Mobility Score (0-10)
        # Formula: Base 10 - Pain Impact + Consistency Bonus
        # Higher pain reduces mobility score. Consistent workouts increase it.
        pain_factor = avg_pain * 0.8  # Pain reduces score significantly
        consistency_factor = min(len(completed_workouts) * 0.5, 3) # Up to 3 points for consistency

        mobility_score = max(1, min(10, 10 - pain_factor + consistency_factor))

        return {
            "success": True,
            "stats": {
                "total_assessments": total_assessments,
                "avg_pain_30_days": round(avg_pain, 1),
                "total_completed_workouts": len(completed_workouts),
                "total_weeks": len(kpis),
                "mobility_score": round(mobility_score, 1)
            },
            "recent_pain": [a.to_dict() for a in recent_pain[-14:]],  # Last 2 weeks
            "kpis": [kpi.to_dict() for kpi in kpis],
            "recent_workouts": [w.to_dict() for w in completed_workouts[-10:]]  # Last 10
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard data: {str(e)}"
        )


@router.get("/pain-trends")
async def get_pain_trends(
    current_user: CurrentUser,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get pain trends for charts.
    """
    try:
        pain_repo = container.get_pain_repository(db)
        assessments = pain_repo.get_last_n_days(current_user.id, days)

        # Format for Recharts
        data = []
        for a in assessments:
            data.append({
                "date": a.date.strftime("%Y-%m-%d"),
                "painLevel": a.pain_level,
                "notes": a.notes
            })

        # Sort by date
        data.sort(key=lambda x: x["date"])

        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching pain trends: {str(e)}"
        )
