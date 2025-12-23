"""Auth Domain Dependency Injection
Provides FastAPI dependencies for auth repositories and services.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.domain.auth.repositories.user_repository import UserRepository
from app.domain.auth.services import AuthService
from app.infrastructure.database.session import get_db


def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    """Get UserRepository instance with database session.
    
    This dependency provides a repository instance for user data access.
    Use this in routers or other services that need user data.
    
    Args:
        db: Database session from FastAPI dependency
        
    Returns:
        UserRepository instance
        
    Example:
        @router.get("/users/{user_id}")
        def get_user(
            user_id: int,
            repository: Annotated[UserRepository, Depends(get_user_repository)]
        ):
            return repository.get_by_id(user_id)
    """
    return UserRepository(db)


def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    """Get AuthService instance with repository dependency.
    
    This dependency provides the auth service with all dependencies injected.
    Use this in routers that need authentication/authorization logic.
    
    Args:
        repository: UserRepository instance from dependency
        
    Returns:
        AuthService instance
        
    Example:
        @router.post("/register")
        def register(
            data: UserRegistration,
            service: Annotated[AuthService, Depends(get_auth_service)]
        ):
            return service.register_user(data.model_dump())
    """
    return AuthService(repository)
