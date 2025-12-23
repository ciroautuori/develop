"""
Nutrition Domain Entities

Entities for nutrition tracking and planning.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel
from src.domain.value_objects.nutrition import DietType, GoalType, MacroNutrients



class FoodItem(BaseModel):
    name: str
    quantity: float
    unit: str  # g, ml, serving
    calories: int
    protein: float
    carbs: float
    fat: float
    brand: Optional[str] = None

class Meal(BaseModel):
    name: str  # Breakfast, Lunch, Dinner, Snack
    foods: List[FoodItem]
    time: Optional[str] = None  # Time as string HH:MM

    @property
    def total_macros(self) -> MacroNutrients:
        p = sum(f.protein for f in self.foods)
        c = sum(f.carbs for f in self.foods)
        f = sum(f.fat for f in self.foods)
        cal = sum(f.calories for f in self.foods)
        return MacroNutrients(protein_g=int(p), carbs_g=int(c), fat_g=int(f), calories_kcal=int(cal))

class DailyNutritionLog:
    def __init__(
        self,
        user_id: str,
        date: datetime,
        meals: List[Meal],
        water_ml: int = 0,
        supplements: List[str] = None,
        notes: str = "",
        id: str = None
    ):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.meals = meals
        self.water_ml = water_ml
        self.supplements = supplements or []
        self.notes = notes

    @property
    def daily_total(self) -> MacroNutrients:
        total_p = sum(m.total_macros.protein_g for m in self.meals)
        total_c = sum(m.total_macros.carbs_g for m in self.meals)
        total_f = sum(m.total_macros.fat_g for m in self.meals)
        total_cal = sum(m.total_macros.calories_kcal for m in self.meals)
        return MacroNutrients(protein_g=total_p, carbs_g=total_c, fat_g=total_f, calories_kcal=total_cal)

class NutritionPlan:
    def __init__(
        self,
        user_id: str,
        goal: GoalType,
        diet_type: DietType,
        target_macros: MacroNutrients,
        weekly_schedule: Dict[str, List[Meal]],  # Day -> Meals
        created_at: datetime,
        id: str = None
    ):
        self.id = id
        self.user_id = user_id
        self.goal = goal
        self.diet_type = diet_type
        self.target_macros = target_macros
        self.weekly_schedule = weekly_schedule
        self.created_at = created_at
