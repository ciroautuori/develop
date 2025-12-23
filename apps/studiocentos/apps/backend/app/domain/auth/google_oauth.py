"""Google OAuth Router - Customer Login

Provides Google OAuth login/callback endpoints for Customer registration.
Uses unified Google OAuth service from app.core.google.

REFACTORED: 2025-05-29
- Now uses GoogleOAuthService for consistency
- Scope management centralized in core/google/scopes.py
- Token storage via OAuthTokenService
"""

import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.google import google_oauth_service
from app.domain.auth.schemas import UserCreate
from app.domain.auth.services import AuthService
from app.domain.auth.user_service import UserService
from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider
from app.infrastructure.database import get_db


logger = logging.getLogger(__name__)


# Stub model for user profile creation (Portfolio domain Phase 2)
class UserProfileCreate(BaseModel):
    """Temporary stub for UserProfileCreate."""
    full_name: str
    title: str = ""
    bio: str = ""
    email: str


router = APIRouter()  # Tags in api/v1/__init__.py

@router.get("/login")
async def google_login(response: Response):
    """Initiate Google OAuth flow.

    Uses unified GoogleOAuthService with 'customer' scope set.
    Redirects user to Google authorization page.
    """
    # Generate CSRF state token
    state = secrets.token_urlsafe(32)

    # Set secure HTTP-only cookie for CSRF protection
    is_production = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="google_oauth_state",
        value=state,
        httponly=True,
        max_age=600,  # 10 minutes
        samesite="lax",
        path="/",
        secure=is_production,  # Secure in production, not in dev
    )

    # Get redirect URI
    redirect_uri = google_oauth_service.get_default_redirect_uri("customer")

    # Generate auth URL using unified service with 'customer' scope set
    google_auth_url = google_oauth_service.get_auth_url(
        redirect_uri=redirect_uri,
        use_case="customer",
        state=state,
    )

    logger.info(f"Initiating Google OAuth for customer, redirect: {redirect_uri}")
    return RedirectResponse(url=google_auth_url, status_code=302)

@router.get("/callback")
async def google_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db),
):
    """Handle Google OAuth callback
    Exchange authorization code for user info and create/login user.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")

    # Verify CSRF state
    stored_state = request.cookies.get("google_oauth_state")

    # Debug logging
    logger.debug(f"OAuth callback state received: {state}")
    logger.debug(f"Cookie state stored: {stored_state}")

    if not stored_state:
        raise HTTPException(
            status_code=400,
            detail=f"Missing state cookie (CSRF protection). Received state: {state}",
        )

    if stored_state != state:
        raise HTTPException(
            status_code=400,
            detail=f"State mismatch (CSRF protection). Expected: {stored_state}, Got: {state}",
        )

    try:
        # Get redirect URI (same as login)
        redirect_uri = google_oauth_service.get_default_redirect_uri("customer")

        # Exchange code for tokens using unified service
        token_response = await google_oauth_service.exchange_code(
            code=code,
            redirect_uri=redirect_uri,
        )

        if not token_response:
            raise HTTPException(
                status_code=400,
                detail="Google token exchange failed. Please try again."
            )

        access_token = token_response.access_token
        refresh_token = token_response.refresh_token
        expires_in = token_response.expires_in
        scope = token_response.scope

        # Get user info using unified service
        google_user = await google_oauth_service.get_user_info(access_token)

        if not google_user:
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch user info from Google"
            )

        # Extract user data from GoogleUserInfo
        email = google_user.email
        name = google_user.name
        google_id = google_user.id
        picture = google_user.picture

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")

        # Get selected plan from request (passed from frontend)
        selected_plan = request.cookies.get("selected_plan") or "trial"

        # Check if user exists
        existing_user = UserService.get_user_by_email(db, email)

        if existing_user:
            # Update existing user with Google info
            if not hasattr(existing_user, "google_id") or not existing_user.google_id:
                # Add Google ID to existing account
                existing_user.google_id = google_id
                if picture and hasattr(existing_user, "profile") and existing_user.user:
                    existing_user.user.avatar = picture
                db.commit()

            user = existing_user
        else:
            # Create user with role based on selected plan
            safe_password = secrets.token_urlsafe(24)
            user_data = UserCreate(
                email=email, password=safe_password, full_name=name or email.split("@")[0]
            )
            profile_data = UserProfileCreate(
                full_name=name or email.split("@")[0], title="", bio="", email=email
            )

            if selected_plan == "trial" or selected_plan == "free":
                user = UserService.create_trial_user_with_profile(db, user_data, profile_data)
            elif selected_plan == "pro":
                # For now create as TRIAL, will be upgraded after Stripe integration
                user = UserService.create_trial_user_with_profile(db, user_data, profile_data)
            else:  # "standard" or default
                # For now create as TRIAL, will be upgraded after Stripe integration
                user = UserService.create_trial_user_with_profile(db, user_data, profile_data)

            # Set Google ID after creation
            user.google_id = google_id
            if picture and hasattr(user, "profile") and user.user:
                user.user.avatar = picture
            db.commit()
            db.refresh(user)

        # Save OAuth tokens in database for token refresh functionality
        if refresh_token or access_token:
            OAuthTokenService.save_oauth_token(
                db=db,
                user_id=user.id,
                provider=OAuthProvider.GOOGLE,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                scope=scope,
                token_type="Bearer"
            )
            logger.info(f"Saved Google OAuth tokens for user {user.id}")

        # Generate JWT token
        jwt_token = AuthService.create_access_token(data={"sub": user.email})

        # Redirect to frontend with token
        frontend_callback_url = f"{settings.FRONTEND_APP_URL}/auth/callback?token={jwt_token}"

        response = RedirectResponse(url=frontend_callback_url, status_code=302)

        # Clear CSRF cookie
        response.delete_cookie(key="google_oauth_state")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Google authentication failed. Please try again later."
        )
