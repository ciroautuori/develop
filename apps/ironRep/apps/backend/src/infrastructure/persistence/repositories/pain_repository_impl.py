"""
Pain Repository Implementation

Concrete implementation of IPainRepository using SQLAlchemy.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.domain.entities.pain_assessment import PainAssessment
from src.domain.repositories.pain_repository import IPainRepository
from src.infrastructure.persistence.models import PainAssessmentModel


class PainRepositoryImpl(IPainRepository):
    """SQLAlchemy implementation of pain repository."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, assessment: PainAssessment) -> PainAssessment:
        """Save a pain assessment to database."""
        # Convert entity to ORM model
        model = PainAssessmentModel(
            id=assessment.id,
            user_id=assessment.user_id,
            date=assessment.date,
            pain_level=assessment.pain_level,
            pain_locations=assessment.pain_locations,
            triggers=assessment.triggers,
            medication_taken=assessment.medication_taken,
            notes=assessment.notes
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._model_to_entity(model)

    def get_by_id(self, assessment_id: str) -> Optional[PainAssessment]:
        """Get assessment by ID."""
        model = self.db.query(PainAssessmentModel).filter(
            PainAssessmentModel.id == assessment_id
        ).first()

        return self._model_to_entity(model) if model else None

    def get_last_n_days(self, user_id: str, days: int) -> List[PainAssessment]:
        """Get pain assessments for last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        models = self.db.query(PainAssessmentModel).filter(
            PainAssessmentModel.user_id == user_id,
            PainAssessmentModel.date >= cutoff_date
        ).order_by(PainAssessmentModel.date.asc()).all()

        return [self._model_to_entity(m) for m in models]

    def get_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[PainAssessment]:
        """Get assessments in date range."""
        models = self.db.query(PainAssessmentModel).filter(
            PainAssessmentModel.user_id == user_id,
            PainAssessmentModel.date >= start_date,
            PainAssessmentModel.date <= end_date
        ).order_by(PainAssessmentModel.date.asc()).all()

        return [self._model_to_entity(m) for m in models]

    def get_all_for_user(self, user_id: str) -> List[PainAssessment]:
        """Get all assessments for a user."""
        models = self.db.query(PainAssessmentModel).filter(
            PainAssessmentModel.user_id == user_id
        ).order_by(PainAssessmentModel.date.asc()).all()

        return [self._model_to_entity(m) for m in models]

    def delete(self, assessment_id: str) -> bool:
        """Delete an assessment."""
        result = self.db.query(PainAssessmentModel).filter(
            PainAssessmentModel.id == assessment_id
        ).delete()

        self.db.commit()
        return result > 0

    def _model_to_entity(self, model: PainAssessmentModel) -> PainAssessment:
        """Convert ORM model to domain entity."""
        return PainAssessment(
            id=model.id,
            user_id=model.user_id,
            date=model.date,
            pain_level=model.pain_level,
            pain_locations=model.pain_locations,
            triggers=model.triggers if model.triggers else [],
            medication_taken=model.medication_taken,
            notes=model.notes
        )
