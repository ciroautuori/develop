"""
Repository Interfaces (Domain Layer)

Repositories define contracts for data access without specifying implementation.
This maintains domain independence from infrastructure concerns.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from src.domain.entities.pain_assessment import PainAssessment


class IPainRepository(ABC):
    """Interface for pain assessment persistence."""

    @abstractmethod
    def save(self, assessment: PainAssessment) -> PainAssessment:
        """Save a pain assessment."""
        pass

    @abstractmethod
    def get_by_id(self, assessment_id: str) -> Optional[PainAssessment]:
        """Get assessment by ID."""
        pass

    @abstractmethod
    def get_last_n_days(self, user_id: str, days: int) -> List[PainAssessment]:
        """Get pain assessments for last N days."""
        pass

    @abstractmethod
    def get_by_date_range(self, user_id: str, start_date: datetime,
                         end_date: datetime) -> List[PainAssessment]:
        """Get assessments in date range."""
        pass

    @abstractmethod
    def get_all_for_user(self, user_id: str) -> List[PainAssessment]:
        """Get all assessments for a user."""
        pass

    @abstractmethod
    def delete(self, assessment_id: str) -> bool:
        """Delete an assessment."""
        pass
