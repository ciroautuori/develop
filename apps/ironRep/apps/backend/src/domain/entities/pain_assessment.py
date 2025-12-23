"""
Pain Assessment Entity

Represents a single pain evaluation at a specific point in time.
"""
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class PainAssessment:
    """
    Entity representing a pain assessment.

    Attributes:
        id: Unique identifier
        user_id: User who made the assessment
        date: When assessment was made
        pain_level: Pain intensity (0-10)
        pain_locations: List of body areas with pain
        triggers: Activities/movements triggering pain
        medication_taken: Whether medication was used
        notes: Additional observations
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"  # MVP: single user
    date: datetime = field(default_factory=datetime.now)
    pain_level: int = 0
    pain_locations: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    medication_taken: bool = False
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate pain assessment data."""
        if not 0 <= self.pain_level <= 10:
            raise ValueError("Pain level must be between 0 and 10")

        if not self.pain_locations:
            raise ValueError("At least one pain location must be specified")

    def is_severe(self) -> bool:
        """Check if pain is severe (>=7)."""
        return self.pain_level >= 7

    def is_moderate(self) -> bool:
        """Check if pain is moderate (4-6)."""
        return 4 <= self.pain_level < 7

    def is_mild(self) -> bool:
        """Check if pain is mild (1-3)."""
        return 1 <= self.pain_level < 4

    def is_pain_free(self) -> bool:
        """Check if no pain."""
        return self.pain_level == 0

    def has_trigger(self, trigger: str) -> bool:
        """Check if specific trigger is present."""
        return trigger in self.triggers

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "pain_level": self.pain_level,
            "pain_locations": self.pain_locations,
            "triggers": self.triggers,
            "medication_taken": self.medication_taken,
            "notes": self.notes
        }
