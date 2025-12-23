"""
Google Token Manager - Unified Token Storage & Refresh

Gestisce TUTTI i token Google per Customer e Admin in modo unificato.
Supporta auto-refresh dei token scaduti.

ARCHITECTURAL DECISION:
Prima c'erano 2 storage separati:
- OAuthToken (oauth_tokens.py) → Customer
- AdminGoogleSettings → Admin

Questo manager unifica l'accesso, mantenendo compatibilità con entrambi.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings


logger = logging.getLogger(__name__)

# Google OAuth2 endpoints
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class GoogleTokenManager:
    """
    Gestione centralizzata dei token Google OAuth.

    Supporta:
    - Token refresh automatico
    - Validazione token
    - Revoca token
    - Storage unificato per Customer e Admin
    """

    # Buffer per refresh preventivo (5 minuti prima della scadenza)
    REFRESH_BUFFER_MINUTES = 5

    def __init__(self, db: Session):
        self.db = db

    async def get_valid_token(
        self,
        user_id: Optional[int] = None,
        admin_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Ottieni un token valido (refresh se necessario).

        Args:
            user_id: ID utente (Customer)
            admin_id: ID admin

        Returns:
            Dict con access_token, refresh_token, expires_at, scopes
            None se non trovato o refresh fallito
        """
        if admin_id:
            return await self._get_admin_token(admin_id)
        elif user_id:
            return await self._get_customer_token(user_id)
        else:
            raise ValueError("Either user_id or admin_id must be provided")

    async def _get_admin_token(self, admin_id: int) -> Optional[Dict[str, Any]]:
        """Ottieni token Admin da AdminGoogleSettings."""
        from app.domain.google.models import AdminGoogleSettings

        google_settings = self.db.query(AdminGoogleSettings).filter(
            AdminGoogleSettings.admin_id == admin_id
        ).first()

        if not google_settings or not google_settings.access_token:
            return None

        # Check if token needs refresh
        if self._needs_refresh(google_settings.token_expires_at):
            if google_settings.refresh_token:
                refreshed = await self.refresh_token(google_settings.refresh_token)
                if refreshed:
                    # Update stored token
                    google_settings.access_token = refreshed["access_token"]
                    google_settings.token_expires_at = refreshed["expires_at"]
                    google_settings.updated_at = datetime.now(timezone.utc)
                    self.db.commit()

                    return {
                        "access_token": refreshed["access_token"],
                        "refresh_token": google_settings.refresh_token,
                        "expires_at": refreshed["expires_at"],
                        "scopes": google_settings.scopes,
                    }

            logger.warning(f"Token expired and refresh failed for admin {admin_id}")
            return None

        return {
            "access_token": google_settings.access_token,
            "refresh_token": google_settings.refresh_token,
            "expires_at": google_settings.token_expires_at,
            "scopes": google_settings.scopes,
        }

    async def _get_customer_token(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Ottieni token Customer da OAuthToken."""
        from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider

        token = OAuthTokenService.get_oauth_token(
            self.db, user_id, OAuthProvider.GOOGLE
        )

        if not token:
            return None

        # Check if token needs refresh
        if self._needs_refresh(token.expires_at):
            if token.refresh_token:
                refreshed = await self.refresh_token(token.refresh_token)
                if refreshed:
                    # Update stored token
                    OAuthTokenService.save_oauth_token(
                        db=self.db,
                        user_id=user_id,
                        provider=OAuthProvider.GOOGLE,
                        access_token=refreshed["access_token"],
                        refresh_token=token.refresh_token,
                        expires_in=refreshed.get("expires_in", 3600),
                        scope=token.scope,
                        token_type=token.token_type
                    )

                    return {
                        "access_token": refreshed["access_token"],
                        "refresh_token": token.refresh_token,
                        "expires_at": refreshed["expires_at"],
                        "scopes": token.scope,
                    }

            logger.warning(f"Token expired and refresh failed for user {user_id}")
            return None

        return {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "expires_at": token.expires_at,
            "scopes": token.scope,
        }

    def _needs_refresh(self, expires_at: Optional[datetime]) -> bool:
        """Check if token needs refresh (with buffer)."""
        if not expires_at:
            return False

        buffer = timedelta(minutes=self.REFRESH_BUFFER_MINUTES)
        return datetime.now(timezone.utc) >= (expires_at - buffer)

    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh Google OAuth token.

        Args:
            refresh_token: Refresh token

        Returns:
            Dict con nuovo access_token e expires_at
            None se refresh fallito
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GOOGLE_TOKEN_URL,
                    data={
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    return None

                data = response.json()
                expires_in = data.get("expires_in", 3600)

                return {
                    "access_token": data["access_token"],
                    "expires_at": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
                    "expires_in": expires_in,
                }

        except Exception as e:
            logger.error(f"Token refresh error: {e}", exc_info=True)
            return None

    async def revoke_token(self, token: str) -> bool:
        """
        Revoca un token Google (logout completo).

        Args:
            token: Access token o refresh token da revocare

        Returns:
            True se revocato con successo
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GOOGLE_REVOKE_URL,
                    params={"token": token},
                    timeout=30.0
                )

                if response.status_code == 200:
                    logger.info("Token revoked successfully")
                    return True
                else:
                    logger.warning(f"Token revocation returned {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Token revocation error: {e}", exc_info=True)
            return False

    async def validate_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Valida un token e ottieni info utente.

        Args:
            access_token: Token da validare

        Returns:
            Dict con user info se valido, None altrimenti
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Token validation failed: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Token validation error: {e}", exc_info=True)
            return None

    async def save_admin_token(
        self,
        admin_id: int,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: int,
        scopes: str,
    ) -> bool:
        """
        Salva token Admin in AdminGoogleSettings.

        Returns:
            True se salvato con successo
        """
        from app.domain.google.models import AdminGoogleSettings

        try:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            google_settings = self.db.query(AdminGoogleSettings).filter(
                AdminGoogleSettings.admin_id == admin_id
            ).first()

            if not google_settings:
                google_settings = AdminGoogleSettings(admin_id=admin_id)
                self.db.add(google_settings)

            google_settings.access_token = access_token
            if refresh_token:
                google_settings.refresh_token = refresh_token
            google_settings.token_expires_at = expires_at
            google_settings.scopes = scopes
            google_settings.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            logger.info(f"Saved Google token for admin {admin_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save admin token: {e}", exc_info=True)
            self.db.rollback()
            return False

    async def save_customer_token(
        self,
        user_id: int,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: int,
        scopes: str,
    ) -> bool:
        """
        Salva token Customer in OAuthToken.

        Returns:
            True se salvato con successo
        """
        from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider

        try:
            OAuthTokenService.save_oauth_token(
                db=self.db,
                user_id=user_id,
                provider=OAuthProvider.GOOGLE,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                scope=scopes,
                token_type="Bearer"
            )
            logger.info(f"Saved Google token for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save customer token: {e}", exc_info=True)
            return False

    def has_scope(
        self,
        granted_scopes: str,
        required_scope: str,
    ) -> bool:
        """
        Verifica se uno scope specifico è stato concesso.

        Args:
            granted_scopes: Stringa di scope (separati da spazio)
            required_scope: Scope da verificare

        Returns:
            True se lo scope è presente
        """
        if not granted_scopes:
            return False

        # Check both full URL and short form
        scopes_list = granted_scopes.split()

        # Direct match
        if required_scope in scopes_list:
            return True

        # Partial match (e.g., "analytics.readonly" in full URL)
        for scope in scopes_list:
            if required_scope in scope:
                return True

        return False
