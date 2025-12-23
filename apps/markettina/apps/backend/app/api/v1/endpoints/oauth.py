"""
OAuth Router - Social Media OAuth Integration Endpoints
PRODUCTION READY - Real database storage for OAuth tokens
"""

from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import httpx
import secrets
import logging

from app.core.config import get_settings
from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.infrastructure.database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["OAuth"])

settings = get_settings()


# ============================================================================
# MODELS
# ============================================================================

class OAuthAuthorizeResponse(BaseModel):
    """OAuth authorization URL response."""
    auth_url: str
    state: str


class OAuthStatusResponse(BaseModel):
    """OAuth connection status response."""
    connected: bool
    platform: str
    username: Optional[str] = None
    profile_url: Optional[str] = None
    expires_at: Optional[str] = None


class OAuthCallbackData(BaseModel):
    """OAuth callback data."""
    code: str
    state: str


# ============================================================================
# OAuth State Storage (in-memory for state, DB for tokens)
# ============================================================================

_oauth_states: dict[str, dict] = {}
_oauth_verifiers: dict[str, str] = {}  # For Twitter PKCE


def generate_state(user_id: str, platform: str) -> str:
    """Generate a secure OAuth state parameter."""
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = {
        "user_id": user_id,
        "platform": platform,
        "created_at": datetime.now(UTC).isoformat(),
    }
    return state


def validate_state(state: str) -> Optional[dict]:
    """Validate and consume OAuth state."""
    return _oauth_states.pop(state, None)


# ============================================================================
# DATABASE TOKEN STORAGE HELPERS
# ============================================================================

def store_oauth_token(db: Session, user_id: int, platform: str, token_data: dict):
    """Store OAuth token in user's profile_data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User {user_id} not found for OAuth token storage")
        return

    if not hasattr(user, 'profile_data') or not user.profile_data:
        user.profile_data = {}

    if 'social_tokens' not in user.profile_data:
        user.profile_data['social_tokens'] = {}

    user.profile_data['social_tokens'][platform] = {
        'access_token': token_data.get('access_token'),
        'token_type': token_data.get('token_type', 'bearer'),
        'expires_in': token_data.get('expires_in'),
        'expires_at': (datetime.now(UTC) + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat() if token_data.get('expires_in') else None,
        'refresh_token': token_data.get('refresh_token'),
        'user_id': token_data.get('user_id'),
        'connected_at': datetime.now(UTC).isoformat(),
    }

    db.commit()
    logger.info(f"Stored {platform} OAuth token for user {user_id}")


def get_oauth_token(db: Session, user_id: int, platform: str) -> Optional[dict]:
    """Retrieve OAuth token from user's profile_data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.profile_data:
        return None

    return user.profile_data.get('social_tokens', {}).get(platform)


def remove_oauth_token(db: Session, user_id: int, platform: str):
    """Remove OAuth token from user's profile_data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.profile_data:
        return

    if 'social_tokens' in user.profile_data and platform in user.profile_data['social_tokens']:
        del user.profile_data['social_tokens'][platform]
        db.commit()
        logger.info(f"Removed {platform} OAuth token for user {user_id}")


# ============================================================================
# INSTAGRAM OAUTH
# ============================================================================

@router.post("/instagram/authorize", response_model=OAuthAuthorizeResponse)
async def instagram_authorize(current_user: User = Depends(get_current_user)):
    """Generate Instagram OAuth authorization URL."""
    if not settings.META_APP_ID or not settings.META_APP_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Instagram OAuth not configured. Please set META_APP_ID and META_APP_SECRET."
        )

    state = generate_state(str(current_user.id), "instagram")
    redirect_uri = f"{settings.FRONTEND_URL}/oauth/callback/instagram"

    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={settings.META_APP_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=instagram_basic,instagram_content_publish,instagram_manage_insights"
        f"&response_type=code"
        f"&state={state}"
    )

    return OAuthAuthorizeResponse(auth_url=auth_url, state=state)


@router.get("/instagram/callback")
async def instagram_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Instagram OAuth callback and store token."""
    state_data = validate_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    redirect_uri = f"{settings.FRONTEND_URL}/oauth/callback/instagram"

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://api.instagram.com/oauth/access_token",
            data={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            }
        )

        if token_response.status_code != 200:
            logger.error(f"Instagram token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")

        token_data = token_response.json()

        # Get long-lived token
        long_token_response = await client.get(
            "https://graph.instagram.com/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": settings.META_APP_SECRET,
                "access_token": token_data["access_token"],
            }
        )

        if long_token_response.status_code == 200:
            long_token_data = long_token_response.json()
            token_data["access_token"] = long_token_data.get("access_token", token_data["access_token"])
            token_data["expires_in"] = long_token_data.get("expires_in", 5184000)  # 60 days

    # Store token in database
    user_id = int(state_data['user_id'])
    store_oauth_token(db, user_id, "instagram", token_data)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/customer/settings?social=instagram&connected=true"
    )


