"""
Google OAuth Service - Calendar and YouTube integration.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from src.infrastructure.logging import get_logger
from src.infrastructure.config.settings import settings

logger = get_logger(__name__)

# OAuth2 Scopes (Calendar + YouTube + Profile + FIT for TEST mode)
SCOPES = {
    "fit": [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.body.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
    ],
    "calendar": ["https://www.googleapis.com/auth/calendar.events"],
    "youtube": ["https://www.googleapis.com/auth/youtube.readonly"],
    "profile": [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
}


def get_all_scopes() -> List[str]:
    """Get all scopes for OAuth."""
    return [scope for scopes in SCOPES.values() for scope in scopes]


class GoogleOAuthService:
    """Google OAuth2 service for IronRep."""

    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")

    def get_authorization_url(self, scopes: Optional[List[str]] = None, state: Optional[str] = None) -> str:
        if not self.client_id:
            raise ValueError("GOOGLE_CLIENT_ID not configured")
        flow = Flow.from_client_config(
            {"web": {"client_id": self.client_id, "client_secret": self.client_secret,
                     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                     "token_uri": "https://oauth2.googleapis.com/token",
                     "redirect_uris": [self.redirect_uri]}},
            scopes=scopes or get_all_scopes(),
        )
        flow.redirect_uri = self.redirect_uri
        url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent", state=state)
        return url

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        if not self.client_id:
            raise ValueError("GOOGLE_CLIENT_ID not configured")
        flow = Flow.from_client_config(
            {"web": {"client_id": self.client_id, "client_secret": self.client_secret,
                     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                     "token_uri": "https://oauth2.googleapis.com/token",
                     "redirect_uris": [self.redirect_uri]}},
            scopes=get_all_scopes(),
        )
        flow.redirect_uri = self.redirect_uri
        flow.fetch_token(code=code)
        creds = flow.credentials
        return {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "expires_at": creds.expiry.isoformat() if creds.expiry else None,
            "scopes": list(creds.scopes) if creds.scopes else [],
        }

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        creds = Credentials(token=None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token",
                           client_id=self.client_id, client_secret=self.client_secret)
        creds.refresh(Request())
        return {"access_token": creds.token, "expires_at": creds.expiry.isoformat() if creds.expiry else None}

    def get_credentials(self, access_token: str, refresh_token: str, expires_at: Optional[datetime] = None) -> Credentials:
        creds = Credentials(token=access_token, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token",
                           client_id=self.client_id, client_secret=self.client_secret, expiry=expires_at)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    def revoke_token(self, access_token: str) -> bool:
        import requests
        resp = requests.post("https://oauth2.googleapis.com/revoke", params={"token": access_token},
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
        return resp.status_code == 200

    def get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        service = build("oauth2", "v2", credentials=credentials)
        info = service.userinfo().get().execute()
        return {"google_user_id": info.get("id"), "email": info.get("email"), "name": info.get("name"), "picture": info.get("picture")}


google_oauth_service = GoogleOAuthService()
