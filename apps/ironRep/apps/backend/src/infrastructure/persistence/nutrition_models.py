"""
Nutrition Database Models
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base
from src.domain.entities.nutrition import DietType, GoalType

class NutritionPlanModel(Base):
    __tablename__ = "nutrition_plans"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    goal = Column(String)
    diet_type = Column(String)
    target_calories = Column(Integer)
    target_protein = Column(Integer)
    target_carbs = Column(Integer)
    target_fat = Column(Integer)
    weekly_schedule = Column(JSON)  # Stores full weekly meal structure
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="nutrition_plans")

class DailyNutritionLogModel(Base):
    __tablename__ = "daily_nutrition_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    date = Column(Date, index=True)
    meals = Column(JSON)  # Stores list of meals with foods
    water_ml = Column(Integer, default=0)
    supplements = Column(JSON)
    notes = Column(String, nullable=True)

    # Cached totals for query performance
    total_calories = Column(Integer)
    total_protein = Column(Integer)
    total_carbs = Column(Integer)
    total_fat = Column(Integer)

    user = relationship("UserModel", back_populates="nutrition_logs")
