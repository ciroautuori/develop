"""
Chat History Repository Implementation

SQLAlchemy implementation of chat history repository.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from src.domain.repositories.chat_repository import IChatRepository
from src.infrastructure.persistence.models import ChatHistoryModel


class ChatRepositoryImpl(IChatRepository):
    """SQLAlchemy implementation of chat repository."""

    def __init__(self, db: Session):
        self.db = db

    def save_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        metadata: dict = None
    ) -> dict:
        """Save a chat message to database."""
        message = ChatHistoryModel(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            message_metadata=metadata,
            timestamp=datetime.now(),
            created_at=datetime.now()
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return self._model_to_dict(message)

    def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[dict]:
        """Get chat history for a session."""
        messages = (
            self.db.query(ChatHistoryModel)
            .filter(ChatHistoryModel.session_id == session_id)
            .order_by(ChatHistoryModel.timestamp.asc())
            .limit(limit)
            .all()
        )

        return [self._model_to_dict(msg) for msg in messages]

    def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[str]:
        """Get recent session IDs for a user."""
        # Get distinct session IDs ordered by most recent message
        sessions = (
            self.db.query(ChatHistoryModel.session_id)
            .filter(ChatHistoryModel.user_id == user_id)
            .distinct()
            .order_by(desc(ChatHistoryModel.timestamp))
            .limit(limit)
            .all()
        )

        return [session[0] for session in sessions]

    def get_user_history(
        self,
        user_id: str,
        days: int = 7,
        limit: int = 100
    ) -> List[dict]:
        """Get user's chat history for last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        messages = (
            self.db.query(ChatHistoryModel)
            .filter(
                ChatHistoryModel.user_id == user_id,
                ChatHistoryModel.timestamp >= cutoff_date
            )
            .order_by(desc(ChatHistoryModel.timestamp))
            .limit(limit)
            .all()
        )

        return [self._model_to_dict(msg) for msg in messages]

    def delete_session(self, session_id: str) -> bool:
        """Delete all messages in a session."""
        try:
            deleted = (
                self.db.query(ChatHistoryModel)
                .filter(ChatHistoryModel.session_id == session_id)
                .delete()
            )
            self.db.commit()
            return deleted > 0
        except Exception:
            self.db.rollback()
            return False

    def create_new_session(self, user_id: str, session_type: str = "chat") -> str:
        """
        Create a new session ID for user.

        Args:
            user_id: User identifier
            session_type: Type of session ('chat', 'checkin', 'wizard')

        Returns:
            New session ID
        """
        session_id = str(uuid.uuid4())

        # Store session metadata as first message
        self.save_message(
            user_id=user_id,
            session_id=session_id,
            role="system",
            content=f"Session started: {session_type}",
            metadata={
                "session_type": session_type,
                "created_at": datetime.now().isoformat()
            }
        )

        return session_id

    def get_sessions_by_type(self, user_id: str, session_type: str, limit: int = 10) -> List[str]:
        """
        Get sessions filtered by type.

        Args:
            user_id: User identifier
            session_type: Type to filter ('chat', 'checkin', 'wizard')
            limit: Max sessions to return

        Returns:
            List of session IDs
        """
        # Find sessions where first message has matching session_type in metadata
        from sqlalchemy import func

        subquery = (
            self.db.query(
                ChatHistoryModel.session_id,
                func.min(ChatHistoryModel.id).label('first_id')
            )
            .filter(ChatHistoryModel.user_id == user_id)
            .group_by(ChatHistoryModel.session_id)
            .subquery()
        )

        sessions = (
            self.db.query(ChatHistoryModel.session_id)
            .join(subquery, ChatHistoryModel.id == subquery.c.first_id)
            .filter(
                ChatHistoryModel.message_metadata['session_type'].astext == session_type
            )
            .order_by(ChatHistoryModel.timestamp.desc())
            .limit(limit)
            .all()
        )

        return [s[0] for s in sessions]

    def _model_to_dict(self, model: ChatHistoryModel) -> dict:
        """Convert ORM model to dict."""
        return {
            "id": model.id,
            "user_id": model.user_id,
            "session_id": model.session_id,
            "role": model.role,
            "content": model.content,
            "metadata": model.message_metadata,
            "timestamp": model.timestamp,
            "created_at": model.created_at
        }
