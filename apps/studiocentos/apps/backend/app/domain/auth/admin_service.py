"""
Admin Authentication Service
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import json

from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    PasswordValidator,
    generate_2fa_secret,
    verify_2fa_token,
    login_rate_limiter
)
from .admin_models import AdminUser, AdminSession, AdminAuditLog
from .admin_schemas import (
    AdminLoginResponse,
    Admin2FASetupResponse,
    AdminProfileResponse
)


class AdminAuthService:
    """Servizio autenticazione amministratori."""

    SETUP_TOKEN_EXPIRY_HOURS = 24
    RESET_TOKEN_EXPIRY_HOURS = 1
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    @staticmethod
    def create_setup_token() -> str:
        """Genera token per setup iniziale."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_or_create_admin_user(db: Session, email: str) -> AdminUser:
        """
        Ottiene o crea l'utente admin (per primo setup).
        """
        stmt = select(AdminUser).where(AdminUser.email == email)
        admin = db.execute(stmt).scalar_one_or_none()

        if not admin:
            admin = AdminUser(
                email=email,
                password_hash="",  # Verrà impostato al setup
                is_setup_complete=False,
                setup_token=AdminAuthService.create_setup_token()
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        return admin

    @staticmethod
    def setup_password(
        db: Session,
        email: str,
        password: str,
        setup_token: str
    ) -> AdminUser:
        """
        Setup password iniziale admin.
        """
        # Valida password
        is_valid, error = PasswordValidator.validate(password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        # Trova admin
        stmt = select(AdminUser).where(AdminUser.email == email)
        admin = db.execute(stmt).scalar_one_or_none()

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amministratore non trovato"
            )

        if admin.is_setup_complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Setup già completato"
            )

        if admin.setup_token != setup_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token di setup non valido"
            )

        # Imposta password
        admin.password_hash = hash_password(password)
        admin.is_setup_complete = True
        admin.setup_token = None
        admin.last_password_change = datetime.utcnow()
        admin.is_active = True

        db.commit()
        db.refresh(admin)

        # Log audit
        AdminAuthService._log_audit(
            db, admin.id, "admin_setup_complete",
            details={"email": email}
        )

        return admin

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
        totp_token: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> AdminLoginResponse:
        """
        Login amministratore con rate limiting e 2FA.
        """
        # Rate limiting
        if not login_rate_limiter.is_allowed(email):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Troppi tentativi di login. Riprova tra 5 minuti."
            )

        # Trova admin
        stmt = select(AdminUser).where(AdminUser.email == email)
        admin = db.execute(stmt).scalar_one_or_none()

        if not admin or not admin.is_setup_complete:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide"
            )

        # Check lockout
        if admin.locked_until and admin.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account bloccato fino a {admin.locked_until.isoformat()}"
            )

        # Verifica password
        if not verify_password(password, admin.password_hash):
            admin.failed_login_attempts += 1

            if admin.failed_login_attempts >= AdminAuthService.MAX_FAILED_ATTEMPTS:
                admin.locked_until = datetime.utcnow() + timedelta(
                    minutes=AdminAuthService.LOCKOUT_DURATION_MINUTES
                )

            db.commit()

            AdminAuthService._log_audit(
                db, admin.id, "admin_login_failed",
                success=False,
                details={"email": email, "ip": ip_address}
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide"
            )

        # Verifica 2FA se abilitato
        if admin.is_2fa_enabled:
            if not totp_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token 2FA richiesto"
                )

            if not verify_2fa_token(admin.totp_secret, totp_token):
                AdminAuthService._log_audit(
                    db, admin.id, "admin_2fa_failed",
                    success=False,
                    details={"email": email}
                )

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token 2FA non valido"
                )

        # Reset failed attempts
        admin.failed_login_attempts = 0
        admin.locked_until = None
        admin.last_login = datetime.utcnow()

        # Crea tokens
        access_token_jti = secrets.token_urlsafe(16)
        refresh_token_jti = secrets.token_urlsafe(16)

        access_token = create_access_token(
            data={
                "sub": str(admin.id),
                "email": admin.email,
                "role": "admin",  # Aggiungo role per compatibilità
                "jti": access_token_jti
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": str(admin.id),
                "email": admin.email,
                "type": "admin",
                "jti": refresh_token_jti
            }
        )

        # Salva sessione
        session = AdminSession(
            admin_id=admin.id,
            access_token_jti=access_token_jti,
            refresh_token_jti=refresh_token_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(session)

        db.commit()

        # Log audit
        AdminAuthService._log_audit(
            db, admin.id, "admin_login_success",
            details={"email": email, "ip": ip_address}
        )

        # Reset rate limiter
        login_rate_limiter.reset(email)

        return AdminLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=604800,  # 7 days in seconds
            admin_email=admin.email,
            requires_2fa=admin.is_2fa_enabled
        )

    @staticmethod
    def change_password(
        db: Session,
        admin_id: int,
        current_password: str,
        new_password: str
    ) -> AdminUser:
        """Cambio password admin."""
        admin = db.get(AdminUser, admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amministratore non trovato"
            )

        # Verifica password attuale
        if not verify_password(current_password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password attuale non corretta"
            )

        # Valida nuova password
        is_valid, error = PasswordValidator.validate(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        # Aggiorna password
        admin.password_hash = hash_password(new_password)
        admin.last_password_change = datetime.utcnow()

        db.commit()
        db.refresh(admin)

        # Log audit
        AdminAuthService._log_audit(
            db, admin.id, "admin_password_changed"
        )

        return admin

    @staticmethod
    def setup_2fa(db: Session, admin_id: int) -> Admin2FASetupResponse:
        """Setup 2FA per admin."""
        admin = db.get(AdminUser, admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amministratore non trovato"
            )

        # Genera secret
        secret = generate_2fa_secret()

        # Genera backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(10)]

        # Salva (non ancora abilitato)
        admin.totp_secret = secret
        admin.backup_codes = json.dumps(backup_codes)

        db.commit()

        # Genera QR code URL
        import pyotp
        totp = pyotp.TOTP(secret)
        qr_url = totp.provisioning_uri(
            name=admin.email,
            issuer_name="StudiocentOS Admin"
        )

        return Admin2FASetupResponse(
            secret=secret,
            qr_code_url=qr_url,
            backup_codes=backup_codes
        )

    @staticmethod
    def enable_2fa(db: Session, admin_id: int, totp_token: str) -> AdminUser:
        """Abilita 2FA dopo verifica token."""
        admin = db.get(AdminUser, admin_id)
        if not admin or not admin.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Setup 2FA non completato"
            )

        # Verifica token
        if not verify_2fa_token(admin.totp_secret, totp_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 2FA non valido"
            )

        admin.is_2fa_enabled = True
        db.commit()
        db.refresh(admin)

        # Log audit
        AdminAuthService._log_audit(
            db, admin.id, "admin_2fa_enabled"
        )

        return admin

    @staticmethod
    def _log_audit(
        db: Session,
        admin_id: int,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log azione audit."""
        log = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            success=success,
            error_message=error_message
        )
        db.add(log)
        db.commit()

    @staticmethod
    def get_or_create_google_admin(
        db: Session,
        google_email: str,
        google_id: str,
        google_name: str,
        access_token: str,
        refresh_token: Optional[str] = None
    ) -> AdminUser:
        """
        Ottieni o crea admin usando Google OAuth.

        Args:
            db: Database session
            google_email: Email Google (es. studiocentos089@gmail.com)
            google_id: Google user ID
            google_name: Nome completo da Google
            access_token: Google access token
            refresh_token: Google refresh token

        Returns:
            AdminUser object
        """
        from app.domain.google.models import AdminGoogleSettings

        # Cerca admin esistente con questo Google ID
        stmt = select(AdminUser).join(
            AdminGoogleSettings,
            AdminGoogleSettings.admin_id == AdminUser.id
        ).where(AdminGoogleSettings.google_user_id == google_id)

        admin = db.execute(stmt).scalar_one_or_none()

        if not admin:
            # Crea nuovo admin se non esiste
            admin = AdminUser(
                email=google_email,
                full_name=google_name or "Admin",
                password_hash="",  # Nessuna password, solo Google OAuth
                is_active=True,
                is_setup_complete=True,  # OAuth login completa il setup
                setup_token=None
            )
            db.add(admin)
            db.flush()

        # Aggiorna/crea Google settings
        google_settings = db.query(AdminGoogleSettings).filter(
            AdminGoogleSettings.admin_id == admin.id
        ).first()

        if not google_settings:
            google_settings = AdminGoogleSettings(
                admin_id=admin.id,
                google_user_id=google_id,
                access_token=access_token,
                refresh_token=refresh_token,
                scopes="openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/business.manage https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/calendar.events"
            )
            db.add(google_settings)
        else:
            google_settings.access_token = access_token
            if refresh_token:
                google_settings.refresh_token = refresh_token
            google_settings.google_user_id = google_id

        # Aggiorna last login
        admin.last_login = datetime.utcnow()

        db.commit()
        db.refresh(admin)

        return admin

    @staticmethod
    def create_admin_session(db: Session, admin: AdminUser) -> AdminLoginResponse:
        """
        Crea sessione admin e genera JWT tokens.

        Args:
            db: Database session
            admin: AdminUser object

        Returns:
            AdminLoginResponse con access_token e refresh_token
        """
        # Generate tokens
        from uuid import uuid4
        access_jti = str(uuid4())
        refresh_jti = str(uuid4())

        access_token = create_access_token(
            data={"sub": str(admin.id), "type": "access", "role": "admin", "jti": access_jti}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(admin.id), "type": "refresh", "role": "admin", "jti": refresh_jti}
        )        # Create session with JTI
        from datetime import timedelta
        session = AdminSession(
            admin_id=admin.id,
            access_token_jti=access_jti,
            refresh_token_jti=refresh_jti,
            expires_at=datetime.utcnow() + timedelta(days=7),
            ip_address=None,
            user_agent=None
        )
        db.add(session)
        db.commit()

        return AdminLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 ora in secondi
            admin_email=admin.email,
            requires_2fa=False
        )