@router.get("/instagram/status", response_model=OAuthStatusResponse)
async def instagram_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check Instagram connection status from database."""
    token = get_oauth_token(db, current_user.id, "instagram")

    if not token:
        return OAuthStatusResponse(connected=False, platform="instagram")

    return OAuthStatusResponse(
        connected=True,
        platform="instagram",
        expires_at=token.get('expires_at')
    )


@router.post("/instagram/disconnect")
async def instagram_disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect Instagram account by removing token."""
    remove_oauth_token(db, current_user.id, "instagram")
    return {"success": True}


# ============================================================================
# FACEBOOK OAUTH
# ============================================================================

@router.post("/facebook/authorize", response_model=OAuthAuthorizeResponse)
async def facebook_authorize(current_user: User = Depends(get_current_user)):
    """Generate Facebook OAuth authorization URL."""
    if not settings.META_APP_ID or not settings.META_APP_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Facebook OAuth not configured. Please set META_APP_ID and META_APP_SECRET."
        )

    state = generate_state(str(current_user.id), "facebook")
    redirect_uri = f"{settings.FRONTEND_URL}/oauth/callback/facebook"

    auth_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={settings.META_APP_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=pages_read_engagement,pages_manage_posts,pages_read_user_content,business_management"
        f"&response_type=code"
        f"&state={state}"
    )

    return OAuthAuthorizeResponse(auth_url=auth_url, state=state)


@router.get("/facebook/callback")
async def facebook_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Facebook OAuth callback and store token."""
    state_data = validate_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    redirect_uri = f"{settings.FRONTEND_URL}/oauth/callback/facebook"

    async with httpx.AsyncClient() as client:
        token_response = await client.get(
            "https://graph.facebook.com/v19.0/oauth/access_token",
            params={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "redirect_uri": redirect_uri,
                "code": code,
            }
        )

        if token_response.status_code != 200:
            logger.error(f"Facebook token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")

        token_data = token_response.json()

    # Store token in database
    user_id = int(state_data['user_id'])
    store_oauth_token(db, user_id, "facebook", token_data)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/customer/settings?social=facebook&connected=true"
    )


@router.get("/facebook/status", response_model=OAuthStatusResponse)
async def facebook_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check Facebook connection status from database."""
    token = get_oauth_token(db, current_user.id, "facebook")

    if not token:
        return OAuthStatusResponse(connected=False, platform="facebook")

    return OAuthStatusResponse(
        connected=True,
        platform="facebook",
        expires_at=token.get('expires_at')
    )


