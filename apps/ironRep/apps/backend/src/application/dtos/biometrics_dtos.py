from pydantic import BaseModel, Field
from typing import Optional


class BiometricEntryDTO(BaseModel):
    """DTO for biometric entry data."""
    id: str
    user_id: str
    date: str
    type: str  # STRENGTH, ROM, BODY_COMP, CARDIOVASCULAR

    # Strength metrics
    exercise_id: Optional[str] = None
    exercise_name: Optional[str] = None
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    estimated_1rm: Optional[float] = None

    # ROM metrics
    rom_test: Optional[str] = None
    rom_degrees: Optional[float] = None
    rom_side: Optional[str] = None

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
    created_at: str


class RecordBiometricRequestDTO(BaseModel):
    """DTO for recording biometric measurement."""
    date: Optional[str] = None  # ISO format, defaults to now
    type: str = Field(..., pattern="^(STRENGTH|ROM|BODY_COMP|CARDIOVASCULAR)$")

    # Strength metrics
    exercise_id: Optional[str] = None
    exercise_name: Optional[str] = None
    weight_kg: Optional[float] = Field(None, ge=0)
    reps: Optional[int] = Field(None, ge=1, le=100)
    estimated_1rm: Optional[float] = Field(None, ge=0)

    # ROM metrics
    rom_test: Optional[str] = None
    rom_degrees: Optional[float] = Field(None, ge=0, le=360)
    rom_side: Optional[str] = Field(None, pattern="^(left|right|bilateral)$")

    # Body composition
    weight: Optional[float] = Field(None, ge=30, le=300)
    body_fat_percent: Optional[float] = Field(None, ge=0, le=100)
    muscle_mass_kg: Optional[float] = Field(None, ge=0)

    # Cardiovascular
    resting_hr: Optional[int] = Field(None, ge=30, le=200)
    hrv: Optional[int] = Field(None, ge=0, le=300)
    vo2max_estimate: Optional[float] = Field(None, ge=0, le=100)

    # Metadata
    notes: Optional[str] = Field(None, max_length=1000)
