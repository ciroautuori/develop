"""Refresh Token Mechanism
SEC-03: Implementa refresh token per JWT security.
"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from app.infrastructure.database import Base

class RefreshToken(Base):
    """Refresh Token Model.

    Memorizza refresh tokens per permettere rinnovo access token
    senza re-login. Supporta revocation e rotation.
    """

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by_token = Column(String, nullable=True)  # Token rotation

    # Relationship
    user = relationship("User", backref="refresh_tokens")

    @property
    def is_expired(self) -> bool:
        """Check se token è scaduto."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check se token è valido (non scaduto e non revocato)."""
        return not self.revoked and not self.is_expired

class RefreshTokenService:
    """Service per gestione refresh tokens."""

    @staticmethod
    def create_refresh_token(db: Session, user_id: int, expires_days: int = 30) -> RefreshToken:
        """Crea nuovo refresh token.

        Args:
            db: Database session
            user_id: ID utente
            expires_days: Giorni validità (default 30)

        Returns:
            RefreshToken: Token creato
        """
        token_string = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        refresh_token = RefreshToken(token=token_string, user_id=user_id, expires_at=expires_at)

        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)

        return refresh_token

    @staticmethod
    def get_by_token(db: Session, token: str) -> RefreshToken | None:
        """Get refresh token by token string."""
        return db.query(RefreshToken).filter(RefreshToken.token == token).first()

    @staticmethod
    def validate_refresh_token(db: Session, token: str) -> RefreshToken | None:
        """Valida refresh token.

        Returns:
            RefreshToken se valido, None altrimenti
        """
        refresh_token = RefreshTokenService.get_by_token(db, token)

        if not refresh_token:
            return None

        if not refresh_token.is_valid:
            return None

        return refresh_token

    @staticmethod
    def revoke_token(db: Session, token: str, replaced_by: str = None) -> bool:
        """Revoca refresh token.

        Args:
            db: Database session
            token: Token da revocare
            replaced_by: Nuovo token (per rotation)

        Returns:
            bool: True se revocato con successo
        """
        refresh_token = RefreshTokenService.get_by_token(db, token)

        if not refresh_token:
            return False

        refresh_token.revoked = True
        refresh_token.revoked_at = datetime.now(timezone.utc)

        if replaced_by:
            refresh_token.replaced_by_token = replaced_by

        db.commit()
        return True

    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> int:
        """Revoca tutti i refresh token di un utente.
        Utile per logout globale o security breach.

        Returns:
            int: Numero di token revocati
        """
        tokens = (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, not RefreshToken.revoked)
            .all()
        )

        count = 0
        for token in tokens:
            token.revoked = True
            token.revoked_at = datetime.now(timezone.utc)
            count += 1

        db.commit()
        return count

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Cleanup tokens scaduti.
        Da eseguire periodicamente (cron job).

        Returns:
            int: Numero di token eliminati
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)  # Mantieni 90 giorni

        deleted = db.query(RefreshToken).filter(RefreshToken.expires_at < cutoff_date).delete()

        db.commit()
        return deleted

    @staticmethod
    def rotate_token(db: Session, old_token: str, user_id: int) -> RefreshToken | None:
        """Token rotation: revoca vecchio token e crea nuovo.

        SECURITY BEST PRACTICE: Previene token replay attacks.

        Args:
            db: Database session
            old_token: Token da sostituire
            user_id: ID utente

        Returns:
            RefreshToken: Nuovo token o None se fallito
        """
        # Valida vecchio token
        old_refresh_token = RefreshTokenService.validate_refresh_token(db, old_token)

        if not old_refresh_token or old_refresh_token.user_id != user_id:
            return None

        # Crea nuovo token
        new_refresh_token = RefreshTokenService.create_refresh_token(db, user_id)

        # Revoca vecchio token
        RefreshTokenService.revoke_token(db, old_token, replaced_by=new_refresh_token.token)

        return new_refresh_token

def create_tokens_for_user(db: Session, user_id: int, email: str) -> dict:
    """Helper per creare access + refresh token.

    Returns:
        dict: {
            "access_token": str,
            "refresh_token": str,
            "token_type": "bearer",
            "expires_in": int (seconds)
        }
    """
    # Import locally to avoid circular import
    from app.domain.auth.services import create_access_token
    from app.core.config import settings

    # Access token (7 days for persistent login)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )

    # Refresh token (long-lived)
    refresh_token = RefreshTokenService.create_refresh_token(db, user_id, expires_days=30)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # convert to seconds
    }
