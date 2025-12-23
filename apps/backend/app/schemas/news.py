from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    excerpt: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    image_url: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    published_at: datetime
    is_active: bool = True


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    excerpt: Optional[str] = Field(None, min_length=1, max_length=300)
    content: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    published_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class NewsRead(NewsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
