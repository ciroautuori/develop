"""
Record Biometric Use Case

Handles recording biometric measurements (strength tests, ROM, body comp, cardio).
"""
from typing import Dict, Any
from datetime import datetime

from src.domain.entities.biometric import BiometricEntry, BiometricType
from src.domain.repositories.biometric_repository import IBiometricRepository
from src.domain.repositories.user_repository import IUserRepository


class RecordBiometricUseCase:
    """
    Use case for recording biometric measurements.

    Supports strength tests, ROM assessments, body composition, and cardiovascular metrics.
    """

    def __init__(
        self,
        biometric_repository: IBiometricRepository,
        user_repository: IUserRepository
    ):
        self.biometric_repository = biometric_repository
        self.user_repository = user_repository

    async def execute(self, user_id: str, biometric_data: Dict[str, Any]) -> BiometricEntry:
        """
        Execute biometric recording.

        Args:
            user_id: User ID
            biometric_data: Dictionary with biometric measurement data

        Returns:
            Created BiometricEntry
        """
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Create BiometricEntry entity
        entry = BiometricEntry(
            user_id=user_id,
            date=datetime.fromisoformat(biometric_data["date"]) if biometric_data.get("date") else datetime.now(),
            type=BiometricType(biometric_data["type"]),

            # Strength metrics
            exercise_id=biometric_data.get("exercise_id"),
            exercise_name=biometric_data.get("exercise_name"),
            weight_kg=biometric_data.get("weight_kg"),
            reps=biometric_data.get("reps"),
            estimated_1rm=biometric_data.get("estimated_1rm"),

            # ROM metrics
            rom_test=biometric_data.get("rom_test"),
            rom_degrees=biometric_data.get("rom_degrees"),
            rom_side=biometric_data.get("rom_side"),

            # Body composition
            weight=biometric_data.get("weight"),
            body_fat_percent=biometric_data.get("body_fat_percent"),
            muscle_mass_kg=biometric_data.get("muscle_mass_kg"),

            # Cardiovascular
            resting_hr=biometric_data.get("resting_hr"),
            hrv=biometric_data.get("hrv"),
            vo2max_estimate=biometric_data.get("vo2max_estimate"),

            # Metadata
            notes=biometric_data.get("notes")
        )

        # Auto-calculate 1RM if not provided
        if entry.type == BiometricType.STRENGTH and not entry.estimated_1rm:
            entry.estimated_1rm = entry.calculate_1rm_epley()

        # Save entry
        saved_entry = self.biometric_repository.save(entry)

        return saved_entry

    async def get_strength_progression(
        self,
        user_id: str,
        exercise_id: str
    ) -> Dict[str, Any]:
        """
        Get strength progression for an exercise.

        Args:
            user_id: User ID
            exercise_id: Exercise ID

        Returns:
            Dict with progression data and analysis
        """
        # Get progression history
        entries = self.biometric_repository.get_strength_progression(user_id, exercise_id, limit=20)

        if not entries:
            return {
                "exercise_id": exercise_id,
                "entries": [],
                "latest_1rm": None,
                "progression_percent": 0,
                "message": "Nessun dato disponibile"
            }

        # Calculate progression
        first_entry = entries[0]
        latest_entry = entries[-1]

        first_1rm = first_entry.estimated_1rm or first_entry.calculate_1rm_epley() or 0
        latest_1rm = latest_entry.estimated_1rm or latest_entry.calculate_1rm_epley() or 0

        progression_percent = 0
        if first_1rm > 0:
            progression_percent = ((latest_1rm - first_1rm) / first_1rm) * 100

        return {
            "exercise_id": exercise_id,
            "exercise_name": latest_entry.exercise_name,
            "entries": [e.to_dict() for e in entries],
            "first_1rm": round(first_1rm, 1),
            "latest_1rm": round(latest_1rm, 1),
            "progression_percent": round(progression_percent, 1),
            "total_tests": len(entries),
            "date_range": {
                "start": first_entry.date.isoformat(),
                "end": latest_entry.date.isoformat()
            }
        }

    async def get_rom_trends(
        self,
        user_id: str,
        rom_test: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get ROM trends over time.

        Args:
            user_id: User ID
            rom_test: ROM test name (e.g., "hip_flexion")
            days: Number of days to look back

        Returns:
            Dict with ROM trend data
        """
        from datetime import timedelta

        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        entries = self.biometric_repository.get_by_user_and_date_range(
            user_id,
            start_date,
            end_date,
            BiometricType.ROM
        )

        # Filter by specific ROM test
        filtered_entries = [e for e in entries if e.rom_test == rom_test]

        if not filtered_entries:
            return {
                "rom_test": rom_test,
                "entries": [],
                "improvement_degrees": 0,
                "message": "Nessun dato disponibile"
            }

        # Calculate improvement
        first_entry = filtered_entries[0]
        latest_entry = filtered_entries[-1]

        improvement = (latest_entry.rom_degrees or 0) - (first_entry.rom_degrees or 0)

        return {
            "rom_test": rom_test,
            "entries": [e.to_dict() for e in filtered_entries],
            "first_rom": first_entry.rom_degrees,
            "latest_rom": latest_entry.rom_degrees,
            "improvement_degrees": round(improvement, 1),
            "total_assessments": len(filtered_entries)
        }
