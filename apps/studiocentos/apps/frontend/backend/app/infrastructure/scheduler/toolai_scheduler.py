"""
ToolAI Daily Scheduler - Generazione automatica quotidiana.

Utilizza APScheduler per generare un nuovo post ToolAI ogni giorno
alle 6:00 AM CET/CEST (per catturare le novità notturne).

DATI REALI da:
- HuggingFace Trending Models
- GitHub Trending AI Repos
- ArXiv AI Papers
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, List
import structlog

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from app.infrastructure.database import SessionLocal
from app.domain.toolai.models import ToolAIPost, AITool, ToolAIPostStatus
from app.infrastructure.ai.toolai_scraper import ToolAIScraper

logger = structlog.get_logger(__name__)


class ToolAIScheduler:
    """
    Scheduler per generazione automatica post ToolAI.

    Genera ogni giorno alle 6:00 AM un nuovo post con:
    - 3-5 tool AI trending
    - Contenuto SEO optimized in IT/EN/ES
    - Immagine di copertina generata con AI
    - Auto-publish
    """

    _instance: Optional['ToolAIScheduler'] = None

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 3600  # 1 ora di tolleranza
            },
            timezone='Europe/Rome'  # CET/CEST
        )
        self._is_running = False

        # Configuration from env
        self.ai_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
        self.ai_api_key = os.getenv("AI_SERVICE_API_KEY", "dev-api-key-change-in-production")
        self.schedule_hour = int(os.getenv("TOOLAI_SCHEDULE_HOUR", "8"))  # 08:30 AM CET
        self.schedule_minute = int(os.getenv("TOOLAI_SCHEDULE_MINUTE", "30"))
        self.num_tools = int(os.getenv("TOOLAI_NUM_TOOLS", "8"))  # Aumentato da 4 a 8 per più scelta
        self.categories = os.getenv("TOOLAI_CATEGORIES", "llm,image,code,audio,video,multimodal").split(",")

    @classmethod
    def get_instance(cls) -> 'ToolAIScheduler':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def start(self):
        """Avvia lo scheduler ToolAI."""
        if self._is_running:
            logger.warning("toolai_scheduler_already_running")
            return

        try:
            # Avvia scheduler
            self.scheduler.start()
            self._is_running = True

            # Job giornaliero alle 08:30 AM CET
            self.scheduler.add_job(
                self._generate_daily_post,
                trigger=CronTrigger(
                    hour=self.schedule_hour,
                    minute=self.schedule_minute,
                    timezone='Europe/Rome'
                ),
                id='toolai_daily_generation',
                replace_existing=True
            )

            # Job TEST tra 5 minuti dalla prima esecuzione
            from datetime import datetime, timedelta
            test_time = datetime.now() + timedelta(minutes=5)
            self.scheduler.add_job(
                self._generate_daily_post,
                trigger='date',
                run_date=test_time,
                id='toolai_test_generation',
                replace_existing=True
            )

            logger.info(
                "toolai_scheduler_started",
                schedule=f"{self.schedule_hour:02d}:{self.schedule_minute:02d} CET (Europe/Rome)",
                test_run=test_time.strftime("%H:%M:%S"),
                num_tools=self.num_tools,
                categories=self.categories
            )

        except Exception as e:
            logger.error("toolai_scheduler_start_error", error=str(e))
            raise

    async def stop(self):
        """Ferma lo scheduler."""
        if self._is_running:
            self.scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("toolai_scheduler_stopped")

    async def trigger_now(self) -> dict:
        """
        Trigger manuale della generazione.
        Utile per testing o generazione on-demand.
        """
        return await self._generate_daily_post()

    async def _generate_daily_post(self) -> dict:
        """
        Genera il post ToolAI quotidiano con DATI REALI.

        Raccoglie tool AI da:
        - HuggingFace trending models
        - GitHub trending AI repos
        - ArXiv recent papers

        Returns:
            dict con risultato della generazione
        """
        import time
        start_time = time.time()
        target_date = datetime.utcnow()
        logger.info("toolai_daily_generation_started", date=target_date.isoformat())

        db = SessionLocal()
        try:
            # Check se esiste già un post per oggi
            from sqlalchemy import func
            existing = db.query(ToolAIPost).filter(
                func.date(ToolAIPost.post_date) == target_date.date()
            ).first()

            if existing:
                logger.info(
                    "toolai_post_already_exists",
                    post_id=existing.id,
                    date=target_date.date()
                )
                return {
                    "success": False,
                    "message": f"Post already exists for {target_date.date()}",
                    "post_id": existing.id
                }

            # Step 0: Get tools already used in last 7 days (deduplication)
            from datetime import timedelta
            seven_days_ago = target_date - timedelta(days=7)
            recent_tools = db.query(AITool.name).join(ToolAIPost).filter(
                ToolAIPost.post_date >= seven_days_ago
            ).all()
            excluded_names = {t.name.lower().replace(" ", "").replace("-", "")[:50] for t in recent_tools}
            logger.info("toolai_excluded_recent_tools", count=len(excluded_names))

            # Step 1: Fetch REAL tools da HuggingFace (Papers, Models, Spaces) + GitHub
            logger.info("toolai_discovering_real_tools",
                       num_tools=self.num_tools,
                       categories=self.categories)

            scraper = ToolAIScraper(
                github_token=os.getenv("GITHUB_TOKEN"),
                excluded_names=excluded_names  # Pass excluded tools
            )
            # Fetch MORE tools (60) da TUTTE le fonti per avere massima varietà
            all_discovered_tools = await scraper.discover_tools(
                num_tools=60,  # Fetch molti di più per compensare esclusioni
                categories=self.categories if self.categories else None,
                sources=[
                    "huggingface_papers",    # Paper del giorno (HF)
                    "huggingface_spaces",    # App AI interattive
                    "huggingface_models",    # Modelli trending
                    "huggingface_datasets",  # Dataset trending
                    "github",                # Repo AI nuovi
                    "arxiv",                 # Paper scientifici
                    "papers_with_code",      # Paper + implementazioni
                    "hacker_news",           # Discussioni tech
                    "reddit",                # Community ML
                    "replicate",             # ML in production
                    "civitai",               # Stable Diffusion models
                    "openrouter"             # API marketplace
                ]
            )

            # Seleziona i TOP tool per trending score
            # Seleziona i TOP tool (l'ordine è già ottimizzato dallo scraper per diversità)
            # all_discovered_tools.sort(...) -> REMOVED to preserve Round-Robin diversity

            # Prendi solo i TOP self.num_tools
            tools = all_discovered_tools[:self.num_tools]

            if not tools:
                logger.warning("toolai_no_tools_discovered")
                return {"success": False, "message": "No tools discovered from sources"}

            logger.info(
                "toolai_tools_discovered",
                count=len(tools),
                total_discovered=len(all_discovered_tools),
                top_scores=[{
                    "name": t.get("name", "")[:30],
                    "trending_score": t.get("trending_score", 0),
                    "stars": t.get("stars", 0),
                    "source": t.get("source", "")
                } for t in tools[:5]]
            )

            # Step 2: Generate content from real tools
            tool_names = [t.get("name", "") for t in tools]
            date_str = target_date.strftime("%d %B %Y")

            # Title e summary basati sui tool reali
            title_it = f"I Migliori Tool AI del {date_str}: {', '.join(tool_names[:3])}"
            title_en = f"Best AI Tools of {date_str}: {', '.join(tool_names[:3])}"
            title_es = f"Las Mejores Herramientas de IA del {date_str}: {', '.join(tool_names[:3])}"

            summary_it = f"Oggi scopriamo {len(tools)} strumenti AI trending: {', '.join(tool_names)}. Modelli da HuggingFace, repository GitHub e paper ArXiv più rilevanti."
            summary_en = f"Today we discover {len(tools)} trending AI tools: {', '.join(tool_names)}. Models from HuggingFace, GitHub repos and most relevant ArXiv papers."
            summary_es = f"Hoy descubrimos {len(tools)} herramientas de IA en tendencia: {', '.join(tool_names)}. Modelos de HuggingFace, repositorios GitHub y papers ArXiv más relevantes."

            # Content strutturato
            content_parts_it = [f"# I Tool AI più Interessanti del {date_str}\n"]
            content_parts_en = [f"# Most Interesting AI Tools of {date_str}\n"]
            content_parts_es = [f"# Herramientas de IA Más Interesantes del {date_str}\n"]

            for i, tool in enumerate(tools, 1):
                content_parts_it.append(f"\n## {i}. {tool.get('name')}\n")
                content_parts_it.append(f"**Fonte:** {tool.get('source', 'N/A').title()}\n")
                content_parts_it.append(f"**Categoria:** {tool.get('category', 'llm').upper()}\n")
                content_parts_it.append(f"{tool.get('description_it', '')}\n")
                if tool.get('stars'):
                    content_parts_it.append(f"⭐ {tool.get('stars'):,} stars\n")
                if tool.get('downloads'):
                    content_parts_it.append(f"📥 {tool.get('downloads'):,} downloads\n")
                content_parts_it.append(f"🔗 [{tool.get('source_url', '')}]({tool.get('source_url', '')})\n")

                content_parts_en.append(f"\n## {i}. {tool.get('name')}\n")
                content_parts_en.append(f"**Source:** {tool.get('source', 'N/A').title()}\n")
                content_parts_en.append(f"**Category:** {tool.get('category', 'llm').upper()}\n")
                content_parts_en.append(f"{tool.get('description_en', tool.get('description_it', ''))}\n")
                if tool.get('stars'):
                    content_parts_en.append(f"⭐ {tool.get('stars'):,} stars\n")
                if tool.get('downloads'):
                    content_parts_en.append(f"📥 {tool.get('downloads'):,} downloads\n")
                content_parts_en.append(f"🔗 [{tool.get('source_url', '')}]({tool.get('source_url', '')})\n")

                content_parts_es.append(f"\n## {i}. {tool.get('name')}\n")
                content_parts_es.append(f"**Fuente:** {tool.get('source', 'N/A').title()}\n")
                content_parts_es.append(f"**Categoría:** {tool.get('category', 'llm').upper()}\n")
                content_parts_es.append(f"{tool.get('description_es', tool.get('description_en', tool.get('description_it', '')))}\n")
                if tool.get('stars'):
                    content_parts_es.append(f"⭐ {tool.get('stars'):,} estrellas\n")
                if tool.get('downloads'):
                    content_parts_es.append(f"📥 {tool.get('downloads'):,} descargas\n")
                content_parts_es.append(f"🔗 [{tool.get('source_url', '')}]({tool.get('source_url', '')})\n")

            content_it = "".join(content_parts_it)
            content_en = "".join(content_parts_en)
            content_es = "".join(content_parts_es)

            # Step 3: Create post with real data
            slug = f"ai-tools-{target_date.strftime('%Y-%m-%d')}"

            # Keywords basate sui tool reali
            keywords = ["AI tools", "machine learning", "deep learning"]
            keywords.extend([t.get("name", "")[:20] for t in tools[:5]])
            keywords.extend([t.get("category", "") for t in tools if t.get("category")])

            post = ToolAIPost(
                post_date=target_date,
                status=ToolAIPostStatus.PUBLISHED.value,
                title_it=title_it[:250],
                title_en=title_en[:250],
                title_es=title_es[:250],
                summary_it=summary_it[:500],
                summary_en=summary_en[:500],
                summary_es=summary_es[:500],
                content_it=content_it,
                content_en=content_en,
                content_es=content_es,
                insights_it=f"Questi {len(tools)} tool rappresentano le tendenze più interessanti nel mondo AI di oggi.",
                insights_en=f"These {len(tools)} tools represent the most interesting trends in today's AI world.",
                insights_es=f"Estas {len(tools)} herramientas representan las tendencias más interesantes en el mundo de la IA hoy.",
                takeaway_it="Esplora questi strumenti per restare aggiornato sulla rivoluzione AI.",
                takeaway_en="Explore these tools to stay updated on the AI revolution.",
                takeaway_es="Explora estas herramientas para mantenerte actualizado sobre la revolución de la IA.",
                meta_description=summary_it[:155],
                meta_keywords=list(set(keywords))[:10],
                slug=slug,
                image_url=None,
                ai_generated=True,
                ai_model="real-data-scraper",
                generation_time=int(time.time() - start_time),
                published_at=datetime.utcnow(),
            )

            # Add tools with real data
            for i, tool_data in enumerate(tools):
                tool = AITool(
                    name=tool_data.get("name", "")[:250],
                    source=tool_data.get("source"),
                    source_url=tool_data.get("source_url"),
                    description_it=tool_data.get("description_it", "")[:1000],
                    description_en=tool_data.get("description_en", tool_data.get("description_it", ""))[:1000],
                    description_es=tool_data.get("description_es", tool_data.get("description_en", tool_data.get("description_it", "")))[:1000],
                    relevance_it=f"Trending su {tool_data.get('source', 'web').title()}",
                    relevance_en=f"Trending on {tool_data.get('source', 'web').title()}",
                    relevance_es=f"Tendencia en {tool_data.get('source', 'web').title()}",
                    category=tool_data.get("category"),
                    tags=tool_data.get("tags", [])[:5],
                    stars=tool_data.get("stars"),
                    downloads=tool_data.get("downloads"),
                    trending_score=tool_data.get("trending_score"),
                    display_order=i,
                )
                post.tools.append(tool)

            db.add(post)
            db.commit()
            db.refresh(post)

            generation_time = int(time.time() - start_time)
            logger.info(
                "toolai_daily_post_created",
                post_id=post.id,
                tools_count=len(post.tools),
                date=target_date.date(),
                generation_time=generation_time,
                sources=["huggingface", "github", "arxiv"]
            )

            return {
                "success": True,
                "message": "Post generated with REAL data successfully",
                "post_id": post.id,
                "tools_count": len(post.tools)
            }

        except Exception as e:
            logger.error("toolai_daily_generation_error", error=str(e))
            import traceback
            traceback.print_exc()
            return {"success": False, "message": str(e)}

        finally:
            db.close()


# Singleton instance
toolai_scheduler = ToolAIScheduler.get_instance()


async def start_toolai_scheduler():
    """Avvia il ToolAI scheduler."""
    await toolai_scheduler.start()


async def stop_toolai_scheduler():
    """Ferma il ToolAI scheduler."""
    await toolai_scheduler.stop()


async def trigger_toolai_generation():
    """Trigger manuale per testing."""
    return await toolai_scheduler.trigger_now()
