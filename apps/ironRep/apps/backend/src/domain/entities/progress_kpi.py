"""
Progress KPI Entity

Tracks weekly key performance indicators for recovery progress.
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class ProgressKPI:
    """
    Entity representing weekly progress metrics.

    Tracks key indicators to determine if user should progress
    to next phase or maintain current phase.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    week: int = 1  # Week number in program
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None

    # Pain metrics
    avg_pain_level: float = 0.0
    max_pain_level: int = 0
    min_pain_level: int = 0
    pain_free_time_hours: float = 0.0

    # Mobility metrics
    rom_hip_flexion: Optional[int] = None  # degrees
    rom_lumbar_flexion: Optional[int] = None  # degrees

    # Strength metrics
    max_deadlift_kg: Optional[float] = None
    max_squat_kg: Optional[float] = None

    # Compliance metrics
    planned_sessions: int = 0
    completed_sessions: int = 0
    compliance_rate: float = 0.0

    def calculate_compliance_rate(self):
        """Calculate compliance percentage."""
        if self.planned_sessions > 0:
            self.compliance_rate = (self.completed_sessions / self.planned_sessions) * 100
        else:
            self.compliance_rate = 0.0

    def meets_progression_criteria(self) -> bool:
        """
        Check if KPIs meet criteria for progression to next phase.

        Criteria:
        - Average pain <= 4/10
        - Compliance >= 80%
        - Pain-free time >= 18 hours/day
        - Functional capacity improving
        """
        criteria_met = {
            "pain_reduction": self.avg_pain_level <= 4,
            "consistency": self.compliance_rate >= 80,
            "pain_free_time": self.pain_free_time_hours >= 18,
        }

        # All core criteria must be met
        return all(criteria_met.values())

    def get_focus_areas(self) -> list:
        """Get areas that need improvement."""
        focus_areas = []

        if self.avg_pain_level > 4:
            focus_areas.append("Riduzione dolore")
        if self.compliance_rate < 80:
            focus_areas.append("Consistenza allenamenti")
        if self.pain_free_time_hours < 18:
            focus_areas.append("Gestione dolore quotidiano")

        return focus_areas

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "week": self.week,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "avg_pain_level": self.avg_pain_level,
            "max_pain_level": self.max_pain_level,
            "min_pain_level": self.min_pain_level,
            "pain_free_time_hours": self.pain_free_time_hours,
            "rom_hip_flexion": self.rom_hip_flexion,
            "rom_lumbar_flexion": self.rom_lumbar_flexion,
            "max_deadlift_kg": self.max_deadlift_kg,
            "max_squat_kg": self.max_squat_kg,
            "planned_sessions": self.planned_sessions,
            "completed_sessions": self.completed_sessions,
            "compliance_rate": self.compliance_rate,
            "meets_criteria": self.meets_progression_criteria(),
            "focus_areas": self.get_focus_areas()
        }
