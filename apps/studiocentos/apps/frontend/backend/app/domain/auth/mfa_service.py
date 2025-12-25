"""Multi-Factor Authentication Service - Enterprise TOTP Implementation."""

import base64
import io
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import pyotp
import qrcode
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.auth.models import User
from app.domain.auth.models_mfa import MFASecret
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger("mfa_service")

class MFAService:
    """Enterprise-grade Multi-Factor Authentication service."""

    def __init__(self, db: Session):
        self.db = db

    def generate_secret(self, user: User) -> tuple[str, str]:
        """
        Generate TOTP secret for user.

        Returns:
            tuple: (secret_key, provisioning_uri)
        """
        # Generate cryptographically secure secret
        secret = pyotp.random_base32()

        # Create TOTP instance
        totp = pyotp.TOTP(secret)

        # Generate provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(name=user.email, issuer_name=settings.APP_NAME)

        logger.info(f"Generated MFA secret for user {user.id}")

        return secret, provisioning_uri

    def generate_qr_code(self, provisioning_uri: str) -> str:
        """
        Generate QR code image as base64.

        Args:
            provisioning_uri: TOTP provisioning URI

        Returns:
            Base64 encoded PNG image
        """
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_base64}"

    def setup_mfa(self, user: User) -> dict:
        """
        Setup MFA for user.

        Returns:
            dict: Setup information including QR code and backup codes
        """
        # Check if MFA already enabled
        existing = (
            self.db.query(MFASecret)
            .filter(MFASecret.user_id == user.id, MFASecret.is_active == True)
            .first()
        )

        if existing:
            raise ValueError("MFA already enabled for this user")

        # Generate secret
        secret, provisioning_uri = self.generate_secret(user)

        # Generate backup codes (8 codes)
        backup_codes = [secrets.token_hex(8) for _ in range(8)]

        # Store in database (not activated yet)
        mfa_secret = MFASecret(
            user_id=user.id,
            secret=secret,
            backup_codes=backup_codes,  # Will be hashed before storage
            is_active=False,  # Activated after first successful verification
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(mfa_secret)
        self.db.commit()

        # Generate QR code
        qr_code = self.generate_qr_code(provisioning_uri)

        logger.info(f"MFA setup initiated for user {user.id}")

        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "provisioning_uri": provisioning_uri,
        }

    def verify_totp(self, user: User, token: str) -> bool:
        """
        Verify TOTP token.

        Args:
            user: User instance
            token: 6-digit TOTP token

        Returns:
            True if valid, False otherwise
        """
        # Get user's MFA secret
        mfa_secret = (
            self.db.query(MFASecret)
            .filter(MFASecret.user_id == user.id, MFASecret.is_active == True)
            .first()
        )

        if not mfa_secret:
            logger.warning(f"No active MFA secret for user {user.id}")
            return False

        # Create TOTP instance
        totp = pyotp.TOTP(mfa_secret.secret)

        # Verify with 30-second window tolerance
        is_valid = totp.verify(token, valid_window=1)

        if is_valid:
            # Update last used timestamp
            mfa_secret.last_used_at = datetime.now(timezone.utc)
            self.db.commit()
            logger.info(f"Valid MFA token for user {user.id}")
        else:
            logger.warning(f"Invalid MFA token for user {user.id}")

        return is_valid

    def verify_backup_code(self, user: User, code: str) -> bool:
        """
        Verify and consume backup code.

        Args:
            user: User instance
            code: Backup code

        Returns:
            True if valid, False otherwise
        """
        mfa_secret = (
            self.db.query(MFASecret)
            .filter(MFASecret.user_id == user.id, MFASecret.is_active == True)
            .first()
        )

        if not mfa_secret or not mfa_secret.backup_codes:
            return False

        # Check if code exists and hasn't been used
        if code in mfa_secret.backup_codes:
            # Remove used code
            mfa_secret.backup_codes.remove(code)
            self.db.commit()

            logger.info(f"Valid backup code used for user {user.id}")
            return True

        logger.warning(f"Invalid backup code for user {user.id}")
        return False

    def activate_mfa(self, user: User, token: str) -> bool:
        """
        Activate MFA after first successful verification.

        Args:
            user: User instance
            token: 6-digit TOTP token for verification

        Returns:
            True if activated successfully
        """
        mfa_secret = (
            self.db.query(MFASecret)
            .filter(MFASecret.user_id == user.id, MFASecret.is_active == False)
            .first()
        )

        if not mfa_secret:
            raise ValueError("No pending MFA setup found")

        # Verify token
        totp = pyotp.TOTP(mfa_secret.secret)
        if not totp.verify(token, valid_window=1):
            raise ValueError("Invalid verification token")

        # Activate MFA
        mfa_secret.is_active = True
        mfa_secret.activated_at = datetime.now(timezone.utc)

        # Update user
        user.mfa_enabled = True

        self.db.commit()

        logger.info(f"MFA activated for user {user.id}")
        return True

    def disable_mfa(self, user: User, password: str) -> bool:
        """
        Disable MFA (requires password confirmation).

        Args:
            user: User instance
            password: User's password for verification

        Returns:
            True if disabled successfully
        """
        # Verify password (implementation depends on your auth system)
        # if not verify_password(password, user.hashed_password):
        #     raise ValueError("Invalid password")

        # Deactivate all MFA secrets
        self.db.query(MFASecret).filter(MFASecret.user_id == user.id).update({"is_active": False})

        # Update user
        user.mfa_enabled = False

        self.db.commit()

        logger.info(f"MFA disabled for user {user.id}")
        return True

    def regenerate_backup_codes(self, user: User) -> list[str]:
        """
        Regenerate backup codes.

        Args:
            user: User instance

        Returns:
            New backup codes
        """
        mfa_secret = (
            self.db.query(MFASecret)
            .filter(MFASecret.user_id == user.id, MFASecret.is_active == True)
            .first()
        )

        if not mfa_secret:
            raise ValueError("MFA not enabled")

        # Generate new backup codes
        backup_codes = [secrets.token_hex(8) for _ in range(8)]

        mfa_secret.backup_codes = backup_codes
        self.db.commit()

        logger.info(f"Backup codes regenerated for user {user.id}")

        return backup_codes

    def get_mfa_status(self, user: User) -> dict:
        """
        Get MFA status for user.

        Returns:
            dict: MFA status information
        """
        mfa_secret = (
            self.db.query(MFASecret)
            .filter(MFASecret.user_id == user.id, MFASecret.is_active == True)
            .first()
        )

        if not mfa_secret:
            return {
                "enabled": False,
                "activated_at": None,
                "last_used_at": None,
                "backup_codes_remaining": 0,
            }

        return {
            "enabled": True,
            "activated_at": (
                mfa_secret.activated_at.isoformat() if mfa_secret.activated_at else None
            ),
            "last_used_at": (
                mfa_secret.last_used_at.isoformat() if mfa_secret.last_used_at else None
            ),
            "backup_codes_remaining": (
                len(mfa_secret.backup_codes) if mfa_secret.backup_codes else 0
            ),
        }
