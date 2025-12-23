"""
Medical Domain Entities

Defines structures for medical reports, clearance levels, and constraints.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from src.domain.entities.workout_session import WorkoutPhase

class ConstraintType(str, Enum):
    """Types of medical constraints."""
    NO_SPINAL_LOADING = "no_spinal_loading"
    NO_FLEXION_UNDER_LOAD = "no_flexion_under_load"
    NO_HEAVY_DEADLIFTS = "no_heavy_deadlifts"
    NO_OVERHEAD_PRESSING = "no_overhead_pressing"
    NO_KIPPING = "no_kipping"
    NO_RUNNING = "no_running"
    NO_BOX_JUMPS = "no_box_jumps"
    NO_DEEP_SQUATS = "no_deep_squats"
    KNEE_FLEXION_MAX_90 = "knee_flexion_max_90"
    REDUCE_INTENSITY = "reduce_intensity"
    AVOID_HIGH_IMPACT = "avoid_high_impact"
    LIMIT_ROM = "limit_rom"


class ClearanceLevel(str, Enum):
    """Medical clearance levels for training."""
    RED = "red"       # No training allowed
    YELLOW = "yellow" # Modified training only
    GREEN = "green"   # Full training allowed


@dataclass
class MedicalReport:
    """
    Structured medical report passed from Medical Agent to Coach.

    Contains constraints that the Coach must respect when generating workouts.
    """
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Pain assessment
    current_pain_level: int = 0  # 0-10
    pain_locations: List[str] = field(default_factory=list)
    pain_trend: str = "stable"  # improving, stable, worsening

    # Medical constraints
    constraints: List[str] = field(default_factory=list)
    clearance_level: ClearanceLevel = ClearanceLevel.YELLOW
    phase: WorkoutPhase = WorkoutPhase.PHASE_1_DECOMPRESSION

    # Recommendations
    max_intensity_percent: int = 70  # % of 1RM
    max_session_duration_minutes: int = 45
    recommended_focus: List[str] = field(default_factory=list)
    avoid_movements: List[str] = field(default_factory=list)

    # Notes
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "current_pain_level": self.current_pain_level,
            "pain_locations": self.pain_locations,
            "pain_trend": self.pain_trend,
            "constraints": self.constraints,
            "clearance_level": self.clearance_level.value,
            "phase": self.phase.value,
            "max_intensity_percent": self.max_intensity_percent,
            "max_session_duration_minutes": self.max_session_duration_minutes,
            "recommended_focus": self.recommended_focus,
            "avoid_movements": self.avoid_movements,
            "notes": self.notes
        }

    def is_safe_for_training(self) -> bool:
        """Check if user is cleared for any training."""
        return self.clearance_level != ClearanceLevel.RED

    def get_constraint_summary(self) -> str:
        """Get human-readable constraint summary."""
        if not self.constraints:
            return "Nessuna restrizione particolare."

        return f"Restrizioni attive: {', '.join(self.constraints)}"
