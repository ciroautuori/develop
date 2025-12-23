"""
Portfolio Admin Service - Business logic per CRUD
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from fastapi import HTTPException, status

from .models import Project, Service
from .admin_schemas import (
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse, ProjectListResponse,
    ServiceCreateRequest, ServiceUpdateRequest, ServiceResponse, ServiceListResponse
)


class PortfolioAdminService:
    """Servizio per gestione admin portfolio."""
    
    # ========================================================================
    # PROJECTS CRUD
    # ========================================================================
    
    @staticmethod
    def create_project(db: Session, data: ProjectCreateRequest) -> Project:
        """Crea nuovo progetto."""
        # Check slug univoco
        existing = db.execute(
            select(Project).where(Project.slug == data.slug)
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Progetto con slug '{data.slug}' già esistente"
            )
        
        project = Project(**data.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def get_projects(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_public: Optional[bool] = None,
        order_by: str = "order"
    ) -> ProjectListResponse:
        """Ottieni lista progetti con filtri e paginazione."""
        query = select(Project)
        
        # Filtri
        if search:
            query = query.where(
                or_(
                    Project.title.ilike(f"%{search}%"),
                    Project.description.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.where(Project.category == category)
        
        if status:
            query = query.where(Project.status == status)
        
        if is_featured is not None:
            query = query.where(Project.is_featured == is_featured)
        
        if is_public is not None:
            query = query.where(Project.is_public == is_public)
        
        # Count totale
        total = db.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar()
        
        # Ordinamento
        if order_by == "order":
            query = query.order_by(Project.order.asc())
        elif order_by == "created_at":
            query = query.order_by(Project.created_at.desc())
        elif order_by == "updated_at":
            query = query.order_by(Project.updated_at.desc())
        elif order_by == "title":
            query = query.order_by(Project.title.asc())
        
        # Paginazione
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        projects = db.execute(query).scalars().all()
        
        return ProjectListResponse(
            items=[ProjectResponse.model_validate(p) for p in projects],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    @staticmethod
    def get_project(db: Session, project_id: int) -> Project:
        """Ottieni singolo progetto."""
        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Progetto {project_id} non trovato"
            )
        return project
    
    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        data: ProjectUpdateRequest
    ) -> Project:
        """Aggiorna progetto."""
        project = PortfolioAdminService.get_project(db, project_id)
        
        # Check slug univoco se modificato
        if data.slug and data.slug != project.slug:
            existing = db.execute(
                select(Project).where(Project.slug == data.slug)
            ).scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Progetto con slug '{data.slug}' già esistente"
                )
        
        # Aggiorna campi
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: int):
        """Elimina progetto."""
        project = PortfolioAdminService.get_project(db, project_id)
        db.delete(project)
        db.commit()
    
    @staticmethod
    def bulk_update_order(db: Session, items: List[Dict[str, int]]):
        """Aggiorna ordine multiplo."""
        for item in items:
            project_id = item.get("id")
            order = item.get("order")
            
            if project_id and order is not None:
                project = db.get(Project, project_id)
                if project:
                    project.order = order
        
        db.commit()
    
    @staticmethod
    def bulk_delete(db: Session, ids: List[int]):
        """Elimina progetti multipli."""
        db.execute(
            select(Project).where(Project.id.in_(ids))
        ).scalars().all()
        
        for project_id in ids:
            project = db.get(Project, project_id)
            if project:
                db.delete(project)
        
        db.commit()
    
    @staticmethod
    def bulk_toggle(db: Session, ids: List[int], field: str, value: bool):
        """Toggle campo multiplo."""
        valid_fields = ["is_featured", "is_public"]
        
        if field not in valid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campo '{field}' non valido. Validi: {valid_fields}"
            )
        
        for project_id in ids:
            project = db.get(Project, project_id)
            if project:
                setattr(project, field, value)
        
        db.commit()
    
    # ========================================================================
    # SERVICES CRUD
    # ========================================================================
    
    @staticmethod
    def create_service(db: Session, data: ServiceCreateRequest) -> Service:
        """Crea nuovo servizio."""
        # Check slug univoco
        existing = db.execute(
            select(Service).where(Service.slug == data.slug)
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Servizio con slug '{data.slug}' già esistente"
            )
        
        service = Service(**data.model_dump())
        db.add(service)
        db.commit()
        db.refresh(service)
        
        return service
    
    @staticmethod
    def get_services(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        order_by: str = "order"
    ) -> ServiceListResponse:
        """Ottieni lista servizi con filtri e paginazione."""
        query = select(Service)
        
        # Filtri
        if search:
            query = query.where(
                or_(
                    Service.title.ilike(f"%{search}%"),
                    Service.description.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.where(Service.category == category)
        
        if is_active is not None:
            query = query.where(Service.is_active == is_active)
        
        if is_featured is not None:
            query = query.where(Service.is_featured == is_featured)
        
        # Count totale
        total = db.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar()
        
        # Ordinamento
        if order_by == "order":
            query = query.order_by(Service.order.asc())
        elif order_by == "created_at":
            query = query.order_by(Service.created_at.desc())
        elif order_by == "title":
            query = query.order_by(Service.title.asc())
        
        # Paginazione
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        services = db.execute(query).scalars().all()
        
        return ServiceListResponse(
            items=[ServiceResponse.model_validate(s) for s in services],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    
    @staticmethod
    def get_service(db: Session, service_id: int) -> Service:
        """Ottieni singolo servizio."""
        service = db.get(Service, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servizio {service_id} non trovato"
            )
        return service
    
    @staticmethod
    def update_service(
        db: Session,
        service_id: int,
        data: ServiceUpdateRequest
    ) -> Service:
        """Aggiorna servizio."""
        service = PortfolioAdminService.get_service(db, service_id)
        
        # Check slug univoco se modificato
        if data.slug and data.slug != service.slug:
            existing = db.execute(
                select(Service).where(Service.slug == data.slug)
            ).scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Servizio con slug '{data.slug}' già esistente"
                )
        
        # Aggiorna campi
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)
        
        db.commit()
        db.refresh(service)
        
        return service
    
    @staticmethod
    def delete_service(db: Session, service_id: int):
        """Elimina servizio."""
        service = PortfolioAdminService.get_service(db, service_id)
        db.delete(service)
        db.commit()
    
    @staticmethod
    def bulk_update_service_order(db: Session, items: List[Dict[str, int]]):
        """Aggiorna ordine servizi multiplo."""
        for item in items:
            service_id = item.get("id")
            order = item.get("order")
            
            if service_id and order is not None:
                service = db.get(Service, service_id)
                if service:
                    service.order = order
        
        db.commit()
    
    @staticmethod
    def bulk_delete_services(db: Session, ids: List[int]):
        """Elimina servizi multipli."""
        for service_id in ids:
            service = db.get(Service, service_id)
            if service:
                db.delete(service)
        
        db.commit()
    
    @staticmethod
    def bulk_toggle_services(db: Session, ids: List[int], field: str, value: bool):
        """Toggle campo servizi multiplo."""
        valid_fields = ["is_active", "is_featured"]
        
        if field not in valid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campo '{field}' non valido. Validi: {valid_fields}"
            )
        
        for service_id in ids:
            service = db.get(Service, service_id)
            if service:
                setattr(service, field, value)
        
        db.commit()
