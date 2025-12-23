"""
Portfolio Admin Router - CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.infrastructure.database.session import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser

from .admin_service import PortfolioAdminService
from .admin_schemas import (
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse, ProjectListResponse,
    ServiceCreateRequest, ServiceUpdateRequest, ServiceResponse, ServiceListResponse,
    BulkOrderUpdate, BulkDeleteRequest, BulkToggleRequest
)

router = APIRouter(prefix="/api/v1/admin/portfolio", tags=["admin-portfolio"])


# ============================================================================
# PROJECTS ENDPOINTS
# ============================================================================

@router.post("/projects", response_model=ProjectResponse)
def create_project(
    data: ProjectCreateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea nuovo progetto (raw SQL to bypass OAuthToken)."""
    from sqlalchemy import text
    from fastapi import HTTPException, status
    from datetime import datetime
    import json

    # 1. Verifica slug univoco
    slug_check = text("SELECT id FROM projects WHERE slug = :slug")
    existing = db.execute(slug_check, {"slug": data.slug}).fetchone()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Progetto con slug '{data.slug}' già esistente"
        )

    # 2. Prepara valori (converti liste/dict a JSON)
    now = datetime.utcnow()

    # 3. INSERT
    insert_query = text("""
        INSERT INTO projects (
            title, slug, description, year, category,
            live_url, github_url, demo_url,
            technologies, metrics,
            status, is_featured, is_public, "order",
            thumbnail_url, images,
            created_at, updated_at
        ) VALUES (
            :title, :slug, :description, :year, :category,
            :live_url, :github_url, :demo_url,
            :technologies, :metrics,
            :status, :is_featured, :is_public, :order,
            :thumbnail_url, :images,
            :created_at, :updated_at
        )
        RETURNING id
    """)

    result = db.execute(insert_query, {
        "title": data.title,
        "slug": data.slug,
        "description": data.description,
        "year": data.year,
        "category": data.category,
        "live_url": data.live_url,
        "github_url": data.github_url,
        "demo_url": data.demo_url,
        "technologies": json.dumps(data.technologies),
        "metrics": json.dumps(data.metrics),
        "status": data.status,
        "is_featured": data.is_featured,
        "is_public": data.is_public,
        "order": data.order,
        "thumbnail_url": data.thumbnail_url,
        "images": json.dumps(data.images),
        "created_at": now,
        "updated_at": now
    })

    new_id = result.fetchone()[0]
    db.commit()

    # 4. Recupera progetto creato
    select_query = text("""
        SELECT id, title, slug, description, year, category,
               live_url, github_url, demo_url, technologies, metrics,
               status, is_featured, is_public, "order",
               thumbnail_url, images, created_at, updated_at
        FROM projects
        WHERE id = :project_id
    """)

    row = db.execute(select_query, {"project_id": new_id}).fetchone()

    return ProjectResponse(
        id=row[0],
        title=row[1],
        slug=row[2],
        description=row[3],
        year=row[4],
        category=row[5],
        live_url=row[6],
        github_url=row[7],
        demo_url=row[8],
        technologies=row[9] or [],
        metrics=row[10] or {},
        status=row[11],
        is_featured=row[12],
        is_public=row[13],
        order=row[14],
        thumbnail_url=row[15],
        images=row[16] or [],
        created_at=row[17],
        updated_at=row[18]
    )


