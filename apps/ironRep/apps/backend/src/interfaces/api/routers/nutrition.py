"""
Nutrition API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from src.infrastructure.config.dependencies import container
from src.infrastructure.persistence.database import get_db
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.persistence.repositories.nutrition_repository_impl import NutritionRepositoryImpl
from src.domain.entities.nutrition import DailyNutritionLog, Meal, FoodItem

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])


class NutritionQuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class GenerateDietRequest(BaseModel):
    goal: str
    diet_type: str
    activity_level: str


@router.post("/ask")
async def ask_nutritionist(
    request: NutritionQuestionRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Ask nutritionist a question about diet/nutrition."""
    try:
        usecase = container.get_ask_nutritionist_usecase(db, current_user.id, request.session_id)
        return await usecase.execute(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-plan")
async def generate_plan(
    request: GenerateDietRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Generate personalized diet plan."""
    try:
        usecase = container.get_generate_diet_usecase(db, current_user.id)
        return await usecase.execute(request.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FoodItemRequest(BaseModel):
    name: str
    quantity: float
    unit: str
    calories: int
    protein: float
    carbs: float
    fat: float
    brand: Optional[str] = None


class MealRequest(BaseModel):
    name: str
    foods: List[FoodItemRequest]
    time: Optional[str] = None


class DailyNutritionLogRequest(BaseModel):
    date: str  # ISO format YYYY-MM-DD
    meals: List[MealRequest]
    water_ml: int = 0
    supplements: List[str] = []
    notes: str = ""


@router.get("/daily-log/{log_date}")
async def get_daily_log(
    log_date: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Get nutrition log for specific date."""
    try:
        parsed_date = datetime.strptime(log_date, "%Y-%m-%d").date()
        repo = NutritionRepositoryImpl(db)
        log = repo.get_log_by_date(current_user.id, parsed_date)

        if not log:
            return {"date": log_date, "meals": [], "water_ml": 0, "supplements": [], "notes": ""}

        return {
            "id": log.id,
            "date": str(log.date),
            "meals": [
                {
                    "name": m.name,
                    "time": m.time,
                    "foods": [
                        {
                            "name": f.name,
                            "quantity": f.quantity,
                            "unit": f.unit,
                            "calories": f.calories,
                            "protein": f.protein,
                            "carbs": f.carbs,
                            "fat": f.fat,
                            "brand": f.brand
                        } for f in m.foods
                    ],
                    "total_macros": {
                        "protein_g": m.total_macros.protein_g,
                        "carbs_g": m.total_macros.carbs_g,
                        "fat_g": m.total_macros.fat_g,
                        "calories_kcal": m.total_macros.calories_kcal
                    }
                } for m in log.meals
            ],
            "water_ml": log.water_ml,
            "supplements": log.supplements,
            "notes": log.notes,
            "daily_total": {
                "protein_g": log.daily_total.protein_g,
                "carbs_g": log.daily_total.carbs_g,
                "fat_g": log.daily_total.fat_g,
                "calories_kcal": log.daily_total.calories_kcal
            }
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-log")
async def save_daily_log(
    request: DailyNutritionLogRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Save or update nutrition log for specific date."""
    try:
        parsed_date = datetime.strptime(request.date, "%Y-%m-%d").date()

        # Convert request to domain entities
        meals = []
        for meal_req in request.meals:
            foods = [
                FoodItem(
                    name=f.name,
                    quantity=f.quantity,
                    unit=f.unit,
                    calories=f.calories,
                    protein=f.protein,
                    carbs=f.carbs,
                    fat=f.fat,
                    brand=f.brand
                ) for f in meal_req.foods
            ]
            meals.append(Meal(name=meal_req.name, foods=foods, time=meal_req.time))

        log = DailyNutritionLog(
            user_id=current_user.id,
            date=parsed_date,
            meals=meals,
            water_ml=request.water_ml,
            supplements=request.supplements,
            notes=request.notes
        )

        repo = NutritionRepositoryImpl(db)
        saved_log = repo.save_log(log)

        return {
            "id": saved_log.id,
            "date": str(saved_log.date),
            "message": "Daily nutrition log saved successfully"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
