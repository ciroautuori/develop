"""
User Repository Implementation

SQLAlchemy implementation of IUserRepository.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from src.domain.entities.user import User, Sex
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.persistence.models import UserModel


class UserRepositoryImpl(IUserRepository):
    """
    SQLAlchemy implementation of User repository.

    Handles mapping between User domain entity and UserModel ORM model.
    """

    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        """Save or update user."""
        # Check if user exists
        existing = self.db.query(UserModel).filter(UserModel.id == user.id).first()

        if existing:
            # Update existing
            return self.update(user)
        else:
            # Create new
            user_model = self._entity_to_model(user)
            self.db.add(user_model)
            self.db.commit()
            self.db.refresh(user_model)
            return self._model_to_entity(user_model)

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        user_model = self.db.query(UserModel).filter(
            UserModel.id == user_id,
            UserModel.is_active == True
        ).first()

        if user_model:
            return self._model_to_entity(user_model)
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_model = self.db.query(UserModel).filter(
            UserModel.email == email,
            UserModel.is_active == True
        ).first()

        if user_model:
            return self._model_to_entity(user_model)
        return None

    def get_all_active(self) -> List[User]:
        """Get all active users."""
        user_models = self.db.query(UserModel).filter(
            UserModel.is_active == True
        ).all()

        return [self._model_to_entity(model) for model in user_models]

    def update(self, user: User) -> User:
        """Update existing user."""
        user_model = self.db.query(UserModel).filter(UserModel.id == user.id).first()

        if not user_model:
            raise ValueError(f"User {user.id} not found")

        # Update fields
        user_model.email = user.email
        user_model.name = user.name
        user_model.age = user.age
        user_model.weight_kg = user.weight_kg
        user_model.height_cm = user.height_cm
        # Handle sex as both string and enum
        # Convert 'male'/'female' to 'M'/'F' for database
        if user.sex:
            if hasattr(user.sex, 'value'):
                user_model.sex = user.sex.value  # Enum -> 'M'/'F'/'O'
            else:
                # String -> convert 'male'/'female' to 'M'/'F'
                sex_map = {'male': 'M', 'female': 'F', 'other': 'O', 'M': 'M', 'F': 'F', 'O': 'O'}
                user_model.sex = sex_map.get(str(user.sex).lower(), 'O')
        else:
            user_model.sex = None
        user_model.injury_date = user.injury_date
        user_model.diagnosis = user.diagnosis
        user_model.pain_locations = user.pain_locations
        user_model.injury_description = user.injury_description
        user_model.baseline_deadlift_1rm = user.baseline_deadlift_1rm
        user_model.baseline_squat_1rm = user.baseline_squat_1rm
        user_model.baseline_front_squat_1rm = user.baseline_front_squat_1rm
        user_model.baseline_bench_press_1rm = user.baseline_bench_press_1rm
        user_model.baseline_shoulder_press_1rm = user.baseline_shoulder_press_1rm
        user_model.baseline_snatch_1rm = user.baseline_snatch_1rm
        user_model.baseline_clean_jerk_1rm = user.baseline_clean_jerk_1rm
        user_model.baseline_pullups_max = user.baseline_pullups_max
        user_model.current_phase = user.current_phase
        user_model.weeks_in_current_phase = user.weeks_in_current_phase
        user_model.program_start_date = user.program_start_date
        user_model.target_return_date = user.target_return_date
        user_model.primary_goal = user.primary_goal
        user_model.goals_description = user.goals_description
        user_model.equipment_available = user.equipment_available
        user_model.preferred_training_time = user.preferred_training_time
        user_model.session_duration_minutes = user.session_duration_minutes
        user_model.is_active = user.is_active
        user_model.is_onboarded = user.is_onboarded
        user_model.updated_at = datetime.now()
        user_model.last_login_at = user.last_login_at

        self.db.commit()
        self.db.refresh(user_model)
        return self._model_to_entity(user_model)

    def delete(self, user_id: str) -> bool:
        """Soft delete user."""
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()

        if not user_model:
            return False

        user_model.is_active = False
        user_model.updated_at = datetime.now()
        self.db.commit()
        return True

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        count = self.db.query(UserModel).filter(
            UserModel.email == email,
            UserModel.is_active == True
        ).count()
        return count > 0

    def _entity_to_model(self, user: User) -> UserModel:
        """Convert User entity to UserModel ORM model with all comprehensive wizard fields."""
        return UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            name=user.name,
            age=user.age,
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            # Handle sex: convert 'male'/'female' to 'M'/'F' for database (varchar(1))
            sex=(
                user.sex.value if hasattr(user.sex, 'value')
                else {'male': 'M', 'female': 'F', 'other': 'O', 'M': 'M', 'F': 'F', 'O': 'O'}.get(str(user.sex).lower(), 'O')
                if user.sex else None
            ),
            injury_date=user.injury_date,
            diagnosis=user.diagnosis,
            pain_locations=user.pain_locations,
            injury_description=user.injury_description,
            baseline_deadlift_1rm=user.baseline_deadlift_1rm,
            baseline_squat_1rm=user.baseline_squat_1rm,
            baseline_front_squat_1rm=user.baseline_front_squat_1rm,
            baseline_bench_press_1rm=user.baseline_bench_press_1rm,
            baseline_shoulder_press_1rm=user.baseline_shoulder_press_1rm,
            baseline_snatch_1rm=user.baseline_snatch_1rm,
            baseline_clean_jerk_1rm=user.baseline_clean_jerk_1rm,
            baseline_pullups_max=user.baseline_pullups_max,
            current_phase=user.current_phase,
            weeks_in_current_phase=user.weeks_in_current_phase,
            program_start_date=user.program_start_date,
            target_return_date=user.target_return_date,
            primary_goal=user.primary_goal,
            goals_description=user.goals_description,
            equipment_available=user.equipment_available,
            preferred_training_time=user.preferred_training_time,
            session_duration_minutes=user.session_duration_minutes,
            # Training Goals (from TrainingGoalsStep)
            training_experience=user.training_experience,
            training_years=user.training_years,
            secondary_goals=user.secondary_goals,
            available_days=user.available_days,
            preferred_time=user.preferred_time,
            intensity_preference=user.intensity_preference,
            # Lifestyle (from LifestyleStep)
            activity_level=user.activity_level,
            work_type=user.work_type,
            work_hours_per_day=user.work_hours_per_day,
            commute_active=user.commute_active,
            stress_level=user.stress_level,
            stress_sources=user.stress_sources,
            sleep_hours=user.sleep_hours,
            sleep_quality=user.sleep_quality,
            sleep_schedule=user.sleep_schedule,
            recovery_capacity=user.recovery_capacity,
            health_conditions=user.health_conditions,
            supplements_used=user.supplements_used,
            # Nutrition Goals (from NutritionGoalsStep)
            nutrition_goal=user.nutrition_goal,
            diet_type=user.diet_type,
            calorie_preference=user.calorie_preference,
            custom_calories=user.custom_calories,
            manual_target_calories=user.manual_target_calories,
            manual_target_protein_g=user.manual_target_protein_g,
            manual_target_carbs_g=user.manual_target_carbs_g,
            manual_target_fat_g=user.manual_target_fat_g,
            protein_priority=user.protein_priority,
            macro_preference=user.macro_preference,
            meal_frequency=user.meal_frequency,
            meal_timing=user.meal_timing,
            intermittent_window=user.intermittent_window,
            budget_preference=user.budget_preference,
            cooking_skill=user.cooking_skill,
            meal_prep_available=user.meal_prep_available,
            supplements_interest=user.supplements_interest,
            # Allergies & Restrictions
            allergies=user.allergies,
            intolerances=user.intolerances,
            dietary_restrictions=user.dietary_restrictions,
            # Food Preferences
            favorite_foods=user.favorite_foods,
            disliked_foods=user.disliked_foods,
            # Account status
            is_active=user.is_active,
            is_onboarded=user.is_onboarded,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert UserModel ORM model to User entity with all comprehensive wizard fields."""
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            name=model.name,
            age=model.age,
            weight_kg=model.weight_kg,
            height_cm=model.height_cm,
            sex=Sex(model.sex) if model.sex else None,
            injury_date=model.injury_date,
            diagnosis=model.diagnosis,
            pain_locations=model.pain_locations or [],
            injury_description=model.injury_description or "",
            baseline_deadlift_1rm=model.baseline_deadlift_1rm,
            baseline_squat_1rm=model.baseline_squat_1rm,
            baseline_front_squat_1rm=model.baseline_front_squat_1rm,
            baseline_bench_press_1rm=model.baseline_bench_press_1rm,
            baseline_shoulder_press_1rm=model.baseline_shoulder_press_1rm,
            baseline_snatch_1rm=model.baseline_snatch_1rm,
            baseline_clean_jerk_1rm=model.baseline_clean_jerk_1rm,
            baseline_pullups_max=model.baseline_pullups_max,
            current_phase=model.current_phase,
            weeks_in_current_phase=model.weeks_in_current_phase,
            program_start_date=model.program_start_date,
            target_return_date=model.target_return_date,
            primary_goal=model.primary_goal,
            goals_description=model.goals_description,
            equipment_available=model.equipment_available or [],
            preferred_training_time=model.preferred_training_time,
            session_duration_minutes=model.session_duration_minutes,
            # Training Goals (from TrainingGoalsStep)
            training_experience=model.training_experience,
            training_years=model.training_years,
            secondary_goals=model.secondary_goals or [],
            available_days=model.available_days,
            preferred_time=model.preferred_time,
            intensity_preference=model.intensity_preference,
            # Lifestyle (from LifestyleStep)
            activity_level=model.activity_level,
            work_type=model.work_type,
            work_hours_per_day=model.work_hours_per_day,
            commute_active=model.commute_active or False,
            stress_level=model.stress_level,
            stress_sources=model.stress_sources or [],
            sleep_hours=model.sleep_hours,
            sleep_quality=model.sleep_quality,
            sleep_schedule=model.sleep_schedule,
            recovery_capacity=model.recovery_capacity,
            health_conditions=model.health_conditions or [],
            supplements_used=model.supplements_used or [],
            # Nutrition Goals (from NutritionGoalsStep)
            nutrition_goal=model.nutrition_goal,
            diet_type=model.diet_type,
            calorie_preference=model.calorie_preference,
            custom_calories=model.custom_calories,
            manual_target_calories=getattr(model, "manual_target_calories", None),
            manual_target_protein_g=getattr(model, "manual_target_protein_g", None),
            manual_target_carbs_g=getattr(model, "manual_target_carbs_g", None),
            manual_target_fat_g=getattr(model, "manual_target_fat_g", None),
            protein_priority=model.protein_priority,
            macro_preference=model.macro_preference,
            meal_frequency=model.meal_frequency,
            meal_timing=model.meal_timing,
            intermittent_window=model.intermittent_window,
            budget_preference=model.budget_preference,
            cooking_skill=model.cooking_skill,
            meal_prep_available=model.meal_prep_available if model.meal_prep_available is not None else True,
            supplements_interest=model.supplements_interest or [],
            # Allergies & Restrictions
            allergies=model.allergies or [],
            intolerances=model.intolerances or [],
            dietary_restrictions=model.dietary_restrictions or [],
            # Food Preferences
            favorite_foods=model.favorite_foods or [],
            disliked_foods=model.disliked_foods or [],
            # Account status
            is_active=model.is_active,
            is_onboarded=model.is_onboarded,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at
        )
