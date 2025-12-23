"""
Courses Admin Router - CRUD endpoints for backoffice.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
import json
from datetime import datetime

from app.infrastructure.database.session import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser
from .schemas import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse
)
from .ai_service import courses_ai_service

router = APIRouter(prefix="/api/v1/admin/courses", tags=["Courses - Admin"])


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea nuovo corso with AI Translation."""
    # Check slug uniqueness
    check_query = text("SELECT id FROM courses WHERE slug = :slug")
    existing = db.execute(check_query, {"slug": data.slug}).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Slug già esistente")
    
    # AI Translation if missing
    if not data.translations:
        try:
            translations = await courses_ai_service.translate_course_content(data.title, data.description)
            if translations:
                data.translations = translations
        except Exception as e:
            # Fallback to empty if AI fails, don't block creation
            pass
    
    insert_query = text("""
        INSERT INTO courses (
            title, slug, description, icon, module_number,
            purchase_url, preview_url, duration_hours, difficulty,
            topics, price, translations, status, is_featured, is_new,
            is_public, "order", thumbnail_url, cover_image,
            created_at, updated_at
        ) VALUES (
            :title, :slug, :description, :icon, :module_number,
            :purchase_url, :preview_url, :duration_hours, :difficulty,
            :topics, :price, :translations, :status, :is_featured, :is_new,
            :is_public, :order, :thumbnail_url, :cover_image,
            :created_at, :updated_at
        ) RETURNING *
    """)
    
    # Ensure translations is handled as dict/json
    translations_json = json.dumps(data.translations) if data.translations else "{}"

    now = datetime.utcnow()
    result = db.execute(insert_query, {
        "title": data.title,
        "slug": data.slug,
        "description": data.description,
        "icon": data.icon,
        "module_number": data.module_number,
        "purchase_url": data.purchase_url,
        "preview_url": data.preview_url,
        "duration_hours": data.duration_hours,
        "difficulty": data.difficulty,
        "topics": json.dumps(data.topics),
        "price": data.price,
        "translations": translations_json,
        "status": data.status,
        "is_featured": data.is_featured,
        "is_new": data.is_new,
        "is_public": data.is_public,
        "order": data.order,
        "thumbnail_url": data.thumbnail_url,
        "cover_image": data.cover_image,
        "created_at": now,
        "updated_at": now,
    })
    db.commit()
    
    row = result.fetchone()
    return _row_to_response(row)


@router.get("", response_model=CourseListResponse)
def list_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    order_by: str = Query("module_number"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista corsi con filtri e paginazione."""
    # Build WHERE clause
    conditions = ["1=1"]
    params = {}
    
    if search:
        conditions.append("(title ILIKE :search OR description ILIKE :search)")
        params["search"] = f"%{search}%"
    if status:
        conditions.append("status = :status")
        params["status"] = status
    if is_featured is not None:
        conditions.append("is_featured = :is_featured")
        params["is_featured"] = is_featured
    
    where_clause = " AND ".join(conditions)
    
    # Count total
    count_query = text(f"SELECT COUNT(*) FROM courses WHERE {where_clause}")
    total = db.execute(count_query, params).scalar()
    
    # Fetch page
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset
    
    order_column = "module_number" if order_by == "module_number" else '"order"'
    data_query = text(f"""
        SELECT * FROM courses
        WHERE {where_clause}
        ORDER BY {order_column} ASC
        LIMIT :limit OFFSET :offset
    """)
    
    rows = db.execute(data_query, params).fetchall()
    
    return CourseListResponse(
        items=[_row_to_response(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Ottieni singolo corso."""
    query = text("SELECT * FROM courses WHERE id = :id")
    row = db.execute(query, {"id": course_id}).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Corso non trovato")
    
    return _row_to_response(row)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna corso."""
    # Check exists
    check_query = text("SELECT id FROM courses WHERE id = :id")
    existing = db.execute(check_query, {"id": course_id}).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Corso non trovato")
    
    # AI Translation for Update if translations cleared or empty
    if data.translations == {} or data.translations is None:
        # Fetch current if needed, or use new data
        current_title = data.title # Might be None if partial update? No, Pydantic fields optional?
        # For update it's complicated because fields are optional. 
        # But if user actively saves form, we likely want to translate if empty.
        # Simplification: Only translate if title and description are present in update data
        if data.title and data.description:
             try:
                translations = await courses_ai_service.translate_course_content(data.title, data.description)
                if translations:
                    data.translations = translations
             except:
                pass

    # Build UPDATE
    update_fields = []
    params = {"id": course_id, "updated_at": datetime.utcnow()}
    
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            if field in ["topics", "translations"]:
                params[field] = json.dumps(value)
            else:
                params[field] = value
            update_fields.append(f"{field} = :{field}")
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="Nessun campo da aggiornare")
    
    update_fields.append("updated_at = :updated_at")
    
    update_query = text(f"""
        UPDATE courses SET {', '.join(update_fields)}
        WHERE id = :id
        RETURNING *
    """)
    
    result = db.execute(update_query, params)
    db.commit()
    
    row = result.fetchone()
    return _row_to_response(row)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina corso."""
    delete_query = text("DELETE FROM courses WHERE id = :id RETURNING id")
    result = db.execute(delete_query, {"id": course_id}).fetchone()
    db.commit()
    
    if not result:
        raise HTTPException(status_code=404, detail="Corso non trovato")


@router.post("/bulk/order")
def bulk_update_order(
    items: List[dict],
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna ordine corsi multipli."""
    for item in items:
        query = text('UPDATE courses SET "order" = :order WHERE id = :id')
        db.execute(query, {"id": item["id"], "order": item["order"]})
    db.commit()
    return {"message": f"Aggiornati {len(items)} corsi"}


# ============================================================================
# HELPERS
# ============================================================================

def _row_to_response(row) -> CourseResponse:
    """Convert DB row to Pydantic response."""
    topics = row.topics if isinstance(row.topics, list) else json.loads(row.topics or "[]")
    translations = row.translations if isinstance(row.translations, dict) else json.loads(row.translations or "{}")
    
    return CourseResponse(
        id=row.id,
        title=row.title,
        slug=row.slug,
        description=row.description,
        icon=row.icon,
        module_number=row.module_number,
        purchase_url=row.purchase_url,
        preview_url=row.preview_url,
        duration_hours=row.duration_hours,
        difficulty=row.difficulty,
        topics=topics,
        price=row.price,
        translations=translations,
        status=row.status,
        is_featured=row.is_featured,
        is_new=row.is_new,
        is_public=row.is_public,
        order=row.order,
        thumbnail_url=row.thumbnail_url,
        cover_image=row.cover_image,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
