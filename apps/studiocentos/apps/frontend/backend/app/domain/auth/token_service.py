"""Token Service - JWT Token Management Layer

Handles JWT token creation, validation, and blacklist management.
Extracted from AuthService as part of MEDIUM-006 refactoring.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

import time

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.infrastructure.cache.manager import RedisCache


class TokenService:
    """Service for JWT token operations and lifecycle management.

    Responsibilities:
    - Create access and refresh tokens
    - Decode and validate tokens
    - Manage token blacklist (logout)
    - Token type verification
    """

    # JWT settings - Use centralized configuration for persistence
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # 7 days from config
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days for refresh

    def __init__(self):
        """Initialize token service with Redis cache for blacklist."""
        self.redis_cache = RedisCache()

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        """Create JWT access token.

        Args:
            data: Data to include in token payload (typically {"sub": email})
            expires_delta: Custom token expiration time (optional)

        Returns:
            Encoded JWT access token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_jwt

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Create JWT refresh token with longer expiration.

        Args:
            data: Data to include in token payload (typically {"sub": email})

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_jwt

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate JWT token (checks blacklist).

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary

        Raises:
            HTTPException: If token is invalid, expired, or blacklisted
        """
        try:
            # Check if token is blacklisted
            blacklist_key = f"token:blacklist:{token}"
            if self.redis_cache.get(blacklist_key):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        """Verify refresh token validity and type.

        Args:
            token: Refresh token string

        Returns:
            Token payload if valid

        Raises:
            HTTPException: If token invalid or not a refresh token
        """
        payload = self.decode_token(token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        return payload

    def create_tokens_for_user(self, email: str) -> dict[str, str]:
        """Create both access and refresh tokens for a user.

        Args:
            email: User email to include in token payload

        Returns:
            Dict with access_token, refresh_token, and token_type
        """
        access_token = self.create_access_token({"sub": email})
        refresh_token = self.create_refresh_token({"sub": email})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist (for logout).

        Args:
            token: JWT token to invalidate

        Returns:
            True if blacklisting successful, False otherwise
        """
        try:
            # Decode token to get expiration
            payload = self.decode_token(token)
            exp = payload.get("exp")

            if not exp:
                return False

            # Calculate TTL (time until token expires)
            now = int(time.time())
            ttl = exp - now

            if ttl <= 0:
                # Token already expired, no need to blacklist
                return True

            # Add token to Redis blacklist with TTL
            blacklist_key = f"token:blacklist:{token}"
            self.redis_cache.set(blacklist_key, "revoked", ttl=ttl)

            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False

    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is in blacklist.

        Args:
            token: JWT token to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        blacklist_key = f"token:blacklist:{token}"
        return bool(self.redis_cache.get(blacklist_key))
