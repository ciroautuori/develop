"""
User Entity

Represents a user profile with injury history, baseline strength, and preferences.
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum
import uuid
from src.domain.value_objects.user import Sex, ActivityLevel
from src.domain.entities.workout_session import WorkoutPhase





@dataclass
class User:
    """
    Entity representing a user.

    Core aggregate root for the user bounded context.
    Includes comprehensive wizard data from TrainingGoals, Lifestyle, and NutritionGoals steps.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    password_hash: Optional[str] = None
    name: str = "Utente"

    # Physical attributes
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    sex: Optional[Sex] = None

    # Injury details
    injury_date: Optional[datetime] = None
    diagnosis: str = ""
    pain_locations: List[str] = field(default_factory=list)
    injury_description: str = ""

    # Baseline strength (pre-injury)
    baseline_deadlift_1rm: Optional[float] = None
    baseline_squat_1rm: Optional[float] = None
    baseline_front_squat_1rm: Optional[float] = None
    baseline_bench_press_1rm: Optional[float] = None
    baseline_shoulder_press_1rm: Optional[float] = None
    baseline_snatch_1rm: Optional[float] = None
    baseline_clean_jerk_1rm: Optional[float] = None
    baseline_pullups_max: Optional[int] = None

    # Current program state
    current_phase: str = WorkoutPhase.PHASE_1_DECOMPRESSION.value
    weeks_in_current_phase: int = 0
    program_start_date: datetime = field(default_factory=datetime.now)

    # Goals
    target_return_date: Optional[datetime] = None
    primary_goal: Optional[str] = None
    goals_description: Optional[str] = None

    # Equipment & Preferences (basic)
    equipment_available: List[str] = field(default_factory=list)
    preferred_training_time: Optional[str] = None
    session_duration_minutes: int = 60

    # =========================================================================
    # TRAINING GOALS & EXPERIENCE (from TrainingGoalsStep)
    # =========================================================================
    training_experience: Optional[str] = None  # beginner, intermediate, advanced, elite
    training_years: Optional[int] = None
    secondary_goals: List[str] = field(default_factory=list)
    available_days: Optional[int] = None  # Days per week
    preferred_time: Optional[str] = None  # morning, afternoon, evening, flexible
    intensity_preference: Optional[str] = None  # low, moderate, high, variable

    # =========================================================================
    # LIFESTYLE & RECOVERY (from LifestyleStep)
    # =========================================================================
    activity_level: Optional[str] = None  # sedentary, lightly_active, moderately_active, very_active, extra_active
    work_type: Optional[str] = None  # desk_job, light_activity, moderate_activity, heavy_labor, mixed
    work_hours_per_day: Optional[int] = None
    commute_active: bool = False
    stress_level: Optional[int] = None  # 1-5
    stress_sources: List[str] = field(default_factory=list)
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[str] = None  # poor, fair, good, excellent
    sleep_schedule: Optional[str] = None  # consistent, variable, shift_work, irregular
    recovery_capacity: Optional[str] = None  # fast, normal, slow, variable
    health_conditions: List[str] = field(default_factory=list)
    supplements_used: List[str] = field(default_factory=list)

    # =========================================================================
    # NUTRITION GOALS & PREFERENCES (from NutritionGoalsStep)
    # =========================================================================
    nutrition_goal: Optional[str] = None  # fat_loss, muscle_gain, maintenance, recomp, performance
    diet_type: Optional[str] = None  # balanced, low_carb, keto, high_protein, mediterranean, vegetarian, vegan
    calorie_preference: Optional[str] = None  # auto_calculate, manual
    custom_calories: Optional[int] = None
    manual_target_calories: Optional[int] = None
    manual_target_protein_g: Optional[int] = None
    manual_target_carbs_g: Optional[int] = None
    manual_target_fat_g: Optional[int] = None
    protein_priority: Optional[str] = None  # standard, high, very_high
    macro_preference: Optional[str] = None  # balanced, high_protein, low_carb, high_carb, flexible
    meal_frequency: Optional[int] = None  # Number of meals per day
    meal_timing: Optional[str] = None  # flexible, structured, intermittent_fasting, pre_post_workout
    intermittent_window: Optional[str] = None  # 16:8, 18:6, 20:4, 5:2, custom
    budget_preference: Optional[str] = None  # budget_friendly, moderate, premium, no_limit
    cooking_skill: Optional[str] = None  # beginner, intermediate, advanced, chef
    meal_prep_available: bool = True
    supplements_interest: List[str] = field(default_factory=list)

    # =========================================================================
    # ALLERGIES & DIETARY RESTRICTIONS
    # =========================================================================
    allergies: List[str] = field(default_factory=list)  # peanuts, tree_nuts, shellfish, etc.
    intolerances: List[str] = field(default_factory=list)  # lactose, gluten, etc.
    dietary_restrictions: List[str] = field(default_factory=list)  # no_pork, no_beef, halal, kosher

    # =========================================================================
    # FOOD PREFERENCES
    # =========================================================================
    favorite_foods: List[str] = field(default_factory=list)
    disliked_foods: List[str] = field(default_factory=list)

    # Account status
    is_active: bool = True
    is_onboarded: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login_at: Optional[datetime] = None

    def get_weeks_in_program(self) -> int:
        """Calculate total weeks since program start."""
        delta = datetime.now() - self.program_start_date
        return delta.days // 7

    def get_current_capacity_percentage(self, current_dl_kg: float) -> float:
        """Calculate current deadlift strength as % of baseline."""
        if self.baseline_deadlift_1rm and self.baseline_deadlift_1rm > 0:
            return (current_dl_kg / self.baseline_deadlift_1rm) * 100
        return 0.0

    def has_baseline_strength_data(self) -> bool:
        """Check if user has any baseline strength data."""
        return any([
            self.baseline_deadlift_1rm,
            self.baseline_squat_1rm,
            self.baseline_snatch_1rm,
            self.baseline_clean_jerk_1rm
        ])

    def get_available_equipment_list(self) -> List[str]:
        """Get list of available equipment."""
        return self.equipment_available if self.equipment_available else []

    def mark_onboarded(self):
        """Mark user as having completed onboarding."""
        self.is_onboarded = True
        self.updated_at = datetime.now()

    def update_phase(self, new_phase: str):
        """Update current rehabilitation phase."""
        self.current_phase = new_phase
        self.weeks_in_current_phase = 0
        self.updated_at = datetime.now()

    def increment_week_in_phase(self):
        """Increment weeks counter in current phase."""
        self.weeks_in_current_phase += 1
        self.updated_at = datetime.now()

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary with all comprehensive wizard data."""
        return {
            # Identity
            "id": self.id,
            "email": self.email,
            "name": self.name,

            # Physical attributes
            "age": self.age,
            "weight_kg": self.weight_kg,
            "height_cm": self.height_cm,
            "sex": self.sex.value if self.sex else None,

            # Injury details
            "injury_date": self.injury_date.isoformat() if self.injury_date else None,
            "diagnosis": self.diagnosis,
            "pain_locations": self.pain_locations,
            "injury_description": self.injury_description,

            # Baseline strength
            "baseline_deadlift_1rm": self.baseline_deadlift_1rm,
            "baseline_squat_1rm": self.baseline_squat_1rm,
            "baseline_front_squat_1rm": self.baseline_front_squat_1rm,
            "baseline_bench_press_1rm": self.baseline_bench_press_1rm,
            "baseline_shoulder_press_1rm": self.baseline_shoulder_press_1rm,
            "baseline_snatch_1rm": self.baseline_snatch_1rm,
            "baseline_clean_jerk_1rm": self.baseline_clean_jerk_1rm,
            "baseline_pullups_max": self.baseline_pullups_max,

            # Program state
            "current_phase": self.current_phase,
            "weeks_in_current_phase": self.weeks_in_current_phase,
            "program_start_date": self.program_start_date.isoformat(),
            "target_return_date": self.target_return_date.isoformat() if self.target_return_date else None,

            # Goals & Equipment (basic)
            "primary_goal": self.primary_goal,
            "goals_description": self.goals_description,
            "equipment_available": self.equipment_available,
            "preferred_training_time": self.preferred_training_time,
            "session_duration_minutes": self.session_duration_minutes,

            # Training Goals (from TrainingGoalsStep)
            "training_experience": self.training_experience,
            "training_years": self.training_years,
            "secondary_goals": self.secondary_goals,
            "available_days": self.available_days,
            "preferred_time": self.preferred_time,
            "intensity_preference": self.intensity_preference,

            # Lifestyle (from LifestyleStep)
            "activity_level": self.activity_level,
            "work_type": self.work_type,
            "work_hours_per_day": self.work_hours_per_day,
            "commute_active": self.commute_active,
            "stress_level": self.stress_level,
            "stress_sources": self.stress_sources,
            "sleep_hours": self.sleep_hours,
            "sleep_quality": self.sleep_quality,
            "sleep_schedule": self.sleep_schedule,
            "recovery_capacity": self.recovery_capacity,
            "health_conditions": self.health_conditions,
            "supplements_used": self.supplements_used,

            # Nutrition Goals (from NutritionGoalsStep)
            "nutrition_goal": self.nutrition_goal,
            "diet_type": self.diet_type,
            "calorie_preference": self.calorie_preference,
            "custom_calories": self.custom_calories,
            "manual_target_calories": self.manual_target_calories,
            "manual_target_protein_g": self.manual_target_protein_g,
            "manual_target_carbs_g": self.manual_target_carbs_g,
            "manual_target_fat_g": self.manual_target_fat_g,
            "protein_priority": self.protein_priority,
            "macro_preference": self.macro_preference,
            "meal_frequency": self.meal_frequency,
            "meal_timing": self.meal_timing,
            "intermittent_window": self.intermittent_window,
            "budget_preference": self.budget_preference,
            "cooking_skill": self.cooking_skill,
            "meal_prep_available": self.meal_prep_available,
            "supplements_interest": self.supplements_interest,

            # Allergies & Restrictions
            "allergies": self.allergies,
            "intolerances": self.intolerances,
            "dietary_restrictions": self.dietary_restrictions,

            # Food Preferences
            "favorite_foods": self.favorite_foods,
            "disliked_foods": self.disliked_foods,

            # Account status
            "is_active": self.is_active,
            "is_onboarded": self.is_onboarded,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,

            # Computed fields
            "weeks_in_program": self.get_weeks_in_program(),
            "has_baseline_data": self.has_baseline_strength_data()
        }
