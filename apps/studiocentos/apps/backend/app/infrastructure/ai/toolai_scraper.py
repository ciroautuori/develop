"""
ToolAI Scraper v8.0 - ULTIMATE MERGE EDITION 🚀
Combines Enterprise robustness (Caching, Retries) with Maximum Data Sources.

Sources:
1. HuggingFace Daily Papers (Fresh Papers)
2. HuggingFace Trending Models (Recent Engagement)
3. HuggingFace Spaces (Interactive Demos)
4. GitHub Trending AI (New & Hot Repos)
5. Product Hunt (New SaaS/Tools)
6. Hacker News (Tech Discussions)
7. Reddit ML (Community Discussions)
8. Papers With Code (Implementation Focus)
9. Big Tech Radar (Official Labs)

Features:
- Persistent JSON Disk Cache
- Robust Retry & Rate Limiting
- Multi-Strategy Parsing
- Structured Logging
"""

import asyncio
import time
import re
import json
import os
import structlog
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Set, Union
from dataclasses import dataclass, field
import httpx


# Enforce mandatory dependencies
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Add simple adapter to mimic bound logger
    class StructLoggerAdapter:
        def __init__(self, logger): self.logger = logger
        def info(self, msg, **kwargs): self.logger.info(f"{msg} {kwargs}")
        def warning(self, msg, **kwargs): self.logger.warning(f"{msg} {kwargs}")
        def error(self, msg, **kwargs): self.logger.error(f"{msg} {kwargs}")
        def debug(self, msg, **kwargs): self.logger.debug(f"{msg} {kwargs}")
    logger = StructLoggerAdapter(logger)

# --- CONFIGURATION MANAGEMENT ---

@dataclass
class ScraperConfig:
    """Centralized configuration for the scraper."""
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    max_concurrency: int = 5
    cache_ttl_seconds: int = 3600  # 1 hour cache
    cache_file: str = "toolai_cache.json"
    timeout_connect: float = 10.0
    timeout_read: float = 30.0
    user_agent: str = "ToolAI-Scraper/8.0 (StudiocentOS; +bot)"
    blacklist: Set[str] = field(default_factory=lambda: {
        "tensorflow", "pytorch", "keras", "pandas", "numpy", "react", "node",
        "chatgpt", "midjourney", "google", "microsoft", "meta", "amazon",
        "scikit-learn", "opencv", "transformers", "huggingface", "langchain",
        "llama-index", "autogpt", "gpt4all", "ollama", "comfyui", "automatic1111"
    })

