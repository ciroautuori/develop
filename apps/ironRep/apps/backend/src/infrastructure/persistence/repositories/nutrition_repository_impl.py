"""
Nutrition Repository Implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import uuid
import json

from src.domain.repositories.nutrition_repository import INutritionRepository
from src.domain.entities.nutrition import NutritionPlan, DailyNutritionLog, DietType, GoalType, MacroNutrients, Meal, FoodItem
from src.infrastructure.persistence.nutrition_models import NutritionPlanModel, DailyNutritionLogModel

class NutritionRepositoryImpl(INutritionRepository):
    def __init__(self, db: Session):
        self.db = db

    def save_plan(self, plan: NutritionPlan) -> NutritionPlan:
        model = NutritionPlanModel(
            id=plan.id or str(uuid.uuid4()),
            user_id=plan.user_id,
            goal=plan.goal.value,
            diet_type=plan.diet_type.value,
            target_calories=plan.target_macros.calories_kcal,
            target_protein=plan.target_macros.protein_g,
            target_carbs=plan.target_macros.carbs_g,
            target_fat=plan.target_macros.fat_g,
            weekly_schedule=json.loads(json.dumps(plan.weekly_schedule, default=lambda o: o.dict())),
            created_at=plan.created_at
        )
        self.db.merge(model)
        self.db.commit()
        return plan

    def get_current_plan(self, user_id: str) -> Optional[NutritionPlan]:
        model = self.db.query(NutritionPlanModel).filter(
            NutritionPlanModel.user_id == user_id
        ).order_by(NutritionPlanModel.created_at.desc()).first()

        if not model:
            return None

        # For now, keep weekly_schedule as dict (raw JSON)
        # In production, deserialize to Meal objects if needed
        return NutritionPlan(
            id=model.id,
            user_id=model.user_id,
            goal=GoalType(model.goal),
            diet_type=DietType(model.diet_type),
            target_macros=MacroNutrients(
                protein_g=model.target_protein,
                carbs_g=model.target_carbs,
                fat_g=model.target_fat,
                calories_kcal=model.target_calories
            ),
            weekly_schedule=model.weekly_schedule or {},
            created_at=model.created_at
        )

    def save_log(self, log: DailyNutritionLog) -> DailyNutritionLog:
        daily_total = log.daily_total

        # Check if log already exists for this user and date
        existing = self.db.query(DailyNutritionLogModel).filter(
            DailyNutritionLogModel.user_id == log.user_id,
            DailyNutritionLogModel.date == log.date
        ).first()

        if existing:
            # Update existing log
            existing.meals = [m.dict() for m in log.meals]
            existing.water_ml = log.water_ml
            existing.supplements = log.supplements
            existing.notes = log.notes
            existing.total_calories = daily_total.calories_kcal
            existing.total_protein = daily_total.protein_g
            existing.total_carbs = daily_total.carbs_g
            existing.total_fat = daily_total.fat_g
            self.db.commit()
            log.id = existing.id
        else:
            # Create new log
            model = DailyNutritionLogModel(
                id=log.id or str(uuid.uuid4()),
                user_id=log.user_id,
                date=log.date,
                meals=[m.dict() for m in log.meals],
                water_ml=log.water_ml,
                supplements=log.supplements,
                notes=log.notes,
                total_calories=daily_total.calories_kcal,
                total_protein=daily_total.protein_g,
                total_carbs=daily_total.carbs_g,
                total_fat=daily_total.fat_g
            )
            self.db.add(model)
            self.db.commit()
            log.id = model.id

        return log

    def get_log_by_date(self, user_id: str, date: date) -> Optional[DailyNutritionLog]:
        model = self.db.query(DailyNutritionLogModel).filter(
            DailyNutritionLogModel.user_id == user_id,
            DailyNutritionLogModel.date == date
        ).first()

        if not model:
            return None

        # Deserialize meals from JSON
        meals = self._deserialize_meals(model.meals) if model.meals else []

        return DailyNutritionLog(
            id=model.id,
            user_id=model.user_id,
            date=model.date,
            meals=meals,
            water_ml=model.water_ml,
            supplements=model.supplements or [],
            notes=model.notes or ""
        )

    def get_logs_range(self, user_id: str, start_date: date, end_date: date) -> List[DailyNutritionLog]:
        models = self.db.query(DailyNutritionLogModel).filter(
            DailyNutritionLogModel.user_id == user_id,
            DailyNutritionLogModel.date >= start_date,
            DailyNutritionLogModel.date <= end_date
        ).all()

        return [
            DailyNutritionLog(
                id=m.id,
                user_id=m.user_id,
                date=m.date,
                meals=self._deserialize_meals(m.meals) if m.meals else [],
                water_ml=m.water_ml,
                supplements=m.supplements or [],
                notes=m.notes or ""
            ) for m in models
        ]

    def _deserialize_meals(self, meals_json: list) -> List[Meal]:
        """Deserialize meals from JSON to Meal objects."""
        if not meals_json:
            return []

        meals = []
        for meal_data in meals_json:
            try:
                foods = []
                for food_data in meal_data.get('foods', []):
                    foods.append(FoodItem(
                        name=food_data.get('name', ''),
                        quantity=food_data.get('quantity', 0),
                        unit=food_data.get('unit', 'g'),
                        calories=food_data.get('calories', 0),
                        protein=food_data.get('protein', 0),
                        carbs=food_data.get('carbs', 0),
                        fat=food_data.get('fat', 0),
                        brand=food_data.get('brand')
                    ))

                meals.append(Meal(
                    name=meal_data.get('name', 'Unknown'),
                    foods=foods,
                    time=meal_data.get('time')
                ))
            except Exception as e:
                print(f"⚠️ Error deserializing meal: {e}")
                continue

        return meals
