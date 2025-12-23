"""
Workout Session Entity

Represents a training session with exercises and metadata.
"""
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid


class WorkoutPhase(Enum):
    """Rehabilitation phases."""
    PHASE_1_DECOMPRESSION = "Fase 1: Decompressione"
    PHASE_2_STABILIZATION = "Fase 2: Stabilizzazione"
    PHASE_3_STRENGTHENING = "Fase 3: Strengthening"
    PHASE_4_RETURN_TO_SPORT = "Fase 4: Return to Sport"


class PainImpact(Enum):
    """Expected pain impact levels."""
    VERY_LOW = "molto_basso"
    LOW = "basso"
    MEDIUM_LOW = "medio_basso"
    MEDIUM = "medio"
    MEDIUM_HIGH = "medio_alto"
    HIGH = "alto"


@dataclass
class Exercise:
    """Individual exercise within a workout."""
    name: str
    sets: int
    reps: str  # Can be "10" or "AMRAP" or "30sec"
    rest_seconds: int = 60
    notes: str = ""
    coaching_cues: List[str] = field(default_factory=list)
    video_url: Optional[str] = None
    completed: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "sets": self.sets,
            "reps": self.reps,
            "rest_seconds": self.rest_seconds,
            "notes": self.notes,
            "coaching_cues": self.coaching_cues,
            "video_url": self.video_url,
            "completed": self.completed
        }


@dataclass
class WorkoutSession:
    """
    Entity representing a complete workout session.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_id: str = "default_user"
    date: datetime = field(default_factory=datetime.now)
    phase: WorkoutPhase = WorkoutPhase.PHASE_1_DECOMPRESSION
    warm_up: List[Exercise] = field(default_factory=list)
    technical_work: List[Exercise] = field(default_factory=list)
    conditioning: List[Exercise] = field(default_factory=list)
    cool_down: List[Exercise] = field(default_factory=list)
    estimated_pain_impact: PainImpact = PainImpact.LOW
    contraindications: List[str] = field(default_factory=list)
    completed: bool = False
    actual_pain_impact: Optional[int] = None
    feedback: Optional[str] = None

    def get_total_exercises(self) -> int:
        """Get total number of exercises."""
        return (len(self.warm_up) + len(self.technical_work) +
                len(self.conditioning) + len(self.cool_down))

    def mark_completed(self, pain_impact: int, feedback: str = ""):
        """Mark workout as completed."""
        self.completed = True
        self.actual_pain_impact = pain_impact
        self.feedback = feedback

    def toggle_exercise_completion(self, exercise_name: str) -> bool:
        """Toggle completion status of an exercise by name."""
        for section in [self.warm_up, self.technical_work, self.conditioning, self.cool_down]:
            for exercise in section:
                if exercise.name == exercise_name:
                    exercise.completed = not exercise.completed
                    return True
        return False

    def is_gentle_session(self) -> bool:
        """Check if this is a gentle/mobility-only session."""
        return (self.phase == WorkoutPhase.PHASE_1_DECOMPRESSION and
                self.estimated_pain_impact in [PainImpact.VERY_LOW, PainImpact.LOW])

    def get_estimated_duration(self) -> int:
        """Estimate workout duration in minutes."""
        total_minutes = 0

        for section in [self.warm_up, self.technical_work, self.conditioning, self.cool_down]:
            for exercise in section:
                # Heuristic: 2 mins per set (working time + rest)
                # If reps is "AMRAP" or high, maybe longer, but 2-3 mins is standard
                sets = exercise.sets if exercise.sets > 0 else 1
                # Add rest time specifically
                work_time = 45  # seconds avg
                set_duration = work_time + exercise.rest_seconds
                total_minutes += (sets * set_duration) / 60

        return int(total_minutes)

    def get_completed_exercises_count(self) -> int:
        """Get number of completed exercises."""
        count = 0
        for section in [self.warm_up, self.technical_work, self.conditioning, self.cool_down]:
            for exercise in section:
                if exercise.completed:
                    count += 1
        return count

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "phase": self.phase.value,
            "warm_up": [ex.to_dict() for ex in self.warm_up],
            "technical_work": [ex.to_dict() for ex in self.technical_work],
            "cool_down": [ex.to_dict() for ex in self.cool_down],
            "conditioning": [ex.to_dict() for ex in self.conditioning],
            "estimated_pain_impact": self.estimated_pain_impact.value,
            "contraindications": self.contraindications,
            "completed": self.completed,
            "actual_pain_impact": self.actual_pain_impact,
            "pain_impact": self.actual_pain_impact, # Alias for frontend
            "feedback": self.feedback,
            "total_exercises": self.get_total_exercises(),
            "completed_exercises": self.get_completed_exercises_count(),
            "estimated_duration_minutes": self.get_estimated_duration()
        }
