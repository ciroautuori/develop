"""
ToolAI Service
Business logic for ToolAI domain.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .models import ToolAIPost, AITool, ToolAIPostStatus
from .schemas import ToolAIPostCreate, ToolAIPostUpdate, GeneratePostRequest

class ToolAIService:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================================================
    # PUBLIC METHODS
    # ==========================================================================

    def get_public_posts(self, page: int = 1, per_page: int = 10, lang: str = 'it') -> Dict[str, Any]:
        query = self.db.query(ToolAIPost).filter(
            ToolAIPost.status == ToolAIPostStatus.PUBLISHED,
            ToolAIPost.published_at <= datetime.utcnow()
        ).order_by(desc(ToolAIPost.post_date))

        total = query.count()
        posts = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "posts": posts
        }

    def get_latest_public_post(self, lang: str = 'it') -> Optional[ToolAIPost]:
        return self.db.query(ToolAIPost).filter(
            ToolAIPost.status == ToolAIPostStatus.PUBLISHED,
            ToolAIPost.published_at <= datetime.utcnow()
        ).order_by(desc(ToolAIPost.post_date)).first()

    def get_public_post_by_slug(self, slug: str, lang: str = 'it') -> Optional[ToolAIPost]:
        return self.db.query(ToolAIPost).filter(
            ToolAIPost.slug == slug,
            ToolAIPost.status == ToolAIPostStatus.PUBLISHED
        ).first()

    # ==========================================================================
    # ADMIN METHODS
    # ==========================================================================

    def get_all_posts(self, page: int = 1, per_page: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
        query = self.db.query(ToolAIPost)

        if status:
            query = query.filter(ToolAIPost.status == status)

        query = query.order_by(desc(ToolAIPost.post_date))

        total = query.count()
        posts = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "posts": posts
        }

    def get_post_by_id(self, post_id: int) -> Optional[ToolAIPost]:
        return self.db.query(ToolAIPost).filter(ToolAIPost.id == post_id).first()

    def update_post(self, post_id: int, data: ToolAIPostUpdate) -> Optional[ToolAIPost]:
        post = self.get_post_by_id(post_id)
        if not post:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(post, key, value)

        self.db.commit()
        self.db.refresh(post)
        return post

    def delete_post(self, post_id: int) -> bool:
        post = self.get_post_by_id(post_id)
        if not post:
            return False

        self.db.delete(post)
        self.db.commit()
        return True

    def publish_post(self, post_id: int) -> Optional[ToolAIPost]:
        post = self.get_post_by_id(post_id)
        if not post:
            return None

        post.status = ToolAIPostStatus.PUBLISHED
        post.published_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_stats(self) -> Dict[str, Any]:
        total = self.db.query(ToolAIPost).count()
        published = self.db.query(ToolAIPost).filter(ToolAIPost.status == ToolAIPostStatus.PUBLISHED).count()
        draft = self.db.query(ToolAIPost).filter(ToolAIPost.status == ToolAIPostStatus.DRAFT).count()
        tools = self.db.query(AITool).count()

        recent = self.db.query(ToolAIPost.id, ToolAIPost.post_date, ToolAIPost.title_it, ToolAIPost.status)\
            .order_by(desc(ToolAIPost.post_date))\
            .limit(5).all()

        return {
            "total_posts": total,
            "published_posts": published,
            "draft_posts": draft,
            "total_tools_discovered": tools,
            "recent_posts": [{"id": r.id, "date": r.post_date.isoformat(), "title": r.title_it, "status": r.status} for r in recent]
        }

    # ==========================================================================
    # AI GENERATION
    # ==========================================================================

    async def generate_post(self, request: GeneratePostRequest) -> Dict[str, Any]:
        """
        Genera un nuovo post ToolAI usando il scheduler singleton.
        """
        from app.infrastructure.scheduler.toolai_scheduler import toolai_scheduler

        # Aggiorna configurazione temporanea
        if request.num_tools:
            toolai_scheduler.num_tools = request.num_tools
        if request.categories:
            toolai_scheduler.categories = request.categories

        # Trigger generazione
        result = await toolai_scheduler.trigger_now()

        if not result.get("success"):
            return {
                "success": False,
                "post_id": None,
                "post": None,
                "tools_discovered": 0,
                "generation_time_seconds": 0,
                "ai_model": "unknown",
                "message": result.get("message", "Generation failed")
            }

        # Fetch post creato
        post_id = result.get("post_id")
        post = self.get_post_by_id(post_id) if post_id else None

        # Auto-publish se richiesto
        if post and request.auto_publish and post.status != ToolAIPostStatus.PUBLISHED:
            self.publish_post(post_id)
            post = self.get_post_by_id(post_id)

        return {
            "success": True,
            "post_id": post_id,
            "post": post,
            "tools_discovered": result.get("tools_count", 0),
            "generation_time_seconds": post.generation_time if post else 0,
            "ai_model": post.ai_model if post else "groq",
            "message": "Post generated successfully"
        }
