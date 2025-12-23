"""
Nutrition Calculator Service

Calculates nutritional targets based on goals and user data.
"""
from typing import Dict, Any, List

class NutritionCalculatorService:
    """Service for calculating macros and calories."""

    @staticmethod
    def calculate_targets(goal: str, base_calories: int) -> Dict[str, int]:
        """
        Calculate daily calorie and macro targets.
        
        Args:
            goal: 'deficit', 'surplus', or 'maintenance'
            base_calories: TDEE or manual target
            
        Returns:
            Dict with calories, protein, carbs, fat
        """
        # Calorie adjustment
        if goal == "deficit":
            calories = int(base_calories * 0.85)
        elif goal == "surplus":
            calories = int(base_calories * 1.15)
        else:
            calories = base_calories
            
        # Standard balanced split (30% P / 40% C / 30% F)
        # TODO: Allow configurable splits via preferences
        protein = int(calories * 0.30 / 4)  # 4 kcal/g
        carbs = int(calories * 0.40 / 4)    # 4 kcal/g
        fat = int(calories * 0.30 / 9)      # 9 kcal/g
        
        return {
            "daily_calories": calories,
            "daily_protein": protein,
            "daily_carbs": carbs,
            "daily_fat": fat
        }

    @staticmethod
    def generate_meal_structure(calories: int) -> List[Dict]:
        """
        Generate a standard daily meal structure.
        """
        return [
            {"name": "Colazione", "time": "07:30", "target_calories": int(calories * 0.25)},
            {"name": "Pranzo", "time": "12:30", "target_calories": int(calories * 0.35)},
            {"name": "Snack", "time": "16:00", "target_calories": int(calories * 0.10)},
            {"name": "Cena", "time": "19:30", "target_calories": int(calories * 0.30)},
        ]
