"""OAuth Token Management - Models and Services for token storage and refresh."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Session
import requests

from app.infrastructure.database import Base
from app.infrastructure.monitoring.logging import get_logger
from app.core.config import settings

logger = get_logger("oauth_tokens")


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    LINKEDIN = "linkedin"
    GITHUB = "github"


class OAuthToken(Base):
    """OAuth token storage for token refresh functionality."""
    
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(20), nullable=False, index=True)  # google, linkedin, github, etc.
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)  # Some providers may not provide refresh tokens
    token_type = Column(String(20), default="Bearer")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scope = Column(Text, nullable=True)  # Comma-separated scopes
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="oauth_tokens")


class OAuthTokenService:
    """Service for OAuth token management and refresh."""
    
    # Token refresh URLs for each provider
    TOKEN_REFRESH_URLS = {
        OAuthProvider.GOOGLE: "https://oauth2.googleapis.com/token",
        OAuthProvider.LINKEDIN: "https://www.linkedin.com/oauth/v2/accessToken",
    }
    
    @staticmethod
    def save_oauth_token(
        db: Session,
        user_id: int,
        provider: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        scope: Optional[str] = None,
        token_type: str = "Bearer"
    ) -> OAuthToken:
        """
        Save or update OAuth token for a user.
        
        Args:
            db: Database session
            user_id: User ID
            provider: OAuth provider name (google, linkedin, etc.)
            access_token: Access token
            refresh_token: Refresh token (optional)
            expires_in: Token expiration in seconds (optional)
            scope: Token scopes (optional)
            token_type: Token type (default: Bearer)
            
        Returns:
            OAuthToken: Saved token record
        """
        # Calculate expiration time
        expires_at = None
        if expires_in:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        # Check if token already exists for this user and provider
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == provider
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = access_token
            if refresh_token:
                existing_token.refresh_token = refresh_token
            existing_token.token_type = token_type
            existing_token.expires_at = expires_at
            if scope:
                existing_token.scope = scope
            existing_token.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(existing_token)
            logger.info(f"Updated OAuth token for user {user_id}, provider {provider}")
            return existing_token
        else:
            # Create new token
            new_token = OAuthToken(
                user_id=user_id,
                provider=provider,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                expires_at=expires_at,
                scope=scope
            )
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            logger.info(f"Saved new OAuth token for user {user_id}, provider {provider}")
            return new_token
    
    @staticmethod
    def get_oauth_token(db: Session, user_id: int, provider: str) -> Optional[OAuthToken]:
        """Get OAuth token for a user and provider."""
        return db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.provider == provider
        ).first()
    
    @staticmethod
    def is_token_expired(token: OAuthToken) -> bool:
        """Check if a token is expired."""
        if not token.expires_at:
            # If no expiration is set, assume token is valid
            return False
        
        # Add 5 minute buffer to refresh before actual expiration
        buffer = timedelta(minutes=5)
        return datetime.now(timezone.utc) >= (token.expires_at - buffer)
    
    @staticmethod
    def refresh_google_token(db: Session, user_id: int) -> Optional[OAuthToken]:
        """
        Refresh Google OAuth token using refresh token.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            OAuthToken: Updated token or None if refresh failed
        """
        token = OAuthTokenService.get_oauth_token(db, user_id, OAuthProvider.GOOGLE)
        
        if not token:
            logger.warning(f"No Google OAuth token found for user {user_id}")
            return None
        
        if not token.refresh_token:
            logger.warning(f"No refresh token available for user {user_id}")
            return None
        
        try:
            # Request new access token
            response = requests.post(
                OAuthTokenService.TOKEN_REFRESH_URLS[OAuthProvider.GOOGLE],
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": token.refresh_token,
                    "grant_type": "refresh_token"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to refresh Google token: {response.text}")
                return None
            
            token_data = response.json()
            new_access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in")
            
            if not new_access_token:
                logger.error("No access token in refresh response")
                return None
            
            # Update token in database
            return OAuthTokenService.save_oauth_token(
                db=db,
                user_id=user_id,
                provider=OAuthProvider.GOOGLE,
                access_token=new_access_token,
                refresh_token=token.refresh_token,  # Keep existing refresh token
                expires_in=expires_in,
                scope=token.scope,
                token_type=token.token_type
            )
            
        except Exception as e:
            logger.error(f"Error refreshing Google token: {e}", exc_info=True)
            return None
    
    @staticmethod
    def refresh_linkedin_token(db: Session, user_id: int) -> Optional[OAuthToken]:
        """
        Refresh LinkedIn OAuth token using refresh token.
        
        Note: LinkedIn tokens expire after 60 days and cannot be refreshed.
        Users must re-authenticate via OAuth flow.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            OAuthToken: None (LinkedIn doesn't support refresh)
        """
        logger.warning("LinkedIn does not support token refresh. User must re-authenticate.")
        return None
    
    @staticmethod
    def get_valid_token(db: Session, user_id: int, provider: str) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            db: Database session
            user_id: User ID
            provider: OAuth provider
            
        Returns:
            str: Valid access token or None
        """
        token = OAuthTokenService.get_oauth_token(db, user_id, provider)
        
        if not token:
            return None
        
        # If token is expired, try to refresh
        if OAuthTokenService.is_token_expired(token):
            logger.info(f"Token expired for user {user_id}, attempting refresh")
            
            if provider == OAuthProvider.GOOGLE:
                refreshed_token = OAuthTokenService.refresh_google_token(db, user_id)
                if refreshed_token:
                    return refreshed_token.access_token
                return None
            elif provider == OAuthProvider.LINKEDIN:
                # LinkedIn doesn't support refresh
                return None
            else:
                logger.warning(f"Token refresh not implemented for provider: {provider}")
                return None
        
        return token.access_token
    
    @staticmethod
    def revoke_oauth_token(db: Session, user_id: int, provider: str) -> bool:
        """
        Revoke and delete OAuth token for a user and provider.
        
        Args:
            db: Database session
            user_id: User ID
            provider: OAuth provider
            
        Returns:
            bool: True if revoked successfully
        """
        token = OAuthTokenService.get_oauth_token(db, user_id, provider)
        
        if not token:
            return False
        
        # Delete token from database
        db.delete(token)
        db.commit()
        logger.info(f"Revoked OAuth token for user {user_id}, provider {provider}")
        
        return True
