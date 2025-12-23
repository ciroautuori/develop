"""LinkedIn OAuth Router
- /oauth/linkedin/login -> Redirect to LinkedIn Authorization URL
- /oauth/linkedin/callback -> Handle code exchange, upsert user and profile, issue JWT, redirect to frontend with token.
"""

import secrets
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.auth.schemas import UserCreate
from app.domain.auth.services import AuthService
from app.domain.auth.user_service import UserService
from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider
from app.infrastructure.database import get_db
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger("linkedin_oauth")

# Stub model for user profile creation (Portfolio domain Phase 2)
class UserProfileCreate(BaseModel):
    """Temporary stub for UserProfileCreate."""
    full_name: str
    title: str = ""
    bio: str = ""
    email: str

router = APIRouter()  # Tags in api/v1/__init__.py

@router.get("/login")
def linkedin_login(request: Request, next: str | None = None):
    """Start LinkedIn OAuth Authorization Code Flow."""
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="LinkedIn OAuth not configured")

    state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "state": state,
        "scope": "r_liteprofile r_emailaddress",
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"

    # Set state in cookie for CSRF protection (10 min)
    resp = RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
    resp.set_cookie(
        key="li_oauth_state",
        value=state,
        httponly=True,
        samesite="lax",
        max_age=600,
        path="/",
    )
    # Optionally preserve next page in cookie
    if next:
        resp.set_cookie(
            key="li_oauth_next",
            value=next,
            httponly=False,
            samesite="lax",
            max_age=600,
            path="/",
        )
    return resp

@router.get("/callback")
def linkedin_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    """Handle LinkedIn callback: exchange code, upsert user/profile, return JWT via redirect."""
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    cookie_state = request.cookies.get("li_oauth_state")
    if not cookie_state or cookie_state != state:
        raise HTTPException(status_code=400, detail="Invalid state")

    # Exchange code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
    }

    token_resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=token_data,
        timeout=10,
    )
    if not token_resp.ok:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_resp.text}")

    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in")  # LinkedIn tokens expire after 60 days

    if not access_token:
        raise HTTPException(status_code=400, detail="Missing access_token from LinkedIn")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Fetch basic profile
    me_resp = requests.get(
        "https://api.linkedin.com/v2/me",
        headers=headers,
        params={"projection": "(id,localizedFirstName,localizedLastName,headline)"},
        timeout=10,
    )
    if not me_resp.ok:
        raise HTTPException(status_code=400, detail=f"LinkedIn /me failed: {me_resp.text}")

    # Fetch primary email
    email_resp = requests.get(
        "https://api.linkedin.com/v2/emailAddress",
        headers=headers,
        params={"q": "members", "projection": "(elements*(handle~))"},
        timeout=10,
    )
    if not email_resp.ok:
        raise HTTPException(
            status_code=400, detail=f"LinkedIn /emailAddress failed: {email_resp.text}"
        )

    me = me_resp.json() or {}
    email_data = email_resp.json() or {}

    first = me.get("localizedFirstName") or ""
    last = me.get("localizedLastName") or ""
    headline = me.get("headline") or ""

    try:
        primary_email = (
            (email_data.get("elements") or [{}])[0].get("handle~", {}).get("emailAddress")
        )
    except Exception:
        primary_email = None

    if not primary_email:
        raise HTTPException(status_code=400, detail="LinkedIn email not available")

    full_name = (f"{first} {last}").strip() or primary_email.split("@")[0]

    # Get selected plan from request (passed from frontend)
    selected_plan = request.cookies.get("selected_plan") or "trial"

    # Upsert user with appropriate role based on plan
    user = UserService.get_user_by_email(db, primary_email)
    if not user:
        # Create user with role based on selected plan
        safe_password = secrets.token_urlsafe(24)
        user_data = UserCreate(email=primary_email, password=safe_password, full_name=full_name)
        profile_data = UserProfileCreate(
            full_name=full_name, title=headline or "", bio="", email=primary_email
        )

        if selected_plan == "trial" or selected_plan == "free":
            user = UserService.create_trial_user_with_profile(db, user_data, profile_data)
        elif selected_plan == "pro":
            # For now create as TRIAL, will be upgraded after Stripe integration
            user = UserService.create_trial_user_with_profile(db, user_data, profile_data)
        else:  # "standard" or default
            # For now create as TRIAL, will be upgraded after Stripe integration
            user = UserService.create_trial_user_with_profile(db, user_data, profile_data)
    else:
        # Update full_name if empty
        if not user.full_name and full_name:
            from app.domain.auth.schemas import UserUpdate

            user = UserService.update_user(db, user.id, UserUpdate(full_name=full_name))
        # Ensure profile exists for existing users
        if not getattr(user, "profile", None):
            profile_data = UserProfileCreate(
                full_name=full_name, title=headline or "", bio="", email=primary_email
            )
            profile_dict = profile_data.model_dump()
            profile_dict["user_id"] = user.id
            # Profile model removed - merged into User

            db_profile = Profile(**profile_dict)
            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)

    # Save OAuth token in database (LinkedIn doesn't provide refresh tokens)
    OAuthTokenService.save_oauth_token(
        db=db,
        user_id=user.id,
        provider=OAuthProvider.LINKEDIN,
        access_token=access_token,
        refresh_token=None,  # LinkedIn doesn't provide refresh tokens
        expires_in=expires_in,
        scope="r_liteprofile r_emailaddress",
        token_type="Bearer"
    )
    logger.info(f"Saved LinkedIn OAuth token for user {user.id}")

    # Issue JWT
    jwt_token = AuthService.create_access_token(data={"sub": primary_email})

    # Redirect to frontend with token
    frontend_url = settings.FRONTEND_APP_URL.rstrip("/")
    redirect_to = f"{frontend_url}/auth/callback?token={jwt_token}"

    # Clear state cookie
    resp = RedirectResponse(url=redirect_to, status_code=status.HTTP_302_FOUND)
    resp.delete_cookie("li_oauth_state", path="/")
    # Preserve li_oauth_next not used currently; future: append to redirect
    return resp
