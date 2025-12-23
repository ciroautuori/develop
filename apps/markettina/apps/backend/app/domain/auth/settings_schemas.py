"""Settings Pydantic Schemas."""


from pydantic import BaseModel, Field, validator


class ProfileUpdate(BaseModel):
    """Schema per aggiornamento profilo."""
    display_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)
    timezone: str | None = Field(None, max_length=50)
    language: str | None = Field(None, max_length=10)


class NotificationPreferences(BaseModel):
    """Schema per preferenze notifiche."""
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    sms_notifications: bool | None = None
    notify_new_booking: bool | None = None
    notify_new_contact: bool | None = None
    notify_project_update: bool | None = None
    notify_system_alert: bool | None = None


class UIPreferences(BaseModel):
    """Schema per preferenze UI."""
    theme: str | None = Field(None, pattern="^(dark|light|auto)$")
    sidebar_collapsed: bool | None = None
    items_per_page: int | None = Field(None, ge=10, le=100)


class PasswordChange(BaseModel):
    """Schema per cambio password."""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("new_password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v


class TwoFactorEnable(BaseModel):
    """Schema per abilitazione 2FA."""
    method: str = Field(..., pattern="^(totp|sms)$")
    phone_number: str | None = Field(None, max_length=20)


class IntegrationToggle(BaseModel):
    """Schema per toggle integrazioni."""
    integration_id: str = Field(..., description="ID dell'integrazione (meta, stripe)")
    enabled: bool = Field(..., description="Stato attivazione")


class AdminSettingsResponse(BaseModel):
    """Response completo settings admin."""
    id: int
    admin_id: int
    display_name: str | None
    avatar_url: str | None
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
    two_factor_method: str | None
    session_timeout_minutes: int
    meta_enabled: bool = False
    stripe_enabled: bool = False

    class Config:
        from_attributes = True
