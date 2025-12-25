"""Permission Dependencies for Role-Based Access Control.

Provides dependency injection functions for authorization checks:
- require_admin: Require admin role
- require_role: Require specific role
- require_any_role: Require any of specified roles
"""

from typing import Annotated, List

from fastapi import Depends, HTTPException, status

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User, UserRole


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Require user to have admin role.
    
    Args:
        current_user: Authenticated user from get_current_user
        
    Returns:
        User object if admin
        
    Raises:
        HTTPException: 403 if user is not admin
        
    Example:
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            admin: Annotated[User, Depends(require_admin)]
        ):
            # Only admins can access this endpoint
            pass
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_role(required_role: UserRole):
    """Create dependency that requires specific role.
    
    Args:
        required_role: Role required to access endpoint
        
    Returns:
        Dependency function
        
    Example:
        @router.get("/premium-content")
        async def get_premium(
            user: Annotated[User, Depends(require_role(UserRole.PREMIUM))]
        ):
            pass
    """
    async def check_role(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_role.value} required"
            )
        return current_user
    
    return check_role


def require_any_role(allowed_roles: List[UserRole]):
    """Create dependency that requires any of specified roles.
    
    Args:
        allowed_roles: List of roles allowed to access endpoint
        
    Returns:
        Dependency function
        
    Example:
        @router.get("/content")
        async def get_content(
            user: Annotated[User, Depends(require_any_role([
                UserRole.PREMIUM,
                UserRole.ADMIN
            ]))]
        ):
            pass
    """
    async def check_any_role(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role not in allowed_roles:
            roles_str = ", ".join([r.value for r in allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {roles_str}"
            )
        return current_user
    
    return check_any_role


async def require_premium_or_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Require user to have premium or admin role.
    
    Common use case: premium features accessible to paying users and admins.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User object if premium or admin
        
    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    if current_user.role not in [UserRole.PREMIUM, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription or admin privileges required"
        )
    return current_user


async def require_active_subscription(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Require user to have active subscription (not trial).
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User object if has active subscription
        
    Raises:
        HTTPException: 403 if user is on trial or free tier
    """
    if current_user.role in [UserRole.TRIAL, UserRole.FREE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required. Please upgrade your plan."
        )
    return current_user


class PermissionChecker:
    """Static permission checker utility class.
    
    Provides methods to check user permissions without raising exceptions.
    Useful for conditional logic in route handlers.
    """
    
    @staticmethod
    def can_access_admin_panel(user: User) -> bool:
        """Check if user can access admin panel.
        
        Args:
            user: User to check
            
        Returns:
            True if user has admin access
        """
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def can_manage_users(user: User) -> bool:
        """Check if user can manage other users.
        
        Args:
            user: User to check
            
        Returns:
            True if user can manage users
        """
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def can_manage_billing(user: User) -> bool:
        """Check if user can manage billing.
        
        Args:
            user: User to check
            
        Returns:
            True if user can manage billing
        """
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def has_premium_access(user: User) -> bool:
        """Check if user has premium features access.
        
        Args:
            user: User to check
            
        Returns:
            True if user has premium or admin role
        """
        return user.role in [UserRole.PREMIUM, UserRole.ADMIN]
    
    @staticmethod
    def is_active_subscriber(user: User) -> bool:
        """Check if user has active subscription.
        
        Args:
            user: User to check
            
        Returns:
            True if user is not on trial or free tier
        """
        return user.role not in [UserRole.TRIAL, UserRole.FREE]


async def require_customer_or_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Require user to have customer or admin role.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User object if customer or admin
        
    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    if current_user.role not in [UserRole.CUSTOMER, UserRole.ADMIN, UserRole.PRO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer subscription or admin privileges required"
        )
    return current_user


__all__ = [
    "require_admin",
    "require_role",
    "require_any_role",
    "require_premium_or_admin",
    "require_active_subscription",
    "require_customer_or_admin",
    "PermissionChecker",
]
