"""MFA API Router - Enterprise Multi-Factor Authentication Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger(__name__)
from app.domain.auth.mfa_service import MFAService
from app.domain.auth.models import User

router = APIRouter(prefix="/auth/mfa", tags=["MFA"])

# Request/Response Models
class MFASetupResponse(BaseModel):
    """MFA setup response."""

    secret: str
    qr_code: str
    backup_codes: list[str]
    provisioning_uri: str

class MFAVerifyRequest(BaseModel):
    """MFA verification request."""

    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP token")

class MFAActivateRequest(BaseModel):
    """MFA activation request."""

    token: str = Field(..., min_length=6, max_length=6)

class MFADisableRequest(BaseModel):
    """MFA disable request."""

    password: str = Field(..., min_length=1)

class BackupCodeRequest(BaseModel):
    """Backup code verification."""

    code: str = Field(..., min_length=16, max_length=16)

class MFAStatusResponse(BaseModel):
    """MFA status response."""

    enabled: bool
    activated_at: str | None
    last_used_at: str | None
    backup_codes_remaining: int

@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get MFA status for current user.

    Returns current MFA configuration and usage statistics.
    """
    try:
        mfa_service = MFAService(db)
        status_data = mfa_service.get_mfa_status(current_user)

        return MFAStatusResponse(**status_data)

    except Exception as e:
        logger.error(f"Error getting MFA status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get MFA status"
        )

@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """
    Initialize MFA setup for user.

    Returns:
        - QR code for authenticator app
        - Secret key for manual entry
        - Backup codes for recovery
    """
    try:
        mfa_service = MFAService(db)
        setup_data = mfa_service.setup_mfa(current_user)

        logger.info(f"MFA setup initiated for user {current_user.id}")

        return MFASetupResponse(**setup_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting up MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to setup MFA"
        )

@router.post("/activate")
async def activate_mfa(
    request: MFAActivateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Activate MFA after verifying first token.

    This completes the MFA setup process.
    """
    try:
        mfa_service = MFAService(db)
        mfa_service.activate_mfa(current_user, request.token)

        logger.info(f"MFA activated for user {current_user.id}")

        return {"success": True, "message": "MFA activated successfully"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error activating MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate MFA"
        )

@router.post("/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify TOTP token.

    Used during login or sensitive operations.
    """
    try:
        mfa_service = MFAService(db)
        is_valid = mfa_service.verify_totp(current_user, request.token)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA token"
            )

        return {"success": True, "message": "Token verified successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify MFA token"
        )

@router.post("/verify-backup")
async def verify_backup_code(
    request: BackupCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify backup code.

    Use when TOTP is not available. Each code can only be used once.
    """
    try:
        mfa_service = MFAService(db)
        is_valid = mfa_service.verify_backup_code(current_user, request.code)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid backup code"
            )

        # Get remaining codes
        status_data = mfa_service.get_mfa_status(current_user)

        return {
            "success": True,
            "message": "Backup code verified successfully",
            "backup_codes_remaining": status_data["backup_codes_remaining"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying backup code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify backup code"
        )

@router.post("/disable")
async def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Disable MFA (requires password).

    Security measure to prevent unauthorized MFA removal.
    """
    try:
        mfa_service = MFAService(db)
        mfa_service.disable_mfa(current_user, request.password)

        logger.info(f"MFA disabled for user {current_user.id}")

        return {"success": True, "message": "MFA disabled successfully"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error disabling MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to disable MFA"
        )

@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Regenerate backup codes.

    Invalidates all previous backup codes.
    """
    try:
        mfa_service = MFAService(db)
        backup_codes = mfa_service.regenerate_backup_codes(current_user)

        logger.info(f"Backup codes regenerated for user {current_user.id}")

        return {
            "success": True,
            "backup_codes": backup_codes,
            "message": "Backup codes regenerated successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error regenerating backup codes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes",
        )
