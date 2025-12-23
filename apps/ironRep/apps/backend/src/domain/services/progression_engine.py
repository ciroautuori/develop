"""
Progression Engine Domain Service

Determines when user should progress to next phase based on KPIs and criteria.
"""
from typing import List, Dict
from src.domain.entities.progress_kpi import ProgressKPI
from src.domain.entities.workout_session import WorkoutPhase


class ProgressionEngine:
    """
    Domain service for progression decision-making.

    Uses KPI data to determine if user should:
    - Progress to next phase
    - Maintain current phase
    - Regress to previous phase
    """

    # Progression criteria by phase
    PHASE_CRITERIA = {
        WorkoutPhase.PHASE_1_DECOMPRESSION: {
            "avg_pain_max": 4,
            "compliance_min": 75,
            "pain_free_hours_min": 16,
            "duration_weeks_min": 2
        },
        WorkoutPhase.PHASE_2_STABILIZATION: {
            "avg_pain_max": 3,
            "compliance_min": 80,
            "pain_free_hours_min": 18,
            "duration_weeks_min": 4
        },
        WorkoutPhase.PHASE_3_STRENGTHENING: {
            "avg_pain_max": 2,
            "compliance_min": 85,
            "pain_free_hours_min": 20,
            "deadlift_capacity_min": 40,  # % of baseline
            "duration_weeks_min": 4
        },
        WorkoutPhase.PHASE_4_RETURN_TO_SPORT: {
            "avg_pain_max": 1,
            "compliance_min": 90,
            "pain_free_hours_min": 22,
            "deadlift_capacity_min": 70,
            "duration_weeks_min": 2
        }
    }

    def evaluate_progression(self, recent_kpis: List[ProgressKPI],
                           current_phase: WorkoutPhase,
                           weeks_in_phase: int) -> Dict:
        """
        Evaluate if user should progress to next phase.

        Args:
            recent_kpis: Last 2-4 weeks of KPI data
            current_phase: Current rehabilitation phase
            weeks_in_phase: Number of weeks in current phase

        Returns:
            dict with decision and rationale
        """
        if not recent_kpis:
            return {
                "action": "maintain",
                "reason": "Dati insufficienti per valutazione"
            }

        # Get latest KPI
        latest_kpi = recent_kpis[-1]

        # Get criteria for current phase
        criteria = self.PHASE_CRITERIA.get(current_phase, {})

        # Evaluate each criterion
        criteria_met = {}
        criteria_met["avg_pain"] = latest_kpi.avg_pain_level <= criteria.get("avg_pain_max", 10)
        criteria_met["compliance"] = latest_kpi.compliance_rate >= criteria.get("compliance_min", 0)
        criteria_met["pain_free_time"] = latest_kpi.pain_free_time_hours >= criteria.get("pain_free_hours_min", 0)
        criteria_met["duration"] = weeks_in_phase >= criteria.get("duration_weeks_min", 0)

        # Check strength criteria if applicable
        if "deadlift_capacity_min" in criteria and latest_kpi.max_deadlift_kg:
            # Would need baseline from user profile
            criteria_met["strength"] = True  # Placeholder

        # Decision logic
        if all(criteria_met.values()):
            return self._generate_progression_decision(current_phase)
        elif criteria_met["avg_pain"] and criteria_met["compliance"]:
            return {
                "action": "maintain",
                "reason": "Buon progresso ma necessario più tempo in questa fase",
                "focus_areas": [k for k, v in criteria_met.items() if not v]
            }
        else:
            return self._generate_regression_decision(latest_kpi)

    def _generate_progression_decision(self, current_phase: WorkoutPhase) -> Dict:
        """Generate decision to progress to next phase."""
        phase_map = {
            WorkoutPhase.PHASE_1_DECOMPRESSION: WorkoutPhase.PHASE_2_STABILIZATION,
            WorkoutPhase.PHASE_2_STABILIZATION: WorkoutPhase.PHASE_3_STRENGTHENING,
            WorkoutPhase.PHASE_3_STRENGTHENING: WorkoutPhase.PHASE_4_RETURN_TO_SPORT,
            WorkoutPhase.PHASE_4_RETURN_TO_SPORT: None  # Completed!
        }

        next_phase = phase_map.get(current_phase)

        if next_phase:
            return {
                "action": "progress",
                "next_phase": next_phase.value,
                "intensity_adjustment": "increase_10_percent",
                "new_exercises": self._get_phase_exercises(next_phase),
                "message": f"✅ Criteri soddisfatti! Passaggio a {next_phase.value}"
            }
        else:
            return {
                "action": "complete",
                "message": "🎉 Programma completato! Ritorno al CrossFit!"
            }

    def _generate_regression_decision(self, kpi: ProgressKPI) -> Dict:
        """Generate decision to regress or maintain with modifications."""
        focus_areas = kpi.get_focus_areas()

        return {
            "action": "modify",
            "reason": "Alcuni criteri non soddisfatti",
            "focus_areas": focus_areas,
            "recommendations": [
                "Ridurre intensità 20%",
                "Focus su esercizi decompressione",
                "Check-in quotidiano più dettagliato"
            ]
        }

    def _get_phase_exercises(self, phase: WorkoutPhase) -> List[str]:
        """Get recommended exercises for a phase."""
        exercises_by_phase = {
            WorkoutPhase.PHASE_1_DECOMPRESSION: [
                "cat_cow", "bird_dog", "dead_bug", "child_pose"
            ],
            WorkoutPhase.PHASE_2_STABILIZATION: [
                "plank", "side_plank", "glute_bridge", "clamshells"
            ],
            WorkoutPhase.PHASE_3_STRENGTHENING: [
                "trap_bar_deadlift", "goblet_squat", "step_ups", "kb_swings"
            ],
            WorkoutPhase.PHASE_4_RETURN_TO_SPORT: [
                "back_squat", "deadlift", "box_jumps", "wall_balls"
            ]
        }

        return exercises_by_phase.get(phase, [])
