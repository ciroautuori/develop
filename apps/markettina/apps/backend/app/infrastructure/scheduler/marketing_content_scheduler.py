"""
Marketing Content Daily Scheduler - Generazione automatica contenuti social.

Utilizza APScheduler per generare batch content giornaliero:
- 1 post per platform (Instagram, Facebook, TikTok, LinkedIn)
- 3 stories (Instagram/Facebook)
- 1 video (Reels/TikTok)

Schedule: Ogni giorno alle 7:00 AM CET per preparare contenuti da pubblicare durante la giornata.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
import structlog
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.domain.marketing.models import PostStatus, ScheduledPost
from app.infrastructure.database import SessionLocal

logger = structlog.get_logger(__name__)


class MarketingContentScheduler:
    """
    Scheduler per generazione automatica batch content marketing.

    Genera ogni giorno alle 7:00 AM un batch completo di contenuti:
    - 4 post (Instagram 1:1, Facebook 16:9, TikTok 9:16, LinkedIn 1:1)
    - 3 stories (Instagram/Facebook 9:16)
    - 1 video (15s Reel/TikTok con audio nativo)

    I contenuti vengono salvati come ScheduledPost e possono essere:
    - Auto-pubblicati immediatamente
    - Schedulati per orari ottimali
    - Revisionati manualmente prima della pubblicazione
    """

    _instance: Optional["MarketingContentScheduler"] = None

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={"default": MemoryJobStore()},
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 3600  # 1 ora di tolleranza
            },
            timezone="Europe/Rome"  # CET/CEST
        )
        self._is_running = False

        # Configuration from env
        self.ai_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
        self.ai_api_key = os.getenv("AI_SERVICE_API_KEY", "dev-api-key-change-in-production")

        # Schedule configuration
        self.schedule_hour = int(os.getenv("MARKETING_SCHEDULE_HOUR", "7"))  # 07:00 AM CET
        self.schedule_minute = int(os.getenv("MARKETING_SCHEDULE_MINUTE", "0"))

        # Content configuration
        self.enabled = os.getenv("MARKETING_AUTO_GENERATION", "false").lower() == "true"
        self.platforms = os.getenv("MARKETING_PLATFORMS", "instagram,facebook,tiktok,linkedin").split(",")
        self.post_count = int(os.getenv("MARKETING_POST_COUNT", "1"))  # Per platform
        self.story_count = int(os.getenv("MARKETING_STORY_COUNT", "3"))
        self.video_count = int(os.getenv("MARKETING_VIDEO_COUNT", "1"))
        self.use_pro_quality = os.getenv("MARKETING_USE_PRO", "false").lower() == "true"
        self.auto_publish = os.getenv("MARKETING_AUTO_PUBLISH", "false").lower() == "true"

        # Topic configuration - rotating topics
        self.topics = self._load_topics()

    def _load_topics(self) -> list[str]:
        """
        Carica i topic per la generazione automatica.
        Può essere da env var o da configurazione dinamica.
        """
        topics_env = os.getenv("MARKETING_TOPICS", "")

        if topics_env:
            return [t.strip() for t in topics_env.split("|") if t.strip()]

        # Default topics per MARKETTINA
        return [
            "Digitalizzazione per PMI italiane - Innovazione tecnologica",
            "Strategie di Marketing Digitale per aziende B2B",
            "Automazione AI per servizi professionali",
            "Trasformazione digitale nel settore manifatturiero",
            "Social Media Marketing per il 2025",
            "SEO e visibilità online per piccole imprese",
            "Customer Experience digitale e fidelizzazione",
        ]

    @classmethod
    def get_instance(cls) -> "MarketingContentScheduler":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def start(self):
        """Avvia lo scheduler Marketing Content."""
        if self._is_running:
            logger.warning("marketing_scheduler_already_running")
            return

        if not self.enabled:
            logger.info("marketing_scheduler_disabled",
                       hint="Set MARKETING_AUTO_GENERATION=true to enable")
            return

        try:
            # Avvia scheduler
            self.scheduler.start()
            self._is_running = True

            # Job giornaliero alle 07:00 AM CET
            self.scheduler.add_job(
                self._generate_daily_content,
                trigger=CronTrigger(
                    hour=self.schedule_hour,
                    minute=self.schedule_minute,
                    timezone="Europe/Rome"
                ),
                id="marketing_daily_generation",
                replace_existing=True
            )

            # Job TEST tra 2 minuti (solo in dev)
            if os.getenv("ENVIRONMENT", "development") == "development":
                from datetime import datetime, timedelta
                test_time = datetime.now() + timedelta(minutes=2)
                self.scheduler.add_job(
                    self._generate_daily_content,
                    trigger="date",
                    run_date=test_time,
                    id="marketing_test_generation",
                    replace_existing=True
                )
                logger.info("marketing_test_generation_scheduled", run_at=test_time.strftime("%H:%M:%S"))

            logger.info(
                "marketing_scheduler_started",
                schedule=f"{self.schedule_hour:02d}:{self.schedule_minute:02d} CET (Europe/Rome)",
                platforms=self.platforms,
                post_count=self.post_count,
                story_count=self.story_count,
                video_count=self.video_count,
                pro_quality=self.use_pro_quality,
                auto_publish=self.auto_publish
            )

        except Exception as e:
            logger.error("marketing_scheduler_start_error", error=str(e))
            raise

    async def stop(self):
        """Ferma lo scheduler."""
        if self._is_running:
            self.scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("marketing_scheduler_stopped")

    async def trigger_now(self, custom_topic: str | None = None) -> dict:
        """
        Trigger manuale della generazione.
        Utile per testing o generazione on-demand.

        Args:
            custom_topic: Topic personalizzato (opzionale)
        """
        return await self._generate_daily_content(custom_topic=custom_topic)

    async def _generate_daily_content(self, custom_topic: str | None = None) -> dict:
        """
        Genera il batch content quotidiano per tutti i social.

        Process:
        1. Seleziona topic (rotating o custom)
        2. Chiama AI Microservice /content/batch/generate
        3. Salva contenuti come ScheduledPost
        4. Schedule pubblicazione orari ottimali o auto-publish

        Returns:
            dict con risultato della generazione
        """
        import time
        start_time = time.time()
        target_date = datetime.utcnow()
        logger.info("marketing_daily_generation_started", date=target_date.isoformat())

        db = SessionLocal()
        try:
            # Step 1: Select topic for today
            if custom_topic:
                topic = custom_topic
            else:
                # Rotating topic based on day of week
                topic_index = target_date.weekday() % len(self.topics)
                topic = self.topics[topic_index]
                # Add date context
                topic = f"{topic} - {target_date.strftime('%d %B %Y')}"

            logger.info("marketing_topic_selected", topic=topic)

            # Step 2: Generate batch content via AI Microservice
            async with aiohttp.ClientSession() as session:
                url = f"{self.ai_url}/api/v1/marketing/content/batch/generate"
                headers = {
                    "Authorization": f"Bearer {self.ai_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "topic": topic,
                    "platforms": self.platforms,
                    "post_count": self.post_count,
                    "story_count": self.story_count,
                    "video_count": self.video_count,
                    "style": "professional",
                    "use_pro_quality": self.use_pro_quality
                }

                logger.info("marketing_calling_ai_microservice", url=url, payload=payload)

                try:
                    async with session.post(url, json=payload, headers=headers, timeout=600) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            logger.error("marketing_ai_error", status=resp.status, error=error_text)
                            return {
                                "success": False,
                                "message": f"AI Microservice error: {resp.status}",
                                "error": error_text
                            }

                        result = await resp.json()
                        logger.info("marketing_batch_generated",
                                   items_count=len(result.get("items", [])),
                                   generation_time=result.get("generation_time"),
                                   cost=result.get("total_cost_estimate"))

                except TimeoutError:
                    logger.error("marketing_ai_timeout")
                    return {"success": False, "message": "AI generation timeout (10min)"}

            # Step 3: Save content as ScheduledPost
            items = result.get("items", [])
            if not items:
                logger.warning("marketing_no_content_generated")
                return {"success": False, "message": "No content generated"}

            scheduled_posts = []
            campaign_id = f"daily_{target_date.strftime('%Y%m%d')}"

            # Define optimal posting times (Italy timezone)
            posting_times = {
                "instagram_post": 18,      # 18:00 - best Instagram engagement
                "facebook_post": 13,       # 13:00 - lunch break
                "tiktok_post": 19,         # 19:00 - evening peak
                "linkedin_post": 9,        # 09:00 - morning professional
                "instagram_story_1": 8,    # 08:00 - morning commute
                "instagram_story_2": 13,   # 13:00 - lunch
                "instagram_story_3": 20,   # 20:00 - evening
                "instagram_video": 18,     # 18:00 - same as post for consistency
            }

            for item in items:
                platform = item["platform"]
                content_type = item["content_type"]

                # Determine posting time
                time_key = f"{platform}_{content_type}"
                if content_type == "story":
                    # Multiple stories - distribute across day
                    story_number = len([p for p in scheduled_posts if p.content_type == "story"]) + 1
                    time_key = f"{platform}_story_{story_number}"

                posting_hour = posting_times.get(time_key, 12)  # Default 12:00

                if self.auto_publish:
                    # Immediate publish
                    scheduled_at = datetime.utcnow()
                    status = PostStatus.SCHEDULED
                else:
                    # Schedule for optimal time today
                    scheduled_at = datetime.utcnow().replace(
                        hour=posting_hour,
                        minute=0,
                        second=0,
                        microsecond=0
                    )
                    # If time passed, schedule for tomorrow
                    if scheduled_at < datetime.utcnow():
                        scheduled_at += timedelta(days=1)

                    status = PostStatus.DRAFT  # Manual review before publish

                # Create ScheduledPost
                post = ScheduledPost(
                    user_id=1,  # System user
                    campaign_id=campaign_id,
                    content=item["caption"],
                    platforms=[platform],
                    scheduled_at=scheduled_at,
                    status=status.value,
                    content_type=content_type,
                    media_urls=[item.get("image_url") or item.get("video_url")],
                    metadata={
                        "generated_by": "marketing_scheduler",
                        "topic": topic,
                        "hashtags": item.get("hashtags", []),
                        "aspect_ratio": item.get("aspect_ratio"),
                        "ai_metadata": item.get("metadata"),
                        "generation_date": target_date.isoformat(),
                        "batch_cost": result.get("total_cost_estimate"),
                    }
                )

                db.add(post)
                scheduled_posts.append(post)

            db.commit()

            # Schedule posts for publication via PostScheduler
            if self.auto_publish:
                from app.infrastructure.scheduler.post_scheduler import post_scheduler
                for post in scheduled_posts:
                    db.refresh(post)
                    await post_scheduler.schedule_post(post.id, post.scheduled_at)

            generation_time = int(time.time() - start_time)
            logger.info(
                "marketing_daily_content_created",
                posts_created=len(scheduled_posts),
                campaign_id=campaign_id,
                topic=topic,
                generation_time=generation_time,
                ai_generation_time=result.get("generation_time"),
                cost=result.get("total_cost_estimate"),
                auto_publish=self.auto_publish
            )

            return {
                "success": True,
                "message": "Daily content generated successfully",
                "campaign_id": campaign_id,
                "posts_created": len(scheduled_posts),
                "topic": topic,
                "generation_time": generation_time,
                "cost": result.get("total_cost_estimate"),
                "scheduled_posts": [
                    {
                        "id": p.id,
                        "platform": p.platforms[0] if p.platforms else None,
                        "content_type": p.content_type,
                        "scheduled_at": p.scheduled_at.isoformat(),
                        "status": p.status
                    }
                    for p in scheduled_posts
                ]
            }

        except Exception as e:
            logger.error("marketing_daily_generation_error", error=str(e))
            import traceback
            traceback.print_exc()
            return {"success": False, "message": str(e)}

        finally:
            db.close()


# Singleton instance
marketing_content_scheduler = MarketingContentScheduler.get_instance()


async def start_marketing_scheduler():
    """Avvia il Marketing Content scheduler."""
    await marketing_content_scheduler.start()


async def stop_marketing_scheduler():
    """Ferma il Marketing Content scheduler."""
    await marketing_content_scheduler.stop()


async def trigger_marketing_generation(custom_topic: str | None = None):
    """Trigger manuale per testing o generazione on-demand."""
    return await marketing_content_scheduler.trigger_now(custom_topic=custom_topic)
