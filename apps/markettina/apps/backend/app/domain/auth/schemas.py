"""
Pydantic models for authentication and users.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """User roles enumeration."""

    ADMIN = "admin"
    TRIAL = "trial"
    CUSTOMER = "customer"
    USER = "user"
    TESTER = "tester"
    PRO = "pro"

class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str | None = None
    full_name: str | None = None
    is_active: bool = True
    role: UserRole = UserRole.USER
    tenant_id: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Validate username format: 3-30 chars, alphanumeric + underscore only."""
        if v is None:
            return None
        if not 3 <= len(v) <= 30:
            raise ValueError("Username must be between 3 and 30 characters")
        if not v.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers and underscores")
        if v[0].isdigit():
            raise ValueError("Username cannot start with a number")
        return v.lower()  # Force lowercase

class UserCreate(UserBase):
    """User creation schema."""

    username: str  # Required for registration
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """User update schema."""

    username: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = None
    role: UserRole | None = None
    tenant_id: str | None = None

class UserRead(UserBase):
    """User read schema."""

    id: int
    username: str  # Always required in response
    created_at: datetime
    updated_at: datetime | None = None
    tenant_id: str | None = None
    trial_expires_at: datetime | None = None
    mfa_enabled: bool = False

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """JWT token schema."""

    access_token: str
    token_type: str = "bearer"
    user: UserRead | None = None

class TokenData(BaseModel):
    """Token data schema."""

    sub: str
    exp: datetime | None = None
    tenant_id: str | None = None

class PasswordReset(BaseModel):
    """Password reset schema."""

    token: str
    new_password: str = Field(..., min_length=8)

class PasswordChange(BaseModel):
    """Password change schema."""

    current_password: str
    new_password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str
