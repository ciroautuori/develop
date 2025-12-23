"""Settings Pydantic Schemas."""

from typing import Optional
from pydantic import BaseModel, Field, validator


class ProfileUpdate(BaseModel):
    """Schema per aggiornamento profilo."""
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)


class NotificationPreferences(BaseModel):
    """Schema per preferenze notifiche."""
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    notify_new_booking: Optional[bool] = None
    notify_new_contact: Optional[bool] = None
    notify_project_update: Optional[bool] = None
    notify_system_alert: Optional[bool] = None


class UIPreferences(BaseModel):
    """Schema per preferenze UI."""
    theme: Optional[str] = Field(None, pattern="^(dark|light|auto)$")
    sidebar_collapsed: Optional[bool] = None
    items_per_page: Optional[int] = Field(None, ge=10, le=100)


class PasswordChange(BaseModel):
    """Schema per cambio password."""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v


class TwoFactorEnable(BaseModel):
    """Schema per abilitazione 2FA."""
    method: str = Field(..., pattern="^(totp|sms)$")
    phone_number: Optional[str] = Field(None, max_length=20)


class IntegrationToggle(BaseModel):
    """Schema per toggle integrazioni."""
    integration_id: str = Field(..., description="ID dell'integrazione (meta, stripe)")
    enabled: bool = Field(..., description="Stato attivazione")


class AdminSettingsResponse(BaseModel):
    """Response completo settings admin."""
    id: int
    admin_id: int
    display_name: Optional[str]
    avatar_url: Optional[str]
    timezone: str
    language: str
    email_notifications: bool
    push_notifications: bool
    sms_notifications: bool
    notify_new_booking: bool
    notify_new_contact: bool
    notify_project_update: bool
    notify_system_alert: bool
    theme: str
    sidebar_collapsed: bool
    items_per_page: int
    two_factor_enabled: bool
    two_factor_method: Optional[str]
    session_timeout_minutes: int
    meta_enabled: bool = False
    stripe_enabled: bool = False

    class Config:
        from_attributes = True
