"""
Onboarding Use Case

Handles new user onboarding flow.
"""
from typing import Dict, Any
from datetime import datetime

from src.domain.entities.user import User, Sex
from src.domain.repositories.user_repository import IUserRepository
from src.application.dtos.dtos import PainAssessmentDTO
from src.application.use_cases.generate_diet import GenerateDietUseCase


class OnboardingUseCase:
    """
    Use case for user onboarding.

    Collects user profile data, injury history, baseline strength, and preferences.
    Also initializes nutrition plan.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        generate_diet_usecase: GenerateDietUseCase = None
    ):
        self.user_repository = user_repository
        self.generate_diet_usecase = generate_diet_usecase

    async def execute(self, onboarding_data: Dict[str, Any]) -> User:
        """
        Execute onboarding workflow.

        Args:
            onboarding_data: Dictionary with all onboarding form data

        Returns:
            Created User entity
        """
        # Validate email uniqueness
        if self.user_repository.exists_by_email(onboarding_data["email"]):
            raise ValueError(f"User with email {onboarding_data['email']} already exists")

        # Create User entity
        user = User(
            email=onboarding_data["email"],
            name=onboarding_data.get("name", "Utente"),
            age=onboarding_data.get("age"),
            weight_kg=onboarding_data.get("weight_kg"),
            height_cm=onboarding_data.get("height_cm"),
            sex=Sex(onboarding_data["sex"]) if onboarding_data.get("sex") else None,

            # Injury details
            injury_date=datetime.fromisoformat(onboarding_data["injury_date"]) if onboarding_data.get("injury_date") else None,
            diagnosis=onboarding_data.get("diagnosis", "Sciatica"),
            pain_locations=onboarding_data.get("pain_locations", []),
            injury_description=onboarding_data.get("injury_description", ""),

            # Baseline strength
            baseline_deadlift_1rm=onboarding_data.get("baseline_deadlift_1rm"),
            baseline_squat_1rm=onboarding_data.get("baseline_squat_1rm"),
            baseline_front_squat_1rm=onboarding_data.get("baseline_front_squat_1rm"),
            baseline_bench_press_1rm=onboarding_data.get("baseline_bench_press_1rm"),
            baseline_shoulder_press_1rm=onboarding_data.get("baseline_shoulder_press_1rm"),
            baseline_snatch_1rm=onboarding_data.get("baseline_snatch_1rm"),
            baseline_clean_jerk_1rm=onboarding_data.get("baseline_clean_jerk_1rm"),
            baseline_pullups_max=onboarding_data.get("baseline_pullups_max"),

            # Goals
            target_return_date=datetime.fromisoformat(onboarding_data["target_return_date"]) if onboarding_data.get("target_return_date") else None,
            primary_goal=onboarding_data.get("primary_goal"),
            goals_description=onboarding_data.get("goals_description"),

            # Equipment & Preferences (basic)
            equipment_available=onboarding_data.get("equipment_available", []),
            preferred_training_time=onboarding_data.get("preferred_training_time"),
            session_duration_minutes=onboarding_data.get("session_duration_minutes", 60),

            # =========================================================================
            # TRAINING GOALS & EXPERIENCE (from TrainingGoalsStep)
            # =========================================================================
            training_experience=onboarding_data.get("training_experience"),
            training_years=onboarding_data.get("training_years"),
            secondary_goals=onboarding_data.get("secondary_goals", []),
            available_days=onboarding_data.get("available_days"),
            preferred_time=onboarding_data.get("preferred_time"),
            intensity_preference=onboarding_data.get("intensity_preference"),

            # =========================================================================
            # LIFESTYLE & RECOVERY (from LifestyleStep)
            # =========================================================================
            activity_level=onboarding_data.get("activity_level"),
            work_type=onboarding_data.get("work_type"),
            work_hours_per_day=onboarding_data.get("work_hours_per_day"),
            commute_active=onboarding_data.get("commute_active", False),
            stress_level=onboarding_data.get("stress_level"),
            stress_sources=onboarding_data.get("stress_sources", []),
            sleep_hours=onboarding_data.get("sleep_hours"),
            sleep_quality=onboarding_data.get("sleep_quality"),
            sleep_schedule=onboarding_data.get("sleep_schedule"),
            recovery_capacity=onboarding_data.get("recovery_capacity"),
            health_conditions=onboarding_data.get("health_conditions", []),
            supplements_used=onboarding_data.get("supplements_used", []),

            # =========================================================================
            # NUTRITION GOALS & PREFERENCES (from NutritionGoalsStep)
            # =========================================================================
            nutrition_goal=onboarding_data.get("nutrition_goal"),
            diet_type=onboarding_data.get("diet_type"),
            calorie_preference=onboarding_data.get("calorie_preference"),
            custom_calories=onboarding_data.get("custom_calories"),
            protein_priority=onboarding_data.get("protein_priority"),
            macro_preference=onboarding_data.get("macro_preference"),
            meal_frequency=onboarding_data.get("meal_frequency"),
            meal_timing=onboarding_data.get("meal_timing"),
            intermittent_window=onboarding_data.get("intermittent_window"),
            budget_preference=onboarding_data.get("budget_preference"),
            cooking_skill=onboarding_data.get("cooking_skill"),
            meal_prep_available=onboarding_data.get("meal_prep_available", True),
            supplements_interest=onboarding_data.get("supplements_interest", []),

            # =========================================================================
            # ALLERGIES & DIETARY RESTRICTIONS
            # =========================================================================
            allergies=onboarding_data.get("allergies", []),
            intolerances=onboarding_data.get("intolerances", []),
            dietary_restrictions=onboarding_data.get("dietary_restrictions", []),

            # =========================================================================
            # FOOD PREFERENCES
            # =========================================================================
            favorite_foods=onboarding_data.get("favorite_foods", []),
            disliked_foods=onboarding_data.get("disliked_foods", []),

            # Set as onboarded
            is_onboarded=True,
            program_start_date=datetime.now()
        )

        # Save user
        saved_user = self.user_repository.save(user)

        # Initialize Nutrition Plan if preferences provided
        if self.generate_diet_usecase and onboarding_data.get("nutrition_goal"):
            try:
                await self.generate_diet_usecase.execute({
                    "goal": onboarding_data.get("nutrition_goal"),
                    "diet_type": onboarding_data.get("diet_type", "balanced"),
                    "activity_level": onboarding_data.get("activity_level", "moderate"),
                    "target_calories": onboarding_data.get("custom_calories") or onboarding_data.get("target_calories"),
                    "injuries": onboarding_data.get("diagnosis"),
                    # Pass new comprehensive data for better diet generation
                    "allergies": onboarding_data.get("allergies", []),
                    "intolerances": onboarding_data.get("intolerances", []),
                    "dietary_restrictions": onboarding_data.get("dietary_restrictions", []),
                    "favorite_foods": onboarding_data.get("favorite_foods", []),
                    "disliked_foods": onboarding_data.get("disliked_foods", []),
                    "meal_frequency": onboarding_data.get("meal_frequency"),
                    "cooking_skill": onboarding_data.get("cooking_skill"),
                    "budget_preference": onboarding_data.get("budget_preference"),
                })
            except Exception as e:
                print(f"⚠️ Error generating initial diet: {e}")

        return saved_user

    def validate_onboarding_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate onboarding data.

        Returns:
            Dict of field_name: error_message for any validation errors
        """
        errors = {}

        # Required fields
        if not data.get("email"):
            errors["email"] = "Email è obbligatoria"
        elif "@" not in data["email"]:
            errors["email"] = "Email non valida"

        if not data.get("name"):
            errors["name"] = "Nome è obbligatorio"

        # Injury validation only if has_injury is True
        if data.get("has_injury", False):
            if not data.get("injury_date"):
                errors["injury_date"] = "Data infortunio è obbligatoria"

            if not data.get("pain_locations") or len(data["pain_locations"]) == 0:
                errors["pain_locations"] = "Seleziona almeno una localizzazione dolore"

        # Optional but validated if present
        if data.get("age") and (data["age"] < 18 or data["age"] > 100):
            errors["age"] = "Età deve essere tra 18 e 100"

        if data.get("weight_kg") and (data["weight_kg"] < 30 or data["weight_kg"] > 300):
            errors["weight_kg"] = "Peso deve essere tra 30 e 300 kg"

        if data.get("height_cm") and (data["height_cm"] < 100 or data["height_cm"] > 250):
            errors["height_cm"] = "Altezza deve essere tra 100 e 250 cm"

        return errors