@router.post("/facebook/disconnect")
async def facebook_disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect Facebook account by removing token."""
    remove_oauth_token(db, current_user.id, "facebook")
    return {"success": True}


# ============================================================================
# LINKEDIN OAUTH
# ============================================================================

@router.post("/linkedin/authorize", response_model=OAuthAuthorizeResponse)
async def linkedin_authorize(current_user: User = Depends(get_current_user)):
    """Generate LinkedIn OAuth authorization URL."""
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="LinkedIn OAuth not configured. Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET."
        )

    state = generate_state(str(current_user.id), "linkedin")
    redirect_uri = settings.LINKEDIN_REDIRECT_URI or f"{settings.FRONTEND_URL}/oauth/callback/linkedin"

    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?client_id={settings.LINKEDIN_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=r_liteprofile%20r_emailaddress%20w_member_social%20rw_organization_admin"
        f"&response_type=code"
        f"&state={state}"
    )

    return OAuthAuthorizeResponse(auth_url=auth_url, state=state)


@router.get("/linkedin/callback")
async def linkedin_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle LinkedIn OAuth callback and store token."""
    state_data = validate_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    redirect_uri = settings.LINKEDIN_REDIRECT_URI or f"{settings.FRONTEND_URL}/oauth/callback/linkedin"

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if token_response.status_code != 200:
            logger.error(f"LinkedIn token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")

        token_data = token_response.json()

    # Store token in database
    user_id = int(state_data['user_id'])
    store_oauth_token(db, user_id, "linkedin", token_data)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/customer/settings?social=linkedin&connected=true"
    )


@router.get("/linkedin/status", response_model=OAuthStatusResponse)
async def linkedin_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check LinkedIn connection status from database."""
    token = get_oauth_token(db, current_user.id, "linkedin")

    if not token:
        return OAuthStatusResponse(connected=False, platform="linkedin")

    return OAuthStatusResponse(
        connected=True,
        platform="linkedin",
        expires_at=token.get('expires_at')
    )


@router.post("/linkedin/disconnect")
async def linkedin_disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect LinkedIn account by removing token."""
    remove_oauth_token(db, current_user.id, "linkedin")
    return {"success": True}


# ============================================================================
# TWITTER/X OAUTH
# ============================================================================

@router.post("/twitter/authorize", response_model=OAuthAuthorizeResponse)
async def twitter_authorize(current_user: User = Depends(get_current_user)):
    """Generate Twitter/X OAuth 2.0 PKCE authorization URL."""
    if not settings.TWITTER_API_KEY or not settings.TWITTER_API_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Twitter OAuth not configured. Please set TWITTER_API_KEY and TWITTER_API_SECRET."
        )

    state = generate_state(str(current_user.id), "twitter")
    redirect_uri = f"{settings.FRONTEND_URL}/oauth/callback/twitter"

    # Generate PKCE code verifier and challenge
    code_verifier = secrets.token_urlsafe(43)
    _oauth_verifiers[state] = code_verifier

    auth_url = (
        f"https://twitter.com/i/oauth2/authorize"
        f"?client_id={settings.TWITTER_API_KEY}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=tweet.read%20tweet.write%20users.read%20offline.access"
        f"&response_type=code"
        f"&state={state}"
        f"&code_challenge={code_verifier}"
        f"&code_challenge_method=plain"
    )

    return OAuthAuthorizeResponse(auth_url=auth_url, state=state)


@router.get("/twitter/callback")
async def twitter_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Twitter/X OAuth callback and store token."""
    state_data = validate_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    code_verifier = _oauth_verifiers.pop(state, None)
    redirect_uri = f"{settings.FRONTEND_URL}/oauth/callback/twitter"

    async with httpx.AsyncClient() as client:
        auth_header = httpx.BasicAuth(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET)

        token_response = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier or "",
            },
            auth=auth_header,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if token_response.status_code != 200:
            logger.error(f"Twitter token exchange failed: {token_response.text}")
            # Still redirect but with error flag
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/customer/settings?social=twitter&error=token_exchange"
            )

        token_data = token_response.json()

    # Store token in database
    user_id = int(state_data['user_id'])
    store_oauth_token(db, user_id, "twitter", token_data)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/customer/settings?social=twitter&connected=true"
    )


@router.get("/twitter/status", response_model=OAuthStatusResponse)
async def twitter_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check Twitter connection status from database."""
    token = get_oauth_token(db, current_user.id, "twitter")

    if not token:
        return OAuthStatusResponse(connected=False, platform="twitter")

    return OAuthStatusResponse(
        connected=True,
        platform="twitter",
        expires_at=token.get('expires_at')
    )


@router.post("/twitter/disconnect")
async def twitter_disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect Twitter account by removing token."""
    remove_oauth_token(db, current_user.id, "twitter")
    return {"success": True}
