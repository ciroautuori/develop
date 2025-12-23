"""
KPI Repository Interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.progress_kpi import ProgressKPI


class IKPIRepository(ABC):
    """Interface for progress KPI persistence."""

    @abstractmethod
    def save(self, kpi: ProgressKPI) -> ProgressKPI:
        """Save a KPI record."""
        pass

    @abstractmethod
    def get_by_id(self, kpi_id: str) -> Optional[ProgressKPI]:
        """Get KPI by ID."""
        pass

    @abstractmethod
    def get_by_week(self, user_id: str, week: int) -> Optional[ProgressKPI]:
        """Get KPI for specific week."""
        pass

    @abstractmethod
    def get_all_for_user(self, user_id: str) -> List[ProgressKPI]:
        """Get all KPI records for a user."""
        pass

    @abstractmethod
    def get_last_n_weeks(self, user_id: str, n: int) -> List[ProgressKPI]:
        """Get KPIs for last N weeks."""
        pass

    @abstractmethod
    def update(self, kpi: ProgressKPI) -> ProgressKPI:
        """Update an existing KPI record."""
        pass

    @abstractmethod
    def delete(self, kpi_id: str) -> bool:
        """Delete a KPI record."""
        pass
