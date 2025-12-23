"""Session Service - Redis Session Management Layer

Handles user session lifecycle in Redis cache.
Extracted from AuthService as part of MEDIUM-006 refactoring.
"""

import logging
import uuid
from datetime import UTC, datetime

from app.infrastructure.cache.manager import RedisCache

logger = logging.getLogger(__name__)


class SessionService:
    """Service for user session management in Redis.
    
    Responsibilities:
    - Create and track user sessions
    - Retrieve active sessions
    - Revoke individual or all user sessions
    - Session TTL management
    """

    def __init__(self, token_ttl_minutes: int = 30):
        """Initialize session service.
        
        Args:
            token_ttl_minutes: Default TTL for sessions in minutes
        """
        self.redis_cache = RedisCache()
        self.token_ttl_minutes = token_ttl_minutes

    def create_session(
        self, user_id: int, token: str, device_info: dict | None = None
    ) -> dict:
        """Create user session in Redis.

        Args:
            user_id: User ID to create session for
            token: JWT access token
            device_info: Optional dict with device/IP/user_agent info

        Returns:
            Dict with session_id, created_at, and expires_in

        Note:
            Session stored in Redis with TTL matching token expiry
        """
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            created_at = datetime.now(UTC)

            # Prepare session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": created_at.isoformat(),
                "token_jti": token[:16],  # Store token prefix for validation
                "device_info": device_info or {},
            }

            # Store in Redis with TTL (match token expiry)
            ttl = self.token_ttl_minutes * 60  # Convert to seconds
            session_key = f"session:{user_id}:{session_id}"
            self.redis_cache.set(session_key, session_data, ttl=ttl)

            # Add to user's active sessions list
            user_sessions_key = f"user:sessions:{user_id}"
            self.redis_cache.sadd(user_sessions_key, session_id)
            self.redis_cache.expire(user_sessions_key, ttl)

            return {
                "session_id": session_id,
                "created_at": created_at,
                "expires_in": ttl,
            }
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {e}")
            # Fallback to basic session without Redis
            return {
                "session_id": f"session_{user_id}",
                "created_at": datetime.now(UTC),
            }

    def get_user_sessions(self, user_id: int) -> list[str]:
        """Get all active session IDs for a user.

        Args:
            user_id: User ID

        Returns:
            List of active session IDs
        """
        try:
            user_sessions_key = f"user:sessions:{user_id}"
            session_ids = self.redis_cache.smembers(user_sessions_key)
            return list(session_ids) if session_ids else []
        except Exception as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []

    def get_session_data(self, user_id: int, session_id: str) -> dict | None:
        """Get session data from Redis.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            Session data dict or None if not found
        """
        try:
            session_key = f"session:{user_id}:{session_id}"
            return self.redis_cache.get(session_key)
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return None

    def revoke_session(self, user_id: int, session_id: str) -> bool:
        """Revoke a specific user session.

        Args:
            user_id: User ID
            session_id: Session ID to revoke

        Returns:
            True if session revoked successfully
        """
        try:
            session_key = f"session:{user_id}:{session_id}"
            user_sessions_key = f"user:sessions:{user_id}"

            # Remove session data
            self.redis_cache.delete(session_key)

            # Remove from user's sessions list
            self.redis_cache.srem(user_sessions_key, session_id)

            return True
        except Exception as e:
            logger.error(f"Failed to revoke session {session_id} for user {user_id}: {e}")
            return False

    def revoke_all_user_sessions(self, user_id: int) -> bool:
        """Revoke all sessions for a user (e.g., password change, security breach).

        Args:
            user_id: User ID

        Returns:
            True if all sessions revoked successfully
        """
        try:
            # Get all session IDs
            session_ids = self.get_user_sessions(user_id)

            # Delete each session
            for session_id in session_ids:
                session_key = f"session:{user_id}:{session_id}"
                self.redis_cache.delete(session_key)

            # Clear sessions list
            user_sessions_key = f"user:sessions:{user_id}"
            self.redis_cache.delete(user_sessions_key)

            logger.info(f"Revoked {len(session_ids)} sessions for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke all sessions for user {user_id}: {e}")
            return False

    def count_active_sessions(self, user_id: int) -> int:
        """Count active sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of active sessions
        """
        return len(self.get_user_sessions(user_id))

    def extend_session_ttl(self, user_id: int, session_id: str, ttl_seconds: int) -> bool:
        """Extend session TTL (e.g., on user activity).

        Args:
            user_id: User ID
            session_id: Session ID to extend
            ttl_seconds: New TTL in seconds

        Returns:
            True if TTL extended successfully
        """
        try:
            session_key = f"session:{user_id}:{session_id}"
            return self.redis_cache.expire(session_key, ttl_seconds)
        except Exception as e:
            logger.error(f"Failed to extend session TTL: {e}")
            return False
