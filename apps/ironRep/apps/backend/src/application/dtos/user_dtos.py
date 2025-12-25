from pydantic import BaseModel, Field
from typing import List, Optional

class UserDTO(BaseModel):
    """DTO for user profile data."""
    id: str
    email: str
    name: str
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    sex: Optional[str] = None
    injury_date: Optional[str] = None
    diagnosis: str
    pain_locations: List[str] = []
    injury_description: str = ""
    baseline_deadlift_1rm: Optional[float] = None
    baseline_squat_1rm: Optional[float] = None
    baseline_front_squat_1rm: Optional[float] = None
    baseline_bench_press_1rm: Optional[float] = None
    baseline_shoulder_press_1rm: Optional[float] = None
    baseline_snatch_1rm: Optional[float] = None
    baseline_clean_jerk_1rm: Optional[float] = None
    baseline_pullups_max: Optional[int] = None
    current_phase: str
    weeks_in_current_phase: int
    program_start_date: str
    target_return_date: Optional[str] = None
    primary_goal: Optional[str] = None
    goals_description: Optional[str] = None
    equipment_available: List[str] = []
    preferred_training_time: Optional[str] = None
    session_duration_minutes: int = 60
    is_active: bool = True
    is_onboarded: bool = False
    created_at: str
    updated_at: str
    weeks_in_program: int = 0
    has_baseline_data: bool = False


