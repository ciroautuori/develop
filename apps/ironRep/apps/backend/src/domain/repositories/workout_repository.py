"""
Workout Repository Interface
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from src.domain.entities.workout_session import WorkoutSession


class IWorkoutRepository(ABC):
    """Interface for workout session persistence."""

    @abstractmethod
    def save(self, workout: WorkoutSession) -> WorkoutSession:
        """Save a workout session."""
        pass

    @abstractmethod
    def get_by_id(self, workout_id: str) -> Optional[WorkoutSession]:
        """Get workout by ID."""
        pass

    @abstractmethod
    def get_by_session_id(self, session_id: str) -> Optional[WorkoutSession]:
        """Get workout by human-readable session ID."""
        pass

    @abstractmethod
    def get_for_date(self, user_id: str, date: datetime) -> Optional[WorkoutSession]:
        """Get workout scheduled for a specific date."""
        pass

    @abstractmethod
    def get_completed_workouts(self, user_id: str) -> List[WorkoutSession]:
        """Get all completed workouts."""
        pass

    @abstractmethod
    def get_by_week(self, user_id: str, week: int) -> List[WorkoutSession]:
        """Get workouts for a specific week."""
        pass

    @abstractmethod
    def update(self, workout: WorkoutSession) -> WorkoutSession:
        """Update an existing workout."""
        pass

    @abstractmethod
    def delete(self, workout_id: str) -> bool:
        """Delete a workout."""
        pass
