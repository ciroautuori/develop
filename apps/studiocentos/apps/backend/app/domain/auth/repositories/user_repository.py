"""User Repository - Data Access Layer for User Domain.

Provides database operations for User entities following Repository pattern.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.domain.auth.models import User
from app.infrastructure.database.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity database operations.
    
    Extends BaseRepository with User-specific queries.
    """
    
    def __init__(self, db: Session):
        """Initialize UserRepository.
        
        Args:
            db: Database session
        """
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists, False otherwise
        """
        return self.db.query(User.id).filter(User.email == email).scalar() is not None
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if username exists, False otherwise
        """
        return self.db.query(User.id).filter(User.username == username).scalar() is not None
    
    def get_active_users(self, limit: Optional[int] = None) -> list[User]:
        """Get all active users.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of active users
        """
        query = self.db.query(User).filter(User.is_active == True)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_role(self, role: str, limit: Optional[int] = None) -> list[User]:
        """Get users by role.
        
        Args:
            role: User role
            limit: Maximum number of results
            
        Returns:
            List of users with specified role
        """
        query = self.db.query(User).filter(User.role == role)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()


__all__ = ["UserRepository"]
