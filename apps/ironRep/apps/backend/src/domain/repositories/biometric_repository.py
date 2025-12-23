"""
Biometric Repository Interface

Defines contract for biometric data persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from src.domain.entities.biometric import BiometricEntry, BiometricType


class IBiometricRepository(ABC):
    """
    Repository interface for BiometricEntry aggregate.

    Follows Repository pattern from DDD.
    """

    @abstractmethod
    def save(self, entry: BiometricEntry) -> BiometricEntry:
        """
        Save biometric entry.

        Args:
            entry: BiometricEntry to save

        Returns:
            Saved entry
        """
        pass

    @abstractmethod
    def get_by_id(self, entry_id: str) -> Optional[BiometricEntry]:
        """
        Get biometric entry by ID.

        Args:
            entry_id: Entry ID

        Returns:
            BiometricEntry if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_user_and_type(
        self,
        user_id: str,
        biometric_type: BiometricType,
        limit: int = 100
    ) -> List[BiometricEntry]:
        """
        Get biometric entries by user and type.

        Args:
            user_id: User ID
            biometric_type: Type of biometric
            limit: Maximum number of entries to return

        Returns:
            List of biometric entries, ordered by date DESC
        """
        pass

    @abstractmethod
    def get_by_user_and_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        biometric_type: Optional[BiometricType] = None
    ) -> List[BiometricEntry]:
        """
        Get biometric entries by user and date range.

        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            biometric_type: Optional filter by type

        Returns:
            List of biometric entries
        """
        pass

    @abstractmethod
    def get_latest_by_exercise(
        self,
        user_id: str,
        exercise_id: str
    ) -> Optional[BiometricEntry]:
        """
        Get latest strength test for specific exercise.

        Args:
            user_id: User ID
            exercise_id: Exercise ID

        Returns:
            Latest BiometricEntry for that exercise, or None
        """
        pass

    @abstractmethod
    def get_strength_progression(
        self,
        user_id: str,
        exercise_id: str,
        limit: int = 20
    ) -> List[BiometricEntry]:
        """
        Get strength progression history for an exercise.

        Args:
            user_id: User ID
            exercise_id: Exercise ID
            limit: Maximum number of entries

        Returns:
            List of strength tests, ordered by date ASC
        """
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """
        Delete biometric entry.

        Args:
            entry_id: Entry ID to delete

        Returns:
            True if deleted, False otherwise
        """
        pass
