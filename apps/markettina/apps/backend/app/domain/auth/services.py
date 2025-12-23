"""Authentication Service - Business Logic Layer
Handles core authentication logic (login, registration, password management).

REFACTORED (MEDIUM-006):
- Extracted TokenService for JWT operations
- Extracted SessionService for Redis session management
- Now uses UserRepository for all data access
- Uses bcrypt directly instead of passlib (bcrypt 4.x compatibility fix)
"""

import logging
from datetime import UTC, datetime

import bcrypt
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

from app.domain.auth.models import User
from app.domain.auth.repositories.user_repository import UserRepository
from app.domain.auth.session_service import SessionService
from app.domain.auth.token_service import TokenService


class AuthService:
    """Service for core authentication operations.

    REFACTORED (MEDIUM-006):
    - Uses TokenService for JWT operations
    - Uses SessionService for session management
    - Focuses on authentication logic only
    - Uses bcrypt directly (passlib bcrypt 4.x compatibility fix)
    """

    def __init__(self, repository: UserRepository):
        """Initialize service with dependencies.

        Args:
            repository: UserRepository instance for data access
        """
        self.repository = repository
        self.token_service = TokenService()
        self.session_service = SessionService()

    # ============================================================================
    # PASSWORD MANAGEMENT
    # ============================================================================

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash using bcrypt directly."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False



    def get_password_hash(self, password: str) -> str:
        """Hash password using bcrypt directly.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength.

        Requirements:
        - At least 8 characters
        - Contains at least one digit

        Args:
            password: Password to validate

        Returns:
            True if password meets requirements, False otherwise
        """
        return len(password) >= 8 and any(c.isdigit() for c in password)

    # ============================================================================
    # USER AUTHENTICATION
    # ============================================================================

    def register_user(self, registration_data: dict) -> User:
        """Register new user with validation.

        Args:
            registration_data: User registration data

        Returns:
            Created User object

        Raises:
            HTTPException: If email exists or validation fails
        """
        # Removed debug logging for production

        # Check if email already exists (using repository)
        if self.repository.email_exists(registration_data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email già registrata"
            )

        # Validate password strength
        password = registration_data.get("password", "")
        if not self.validate_password_strength(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password deve contenere almeno 8 caratteri e 1 numero",
            )

        # Hash password
        hashed_password = self.get_password_hash(registration_data["password"])

        # Create user entity
        new_user = User(
            email=registration_data["email"],
            username=registration_data.get("username"),
            full_name=registration_data["full_name"],
            password=hashed_password,
            role=registration_data.get("role", "CUSTOMER"),
            is_active=True,
            created_at=datetime.now(UTC),
        )

        try:
            # Create via repository
            created_user = self.repository.create(new_user)
            self.repository.commit()
            return created_user
        except Exception:
            self.repository.rollback()
            logger.error(f"Registration failed for {registration_data.get('email')}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore durante registrazione. Riprova più tardi.",
            )

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            User object if authenticated, None otherwise
        """
        # Get user by email (using repository)
        user = self.repository.get_by_email(email)

        if not user:
            return None

        if not self.verify_password(password, user.password):
            return None

        return user

    def get_current_user_from_token(self, token: str) -> User:
        """Get current user from JWT token.

        Args:
            token: JWT access token

        Returns:
            User object

        Raises:
            HTTPException: If token invalid or user not found
        """
        # Delegate token decoding to TokenService
        payload = self.token_service.decode_token(token)
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user by email (using repository)
        user = self.repository.get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    # ============================================================================
    # TOKEN & SESSION DELEGATION (Backward Compatibility)
    # ============================================================================

    def create_tokens_for_user(self, user: User) -> dict[str, str]:
        """Create access and refresh tokens for user.

        Delegates to TokenService.

        Args:
            user: User object

        Returns:
            Dict with access_token, refresh_token, and token_type
        """
        return self.token_service.create_tokens_for_user(user.email)

    def check_permission(self, user: User, required_role: str) -> bool:
        """Check if user has required permission level.

        Uses role hierarchy: USER < CUSTOMER < PRO < ADMIN

        Args:
            user: User object to check
            required_role: Minimum required role

        Returns:
            True if user has sufficient permissions, False otherwise
        """
        role_hierarchy = ["USER", "CUSTOMER", "PRO", "ADMIN"]
        user_level = (
            role_hierarchy.index(user.role.upper()) if user.role.upper() in role_hierarchy else 0
        )
        required_level = (
            role_hierarchy.index(required_role.upper())
            if required_role.upper() in role_hierarchy
            else 0
        )
        return user_level >= required_level

    # ============================================================================
    # PERMISSION & ROLE MANAGEMENT
    # ============================================================================


# ============================================================================
# BACKWARD COMPATIBILITY - STANDALONE FUNCTIONS
# ============================================================================
# These provide backward compatibility for code that imports functions directly.
# New code should use service instances instead.
#
# REFACTORED (MEDIUM-006):
# - Token operations now use TokenService
# - Session operations now use SessionService
# - Password helpers use bcrypt directly (passlib bcrypt 4.x compatibility fix)

# Password helpers (stateless, using bcrypt directly)
def verify_password(plain: str, hashed: str) -> bool:
    """Verify password using bcrypt directly."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

# Token service instance for standalone functions
_token_service = TokenService()

# Token operations (delegate to TokenService)
def create_access_token(data: dict, expires_delta=None) -> str:
    """Standalone function for backward compatibility."""
    return _token_service.create_access_token(data, expires_delta)

def create_refresh_token(data: dict) -> str:
    """Standalone function for backward compatibility."""
    return _token_service.create_refresh_token(data)

def decode_token(token: str) -> dict:
    """Standalone function for backward compatibility."""
    return _token_service.decode_token(token)

# Export constants
ACCESS_TOKEN_EXPIRE_MINUTES = TokenService.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = TokenService.REFRESH_TOKEN_EXPIRE_DAYS
