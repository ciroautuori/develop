"""
Chat History Repository Interface

Domain repository for chat history persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime


class IChatRepository(ABC):
    """Interface for chat history repository."""

    @abstractmethod
    def save_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        metadata: dict = None
    ) -> dict:
        """
        Save a chat message.

        Args:
            user_id: User ID
            session_id: Session ID for grouping conversations
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (tools used, context, etc.)

        Returns:
            dict with saved message data
        """
        pass

    @abstractmethod
    def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[dict]:
        """
        Get chat history for a session.

        Args:
            session_id: Session ID
            limit: Max messages to retrieve

        Returns:
            List of messages ordered by timestamp
        """
        pass

    @abstractmethod
    def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[str]:
        """
        Get recent session IDs for a user.

        Args:
            user_id: User ID
            limit: Max sessions to retrieve

        Returns:
            List of session IDs ordered by most recent
        """
        pass

    @abstractmethod
    def get_user_history(
        self,
        user_id: str,
        days: int = 7,
        limit: int = 100
    ) -> List[dict]:
        """
        Get user's chat history for last N days.

        Args:
            user_id: User ID
            days: Number of days to look back
            limit: Max messages to retrieve

        Returns:
            List of messages ordered by timestamp desc
        """
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """
        Delete all messages in a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False otherwise
        """
        pass

    @abstractmethod
    def create_new_session(self, user_id: str, session_type: str = "chat") -> str:
        """
        Create a new session ID for user.

        Args:
            user_id: User ID
            session_type: Type of session ("chat" or "checkin")

        Returns:
            New session ID (UUID)
        """
        pass
