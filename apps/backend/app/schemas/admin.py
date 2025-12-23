from pydantic import BaseModel, Field


class AdminUserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=6)


class AdminUserRead(AdminUserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class AdminLogin(BaseModel):
    username: str
    password: str
