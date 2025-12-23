"""Tests for OAuth Token Management."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider, OAuthToken
from app.domain.auth.models import User


class TestOAuthTokenService:
    """Test suite for OAuth token management."""
    
    def test_save_oauth_token_new(self, db_session, test_user):
        """Test saving a new OAuth token."""
        token = OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
            scope="openid email profile"
        )
        
        assert token.id is not None
        assert token.user_id == test_user.id
        assert token.provider == OAuthProvider.GOOGLE
        assert token.access_token == "test_access_token"
        assert token.refresh_token == "test_refresh_token"
        assert token.expires_at is not None
        assert token.scope == "openid email profile"
    
    def test_save_oauth_token_update_existing(self, db_session, test_user):
        """Test updating an existing OAuth token."""
        # Create initial token
        token1 = OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="old_token",
            refresh_token="old_refresh"
        )
        
        # Update with new token
        token2 = OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="new_token",
            refresh_token="new_refresh"
        )
        
        assert token1.id == token2.id  # Same record
        assert token2.access_token == "new_token"
        assert token2.refresh_token == "new_refresh"
    
    def test_get_oauth_token(self, db_session, test_user):
        """Test retrieving OAuth token."""
        # Save token
        OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="test_token"
        )
        
        # Retrieve token
        token = OAuthTokenService.get_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE
        )
        
        assert token is not None
        assert token.access_token == "test_token"
    
    def test_get_oauth_token_not_found(self, db_session, test_user):
        """Test retrieving non-existent OAuth token."""
        token = OAuthTokenService.get_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.LINKEDIN
        )
        
        assert token is None
    
    def test_is_token_expired_not_expired(self, db_session, test_user):
        """Test token expiration check for valid token."""
        # Create token that expires in 1 hour
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        token = OAuthToken(
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="test",
            expires_at=future_time
        )
        
        assert not OAuthTokenService.is_token_expired(token)
    
    def test_is_token_expired_expired(self, db_session, test_user):
        """Test token expiration check for expired token."""
        # Create token that expired 1 hour ago
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        token = OAuthToken(
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="test",
            expires_at=past_time
        )
        
        assert OAuthTokenService.is_token_expired(token)
    
    def test_is_token_expired_no_expiration(self, db_session, test_user):
        """Test token without expiration (never expires)."""
        token = OAuthToken(
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="test",
            expires_at=None
        )
        
        assert not OAuthTokenService.is_token_expired(token)
    
    @patch('app.domain.auth.oauth_tokens.requests.post')
    def test_refresh_google_token_success(self, mock_post, db_session, test_user):
        """Test successful Google token refresh."""
        # Save token with refresh_token
        OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="old_token",
            refresh_token="refresh_token_123",
            expires_in=3600
        )
        
        # Mock successful refresh response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        # Refresh token
        refreshed = OAuthTokenService.refresh_google_token(db_session, test_user.id)
        
        assert refreshed is not None
        assert refreshed.access_token == "new_access_token"
        assert refreshed.refresh_token == "refresh_token_123"  # Preserved
    
    @patch('app.domain.auth.oauth_tokens.requests.post')
    def test_refresh_google_token_failure(self, mock_post, db_session, test_user):
        """Test failed Google token refresh."""
        # Save token with refresh_token
        OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="old_token",
            refresh_token="refresh_token_123"
        )
        
        # Mock failed refresh response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid refresh token"
        mock_post.return_value = mock_response
        
        # Refresh token
        refreshed = OAuthTokenService.refresh_google_token(db_session, test_user.id)
        
        assert refreshed is None
    
    def test_refresh_linkedin_token(self, db_session, test_user):
        """Test LinkedIn token refresh (not supported)."""
        # Save LinkedIn token
        OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.LINKEDIN,
            access_token="linkedin_token"
        )
        
        # Try to refresh (should return None - not supported)
        refreshed = OAuthTokenService.refresh_linkedin_token(db_session, test_user.id)
        
        assert refreshed is None
    
    @patch('app.domain.auth.oauth_tokens.OAuthTokenService.refresh_google_token')
    def test_get_valid_token_not_expired(self, mock_refresh, db_session, test_user):
        """Test get_valid_token with unexpired token."""
        # Save valid token (expires in 1 hour)
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="valid_token",
            expires_in=3600
        )
        
        # Get valid token
        token = OAuthTokenService.get_valid_token(
            db_session, test_user.id, OAuthProvider.GOOGLE
        )
        
        # Should return existing token without refresh
        assert token == "valid_token"
        mock_refresh.assert_not_called()
    
    @patch('app.domain.auth.oauth_tokens.OAuthTokenService.refresh_google_token')
    def test_get_valid_token_expired(self, mock_refresh, db_session, test_user):
        """Test get_valid_token with expired token triggers refresh."""
        # Save expired token
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        token = OAuthToken(
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="expired_token",
            refresh_token="refresh",
            expires_at=past_time
        )
        db_session.add(token)
        db_session.commit()
        
        # Mock successful refresh
        refreshed_token = OAuthToken(
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="refreshed_token",
            refresh_token="refresh"
        )
        mock_refresh.return_value = refreshed_token
        
        # Get valid token
        result = OAuthTokenService.get_valid_token(
            db_session, test_user.id, OAuthProvider.GOOGLE
        )
        
        # Should trigger refresh
        mock_refresh.assert_called_once()
        assert result == "refreshed_token"
    
    def test_revoke_oauth_token(self, db_session, test_user):
        """Test revoking OAuth token."""
        # Save token
        OAuthTokenService.save_oauth_token(
            db=db_session,
            user_id=test_user.id,
            provider=OAuthProvider.GOOGLE,
            access_token="token_to_revoke"
        )
        
        # Revoke token
        success = OAuthTokenService.revoke_oauth_token(
            db_session, test_user.id, OAuthProvider.GOOGLE
        )
        
        assert success is True
        
        # Verify token is deleted
        token = OAuthTokenService.get_oauth_token(
            db_session, test_user.id, OAuthProvider.GOOGLE
        )
        assert token is None
    
    def test_revoke_oauth_token_not_found(self, db_session, test_user):
        """Test revoking non-existent OAuth token."""
        success = OAuthTokenService.revoke_oauth_token(
            db_session, test_user.id, OAuthProvider.GOOGLE
        )
        
        assert success is False
