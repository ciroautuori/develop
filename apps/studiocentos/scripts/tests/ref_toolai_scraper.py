"""
ToolAI Scraper v7.0 - ENTERPRISE EDITION 🏆
Production-ready AI tool discovery with persistent caching, multi-strategy parsing,
and robust configuration management.

Changelog v7.0:
- Added JSON disk persistence for cache (survives restarts)
- Implemented Multi-Selector fallback for Product Hunt
- Added Input Validation & Defensive Coding
- Standardized English comments for international maintenance
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
    raise ImportError("Critical dependency missing: 'beautifulsoup4'. Install via pip.")

logger = structlog.get_logger(__name__)

# --- CONFIGURATION MANAGEMENT ---

@dataclass
class ScraperConfig:
    """Centralized configuration for the scraper."""
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    max_concurrency: int = 5
    cache_ttl_seconds: int = 3600
    cache_file: str = "toolai_cache.json"
    timeout_connect: float = 10.0
    timeout_read: float = 30.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    blacklist: Set[str] = field(default_factory=lambda: {
        "tensorflow", "pytorch", "keras", "pandas", "numpy", "react", "node",
        "chatgpt", "midjourney", "google", "microsoft", "meta", "amazon"
    })

class ToolAIScraper:
    """
    Enterprise-grade scraper with persistent caching and rate limiting.
    """

    # Endpoints
    HUGGINGFACE_API = "https://huggingface.co/api"
    GITHUB_API = "https://api.github.com"

    CATEGORY_KEYWORDS = {
        "llm": ["llm", "gpt", "claude", "gemini", "chat", "text-generation", "rag", "llama", "mistral", "reasoning"],
        "image": ["image", "diffusion", "flux", "generation", "vision", "upscale", "lora"],
        "video": ["video", "sora", "runway", "pika", "animation", "motion"],
        "audio": ["audio", "speech", "tts", "voice", "music", "whisper"],
        "dev": ["code", "ide", "vscode", "copilot", "cursor", "api", "sdk", "database"],
        "app": ["app", "saas", "platform", "assistant", "workflow", "automation", "productivity"],
        "research": ["paper", "arxiv", "thesis", "experiment", "lab"]
    }

    def __init__(self, config: Optional[ScraperConfig] = None, excluded_names: Optional[Set[str]] = None):
        """
        Initialize scraper with config and persistence.
        """
        self.config = config or ScraperConfig()

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
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=self.config.timeout_connect, read=self.config.timeout_read),
                headers={
                    "User-Agent": self.config.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
                follow_redirects=True,
                http2=True
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
        return "gen-ai"

    # =========================================================================
    # 1. BIG TECH RADAR
    # =========================================================================
    async def fetch_big_tech_radar(self, limit: int = 5) -> List[Dict]:
        """Scans for official announcements from major AI labs."""
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
                title = hit.get("title", "")
                points = hit.get("points", 0)

                if not url or not any(d in url for d in domains): continue

                clean_name = re.sub(r'^(Show HN:|Launch:|Announcing)\s+', '', title, flags=re.IGNORECASE).strip()
                domain = next((d for d in domains if d in url), "Big Tech")

                tools.append({
                    "name": clean_name,
                    "source": "Official_Launch",
                    "source_url": url,
                    "description_it": f"🚨 ANNUNCIO UFFICIALE: {title} da {domain}.",
                    "description_en": f"🚨 OFFICIAL ANNOUNCEMENT: {title} from {domain}.",
                    "category": "news",
                    "tags": ["official", "big-tech"],
                    "stars": points,
                    "trending_score": 5000 + points, # HYPE FIRST
                    "freshness": "breaking"
                })
        return tools[:limit]

    # =========================================================================
    # 2. PRODUCT HUNT (Multi-Strategy Parser)
    # =========================================================================
    async def fetch_producthunt_robust(self, limit: int = 15) -> List[Dict]:
        """
        Scrapes Product Hunt with multi-selector strategy to be resilient against DOM changes.
        """
        tools = []
        html = await self._fetch_with_retry("https://www.producthunt.com/topics/artificial-intelligence", cache_key="ph_ai_topic")

        if not html or not isinstance(html, str): return []

        soup = BeautifulSoup(html, 'html.parser')

        # Strategy A: Semantic "styles_item" (Class names usually contain hash, verify strict start)
        # Strategy B: Generic Link containing /posts/ inside a List Item
        # Strategy C: Any link containing /posts/

        strategies = [
            lambda s: s.find_all('div', class_=re.compile(r'styles_item__')), # Specific container
            lambda s: s.find_all('a', href=re.compile(r'^/posts/')), # Generic Link
        ]

        raw_items = []
        for strategy in strategies:
            results = strategy(soup)
            if results:
                raw_items = results
                break # Stop at first working strategy

        seen_urls = set()

        for item in raw_items:
            try:
                # If item is div, find link inside. If item is a, use it.
                link = item if item.name == 'a' else item.find('a', href=re.compile(r'^/posts/'))
                if not link: continue

                href = link.get('href')
                if href in seen_urls: continue

                # Text Extraction Strategy
                # 1. Try to find H3 or strong tags for name
                # 2. Fallback to full text pipe split

                text_content = link.get_text(" | ", strip=True)
                parts = text_content.split(" | ")

                if len(parts) < 2: continue

                name = parts[0][:50] # Safety cap
                desc = parts[1]

                # Try to extract votes from anywhere in the string
                votes = 0
                for p in parts:
                    clean_p = p.replace(',', '')
                    if clean_p.isdigit():
                        v = int(clean_p)
                        if v > votes: votes = v # Take max number found as votes

                if votes < 10: continue

                seen_urls.add(href)
                tools.append({
                    "name": name,
                    "source": "Product_Hunt",
                    "source_url": f"https://www.producthunt.com{href}",
                    "description_it": f"🚀 Trending SaaS: {desc}",
                    "description_en": f"🚀 Trending SaaS: {desc}",
                    "category": "app",
                    "tags": ["saas", "consumer"],
                    "stars": votes,
                    "trending_score": 1000 + (votes * 5),
                    "freshness": "today"
                })
            except Exception:
                continue # Skip bad item, don't crash loop

        return sorted(tools, key=lambda x: x['stars'], reverse=True)[:limit]

    # =========================================================================
    # 3. GITHUB (Smart)
    # =========================================================================
    async def fetch_github_smart(self, limit: int = 10) -> List[Dict]:
        tools = []
        since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

        headers = {}
        if self.config.github_token:
            headers["Authorization"] = f"token {self.config.github_token}"

        data = await self._fetch_with_retry(
            f"{self.GITHUB_API}/search/repositories",
            params={"q": f"topic:ai stars:>50 created:>{since}", "sort": "stars", "order": "desc", "per_page": 20},
            headers=headers,
            cache_key="github_trending"
        )

        if data and "items" in data:
            for repo in data["items"]:
                name = repo.get("name", "")
                if self._normalize_name(name) in self.config.blacklist: continue

                stars = repo.get("stargazers_count", 0)
                tools.append({
                    "name": name,
                    "source": "GitHub",
                    "source_url": repo.get("html_url"),
                    "description_it": f"💻 Dev Tool: {repo.get('description', 'N/A')}",
                    "description_en": f"💻 Dev Tool: {repo.get('description', 'N/A')}",
                    "category": self._categorize_tool(name, str(repo.get("description")), repo.get("topics", [])),
                    "tags": repo.get("topics", [])[:5],
                    "stars": stars,
                    "trending_score": 500 + stars,
                    "freshness": "week"
                })
        return tools[:limit]

    # =========================================================================
    # 4. HUGGINGFACE
    # =========================================================================
    async def fetch_hf_papers(self, limit: int = 10) -> List[Dict]:
        tools = []
        data = await self._fetch_with_retry("https://huggingface.co/api/daily_papers", cache_key="hf_papers")

        if isinstance(data, list):
            data.sort(key=lambda x: x.get("paper", {}).get("upvotes", 0), reverse=True)
            for p in data[:limit]:
                paper = p.get("paper", {})
                upvotes = paper.get("upvotes", 0)
                tools.append({
                    "name": paper.get("title"),
                    "source": "HuggingFace_Papers",
                    "source_url": f"https://huggingface.co/papers/{paper.get('id')}",
                    "description_it": f"📄 Paper Ricerca ({upvotes}⬆️): {paper.get('summary', '')[:150]}...",
                    "description_en": f"📄 Research Paper ({upvotes}⬆️): {paper.get('summary', '')[:150]}...",
                    "category": "research",
                    "tags": ["paper"],
                    "stars": upvotes,
                    "trending_score": 200 + (upvotes * 20),
                    "freshness": "today"
                })
        return tools

    # =========================================================================
    # MAIN ORCHESTRATOR
    # =========================================================================
    async def discover_tools(self, num_tools: int = 10) -> List[Dict[str, Any]]:
        """
        Main entry point. Validates input, aggregates sources, deduplicates.
        """
        # Input Validation
        if num_tools < 1: num_tools = 10
        if num_tools > 100: num_tools = 100

        await self._ensure_client()
        start = time.time()

        tasks = [
            self.fetch_big_tech_radar(5),
            self.fetch_producthunt_robust(15),
            self.fetch_hf_papers(10),
            self.fetch_github_smart(10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_tools = []

        for res in results:
            if isinstance(res, list): all_tools.extend(res)
            else: logger.error("task_failed", error=str(res))

        # Deduplication Logic
        unique = []
        seen = set()
        if self._excluded_names: seen.update(self._excluded_names)

        # HYPE-FIRST Sorting
        all_tools.sort(key=lambda x: x.get("trending_score", 0), reverse=True)

        for t in all_tools:
            k = self._normalize_name(t["name"])
            if k not in seen and k not in self.config.blacklist and len(k) > 2:
                seen.add(k)
                unique.append(t)
                if len(unique) >= num_tools: break

        await self.close() # Save cache

        logger.info("discovery_done", found=len(unique), time=f"{time.time()-start:.2f}s")
        return unique

# --- CLI ENTRY POINT ---
if __name__ == "__main__":
    structlog.configure(processors=[structlog.processors.JSONRenderer()])
    async def main():
        print("🚀 Starting ToolAI Enterprise Scraper...")
        scraper = ToolAIScraper()
        tools = await scraper.discover_tools(5)
        print(json.dumps(tools, indent=2))
    asyncio.run(main())
