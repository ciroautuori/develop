from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    created_at: str
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserInfo
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
