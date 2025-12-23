"""
Nutrition Repository Interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from src.domain.entities.nutrition import NutritionPlan, DailyNutritionLog

class INutritionRepository(ABC):
    @abstractmethod
    def save_plan(self, plan: NutritionPlan) -> NutritionPlan:
        pass

    @abstractmethod
    def get_current_plan(self, user_id: str) -> Optional[NutritionPlan]:
        pass

    @abstractmethod
    def save_log(self, log: DailyNutritionLog) -> DailyNutritionLog:
        pass

    @abstractmethod
    def get_log_by_date(self, user_id: str, date: date) -> Optional[DailyNutritionLog]:
        pass

    @abstractmethod
    def get_logs_range(self, user_id: str, start_date: date, end_date: date) -> List[DailyNutritionLog]:
        pass
