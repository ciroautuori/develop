"""
User Repository Interface

Defines contract for user persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.user import User


class IUserRepository(ABC):
    """
    Repository interface for User aggregate.

    Follows Repository pattern from DDD.
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Save or update user.

        Args:
            user: User entity to save

        Returns:
            Saved user with updated timestamps
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all_active(self) -> List[User]:
        """
        Get all active users.

        Returns:
            List of active users
        """
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """
        Update existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user
        """
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """
        Soft delete user (set is_active=False).

        Args:
            user_id: User ID to delete

        Returns:
            True if deleted, False otherwise
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.

        Args:
            email: Email to check

        Returns:
            True if exists, False otherwise
        """
        pass
