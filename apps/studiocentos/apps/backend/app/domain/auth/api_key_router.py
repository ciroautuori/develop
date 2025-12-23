"""API Key Management Router - Enterprise API Key Operations."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.api_key_rotation import APIKeyRotationService, get_api_key_service
from app.core.api.dependencies.auth_deps import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)
from app.domain.auth.models import User

router = APIRouter(prefix="/auth/api-keys", tags=["API Keys"])

# Request/Response Models
class CreateAPIKeyRequest(BaseModel):
    """Create API key request."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    scopes: List[str] = Field(..., min_items=1)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
    ip_whitelist: Optional[List[str]] = None

class RotateAPIKeyRequest(BaseModel):
    """Rotate API key request."""

    key_id: str = Field(..., min_length=1)
    keep_old_key_days: int = Field(7, ge=1, le=30)

class RevokeAPIKeyRequest(BaseModel):
    """Revoke API key request."""

    key_id: str = Field(..., min_length=1)

class APIKeyResponse(BaseModel):
    """API key response."""

    key_id: str
    key_prefix: str
    name: str
    scopes: List[str]
    is_active: bool
    created_at: str
    expires_at: Optional[str]
    last_used_at: Optional[str]
    rotation_count: int
    expires_soon: bool
    days_until_expiry: Optional[int]

@router.post("/create")
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    service: APIKeyRotationService = Depends(get_api_key_service),
):
    """
    Create new API key.

    Returns the API key only once - save it securely!
    """
    try:
        result = await service.create_api_key(
            user_id=current_user.id,
            name=request.name,
            scopes=request.scopes,
            description=request.description,
            expires_in_days=request.expires_in_days,
            ip_whitelist=request.ip_whitelist,
        )

        return {"success": True, **result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create API key"
        )

@router.post("/rotate")
async def rotate_api_key(
    request: RotateAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    service: APIKeyRotationService = Depends(get_api_key_service),
):
    """
    Rotate API key.

    Creates new key and keeps old one active for transition period.
    """
    try:
        result = await service.rotate_api_key(
            key_id=request.key_id,
            user_id=current_user.id,
            keep_old_key_days=request.keep_old_key_days,
        )

        return {"success": True, **result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error rotating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to rotate API key"
        )

@router.post("/revoke")
async def revoke_api_key(
    request: RevokeAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    service: APIKeyRotationService = Depends(get_api_key_service),
):
    """
    Revoke API key immediately.

    This action is irreversible.
    """
    try:
        await service.revoke_api_key(key_id=request.key_id, user_id=current_user.id)

        return {"success": True, "message": "API key revoked successfully"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to revoke API key"
        )

@router.get("/list", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    service: APIKeyRotationService = Depends(get_api_key_service),
):
    """
    List all API keys for current user.

    Returns API key metadata (not the actual keys).
    """
    try:
        keys = await service.get_user_api_keys(current_user.id)
        return keys

    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list API keys"
        )

@router.get("/scopes")
async def get_available_scopes():
    """
    Get available API scopes.

    Returns list of available permissions for API keys.
    """
    return {
        "scopes": [
            {"name": "portfolio:read", "description": "Read portfolio data"},
            {"name": "portfolio:write", "description": "Create/update portfolio data"},
            {"name": "analytics:read", "description": "Read analytics data"},
            {"name": "billing:read", "description": "Read billing information"},
            {"name": "admin:*", "description": "Full admin access (use with caution)"},
        ]
    }
