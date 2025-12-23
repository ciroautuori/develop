from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.newspost import NewsPost
from app.schemas.news import NewsCreate, NewsUpdate


async def get_news_posts(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[NewsPost]:
    query = select(NewsPost).where(NewsPost.is_active == True)
    query = query.offset(skip).limit(limit).order_by(NewsPost.published_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_news_post_by_slug(db: AsyncSession, slug: str) -> Optional[NewsPost]:
    query = select(NewsPost).where(NewsPost.slug == slug, NewsPost.is_active == True)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_news_post_by_id(db: AsyncSession, news_id: int) -> Optional[NewsPost]:
    query = select(NewsPost).where(NewsPost.id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_news_post(db: AsyncSession, news: NewsCreate) -> NewsPost:
    db_news = NewsPost(**news.model_dump())
    db.add(db_news)
    await db.commit()
    await db.refresh(db_news)
    return db_news


async def update_news_post(db: AsyncSession, news_id: int, news_update: NewsUpdate) -> Optional[NewsPost]:
    db_news = await get_news_post_by_id(db, news_id)
    if not db_news:
        return None
    
    update_data = news_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_news, field, value)
    
    await db.commit()
    await db.refresh(db_news)
    return db_news


async def delete_news_post(db: AsyncSession, news_id: int) -> bool:
    db_news = await get_news_post_by_id(db, news_id)
    if not db_news:
        return False
    
    await db.delete(db_news)
    await db.commit()
    return True
