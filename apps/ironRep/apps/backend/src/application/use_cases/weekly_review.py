"""
Weekly Review Use Case

Calculates KPIs, evaluates progression, and generates next week's program.
"""
from datetime import datetime, timedelta
from typing import List

from src.domain.entities.progress_kpi import ProgressKPI
from src.domain.entities.workout_session import WorkoutPhase
from src.domain.services.progression_engine import ProgressionEngine
from src.domain.repositories.pain_repository import IPainRepository
from src.domain.repositories.workout_repository import IWorkoutRepository
from src.domain.repositories.kpi_repository import IKPIRepository
from src.application.dtos.dtos import WeeklyReviewResponseDTO, KPIDTO, WorkoutDTO


class WeeklyReviewUseCase:
    """
    Use case for weekly progress review and planning.

    Analyzes weekly performance and decides on progression.
    """

    def __init__(
        self,
        pain_repository: IPainRepository,
        workout_repository: IWorkoutRepository,
        kpi_repository: IKPIRepository,
        workout_generator,
        user_repository=None,
        user_id: str = None
    ):
        self.pain_repository = pain_repository
        self.workout_repository = workout_repository
        self.kpi_repository = kpi_repository
        self.workout_generator = workout_generator
        self.user_repository = user_repository
        self.user_id = user_id
        self.progression_engine = ProgressionEngine()

    async def execute(self, week_number: int) -> WeeklyReviewResponseDTO:
        """
        Execute weekly review.

        Args:
            week_number: Current week number in program

        Returns:
            WeeklyReviewResponseDTO with KPIs and next week plan
        """
        # Step 1: Calculate KPIs for the week
        kpi = await self._calculate_weekly_kpi(week_number)

        # Step 2: Save KPI
        saved_kpi = self.kpi_repository.save(kpi)

        # Step 3: Get recent KPI history for progression evaluation
        kpi_history = self.kpi_repository.get_last_n_weeks(self.user_id, n=4)

        # Step 4: Evaluate progression - Get phase from user profile
        current_phase, weeks_in_phase = self._get_user_phase(week_number)

        progression_decision = self.progression_engine.evaluate_progression(
            kpi_history,
            current_phase,
            weeks_in_phase
        )

        # Step 5: Generate next week's program based on decision
        next_week_workouts = await self._generate_next_week_program(
            progression_decision,
            week_number + 1
        )

        # Step 6: Prepare chart data
        chart_data = self._prepare_chart_data(kpi_history)

        # Step 7: Return response
        return WeeklyReviewResponseDTO(
            week_number=week_number,
            kpi=self._kpi_to_dto(saved_kpi),
            progression_decision=progression_decision,
            next_week_program=next_week_workouts,
            chart_data=chart_data
        )

    async def _calculate_weekly_kpi(self, week_number: int) -> ProgressKPI:
        """Calculate KPI metrics for the week."""
        # Get week date range
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()

        # Get pain assessments for the week
        pain_assessments = self.pain_repository.get_by_date_range(
            self.user_id,
            week_start,
            week_end
        )

        # Get workouts for the week
        workouts = self.workout_repository.get_by_week(self.user_id, week_number)

        # Calculate pain metrics
        pain_levels = [a.pain_level for a in pain_assessments]
        avg_pain = sum(pain_levels) / len(pain_levels) if pain_levels else 0
        max_pain = max(pain_levels) if pain_levels else 0
        min_pain = min(pain_levels) if pain_levels else 0

        # Calculate pain-free time (rough estimate)
        # Assuming each pain level represents hours of pain
        # Pain free time = 24 - (avg_pain / 10 * 24)
        pain_free_hours = 24 - (avg_pain / 10 * 24)

        # Calculate compliance
        completed_workouts = [w for w in workouts if w.completed]
        planned_sessions = len(workouts)
        completed_sessions = len(completed_workouts)

        # Create KPI entity
        kpi = ProgressKPI(
            user_id=self.user_id,
            week=week_number,
            start_date=week_start,
            end_date=week_end,
            avg_pain_level=round(avg_pain, 1),
            max_pain_level=max_pain,
            min_pain_level=min_pain,
            pain_free_time_hours=round(pain_free_hours, 1),
            planned_sessions=planned_sessions if planned_sessions > 0 else 3,  # Default 3
            completed_sessions=completed_sessions
        )

        # Calculate compliance rate
        kpi.calculate_compliance_rate()

        return kpi

    async def _generate_next_week_program(
        self,
        progression_decision: dict,
        next_week: int
    ) -> List[WorkoutDTO]:
        """Generate workouts for next week based on progression decision."""
        workouts = []

        # Determine phase for next week
        if progression_decision["action"] == "progress":
            # Move to next phase
            next_phase_str = progression_decision["next_phase"]
            # Parse phase from string (simplified)
            next_phase = WorkoutPhase.PHASE_2_STABILIZATION
        else:
            # Stay in current phase
            next_phase = WorkoutPhase.PHASE_1_DECOMPRESSION

        # Generate 3 workouts for next week (simplified - could be 4-5)
        for day in range(1, 4):
            # Use workout generator with normal pain state for planning
            workout = await self.workout_generator.generate_workout(
                current_pain=2,  # Planning assumes low pain
                pain_locations=["lombare"],  # Default
                triggers=[],
                pain_analysis={},
                phase=next_phase
            )
            workouts.append(workout)

        return workouts

    def _prepare_chart_data(self, kpi_history: List[ProgressKPI]) -> dict:
        """Prepare data for charts."""
        weeks = [kpi.week for kpi in kpi_history]
        avg_pain = [kpi.avg_pain_level for kpi in kpi_history]
        compliance = [kpi.compliance_rate for kpi in kpi_history]
        pain_free_hours = [kpi.pain_free_time_hours for kpi in kpi_history]

        return {
            "weeks": weeks,
            "avg_pain_levels": avg_pain,
            "compliance_rates": compliance,
            "pain_free_hours": pain_free_hours
        }

    def _kpi_to_dto(self, kpi: ProgressKPI) -> KPIDTO:
        """Convert KPI entity to DTO."""
        return KPIDTO(
            week=kpi.week,
            start_date=kpi.start_date.isoformat(),
            end_date=kpi.end_date.isoformat() if kpi.end_date else None,
            avg_pain_level=kpi.avg_pain_level,
            max_pain_level=kpi.max_pain_level,
            min_pain_level=kpi.min_pain_level,
            pain_free_time_hours=kpi.pain_free_time_hours,
            compliance_rate=kpi.compliance_rate,
            completed_sessions=kpi.completed_sessions,
            planned_sessions=kpi.planned_sessions,
            meets_progression_criteria=kpi.meets_progression_criteria(),
            focus_areas=kpi.get_focus_areas()
        )

    def _get_user_phase(self, week_number: int) -> tuple:
        """
        Get current phase and weeks in phase from user profile.

        Args:
            week_number: Current week number (fallback)

        Returns:
            Tuple of (WorkoutPhase, weeks_in_phase)
        """
        if self.user_repository:
            try:
                user = self.user_repository.get_by_id(self.user_id)
                if user:
                    # Map user.current_phase string to WorkoutPhase enum
                    phase_mapping = {
                        WorkoutPhase.PHASE_1_DECOMPRESSION.value: WorkoutPhase.PHASE_1_DECOMPRESSION,
                        WorkoutPhase.PHASE_2_STABILIZATION.value: WorkoutPhase.PHASE_2_STABILIZATION,
                        WorkoutPhase.PHASE_3_STRENGTHENING.value: WorkoutPhase.PHASE_3_STRENGTHENING,
                        WorkoutPhase.PHASE_4_RETURN_TO_SPORT.value: WorkoutPhase.PHASE_4_RETURN_TO_SPORT,
                    }
                    current_phase = phase_mapping.get(
                        user.current_phase,
                        WorkoutPhase.PHASE_1_DECOMPRESSION
                    )
                    weeks_in_phase = user.weeks_in_current_phase or week_number
                    return current_phase, weeks_in_phase
            except Exception as e:
                print(f"⚠️ Error getting user phase: {e}")

        # Fallback to defaults
        return WorkoutPhase.PHASE_1_DECOMPRESSION, week_number
