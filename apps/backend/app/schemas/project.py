from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    excerpt: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    image_url: str = Field(..., min_length=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    excerpt: Optional[str] = Field(None, min_length=1, max_length=300)
    content: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = Field(None, min_length=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
