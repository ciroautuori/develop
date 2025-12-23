from pydantic import BaseModel
from typing import Optional, List

class FoodItem(BaseModel):
    id: str
    name: str
    brand: Optional[str] = None
    type: str = "generic"
    calories: int
    protein: float
    carbs: float
    fat: float
    url: Optional[str] = None

class FoodServing(BaseModel):
    id: str
    description: str
    metric_amount: float
    metric_unit: str
    calories: float
    protein: float
    carbs: float
    fat: float
