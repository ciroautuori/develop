"""
User Profile Entity

Represents the user's profile and injury history.
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid


class ActivityLevel(Enum):
    """User's physical activity level."""
    SEDENTARY = "sedentario"
    LIGHTLY_ACTIVE = "leggermente_attivo"
    MODERATELY_ACTIVE = "moderatamente_attivo"
    VERY_ACTIVE = "molto_attivo"
    ATHLETE = "atleta"


@dataclass
class UserProfile:
    """
    Entity representing user profile.

    For MVP: single user system, but designed for multi-user expansion.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Utente"
    age: Optional[int] = None
    activity_level: ActivityLevel = ActivityLevel.ATHLETE

    # Injury details
    injury_date: Optional[datetime] = None
    injury_description: str = ""
    diagnosis: str = ""

    # Pre-injury baseline
    baseline_deadlift_kg: Optional[float] = None
    baseline_squat_kg: Optional[float] = None

    # Current program
    current_week: int = 1
    current_phase: str = "Fase 1: Decompressione"
    program_start_date: datetime = field(default_factory=datetime.now)

    # Goals
    target_return_date: Optional[datetime] = None
    goals: str = "Ritorno al CrossFit intermedio senza dolore"

    def get_weeks_in_program(self) -> int:
        """Calculate weeks since program start."""
        delta = datetime.now() - self.program_start_date
        return delta.days // 7

    def get_current_capacity_percentage(self, current_dl_kg: float) -> float:
        """Calculate current strength as % of baseline."""
        if self.baseline_deadlift_kg and self.baseline_deadlift_kg > 0:
            return (current_dl_kg / self.baseline_deadlift_kg) * 100
        return 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "activity_level": self.activity_level.value,
            "injury_date": self.injury_date.isoformat() if self.injury_date else None,
            "injury_description": self.injury_description,
            "diagnosis": self.diagnosis,
            "baseline_deadlift_kg": self.baseline_deadlift_kg,
            "baseline_squat_kg": self.baseline_squat_kg,
            "current_week": self.current_week,
            "current_phase": self.current_phase,
            "program_start_date": self.program_start_date.isoformat(),
            "target_return_date": self.target_return_date.isoformat() if self.target_return_date else None,
            "goals": self.goals,
            "weeks_in_program": self.get_weeks_in_program()
        }
