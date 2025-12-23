"""
SQLAlchemy ORM Models

ORM models that map to database tables.
These are separate from domain entities to maintain separation of concerns.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .database import Base
from src.domain.entities.workout_session import WorkoutPhase


class UserModel(Base):
    """User table model with comprehensive wizard data fields."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    sex = Column(String(1), nullable=True)

    # Injury details
    injury_date = Column(DateTime, nullable=True)
    diagnosis = Column(String(255), nullable=True, default='')  # User selects their diagnosis
    pain_locations = Column(JSON, nullable=True)
    injury_description = Column(Text, nullable=True)

    # Baseline strength
    baseline_deadlift_1rm = Column(Float, nullable=True)
    baseline_squat_1rm = Column(Float, nullable=True)
    baseline_front_squat_1rm = Column(Float, nullable=True)
    baseline_bench_press_1rm = Column(Float, nullable=True)
    baseline_shoulder_press_1rm = Column(Float, nullable=True)
    baseline_snatch_1rm = Column(Float, nullable=True)
    baseline_clean_jerk_1rm = Column(Float, nullable=True)
    baseline_pullups_max = Column(Integer, nullable=True)

    # Program state
    current_phase = Column(String(50), nullable=False, default=WorkoutPhase.PHASE_1_DECOMPRESSION.value)
    weeks_in_current_phase = Column(Integer, nullable=False, default=0)
    program_start_date = Column(DateTime, nullable=False, default=datetime.now)

    # Goals
    target_return_date = Column(DateTime, nullable=True)
    primary_goal = Column(String(255), nullable=True)
    goals_description = Column(Text, nullable=True)

    # Preferences
    equipment_available = Column(JSON, nullable=True)
    preferred_training_time = Column(String(50), nullable=True)
    session_duration_minutes = Column(Integer, nullable=True, default=60)

    # =========================================================================
    # TRAINING GOALS & EXPERIENCE (from TrainingGoalsStep)
    # =========================================================================
    training_experience = Column(String(50), nullable=True)  # beginner, intermediate, advanced, elite
    training_years = Column(Integer, nullable=True)
    secondary_goals = Column(JSON, nullable=True)  # List of secondary goals
    available_days = Column(Integer, nullable=True)  # Days per week
    preferred_time = Column(String(50), nullable=True)  # morning, afternoon, evening, flexible
    intensity_preference = Column(String(50), nullable=True)  # low, moderate, high, variable

    # =========================================================================
    # LIFESTYLE & RECOVERY (from LifestyleStep)
    # =========================================================================
    activity_level = Column(String(50), nullable=True)  # sedentary, lightly_active, moderately_active, very_active, extra_active
    work_type = Column(String(50), nullable=True)  # desk_job, light_activity, moderate_activity, heavy_labor, mixed
    work_hours_per_day = Column(Integer, nullable=True)
    commute_active = Column(Boolean, nullable=True, default=False)
    stress_level = Column(Integer, nullable=True)  # 1-5
    stress_sources = Column(JSON, nullable=True)  # List of stress sources
    sleep_hours = Column(Float, nullable=True)
    sleep_quality = Column(String(50), nullable=True)  # poor, fair, good, excellent
    sleep_schedule = Column(String(50), nullable=True)  # consistent, variable, shift_work, irregular
    recovery_capacity = Column(String(50), nullable=True)  # fast, normal, slow, variable
    health_conditions = Column(JSON, nullable=True)  # List of health conditions
    supplements_used = Column(JSON, nullable=True)  # List of supplements currently used

    # =========================================================================
    # NUTRITION GOALS & PREFERENCES (from NutritionGoalsStep)
    # =========================================================================
    nutrition_goal = Column(String(50), nullable=True)  # fat_loss, muscle_gain, maintenance, recomp, performance
    diet_type = Column(String(50), nullable=True)  # balanced, low_carb, keto, high_protein, mediterranean, vegetarian, vegan, pescatarian
    calorie_preference = Column(String(50), nullable=True)  # auto_calculate, manual
    custom_calories = Column(Integer, nullable=True)
    manual_target_calories = Column(Integer, nullable=True)
    manual_target_protein_g = Column(Integer, nullable=True)
    manual_target_carbs_g = Column(Integer, nullable=True)
    manual_target_fat_g = Column(Integer, nullable=True)
    protein_priority = Column(String(50), nullable=True)  # standard, high, very_high
    macro_preference = Column(String(50), nullable=True)  # balanced, high_protein, low_carb, high_carb, flexible
    meal_frequency = Column(Integer, nullable=True)  # Number of meals per day
    meal_timing = Column(String(50), nullable=True)  # flexible, structured, intermittent_fasting, pre_post_workout
    intermittent_window = Column(String(50), nullable=True)  # 16:8, 18:6, 20:4, 5:2, custom
    budget_preference = Column(String(50), nullable=True)  # budget_friendly, moderate, premium, no_limit
    cooking_skill = Column(String(50), nullable=True)  # beginner, intermediate, advanced, chef
    meal_prep_available = Column(Boolean, nullable=True, default=True)
    supplements_interest = Column(JSON, nullable=True)  # List of supplements user is interested in

    # =========================================================================
    # ALLERGIES & DIETARY RESTRICTIONS
    # =========================================================================
    allergies = Column(JSON, nullable=True)  # Food allergies (peanuts, tree_nuts, shellfish, etc.)
    intolerances = Column(JSON, nullable=True)  # Food intolerances (lactose, gluten, etc.)
    dietary_restrictions = Column(JSON, nullable=True)  # Dietary restrictions (no_pork, no_beef, halal, kosher)

    # =========================================================================
    # FOOD PREFERENCES
    # =========================================================================
    favorite_foods = Column(JSON, nullable=True)  # List of favorite foods
    disliked_foods = Column(JSON, nullable=True)  # List of disliked foods

    # Account status
    is_active = Column(Boolean, nullable=False, default=True)
    is_onboarded = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    pain_assessments = relationship("PainAssessmentModel", back_populates="user", cascade="all, delete-orphan")
    workout_sessions = relationship("WorkoutSessionModel", back_populates="user", cascade="all, delete-orphan")
    progress_kpis = relationship("ProgressKPIModel", back_populates="user", cascade="all, delete-orphan")
    biometric_entries = relationship("BiometricEntryModel", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistoryModel", back_populates="user", cascade="all, delete-orphan")
    nutrition_plans = relationship("NutritionPlanModel", back_populates="user", cascade="all, delete-orphan")
    nutrition_logs = relationship("DailyNutritionLogModel", back_populates="user", cascade="all, delete-orphan")
    recipes = relationship("RecipeModel", back_populates="user", cascade="all, delete-orphan")
    google_account = relationship("GoogleAccountModel", back_populates="user", uselist=False, cascade="all, delete-orphan")


class GoogleAccountModel(Base):
    """Google OAuth account linked to a user."""
    __tablename__ = "google_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    google_user_id = Column(String(255), nullable=True, unique=True)
    google_email = Column(String(255), nullable=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    scopes = Column(JSON, nullable=True)
    fit_sync_enabled = Column(Boolean, nullable=False, default=True)
    calendar_sync_enabled = Column(Boolean, nullable=False, default=True)
    last_fit_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    user = relationship("UserModel", back_populates="google_account")


class BiometricEntryModel(Base):
    """Biometric entry table model."""
    __tablename__ = "biometric_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)

    # Strength metrics
    exercise_id = Column(String(100), nullable=True, index=True)
    exercise_name = Column(String(255), nullable=True)
    weight_kg = Column(Float, nullable=True)
    reps = Column(Integer, nullable=True)
    estimated_1rm = Column(Float, nullable=True)

    # ROM metrics
    rom_test = Column(String(100), nullable=True)
    rom_degrees = Column(Float, nullable=True)
    rom_side = Column(String(10), nullable=True)

    # Body composition
    weight = Column(Float, nullable=True)
    body_fat_percent = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)

    # Cardiovascular
    resting_hr = Column(Integer, nullable=True)
    hrv = Column(Integer, nullable=True)
    vo2max_estimate = Column(Float, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relationships
    user = relationship("UserModel", back_populates="biometric_entries")


class ExerciseModel(Base):
    """Exercise table model."""
    __tablename__ = "exercises"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    movement_pattern = Column(String(50), nullable=True)
    phases = Column(JSON, nullable=False)
    equipment = Column(JSON, nullable=False)
    contraindications = Column(JSON, nullable=False)
    progressions = Column(JSON, nullable=True)
    regressions = Column(JSON, nullable=True)
    coaching_cues = Column(JSON, nullable=False)
    video_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    sets_range_min = Column(Integer, nullable=False, default=2)
    sets_range_max = Column(Integer, nullable=False, default=4)
    reps_range_min = Column(Integer, nullable=False, default=5)
    reps_range_max = Column(Integer, nullable=False, default=12)
    rest_seconds = Column(Integer, nullable=False, default=60)
    difficulty = Column(String(20), nullable=False, default='beginner', index=True)
    injury_risk_profile = Column(JSON, nullable=True)  # Multi-injury risk data (replaces sciatica_risk)
    modifications = Column(JSON, nullable=True)  # Injury-specific modifications
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class PainAssessmentModel(Base):
    """ORM model for pain_assessments table."""
    __tablename__ = "pain_assessments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False, index=True)
    pain_level = Column(Integer, nullable=False)
    pain_locations = Column(JSON, nullable=False)  # Stored as JSON array
    triggers = Column(JSON, default=list)  # Stored as JSON array
    medication_taken = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("UserModel", back_populates="pain_assessments")

    def __repr__(self):
        return f"<PainAssessment(id={self.id}, pain_level={self.pain_level}, date={self.date})>"


class WorkoutSessionModel(Base):
    """ORM model for workout_sessions table."""
    __tablename__ = "workout_sessions"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False, index=True)
    phase = Column(String, nullable=False)
    warm_up = Column(JSON, default=list)
    technical_work = Column(JSON, default=list)
    conditioning = Column(JSON, default=list)
    cool_down = Column(JSON, default=list)
    estimated_pain_impact = Column(String, nullable=False)
    contraindications = Column(JSON, default=list)
    completed = Column(Boolean, default=False)
    actual_pain_impact = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("UserModel", back_populates="workout_sessions")

    def __repr__(self):
        return f"<WorkoutSession(session_id={self.session_id}, phase={self.phase}, completed={self.completed})>"


class ProgressKPIModel(Base):
    """ORM model for progress_kpi table."""
    __tablename__ = "progress_kpi"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    week = Column(Integer, nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    avg_pain_level = Column(Float, default=0.0)
    max_pain_level = Column(Integer, default=0)
    min_pain_level = Column(Integer, default=0)
    pain_free_time_hours = Column(Float, default=0.0)
    rom_hip_flexion = Column(Integer, nullable=True)
    rom_lumbar_flexion = Column(Integer, nullable=True)
    max_deadlift_kg = Column(Float, nullable=True)
    max_squat_kg = Column(Float, nullable=True)
    planned_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    compliance_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("UserModel", back_populates="progress_kpis")

    def __repr__(self):
        return f"<ProgressKPI(week={self.week}, avg_pain={self.avg_pain_level}, compliance={self.compliance_rate}%)>"


class UserProfileModel(Base):
    """ORM model for user_profile table."""
    __tablename__ = "user_profile"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, default="Utente")
    age = Column(Integer, nullable=True)
    activity_level = Column(String, default="atleta")
    injury_date = Column(DateTime, nullable=True)
    injury_description = Column(Text, nullable=True)
    diagnosis = Column(String, default="")  # User selects their diagnosis
    baseline_deadlift_kg = Column(Float, nullable=True)
    baseline_squat_kg = Column(Float, nullable=True)
    current_week = Column(Integer, default=1)
    current_phase = Column(String, default=WorkoutPhase.PHASE_1_DECOMPRESSION.value)
    program_start_date = Column(DateTime, default=datetime.now)
    target_return_date = Column(DateTime, nullable=True)
    goals = Column(Text, default="Ritorno al CrossFit intermedio senza dolore")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<UserProfile(name={self.name}, current_week={self.current_week}, phase={self.current_phase})>"


class ChatHistoryModel(Base):
    """Chat history ORM model for persistent conversations."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = Column(String(36), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # For context, tools used, etc.
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relationship to user
    user = relationship("UserModel", back_populates="chat_history")

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id}, role={self.role}, session={self.session_id})>"


class WorkoutPlanModel(Base):
    """Workout plan table model for generated training programs."""
    __tablename__ = "workout_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), nullable=False, default='generated')  # generated, completed, skipped

    # Plan content
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    exercises = Column(JSON, nullable=True)  # List of exercises with sets/reps
    duration_minutes = Column(Integer, nullable=True)

    # Medical constraints applied
    constraints = Column(JSON, nullable=True)  # MedicalReport constraints
    clearance_level = Column(String(20), nullable=True)  # RED, YELLOW, GREEN
    max_intensity_percent = Column(Integer, nullable=True)

    # Completion tracking
    completed_at = Column(DateTime, nullable=True)
    feedback = Column(Text, nullable=True)
    pain_after = Column(Integer, nullable=True)  # 0-10

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("UserModel", backref="workout_plans")

    def __repr__(self):
        return f"<WorkoutPlan(id={self.id}, user_id={self.user_id}, date={self.date}, status={self.status})>"


class ExercisePreferenceModel(Base):
    """Exercise preference table model for user likes/dislikes."""
    __tablename__ = "exercise_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    exercise_id = Column(String(100), nullable=False, index=True)
    exercise_name = Column(String(255), nullable=False)

    # Preference: like, dislike, neutral
    preference = Column(String(20), nullable=False, default='neutral')

    # Rating 1-5 (optional)
    rating = Column(Integer, nullable=True)

    # Reason for preference
    reason = Column(Text, nullable=True)

    # Extra data (equipment, difficulty, etc.)
    extra_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("UserModel", backref="exercise_preferences")

    def __repr__(self):
        return f"<ExercisePreference(user_id={self.user_id}, exercise={self.exercise_name}, pref={self.preference})>"


# ============================================================================
# WEEKLY PLANS - Unified weekly planning system
# ============================================================================

class WeeklyPlanModel(Base):
    """Unified weekly plan that ties together Coach, Medical, Nutrition for a week."""
    __tablename__ = "weekly_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Week identification
    week_number = Column(Integer, nullable=False, index=True)  # 1-52
    year = Column(Integer, nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Status: draft, active, completed, skipped
    status = Column(String(20), nullable=False, default='draft')

    # Agent-specific plan IDs (foreign keys to specific plan tables)
    coach_plan_id = Column(String(36), nullable=True)
    medical_plan_id = Column(String(36), nullable=True)
    nutrition_plan_id = Column(String(36), nullable=True)

    # Summary data for quick access
    coach_summary = Column(JSON, nullable=True)  # {sessions: 4, focus: "Upper/Lower", progress: 75}
    medical_summary = Column(JSON, nullable=True)  # {phase: "Fase 2", avg_pain: 3.5, exercises: 5}
    nutrition_summary = Column(JSON, nullable=True)  # {goal: "deficit", calories: 2200, compliance: 85}

    # Weekly review data
    review_completed = Column(Boolean, default=False)
    review_notes = Column(Text, nullable=True)
    ai_suggestions = Column(JSON, nullable=True)  # AI-generated suggestions for next week

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("UserModel", backref="weekly_plans")

    def __repr__(self):
        return f"<WeeklyPlan(user_id={self.user_id}, week={self.week_number}/{self.year}, status={self.status})>"


class MedicalProtocolModel(Base):
    """Medical/rehabilitation protocol for a week."""
    __tablename__ = "medical_protocols"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Week identification
    week_number = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)

    # Protocol details
    phase = Column(String(100), nullable=False)  # "Fase 1 - Riduzione dolore", etc.
    phase_number = Column(Integer, nullable=False, default=1)

    # Pain tracking targets
    target_pain_reduction = Column(Float, nullable=True)
    starting_pain_level = Column(Float, nullable=True)
    ending_pain_level = Column(Float, nullable=True)

    # Daily exercises
    daily_exercises = Column(JSON, nullable=False, default=list)  # [{name, duration, sets, reps, video_url}]

    # Restrictions and notes
    restrictions = Column(JSON, nullable=True)  # ["No flessione lombare > 30°", etc.]
    notes = Column(Text, nullable=True)

    # Check-in requirements
    checkin_frequency = Column(String(20), default='daily')  # daily, twice_daily, weekly
    checkins_required = Column(Integer, default=7)
    checkins_completed = Column(Integer, default=0)

    # Status
    status = Column(String(20), nullable=False, default='active')

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("UserModel", backref="medical_protocols")

    def __repr__(self):
        return f"<MedicalProtocol(user_id={self.user_id}, phase={self.phase}, week={self.week_number})>"


class CoachWeeklyPlanModel(Base):
    """Coach/workout weekly plan with daily sessions."""
    __tablename__ = "coach_weekly_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Week identification
    week_number = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)

    # Plan details
    name = Column(String(255), nullable=True)  # "Upper/Lower Split", "Push/Pull/Legs"
    focus = Column(String(255), nullable=True)  # "Strength focus", "Deload week"
    sport_type = Column(String(50), nullable=True)  # crossfit, bodybuilding, etc.

    # Sessions for each day (Mon-Sun)
    sessions = Column(JSON, nullable=False, default=list)
    # Structure: [{day: "monday", name: "Upper A", exercises: [...], duration: 60, completed: false}]

    # Progress tracking
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    total_volume = Column(Integer, nullable=True)  # Total sets

    # Medical constraints applied
    medical_constraints = Column(JSON, nullable=True)
    max_intensity_percent = Column(Integer, default=100)

    # Status
    status = Column(String(20), nullable=False, default='active')

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("UserModel", backref="coach_weekly_plans")

    def __repr__(self):
        return f"<CoachWeeklyPlan(user_id={self.user_id}, name={self.name}, week={self.week_number})>"


class NutritionWeeklyPlanModel(Base):
    """Nutrition weekly plan with daily meals."""
    __tablename__ = "nutrition_weekly_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Week identification
    week_number = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)

    # Plan details
    goal = Column(String(50), nullable=False, default='maintenance')  # deficit, maintenance, surplus

    # Daily targets
    daily_calories = Column(Integer, nullable=False)
    daily_protein = Column(Integer, nullable=False)
    daily_carbs = Column(Integer, nullable=False)
    daily_fat = Column(Integer, nullable=False)
    water_target_liters = Column(Float, default=2.5)

    # Daily meal plans (Mon-Sun)
    daily_meals = Column(JSON, nullable=False, default=list)
    # Structure: [{day: "monday", meals: [{name: "Colazione", foods: [...], calories: 400}]}]

    # Preferences applied
    diet_type = Column(String(50), nullable=True)  # balanced, high_protein, keto, vegetarian
    excluded_foods = Column(JSON, nullable=True)  # Allergies, dislikes
    preferred_foods = Column(JSON, nullable=True)

    # Progress tracking
    avg_compliance = Column(Float, default=0)  # 0-100%
    avg_calories_consumed = Column(Integer, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default='active')

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("UserModel", backref="nutrition_weekly_plans")

    def __repr__(self):
        return f"<NutritionWeeklyPlan(user_id={self.user_id}, goal={self.goal}, week={self.week_number})>"


class RecipeModel(Base):
    """Recipe model for user-created recipes."""
    __tablename__ = "recipes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Core Data
    ingredients = Column(JSON, nullable=False)  # List of {food_id, name, brand, grams, macros}
    total_calories = Column(Float, nullable=False)
    total_protein = Column(Float, nullable=False)
    total_carbs = Column(Float, nullable=False)
    total_fat = Column(Float, nullable=False)
    
    # Metadata
    servings = Column(Integer, default=1)
    prep_time_minutes = Column(Integer, nullable=True)
    instructions = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user = relationship("UserModel", back_populates="recipes")

    def __repr__(self):
        return f"<Recipe(name={self.name}, calories={self.total_calories})>"


class UserPreferencesModel(Base):
    """Extended user preferences for personalization."""
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)

    # Training preferences
    preferred_training_days = Column(JSON, nullable=True)  # ["monday", "wednesday", "friday"]
    preferred_training_time = Column(String(20), nullable=True)  # morning, afternoon, evening
    session_duration_minutes = Column(Integer, default=60)
    equipment_available = Column(JSON, nullable=True)  # ["barbell", "dumbbells", "pullup_bar"]
    training_location = Column(String(50), nullable=True)  # home, gym, outdoor

    # Nutrition preferences
    diet_type = Column(String(50), nullable=True)  # balanced, vegetarian, vegan, keto
    allergies = Column(JSON, nullable=True)  # ["nuts", "lactose"]
    disliked_foods = Column(JSON, nullable=True)  # ["broccoli", "liver"]
    favorite_foods = Column(JSON, nullable=True)  # ["chicken", "rice", "eggs"]
    meals_per_day = Column(Integer, default=4)
    cooking_skill = Column(String(20), nullable=True)  # beginner, intermediate, advanced
    meal_prep_time_minutes = Column(Integer, default=30)

    # Medical preferences
    pain_tracking_frequency = Column(String(20), default='daily')
    mobility_routine_time = Column(String(20), nullable=True)  # morning, evening

    # Notification preferences
    workout_reminders = Column(Boolean, default=True)
    meal_reminders = Column(Boolean, default=True)
    pain_checkin_reminders = Column(Boolean, default=True)
    reminder_time = Column(String(10), nullable=True)  # "08:00"

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("UserModel", backref="preferences")

    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id})>"


class WizardSessionModel(Base):
    """
    Wizard session persistence for production reliability.

    Stores interview state to survive server restarts and enable
    session resumption across devices.
    """
    __tablename__ = "wizard_sessions"

    id = Column(String(36), primary_key=True)  # session_id
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    email = Column(String(255), nullable=True)

    # Interview state
    phase = Column(String(50), nullable=False, default='greeting')
    collected_data = Column(JSON, nullable=False, default=dict)
    agent_config = Column(JSON, nullable=False, default=dict)
    conversation_history = Column(JSON, nullable=False, default=list)

    # Metadata
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, nullable=False, default=False)

    # Optional user relationship
    user = relationship("UserModel", backref="wizard_sessions")

    def __repr__(self):
        return f"<WizardSession(id={self.id}, phase={self.phase}, completed={self.is_completed})>"
