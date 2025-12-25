"""
Courses Public Router - Public endpoints for landing page.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.infrastructure.database.session import get_db
from .schemas import CourseLocalizedResponse

router = APIRouter(prefix="/api/v1/courses", tags=["Courses - Public"])


@router.get("/public", response_model=List[CourseLocalizedResponse])
def list_public_courses(
    lang: str = Query("it", regex="^(it|en|es)$"),
    db: Session = Depends(get_db)
):
    """
    Lista corsi pubblici con traduzioni.
    Ritorna corsi attivi ordinati per module_number.
    """
    query = text("""
        SELECT 
            id, title, slug, description, icon, module_number,
            purchase_url, preview_url, duration_hours, difficulty,
            topics, price, is_featured, is_new, thumbnail_url, cover_image,
            translations
        FROM courses
        WHERE status = 'active' AND is_public = true
        ORDER BY module_number ASC, "order" ASC
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    courses = []
    for row in rows:
        # Get localized content
        translations = row.translations or {}
        localized = translations.get(lang, {}) if lang != "it" else {}
        
        courses.append(CourseLocalizedResponse(
            id=row.id,
            title=localized.get("title", row.title),
            slug=row.slug,
            description=localized.get("description", row.description),
            icon=row.icon,
            module_number=row.module_number,
            purchase_url=row.purchase_url,
            preview_url=row.preview_url,
            duration_hours=row.duration_hours,
            difficulty=row.difficulty,
            topics=row.topics or [],
            price=row.price,
            is_featured=row.is_featured,
            is_new=row.is_new,
            thumbnail_url=row.thumbnail_url,
            cover_image=row.cover_image,
        ))
    
    return courses
