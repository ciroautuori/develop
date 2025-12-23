"""
Workout Repository Implementation
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.entities.workout_session import WorkoutSession, WorkoutPhase, Exercise, PainImpact
from src.domain.repositories.workout_repository import IWorkoutRepository
from src.infrastructure.persistence.models import WorkoutSessionModel


class WorkoutRepositoryImpl(IWorkoutRepository):
    """SQLAlchemy implementation of workout repository."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, workout: WorkoutSession) -> WorkoutSession:
        """Save a workout session."""
        model = WorkoutSessionModel(
            id=workout.id,
            session_id=workout.session_id,
            user_id=workout.user_id,
            date=workout.date,
            phase=workout.phase.value,
            warm_up=[ex.to_dict() for ex in workout.warm_up],
            technical_work=[ex.to_dict() for ex in workout.technical_work],
            conditioning=[ex.to_dict() for ex in workout.conditioning],
            cool_down=[ex.to_dict() for ex in workout.cool_down],
            estimated_pain_impact=workout.estimated_pain_impact.value,
            contraindications=workout.contraindications,
            completed=workout.completed,
            actual_pain_impact=workout.actual_pain_impact,
            feedback=workout.feedback
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._model_to_entity(model)

    def get_by_id(self, workout_id: str) -> Optional[WorkoutSession]:
        """Get workout by ID."""
        model = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.id == workout_id
        ).first()

        return self._model_to_entity(model) if model else None

    def get_by_session_id(self, session_id: str) -> Optional[WorkoutSession]:
        """Get workout by session ID."""
        model = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.session_id == session_id
        ).first()

        return self._model_to_entity(model) if model else None

    def get_for_date(self, user_id: str, date: datetime) -> Optional[WorkoutSession]:
        """Get workout for specific date."""
        # Match on date only (ignoring time)
        model = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.user_id == user_id,
            WorkoutSessionModel.date >= date.replace(hour=0, minute=0, second=0),
            WorkoutSessionModel.date < date.replace(hour=23, minute=59, second=59)
        ).first()

        return self._model_to_entity(model) if model else None

    def get_completed_workouts(self, user_id: str) -> List[WorkoutSession]:
        """Get all completed workouts."""
        models = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.user_id == user_id,
            WorkoutSessionModel.completed == True
        ).order_by(WorkoutSessionModel.date.asc()).all()

        return [self._model_to_entity(m) for m in models]

    def get_by_week(self, user_id: str, week: int) -> List[WorkoutSession]:
        """Get workouts for specific week."""
        # This is simplified - would need proper week calculation
        models = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.user_id == user_id,
            WorkoutSessionModel.session_id.like(f"W{week}%")
        ).all()

        return [self._model_to_entity(m) for m in models]

    def get_last_n(self, user_id: str, n: int) -> List[WorkoutSession]:
        """Get last N workouts for user."""
        models = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.user_id == user_id
        ).order_by(WorkoutSessionModel.date.desc()).limit(n).all()

        return [self._model_to_entity(m) for m in models]


    def update(self, workout: WorkoutSession) -> WorkoutSession:
        """Update an existing workout."""
        model = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.id == workout.id
        ).first()

        if not model:
            raise ValueError(f"Workout {workout.id} not found")

        # Update fields
        model.completed = workout.completed
        model.actual_pain_impact = workout.actual_pain_impact
        model.feedback = workout.feedback

        self.db.commit()
        self.db.refresh(model)

        return self._model_to_entity(model)

    def delete(self, workout_id: str) -> bool:
        """Delete a workout."""
        result = self.db.query(WorkoutSessionModel).filter(
            WorkoutSessionModel.id == workout_id
        ).delete()

        self.db.commit()
        return result > 0

    def _model_to_entity(self, model: WorkoutSessionModel) -> WorkoutSession:
        """Convert ORM model to domain entity."""
        return WorkoutSession(
            id=model.id,
            session_id=model.session_id,
            user_id=model.user_id,
            date=model.date,
            phase=WorkoutPhase(model.phase),
            warm_up=self._dict_list_to_exercises(model.warm_up),
            technical_work=self._dict_list_to_exercises(model.technical_work),
            conditioning=self._dict_list_to_exercises(model.conditioning),
            cool_down=self._dict_list_to_exercises(model.cool_down),
            estimated_pain_impact=PainImpact(model.estimated_pain_impact),
            contraindications=model.contraindications if model.contraindications else [],
            completed=model.completed,
            actual_pain_impact=model.actual_pain_impact,
            feedback=model.feedback
        )

    def _dict_list_to_exercises(self, dict_list: List[dict]) -> List[Exercise]:
        """Convert list of dicts to Exercise objects."""
        if not dict_list:
            return []

        return [
            Exercise(
                name=ex.get("name", ""),
                sets=ex.get("sets", 2),
                reps=ex.get("reps", "10"),
                rest_seconds=ex.get("rest_seconds", 60),
                notes=ex.get("notes", ""),
                coaching_cues=ex.get("coaching_cues", []),
                video_url=ex.get("video_url"),
                completed=ex.get("completed", False)
            )
            for ex in dict_list
        ]
