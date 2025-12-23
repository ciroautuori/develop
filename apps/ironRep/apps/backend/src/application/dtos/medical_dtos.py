from pydantic import BaseModel, Field
from typing import List, Optional
from src.application.dtos.workout_dtos import WorkoutDTO

class PainAssessmentDTO(BaseModel):
    """DTO for pain assessment data transfer."""
    pain_level: int = Field(..., ge=0, le=10, description="Pain intensity 0-10")
    pain_locations: List[str] = Field(..., min_items=1, description="Body areas with pain")
    triggers: List[str] = Field(default_factory=list, description="Pain triggers")
    medication_taken: bool = Field(default=False, description="Medication used")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "pain_level": 6,
                "pain_locations": ["lombare", "gluteo_dx"],
                "triggers": ["seduto_prolungato", "flessione"],
                "medication_taken": False,
                "notes": "Dolore peggiorato dopo guida lunga"
            }
        }


class DailyCheckInResponseDTO(BaseModel):
    """Response DTO for daily check-in."""
    pain_assessment_saved: bool
    pain_analysis: dict
    red_flags: dict
    adapted_workout: WorkoutDTO
    recommendations: List[str]