class ToolAIScraper:
    """
    Enterprise-grade scraper with persistent caching and rate limiting.
    Aggregates data from 9+ sources.
    """

    # Endpoints
    HUGGINGFACE_API = "https://huggingface.co/api"
    GITHUB_API = "https://api.github.com"
    PAPERS_WITH_CODE = "https://paperswithcode.com/api/v1"

    CATEGORY_KEYWORDS = {
        "llm": ["llm", "gpt", "claude", "gemini", "chat", "text-generation", "rag", "llama", "mistral", "reasoning", "qwen"],
        "image": ["image", "diffusion", "flux", "generation", "vision", "upscale", "lora", "sdxl"],
        "video": ["video", "sora", "runway", "pika", "animation", "motion"],
        "audio": ["audio", "speech", "tts", "voice", "music", "whisper", "kokoro"],
        "dev": ["code", "ide", "vscode", "copilot", "cursor", "api", "sdk", "database", "codegen"],
        "app": ["app", "saas", "platform", "assistant", "workflow", "automation", "productivity", "agent"],
        "research": ["paper", "arxiv", "thesis", "experiment", "lab"],
        "robotics": ["robot", "embodied", "navigation", "manipulation"],
        "multimodal": ["multimodal", "vision-language", "clip", "vqa"]
    }

    def __init__(self, config: Optional[ScraperConfig] = None, excluded_names: Optional[Set[str]] = None, github_token: Optional[str] = None):
        """
        Initialize scraper with config and persistence.
        """
        self.config = config or ScraperConfig()
        
        # Legacy support
        if github_token and not self.config.github_token:
            self.config.github_token = github_token

        if not self.config.github_token:
            logger.warning("init_warning", msg="GitHub token missing. Rate limits will be strict (60 req/hr).")

        self.client: Optional[httpx.AsyncClient] = None
        self._excluded_names: Set[str] = excluded_names or set()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrency)

        # Load Cache from Disk
        self._cache: Dict[str, Dict[str, Any]] = self._load_cache_from_disk()

    # --- PERSISTENCE LAYER ---

    def _load_cache_from_disk(self) -> Dict[str, Any]:
        """Loads cache from JSON file if exists."""
        if os.path.exists(self.config.cache_file):
            try:
                with open(self.config.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Cleanup expired entries immediately
                    current_time = time.time()
                    valid_data = {k: v for k, v in data.items() if v['expires'] > current_time}
                    logger.info("cache_loaded", entries=len(valid_data), file=self.config.cache_file)
                    return valid_data
            except Exception as e:
                logger.error("cache_load_error", error=str(e))
        return {}

    def _save_cache_to_disk(self):
        """Saves current memory cache to JSON file."""
        try:
            with open(self.config.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f)
        except Exception as e:
            logger.error("cache_save_error", error=str(e))

    # --- HTTP ENGINE ---

    async def _ensure_client(self):
        if self.client is None:
            # Fix timeout: use simple timeout or full object correctly
            timeout = httpx.Timeout(30.0, connect=self.config.timeout_connect, read=self.config.timeout_read)
            
            self.client = httpx.AsyncClient(
                timeout=timeout,
                headers={
                    "User-Agent": self.config.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
                follow_redirects=True,
                http2=False
            )

    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None
        self._save_cache_to_disk() # Persist on close

    async def _fetch_with_retry(self, url: str, params: dict = None, headers: dict = None, cache_key: str = None) -> Optional[Any]:
        """
        Robust fetch with Caching > RateLimit > Retry > Backoff.
        """
        # 1. Check Cache
        if cache_key and cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() < entry['expires']:
                logger.debug("cache_hit", url=url)
                return entry['data']

        await self._ensure_client()
        params = params or {}
        req_headers = headers or {}
        # Merge default headers with request headers
        
        retries = 3
        backoff = 2

        async with self._semaphore:
            for attempt in range(retries):
                start_time = time.time()
                try:
                    response = await self.client.get(url, params=params, headers=req_headers)
                    duration = int((time.time() - start_time) * 1000)

                    # Handle Rate Limits (429)
                    if response.status_code == 429:
                        wait = int(response.headers.get("Retry-After", backoff * (attempt + 1)))
                        logger.warning("rate_limit_hit", url=url, wait_seconds=wait)
                        await asyncio.sleep(wait)
                        continue

                    response.raise_for_status()

                    # Content Type Handling
                    content_type = response.headers.get("content-type", "")
                    if "application/json" in content_type:
                        data = response.json()
                    else:
                        data = response.text

                    # Update Cache
                    if cache_key:
                        self._cache[cache_key] = {
                            'data': data,
                            'expires': time.time() + self.config.cache_ttl_seconds
                        }

                    logger.info("request_success", url=url, status=response.status_code, ms=duration)
                    return data

                except httpx.HTTPStatusError as e:
                    # Don't retry client errors (4xx) except 429
                    if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                        logger.error("client_error", url=url, status=e.response.status_code)
                        break
                    logger.warning("server_error", url=url, status=e.response.status_code)
                except Exception as e:
                    logger.warning("network_error", url=url, attempt=attempt+1, error=str(e))

                # Backoff
                if attempt < retries - 1:
                    await asyncio.sleep(backoff * (attempt + 1))

        return None

    # --- UTILS ---

    def _normalize_name(self, name: str) -> str:
        if not name: return ""
        return re.sub(r'[^a-z0-9]', '', name.lower())[:50]

    def _categorize_tool(self, name: str, desc: str, tags: List[str]) -> str:
        text = f"{name} {desc} {' '.join(tags)}".lower()
        for cat, kws in self.CATEGORY_KEYWORDS.items():
            if any(k in text for k in kws): return cat
        return "llm" # Default

    def _is_blacklisted(self, name: str) -> bool:
        normalized = self._normalize_name(name)
        return any(bl in normalized for bl in self.config.blacklist)

    # =========================================================================
    # 1. HUGGINGFACE DAILY PAPERS (Priority High)
    # =========================================================================
    async def fetch_huggingface_daily_papers(self, limit: int = 15) -> List[Dict]:
        tools = []
        data = await self._fetch_with_retry("https://huggingface.co/api/daily_papers", cache_key="hf_daily_papers")

        if isinstance(data, list):
            # Sort by upvotes
            data.sort(key=lambda x: x.get("paper", {}).get("upvotes", 0), reverse=True)
            
            for p in data[:limit]:
                paper = p.get("paper", {})
                title = paper.get("title", "")
                if not title: continue
                
                upvotes = paper.get("upvotes", 0)
                summary = paper.get("summary", "")[:300]
                github_stars = paper.get("githubStars", 0) or 0
                
                # Trending score: upvotes + stars
                trending_score = (upvotes * 20) + (github_stars * 1)

                tools.append({
                    "name": title[:100],
                    "source": "HuggingFace_Papers",
                    "source_url": f"https://huggingface.co/papers/{paper.get('id')}",
                    "description_it": f"📄 Paper Trending ({upvotes}⬆️): {summary}...",
                    "description_en": f"📄 Trending Paper ({upvotes}⬆️): {summary}...",
                    "category": self._categorize_tool(title, summary, paper.get("ai_keywords", [])),
                    "tags": paper.get("ai_keywords", [])[:5],
                    "stars": upvotes, 
                    "trending_score": trending_score + 2000, # Priority Boost
                    "freshness": "today"
                })
        return tools

    # =========================================================================
    # 2. HUGGINGFACE MODELS (Recent & Trending)
    # =========================================================================
    async def fetch_huggingface_trending_models(self, limit: int = 10) -> List[Dict]:
        tools = []
        # Fetch detailed models sorted by lastModified
        data = await self._fetch_with_retry(
            f"{self.HUGGINGFACE_API}/models",
            params={"sort": "lastModified", "direction": -1, "limit": 100, "full": "true"},
            cache_key="hf_trending_models"
        )

        if isinstance(data, list):
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).strftime("%Y-%m-%d")
            
            for model in data:
                model_id = model.get("modelId", "")
                if not model_id or self._is_blacklisted(model_id): continue
                
                last_modified = model.get("lastModified", "")[:10]
                if last_modified < cutoff: continue # Too old

                downloads = model.get("downloads", 0) or 0
                likes = model.get("likes", 0) or 0
                
                # Minimum engagement filter
                if likes == 0 and downloads < 100: continue

                engagement = (likes * 10) + (downloads // 1000)
                
                tools.append({
                    "name": model_id.split("/")[-1],
                    "source": "HuggingFace_Models",
                    "source_url": f"https://huggingface.co/{model_id}",
                    "description_it": f"🤗 Modello {model.get('pipeline_tag','')}: {downloads:,} DLs, {likes} likes",
                    "description_en": f"🤗 Model {model.get('pipeline_tag','')}: {downloads:,} DLs, {likes} likes",
                    "category": self._categorize_tool(model_id, model.get("pipeline_tag",""), model.get("tags",[])),
                    "tags": model.get("tags", [])[:5],
                    "stars": likes,
                    "trending_score": engagement + 500,
                    "freshness": "48h"
                })
        
        # Sort by trending score
        tools.sort(key=lambda x: x["trending_score"], reverse=True)
        return tools[:limit]

    # =========================================================================
    # 3. HUGGINGFACE SPACES (Interactive)
    # =========================================================================
    async def fetch_huggingface_spaces(self, limit: int = 10) -> List[Dict]:
        tools = []
        data = await self._fetch_with_retry(
            f"{self.HUGGINGFACE_API}/spaces",
            params={"sort": "trending", "direction": -1, "limit": 50, "full": "true"},
            cache_key="hf_spaces"
        )
        
        if isinstance(data, list):
            for space in data:
                space_id = space.get("id", "")
                if not space_id or self._is_blacklisted(space_id): continue
                
                likes = space.get("likes", 0) or 0
                if likes < 10: continue

                sdk = space.get("sdk", "gradio")
                
                tools.append({
                    "name": space_id.split("/")[-1],
                    "source": "HuggingFace_Spaces",
                    "source_url": f"https://huggingface.co/spaces/{space_id}",
                    "description_it": f"🚀 Space Interattivo ({likes}❤️): App {sdk}",
                    "description_en": f"🚀 Interactive Space ({likes}❤️): {sdk} App",
                    "category": self._categorize_tool(space_id, sdk, space.get("tags",[])),
                    "tags": space.get("tags", [])[:5],
                    "stars": likes,
                    "trending_score": (likes * 5) + 300,
                    "freshness": "trending"
                })
        
        tools.sort(key=lambda x: x["trending_score"], reverse=True)
        return tools[:limit]

    # =========================================================================
    # 4. GITHUB TRENDING (Smart)
    # =========================================================================
    async def fetch_github_smart(self, limit: int = 10) -> List[Dict]:
        tools = []
        since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

        headers = {}
        if self.config.github_token:
            headers["Authorization"] = f"token {self.config.github_token}"

        data = await self._fetch_with_retry(
            f"{self.GITHUB_API}/search/repositories",
            params={"q": f"topic:ai stars:>50 created:>{since}", "sort": "stars", "order": "desc", "per_page": 30},
            headers=headers,
            cache_key="github_trending"
        )

        if data and "items" in data:
            for repo in data["items"]:
                name = repo.get("name", "")
                if self._is_blacklisted(name): continue

                stars = repo.get("stargazers_count", 0)
                tools.append({
                    "name": name,
                    "source": "GitHub",
                    "source_url": repo.get("html_url"),
                    "description_it": f"💻 Dev Tool ({stars}⭐): {repo.get('description', '')[:200]}",
                    "description_en": f"💻 Dev Tool ({stars}⭐): {repo.get('description', '')[:200]}",
                    "category": self._categorize_tool(name, str(repo.get("description")), repo.get("topics", [])),
                    "tags": repo.get("topics", [])[:5],
                    "stars": stars,
                    "trending_score": stars + 1000,
                    "freshness": "week"
                })
        return tools[:limit]

    # =========================================================================
    # 5. PRODUCT HUNT (Multi-Strategy)
    # =========================================================================
    async def fetch_producthunt_robust(self, limit: int = 15) -> List[Dict]:
        if not BeautifulSoup: return [] # Skip if bs4 not available
        
        tools = []
        html = await self._fetch_with_retry("https://www.producthunt.com/topics/artificial-intelligence", cache_key="ph_ai_topic")

        if not html or not isinstance(html, str): return []

        soup = BeautifulSoup(html, 'html.parser')

        # Generic strategy to find post links
        links = soup.find_all('a', href=re.compile(r'^/posts/'))
        
        seen_urls = set()
        for link in links:
            href = link.get('href')
            if href in seen_urls: continue
            
            # Extract text safely
            text = link.get_text(" | ", strip=True)
            parts = text.split(" | ")
            if len(parts) < 2: continue
            
            name = parts[0][:50]
            desc = parts[1]
            
            # Simple vote extraction heuristic
            votes = 0
            for p in parts:
                clean_p = p.replace(',', '')
                if clean_p.isdigit():
                    v = int(clean_p)
                    if v > votes: votes = v

            if votes < 10: continue

            seen_urls.add(href)
            tools.append({
                "name": name,
                "source": "Product_Hunt",
                "source_url": f"https://www.producthunt.com{href}",
                "description_it": f"🚀 SaaS Launch: {desc}",
                "description_en": f"🚀 SaaS Launch: {desc}",
                "category": "app",
                "tags": ["saas", "launch"],
                "stars": votes,
                "trending_score": 1000 + (votes * 5),
                "freshness": "today"
            })
            
        return sorted(tools, key=lambda x: x['stars'], reverse=True)[:limit]

    # =========================================================================
    # 6. BIG TECH RADAR (Official News via Hacker News)
    # =========================================================================
    async def fetch_big_tech_radar(self, limit: int = 5) -> List[Dict]:
        tools = []
        domains = ["labs.google", "openai.com", "anthropic.com", "midjourney.com", "stability.ai", "deepmind.google"]
        query = " OR ".join(domains)
        ts_48h = int((datetime.now() - timedelta(hours=48)).timestamp())

        data = await self._fetch_with_retry(
            "https://hn.algolia.com/api/v1/search",
            params={"query": query, "tags": "story", "numericFilters": f"created_at_i>{ts_48h},points>10"},
            cache_key="big_tech_radar"
        )

        if data and "hits" in data:
            for hit in data["hits"]:
                url = hit.get("url", "")
                if not url or not any(d in url for d in domains): continue
                
                title = hit.get("title", "")
                points = hit.get("points", 0)
                
                tools.append({
                    "name": title.replace("Show HN:", "").strip(),
                    "source": "Official_Launch",
                    "source_url": url,
                    "description_it": f"🚨 BIG TECH NEWS: {title}",
                    "description_en": f"🚨 BIG TECH NEWS: {title}",
                    "category": "news",
                    "tags": ["big-tech", "official"],
                    "stars": points,
                    "trending_score": 5000 + points,
                    "freshness": "breaking"
                })
        return tools[:limit]

    # =========================================================================
    # 7. HACKER NEWS AI (Discussions)
    # =========================================================================
    async def fetch_hacker_news_ai(self, limit: int = 5) -> List[Dict]:
        tools = []
        data = await self._fetch_with_retry(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": "AI OR LLM OR GPT OR machine learning",
                "tags": "story",
                "hitsPerPage": 20,
                "numericFilters": "points>50"
            },
            cache_key="hn_ai"
        )
        
        if data and "hits" in data:
            for hit in data["hits"]:
                title = hit.get("title", "")
                points = hit.get("points", 0)
                # Avoid duplicates with big tech radar
                if "openai.com" in hit.get("url", "") or "anthropic.com" in hit.get("url", ""): continue
                
                tools.append({
                    "name": title[:80],
                    "source": "Hacker_News",
                    "source_url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    "description_it": f"🔥 HN Discussione ({points} pts): {title}",
                    "description_en": f"🔥 HN Discussion ({points} pts): {title}",
                    "category": "news",
                    "tags": ["community", "discussion"],
                    "stars": points,
                    "trending_score": points + 100,
                    "freshness": "today"
                })
        return tools[:limit]

    # =========================================================================
    # 8. REDDIT ML (Community)
    # =========================================================================
    async def fetch_reddit_ml(self, limit: int = 5) -> List[Dict]:
        tools = []
        data = await self._fetch_with_retry(
            "https://www.reddit.com/r/MachineLearning/hot.json",
            params={"limit": 20},
            headers={"User-Agent": self.config.user_agent}, # Must differ from browser UA sometimes
            cache_key="reddit_ml"
        )
        
        if data and "data" in data and "children" in data["data"]:
            for post in data["data"]["children"]:
                p = post["data"]
                if p.get("stickied") or p.get("score", 0) < 20: continue
                
                tools.append({
                    "name": p.get("title", "")[:80],
                    "source": "Reddit_ML",
                    "source_url": f"https://reddit.com{p.get('permalink')}",
                    "description_it": f"🤖 Reddit ML ({p.get('score')} pts): {p.get('title')}",
                    "description_en": f"🤖 Reddit ML ({p.get('score')} pts): {p.get('title')}",
                    "category": "news",
                    "tags": ["reddit", "community"],
                    "stars": p.get("score"),
                    "trending_score": p.get("score") + 50,
                    "freshness": "today"
                })
        return tools[:limit]

    # =========================================================================
    # 9. PAPERS WITH CODE
    # =========================================================================
    async def fetch_papers_with_code(self, limit: int = 5) -> List[Dict]:
        tools = []
        data = await self._fetch_with_retry(
            f"{self.PAPERS_WITH_CODE}/papers/",
            params={"ordering": "-github_stars", "items_per_page": 10},
            cache_key="pwc_trending"
        )
        
        if data and "results" in data:
            for paper in data["results"][:limit]:
                title = paper.get("title", "")
                if not title: continue
                
                stars = paper.get("github_stars", 0) or 0
                
                tools.append({
                    "name": title[:80],
                    "source": "Papers_With_Code",
                    "source_url": f"https://paperswithcode.com{paper.get('url', '')}",
                    "description_it": f"📊 Paper+Code ({stars}⭐): {paper.get('abstract', '')[:100]}...",
                    "description_en": f"📊 Paper+Code ({stars}⭐): {paper.get('abstract', '')[:100]}...",
                    "category": "research",
                    "tags": ["code", "research"],
                    "stars": stars,
                    "trending_score": stars + 100,
                    "freshness": "recent"
                })
        return tools

    # =========================================================================
    # MAIN ORCHESTRATOR
    # =========================================================================
    async def discover_tools(self, num_tools: int = 10, categories: Optional[List[str]] = None, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Main entry point. Validates input, aggregates sources, deduplicates.
        """
        if num_tools < 1: num_tools = 10
        if num_tools > 100: num_tools = 100

        await self._ensure_client()
        start = time.time()
        logger.info("discovery_start", target=num_tools)

        # Launch all tasks
        tasks = [
            self.fetch_big_tech_radar(5),              # Hype / News
            self.fetch_huggingface_daily_papers(15),   # High Quality Research
            self.fetch_producthunt_robust(10),         # Apps / SaaS
            self.fetch_github_smart(15),               # Dev Tools
            self.fetch_huggingface_trending_models(10),# Models
            self.fetch_huggingface_spaces(10),         # Demos
            self.fetch_reddit_ml(5),                   # Community
            self.fetch_hacker_news_ai(5),              # Community
            self.fetch_papers_with_code(5)             # Research
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_tools = []

        for res in results:
            if isinstance(res, list): all_tools.extend(res)
            elif isinstance(res, Exception): logger.error("task_failed", error=str(res))


        # Deduplication Logic
        unique_map = {}
        seen = set()
        if self._excluded_names: seen.update(self._excluded_names)

        # 1. Group by Source
        tools_by_source = {}
        for t in all_tools:
            k = self._normalize_name(t["name"])
            if k in seen or k in self.config.blacklist or len(k) < 3: continue
            
            src = t.get("source", "misc")
            if src not in tools_by_source: tools_by_source[src] = []
            tools_by_source[src].append(t)

        # 2. Sort within sources
        for src in tools_by_source:
            tools_by_source[src].sort(key=lambda x: x.get("trending_score", 0), reverse=True)

        # 3. Round Robin Selection
        final_list = []
        sources = list(tools_by_source.keys())
        
        while len(final_list) < num_tools and sources:
            for src in list(sources): # Copy to safely remove
                if not tools_by_source[src]:
                    sources.remove(src)
                    continue
                
                # Pick top tool from this source
                tool = tools_by_source[src].pop(0)
                k = self._normalize_name(tool["name"])
                
                if k not in seen:
                    seen.add(k)
                    final_list.append(tool)
                    if len(final_list) >= num_tools: break
            
            if len(final_list) >= num_tools: break

        await self.close() # Save cache

        logger.info("discovery_done", found=len(final_list), time=f"{time.time()-start:.2f}s")
        return final_list

# --- CLI ENTRY POINT ---
if __name__ == "__main__":
    structlog.configure(processors=[structlog.processors.JSONRenderer()])
    async def main():
        print("🚀 Starting ToolAI V8.0 Scraper (Merged)...")
        scraper = ToolAIScraper()
        tools = await scraper.discover_tools(10)
        print(f"Found {len(tools)} tools:")
        print(json.dumps(tools, indent=2))
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
