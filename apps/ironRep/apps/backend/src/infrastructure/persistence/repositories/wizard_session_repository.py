"""
Wizard Session Repository

Persists wizard interview sessions to database for production reliability.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import json

from src.infrastructure.persistence.models import WizardSessionModel


class WizardSessionRepository:
    """Repository for wizard session persistence."""

    def __init__(self, db: Session):
        self.db = db

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.

        Returns dict compatible with WizardAgent._sessions format.
        """
        model = self.db.query(WizardSessionModel).filter(
            WizardSessionModel.id == session_id
        ).first()

        if not model:
            return None

        return {
            "phase": model.phase,
            "collected_data": model.collected_data or {},
            "conversation_history": model.conversation_history or [],
            "user_id": model.user_id,
            "email": model.email,
            "started_at": model.started_at.isoformat() if model.started_at else None,
            "agent_config": model.agent_config or {
                "medical_mode": "wellness_tips",
                "coach_mode": "general_fitness",
                "nutrition_mode": "tips_tracking",
                "has_injury": False,
                "sport_type": None
            }
        }

    def create_session(self, session_id: str, user_id: str = None, email: str = None) -> Dict[str, Any]:
        """Create new wizard session."""
        model = WizardSessionModel(
            id=session_id,
            user_id=user_id,
            email=email,
            phase="greeting",
            collected_data={},
            agent_config={
                "medical_mode": "wellness_tips",
                "coach_mode": "general_fitness",
                "nutrition_mode": "tips_tracking",
                "has_injury": False,
                "sport_type": None
            },
            conversation_history=[],
            started_at=datetime.now()
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self.get_session(session_id)

    def update_session(
        self,
        session_id: str,
        phase: str = None,
        collected_data: Dict = None,
        agent_config: Dict = None,
        conversation_history: list = None,
        user_id: str = None,
        email: str = None
    ) -> Optional[Dict[str, Any]]:
        """Update existing session."""
        model = self.db.query(WizardSessionModel).filter(
            WizardSessionModel.id == session_id
        ).first()

        if not model:
            return None

        if phase is not None:
            model.phase = phase
        if collected_data is not None:
            model.collected_data = collected_data
        if agent_config is not None:
            model.agent_config = agent_config
        if conversation_history is not None:
            model.conversation_history = conversation_history
        if user_id is not None:
            model.user_id = user_id
        if email is not None:
            model.email = email

        model.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(model)

        return self.get_session(session_id)

    def complete_session(self, session_id: str) -> bool:
        """Mark session as completed."""
        model = self.db.query(WizardSessionModel).filter(
            WizardSessionModel.id == session_id
        ).first()

        if not model:
            return False

        model.is_completed = True
        model.completed_at = datetime.now()
        model.phase = "complete"

        self.db.commit()
        return True

    def get_or_create_session(
        self,
        session_id: str,
        user_id: str = None,
        email: str = None
    ) -> Dict[str, Any]:
        """Get existing session or create new one."""
        existing = self.get_session(session_id)
        if existing:
            return existing
        return self.create_session(session_id, user_id, email)

    def get_active_session_for_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent incomplete session for a user."""
        model = self.db.query(WizardSessionModel).filter(
            WizardSessionModel.user_id == user_id,
            WizardSessionModel.is_completed == False
        ).order_by(WizardSessionModel.updated_at.desc()).first()

        if not model:
            return None

        return self.get_session(model.id)

    def cleanup_old_sessions(self, days: int = 7) -> int:
        """Delete incomplete sessions older than X days."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)

        deleted = self.db.query(WizardSessionModel).filter(
            WizardSessionModel.is_completed == False,
            WizardSessionModel.updated_at < cutoff
        ).delete()

        self.db.commit()
        return deleted