@router.get("/projects", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    is_public: Optional[bool] = Query(None),
    order_by: str = Query("order"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Lista progetti con filtri e paginazione.
    TEMPORARY: Using raw SQL to bypass OAuthToken circular dependency.
    """
    from sqlalchemy import text
    from datetime import datetime

    # Build WHERE clause
    where_conditions = []
    params = {}

    if search:
        where_conditions.append("(title ILIKE :search OR description ILIKE :search)")
        params['search'] = f"%{search}%"
    if category:
        where_conditions.append("category = :category")
        params['category'] = category
    if status:
        where_conditions.append("status = :status")
        params['status'] = status
    if is_featured is not None:
        where_conditions.append("is_featured = :is_featured")
        params['is_featured'] = is_featured
    if is_public is not None:
        where_conditions.append("is_public = :is_public")
        params['is_public'] = is_public

    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

    # Order by
    order_mapping = {
        "order": "\"order\" ASC",
        "created_at": "created_at DESC",
        "updated_at": "updated_at DESC",
        "title": "title ASC"
    }
    order_clause = f"ORDER BY {order_mapping.get(order_by, 'order ASC')}"

    # Count total
    count_query = f"SELECT COUNT(*) FROM projects {where_clause}"
    total = db.execute(text(count_query), params).scalar()

    # Get projects
    offset = (page - 1) * page_size
    query = f"""
        SELECT id, title, slug, description, year, category,
               live_url, github_url, demo_url, technologies, metrics,
               status, is_featured, is_public, "order",
               thumbnail_url, images, created_at, updated_at
        FROM projects
        {where_clause}
        {order_clause}
        LIMIT :limit OFFSET :offset
    """
    params['limit'] = page_size
    params['offset'] = offset

    result = db.execute(text(query), params)
    rows = result.fetchall()

    # Convert to ProjectResponse
    projects = []
    for row in rows:
        projects.append(ProjectResponse(
            id=row[0],
            title=row[1],
            slug=row[2],
            description=row[3],
            year=row[4],
            category=row[5],
            live_url=row[6],
            github_url=row[7],
            demo_url=row[8],
            technologies=row[9] or [],
            metrics=row[10] or {},
            status=row[11],
            is_featured=row[12],
            is_public=row[13],
            order=row[14],
            thumbnail_url=row[15],
            images=row[16] or [],
            created_at=row[17],
            updated_at=row[18]
        ))

    return ProjectListResponse(
        items=projects,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Ottieni singolo progetto (raw SQL to bypass OAuthToken)."""
    from sqlalchemy import text
    from fastapi import HTTPException, status

    query = text("""
        SELECT id, title, slug, description, year, category,
               live_url, github_url, demo_url, technologies, metrics,
               status, is_featured, is_public, "order",
               thumbnail_url, images, created_at, updated_at
        FROM projects
        WHERE id = :project_id
    """)

    result = db.execute(query, {"project_id": project_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progetto {project_id} non trovato"
        )

    return ProjectResponse(
        id=row[0],
        title=row[1],
        slug=row[2],
        description=row[3],
        year=row[4],
        category=row[5],
        live_url=row[6],
        github_url=row[7],
        demo_url=row[8],
        technologies=row[9] or [],
        metrics=row[10] or {},
        status=row[11],
        is_featured=row[12],
        is_public=row[13],
        order=row[14],
        thumbnail_url=row[15],
        images=row[16] or [],
        created_at=row[17],
        updated_at=row[18]
    )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna progetto (raw SQL to bypass OAuthToken)."""
    from sqlalchemy import text
    from fastapi import HTTPException, status
    from datetime import datetime
    import json

    # 1. Verifica che progetto esista
    check_query = text("SELECT id FROM projects WHERE id = :project_id")
    existing = db.execute(check_query, {"project_id": project_id}).fetchone()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progetto {project_id} non trovato"
        )

    # 2. Ottieni solo campi forniti
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nessun campo da aggiornare fornito"
        )

    # 3. Se slug cambiato, verifica univocità
    if "slug" in update_data:
        slug_check = text("""
            SELECT id FROM projects
            WHERE slug = :slug AND id != :project_id
        """)
        duplicate = db.execute(slug_check, {
            "slug": update_data["slug"],
            "project_id": project_id
        }).fetchone()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Progetto con slug '{update_data['slug']}' già esistente"
            )

    # 4. Costruisci UPDATE dinamico
    set_clauses = []
    params = {"project_id": project_id}

    # Lista di parole riservate SQL che devono essere quotate
    reserved_words = {"order", "group", "select", "from", "where", "table", "index", "user", "key"}

    for field, value in update_data.items():
        # Converti liste/dict a JSON per PostgreSQL
        if isinstance(value, (list, dict)):
            params[field] = json.dumps(value)
        else:
            params[field] = value

        # Quota il nome campo se è una parola riservata SQL
        field_name = f'"{field}"' if field.lower() in reserved_words else field
        set_clauses.append(f"{field_name} = :{field}")

    # Aggiungi updated_at
    set_clauses.append("updated_at = :updated_at")
    params["updated_at"] = datetime.utcnow()

    # 5. Esegui UPDATE
    update_query = text(f"""
        UPDATE projects
        SET {', '.join(set_clauses)}
        WHERE id = :project_id
    """)

    db.execute(update_query, params)
    db.commit()

    # 6. Recupera progetto aggiornato
    select_query = text("""
        SELECT id, title, slug, description, year, category,
               live_url, github_url, demo_url, technologies, metrics,
               status, is_featured, is_public, "order",
               thumbnail_url, images, created_at, updated_at
        FROM projects
        WHERE id = :project_id
    """)

    result = db.execute(select_query, {"project_id": project_id})
    row = result.fetchone()

    return ProjectResponse(
        id=row[0],
        title=row[1],
        slug=row[2],
        description=row[3],
        year=row[4],
        category=row[5],
        live_url=row[6],
        github_url=row[7],
        demo_url=row[8],
        technologies=row[9] or [],
        metrics=row[10] or {},
        status=row[11],
        is_featured=row[12],
        is_public=row[13],
        order=row[14],
        thumbnail_url=row[15],
        images=row[16] or [],
        created_at=row[17],
        updated_at=row[18]
    )


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina progetto (raw SQL to bypass OAuthToken)."""
    from sqlalchemy import text
    from fastapi import HTTPException, status

    # Verifica che progetto esista
    check_query = text("SELECT id FROM projects WHERE id = :project_id")
    existing = db.execute(check_query, {"project_id": project_id}).fetchone()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Progetto {project_id} non trovato"
        )

    # Elimina
    delete_query = text("DELETE FROM projects WHERE id = :project_id")
    db.execute(delete_query, {"project_id": project_id})
    db.commit()

    return {"message": "Progetto eliminato con successo"}


@router.post("/projects/bulk/order")
def bulk_update_project_order(
    data: BulkOrderUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna ordine progetti multipli."""
    PortfolioAdminService.bulk_update_order(db, data.items)
    return {"message": "Ordine aggiornato con successo"}


@router.post("/projects/bulk/delete")
def bulk_delete_projects(
    data: BulkDeleteRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina progetti multipli."""
    PortfolioAdminService.bulk_delete(db, data.ids)
    return {"message": f"{len(data.ids)} progetti eliminati"}


@router.post("/projects/bulk/toggle")
def bulk_toggle_projects(
    data: BulkToggleRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Toggle campo progetti multipli."""
    PortfolioAdminService.bulk_toggle(db, data.ids, data.field, data.value)
    return {"message": f"Campo '{data.field}' aggiornato per {len(data.ids)} progetti"}


# ============================================================================
# SERVICES ENDPOINTS
# ============================================================================

@router.post("/services", response_model=ServiceResponse)
def create_service(
    data: ServiceCreateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea nuovo servizio."""
    return PortfolioAdminService.create_service(db, data)


@router.get("/services", response_model=ServiceListResponse)
def list_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_featured: Optional[bool] = Query(None),
    order_by: str = Query("order"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista servizi con filtri e paginazione."""
    return PortfolioAdminService.get_services(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        is_active=is_active,
        is_featured=is_featured,
        order_by=order_by
    )


@router.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Ottieni singolo servizio."""
    service = PortfolioAdminService.get_service(db, service_id)
    return ServiceResponse.model_validate(service)


@router.put("/services/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    data: ServiceUpdateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna servizio."""
    service = PortfolioAdminService.update_service(db, service_id, data)
    return ServiceResponse.model_validate(service)


@router.delete("/services/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina servizio."""
    PortfolioAdminService.delete_service(db, service_id)
    return {"message": "Servizio eliminato con successo"}


@router.post("/services/bulk/order")
def bulk_update_service_order(
    data: BulkOrderUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna ordine servizi multipli."""
    PortfolioAdminService.bulk_update_service_order(db, data.items)
    return {"message": "Ordine aggiornato con successo"}


@router.post("/services/bulk/delete")
def bulk_delete_services(
    data: BulkDeleteRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina servizi multipli."""
    PortfolioAdminService.bulk_delete_services(db, data.ids)
    return {"message": f"{len(data.ids)} servizi eliminati"}


@router.post("/services/bulk/toggle")
def bulk_toggle_services(
    data: BulkToggleRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Toggle campo servizi multipli."""
    PortfolioAdminService.bulk_toggle_services(db, data.ids, data.field, data.value)
    return {"message": f"Campo '{data.field}' aggiornato per {len(data.ids)} servizi"}
