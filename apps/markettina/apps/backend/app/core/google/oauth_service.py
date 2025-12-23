"""
Google OAuth Service - Unified Authentication Flow

SINGLE POINT OF ENTRY per tutti i flussi OAuth Google.
Sostituisce le implementazioni frammentate in:
- domain/auth/google_oauth.py
- domain/google/router.py
- integrations/google_meet.py
- services/calendar_service.py

Usage:
    from app.core.google import google_oauth_service, GOOGLE_SCOPE_SETS

    # Login Customer
    auth_url = google_oauth_service.get_auth_url(
        use_case="customer",
        state="csrf_token",
        redirect_uri="http://example.com/callback"
    )

    # Admin full integration
    auth_url = google_oauth_service.get_auth_url(
        use_case="admin_full",
        state="csrf_token",
        redirect_uri="http://example.com/admin/callback"
    )
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from app.core.config import settings

from .scopes import GOOGLE_SCOPE_SETS, get_scopes_for_use_case

logger = logging.getLogger(__name__)

# Google OAuth2 endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class GoogleTokenResponse(BaseModel):
    """Risposta dal token exchange."""
    access_token: str
    refresh_token: str | None = None
    expires_in: int = 3600
    scope: str = ""
    token_type: str = "Bearer"
    id_token: str | None = None

    @property
    def expires_at(self) -> datetime:
        return datetime.now(UTC) + timedelta(seconds=self.expires_in)


class GoogleUserInfo(BaseModel):
    """Info utente da Google."""
    id: str
    email: str
    verified_email: bool = False
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None
    locale: str | None = None


class GoogleOAuthService:
    """
    Servizio OAuth Google unificato.

    Gestisce:
    - Generazione URL autorizzazione con scope corretti
    - Exchange authorization code per token
    - Fetch user info
    - Token refresh
    """

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
    ):
        self.client_id = client_id or settings.GOOGLE_CLIENT_ID
        self.client_secret = client_secret or settings.GOOGLE_CLIENT_SECRET

        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured")

    def get_auth_url(
        self,
        redirect_uri: str,
        use_case: str = "customer",
        state: str | None = None,
        custom_scopes: list[str] | None = None,
        login_hint: str | None = None,
        prompt: str = "consent",
    ) -> str:
        """
        Genera URL di autorizzazione Google.

        Args:
            redirect_uri: URL callback dopo auth
            use_case: Caso d'uso (chiave di GOOGLE_SCOPE_SETS)
            state: CSRF token (generato automaticamente se None)
            custom_scopes: Override scope (usa use_case se None)
            login_hint: Email suggerita per login
            prompt: Tipo di prompt ("consent", "select_account", "none")

        Returns:
            URL completo per redirect a Google

        Example:
            >>> url = service.get_auth_url(
            ...     redirect_uri="http://localhost:8000/callback",
            ...     use_case="admin_full",
            ...     state="my_csrf_token"
            ... )
        """
        # Determina scope
        if custom_scopes:
            scopes = custom_scopes
        else:
            scopes = get_scopes_for_use_case(use_case)

        # Genera state se non fornito
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "response_type": "code",
            "state": state,
            "access_type": "offline",  # Per ottenere refresh token
            "prompt": prompt,  # Force consent per refresh token
        }

        if login_hint:
            params["login_hint"] = login_hint

        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> GoogleTokenResponse | None:
        """
        Scambia authorization code per access/refresh token.

        Args:
            code: Authorization code da Google callback
            redirect_uri: Stesso redirect_uri usato in get_auth_url

        Returns:
            GoogleTokenResponse con tutti i token
            None se exchange fallito
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GOOGLE_TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                return GoogleTokenResponse(**data)

        except Exception as e:
            logger.error(f"Token exchange error: {e}", exc_info=True)
            return None

    async def get_user_info(
        self,
        access_token: str,
    ) -> GoogleUserInfo | None:
        """
        Ottieni info utente da Google.

        Args:
            access_token: Access token valido

        Returns:
            GoogleUserInfo con dati utente
            None se richiesta fallita
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    logger.error(f"User info fetch failed: {response.status_code}")
                    return None

                data = response.json()
                return GoogleUserInfo(**data)

        except Exception as e:
            logger.error(f"User info fetch error: {e}", exc_info=True)
            return None

    async def refresh_token(
        self,
        refresh_token: str,
    ) -> GoogleTokenResponse | None:
        """
        Refresh access token.

        Args:
            refresh_token: Refresh token

        Returns:
            GoogleTokenResponse con nuovo access_token
            None se refresh fallito
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GOOGLE_TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.status_code}")
                    return None

                data = response.json()
                # Refresh response doesn't include refresh_token
                data["refresh_token"] = refresh_token
                return GoogleTokenResponse(**data)

        except Exception as e:
            logger.error(f"Token refresh error: {e}", exc_info=True)
            return None

    def generate_csrf_state(
        self,
        extra_data: str | None = None,
    ) -> str:
        """
        Genera token CSRF per OAuth state.

        Args:
            extra_data: Dati extra da includere (es: admin_id)

        Returns:
            State token (formato: "random:extra" se extra_data)
        """
        random_part = secrets.token_urlsafe(32)

        if extra_data:
            return f"{random_part}:{extra_data}"

        return random_part

    def parse_csrf_state(
        self,
        state: str,
    ) -> dict[str, str]:
        """
        Parse state token per estrarre dati.

        Args:
            state: State token da callback

        Returns:
            Dict con "token" e opzionale "extra"
        """
        if ":" in state:
            parts = state.split(":", 1)
            return {"token": parts[0], "extra": parts[1]}

        return {"token": state, "extra": None}

    def get_default_redirect_uri(
        self,
        user_type: str = "customer",
    ) -> str:
        """
        Ottieni redirect URI di default per tipo utente.

        Args:
            user_type: "customer", "admin", o "admin_login"

        Returns:
            Redirect URI configurato

        IMPORTANT: Tutti devono essere registrati nella Google Cloud Console!
        - Customer: {BASE_URL}/api/v1/auth/google/callback
        - Admin: {BASE_URL}/api/v1/admin/google/callback
        - Admin Login: {BASE_URL}/api/v1/admin/auth/google/callback
        """
        base_url = settings.BASE_URL or settings.BACKEND_URL or "http://localhost:8000"

        if user_type == "admin":
            return f"{base_url}/api/v1/admin/google/callback"
        if user_type == "admin_login":
            return f"{base_url}/api/v1/admin/auth/google/callback"
        # Customer callback - NON usare GOOGLE_REDIRECT_URI che potrebbe essere l'admin
        return f"{base_url}/api/v1/auth/google/callback"

    def is_configured(self) -> bool:
        """Check se OAuth è configurato."""
        return bool(self.client_id and self.client_secret)

    def get_supported_scopes(self) -> dict[str, list[str]]:
        """Ritorna tutti i set di scope supportati."""
        return GOOGLE_SCOPE_SETS.copy()


# Singleton instance
google_oauth_service = GoogleOAuthService()
