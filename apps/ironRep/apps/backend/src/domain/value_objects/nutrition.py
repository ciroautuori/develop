from enum import Enum
from pydantic import BaseModel

class DietType(str, Enum):
    BALANCED = "balanced"
    KETO = "keto"
    PALEO = "paleo"
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    HIGH_PROTEIN = "high_protein"
    MEDITERRANEAN = "mediterranean"

class GoalType(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"
    PERFORMANCE = "performance"
    RECOVERY = "recovery"  # Specific for injury

class MacroNutrients(BaseModel):
    protein_g: int
    carbs_g: int
    fat_g: int
    calories_kcal: int
