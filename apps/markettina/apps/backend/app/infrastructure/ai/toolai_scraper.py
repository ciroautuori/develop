"""
ToolAI Real Data Scraper v3.0 - PERFETTO

Raccoglie i MIGLIORI tool AI NUOVI delle ultime 24-48h da:
1. HuggingFace Daily Papers - Paper del giorno con upvotes (PRIORITÀ MASSIMA)
2. HuggingFace Trending Models - Modelli con engagement recente
3. GitHub Trending AI - Repo NUOVI (creati ultima settimana) con più stars
4. Papers With Code - Tool con implementazioni

STRATEGIA SEO:
- Contenuti FRESCHI ogni giorno (Google freshness boost)
- Tool con ENGAGEMENT reale (upvotes, stars, downloads)
- NO tool vecchi/storici (TensorFlow, PyTorch, etc.)

NO mock data - Solo dati reali aggiornati!
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class ToolAIScraper:
    """
    Scraper per raccogliere i MIGLIORI tool AI NUOVI da multiple fonti.

    PRIORITÀ:
    1. HuggingFace Daily Papers (upvotes freschi del giorno)
    2. GitHub repo NUOVI (creati ultima settimana, con stars)
    3. HuggingFace Models (aggiornati nelle ultime 48h)
    4. Papers With Code (tool con implementazioni)
    """

    # API Endpoints
    HUGGINGFACE_DAILY_PAPERS = "https://huggingface.co/api/daily_papers"
    HUGGINGFACE_MODELS = "https://huggingface.co/api/models"
    GITHUB_API = "https://api.github.com"
    PAPERS_WITH_CODE = "https://paperswithcode.com/api/v1"

    CATEGORY_KEYWORDS = {
        "llm": ["llm", "language", "gpt", "bert", "transformer", "text-generation", "chat", "reasoning", "qwen", "llama", "mistral"],
        "image": ["image", "diffusion", "stable-diffusion", "text-to-image", "vision", "flux", "sdxl", "generation"],
        "audio": ["audio", "speech", "tts", "text-to-speech", "voice", "music", "whisper", "kokoro"],
        "code": ["code", "coding", "programming", "codegen", "copilot", "coder"],
        "video": ["video", "text-to-video", "video-generation", "sora", "animation"],
        "multimodal": ["multimodal", "vision-language", "clip", "llava", "mllm", "vqa"],
        "3d": ["3d", "gaussian", "mesh", "point-cloud", "nerf"],
        "robotics": ["robot", "embodied", "navigation", "manipulation"],
        "agent": ["agent", "agentic", "workflow", "automation", "tool-use"]
    }

    # Blacklist tool storici (sempre trending ma NON nuovi)
    BLACKLIST = {
        "tensorflow", "pytorch", "keras", "scikit-learn", "opencv",
        "transformers", "huggingface", "langchain", "llama-index",
        "autogpt", "gpt4all", "text-generation-webui", "ollama",
        "stable-diffusion-webui", "comfyui", "automatic1111"
    }

    def __init__(self, github_token: str | None = None):
        self.github_token = github_token
        self.client: httpx.AsyncClient | None = None
        self._seen_names: set[str] = set()

    async def _ensure_client(self):
        """Inizializza il client HTTP se non esiste."""
        if self.client is None:
            headers = {
                "Accept": "application/json",
                "User-Agent": "ToolAI-Scraper/3.0 (markettina)"
            }
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            self.client = httpx.AsyncClient(timeout=30.0, headers=headers)

    async def close(self):
        """Chiudi il client HTTP."""
        if self.client:
            await self.client.aclose()
            self.client = None

    def _categorize_tool(self, name: str, description: str, tags: list[str]) -> str:
        """Categorizza un tool basandosi su nome, descrizione e tags."""
        text = f"{name} {description} {' '.join(tags)}".lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return category
        return "llm"

    def _normalize_name(self, name: str) -> str:
        """Normalizza il nome per deduplicazione."""
        return name.lower().replace("-", "").replace("_", "").replace(" ", "")[:50]

    def _is_blacklisted(self, name: str) -> bool:
        """Controlla se il tool è nella blacklist (progetti storici)."""
        normalized = self._normalize_name(name)
        return any(bl in normalized for bl in self.BLACKLIST)

    # =========================================================================
    # 1. HUGGINGFACE DAILY PAPERS - PRIORITÀ MASSIMA (Paper freschi del giorno)
    # =========================================================================

    async def fetch_huggingface_daily_papers(self, limit: int = 15) -> list[dict[str, Any]]:
        """
        Fetch DAILY PAPERS da HuggingFace - Paper pubblicati OGGI con upvotes!

        Questi sono i contenuti PIÙ FRESCHI e di QUALITÀ:
        - Pubblicati nelle ultime 24h
        - Ordinati per upvotes della community
        - Spesso hanno già implementazioni GitHub
        """
        await self._ensure_client()
        tools = []

        try:
            response = await self.client.get(self.HUGGINGFACE_DAILY_PAPERS)

            if response.status_code == 200:
                papers = response.json()

                # Ordina per upvotes (qualità community)
                papers_sorted = sorted(
                    papers,
                    key=lambda x: x.get("paper", {}).get("upvotes", 0),
                    reverse=True
                )

                for paper in papers_sorted[:limit]:
                    paper_data = paper.get("paper", {})
                    title = paper_data.get("title", paper.get("title", ""))
                    summary = paper_data.get("summary", "")[:300]

                    if not title:
                        continue

                    # GitHub repo se disponibile
                    github_url = paper_data.get("githubRepo", "")
                    github_stars = paper_data.get("githubStars", 0) or 0

                    # ArXiv info
                    arxiv_id = paper_data.get("id", "")
                    paper_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""

                    # Upvotes = engagement del giorno
                    upvotes = paper_data.get("upvotes", 0) or 0

                    # AI keywords
                    ai_keywords = paper_data.get("ai_keywords", [])

                    # Trending score: upvotes hanno priorità massima
                    trending_score = (upvotes * 100) + (github_stars * 2)

                    tools.append({
                        "name": title[:100],
                        "source": "HuggingFace_Daily_Papers",
                        "source_url": paper_url or github_url,
                        "github_url": github_url,
                        "description_it": f"📄 Paper AI trending ({upvotes} ⬆️): {summary}...",
                        "description_en": f"📄 Trending AI Paper ({upvotes} ⬆️): {summary}...",
                        "category": self._categorize_tool(title, summary, ai_keywords),
                        "tags": ai_keywords[:5],
                        "stars": github_stars,
                        "upvotes": upvotes,
                        "trending_score": trending_score,
                        "freshness": "today",
                        "arxiv_id": arxiv_id
                    })

                logger.info(
                    "huggingface_daily_papers_complete",
                    count=len(tools),
                    top_upvotes=tools[0].get("upvotes", 0) if tools else 0,
                    top_name=tools[0].get("name", "")[:50] if tools else ""
                )

        except Exception as e:
            logger.error("huggingface_daily_papers_error", error=str(e))

        return tools

    # =========================================================================
    # 2. GITHUB TRENDING AI - Repo NUOVI (creati ultima settimana) con stars
    # =========================================================================

    async def fetch_github_trending_ai(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch repo AI NUOVI da GitHub - Creati nell'ultima settimana con più stars.

        STRATEGIA:
        - Cerca repo CREATI di recente (non solo pushati)
        - Questo evita i big players storici (tensorflow, pytorch, etc.)
        - Trova progetti NUOVI che stanno guadagnando trazione
        """
        await self._ensure_client()
        tools = []

        try:
            # Cerca repo CREATI negli ultimi 7 giorni
            since_created = (datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d")
            since_24h = (datetime.now(UTC) - timedelta(hours=24)).strftime("%Y-%m-%d")

            # Query: repo AI nuovi con almeno 10 stars
            # Formato corretto per GitHub: topic:X invece di keywords libere
            query = f"topic:machine-learning topic:ai stars:>10 created:>{since_created}"

            response = await self.client.get(
                f"{self.GITHUB_API}/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 50
                }
            )

            if response.status_code == 200:
                data = response.json()
                repos = data.get("items", [])

                for repo in repos:
                    name = repo.get("name", "")
                    stars = repo.get("stargazers_count", 0)

                    # Skip blacklisted (progetti storici)
                    if self._is_blacklisted(name):
                        continue

                    # Skip senza descrizione
                    desc = repo.get("description", "") or ""
                    if not desc:
                        continue

                    topics = repo.get("topics", [])
                    updated_at = repo.get("updated_at", "")[:10]
                    created_at = repo.get("created_at", "")[:10]
                    forks = repo.get("forks_count", 0)

                    # Engagement: stars + forks bonus
                    engagement = stars + (forks * 3)

                    # Bonus per repo aggiornati oggi
                    if updated_at >= since_24h:
                        engagement = int(engagement * 1.5)

                    tools.append({
                        "name": name,
                        "source": "GitHub_New_Trending",
                        "source_url": repo.get("html_url", ""),
                        "description_it": f"🆕 GitHub ({stars}⭐): {desc[:200]}",
                        "description_en": f"🆕 New GitHub ({stars}⭐): {desc[:200]}",
                        "category": self._categorize_tool(name, desc, topics),
                        "tags": topics[:5],
                        "stars": stars,
                        "forks": forks,
                        "trending_score": engagement,
                        "created_at": created_at,
                        "freshness": "week",
                        "language": repo.get("language", "")
                    })

                    if len(tools) >= limit:
                        break

                logger.info(
                    "github_trending_complete",
                    count=len(tools),
                    top_stars=tools[0].get("stars", 0) if tools else 0,
                    top_name=tools[0].get("name", "") if tools else ""
                )

            elif response.status_code == 403:
                logger.warning("github_rate_limited", status=403)
            else:
                logger.warning("github_api_error", status=response.status_code)

        except Exception as e:
            logger.error("github_trending_error", error=str(e))

        return tools

    # =========================================================================
    # 3. HUGGINGFACE MODELS - Modelli aggiornati nelle ultime 48h
    # =========================================================================

    async def fetch_huggingface_trending_models(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch MODELS da HuggingFace - Aggiornati nelle ultime 48h con engagement.

        Filtra per:
        - lastModified nelle ultime 48h
        - Minimo engagement (likes > 0 OR downloads > 100)
        - Ordina per engagement score
        """
        await self._ensure_client()
        tools = []

        try:
            cutoff = (datetime.now(UTC) - timedelta(hours=48)).strftime("%Y-%m-%d")
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            yesterday = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")

            response = await self.client.get(
                self.HUGGINGFACE_MODELS,
                params={
                    "sort": "lastModified",
                    "direction": -1,
                    "limit": 200,
                    "full": "true"
                }
            )

            if response.status_code == 200:
                models = response.json()
                candidates = []

                for model in models:
                    model_id = model.get("modelId", "")
                    pipeline_tag = model.get("pipeline_tag", "")

                    if not model_id or not pipeline_tag:
                        continue

                    # Skip blacklisted
                    if self._is_blacklisted(model_id):
                        continue

                    last_modified = model.get("lastModified", "")[:10]
                    downloads = model.get("downloads", 0) or 0
                    likes = model.get("likes", 0) or 0
                    tags = model.get("tags", [])

                    # Filtro temporale: ultime 48h
                    if last_modified < cutoff:
                        continue

                    # Filtro qualità: minimo engagement
                    if likes == 0 and downloads < 100:
                        continue

                    # Engagement score
                    engagement = (likes * 10) + (downloads // 1000)

                    # Bonus freshness
                    if last_modified == today:
                        engagement = int(engagement * 1.5)
                    elif last_modified == yesterday:
                        engagement = int(engagement * 1.2)

                    name = model_id.split("/")[-1] if "/" in model_id else model_id

                    candidates.append({
                        "name": name,
                        "source": "HuggingFace_Models",
                        "source_url": f"https://huggingface.co/{model_id}",
                        "description_it": f"🤗 Modello {pipeline_tag}: {downloads:,} downloads, {likes:,} likes",
                        "description_en": f"🤗 {pipeline_tag} Model: {downloads:,} downloads, {likes:,} likes",
                        "category": self._categorize_tool(model_id, pipeline_tag, tags),
                        "tags": tags[:5],
                        "downloads": downloads,
                        "stars": likes,
                        "trending_score": engagement,
                        "pipeline_tag": pipeline_tag,
                        "freshness": "48h"
                    })

                # Ordina per engagement
                candidates.sort(key=lambda x: x["trending_score"], reverse=True)
                tools = candidates[:limit]

                logger.info(
                    "huggingface_models_complete",
                    count=len(tools),
                    top_score=tools[0].get("trending_score", 0) if tools else 0
                )

        except Exception as e:
            logger.error("huggingface_models_error", error=str(e))

        return tools

    # =========================================================================
    # 4. PAPERS WITH CODE - Tool con implementazioni
    # =========================================================================

    async def fetch_papers_with_code(self, limit: int = 5) -> list[dict[str, Any]]:
        """
        Fetch trending papers da Papers With Code.

        Ottimi per SEO: paper con implementazioni GitHub!
        """
        await self._ensure_client()
        tools = []

        try:
            # API Papers With Code per trending
            response = await self.client.get(
                f"{self.PAPERS_WITH_CODE}/papers/",
                params={"ordering": "-github_stars", "items_per_page": 20}
            )

            if response.status_code == 200:
                data = response.json()
                papers = data.get("results", [])

                for paper in papers[:limit]:
                    title = paper.get("title", "")
                    abstract = paper.get("abstract", "")[:200]

                    if not title:
                        continue

                    stars = paper.get("github_stars", 0) or 0
                    paper_url = paper.get("url_abs", "")

                    tools.append({
                        "name": title[:80],
                        "source": "Papers_With_Code",
                        "source_url": f"https://paperswithcode.com{paper.get('url', '')}",
                        "description_it": f"📊 Paper + Code ({stars}⭐): {abstract}...",
                        "description_en": f"📊 Paper + Code ({stars}⭐): {abstract}...",
                        "category": self._categorize_tool(title, abstract, []),
                        "tags": [],
                        "stars": stars,
                        "trending_score": stars,
                        "freshness": "recent"
                    })

                logger.info("papers_with_code_complete", count=len(tools))

        except Exception as e:
            logger.warning("papers_with_code_error", error=str(e))

        return tools

    # =========================================================================
    # DISCOVER TOOLS - Aggregatore principale
    # =========================================================================

    async def discover_tools(
        self,
        num_tools: int = 10,
        categories: list[str] | None = None,
        sources: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Scopri i MIGLIORI tool AI NUOVI da tutte le fonti.

        PRIORITÀ SORTING:
        1. HuggingFace Daily Papers (upvotes × 100)
        2. GitHub New Trending (stars nuovi)
        3. HuggingFace Models (engagement)
        4. Papers With Code
        """
        await self._ensure_client()

        if sources is None:
            sources = ["huggingface_papers", "github", "huggingface_models"]

        all_tools = []
        tasks = []

        # Fetch da tutte le fonti in parallelo
        if "huggingface_papers" in sources:
            tasks.append(self.fetch_huggingface_daily_papers(limit=15))

        if "github" in sources:
            tasks.append(self.fetch_github_trending_ai(limit=10))

        if "huggingface_models" in sources:
            tasks.append(self.fetch_huggingface_trending_models(limit=10))

        if "papers_with_code" in sources:
            tasks.append(self.fetch_papers_with_code(limit=5))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_tools.extend(result)
                elif isinstance(result, Exception):
                    logger.error("discover_tools_source_error", error=str(result))

        # Filter by category
        if categories:
            all_tools = [t for t in all_tools if t.get("category") in categories]

        # STRATEGIA MIX EQUILIBRATO:
        # Garantisce diversità: Papers (60%) + GitHub (25%) + Models (15%)
        papers = [t for t in all_tools if "Paper" in t.get("source", "")]
        github = [t for t in all_tools if "GitHub" in t.get("source", "")]
        models = [t for t in all_tools if "Models" in t.get("source", "")]

        # Ordina ogni gruppo per score
        papers.sort(key=lambda x: x.get("upvotes", 0), reverse=True)
        github.sort(key=lambda x: x.get("stars", 0), reverse=True)
        models.sort(key=lambda x: x.get("trending_score", 0), reverse=True)

        # Mix equilibrato
        num_papers = max(int(num_tools * 0.6), 4)  # 60% papers, min 4
        num_github = max(int(num_tools * 0.25), 1)  # 25% github, min 1
        num_models = num_tools - num_papers - num_github  # resto per models

        # Assegna da ogni fonte
        mixed = []
        mixed.extend(papers[:num_papers])
        mixed.extend(github[:num_github])
        mixed.extend(models[:num_models])

        # Se non abbastanza, riempi con quello che c'è
        if len(mixed) < num_tools:
            remaining = num_tools - len(mixed)
            # Prova papers extra
            for p in papers[num_papers:]:
                if len(mixed) >= num_tools:
                    break
                mixed.append(p)
            # Prova github extra
            for g in github[num_github:]:
                if len(mixed) >= num_tools:
                    break
                mixed.append(g)
            # Prova models extra
            for m in models[num_models:]:
                if len(mixed) >= num_tools:
                    break
                mixed.append(m)

        # Ordina il mix finale per engagement
        mixed.sort(
            key=lambda x: x.get("upvotes", 0) * 10 + x.get("trending_score", 0),
            reverse=True
        )

        # Deduplicazione intelligente
        seen = set()
        unique_tools = []
        for tool in mixed:
            name_key = self._normalize_name(tool.get("name", ""))
            if name_key not in seen and len(name_key) > 3:
                seen.add(name_key)
                unique_tools.append(tool)
                if len(unique_tools) >= num_tools:
                    break

        # Cleanup
        await self.close()

        logger.info(
            "discover_tools_complete",
            num_tools=num_tools,
            total_found=len(all_tools),
            unique_returned=len(unique_tools),
            sources=sources
        )

        return unique_tools
