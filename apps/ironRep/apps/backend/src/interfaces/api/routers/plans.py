"""
Plans API Router

Endpoints for weekly plans (Coach, Medical, Nutrition).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from src.infrastructure.persistence.database import get_db
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.persistence.repositories.weekly_plans_repository import (
    WeeklyPlansRepository,
    get_week_number
)
from src.infrastructure.config.dependencies import get_container
from src.application.services.ai_parsing_service import AIParsingService
from src.application.services.workout_template_service import WorkoutTemplateService
from src.domain.services.nutrition_calculator_service import NutritionCalculatorService

logger = logging.getLogger(__name__)

# ... (omitted code) ...



router = APIRouter(prefix="/api/plans", tags=["plans"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GenerateCoachPlanRequest(BaseModel):
    """Request model for generating coach weekly plan."""
    focus: Optional[str] = None
    days_available: Optional[int] = Field(default=4, alias="daysAvailable")
    notes: Optional[str] = None

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase


class GenerateMedicalPlanRequest(BaseModel):
    """Request model for generating medical protocol."""
    current_pain_level: Optional[int] = Field(default=None, alias="currentPainLevel")
    target_areas: Optional[List[str]] = Field(default=None, alias="targetAreas")
    notes: Optional[str] = None

    class Config:
        populate_by_name = True


class GenerateNutritionPlanRequest(BaseModel):
    """Request model for generating nutrition plan."""
    goal: Optional[str] = "maintenance"
    calorie_target: Optional[int] = Field(default=None, alias="calorieTarget")
    notes: Optional[str] = None

    class Config:
        populate_by_name = True


class CompleteSessionRequest(BaseModel):
    rating: int
    notes: Optional[str] = None
    exercises: Optional[List[Dict]] = None


class PainCheckInRequest(BaseModel):
    pain_level: int
    locations: List[str]
    red_flags: Optional[List[str]] = None
    notes: Optional[str] = None


class WeeklyReviewRequest(BaseModel):
    week_number: int
    year: int
    user_feedback: Optional[str] = None





# ============================================================================
# UNIFIED WEEKLY PLANS
# ============================================================================

@router.get("/calendar/{year}/{month}", response_model=Dict[str, Any])
async def get_month_calendar(
    year: int,
    month: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get calendar data for a month with all weekly plans."""
    repo = WeeklyPlansRepository(db)
    plans = repo.get_month_plans(str(current_user.id), year, month)

    weeks = []
    for plan in plans:
        weeks.append({
            "week_number": plan.week_number,
            "year": plan.year,
            "start_date": plan.start_date.isoformat(),
            "end_date": plan.end_date.isoformat(),
            "status": plan.status,
            "coach": plan.coach_summary,
            "medical": plan.medical_summary,
            "nutrition": plan.nutrition_summary
        })

    return {
        "year": year,
        "month": month,
        "weeks": weeks
    }


