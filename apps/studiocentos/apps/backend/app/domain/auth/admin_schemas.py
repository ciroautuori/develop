"""
Admin Authentication Schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AdminSetupPasswordRequest(BaseModel):
    """Request per setup password iniziale admin."""
    email: str = Field(..., description="Email amministratore")
    password: str = Field(..., min_length=12, description="Password sicura (min 12 caratteri)")
    password_confirm: str = Field(..., description="Conferma password")
    setup_token: str = Field(..., description="Token di setup (fornito al primo avvio)")
    
    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Le password non coincidono')
        return v


class AdminChangePasswordRequest(BaseModel):
    """Request per cambio password admin."""
    current_password: str = Field(..., description="Password attuale")
    new_password: str = Field(..., min_length=12, description="Nuova password")
    new_password_confirm: str = Field(..., description="Conferma nuova password")
    
    @field_validator('new_password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Le password non coincidono')
        return v


class AdminLoginRequest(BaseModel):
    """Request per login admin."""
    email: str = Field(..., description="Email amministratore")
    password: str = Field(..., description="Password")
    totp_token: Optional[str] = Field(None, description="Token 2FA (se abilitato)")


class AdminLoginResponse(BaseModel):
    """Response login admin."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Secondi prima della scadenza")
    admin_email: str
    requires_2fa: bool = False


class AdminRefreshTokenRequest(BaseModel):
    """Request per refresh token."""
    refresh_token: str = Field(..., description="Refresh token")


class Admin2FASetupResponse(BaseModel):
    """Response setup 2FA."""
    secret: str = Field(..., description="Secret TOTP")
    qr_code_url: str = Field(..., description="URL QR code per app authenticator")
    backup_codes: list[str] = Field(..., description="Codici di backup")


class Admin2FAEnableRequest(BaseModel):
    """Request per abilitare 2FA."""
    totp_token: str = Field(..., description="Token 6 cifre per verifica")


class AdminPasswordResetRequest(BaseModel):
    """Request per reset password (via email)."""
    email: str = Field(..., description="Email amministratore")


class AdminPasswordResetConfirm(BaseModel):
    """Conferma reset password."""
    reset_token: str = Field(..., description="Token ricevuto via email")
    new_password: str = Field(..., min_length=12, description="Nuova password")
    new_password_confirm: str = Field(..., description="Conferma nuova password")
    
    @field_validator('new_password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Le password non coincidono')
        return v


class AdminProfileResponse(BaseModel):
    """Response profilo admin."""
    id: int
    email: str
    full_name: Optional[str]
    is_2fa_enabled: bool
    created_at: str
    last_login: Optional[str]
    
    class Config:
        from_attributes = True
