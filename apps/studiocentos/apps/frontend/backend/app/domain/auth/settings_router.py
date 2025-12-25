"""Settings API Router - Gestione impostazioni admin."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.infrastructure.database.session import get_db
from .admin_models import AdminUser
from .settings_models import AdminSettings, AdminPasswordHistory
from .settings_schemas import (
    ProfileUpdate,
    NotificationPreferences,
    UIPreferences,
    PasswordChange,
    TwoFactorEnable,
    IntegrationToggle,
    AdminSettingsResponse
)
from app.core.api.dependencies.auth_deps import get_current_admin_user


router = APIRouter(prefix="/settings", tags=["settings"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_or_create_settings(db: Session, admin: AdminUser) -> AdminSettings:
    """Get or create settings for admin."""
    settings = db.query(AdminSettings).filter(
        AdminSettings.admin_id == admin.id
    ).first()

    if not settings:
        settings = AdminSettings(admin_id=admin.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.get("", response_model=AdminSettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get admin settings."""
    settings = get_or_create_settings(db, admin)
    return settings


@router.put("/profile", response_model=AdminSettingsResponse)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Update admin profile."""
    settings = get_or_create_settings(db, admin)

    # Update fields
    if data.display_name is not None:
        settings.display_name = data.display_name
    if data.avatar_url is not None:
        settings.avatar_url = data.avatar_url
    if data.timezone is not None:
        settings.timezone = data.timezone
    if data.language is not None:
        settings.language = data.language

    db.commit()
    db.refresh(settings)
    return settings


@router.put("/notifications", response_model=AdminSettingsResponse)
def update_notification_preferences(
    data: NotificationPreferences,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Update notification preferences."""
    settings = get_or_create_settings(db, admin)

    # Update all notification preferences
    for field, value in data.dict(exclude_unset=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings


@router.put("/ui", response_model=AdminSettingsResponse)
def update_ui_preferences(
    data: UIPreferences,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Update UI preferences."""
    settings = get_or_create_settings(db, admin)

    if data.theme is not None:
        settings.theme = data.theme
    if data.sidebar_collapsed is not None:
        settings.sidebar_collapsed = data.sidebar_collapsed
    if data.items_per_page is not None:
        settings.items_per_page = data.items_per_page

    db.commit()
    db.refresh(settings)
    return settings


@router.post("/security/password")
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Change admin password."""
    # Verify current password
    if not pwd_context.verify(data.current_password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Check password history (last 5)
    history = db.query(AdminPasswordHistory).filter(
        AdminPasswordHistory.admin_id == admin.id
    ).order_by(AdminPasswordHistory.created_at.desc()).limit(5).all()

    for old_hash in history:
        if pwd_context.verify(data.new_password, old_hash.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reuse recent password"
            )

    # Save current to history
    history_entry = AdminPasswordHistory(
        admin_id=admin.id,
        password_hash=admin.password_hash
    )
    db.add(history_entry)

    # Update password
    admin.password_hash = pwd_context.hash(data.new_password)
    db.commit()

    return {"success": True, "message": "Password changed successfully"}


@router.post("/security/2fa/enable")
def enable_two_factor(
    data: TwoFactorEnable,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Enable 2FA for admin."""
    settings = get_or_create_settings(db, admin)

    settings.two_factor_enabled = True
    settings.two_factor_method = data.method

    # 2FA implementation: TOTP secret generation in MFASecret model
    # SMS verification requires external provider (Phase 3)

    db.commit()

    return {
        "success": True,
        "message": "2FA enabled successfully",
        "method": data.method
    }


@router.post("/security/2fa/disable")
def disable_two_factor(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Disable 2FA for admin."""
    settings = get_or_create_settings(db, admin)

    settings.two_factor_enabled = False
    settings.two_factor_method = None

    db.commit()

    return {"success": True, "message": "2FA disabled successfully"}


@router.post("/integrations/toggle")
def toggle_integration(
    data: IntegrationToggle,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Toggle integration status (Meta, Stripe, etc.)."""
    settings = get_or_create_settings(db, admin)

    # Map integration_id to field
    integration_map = {
        "meta": "meta_enabled",
        "stripe": "stripe_enabled",
    }

    field_name = integration_map.get(data.integration_id)
    if not field_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown integration: {data.integration_id}"
        )

    # Update the field
    setattr(settings, field_name, data.enabled)
    db.commit()
    db.refresh(settings)

    return {
        "success": True,
        "integration_id": data.integration_id,
        "enabled": data.enabled,
        "message": f"{data.integration_id.title()} {'enabled' if data.enabled else 'disabled'}"
    }


@router.get("/integrations/status")
def get_integrations_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get all integrations status."""
    settings = get_or_create_settings(db, admin)

    return {
        "meta_enabled": settings.meta_enabled,
        "stripe_enabled": settings.stripe_enabled,
    }
