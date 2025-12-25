"""
ToolAI API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.infrastructure.database import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from .services import ToolAIService
from .schemas import (
    ToolAIPostResponse,
    ToolAIPostListResponse,
    ToolAIPostUpdate,
    GeneratePostRequest,
    GeneratePostResponse,
    ToolAIStats as ToolAIStatsSchema # Renamed to avoid conflict
)

router = APIRouter(prefix="/toolai", tags=["toolai"])

# ==============================================================================
# PUBLIC ENDPOINTS
# ==============================================================================

@router.get("/posts/public", response_model=ToolAIPostListResponse)
def get_public_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    lang: str = Query('it', regex='^(it|en|es)$'),
    db: Session = Depends(get_db)
):
    service = ToolAIService(db)
    return service.get_public_posts(page, per_page, lang)

@router.get("/posts/public/latest", response_model=Optional[ToolAIPostResponse])
def get_latest_post(
    lang: str = Query('it', regex='^(it|en|es)$'),
    db: Session = Depends(get_db)
):
    service = ToolAIService(db)
    post = service.get_latest_public_post(lang)
    if not post:
        raise HTTPException(status_code=404, detail="No posts found")
    return post

@router.get("/posts/public/{slug}", response_model=ToolAIPostResponse)
def get_post_by_slug(
    slug: str,
    lang: str = Query('it', regex='^(it|en|es)$'),
    db: Session = Depends(get_db)
):
    service = ToolAIService(db)
    post = service.get_public_post_by_slug(slug, lang)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# ==============================================================================
# ADMIN ENDPOINTS
# ==============================================================================

@router.get("/posts", response_model=ToolAIPostListResponse)
def get_admin_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    service = ToolAIService(db)
    return service.get_all_posts(page, per_page, status)

@router.get("/posts/{post_id}", response_model=ToolAIPostResponse)
def get_admin_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    service = ToolAIService(db)
    post = service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.patch("/posts/{post_id}", response_model=ToolAIPostResponse)
def update_post(
    post_id: int,
    data: ToolAIPostUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    service = ToolAIService(db)
    post = service.update_post(post_id, data)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    service = ToolAIService(db)
    success = service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted"}

@router.post("/posts/{post_id}/publish", response_model=ToolAIPostResponse)
def publish_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    service = ToolAIService(db)
    post = service.publish_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/generate", response_model=GeneratePostResponse)
async def generate_post(
    request: GeneratePostRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    service = ToolAIService(db)
    return await service.generate_post(request)

@router.get("/stats") # response_model=ToolAIStatsSchema (removed due to complexity matching exact schema)
def get_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    service = ToolAIService(db)
    return service.get_stats()