class OnboardingRequestDTO(BaseModel):
    """DTO for onboarding request - comprehensive wizard data collection."""
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    age: Optional[int] = Field(None, ge=18, le=100)
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    height_cm: Optional[float] = Field(None, ge=100, le=250)
    sex: Optional[str] = Field(None, pattern="^(M|F|O)$")

    # Injury details (all optional for users without injuries)
    has_injury: bool = Field(default=False, description="Whether user has an active injury")
    injury_date: Optional[str] = Field(None, description="Injury date ISO format")
    diagnosis: str = Field(default="")
    pain_locations: List[str] = Field(default_factory=list)
    injury_description: Optional[str] = None

    # Baseline strength
    baseline_deadlift_1rm: Optional[float] = Field(None, ge=0)
    baseline_squat_1rm: Optional[float] = Field(None, ge=0)
    baseline_front_squat_1rm: Optional[float] = Field(None, ge=0)
    baseline_bench_press_1rm: Optional[float] = Field(None, ge=0)
    baseline_shoulder_press_1rm: Optional[float] = Field(None, ge=0)
    baseline_snatch_1rm: Optional[float] = Field(None, ge=0)
    baseline_clean_jerk_1rm: Optional[float] = Field(None, ge=0)
    baseline_pullups_max: Optional[int] = Field(None, ge=0)

    # Goals
    target_return_date: Optional[str] = None
    primary_goal: Optional[str] = None
    goals_description: Optional[str] = None

    # Equipment & Preferences
    equipment_available: List[str] = Field(default_factory=list)
    preferred_training_time: Optional[str] = None
    session_duration_minutes: int = Field(default=60, ge=20, le=180)

    # =========================================================================
    # TRAINING GOALS & EXPERIENCE (from TrainingGoalsStep)
    # =========================================================================
    training_experience: Optional[str] = Field(None, description="beginner, intermediate, advanced, elite")
    training_years: Optional[int] = Field(None, ge=0, le=50)
    secondary_goals: List[str] = Field(default_factory=list)
    available_days: Optional[int] = Field(None, ge=1, le=7)
    preferred_time: Optional[str] = Field(None, description="morning, afternoon, evening, flexible")
    intensity_preference: Optional[str] = Field(None, description="low, moderate, high, variable")

    # =========================================================================
    # LIFESTYLE & RECOVERY (from LifestyleStep)
    # =========================================================================
    activity_level: Optional[str] = Field(None, description="sedentary, lightly_active, moderately_active, very_active, extra_active")
    work_type: Optional[str] = Field(None, description="desk_job, light_activity, moderate_activity, heavy_labor, mixed")
    work_hours_per_day: Optional[int] = Field(None, ge=0, le=16)
    commute_active: Optional[bool] = Field(None)
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    stress_sources: List[str] = Field(default_factory=list)
    sleep_hours: Optional[float] = Field(None, ge=0, le=14)
    sleep_quality: Optional[str] = Field(None, description="poor, fair, good, excellent")
    sleep_schedule: Optional[str] = Field(None, description="consistent, variable, shift_work, irregular")
    recovery_capacity: Optional[str] = Field(None, description="fast, normal, slow, variable")
    health_conditions: List[str] = Field(default_factory=list)
    supplements_used: List[str] = Field(default_factory=list)

    # =========================================================================
    # NUTRITION GOALS & PREFERENCES (from NutritionGoalsStep)
    # =========================================================================
    nutrition_goal: Optional[str] = Field(None, description="fat_loss, muscle_gain, maintenance, recomp, performance")
    diet_type: Optional[str] = Field(None, description="balanced, low_carb, keto, high_protein, mediterranean, vegetarian, vegan, pescatarian")
    calorie_preference: Optional[str] = Field(None, description="auto_calculate, manual")
    custom_calories: Optional[int] = Field(None, ge=800, le=6000)
    target_calories: Optional[int] = Field(None, ge=1000, le=5000)  # Legacy support
    protein_priority: Optional[str] = Field(None, description="standard, high, very_high")
    macro_preference: Optional[str] = Field(None, description="balanced, high_protein, low_carb, high_carb, flexible")
    meal_frequency: Optional[int] = Field(None, ge=1, le=8)
    meal_timing: Optional[str] = Field(None, description="flexible, structured, intermittent_fasting, pre_post_workout")
    intermittent_window: Optional[str] = Field(None, description="16:8, 18:6, 20:4, 5:2, custom")
    budget_preference: Optional[str] = Field(None, description="budget_friendly, moderate, premium, no_limit")
    cooking_skill: Optional[str] = Field(None, description="beginner, intermediate, advanced, chef")
    meal_prep_available: Optional[bool] = Field(None)
    supplements_interest: List[str] = Field(default_factory=list)

    # =========================================================================
    # ALLERGIES & DIETARY RESTRICTIONS
    # =========================================================================
    allergies: List[str] = Field(default_factory=list, description="Food allergies")
    intolerances: List[str] = Field(default_factory=list, description="Food intolerances")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions")

    # =========================================================================
    # FOOD PREFERENCES
    # =========================================================================
    favorite_foods: List[str] = Field(default_factory=list)
    disliked_foods: List[str] = Field(default_factory=list)

    # =========================================================================
    # MODULAR AGENT CONFIGURATION (from Wizard)
    # =========================================================================
    medical_mode: Optional[str] = Field("wellness_tips", description="injury_recovery, wellness_tips, disabled")
    coach_mode: Optional[str] = Field("general_fitness", description="crossfit, bodybuilding, powerlifting, running, functional, general_fitness, rehab_focused")
    nutrition_mode: Optional[str] = Field("tips_tracking", description="full_diet_plan, recipes_only, tips_tracking, disabled")
    sport_type: Optional[str] = Field(None, description="Specific sport type if selected")


class BiometricsUpdateDTO(BaseModel):
    """DTO for updating biometric data specifically."""
    age: Optional[int] = Field(None, ge=18, le=100)
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    height_cm: Optional[float] = Field(None, ge=100, le=250)
    sex: Optional[str] = Field(None, pattern="^(M|F|O)$")

class MedicalUpdateDTO(BaseModel):
    """DTO for updating medical/injury status."""
    has_injury: bool
    injury_date: Optional[str] = None
    diagnosis: Optional[str] = None
    pain_locations: List[str] = Field(default_factory=list)
    injury_description: Optional[str] = None
    medical_mode: Optional[str] = Field(None, description="injury_recovery, wellness_tips")

class GoalsUpdateDTO(BaseModel):
    """DTO for updating training goals."""
    primary_goal: Optional[str] = None
    training_experience: Optional[str] = None
    available_days: Optional[int] = Field(None, ge=1, le=7)
    coach_mode: Optional[str] = None
    nutrition_mode: Optional[str] = None
