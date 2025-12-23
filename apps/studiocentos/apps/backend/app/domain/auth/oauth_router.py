"""OAuth Token Management Router - Endpoints for token refresh and management."""

from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_user
from app.infrastructure.database import get_db
from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider, OAuthToken
from app.domain.auth.models import User

router = APIRouter(tags=["OAuth Tokens"])


@router.post("/refresh/{provider}")
async def refresh_oauth_token(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Refresh OAuth access token for a specific provider.
    
    Args:
        provider: OAuth provider (google, linkedin, etc.)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with new access token
        
    Raises:
        400: If provider is not supported or token refresh fails
        404: If no OAuth token found for user
    """
    # Validate provider
    try:
        oauth_provider = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}. Supported: {', '.join([p.value for p in OAuthProvider])}"
        )
    
    # Check if token exists
    existing_token = OAuthTokenService.get_oauth_token(db, current_user.id, oauth_provider)
    if not existing_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No OAuth token found for provider: {provider}"
        )
    
    # Refresh token
    if oauth_provider == OAuthProvider.GOOGLE:
        refreshed_token = OAuthTokenService.refresh_google_token(db, current_user.id)
    elif oauth_provider == OAuthProvider.LINKEDIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LinkedIn tokens cannot be refreshed. Please re-authenticate."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token refresh not implemented for provider: {provider}"
        )
    
    if not refreshed_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refresh token. Please re-authenticate."
        )
    
    return {
        "access_token": refreshed_token.access_token,
        "token_type": refreshed_token.token_type,
        "expires_at": refreshed_token.expires_at.isoformat() if refreshed_token.expires_at else None,
        "provider": provider
    }


@router.get("/tokens")
async def list_oauth_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, List[Dict]]:
    """
    List all OAuth tokens for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with list of OAuth tokens (without sensitive data)
    """
    # Get all OAuth tokens for user
    tokens = db.query(OAuthToken).filter(
        OAuthToken.user_id == current_user.id
    ).all()
    
    return {
        "tokens": [
            {
                "id": token.id,
                "provider": token.provider,
                "token_type": token.token_type,
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "is_expired": OAuthTokenService.is_token_expired(token),
                "has_refresh_token": token.refresh_token is not None,
                "scope": token.scope,
                "created_at": token.created_at.isoformat(),
                "updated_at": token.updated_at.isoformat()
            }
            for token in tokens
        ]
    }


@router.get("/tokens/{provider}")
async def get_oauth_token_info(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    Get OAuth token information for a specific provider.
    
    Args:
        provider: OAuth provider
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with token information (without sensitive data)
        
    Raises:
        404: If no token found
    """
    # Validate provider
    try:
        oauth_provider = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    token = OAuthTokenService.get_oauth_token(db, current_user.id, oauth_provider)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No OAuth token found for provider: {provider}"
        )
    
    return {
        "id": token.id,
        "provider": token.provider,
        "token_type": token.token_type,
        "expires_at": token.expires_at.isoformat() if token.expires_at else None,
        "is_expired": OAuthTokenService.is_token_expired(token),
        "has_refresh_token": token.refresh_token is not None,
        "scope": token.scope,
        "created_at": token.created_at.isoformat(),
        "updated_at": token.updated_at.isoformat()
    }


@router.delete("/tokens/{provider}")
async def revoke_oauth_token(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, bool]:
    """
    Revoke and delete OAuth token for a specific provider.
    
    Args:
        provider: OAuth provider
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with success status
        
    Raises:
        404: If no token found
    """
    # Validate provider
    try:
        oauth_provider = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    success = OAuthTokenService.revoke_oauth_token(db, current_user.id, oauth_provider)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No OAuth token found for provider: {provider}"
        )
    
    return {"success": True, "provider": provider}


@router.post("/tokens/{provider}/validate")
async def validate_oauth_token(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, bool | str]:
    """
    Validate OAuth token and get a valid access token (refreshing if needed).
    
    Args:
        provider: OAuth provider
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict with validation result and valid access token
        
    Raises:
        400: If provider is not supported
        404: If no token found
    """
    # Validate provider
    try:
        oauth_provider = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    # Get valid token (will refresh if expired)
    access_token = OAuthTokenService.get_valid_token(db, current_user.id, oauth_provider)
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid OAuth token. Please re-authenticate."
        )
    
    return {
        "valid": True,
        "access_token": access_token,
        "provider": provider
    }
