"""
Admin Authentication Router
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.infrastructure.database.session import get_db

from .admin_models import AdminUser
from .admin_schemas import (
    Admin2FAEnableRequest,
    Admin2FASetupResponse,
    AdminChangePasswordRequest,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminProfileResponse,
    AdminRefreshTokenRequest,
    AdminSetupPasswordRequest,
)
from .admin_service import AdminAuthService

router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"])


@router.post("/setup", response_model=AdminProfileResponse)
def setup_admin_password(
    request: AdminSetupPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Setup password iniziale amministratore.

    Questo endpoint viene usato solo al primo avvio del sistema.
    Richiede il token di setup generato automaticamente.
    """
    admin = AdminAuthService.setup_password(
        db=db,
        email=request.email,
        password=request.password,
        setup_token=request.setup_token
    )

    return AdminProfileResponse(
        id=admin.id,
        email=admin.email,
        full_name=admin.full_name,
        is_2fa_enabled=admin.is_2fa_enabled,
        created_at=admin.created_at.isoformat(),
        last_login=admin.last_login.isoformat() if admin.last_login else None
    )


@router.post("/login", response_model=AdminLoginResponse)
def login_admin(
    request: AdminLoginRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Login amministratore con email/password.

    - Rate limiting: max 5 tentativi ogni 5 minuti
    - Lockout automatico dopo 5 tentativi falliti
    - Supporto 2FA opzionale

    DEPRECATO: Usa /auth/google/login per autenticazione Google OAuth
    """
    ip_address = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent")

    return AdminAuthService.login(
        db=db,
        email=request.email,
        password=request.password,
        totp_token=request.totp_token,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.get("/google/login")
async def google_login_redirect(db: Session = Depends(get_db)):
    """
    Inizia Google OAuth login flow per amministratori.

    Redirect a Google per autenticazione con markettina089@gmail.com.
    Dopo il login, Google reindirizza a /auth/google/callback.
    """
    from app.core.google.oauth_service import google_oauth_service

    # Generate CSRF state
    state = google_oauth_service.generate_csrf_state(extra_data="admin_login")

    # Build redirect URI for admin login
    redirect_uri = google_oauth_service.get_default_redirect_uri("admin_login")

    # Generate auth URL with admin scopes
    google_auth_url = google_oauth_service.get_auth_url(
        redirect_uri=redirect_uri,
        use_case="admin_full",
        state=state,
    )

    return {"auth_url": google_auth_url, "state": state.split(":")[0]}


@router.get("/google/callback")
async def google_login_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """
    Callback Google OAuth per admin login.

    Autentica admin usando Google account (markettina089@gmail.com).
    Crea automaticamente account admin se non esiste.
    """
    import logging

    import httpx
    from fastapi.responses import RedirectResponse

    from app.core.config import settings
    from app.core.google.oauth_service import google_oauth_service

    logger = logging.getLogger(__name__)

    if error:
        logger.error(f"Google OAuth error: {error}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={error}",
            status_code=302
        )

    if not code:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=missing_code",
            status_code=302
        )

    try:
        # Exchange code for tokens
        redirect_uri = google_oauth_service.get_default_redirect_uri("admin_login")
        token_response = await google_oauth_service.exchange_code(
            code=code,
            redirect_uri=redirect_uri
        )

        if not token_response:
            raise ValueError("Token exchange failed")

        # Get user info from Google
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_response.access_token}"}
            )
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()

        google_email = user_info.get("email")
        google_name = user_info.get("name")
        google_id = user_info.get("id")

        # Verifica che sia un'email autorizzata
        allowed_emails = [e.strip() for e in settings.ALLOWED_ADMIN_EMAILS.split(",")]
        if google_email not in allowed_emails:
            logger.warning(f"Unauthorized Google account attempted login: {google_email}")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error=unauthorized_account",
                status_code=302
            )

        # Find or create admin user
        admin = AdminAuthService.get_or_create_google_admin(
            db=db,
            google_email=google_email,
            google_id=google_id,
            google_name=google_name,
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token
        )

        # Generate JWT token
        auth_response = AdminAuthService.create_admin_session(db, admin)

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/admin/login?token={auth_response.access_token}&admin_id={admin.id}",
            status_code=302
        )

    except Exception as e:
        logger.error(f"Google login callback error: {e}", exc_info=True)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=authentication_failed",
            status_code=302
        )


@router.post("/change-password")
def change_admin_password(
    request: AdminChangePasswordRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cambio password amministratore (autenticato).
    """
    AdminAuthService.change_password(
        db=db,
        admin_id=current_admin.id,
        current_password=request.current_password,
        new_password=request.new_password
    )

    return {"message": "Password aggiornata con successo"}


@router.get("/profile", response_model=AdminProfileResponse)
def get_admin_profile(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Ottieni profilo amministratore corrente.
    """
    return AdminProfileResponse(
        id=current_admin.id,
        email=current_admin.email,
        full_name=current_admin.full_name,
        is_2fa_enabled=current_admin.is_2fa_enabled,
        created_at=current_admin.created_at.isoformat(),
        last_login=current_admin.last_login.isoformat() if current_admin.last_login else None
    )


@router.post("/2fa/setup", response_model=Admin2FASetupResponse)
def setup_2fa(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Setup 2FA (TOTP) per amministratore.

    Restituisce:
    - Secret TOTP
    - URL QR code per app authenticator (Google Authenticator, Authy, etc.)
    - Codici di backup (10)
    """
    return AdminAuthService.setup_2fa(db=db, admin_id=current_admin.id)


@router.post("/2fa/enable")
def enable_2fa(
    request: Admin2FAEnableRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Abilita 2FA dopo verifica token.

    Richiede un token valido generato dall'app authenticator
    per confermare che il setup è corretto.
    """
    AdminAuthService.enable_2fa(
        db=db,
        admin_id=current_admin.id,
        totp_token=request.totp_token
    )

    return {"message": "2FA abilitato con successo"}


@router.post("/2fa/disable")
def disable_2fa(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Disabilita 2FA per amministratore.
    """
    current_admin.is_2fa_enabled = False
    current_admin.totp_secret = None
    current_admin.backup_codes = None

    db.commit()

    # Log audit
    AdminAuthService._log_audit(
        db, current_admin.id, "admin_2fa_disabled"
    )

    return {"message": "2FA disabilitato"}


@router.post("/refresh", response_model=AdminLoginResponse)
def refresh_admin_token(
    request: AdminRefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token usando refresh token.
    """
    import secrets

    from app.core.security import create_access_token, decode_token

    # Decodifica refresh token
    try:
        payload = decode_token(request.refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token non valido"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido"
        )

    admin_id = int(payload.get("sub"))
    admin = db.get(AdminUser, admin_id)

    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Amministratore non trovato o disattivato"
        )

    # Crea nuovo access token
    access_token_jti = secrets.token_urlsafe(16)
    access_token = create_access_token(
        data={
            "sub": str(admin.id),
            "email": admin.email,
            "type": "admin",
            "jti": access_token_jti
        }
    )

    return AdminLoginResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Stesso refresh token
        expires_in=604800,  # 7 days in seconds
        admin_email=admin.email,
        requires_2fa=admin.is_2fa_enabled
    )


@router.post("/logout")
def logout_admin(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Logout amministratore (revoca sessione).
    """

    # Per ora solo log audit
    AdminAuthService._log_audit(
        db, current_admin.id, "admin_logout"
    )

    return {"message": "Logout effettuato"}


@router.get("/setup-token")
def get_setup_token(db: Session = Depends(get_db)):
    """
    Ottieni token di setup per primo amministratore.

    ⚠️ QUESTO ENDPOINT DEVE ESSERE PROTETTO IN PRODUZIONE!
    Usare solo per setup iniziale, poi disabilitare.
    """
    # Verifica se esiste già un admin
    from sqlalchemy import select
    stmt = select(AdminUser).where(AdminUser.is_setup_complete == True)
    existing_admin = db.execute(stmt).scalar_one_or_none()

    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Setup già completato"
        )

    # Crea o ottieni admin di default
    admin = AdminAuthService.get_or_create_admin_user(
        db=db,
        email="admin@markettina.it"
    )

    return {
        "email": admin.email,
        "setup_token": admin.setup_token,
        "message": "Usa questo token per completare il setup"
    }
