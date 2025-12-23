"""Enterprise Session Security - Device Fingerprinting & Timeout Management."""

import hashlib
import json
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Request
from redis import asyncio as aioredis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger("session_security")

class SessionSecurity:
    """Enterprise-grade session security service."""

    # Configuration
    SESSION_TIMEOUT = 1800  # 30 minutes of inactivity
    SESSION_MAX_LIFETIME = 43200  # 12 hours absolute
    TOKEN_REFRESH_THRESHOLD = 300  # Refresh if <5 min remaining
    MAX_CONCURRENT_SESSIONS = 3
    REMEMBER_ME_DURATION = 2592000  # 30 days

    def __init__(self, redis_client: aioredis.Redis | None = None, db: Session | None = None):
        self.redis = redis_client
        self.db = db

    def generate_device_fingerprint(self, request: Request) -> str:
        """
        Generate device fingerprint from request metadata.

        Args:
            request: FastAPI request object

        Returns:
            Unique device fingerprint hash
        """
        # Collect device information
        user_agent = request.headers.get("user-agent", "")
        accept_language = request.headers.get("accept-language", "")
        accept_encoding = request.headers.get("accept-encoding", "")

        # Client IP (consider proxy headers)
        client_ip = request.client.host if request.client else "unknown"
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()

        # Create fingerprint string
        fingerprint_data = "|".join([user_agent, accept_language, accept_encoding, client_ip])

        # Hash for consistency and privacy
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

        return fingerprint

    def extract_device_info(self, request: Request) -> dict:
        """Extract detailed device information."""
        user_agent = request.headers.get("user-agent", "")

        # Parse user agent (simplified - use user-agents library in production)
        device_info = {
            "user_agent": user_agent,
            "ip_address": request.client.host if request.client else "unknown",
            "device_type": self.detect_device_type(user_agent),
            "browser": self.detect_browser(user_agent),
            "os": self.detect_os(user_agent),
            "is_mobile": "Mobile" in user_agent
            or "Android" in user_agent
            or "iPhone" in user_agent,
            "is_bot": self.is_bot(user_agent),
        }

        return device_info

    @staticmethod
    def detect_device_type(user_agent: str) -> str:
        """Detect device type from user agent."""
        ua_lower = user_agent.lower()

        if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            return "mobile"
        if "tablet" in ua_lower or "ipad" in ua_lower:
            return "tablet"
        return "desktop"

    @staticmethod
    def detect_browser(user_agent: str) -> str:
        """Detect browser from user agent."""
        ua_lower = user_agent.lower()

        if "firefox" in ua_lower:
            return "Firefox"
        if "chrome" in ua_lower:
            return "Chrome"
        if "safari" in ua_lower:
            return "Safari"
        if "edge" in ua_lower:
            return "Edge"
        if "opera" in ua_lower:
            return "Opera"
        return "Unknown"

    @staticmethod
    def detect_os(user_agent: str) -> str:
        """Detect operating system from user agent."""
        if "Windows" in user_agent:
            return "Windows"
        if "Mac OS" in user_agent or "macOS" in user_agent:
            return "macOS"
        if "Linux" in user_agent:
            return "Linux"
        if "Android" in user_agent:
            return "Android"
        if "iOS" in user_agent or "iPhone" in user_agent:
            return "iOS"
        return "Unknown"

    @staticmethod
    def is_bot(user_agent: str) -> bool:
        """Detect if request is from a bot."""
        bot_keywords = ["bot", "crawler", "spider", "scraper", "curl", "wget"]
        ua_lower = user_agent.lower()
        return any(keyword in ua_lower for keyword in bot_keywords)

    async def create_session(
        self, user_id: int, request: Request, remember_me: bool = False
    ) -> dict:
        """
        Create new session with device fingerprint.

        Args:
            user_id: User ID
            request: Request object
            remember_me: Extended session duration

        Returns:
            Session data including token
        """
        if not self.redis:
            return {}

        # Generate device fingerprint
        fingerprint = self.generate_device_fingerprint(request)
        device_info = self.extract_device_info(request)

        # Generate session token
        session_token = secrets.token_urlsafe(32)

        # Session metadata
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(
            seconds=self.REMEMBER_ME_DURATION if remember_me else self.SESSION_MAX_LIFETIME
        )

        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "device_fingerprint": fingerprint,
            "device_info": device_info,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_activity": created_at.isoformat(),
            "remember_me": remember_me,
        }

        # Store in Redis
        session_key = f"session:{session_token}"
        user_sessions_key = f"user_sessions:{user_id}"

        # Store session data
        await self.redis.setex(
            session_key, int((expires_at - created_at).total_seconds()), json.dumps(session_data)
        )

        # Add to user's session list
        await self.redis.sadd(user_sessions_key, session_token)

        # Enforce max concurrent sessions
        await self.enforce_session_limit(user_id)

        logger.info(
            f"Session created for user {user_id} "
            f"(device: {device_info['device_type']}, "
            f"remember_me: {remember_me})"
        )

        return session_data

    async def validate_session(
        self, session_token: str, request: Request, check_fingerprint: bool = True
    ) -> tuple[bool, dict | None]:
        """
        Validate session and check for hijacking.

        Args:
            session_token: Session token
            request: Current request
            check_fingerprint: Verify device fingerprint matches

        Returns:
            tuple: (is_valid, session_data)
        """
        if not self.redis:
            return False, None

        session_key = f"session:{session_token}"

        # Get session data
        session_str = await self.redis.get(session_key)
        if not session_str:
            logger.warning(f"Invalid session token: {session_token[:16]}...")
            return False, None

        session_data = json.loads(session_str)

        # Check expiration
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.now(UTC) > expires_at:
            logger.info(f"Expired session: {session_token[:16]}...")
            await self.destroy_session(session_token)
            return False, None

        # Check inactivity timeout
        last_activity = datetime.fromisoformat(session_data["last_activity"])
        if datetime.now(UTC) - last_activity > timedelta(seconds=self.SESSION_TIMEOUT):
            if not session_data.get("remember_me"):
                logger.info(f"Session timed out (inactivity): {session_token[:16]}...")
                await self.destroy_session(session_token)
                return False, None

        # Verify device fingerprint (session hijacking prevention)
        if check_fingerprint:
            current_fingerprint = self.generate_device_fingerprint(request)
            stored_fingerprint = session_data.get("device_fingerprint")

            if current_fingerprint != stored_fingerprint:
                logger.warning(
                    f"Device fingerprint mismatch - possible session hijacking "
                    f"(session: {session_token[:16]}...)"
                )
                # In strict mode, invalidate session
                # await self.destroy_session(session_token)
                # return False, None

                # For now, just log the warning

        # Update last activity
        session_data["last_activity"] = datetime.now(UTC).isoformat()

        # Refresh session TTL
        ttl = int((expires_at - datetime.now(UTC)).total_seconds())
        await self.redis.setex(session_key, ttl, json.dumps(session_data))

        return True, session_data

    async def destroy_session(self, session_token: str):
        """Destroy session."""
        if not self.redis:
            return

        session_key = f"session:{session_token}"

        # Get session data to remove from user's session list
        session_str = await self.redis.get(session_key)
        if session_str:
            session_data = json.loads(session_str)
            user_id = session_data.get("user_id")

            if user_id:
                user_sessions_key = f"user_sessions:{user_id}"
                await self.redis.srem(user_sessions_key, session_token)

        # Delete session
        await self.redis.delete(session_key)
        logger.info(f"Session destroyed: {session_token[:16]}...")

    async def destroy_all_user_sessions(self, user_id: int):
        """Destroy all sessions for a user (security action)."""
        if not self.redis:
            return

        user_sessions_key = f"user_sessions:{user_id}"

        # Get all user sessions
        sessions = await self.redis.smembers(user_sessions_key)

        # Delete each session
        for session_token in sessions:
            await self.destroy_session(session_token)

        # Clear user sessions set
        await self.redis.delete(user_sessions_key)

        logger.info(f"All sessions destroyed for user {user_id}")

    async def enforce_session_limit(self, user_id: int):
        """Enforce maximum concurrent sessions."""
        if not self.redis:
            return

        user_sessions_key = f"user_sessions:{user_id}"

        # Get all user sessions
        sessions = await self.redis.smembers(user_sessions_key)

        if len(sessions) <= self.MAX_CONCURRENT_SESSIONS:
            return

        # Remove oldest sessions
        sessions_with_time = []
        for session_token in sessions:
            session_key = f"session:{session_token}"
            session_str = await self.redis.get(session_key)

            if session_str:
                session_data = json.loads(session_str)
                created_at = datetime.fromisoformat(session_data["created_at"])
                sessions_with_time.append((session_token, created_at))

        # Sort by creation time
        sessions_with_time.sort(key=lambda x: x[1])

        # Remove excess sessions
        excess_count = len(sessions_with_time) - self.MAX_CONCURRENT_SESSIONS
        for i in range(excess_count):
            session_token = sessions_with_time[i][0]
            await self.destroy_session(session_token)

        logger.info(
            f"Enforced session limit for user {user_id} (removed {excess_count} old sessions)"
        )

    async def get_user_sessions(self, user_id: int) -> list[dict]:
        """Get all active sessions for user."""
        if not self.redis:
            return []

        user_sessions_key = f"user_sessions:{user_id}"
        session_tokens = await self.redis.smembers(user_sessions_key)

        sessions = []
        for session_token in session_tokens:
            session_key = f"session:{session_token}"
            session_str = await self.redis.get(session_key)

            if session_str:
                session_data = json.loads(session_str)
                sessions.append(
                    {
                        "session_token": session_token[:16] + "...",  # Truncated for security
                        "device_info": session_data.get("device_info", {}),
                        "created_at": session_data.get("created_at"),
                        "last_activity": session_data.get("last_activity"),
                        "is_current": False,  # Set by caller if this is current session
                    }
                )

        return sessions

# Dependency for FastAPI
async def get_session_security(db: Session) -> SessionSecurity:
    """Get session security instance."""
    redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return SessionSecurity(redis_client, db)
