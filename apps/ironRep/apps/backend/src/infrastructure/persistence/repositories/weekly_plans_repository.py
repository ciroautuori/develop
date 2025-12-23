"""
Weekly Plans Repository Implementation

Manages storage and retrieval of weekly plans for all agents.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from src.infrastructure.persistence.models import (
    WeeklyPlanModel,
    MedicalProtocolModel,
    CoachWeeklyPlanModel,
    NutritionWeeklyPlanModel,
    UserPreferencesModel
)


def get_week_number(date: datetime) -> tuple[int, int]:
    """Get ISO week number and year for a date."""
    iso_calendar = date.isocalendar()
    return iso_calendar.week, iso_calendar.year


def get_week_start_end(week_number: int, year: int) -> tuple[datetime, datetime]:
    """Get start and end dates for a week number using ISO calendar."""
    # Use fromisocalendar to find the Monday of the given ISO week/year
    start = datetime.fromisocalendar(year, week_number, 1)  # 1 = Monday
    end = datetime.fromisocalendar(year, week_number, 7)    # 7 = Sunday
    
    # Ensure times are at standard boundaries (start of day, end of day if needed)
    # But repos usually return simple dates or datetime at 00:00:00
    return start, end


class WeeklyPlansRepository:
    """Repository for managing weekly plans."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # UNIFIED WEEKLY PLAN
    # =========================================================================

    def get_current_week_plan(self, user_id: str) -> Optional[WeeklyPlanModel]:
        """Get current week's unified plan."""
        week_num, year = get_week_number(datetime.now())
        return self.get_week_plan(user_id, week_num, year)

    def get_week_plan(self, user_id: str, week_number: int, year: int) -> Optional[WeeklyPlanModel]:
        """Get a specific week's plan."""
        return self.db.query(WeeklyPlanModel).filter(
            WeeklyPlanModel.user_id == user_id,
            WeeklyPlanModel.week_number == week_number,
            WeeklyPlanModel.year == year
        ).first()

    def create_week_plan(
        self,
        user_id: str,
        week_number: int,
        year: int,
        coach_plan_id: str = None,
        medical_plan_id: str = None,
        nutrition_plan_id: str = None
    ) -> WeeklyPlanModel:
        """Create a new weekly plan."""
        start_date, end_date = get_week_start_end(week_number, year)

        plan = WeeklyPlanModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            week_number=week_number,
            year=year,
            start_date=start_date,
            end_date=end_date,
            status='active',
            coach_plan_id=coach_plan_id,
            medical_plan_id=medical_plan_id,
            nutrition_plan_id=nutrition_plan_id
        )

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update_week_plan_summaries(
        self,
        plan_id: str,
        coach_summary: Dict = None,
        medical_summary: Dict = None,
        nutrition_summary: Dict = None
    ) -> WeeklyPlanModel:
        """Update week plan summaries."""
        plan = self.db.query(WeeklyPlanModel).filter(WeeklyPlanModel.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        if coach_summary:
            plan.coach_summary = coach_summary
        if medical_summary:
            plan.medical_summary = medical_summary
        if nutrition_summary:
            plan.nutrition_summary = nutrition_summary

        plan.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_month_plans(self, user_id: str, year: int, month: int) -> List[WeeklyPlanModel]:
        """Get all weekly plans for a month."""
        # Get first and last day of month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)

        return self.db.query(WeeklyPlanModel).filter(
            WeeklyPlanModel.user_id == user_id,
            WeeklyPlanModel.start_date >= first_day,
            WeeklyPlanModel.end_date <= last_day + timedelta(days=7)
        ).order_by(WeeklyPlanModel.week_number).all()

    # =========================================================================
    # COACH WEEKLY PLAN
    # =========================================================================

    def get_coach_plan(self, user_id: str, week_number: int, year: int) -> Optional[CoachWeeklyPlanModel]:
        """Get coach plan for a week."""
        return self.db.query(CoachWeeklyPlanModel).filter(
            CoachWeeklyPlanModel.user_id == user_id,
            CoachWeeklyPlanModel.week_number == week_number,
            CoachWeeklyPlanModel.year == year
        ).first()

    def get_current_coach_plan(self, user_id: str) -> Optional[CoachWeeklyPlanModel]:
        """Get current week's coach plan."""
        week_num, year = get_week_number(datetime.now())
        return self.get_coach_plan(user_id, week_num, year)

    def create_coach_plan(
        self,
        user_id: str,
        week_number: int,
        year: int,
        name: str,
        focus: str,
        sport_type: str,
        sessions: List[Dict],
        medical_constraints: Dict = None,
        max_intensity: int = 100
    ) -> CoachWeeklyPlanModel:
        """Create a new coach weekly plan."""
        plan = CoachWeeklyPlanModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            week_number=week_number,
            year=year,
            name=name,
            focus=focus,
            sport_type=sport_type,
            sessions=sessions,
            total_sessions=len([s for s in sessions if s.get('name') != 'Rest']),
            completed_sessions=0,
            medical_constraints=medical_constraints,
            max_intensity_percent=max_intensity,
            status='active'
        )

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update_coach_session_completed(self, plan_id: str, session_index: int) -> CoachWeeklyPlanModel:
        """Mark a session as completed."""
        plan = self.db.query(CoachWeeklyPlanModel).filter(CoachWeeklyPlanModel.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        sessions = plan.sessions
        if 0 <= session_index < len(sessions):
            sessions[session_index]['completed'] = True
            plan.sessions = sessions
            plan.completed_sessions = len([s for s in sessions if s.get('completed')])

        plan.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(plan)
        return plan

    # =========================================================================
    # MEDICAL PROTOCOL
    # =========================================================================

    def get_medical_protocol(self, user_id: str, week_number: int, year: int) -> Optional[MedicalProtocolModel]:
        """Get medical protocol for a week."""
        return self.db.query(MedicalProtocolModel).filter(
            MedicalProtocolModel.user_id == user_id,
            MedicalProtocolModel.week_number == week_number,
            MedicalProtocolModel.year == year
        ).first()

    def get_current_medical_protocol(self, user_id: str) -> Optional[MedicalProtocolModel]:
        """Get current week's medical protocol."""
        week_num, year = get_week_number(datetime.now())
        return self.get_medical_protocol(user_id, week_num, year)

    def create_medical_protocol(
        self,
        user_id: str,
        week_number: int,
        year: int,
        phase: str,
        phase_number: int,
        daily_exercises: List[Dict],
        restrictions: List[str] = None,
        starting_pain: float = None,
        target_pain_reduction: float = None
    ) -> MedicalProtocolModel:
        """Create a new medical protocol."""
        protocol = MedicalProtocolModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            week_number=week_number,
            year=year,
            phase=phase,
            phase_number=phase_number,
            daily_exercises=daily_exercises,
            restrictions=restrictions or [],
            starting_pain_level=starting_pain,
            target_pain_reduction=target_pain_reduction,
            status='active'
        )

        self.db.add(protocol)
        self.db.commit()
        self.db.refresh(protocol)
        return protocol

    def increment_checkin(self, protocol_id: str) -> MedicalProtocolModel:
        """Increment check-in count."""
        protocol = self.db.query(MedicalProtocolModel).filter(MedicalProtocolModel.id == protocol_id).first()
        if not protocol:
            raise ValueError(f"Protocol {protocol_id} not found")

        protocol.checkins_completed += 1
        protocol.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(protocol)
        return protocol

    # =========================================================================
    # NUTRITION WEEKLY PLAN
    # =========================================================================

    def get_nutrition_plan(self, user_id: str, week_number: int, year: int) -> Optional[NutritionWeeklyPlanModel]:
        """Get nutrition plan for a week."""
        return self.db.query(NutritionWeeklyPlanModel).filter(
            NutritionWeeklyPlanModel.user_id == user_id,
            NutritionWeeklyPlanModel.week_number == week_number,
            NutritionWeeklyPlanModel.year == year
        ).first()

    def get_current_nutrition_plan(self, user_id: str) -> Optional[NutritionWeeklyPlanModel]:
        """Get current week's nutrition plan."""
        week_num, year = get_week_number(datetime.now())
        return self.get_nutrition_plan(user_id, week_num, year)

    def create_nutrition_plan(
        self,
        user_id: str,
        week_number: int,
        year: int,
        goal: str,
        daily_calories: int,
        daily_protein: int,
        daily_carbs: int,
        daily_fat: int,
        daily_meals: List[Dict] = None,
        diet_type: str = None,
        excluded_foods: List[str] = None,
        preferred_foods: List[str] = None
    ) -> NutritionWeeklyPlanModel:
        """Create a new nutrition weekly plan."""
        plan = NutritionWeeklyPlanModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            week_number=week_number,
            year=year,
            goal=goal,
            daily_calories=daily_calories,
            daily_protein=daily_protein,
            daily_carbs=daily_carbs,
            daily_fat=daily_fat,
            daily_meals=daily_meals or [],
            diet_type=diet_type,
            excluded_foods=excluded_foods,
            preferred_foods=preferred_foods,
            status='active'
        )

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    # =========================================================================
    # USER PREFERENCES
    # =========================================================================

    def get_preferences(self, user_id: str) -> Optional[UserPreferencesModel]:
        """Get user preferences."""
        return self.db.query(UserPreferencesModel).filter(
            UserPreferencesModel.user_id == user_id
        ).first()

    def save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> UserPreferencesModel:
        """Save or update user preferences."""
        existing = self.get_preferences(user_id)

        if existing:
            for key, value in preferences.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return existing

        prefs = UserPreferencesModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            **preferences
        )
        self.db.add(prefs)
        self.db.commit()
        self.db.refresh(prefs)
        return prefs

    # =========================================================================
    # HISTORY
    # =========================================================================

    def get_plan_history(self, user_id: str, agent_type: str, limit: int = 12) -> List:
        """Get plan history for an agent."""
        if agent_type == 'coach':
            return self.db.query(CoachWeeklyPlanModel).filter(
                CoachWeeklyPlanModel.user_id == user_id
            ).order_by(
                CoachWeeklyPlanModel.year.desc(),
                CoachWeeklyPlanModel.week_number.desc()
            ).limit(limit).all()

        elif agent_type == 'medical':
            return self.db.query(MedicalProtocolModel).filter(
                MedicalProtocolModel.user_id == user_id
            ).order_by(
                MedicalProtocolModel.year.desc(),
                MedicalProtocolModel.week_number.desc()
            ).limit(limit).all()

        elif agent_type == 'nutrition':
            return self.db.query(NutritionWeeklyPlanModel).filter(
                NutritionWeeklyPlanModel.user_id == user_id
            ).order_by(
                NutritionWeeklyPlanModel.year.desc(),
                NutritionWeeklyPlanModel.week_number.desc()
            ).limit(limit).all()

        return []