@router.get("/week/{year}/{week_number}/summary", response_model=Dict[str, Any])
async def get_week_summary(
    year: int,
    week_number: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get summary for a specific week."""
    repo = WeeklyPlansRepository(db)
    plan = repo.get_week_plan(str(current_user.id), week_number, year)

    if not plan:
        return {
            "week_number": week_number,
            "year": year,
            "start_date": None,
            "end_date": None,
            "coach": None,
            "medical": None,
            "nutrition": None
        }

    return {
        "week_number": plan.week_number,
        "year": plan.year,
        "start_date": plan.start_date.isoformat(),
        "end_date": plan.end_date.isoformat(),
        "coach": plan.coach_summary,
        "medical": plan.medical_summary,
        "nutrition": plan.nutrition_summary
    }


# ============================================================================
# COACH PLANS
# ============================================================================

@router.get("/coach/current", response_model=Dict[str, Any])
async def get_current_coach_plan(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get current week's coach plan."""
    repo = WeeklyPlansRepository(db)
    plan = repo.get_current_coach_plan(str(current_user.id))

    if not plan:
        return {"plan": None}

    return {
        "plan": {
            "id": plan.id,
            "week_number": plan.week_number,
            "year": plan.year,
            "name": plan.name,
            "focus": plan.focus,
            "sport_type": plan.sport_type,
            "sessions": plan.sessions,
            "total_sessions": plan.total_sessions,
            "completed_sessions": plan.completed_sessions,
            "status": plan.status
        }
    }


@router.get("/coach/week/{year}/{week_number}", response_model=Dict[str, Any])
async def get_coach_plan_by_week(
    year: int,
    week_number: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get coach plan for a specific week."""
    repo = WeeklyPlansRepository(db)
    plan = repo.get_coach_plan(str(current_user.id), week_number, year)

    if not plan:
        return {"plan": None}

    return {
        "plan": {
            "id": plan.id,
            "week_number": plan.week_number,
            "year": plan.year,
            "name": plan.name,
            "focus": plan.focus,
            "sport_type": plan.sport_type,
            "sessions": plan.sessions,
            "total_sessions": plan.total_sessions,
            "completed_sessions": plan.completed_sessions,
            "status": plan.status
        }
    }


@router.post("/coach/generate", response_model=Dict[str, Any])
async def generate_coach_plan(
    request: GenerateCoachPlanRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Generate a new coach weekly plan."""
    repo = WeeklyPlansRepository(db)
    week_num, year = get_week_number(datetime.now())

    # Check if plan already exists
    existing = repo.get_coach_plan(str(current_user.id), week_num, year)
    if existing:
        return {"plan": None, "error": "Plan already exists for this week"}

    # Get user preferences
    prefs = repo.get_preferences(str(current_user.id))

    # Get AI coach to generate real exercises
    container = get_container()
    workout_coach = container.get_workout_coach(db, str(current_user.id))

    # Get medical clearance for safe exercise generation
    medical_clearance = {
        "pain_level": 0,
        "phase": "phase_4_return_to_sport",
        "contraindications": [],
        "max_intensity": 100,
        "avoid_movements": []
    }

    # If user has active medical protocol, get constraints
    medical_protocol = repo.get_current_medical_protocol(str(current_user.id))
    if medical_protocol:
        medical_clearance = {
            "pain_level": medical_protocol.starting_pain_level,
            "phase": medical_protocol.phase,
            "contraindications": medical_protocol.restrictions or [],
            "max_intensity": 70 if medical_protocol.phase_number <= 2 else 85,
            "avoid_movements": medical_protocol.restrictions or []
        }

    # Generate program with AI
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    training_days = request.days_available or 4
    sessions = []

    try:
        ai_result = await workout_coach.generate_weekly_program(
            user_id=str(current_user.id),
            medical_clearance=medical_clearance,
            training_days=training_days,
            sport_type=request.focus or "general_fitness"
        )

        # Parse AI output into structured sessions
        ai_program = ai_result.get("program", "") if ai_result.get("success") else ""
        
        for i, day in enumerate(days):
            if i < training_days:
                exercises = []
                if ai_program:
                    exercises = AIParsingService.parse_exercises_from_text(ai_program)
                    # Limit exercises to avoid overwhelming UI if parser grabs too many
                    exercises = exercises[:8]
                
                if not exercises:
                    exercises = WorkoutTemplateService.get_default_exercises(i, request.focus)

                sessions.append({
                    "day": day,
                    "name": f"Session {i + 1}: {request.focus or 'Strength'}",
                    "type": request.focus or "strength",
                    "duration": prefs.session_duration_minutes if prefs else 60,
                    "exercises": exercises,
                    "completed": False,
                    "ai_notes": ai_program[:500] if ai_program else None
                })
            else:
                sessions.append({
                    "day": day,
                    "name": "Rest",
                    "type": "rest",
                    "duration": 0,
                    "exercises": [],
                    "completed": True
                })
    except Exception as e:
        logger.error(f"AI workout generation failed: {e}")
        # Fallback to defaults
        for i, day in enumerate(days):
            if i < training_days:
                sessions.append({
                    "day": day,
                    "name": f"Session {i + 1}",
                    "type": "strength",
                    "duration": prefs.session_duration_minutes if prefs else 60,
                    "exercises": WorkoutTemplateService.get_default_exercises(i, request.focus),
                    "completed": False
                })
            else:
                sessions.append({
                    "day": day,
                    "name": "Rest",
                    "type": "rest",
                    "duration": 0,
                    "exercises": [],
                    "completed": True
                })

    plan = repo.create_coach_plan(
        user_id=str(current_user.id),
        week_number=week_num,
        year=year,
        name=request.focus or "Weekly Program",
        focus=request.focus or "General Fitness",
        sport_type=prefs.training_location if prefs else "general",
        sessions=sessions
    )

    return {
        "plan": {
            "id": plan.id,
            "week_number": plan.week_number,
            "year": plan.year,
            "name": plan.name,
            "focus": plan.focus,
            "sessions": plan.sessions,
            "total_sessions": plan.total_sessions
        }
    }


@router.post("/coach/{plan_id}/sessions/{session_index}/complete", response_model=Dict[str, Any])
async def complete_coach_session(
    plan_id: str,
    session_index: int,
    request: CompleteSessionRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Mark a workout session as completed."""
    repo = WeeklyPlansRepository(db)

    try:
        plan = repo.update_coach_session_completed(plan_id, session_index)
        return {"success": True, "completed_sessions": plan.completed_sessions}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/coach/history", response_model=Dict[str, Any])
async def get_coach_history(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = 12
):
    """Get coach plan history."""
    repo = WeeklyPlansRepository(db)
    plans = repo.get_plan_history(str(current_user.id), 'coach', limit)

    return {
        "plans": [
            {
                "id": p.id,
                "week_number": p.week_number,
                "year": p.year,
                "name": p.name,
                "focus": p.focus,
                "completed_sessions": p.completed_sessions,
                "total_sessions": p.total_sessions,
                "status": p.status
            }
            for p in plans
        ]
    }


# ============================================================================
# MEDICAL PROTOCOLS
# ============================================================================

@router.get("/medical/current", response_model=Dict[str, Any])
async def get_current_medical_protocol(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get current week's medical protocol."""
    repo = WeeklyPlansRepository(db)
    protocol = repo.get_current_medical_protocol(str(current_user.id))

    if not protocol:
        return {"plan": None}

    return {
        "plan": {
            "id": protocol.id,
            "week_number": protocol.week_number,
            "year": protocol.year,
            "phase": protocol.phase,
            "phase_number": protocol.phase_number,
            "daily_exercises": protocol.daily_exercises,
            "restrictions": protocol.restrictions,
            "checkins_completed": protocol.checkins_completed,
            "checkins_required": protocol.checkins_required,
            "starting_pain_level": protocol.starting_pain_level,
            "status": protocol.status
        }
    }


@router.post("/medical/generate", response_model=Dict[str, Any])
async def generate_medical_protocol(
    request: GenerateMedicalPlanRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Generate a new medical protocol."""
    repo = WeeklyPlansRepository(db)
    week_num, year = get_week_number(datetime.now())

    existing = repo.get_medical_protocol(str(current_user.id), week_num, year)
    if existing:
        return {"plan": None, "error": "Protocol already exists for this week"}

    # Default exercises based on pain level
    pain = request.current_pain_level or 5

    if pain >= 7:
        phase = "Fase 1 - Riduzione dolore"
        phase_num = 1
        exercises = [
            {"name": "Respirazione diaframmatica", "duration": "3 min", "sets": 1, "reps": "10 respiri"},
            {"name": "Cat-Cow gentile", "duration": "2 min", "sets": 2, "reps": "10"},
            {"name": "Supine twist", "duration": "1 min/lato", "sets": 1, "reps": "30 sec hold"},
        ]
        restrictions = ["Evitare flessione lombare", "No carichi", "Movimenti lenti"]
    elif pain >= 4:
        phase = "Fase 2 - Mobilità"
        phase_num = 2
        exercises = [
            {"name": "Cat-Cow", "duration": "2 min", "sets": 2, "reps": "15"},
            {"name": "Bird Dog", "duration": "3 min", "sets": 3, "reps": "10/lato"},
            {"name": "Dead Bug", "duration": "3 min", "sets": 3, "reps": "10/lato"},
            {"name": "Glute Bridge", "duration": "2 min", "sets": 3, "reps": "15"},
        ]
        restrictions = ["Evitare flessione lombare > 30°", "Carichi leggeri OK"]
    else:
        phase = "Fase 3 - Rinforzo"
        phase_num = 3
        exercises = [
            {"name": "Bird Dog avanzato", "duration": "3 min", "sets": 3, "reps": "12/lato"},
            {"name": "Side Plank", "duration": "2 min", "sets": 3, "reps": "30 sec/lato"},
            {"name": "Hip Hinge", "duration": "3 min", "sets": 3, "reps": "12"},
            {"name": "Goblet Squat leggero", "duration": "3 min", "sets": 3, "reps": "10"},
        ]
        restrictions = ["Progressione graduale dei carichi"]

    protocol = repo.create_medical_protocol(
        user_id=str(current_user.id),
        week_number=week_num,
        year=year,
        phase=phase,
        phase_number=phase_num,
        daily_exercises=exercises,
        restrictions=restrictions,
        starting_pain=pain,
        target_pain_reduction=1.0
    )

    return {
        "plan": {
            "id": protocol.id,
            "phase": protocol.phase,
            "daily_exercises": protocol.daily_exercises,
            "restrictions": protocol.restrictions
        }
    }


@router.post("/medical/checkin", response_model=Dict[str, Any])
async def submit_pain_checkin(
    request: PainCheckInRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Submit a pain check-in."""
    from src.infrastructure.persistence.models import PainAssessmentModel
    import uuid

    # Save pain assessment
    assessment = PainAssessmentModel(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        date=datetime.now(),
        pain_level=request.pain_level,
        pain_locations=request.locations,
        triggers=request.red_flags or [],
        notes=request.notes
    )
    db.add(assessment)

    # Increment protocol check-in count
    repo = WeeklyPlansRepository(db)
    protocol = repo.get_current_medical_protocol(str(current_user.id))
    if protocol:
        repo.increment_checkin(protocol.id)

    db.commit()

    return {"success": True, "assessment_id": assessment.id}


@router.get("/medical/history", response_model=Dict[str, Any])
async def get_medical_history(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = 12
):
    """Get medical protocol history."""
    repo = WeeklyPlansRepository(db)
    protocols = repo.get_plan_history(str(current_user.id), 'medical', limit)

    return {
        "plans": [
            {
                "id": p.id,
                "week_number": p.week_number,
                "year": p.year,
                "phase": p.phase,
                "checkins_completed": p.checkins_completed,
                "starting_pain_level": p.starting_pain_level,
                "ending_pain_level": p.ending_pain_level,
                "status": p.status
            }
            for p in protocols
        ]
    }


# ============================================================================
# NUTRITION PLANS
# ============================================================================

@router.get("/nutrition/current", response_model=Dict[str, Any])
async def get_current_nutrition_plan(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get current week's nutrition plan."""
    repo = WeeklyPlansRepository(db)
    plan = repo.get_current_nutrition_plan(str(current_user.id))

    if not plan:
        return {"plan": None}

    return {
        "plan": {
            "id": plan.id,
            "week_number": plan.week_number,
            "year": plan.year,
            "goal": plan.goal,
            "daily_calories": plan.daily_calories,
            "daily_protein": plan.daily_protein,
            "daily_carbs": plan.daily_carbs,
            "daily_fat": plan.daily_fat,
            "daily_meals": plan.daily_meals,
            "diet_type": plan.diet_type,
            "avg_compliance": plan.avg_compliance,
            "status": plan.status
        }
    }


@router.post("/nutrition/generate", response_model=Dict[str, Any])
async def generate_nutrition_plan(
    request: GenerateNutritionPlanRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Generate a new nutrition weekly plan."""
    repo = WeeklyPlansRepository(db)
    week_num, year = get_week_number(datetime.now())

    existing = repo.get_nutrition_plan(str(current_user.id), week_num, year)
    if existing:
        return {"plan": None, "error": "Plan already exists for this week"}

    # Get user preferences
    prefs = repo.get_preferences(str(current_user.id))

    # Calculate macros based on goal
    targets = NutritionCalculatorService.calculate_daily_targets(
        base_calories=request.calorie_target,
        goal=request.goal or "maintenance"
    )
    
    calories = targets["calories"]
    protein = targets["protein"]
    carbs = targets["carbs"]
    fat = targets["fat"]

    # Generate basic meal structure
    daily_meals = NutritionCalculatorService.generate_meal_structure(calories)

    plan = repo.create_nutrition_plan(
        user_id=str(current_user.id),
        week_number=week_num,
        year=year,
        goal=request.goal or "maintenance",
        daily_calories=calories,
        daily_protein=protein,
        daily_carbs=carbs,
        daily_fat=fat,
        daily_meals=daily_meals,
        diet_type=prefs.diet_type if prefs else "balanced",
        excluded_foods=prefs.allergies if prefs else None,
        preferred_foods=prefs.favorite_foods if prefs else None
    )

    return {
        "plan": {
            "id": plan.id,
            "goal": plan.goal,
            "daily_calories": plan.daily_calories,
            "daily_protein": plan.daily_protein,
            "daily_carbs": plan.daily_carbs,
            "daily_fat": plan.daily_fat,
            "daily_meals": plan.daily_meals
        }
    }


@router.get("/nutrition/history", response_model=Dict[str, Any])
async def get_nutrition_history(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = 12
):
    """Get nutrition plan history."""
    repo = WeeklyPlansRepository(db)
    plans = repo.get_plan_history(str(current_user.id), 'nutrition', limit)

    return {
        "plans": [
            {
                "id": p.id,
                "week_number": p.week_number,
                "year": p.year,
                "goal": p.goal,
                "daily_calories": p.daily_calories,
                "avg_compliance": p.avg_compliance,
                "status": p.status
            }
            for p in plans
        ]
    }


# ============================================================================
# USER PREFERENCES
# ============================================================================

@router.get("/preferences", response_model=Dict[str, Any])
async def get_user_preferences(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get user preferences."""
    repo = WeeklyPlansRepository(db)
    prefs = repo.get_preferences(str(current_user.id))

    if not prefs:
        return {"preferences": None}

    return {
        "preferences": {
            "training": {
                "days": prefs.preferred_training_days,
                "time": prefs.preferred_training_time,
                "duration": prefs.session_duration_minutes,
                "equipment": prefs.equipment_available,
                "location": prefs.training_location
            },
            "nutrition": {
                "diet_type": prefs.diet_type,
                "allergies": prefs.allergies,
                "disliked_foods": prefs.disliked_foods,
                "favorite_foods": prefs.favorite_foods,
                "meals_per_day": prefs.meals_per_day,
                "cooking_skill": prefs.cooking_skill
            },
            "notifications": {
                "workout_reminders": prefs.workout_reminders,
                "meal_reminders": prefs.meal_reminders,
                "pain_checkin_reminders": prefs.pain_checkin_reminders,
                "reminder_time": prefs.reminder_time
            }
        }
    }


@router.post("/preferences", response_model=Dict[str, Any])
async def save_user_preferences(
    preferences: Dict[str, Any],
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Save user preferences with UserContextRAG integration."""
    repo = WeeklyPlansRepository(db)

    # Flatten nested structure
    flat_prefs = {}

    if "training" in preferences:
        t = preferences["training"]
        flat_prefs.update({
            "preferred_training_days": t.get("days"),
            "preferred_training_time": t.get("time"),
            "session_duration_minutes": t.get("duration"),
            "equipment_available": t.get("equipment"),
            "training_location": t.get("location")
        })

    if "nutrition" in preferences:
        n = preferences["nutrition"]
        flat_prefs.update({
            "diet_type": n.get("diet_type"),
            "allergies": n.get("allergies"),
            "disliked_foods": n.get("disliked_foods"),
            "favorite_foods": n.get("favorite_foods"),
            "meals_per_day": n.get("meals_per_day"),
            "cooking_skill": n.get("cooking_skill")
        })

    if "notifications" in preferences:
        notif = preferences["notifications"]
        flat_prefs.update({
            "workout_reminders": notif.get("workout_reminders"),
            "meal_reminders": notif.get("meal_reminders"),
            "pain_checkin_reminders": notif.get("pain_checkin_reminders"),
            "reminder_time": notif.get("reminder_time")
        })

    prefs = repo.save_preferences(str(current_user.id), flat_prefs)

    # CRITICAL FIX: Store nutrition preferences in UserContextRAG for AI agents
    if "nutrition" in preferences:
        try:
            from src.infrastructure.ai.user_context_rag import get_user_context_rag
            user_rag = get_user_context_rag()

            n = preferences["nutrition"]

            # Store food preferences in RAG for agent memory
            if n.get("favorite_foods"):
                user_rag.store_context(
                    user_id=str(current_user.id),
                    text=f"Cibi preferiti: {', '.join(n.get('favorite_foods', []))}",
                    category="preference",
                    metadata={"type": "food_preferences", "preference_type": "favorites"}
                )

            if n.get("disliked_foods"):
                user_rag.store_context(
                    user_id=str(current_user.id),
                    text=f"Cibi da evitare: {', '.join(n.get('disliked_foods', []))}",
                    category="preference",
                    metadata={"type": "food_preferences", "preference_type": "dislikes"}
                )

            if n.get("allergies"):
                user_rag.store_context(
                    user_id=str(current_user.id),
                    text=f"Allergie alimentari: {', '.join(n.get('allergies', []))}",
                    category="medical",
                    metadata={"type": "food_allergies"}
                )

            logger.info(f"✅ Food preferences saved to RAG for user {current_user.id}")
        except Exception as e:
            logger.error(f"Failed to save food preferences to RAG: {e}")
            # Non-fatal, continue

    return {"success": True, "preferences_id": prefs.id}
