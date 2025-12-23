from pydantic import BaseModel, Field
from typing import List, Optional

class WorkoutDTO(BaseModel):
    """DTO for workout data transfer."""
    session_id: str
    date: str  # ISO format
    phase: str
    warm_up: List[dict]
    technical_work: List[dict]
    conditioning: List[dict]
    cool_down: List[dict]
    estimated_pain_impact: str
    contraindications: List[str]
    total_exercises: int
    estimated_duration_minutes: int


class KPIDTO(BaseModel):
    """DTO for KPI data transfer."""
    week: int
    start_date: str
    end_date: Optional[str]
    avg_pain_level: float
    max_pain_level: int
    min_pain_level: int
    pain_free_time_hours: float
    compliance_rate: float
    completed_sessions: int
    planned_sessions: int
    meets_progression_criteria: bool
    focus_areas: List[str]


class WeeklyReviewResponseDTO(BaseModel):
    """Response DTO for weekly review."""
    week_number: int
    kpi: KPIDTO
    progression_decision: dict
    next_week_program: List[WorkoutDTO]
    chart_data: dict
