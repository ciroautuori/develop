"""
Portfolio API Router - Gestione prodotti e servizi StudiocentOS.
Supporta traduzioni multilingua (it, en, es).
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from app.infrastructure.database.session import get_db
from .models import Project, Service, ContactRequest
from .schemas import (
    ProjectResponse,
    ServiceResponse,
    ProjectLocalizedResponse,
    ServiceLocalizedResponse,
    ContactRequestCreate,
    ContactRequestResponse,
    PortfolioPublicResponse
)

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


# ============================================================================
# HELPER FUNCTIONS - Localizzazione contenuti
# ============================================================================

def localize_project(project: Project, lang: str = "it") -> dict:
    """Localizza un progetto nella lingua richiesta."""
    data = {
        "id": project.id,
        "title": project.title,
        "slug": project.slug,
        "description": project.description,
        "year": project.year,
        "category": project.category,
        "live_url": project.live_url,
        "github_url": project.github_url,
        "demo_url": project.demo_url,
        "technologies": project.technologies or [],
        "metrics": project.metrics or {},
        "status": project.status,
        "is_featured": project.is_featured,
        "is_public": project.is_public,
        "order": project.order,
        "thumbnail_url": project.thumbnail_url,
        "images": project.images or [],
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "translations": project.translations or {}
    }

    # Applica traduzioni se esistono per la lingua richiesta
    if lang != "it" and project.translations:
        trans = project.translations.get(lang, {})
        if trans:
            if trans.get("title"):
                data["title"] = trans["title"]
            if trans.get("description"):
                data["description"] = trans["description"]

    return data


def localize_service(service: Service, lang: str = "it") -> dict:
    """Localizza un servizio nella lingua richiesta."""
    data = {
        "id": service.id,
        "title": service.title,
        "slug": service.slug,
        "description": service.description,
        "icon": service.icon,
        "category": service.category,
        "features": service.features or [],
        "benefits": service.benefits or [],
        "value_indicator": service.value_indicator,
        "cta_text": service.cta_text,
        "cta_url": service.cta_url,
        "thumbnail_url": getattr(service, 'thumbnail_url', None),
        "is_active": service.is_active,
        "is_featured": service.is_featured,
        "order": service.order,
        "created_at": service.created_at,
        "updated_at": service.updated_at,
        "translations": service.translations or {}
    }

    # Applica traduzioni se esistono per la lingua richiesta
    if lang != "it" and service.translations:
        trans = service.translations.get(lang, {})
        if trans:
            if trans.get("title"):
                data["title"] = trans["title"]
            if trans.get("description"):
                data["description"] = trans["description"]
            if trans.get("features"):
                data["features"] = trans["features"]
            if trans.get("cta_text"):
                data["cta_text"] = trans["cta_text"]

    return data


# ============================================================================
# PUBLIC ENDPOINTS - Portfolio pubblico
# ============================================================================

@router.get("/public", response_model=PortfolioPublicResponse)
def get_public_portfolio(
    lang: str = Query("it", description="Lingua (it, en, es)"),
    db: Session = Depends(get_db)
):
    """
    Get public portfolio data (projects + services) from DATABASE.

    Endpoint pubblico per la landing page StudiocentOS.
    Legge dati REALI dal database PostgreSQL.
    Supporta traduzioni multilingua tramite parametro ?lang=
    """
    # Valida lingua
    if lang not in ["it", "en", "es"]:
        lang = "it"

    # Get public projects from database
    projects_query = select(Project).where(
        Project.is_public == True,
        Project.status == "active"
    ).order_by(Project.order, Project.created_at.desc())

    projects_result = db.execute(projects_query)
    projects = projects_result.scalars().all()

    # Get active services from database
    services_query = select(Service).where(
        Service.is_active == True
    ).order_by(Service.order, Service.created_at.desc())

    services_result = db.execute(services_query)
    services = services_result.scalars().all()

    # Calculate stats from real data
    total_technologies = 0
    for p in projects:
        if p.technologies:
            total_technologies += len(p.technologies)

    stats = {
        "total_projects": len(projects),
        "total_services": len(services),
        "years_experience": 4,
        "technologies": total_technologies
    }

    # Localizza i contenuti
    localized_projects = [localize_project(p, lang) for p in projects]
    localized_services = [localize_service(s, lang) for s in services]

    return {
        "projects": localized_projects,
        "services": localized_services,
        "stats": stats
    }


@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all public projects."""
    query = select(Project).where(
        Project.is_public == True,
        Project.status == "active"
    )

    if featured_only:
        query = query.where(Project.is_featured == True)

    query = query.order_by(Project.order, Project.created_at.desc())

    result = db.execute(query)
    projects = result.scalars().all()

    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/projects/{slug}", response_model=ProjectResponse)
def get_project_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get project by slug."""
    query = select(Project).where(
        Project.slug == slug,
        Project.is_public == True
    )

    result = db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse.model_validate(project)


@router.get("/services", response_model=List[ServiceResponse])
def get_services(
    category: str = None,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all active services."""
    query = select(Service).where(Service.is_active == True)

    if category:
        query = query.where(Service.category == category)

    if featured_only:
        query = query.where(Service.is_featured == True)

    query = query.order_by(Service.order, Service.created_at.desc())

    result = db.execute(query)
    services = result.scalars().all()

    return [ServiceResponse.model_validate(s) for s in services]


