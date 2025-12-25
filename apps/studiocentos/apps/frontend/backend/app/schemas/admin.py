"""
Pydantic schemas for admin authentication and management.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class AdminRole(str, Enum):
    """Ruoli amministratore."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"


# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class AdminSetupPasswordRequest(BaseModel):
    """Request per setup password iniziale admin."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=12)
    password_confirm: str = Field(..., min_length=12)
    setup_token: str = Field(..., description="Token segreto per primo setup")
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Le password non corrispondono')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "email": "admin@studiocentos.it",
                "password": "MySecureP@ssw0rd123!",
                "password_confirm": "MySecureP@ssw0rd123!",
                "setup_token": "secret-setup-token-from-env"
            }
        }


class AdminLoginRequest(BaseModel):
    """Request per login admin."""
    
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
    totp_token: Optional[str] = Field(None, min_length=6, max_length=6, description="Token 2FA se abilitato")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "MySecureP@ssw0rd123!",
                "totp_token": "123456"
            }
        }


class AdminChangePasswordRequest(BaseModel):
    """Request per cambio password."""
    
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=12)
    new_password_confirm: str = Field(..., min_length=12)
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Le nuove password non corrispondono')
        return v
    
    @validator('new_password')
    def password_not_same(cls, v, values):
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('La nuova password deve essere diversa da quella attuale')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldP@ssw0rd123!",
                "new_password": "NewSecureP@ssw0rd456!",
                "new_password_confirm": "NewSecureP@ssw0rd456!"
            }
        }


class AdminResetPasswordRequest(BaseModel):
    """Request per reset password (via email)."""
    
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@studiocentos.it"
            }
        }


class AdminResetPasswordConfirm(BaseModel):
    """Conferma reset password con token."""
    
    token: str = Field(..., min_length=32)
    new_password: str = Field(..., min_length=12)
    new_password_confirm: str = Field(..., min_length=12)
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Le password non corrispondono')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset-token-from-email",
                "new_password": "NewSecureP@ssw0rd789!",
                "new_password_confirm": "NewSecureP@ssw0rd789!"
            }
        }


class TokenResponse(BaseModel):
    """Response con JWT tokens."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Secondi prima della scadenza")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request per refresh del token."""
    
    refresh_token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# ============================================================================
# 2FA SCHEMAS
# ============================================================================

class Admin2FASetupResponse(BaseModel):
    """Response per setup 2FA."""
    
    secret: str = Field(..., description="Secret TOTP da salvare nell'app")
    qr_code_url: str = Field(..., description="URL per generare QR code")
    backup_codes: list[str] = Field(..., description="Codici di backup")
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code_url": "otpauth://totp/StudiocentOS:admin?secret=JBSWY3DPEHPK3PXP&issuer=StudiocentOS",
                "backup_codes": ["12345678", "87654321", "11223344"]
            }
        }


class Admin2FAVerifyRequest(BaseModel):
    """Request per verifica 2FA durante setup."""
    
    totp_token: str = Field(..., min_length=6, max_length=6)
    
    class Config:
        json_schema_extra = {
            "example": {
                "totp_token": "123456"
            }
        }


class Admin2FADisableRequest(BaseModel):
    """Request per disabilitare 2FA."""
    
    password: str = Field(..., description="Password corrente per conferma")
    totp_token: Optional[str] = Field(None, min_length=6, max_length=6, description="Token 2FA o backup code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "MySecureP@ssw0rd123!",
                "totp_token": "123456"
            }
        }


# ============================================================================
# ADMIN USER SCHEMAS
# ============================================================================

class AdminUserBase(BaseModel):
    """Base schema per admin user."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    role: AdminRole = AdminRole.ADMIN
    is_active: bool = True


class AdminUserCreate(AdminUserBase):
    """Schema per creazione admin user."""
    
    password: str = Field(..., min_length=12)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "newadmin",
                "email": "newadmin@studiocentos.it",
                "full_name": "Nuovo Amministratore",
                "role": "admin",
                "is_active": True,
                "password": "SecureP@ssw0rd123!"
            }
        }


class AdminUserUpdate(BaseModel):
    """Schema per update admin user."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "updated@studiocentos.it",
                "full_name": "Nome Aggiornato",
                "role": "moderator",
                "is_active": True
            }
        }


class AdminUserResponse(AdminUserBase):
    """Schema per response admin user."""
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_2fa_enabled: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@studiocentos.it",
                "full_name": "Amministratore Principale",
                "role": "super_admin",
                "is_active": True,
                "created_at": "2025-11-06T09:00:00Z",
                "updated_at": "2025-11-06T10:00:00Z",
                "last_login": "2025-11-06T09:30:00Z",
                "is_2fa_enabled": True,
                "failed_login_attempts": 0,
                "locked_until": None
            }
        }


class AdminUserListResponse(BaseModel):
    """Response per lista admin users."""
    
    total: int
    items: list[AdminUserResponse]
    page: int = 1
    page_size: int = 20
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 5,
                "items": [],
                "page": 1,
                "page_size": 20
            }
        }


# ============================================================================
# SESSION SCHEMAS
# ============================================================================

class AdminSessionResponse(BaseModel):
    """Response per sessione admin attiva."""
    
    id: int
    user_id: int
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_current: bool = False
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "created_at": "2025-11-06T09:00:00Z",
                "last_activity": "2025-11-06T09:30:00Z",
                "expires_at": "2025-11-13T09:00:00Z",
                "is_current": True
            }
        }


class AdminSessionListResponse(BaseModel):
    """Response per lista sessioni admin."""
    
    total: int
    items: list[AdminSessionResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "items": []
            }
        }


# ============================================================================
# AUDIT LOG SCHEMAS
# ============================================================================

class AdminAuditLogResponse(BaseModel):
    """Response per audit log."""
    
    id: int
    user_id: int
    username: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    ip_address: str
    user_agent: str
    details: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "username": "admin",
                "action": "login",
                "resource_type": None,
                "resource_id": None,
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "details": {"success": True},
                "created_at": "2025-11-06T09:00:00Z"
            }
        }


class AdminAuditLogListResponse(BaseModel):
    """Response per lista audit logs."""
    
    total: int
    items: list[AdminAuditLogResponse]
    page: int = 1
    page_size: int = 50
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "items": [],
                "page": 1,
                "page_size": 50
            }
        }
