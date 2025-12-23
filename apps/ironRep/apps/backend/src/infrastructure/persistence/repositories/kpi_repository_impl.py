"""
KPI Repository Implementation
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities.progress_kpi import ProgressKPI
from src.domain.repositories.kpi_repository import IKPIRepository
from src.infrastructure.persistence.models import ProgressKPIModel


class KPIRepositoryImpl(IKPIRepository):
    """SQLAlchemy implementation of KPI repository."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, kpi: ProgressKPI) -> ProgressKPI:
        """Save a KPI record."""
        model = ProgressKPIModel(
            id=kpi.id,
            user_id=kpi.user_id,
            week=kpi.week,
            start_date=kpi.start_date,
            end_date=kpi.end_date,
            avg_pain_level=kpi.avg_pain_level,
            max_pain_level=kpi.max_pain_level,
            min_pain_level=kpi.min_pain_level,
            pain_free_time_hours=kpi.pain_free_time_hours,
            rom_hip_flexion=kpi.rom_hip_flexion,
            rom_lumbar_flexion=kpi.rom_lumbar_flexion,
            max_deadlift_kg=kpi.max_deadlift_kg,
            max_squat_kg=kpi.max_squat_kg,
            planned_sessions=kpi.planned_sessions,
            completed_sessions=kpi.completed_sessions,
            compliance_rate=kpi.compliance_rate
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._model_to_entity(model)

    def get_by_id(self, kpi_id: str) -> Optional[ProgressKPI]:
        """Get KPI by ID."""
        model = self.db.query(ProgressKPIModel).filter(
            ProgressKPIModel.id == kpi_id
        ).first()

        return self._model_to_entity(model) if model else None

    def get_by_week(self, user_id: str, week: int) -> Optional[ProgressKPI]:
        """Get KPI for specific week."""
        model = self.db.query(ProgressKPIModel).filter(
            ProgressKPIModel.user_id == user_id,
            ProgressKPIModel.week == week
        ).first()

        return self._model_to_entity(model) if model else None

    def get_all_for_user(self, user_id: str) -> List[ProgressKPI]:
        """Get all KPI records for a user."""
        models = self.db.query(ProgressKPIModel).filter(
            ProgressKPIModel.user_id == user_id
        ).order_by(ProgressKPIModel.week.asc()).all()

        return [self._model_to_entity(m) for m in models]

    def get_last_n_weeks(self, user_id: str, n: int) -> List[ProgressKPI]:
        """Get KPIs for last N weeks."""
        models = self.db.query(ProgressKPIModel).filter(
            ProgressKPIModel.user_id == user_id
        ).order_by(ProgressKPIModel.week.desc()).limit(n).all()

        # Reverse to get chronological order
        models.reverse()

        return [self._model_to_entity(m) for m in models]

    def update(self, kpi: ProgressKPI) -> ProgressKPI:
        """Update an existing KPI record."""
        model = self.db.query(ProgressKPIModel).filter(
            ProgressKPIModel.id == kpi.id
        ).first()

        if not model:
            raise ValueError(f"KPI {kpi.id} not found")

        # Update fields
        model.end_date = kpi.end_date
        model.avg_pain_level = kpi.avg_pain_level
        model.max_pain_level = kpi.max_pain_level
        model.min_pain_level = kpi.min_pain_level
        model.pain_free_time_hours = kpi.pain_free_time_hours
        model.rom_hip_flexion = kpi.rom_hip_flexion
        model.rom_lumbar_flexion = kpi.rom_lumbar_flexion
        model.max_deadlift_kg = kpi.max_deadlift_kg
        model.max_squat_kg = kpi.max_squat_kg
        model.completed_sessions = kpi.completed_sessions
        model.compliance_rate = kpi.compliance_rate

        self.db.commit()
        self.db.refresh(model)

        return self._model_to_entity(model)

    def delete(self, kpi_id: str) -> bool:
        """Delete a KPI record."""
        result = self.db.query(ProgressKPIModel).filter(
            ProgressKPIModel.id == kpi_id
        ).delete()

        self.db.commit()
        return result > 0

    def _model_to_entity(self, model: ProgressKPIModel) -> ProgressKPI:
        """Convert ORM model to domain entity."""
        kpi = ProgressKPI(
            id=model.id,
            user_id=model.user_id,
            week=model.week,
            start_date=model.start_date,
            end_date=model.end_date,
            avg_pain_level=model.avg_pain_level,
            max_pain_level=model.max_pain_level,
            min_pain_level=model.min_pain_level,
            pain_free_time_hours=model.pain_free_time_hours,
            rom_hip_flexion=model.rom_hip_flexion,
            rom_lumbar_flexion=model.rom_lumbar_flexion,
            max_deadlift_kg=model.max_deadlift_kg,
            max_squat_kg=model.max_squat_kg,
            planned_sessions=model.planned_sessions,
            completed_sessions=model.completed_sessions,
            compliance_rate=model.compliance_rate
        )

        return kpi
