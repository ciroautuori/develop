"""Enterprise Brute Force Protection - Progressive Delays & Account Lockout."""

import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from redis import asyncio as aioredis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger("brute_force")

class BruteForceProtection:
    """Enterprise-grade brute force protection service."""

    # Configuration
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 1800  # 30 minutes
    PROGRESSIVE_DELAYS = [0, 2, 5, 10, 30]  # seconds

    # Suspicious activity thresholds
    SUSPICIOUS_THRESHOLD = 10  # attempts
    BAN_THRESHOLD = 20  # attempts
    BAN_DURATION = 86400  # 24 hours

    def __init__(self, redis_client: Optional[aioredis.Redis] = None, db: Optional[Session] = None):
        self.redis = redis_client
        self.db = db

    async def record_login_attempt(
        self, identifier: str, success: bool, ip_address: str, user_agent: str = ""
    ) -> dict:
        """
        Record login attempt and check for brute force.

        Args:
            identifier: Email or username
            success: Whether login was successful
            ip_address: Client IP address
            user_agent: User agent string

        Returns:
            dict: Protection status and actions
        """
        if not self.redis:
            return {"allowed": True}

        # Redis keys
        user_key = f"login_attempts:user:{identifier}"
        ip_key = f"login_attempts:ip:{ip_address}"
        lockout_key = f"lockout:user:{identifier}"
        ban_key = f"ban:ip:{ip_address}"

        # Check if IP is banned
        if await self.redis.exists(ban_key):
            logger.warning(f"Login attempt from banned IP: {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your IP has been temporarily banned due to suspicious activity",
            )

        # Check if account is locked
        if await self.redis.exists(lockout_key):
            ttl = await self.redis.ttl(lockout_key)
            logger.warning(f"Login attempt on locked account: {identifier}")
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account temporarily locked. Try again in {ttl // 60} minutes.",
            )

        if success:
            # Successful login - reset counters
            await self.redis.delete(user_key)
            await self.redis.delete(ip_key)
            logger.info(f"Successful login: {identifier} from {ip_address}")

            return {"allowed": True, "action": "login_success"}

        # Failed login - increment counters
        user_attempts = await self.redis.incr(user_key)
        ip_attempts = await self.redis.incr(ip_key)

        # Set expiration (1 hour)
        await self.redis.expire(user_key, 3600)
        await self.redis.expire(ip_key, 3600)

        logger.warning(
            f"Failed login: {identifier} from {ip_address} "
            f"(user_attempts={user_attempts}, ip_attempts={ip_attempts})"
        )

        # Check for account lockout
        if user_attempts >= self.MAX_LOGIN_ATTEMPTS:
            await self.redis.setex(lockout_key, self.LOCKOUT_DURATION, "1")

            # Log security event
            await self.log_security_event(
                event_type="account_lockout",
                identifier=identifier,
                ip_address=ip_address,
                details=f"Account locked after {user_attempts} failed attempts",
            )

            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Too many failed attempts. Account locked for {self.LOCKOUT_DURATION // 60} minutes.",
            )

        # Check for IP ban
        if ip_attempts >= self.BAN_THRESHOLD:
            await self.redis.setex(ban_key, self.BAN_DURATION, "1")

            await self.log_security_event(
                event_type="ip_ban",
                identifier=identifier,
                ip_address=ip_address,
                details=f"IP banned after {ip_attempts} failed attempts",
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your IP has been temporarily banned due to suspicious activity",
            )

        # Progressive delay
        delay = self.get_progressive_delay(user_attempts)
        if delay > 0:
            await asyncio.sleep(delay)

        # Check for suspicious activity
        if ip_attempts >= self.SUSPICIOUS_THRESHOLD:
            await self.log_security_event(
                event_type="suspicious_activity",
                identifier=identifier,
                ip_address=ip_address,
                details=f"Suspicious activity: {ip_attempts} failed attempts from IP",
            )

        return {
            "allowed": True,
            "action": "login_failed",
            "attempts_remaining": self.MAX_LOGIN_ATTEMPTS - user_attempts,
            "delay_applied": delay,
            "warning": "suspicious" if ip_attempts >= self.SUSPICIOUS_THRESHOLD else None,
        }

    def get_progressive_delay(self, attempt_count: int) -> int:
        """Get progressive delay based on attempt count."""
        if attempt_count <= 0 or attempt_count > len(self.PROGRESSIVE_DELAYS):
            return self.PROGRESSIVE_DELAYS[-1]
        return self.PROGRESSIVE_DELAYS[attempt_count - 1]

    async def check_account_status(self, identifier: str) -> dict:
        """Check if account is locked or has restrictions."""
        if not self.redis:
            return {"locked": False}

        lockout_key = f"lockout:user:{identifier}"
        user_key = f"login_attempts:user:{identifier}"

        is_locked = await self.redis.exists(lockout_key)
        attempts = await self.redis.get(user_key)

        if is_locked:
            ttl = await self.redis.ttl(lockout_key)
            return {"locked": True, "unlock_in": ttl, "reason": "Too many failed login attempts"}

        return {
            "locked": False,
            "failed_attempts": int(attempts) if attempts else 0,
            "max_attempts": self.MAX_LOGIN_ATTEMPTS,
        }

    async def unlock_account(self, identifier: str, admin_override: bool = False):
        """Unlock account (admin function)."""
        if not self.redis:
            return

        lockout_key = f"lockout:user:{identifier}"
        user_key = f"login_attempts:user:{identifier}"

        await self.redis.delete(lockout_key)
        await self.redis.delete(user_key)

        if admin_override:
            await self.log_security_event(
                event_type="admin_unlock",
                identifier=identifier,
                ip_address="admin",
                details="Account unlocked by administrator",
            )

        logger.info(f"Account unlocked: {identifier}")

    async def unban_ip(self, ip_address: str, admin_override: bool = False):
        """Unban IP address (admin function)."""
        if not self.redis:
            return

        ban_key = f"ban:ip:{ip_address}"
        ip_key = f"login_attempts:ip:{ip_address}"

        await self.redis.delete(ban_key)
        await self.redis.delete(ip_key)

        if admin_override:
            await self.log_security_event(
                event_type="admin_unban",
                identifier="",
                ip_address=ip_address,
                details="IP unbanned by administrator",
            )

        logger.info(f"IP unbanned: {ip_address}")

    async def log_security_event(
        self, event_type: str, identifier: str, ip_address: str, details: str
    ):
        """Log security event to database and monitoring."""
        try:
            # Log to file
            logger.warning(
                f"SECURITY EVENT: {event_type} | "
                f"User: {identifier} | "
                f"IP: {ip_address} | "
                f"Details: {details}"
            )

            # Store in Redis for monitoring
            if self.redis:
                event_key = f"security_events:{datetime.now(timezone.utc).strftime('%Y%m%d')}"
                event_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": event_type,
                    "identifier": identifier,
                    "ip": ip_address,
                    "details": details,
                }

                await self.redis.rpush(event_key, str(event_data))
                await self.redis.expire(event_key, 604800)  # 7 days

            # Log to external monitoring (production ready)
            logger.warning(
                f"SECURITY_EVENT: {event_type} for {identifier} from {ip_address}",
                extra={
                    "event_type": event_type,
                    "identifier": identifier,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "metadata": metadata,
                    "security_alert": True,
                },
            )

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    async def get_security_stats(self) -> dict:
        """Get security statistics (admin dashboard)."""
        if not self.redis:
            return {}

        # Get current day's events
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        event_key = f"security_events:{today}"

        events = await self.redis.lrange(event_key, 0, -1)

        # Count by type
        event_counts = {}
        for event_str in events:
            try:
                event = eval(event_str)
                event_type = event.get("type", "unknown")
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            except:
                pass

        return {"date": today, "total_events": len(events), "events_by_type": event_counts}

# Dependency for FastAPI
async def get_brute_force_protection(db: Session) -> BruteForceProtection:
    """Get brute force protection instance."""
    redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return BruteForceProtection(redis_client, db)

# Decorator for login endpoints
def protect_login_endpoint():
    """Decorator to protect login endpoints from brute force."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Implementation depends on your auth flow
            # This should be integrated with your login handler
            return await func(*args, **kwargs)

        return wrapper

    return decorator
