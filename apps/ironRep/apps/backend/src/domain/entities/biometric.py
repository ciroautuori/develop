"""
Biometric Entry Entity

Represents biometric measurements (strength, ROM, body composition, cardiovascular).
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid


class BiometricType(Enum):
    """Type of biometric measurement."""
    STRENGTH = "STRENGTH"
    ROM = "ROM"
    BODY_COMP = "BODY_COMP"
    CARDIOVASCULAR = "CARDIOVASCULAR"


class ROMTest(Enum):
    """Range of Motion test types."""
    HIP_FLEXION = "hip_flexion"
    HIP_EXTENSION = "hip_extension"
    SHOULDER_FLEXION = "shoulder_flexion"
    SHOULDER_ABDUCTION = "shoulder_abduction"
    ANKLE_DORSIFLEXION = "ankle_dorsiflexion"
    THORACIC_ROTATION = "thoracic_rotation"
    TOE_TOUCH = "toe_touch"
    OVERHEAD_SQUAT = "overhead_squat"


@dataclass
class BiometricEntry:
    """
    Entity representing a biometric measurement.

    Can track strength tests, ROM assessments, body composition, or cardiovascular metrics.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    date: datetime = field(default_factory=datetime.now)
    type: BiometricType = BiometricType.STRENGTH

    # Strength metrics
    exercise_id: Optional[str] = None
    exercise_name: Optional[str] = None
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    estimated_1rm: Optional[float] = None

    # ROM metrics
    rom_test: Optional[str] = None
    rom_degrees: Optional[float] = None
    rom_side: Optional[str] = None  # left, right, bilateral

    # Body composition
    weight: Optional[float] = None
    body_fat_percent: Optional[float] = None
    muscle_mass_kg: Optional[float] = None

    # Cardiovascular
    resting_hr: Optional[int] = None
    hrv: Optional[int] = None
    vo2max_estimate: Optional[float] = None

    # Metadata
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def calculate_1rm_epley(self) -> Optional[float]:
        """
        Calculate estimated 1RM using Epley formula.

        1RM = weight * (1 + reps/30)
        """
        if self.weight_kg and self.reps:
            return self.weight_kg * (1 + self.reps / 30)
        return None

    def calculate_1rm_brzycki(self) -> Optional[float]:
        """
        Calculate estimated 1RM using Brzycki formula.

        1RM = weight * (36 / (37 - reps))
        """
        if self.weight_kg and self.reps and self.reps < 37:
            return self.weight_kg * (36 / (37 - self.reps))
        return None

    def is_strength_test(self) -> bool:
        """Check if this is a strength test entry."""
        return self.type == BiometricType.STRENGTH

    def is_rom_test(self) -> bool:
        """Check if this is a ROM test entry."""
        return self.type == BiometricType.ROM

    def is_body_comp(self) -> bool:
        """Check if this is a body composition entry."""
        return self.type == BiometricType.BODY_COMP

    def is_cardiovascular(self) -> bool:
        """Check if this is a cardiovascular entry."""
        return self.type == BiometricType.CARDIOVASCULAR

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "type": self.type.value,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise_name,
            "weight_kg": self.weight_kg,
            "reps": self.reps,
            "estimated_1rm": self.estimated_1rm or self.calculate_1rm_epley(),
            "rom_test": self.rom_test,
            "rom_degrees": self.rom_degrees,
            "rom_side": self.rom_side,
            "weight": self.weight,
            "body_fat_percent": self.body_fat_percent,
            "muscle_mass_kg": self.muscle_mass_kg,
            "resting_hr": self.resting_hr,
            "hrv": self.hrv,
            "vo2max_estimate": self.vo2max_estimate,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }
