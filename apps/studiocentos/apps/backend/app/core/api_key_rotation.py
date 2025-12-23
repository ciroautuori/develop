"""Enterprise API Key Rotation - Automated Security Management."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from redis import asyncio as aioredis
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from app.core.config import settings
from app.infrastructure.database import Base
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger("api_key_rotation")

class APIKey(Base):
    """API Key model for external integrations."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Key details
    key_id = Column(String(32), unique=True, nullable=False, index=True)
    key_hash = Column(String(128), nullable=False)  # Hashed API key
    key_prefix = Column(String(8), nullable=False)  # First 8 chars for display

    # Metadata
    name = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)

    # Permissions
    scopes = Column(String(500), nullable=True)  # Comma-separated scopes

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Rotation
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    last_rotated_at = Column(DateTime, nullable=True)
    rotation_count = Column(Integer, default=0, nullable=False)

    # Security
    ip_whitelist = Column(String(500), nullable=True)  # Comma-separated IPs

    # Relationship
    user = relationship("User", back_populates="api_keys")

class APIKeyRotationService:
    """Enterprise API Key rotation and management service."""

    # Configuration
    KEY_LENGTH = 32
    KEY_LIFETIME = 90  # days
    ROTATION_WARNING_DAYS = 7
    MAX_KEYS_PER_USER = 10

    def __init__(self, db: Session, redis_client: Optional[aioredis.Redis] = None):
        self.db = db
        self.redis = redis_client

    def generate_api_key(self) -> tuple[str, str, str]:
        """
        Generate new API key.

        Returns:
            tuple: (key_id, api_key, key_prefix)
        """
        # Generate unique key ID
        key_id = secrets.token_urlsafe(16)

        # Generate API key
        api_key = f"cvlab_{secrets.token_urlsafe(self.KEY_LENGTH)}"

        # Extract prefix for display
        key_prefix = api_key[:12]

        return key_id, api_key, key_prefix

    def hash_key(self, api_key: str) -> str:
        """Hash API key for storage."""
        import hashlib

        return hashlib.sha256(api_key.encode()).hexdigest()

    async def create_api_key(
        self,
        user_id: int,
        name: str,
        scopes: List[str],
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        ip_whitelist: Optional[List[str]] = None,
    ) -> dict:
        """
        Create new API key.

        Args:
            user_id: User ID
            name: Key name
            scopes: Permission scopes
            description: Key description
            expires_in_days: Custom expiration (default: 90 days)
            ip_whitelist: Allowed IP addresses

        Returns:
            API key details (key shown only once)
        """
        # Check key limit
        existing_keys = (
            self.db.query(APIKey)
            .filter(APIKey.user_id == user_id, APIKey.is_active == True)
            .count()
        )

        if existing_keys >= self.MAX_KEYS_PER_USER:
            raise ValueError(f"Maximum {self.MAX_KEYS_PER_USER} active API keys allowed")

        # Generate key
        key_id, api_key, key_prefix = self.generate_api_key()
        key_hash = self.hash_key(api_key)

        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days or self.KEY_LIFETIME)

        # Create key record
        db_key = APIKey(
            user_id=user_id,
            key_id=key_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
            description=description,
            scopes=",".join(scopes),
            expires_at=expires_at,
            ip_whitelist=",".join(ip_whitelist) if ip_whitelist else None,
        )

        self.db.add(db_key)
        self.db.commit()
        self.db.refresh(db_key)

        logger.info(f"API key created for user {user_id}: {key_prefix}...")

        return {
            "key_id": key_id,
            "api_key": api_key,  # Only shown once!
            "key_prefix": key_prefix,
            "name": name,
            "scopes": scopes,
            "expires_at": expires_at.isoformat(),
            "warning": "Save this API key securely. It won't be shown again.",
        }

    async def rotate_api_key(self, key_id: str, user_id: int, keep_old_key_days: int = 7) -> dict:
        """
        Rotate API key (create new, deprecate old).

        Args:
            key_id: Current key ID
            user_id: User ID
            keep_old_key_days: Days to keep old key active

        Returns:
            New API key details
        """
        # Get current key
        old_key = (
            self.db.query(APIKey)
            .filter(APIKey.key_id == key_id, APIKey.user_id == user_id, APIKey.is_active == True)
            .first()
        )

        if not old_key:
            raise ValueError("API key not found")

        # Generate new key
        new_key_id, new_api_key, new_key_prefix = self.generate_api_key()
        new_key_hash = self.hash_key(new_api_key)

        # Create new key with same permissions
        new_key = APIKey(
            user_id=user_id,
            key_id=new_key_id,
            key_hash=new_key_hash,
            key_prefix=new_key_prefix,
            name=old_key.name,
            description=f"Rotated from {old_key.key_prefix}...",
            scopes=old_key.scopes,
            expires_at=datetime.now(timezone.utc) + timedelta(days=self.KEY_LIFETIME),
            ip_whitelist=old_key.ip_whitelist,
            rotation_count=old_key.rotation_count + 1,
        )

        self.db.add(new_key)

        # Deprecate old key (keep active for transition period)
        old_key.expires_at = datetime.now(timezone.utc) + timedelta(days=keep_old_key_days)
        old_key.last_rotated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(new_key)

        logger.info(
            f"API key rotated for user {user_id}: "
            f"{old_key.key_prefix}... -> {new_key_prefix}... "
            f"(old key expires in {keep_old_key_days} days)"
        )

        return {
            "key_id": new_key_id,
            "api_key": new_api_key,
            "key_prefix": new_key_prefix,
            "old_key_prefix": old_key.key_prefix,
            "old_key_expires_at": old_key.expires_at.isoformat(),
            "transition_period_days": keep_old_key_days,
            "warning": "Update your applications with the new API key before the old one expires.",
        }

    async def validate_api_key(
        self,
        api_key: str,
        required_scopes: Optional[List[str]] = None,
        client_ip: Optional[str] = None,
    ) -> tuple[bool, Optional[dict]]:
        """
        Validate API key and check permissions.

        Args:
            api_key: API key to validate
            required_scopes: Required permission scopes
            client_ip: Client IP address

        Returns:
            tuple: (is_valid, key_data)
        """
        # Hash key for lookup
        key_hash = self.hash_key(api_key)

        # Check cache first (Redis)
        if self.redis:
            cache_key = f"api_key:{key_hash[:16]}"
            cached = await self.redis.get(cache_key)

            if cached:
                import json

                key_data = json.loads(cached)

                # Update last used
                self.db.query(APIKey).filter(APIKey.key_id == key_data["key_id"]).update(
                    {"last_used_at": datetime.now(timezone.utc)}
                )
                self.db.commit()

                return True, key_data

        # Look up key in database
        db_key = (
            self.db.query(APIKey)
            .filter(APIKey.key_hash == key_hash, APIKey.is_active == True)
            .first()
        )

        if not db_key:
            logger.warning("Invalid API key attempted")
            return False, None

        # Check expiration
        if db_key.expires_at and datetime.now(timezone.utc) > db_key.expires_at:
            logger.warning(f"Expired API key used: {db_key.key_prefix}...")
            return False, None

        # Check IP whitelist
        if db_key.ip_whitelist and client_ip:
            allowed_ips = db_key.ip_whitelist.split(",")
            if client_ip not in allowed_ips:
                logger.warning(
                    f"API key used from unauthorized IP: {client_ip} "
                    f"(key: {db_key.key_prefix}...)"
                )
                return False, None

        # Check scopes
        key_scopes = db_key.scopes.split(",") if db_key.scopes else []
        if required_scopes:
            if not all(scope in key_scopes for scope in required_scopes):
                logger.warning(
                    f"API key missing required scopes: {required_scopes} "
                    f"(key: {db_key.key_prefix}...)"
                )
                return False, None

        # Update last used
        db_key.last_used_at = datetime.now(timezone.utc)
        self.db.commit()

        # Prepare key data
        key_data = {
            "key_id": db_key.key_id,
            "user_id": db_key.user_id,
            "scopes": key_scopes,
            "name": db_key.name,
        }

        # Cache valid key (5 minutes)
        if self.redis:
            import json

            cache_key = f"api_key:{key_hash[:16]}"
            await self.redis.setex(cache_key, 300, json.dumps(key_data))

        return True, key_data

    async def revoke_api_key(self, key_id: str, user_id: int):
        """Revoke API key immediately."""
        key = (
            self.db.query(APIKey).filter(APIKey.key_id == key_id, APIKey.user_id == user_id).first()
        )

        if not key:
            raise ValueError("API key not found")

        key.is_active = False
        self.db.commit()

        # Clear cache
        if self.redis:
            cache_key = f"api_key:{key.key_hash[:16]}"
            await self.redis.delete(cache_key)

        logger.info(f"API key revoked: {key.key_prefix}... (user: {user_id})")

    async def get_user_api_keys(self, user_id: int) -> List[dict]:
        """Get all API keys for user."""
        keys = (
            self.db.query(APIKey)
            .filter(APIKey.user_id == user_id)
            .order_by(APIKey.created_at.desc())
            .all()
        )

        result = []
        for key in keys:
            # Check if expiring soon
            days_until_expiry = None
            expires_soon = False

            if key.expires_at:
                days_until_expiry = (key.expires_at - datetime.now(timezone.utc)).days
                expires_soon = days_until_expiry <= self.ROTATION_WARNING_DAYS

            result.append(
                {
                    "key_id": key.key_id,
                    "key_prefix": key.key_prefix,
                    "name": key.name,
                    "scopes": key.scopes.split(",") if key.scopes else [],
                    "is_active": key.is_active,
                    "created_at": key.created_at.isoformat(),
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                    "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                    "rotation_count": key.rotation_count,
                    "expires_soon": expires_soon,
                    "days_until_expiry": days_until_expiry,
                }
            )

        return result

    async def auto_rotate_expiring_keys(self):
        """
        Automated task to rotate keys expiring soon.
        Run this as a scheduled task (cron/celery).
        """
        warning_date = datetime.now(timezone.utc) + timedelta(days=self.ROTATION_WARNING_DAYS)

        # Find keys expiring soon
        expiring_keys = (
            self.db.query(APIKey)
            .filter(
                APIKey.is_active == True,
                APIKey.expires_at <= warning_date,
                APIKey.expires_at > datetime.now(timezone.utc),
            )
            .all()
        )

        rotated_count = 0

        for key in expiring_keys:
            try:
                # Auto-rotate with notification
                result = await self.rotate_api_key(
                    key.key_id, key.user_id, keep_old_key_days=self.ROTATION_WARNING_DAYS
                )

                # Log API key rotation
                logger.warning(
                    f"API_KEY_ROTATED: Auto-rotated for user {key.user_id}: {key.key_prefix}... -> {result['key_prefix']}...",
                    extra={
                        "event_type": "api_key_rotation",
                        "user_id": key.user_id,
                        "old_key_prefix": key.key_prefix,
                        "new_key_prefix": result["key_prefix"],
                        "rotation_reason": "scheduled_auto_rotation",
                        "requires_user_notification": True,
                        "security_alert": True,
                    },
                )

                # Send email notification
                try:
                    from app.infrastructure.external.email import EmailService
                    
                    # Get user email from relationship
                    user = key.user
                    if user and user.email:
                        EmailService.send_api_key_rotation_notification(
                            email=user.email,
                            key_name=key.name or f"API Key {key.key_prefix}",
                            new_key_prefix=result["key_prefix"],
                            rotation_reason="scheduled"
                        )
                        logger.info(f"Email notification sent to {user.email} for key rotation")
                    else:
                        logger.warning(f"Could not send email: user or email not found for user_id {key.user_id}")
                except Exception as email_error:
                    logger.error(f"Failed to send email notification: {email_error}")
                    # Continue even if email fails (non-blocking)

                rotated_count += 1

            except Exception as e:
                logger.error(f"Failed to auto-rotate key {key.key_id}: {e}")

        logger.info(f"Auto-rotation complete: {rotated_count} keys rotated")
        return rotated_count

# Dependency for FastAPI
async def get_api_key_service() -> APIKeyRotationService:
    """Get API key service instance.
    
    Note: This is a stub implementation. Full implementation requires db injection.
    """
    redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return APIKeyRotationService(None, redis_client)
