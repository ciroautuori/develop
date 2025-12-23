from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.api.deps import get_current_admin
from app.crud import news
from app.database.database import get_db
from app.schemas.news import NewsCreate, NewsRead, NewsUpdate
from app.models.admin import AdminUser

router = APIRouter()


@router.get("/", response_model=List[NewsRead])
@cache(expire=600)
async def get_news_posts(
    skip: int = 0,
    limit: int = 12,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all news posts (public endpoint)."""
    news_posts = await news.get_news_posts(db, skip=skip, limit=limit)
    return news_posts


@router.get("/{slug}", response_model=NewsRead)
@cache(expire=300)
async def get_news_post_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a news post by slug (public endpoint)."""
    db_news = await news.get_news_post_by_slug(db, slug=slug)
    if not db_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News post not found"
        )
    return db_news


@router.post("/", response_model=NewsRead)
async def create_news_post(
    news_data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Create a new news post (protected endpoint)."""
    return await news.create_news_post(db, news=news_data)


@router.put("/{news_id}", response_model=NewsRead)
async def update_news_post(
    news_id: int,
    news_data: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Update a news post (protected endpoint)."""
    db_news = await news.update_news_post(db, news_id=news_id, news_update=news_data)
    if not db_news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News post not found"
        )
    return db_news


@router.delete("/{news_id}")
async def delete_news_post(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete a news post (protected endpoint)."""
    success = await news.delete_news_post(db, news_id=news_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News post not found"
        )
    return {"message": "News post deleted successfully"}
