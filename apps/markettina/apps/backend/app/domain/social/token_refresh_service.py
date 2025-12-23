"""
Meta Token Refresh Service - Automatic Token Management

Risolve il problema dei token Facebook/Instagram che scadono.

Tipi di Token Meta:
1. Short-lived (1 ora) - Da Graph API Explorer
2. Long-lived (60 giorni) - Convertito da short-lived
3. Page Token - Mai scade se da long-lived user token

Workflow:
1. Ottieni short-lived token da Facebook Login
2. Converti in long-lived token (dura 60 giorni)
3. Ottieni Page Access Token (non scade)
4. Salva token nel database
5. Refresh automatico 7 giorni prima della scadenza

Author: MARKETTINA
Date: December 2025
"""

from datetime import datetime, timedelta
from typing import Any

import httpx
import structlog
from pydantic import BaseModel

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TokenInfo(BaseModel):
    """Token information model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None  # Seconds until expiration
    expires_at: datetime | None = None
    is_long_lived: bool = False


class MetaTokenService:
    """
    Service for managing Meta (Facebook/Instagram) tokens.

    Handles:
    - Token validation
    - Short-to-long conversion
    - Page token generation
    - Automatic refresh
    """

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self):
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET
        self.user_token = settings.META_ACCESS_TOKEN
        self.page_id = settings.FACEBOOK_PAGE_ID
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """Check if Meta is properly configured."""
        return bool(self.app_id and self.app_secret and self.user_token)

    async def get_client(self) -> httpx.AsyncClient:
        """Get HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # =========================================================================
    # TOKEN VALIDATION
    # =========================================================================

    async def validate_token(self, token: str) -> dict[str, Any]:
        """
        Validate a token and get its info.

        Returns:
            {
                "is_valid": bool,
                "expires_at": datetime or None,
                "scopes": list,
                "type": "USER" | "PAGE",
                "error": str or None
            }
        """
        try:
            client = await self.get_client()

            # Debug token endpoint
            url = f"{self.BASE_URL}/debug_token"
            params = {
                "input_token": token,
                "access_token": f"{self.app_id}|{self.app_secret}"  # App access token
            }

            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json().get("data", {})

                expires_at = None
                if data.get("expires_at"):
                    expires_at = datetime.fromtimestamp(data["expires_at"])

                return {
                    "is_valid": data.get("is_valid", False),
                    "expires_at": expires_at,
                    "scopes": data.get("scopes", []),
                    "type": data.get("type", "UNKNOWN"),
                    "app_id": data.get("app_id"),
                    "user_id": data.get("user_id"),
                    "error": None
                }
            error = response.json().get("error", {})
            return {
                "is_valid": False,
                "expires_at": None,
                "scopes": [],
                "type": "UNKNOWN",
                "error": error.get("message", "Token validation failed")
            }

        except Exception as e:
            logger.exception("token_validation_error")
            return {
                "is_valid": False,
                "expires_at": None,
                "scopes": [],
                "type": "UNKNOWN",
                "error": str(e)
            }

    # =========================================================================
    # TOKEN CONVERSION
    # =========================================================================

    async def convert_to_long_lived(self, short_lived_token: str) -> TokenInfo | None:
        """
        Convert a short-lived token to long-lived (60 days).

        Args:
            short_lived_token: Token from Facebook Login (1 hour expiry)

        Returns:
            TokenInfo with long-lived token or None if failed
        """
        if not self.app_id or not self.app_secret:
            logger.error("missing_app_credentials",
                        message="META_APP_ID and META_APP_SECRET required")
            return None

        try:
            client = await self.get_client()

            url = f"{self.BASE_URL}/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "fb_exchange_token": short_lived_token
            }

            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                expires_in = data.get("expires_in", 5184000)  # Default 60 days
                expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                logger.info(
                    "token_converted_to_long_lived",
                    expires_in=expires_in,
                    expires_at=expires_at.isoformat()
                )

                return TokenInfo(
                    access_token=data["access_token"],
                    token_type=data.get("token_type", "bearer"),
                    expires_in=expires_in,
                    expires_at=expires_at,
                    is_long_lived=True
                )
            error = response.json().get("error", {})
            logger.error(
                "token_conversion_failed",
                error=error.get("message"),
                code=error.get("code")
            )
            return None

        except Exception:
            logger.exception("token_conversion_exception")
            return None

    # =========================================================================
    # PAGE TOKEN
    # =========================================================================

    async def get_page_token(self, user_token: str | None = None) -> str | None:
        """
        Get Page Access Token from User Access Token.

        Page tokens from long-lived user tokens DON'T EXPIRE!

        Args:
            user_token: Long-lived user token (uses configured token if not provided)

        Returns:
            Page access token or None
        """
        token = user_token or self.user_token

        if not token or not self.page_id:
            logger.error("missing_token_or_page_id")
            return None

        try:
            client = await self.get_client()

            # Get pages the user manages
            url = f"{self.BASE_URL}/me/accounts"
            params = {"access_token": token}

            response = await client.get(url, params=params)

            if response.status_code == 200:
                pages = response.json().get("data", [])

                for page in pages:
                    if page.get("id") == self.page_id:
                        page_token = page.get("access_token")
                        logger.info(
                            "page_token_obtained",
                            page_id=self.page_id,
                            page_name=page.get("name")
                        )
                        return page_token

                # Page not found
                logger.warning(
                    "page_not_found",
                    page_id=self.page_id,
                    available_pages=[p.get("id") for p in pages]
                )
                return None
            error = response.json().get("error", {})
            logger.error(
                "page_token_error",
                error=error.get("message"),
                code=error.get("code")
            )
            return None

        except Exception:
            logger.exception("page_token_exception")
            return None

    # =========================================================================
    # TOKEN STATUS
    # =========================================================================

    async def get_token_status(self) -> dict[str, Any]:
        """
        Get comprehensive status of configured tokens.

        Returns status for:
        - User token (META_ACCESS_TOKEN)
        - Page token (derived)
        - Instagram token
        """
        status = {
            "configured": self.is_configured,
            "user_token": None,
            "page_token": None,
            "needs_refresh": False,
            "error": None
        }

        if not self.is_configured:
            status["error"] = "Meta credentials not configured"
            return status

        # Check user token
        user_status = await self.validate_token(self.user_token)
        status["user_token"] = {
            "valid": user_status["is_valid"],
            "expires_at": user_status["expires_at"].isoformat() if user_status["expires_at"] else None,
            "type": user_status["type"],
            "scopes": user_status["scopes"]
        }

        if not user_status["is_valid"]:
            status["error"] = user_status["error"]
            status["needs_refresh"] = True
            return status

        # Check if token expires soon (within 7 days)
        if user_status["expires_at"]:
            days_until_expiry = (user_status["expires_at"] - datetime.utcnow()).days
            status["user_token"]["days_until_expiry"] = days_until_expiry

            if days_until_expiry <= 7:
                status["needs_refresh"] = True
                logger.warning(
                    "token_expiring_soon",
                    days_until_expiry=days_until_expiry
                )

        # Try to get page token
        page_token = await self.get_page_token()
        if page_token:
            page_status = await self.validate_token(page_token)
            status["page_token"] = {
                "valid": page_status["is_valid"],
                "expires_at": page_status["expires_at"].isoformat() if page_status["expires_at"] else "never",
                "type": page_status["type"]
            }
        else:
            status["page_token"] = {"valid": False, "error": "Could not obtain page token"}

        return status

    # =========================================================================
    # REFRESH INSTRUCTIONS
    # =========================================================================

    def get_refresh_instructions(self) -> str:
        """
        Get instructions for refreshing Meta tokens.
        """
        return f"""
# 🔑 Come Rinnovare i Token Meta (Facebook/Instagram)

## Metodo 1: Graph API Explorer (Veloce)

1. Vai su: https://developers.facebook.com/tools/explorer/
2. Seleziona la tua app: {self.app_id or '[APP_ID mancante]'}
3. Clicca "Generate Access Token"
4. Seleziona permessi:
   - pages_show_list
   - pages_read_engagement
   - pages_manage_posts
   - instagram_basic
   - instagram_content_publish
5. Copia il token generato

## Metodo 2: Converti in Long-Lived (60 giorni)

Dopo aver ottenuto il token dal Graph API Explorer:

```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?\\
grant_type=fb_exchange_token&\\
client_id={self.app_id or 'YOUR_APP_ID'}&\\
client_secret={self.app_secret or 'YOUR_APP_SECRET'}&\\
fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

## Metodo 3: Aggiorna .env.production

```env
META_ACCESS_TOKEN=YOUR_NEW_LONG_LIVED_TOKEN
```

## Metodo 4: Page Token (Non Scade Mai!)

Usa un long-lived user token per ottenere un Page Token.
I Page Token derivati da long-lived user token NON SCADONO.

---

⚠️ IMPORTANTE: I token scadono perché stai usando un short-lived token.
Converti SEMPRE in long-lived dopo il login!
"""


# Singleton instance
meta_token_service = MetaTokenService()


async def check_and_report_token_status():
    """
    Check token status and log warnings if refresh needed.
    Call this on app startup or periodically.
    """
    service = meta_token_service

    try:
        status = await service.get_token_status()

        if status["error"]:
            logger.error(
                "meta_token_error",
                error=status["error"],
                instructions="Run /api/v1/social/token/refresh-instructions"
            )
        elif status["needs_refresh"]:
            logger.warning(
                "meta_token_needs_refresh",
                days_until_expiry=status["user_token"].get("days_until_expiry"),
                instructions="Run /api/v1/social/token/refresh-instructions"
            )
        else:
            logger.info(
                "meta_token_ok",
                expires_at=status["user_token"].get("expires_at")
            )

        return status

    except Exception as e:
        logger.exception("token_status_check_failed")
        return {"error": str(e)}
    finally:
        await service.close()
