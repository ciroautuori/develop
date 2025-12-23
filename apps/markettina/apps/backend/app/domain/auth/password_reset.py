"""
Sistema sicuro per reset password con token temporanei.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.domain.auth.models import User

class PasswordResetToken(Base):
    """Token per reset password con scadenza e sicurezza."""

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String, nullable=False, unique=True)  # Hashed token per sicurezza
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="password_reset_tokens")

class PasswordResetService:
    """Service per gestione sicura reset password."""

    @staticmethod
    def generate_reset_token() -> str:
        """Genera token sicuro per reset."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash del token per storage sicuro."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def create_reset_token(db: Session, user_id: int) -> tuple[str, PasswordResetToken]:
        """Crea nuovo token di reset per utente.

        Returns:
            tuple: (plain_token, db_token_record)
        """
        # Invalida tutti i token esistenti per questo utente
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id, not PasswordResetToken.is_used
        ).update({"is_used": True, "used_at": datetime.now(UTC)})

        # Genera nuovo token
        plain_token = PasswordResetService.generate_reset_token()
        token_hash = PasswordResetService.hash_token(plain_token)

        # Scadenza: 30 minuti
        expires_at = datetime.now(UTC) + timedelta(minutes=30)

        # Crea record nel database
        db_token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)

        db.add(db_token)
        db.commit()
        db.refresh(db_token)

        return plain_token, db_token

    @staticmethod
    def validate_reset_token(db: Session, token: str) -> PasswordResetToken | None:
        """Valida token di reset.

        Returns:
            PasswordResetToken se valido, None altrimenti
        """
        token_hash = PasswordResetService.hash_token(token)

        db_token = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
                not PasswordResetToken.is_used,
                PasswordResetToken.expires_at > datetime.now(UTC),
            )
            .first()
        )

        return db_token

    @staticmethod
    def use_reset_token(db: Session, token: str, new_password_hash: str) -> bool:
        """Usa token per reset password.

        Returns:
            bool: True se successo, False altrimenti
        """
        db_token = PasswordResetService.validate_reset_token(db, token)

        if not db_token:
            return False

        # Aggiorna password utente
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            return False

        user.password = new_password_hash

        # Marca token come usato
        db_token.is_used = True
        db_token.used_at = datetime.now(UTC)

        # Invalida tutti gli altri token dell'utente
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == db_token.user_id,
            PasswordResetToken.id != db_token.id,
            not PasswordResetToken.is_used,
        ).update({"is_used": True, "used_at": datetime.now(UTC)})

        db.commit()
        return True

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Pulisce token scaduti.

        Returns:
            int: Numero di token rimossi
        """
        expired_count = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.expires_at < datetime.now(UTC))
            .count()
        )

        db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.now(UTC)
        ).delete()

        db.commit()
        return expired_count
