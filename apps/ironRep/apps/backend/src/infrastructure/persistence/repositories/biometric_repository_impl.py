"""
Biometric Repository Implementation

SQLAlchemy implementation of IBiometricRepository.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from datetime import datetime

from src.domain.entities.biometric import BiometricEntry, BiometricType
from src.domain.repositories.biometric_repository import IBiometricRepository
from src.infrastructure.persistence.models import BiometricEntryModel


class BiometricRepositoryImpl(IBiometricRepository):
    """
    SQLAlchemy implementation of Biometric repository.

    Handles mapping between BiometricEntry domain entity and BiometricEntryModel ORM model.
    """

    def __init__(self, db: Session):
        self.db = db

    def save(self, entry: BiometricEntry) -> BiometricEntry:
        """Save biometric entry."""
        entry_model = self._entity_to_model(entry)
        self.db.add(entry_model)
        self.db.commit()
        self.db.refresh(entry_model)
        return self._model_to_entity(entry_model)

    def get_by_id(self, entry_id: str) -> Optional[BiometricEntry]:
        """Get biometric entry by ID."""
        entry_model = self.db.query(BiometricEntryModel).filter(
            BiometricEntryModel.id == entry_id
        ).first()

        if entry_model:
            return self._model_to_entity(entry_model)
        return None

    def get_by_user_and_type(
        self,
        user_id: str,
        biometric_type: BiometricType,
        limit: int = 100
    ) -> List[BiometricEntry]:
        """Get biometric entries by user and type."""
        entry_models = self.db.query(BiometricEntryModel).filter(
            and_(
                BiometricEntryModel.user_id == user_id,
                BiometricEntryModel.type == biometric_type.value
            )
        ).order_by(desc(BiometricEntryModel.date)).limit(limit).all()

        return [self._model_to_entity(model) for model in entry_models]

    def get_by_user_and_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        biometric_type: Optional[BiometricType] = None
    ) -> List[BiometricEntry]:
        """Get biometric entries by user and date range."""
        query = self.db.query(BiometricEntryModel).filter(
            and_(
                BiometricEntryModel.user_id == user_id,
                BiometricEntryModel.date >= start_date,
                BiometricEntryModel.date <= end_date
            )
        )

        if biometric_type:
            query = query.filter(BiometricEntryModel.type == biometric_type.value)

        entry_models = query.order_by(asc(BiometricEntryModel.date)).all()
        return [self._model_to_entity(model) for model in entry_models]

    def get_latest_by_exercise(
        self,
        user_id: str,
        exercise_id: str
    ) -> Optional[BiometricEntry]:
        """Get latest strength test for specific exercise."""
        entry_model = self.db.query(BiometricEntryModel).filter(
            and_(
                BiometricEntryModel.user_id == user_id,
                BiometricEntryModel.type == BiometricType.STRENGTH.value,
                BiometricEntryModel.exercise_id == exercise_id
            )
        ).order_by(desc(BiometricEntryModel.date)).first()

        if entry_model:
            return self._model_to_entity(entry_model)
        return None

    def get_strength_progression(
        self,
        user_id: str,
        exercise_id: str,
        limit: int = 20
    ) -> List[BiometricEntry]:
        """Get strength progression history for an exercise."""
        entry_models = self.db.query(BiometricEntryModel).filter(
            and_(
                BiometricEntryModel.user_id == user_id,
                BiometricEntryModel.type == BiometricType.STRENGTH.value,
                BiometricEntryModel.exercise_id == exercise_id
            )
        ).order_by(asc(BiometricEntryModel.date)).limit(limit).all()

        return [self._model_to_entity(model) for model in entry_models]

    def delete(self, entry_id: str) -> bool:
        """Delete biometric entry."""
        entry_model = self.db.query(BiometricEntryModel).filter(
            BiometricEntryModel.id == entry_id
        ).first()

        if not entry_model:
            return False

        self.db.delete(entry_model)
        self.db.commit()
        return True

    def _entity_to_model(self, entry: BiometricEntry) -> BiometricEntryModel:
        """Convert BiometricEntry entity to BiometricEntryModel ORM model."""
        return BiometricEntryModel(
            id=entry.id,
            user_id=entry.user_id,
            date=entry.date,
            type=entry.type.value,
            exercise_id=entry.exercise_id,
            exercise_name=entry.exercise_name,
            weight_kg=entry.weight_kg,
            reps=entry.reps,
            estimated_1rm=entry.estimated_1rm or entry.calculate_1rm_epley(),
            rom_test=entry.rom_test,
            rom_degrees=entry.rom_degrees,
            rom_side=entry.rom_side,
            weight=entry.weight,
            body_fat_percent=entry.body_fat_percent,
            muscle_mass_kg=entry.muscle_mass_kg,
            resting_hr=entry.resting_hr,
            hrv=entry.hrv,
            vo2max_estimate=entry.vo2max_estimate,
            notes=entry.notes,
            created_at=entry.created_at
        )

    def _model_to_entity(self, model: BiometricEntryModel) -> BiometricEntry:
        """Convert BiometricEntryModel ORM model to BiometricEntry entity."""
        return BiometricEntry(
            id=model.id,
            user_id=model.user_id,
            date=model.date,
            type=BiometricType(model.type),
            exercise_id=model.exercise_id,
            exercise_name=model.exercise_name,
            weight_kg=model.weight_kg,
            reps=model.reps,
            estimated_1rm=model.estimated_1rm,
            rom_test=model.rom_test,
            rom_degrees=model.rom_degrees,
            rom_side=model.rom_side,
            weight=model.weight,
            body_fat_percent=model.body_fat_percent,
            muscle_mass_kg=model.muscle_mass_kg,
            resting_hr=model.resting_hr,
            hrv=model.hrv,
            vo2max_estimate=model.vo2max_estimate,
            notes=model.notes,
            created_at=model.created_at
        )
