from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# Shared models
class Ingredient(BaseModel):
    food_id: str
    name: str
    brand: Optional[str] = None
    grams: float = Field(gt=0)
    calories: float
    protein: float
    carbs: float
    fat: float

# Schemas
class RecipeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    ingredients: List[Ingredient]
    servings: int = Field(default=1, gt=0)
    prep_time_minutes: Optional[int] = None
    instructions: Optional[str] = None

class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[Ingredient]] = None
    servings: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    instructions: Optional[str] = None

class RecipeResponse(BaseModel):
    id: str  # String UUID to match model
    user_id: str
    name: str
    description: Optional[str] = None
    ingredients: List[Ingredient]
    
    # Calculated totals
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    
    servings: int
    prep_time_minutes: Optional[int] = None
    instructions: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
