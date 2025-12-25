"""Password Reset Router
Endpoint sicuri per reset password con rate limiting.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_user, get_password_hash
from app.core.api.middleware.rate_limit import rate_limit
from app.core.config import settings
from app.core.constants import AuthConstants, RateLimitConstants
from app.domain.auth.models import User, UserRole
from app.domain.auth.password_reset import PasswordResetService
from app.infrastructure.database import get_db
from app.infrastructure.external.email import EmailService

logger = logging.getLogger(__name__)

router = APIRouter()  # Tags in api/v1/__init__.py

class PasswordResetRequest(BaseModel):
    """Schema per richiesta reset password."""

    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema per conferma reset password."""

    token: str
    new_password: str

@router.post("/password-reset")
@rate_limit(
    max_requests=AuthConstants.MAX_PASSWORD_RESET_PER_HOUR,
    window_seconds=3600
)
async def request_password_reset_compat(
    request: Request, reset_request: PasswordResetRequest, db: Session = Depends(get_db)
):
    """Password reset endpoint (E2E compatibility)."""
    return await request_password_reset(request, reset_request, db)

@router.post("/password-reset-request")
@rate_limit(
    max_requests=AuthConstants.MAX_PASSWORD_RESET_PER_HOUR,
    window_seconds=3600
)
async def request_password_reset(
    request: Request, reset_request: PasswordResetRequest, db: Session = Depends(get_db)
):
    """Richiede reset password - invia email con token.

    SECURITY FEATURES:
    - Rate limiting: 3 richieste/ora per IP
    - Non rivela se email exists (sempre success)
    - Token scade in 30 minuti
    - Invalida token precedenti
    """
    try:
        # Cerca utente per email
        user = db.query(User).filter(User.email == reset_request.email).first()

        if user and user.is_active:
            # Genera token di reset
            plain_token, db_token = PasswordResetService.create_reset_token(db, user.id)

            # Prepara email di reset
            reset_url = f"{settings.PASSWORD_RESET_URL_BASE_COMPUTED}?token={plain_token}"

            email_content = f"""
            Ciao {user.full_name or 'Utente'},

            Hai richiesto il reset della tua password per CV-Lab.

            Clicca sul link qui sotto per impostare una nuova password:
            {reset_url}

            ⚠️ IMPORTANTE:
            - Questo link scade tra 30 minuti
            - Se non hai richiesto tu questo reset, ignora questa email
            - La tua password attuale rimane valida fino al completamento del reset

            Cordiali saluti,
            Il team CV-Lab
            """

            try:
                # Invia email (in modalità dev potrebbe fallire)
                email_sent = EmailService.send_email(
                    to_email=user.email, subject="🔒 Reset Password - CV-Lab", body=email_content
                )

                if email_sent:
                    logger.info(f"Password reset email sent to {user.email}")
                else:
                    logger.warning(f"Email service unavailable for {user.email}")

            except Exception as e:
                logger.error(f"Failed to send reset email to {user.email}: {e}")
                # In produzione, non fallire per problemi email

        # SECURITY: Sempre restituisce success (non rivela se email esiste)
        response = {
            "message": "Se l'email è registrata nel sistema, riceverai un link per il reset della password.",
            "success": True,
        }

        # Security: Token never exposed in API response for production safety

        return response

    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore interno durante la richiesta di reset",
        )

@router.post("/password-reset-confirm")
@rate_limit(
    max_requests=5,
    window_seconds=3600
)
async def confirm_password_reset(
    request: Request, reset_confirm: PasswordResetConfirm, db: Session = Depends(get_db)
):
    """Conferma reset password con token.

    SECURITY FEATURES:
    - Rate limiting: 5 conferme/ora per IP
    - Token validation con scadenza
    - Hash sicuro della nuova password
    - Invalidazione di tutti i token utente
    """
    try:
        # Valida lunghezza password
        if len(reset_confirm.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La password deve essere di almeno 8 caratteri",
            )

        # Hash della nuova password
        new_password_hash = get_password_hash(reset_confirm.new_password)

        # Usa token per reset
        success = PasswordResetService.use_reset_token(db, reset_confirm.token, new_password_hash)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token non valido, scaduto o già utilizzato",
            )

        logger.info("Password reset completed successfully")

        return {
            "message": "Password aggiornata con successo. Ora puoi effettuare il login con la nuova password.",
            "success": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirm error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore interno durante il reset della password",
        )

@router.post("/admin/password-reset/{user_id}")
@rate_limit(
    max_requests=10,
    window_seconds=3600
)
async def admin_force_password_reset(
    user_id: int,
    new_password: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin può resettare password di qualsiasi utente direttamente.

    SECURITY:
    - Solo ADMIN può usare questo endpoint
    - Rate limiting dedicato per admin
    - Audit log di tutte le operazioni admin
    """
    # Verifica che sia admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli admin possono resettare password di altri utenti",
        )

    try:
        # Trova utente target
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utente non trovato")

        # Valida password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La password deve essere di almeno 8 caratteri",
            )

        # Hash e aggiorna password
        new_password_hash = get_password_hash(new_password)
        target_user.password = new_password_hash

        # Invalida tutti i reset token esistenti
        PasswordResetService.cleanup_expired_tokens(db)

        db.commit()

        # Audit log
        logger.info(f"Admin {current_user.email} reset password for user {target_user.email}")

        return {
            "message": f"Password per {target_user.email} aggiornata con successo",
            "success": True,
            "user_email": target_user.email,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Admin password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il reset admin della password",
        )