@router.get("/services/{slug}", response_model=ServiceResponse)
def get_service_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get service by slug."""
    query = select(Service).where(
        Service.slug == slug,
        Service.is_active == True
    )

    result = db.execute(query)
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return ServiceResponse.model_validate(service)


@router.post("/contact", response_model=ContactRequestResponse, status_code=201)
def create_contact_request(
    contact: ContactRequestCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create contact request.

    Endpoint per il form di contatto della landing page.
    """
    # Create contact request
    contact_request = ContactRequest(
        name=contact.name,
        email=contact.email,
        company=contact.company,
        phone=contact.phone,
        subject=contact.subject,
        message=contact.message,
        request_type=contact.request_type,
        status="new",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer")
    )

    db.add(contact_request)
    db.commit()
    db.refresh(contact_request)

    # Email notifications: Use email_service for admin/user notifications
    # Integration: email_service.send_notification() and send_confirmation()

    return ContactRequestResponse.model_validate(contact_request)


# ============================================================================
# ADMIN ENDPOINTS - Gestione portfolio (protected)
# ============================================================================

from app.core.api.dependencies.auth_deps import get_current_user
from app.core.api.dependencies.permissions import require_admin
from app.domain.auth.models import User


@router.get("/admin/services", response_model=List[ServiceResponse])
def admin_get_all_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all services (admin only) - including inactive."""
    query = select(Service).order_by(Service.order, Service.created_at.desc())
    result = db.execute(query)
    services = result.scalars().all()
    return [ServiceResponse.model_validate(s) for s in services]


@router.post("/admin/services", response_model=ServiceResponse, status_code=201)
def admin_create_service(
    service: ServiceResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new service (admin only)."""
    new_service = Service(
        title=service.title,
        slug=service.slug,
        description=service.description,
        icon=service.icon,
        category=service.category,
        features=service.features,
        value_indicator=service.value_indicator,
        cta_text=service.cta_text,
        cta_url=service.cta_url,
        is_active=service.is_active,
        is_featured=service.is_featured,
        order=service.order,
        translations=service.translations
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return ServiceResponse.model_validate(new_service)


@router.put("/admin/services/{service_id}", response_model=ServiceResponse)
def admin_update_service(
    service_id: int,
    service_update: ServiceResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update service (admin only)."""
    query = select(Service).where(Service.id == service_id)
    result = db.execute(query)
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Update fields
    service.title = service_update.title
    service.slug = service_update.slug
    service.description = service_update.description
    service.icon = service_update.icon
    service.category = service_update.category
    service.features = service_update.features
    service.value_indicator = service_update.value_indicator
    service.cta_text = service_update.cta_text
    service.cta_url = service_update.cta_url
    service.is_active = service_update.is_active
    service.is_featured = service_update.is_featured
    service.order = service_update.order
    service.translations = service_update.translations

    db.commit()
    db.refresh(service)

    return ServiceResponse.model_validate(service)


@router.delete("/admin/services/{service_id}", status_code=204)
def admin_delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete service (admin only)."""
    query = select(Service).where(Service.id == service_id)
    result = db.execute(query)
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()

    return None


@router.get("/admin/projects", response_model=List[ProjectResponse])
def admin_get_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all projects (admin only) - including private."""
    query = select(Project).order_by(Project.order, Project.created_at.desc())
    result = db.execute(query)
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("/admin/projects", response_model=ProjectResponse, status_code=201)
def admin_create_project(
    project: ProjectResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new project (admin only)."""
    new_project = Project(
        title=project.title,
        slug=project.slug,
        description=project.description,
        year=project.year,
        category=project.category,
        live_url=project.live_url,
        github_url=project.github_url,
        technologies=project.technologies,
        metrics=project.metrics,
        is_public=project.is_public,
        is_featured=project.is_featured,
        status=project.status,
        order=project.order,
        translations=project.translations
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return ProjectResponse.model_validate(new_project)


@router.put("/admin/projects/{project_id}", response_model=ProjectResponse)
def admin_update_project(
    project_id: int,
    project_update: ProjectResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update project (admin only)."""
    query = select(Project).where(Project.id == project_id)
    result = db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    project.title = project_update.title
    project.slug = project_update.slug
    project.description = project_update.description
    project.year = project_update.year
    project.category = project_update.category
    project.live_url = project_update.live_url
    project.github_url = project_update.github_url
    project.technologies = project_update.technologies
    project.metrics = project_update.metrics
    project.is_public = project_update.is_public
    project.is_featured = project_update.is_featured
    project.status = project_update.status
    project.order = project_update.order
    project.translations = project_update.translations

    db.commit()
    db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.delete("/admin/projects/{project_id}", status_code=204)
def admin_delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete project (admin only)."""
    query = select(Project).where(Project.id == project_id)
    result = db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return None


@router.get("/health")
async def portfolio_health():
    """Health check for portfolio service."""
    return {
        "status": "healthy",
        "service": "portfolio",
        "endpoints": [
            "GET /public",
            "GET /projects",
            "GET /services",
            "POST /contact"
        ]
    }


# ============================================================================
# AI TRANSLATION PROXY - Proxy to AI microservice for translations
# ============================================================================

import httpx
import os
from pydantic import BaseModel

class TranslateRequest(BaseModel):
    title: str
    description: str
    source_language: str = "it"
    target_languages: list = ["en", "es"]


@router.post("/admin/translate")
async def admin_translate_portfolio(
    request: TranslateRequest,
    current_user: User = Depends(require_admin)
):
    """
    Proxy to AI microservice for portfolio translation.
    Translates title and description to target languages using AI.
    """
    ai_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
    ai_api_key = os.getenv("AI_SERVICE_API_KEY", "dev-api-key-change-in-production")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{ai_url}/api/v1/marketing/translate/portfolio",
                json={
                    "title": request.title,
                    "description": request.description,
                    "source_language": request.source_language,
                    "target_languages": request.target_languages
                },
                headers={"Authorization": f"Bearer {ai_api_key}"}
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI service error: {response.text}"
                )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
