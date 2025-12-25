"""
Post Scheduler - Pubblicazione automatica post social media.

Utilizza APScheduler per eseguire job di pubblicazione
al momento programmato per ogni post.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import structlog

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from sqlalchemy import select, and_

from app.infrastructure.database import SessionLocal
from app.domain.marketing.models import ScheduledPost, PostStatus
from app.integrations.social_media import SocialMediaIntegration

logger = structlog.get_logger(__name__)


class PostScheduler:
    """
    Scheduler per pubblicazione automatica post social.

    Features:
    - Scheduling preciso al minuto
    - Retry automatico in caso di fallimento
    - Multi-piattaforma in parallelo
    - Metrics tracking post-pubblicazione
    """

    _instance: Optional['PostScheduler'] = None

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            job_defaults={
                'coalesce': True,
                'max_instances': 3,
                'misfire_grace_time': 300  # 5 minuti di tolleranza
            }
        )
        self.social_media = SocialMediaIntegration()
        self._is_running = False

    @classmethod
    def get_instance(cls) -> 'PostScheduler':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def start(self):
        """Avvia lo scheduler e carica i job pendenti."""
        if self._is_running:
            logger.warning("scheduler_already_running")
            return

        try:
            # Avvia scheduler
            self.scheduler.start()
            self._is_running = True

            # Job periodico per controllare post da pubblicare
            self.scheduler.add_job(
                self._check_pending_posts,
                trigger=IntervalTrigger(minutes=1),
                id='check_pending_posts',
                replace_existing=True
            )

            # Job per aggiornamento metriche
            self.scheduler.add_job(
                self._update_metrics,
                trigger=IntervalTrigger(hours=1),
                id='update_metrics',
                replace_existing=True
            )

            # Carica post già schedulati dal database
            await self._load_scheduled_posts()

            logger.info("post_scheduler_started")

        except Exception as e:
            logger.error("scheduler_start_error", error=str(e))
            raise

    async def stop(self):
        """Ferma lo scheduler."""
        if self._is_running:
            self.scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("post_scheduler_stopped")

    async def schedule_post(self, post_id: int, scheduled_at: datetime) -> bool:
        """
        Programma un post per la pubblicazione.

        Args:
            post_id: ID del post da schedulare
            scheduled_at: Datetime di pubblicazione

        Returns:
            True se schedulato con successo
        """
        try:
            job_id = f"publish_post_{post_id}"

            # Rimuovi job esistente se presente
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # Aggiungi nuovo job
            self.scheduler.add_job(
                self._publish_post,
                trigger=DateTrigger(run_date=scheduled_at),
                args=[post_id],
                id=job_id,
                replace_existing=True
            )

            logger.info("post_scheduled", post_id=post_id, scheduled_at=scheduled_at.isoformat())
            return True

        except Exception as e:
            logger.error("schedule_post_error", post_id=post_id, error=str(e))
            return False

    async def cancel_post(self, post_id: int) -> bool:
        """Cancella uno scheduled post."""
        try:
            job_id = f"publish_post_{post_id}"

            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info("post_cancelled", post_id=post_id)
                return True

            return False

        except Exception as e:
            logger.error("cancel_post_error", post_id=post_id, error=str(e))
            return False

    async def _load_scheduled_posts(self):
        """Carica tutti i post schedulati dal database."""
        try:
            db = SessionLocal()
            try:
                now = datetime.utcnow()
                posts = db.query(ScheduledPost).filter(
                    and_(
                        ScheduledPost.status == PostStatus.SCHEDULED,
                        ScheduledPost.scheduled_at > now
                    )
                ).all()

                for post in posts:
                    await self.schedule_post(post.id, post.scheduled_at)

                logger.info("loaded_scheduled_posts", count=len(posts))
            finally:
                db.close()
        except Exception as e:
            logger.error("load_scheduled_posts_error", error=str(e))

    async def _check_pending_posts(self):
        """
        Controlla post che devono essere pubblicati.
        Job eseguito ogni minuto.
        """
        try:
            db = SessionLocal()
            try:
                now = datetime.utcnow()
                window = now + timedelta(minutes=2)

                posts = db.query(ScheduledPost).filter(
                    and_(
                        ScheduledPost.status == PostStatus.SCHEDULED,
                        ScheduledPost.scheduled_at <= window,
                        ScheduledPost.scheduled_at >= now - timedelta(minutes=5)
                    )
                ).all()

                for post in posts:
                    job_id = f"publish_post_{post.id}"
                    if not self.scheduler.get_job(job_id):
                        if post.scheduled_at <= now:
                            asyncio.create_task(self._publish_post(post.id))
                        else:
                            await self.schedule_post(post.id, post.scheduled_at)
            finally:
                db.close()

        except Exception as e:
            logger.error("check_pending_posts_error", error=str(e))

    async def _publish_post(self, post_id: int):
        """
        Pubblica un post su tutte le piattaforme configurate.

        Args:
            post_id: ID del post da pubblicare
        """
        logger.info("publishing_post", post_id=post_id)

        db = SessionLocal()
        try:
            post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

            if not post:
                logger.error("post_not_found", post_id=post_id)
                return

            if post.status not in [PostStatus.SCHEDULED, PostStatus.FAILED]:
                logger.warning("post_invalid_status", post_id=post_id, status=post.status.value)
                return

            # Aggiorna status a PUBLISHING
            post.status = PostStatus.PUBLISHING
            db.commit()

            # Pubblica su ogni piattaforma
            platforms = post.platforms or []
            platform_results = {}
            all_success = True

            for platform in platforms:
                try:
                    result = await self.social_media.publish_post(
                        platform=platform,
                        content=post.content,
                        media_urls=post.media_urls if post.media_urls else None
                    )

                    platform_results[platform] = result

                    if result.get('status') != 'success':
                        all_success = False

                except Exception as e:
                    platform_results[platform] = {
                        'status': 'error',
                        'message': str(e)
                    }
                    all_success = False

            # Aggiorna post con risultati
            post.platform_results = platform_results
            post.published_at = datetime.utcnow()

            if all_success:
                post.status = PostStatus.PUBLISHED
                logger.info("post_published", post_id=post_id, platforms=platforms)
            else:
                if post.retry_count < post.max_retries:
                    post.retry_count += 1
                    post.status = PostStatus.SCHEDULED
                    post.scheduled_at = datetime.utcnow() + timedelta(minutes=15)
                    await self.schedule_post(post.id, post.scheduled_at)
                    logger.warning("post_retry_scheduled", post_id=post_id, retry=post.retry_count)
                else:
                    post.status = PostStatus.FAILED
                    post.error_message = "Max retries exceeded"
                    logger.error("post_failed", post_id=post_id)

            db.commit()

        except Exception as e:
            logger.error("publish_post_error", post_id=post_id, error=str(e))
            try:
                post.status = PostStatus.FAILED
                post.error_message = str(e)
                db.commit()
            except:
                pass
        finally:
            db.close()

    async def _update_metrics(self):
        """
        Aggiorna le metriche dei post pubblicati.
        Job eseguito ogni ora.
        """
        try:
            db = SessionLocal()
            try:
                cutoff = datetime.utcnow() - timedelta(hours=48)

                posts = db.query(ScheduledPost).filter(
                    and_(
                        ScheduledPost.status == PostStatus.PUBLISHED,
                        ScheduledPost.published_at >= cutoff
                    )
                ).all()

                for post in posts:
                    updated_metrics = {}

                    for platform, res in (post.platform_results or {}).items():
                        if res.get('status') == 'success' and res.get('post_id'):
                            try:
                                metrics = await self.social_media.get_engagement_metrics(
                                    platform=platform,
                                    post_id=res['post_id']
                                )
                                updated_metrics[platform] = metrics
                            except:
                                pass

                    if updated_metrics:
                        post.metrics = updated_metrics

                db.commit()
                logger.info("metrics_updated", count=len(posts))
            finally:
                db.close()

        except Exception as e:
            logger.error("update_metrics_error", error=str(e))


# Singleton instance
post_scheduler = PostScheduler.get_instance()


async def start_post_scheduler():
    """Avvia il post scheduler."""
    await post_scheduler.start()


async def stop_post_scheduler():
    """Ferma il post scheduler."""
    await post_scheduler.stop()
