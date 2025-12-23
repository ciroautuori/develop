"""
Tool Discovery Agent

Discovers trending AI tools/models from:
- HuggingFace (models, datasets, spaces)
- GitHub (trending AI repos)
- arXiv (latest AI papers)

Uses the GROQ API for intelligent filtering and categorization.
"""

import os
import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ...core.logging import get_logger

logger = get_logger(__name__)


class DiscoveredTool(BaseModel):
    """Schema for a discovered AI tool."""
    name: str
    source: str  # huggingface, github, arxiv
    source_url: str
    description_it: str
    description_en: Optional[str] = None
    description_es: Optional[str] = None
    relevance_it: Optional[str] = None
    relevance_en: Optional[str] = None
    relevance_es: Optional[str] = None
    category: str  # llm, image, audio, video, code, multimodal
    tags: List[str] = []
    stars: Optional[int] = None
    downloads: Optional[int] = None
    trending_score: int = 0


class ToolDiscoveryAgent:
    """
    Agent for discovering trending AI tools.

    Searches multiple sources and uses AI to:
    - Filter relevant tools
    - Generate Italian descriptions
    - Calculate relevance scores
    """

    def __init__(self):
        self.huggingface_api = "https://huggingface.co/api"
        self.github_api = "https://api.github.com"
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    async def discover_tools(
        self,
        num_tools: int = 5,
        categories: List[str] = None,
        sources: List[str] = None,
    ) -> List[DiscoveredTool]:
        """
        Discover trending AI tools from multiple sources.

        Args:
            num_tools: Number of tools to return
            categories: Filter by categories (llm, image, audio, code)
            sources: Sources to search (huggingface, github)

        Returns:
            List of discovered tools with Italian descriptions
        """
        categories = categories or ["llm", "image", "audio", "code"]
        sources = sources or ["huggingface", "github"]

        logger.info(
            "toolai_discovery_start",
            num_tools=num_tools,
            categories=categories,
            sources=sources
        )

        all_tools = []

        # Discover from each source in parallel
        tasks = []
        if "huggingface" in sources:
            tasks.append(self._discover_huggingface(categories))
        if "github" in sources:
            tasks.append(self._discover_github(categories))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_tools.extend(result)
            elif isinstance(result, Exception):
                logger.error("toolai_discovery_source_error", error=str(result))

        # Sort by trending score and take top N
        all_tools.sort(key=lambda x: x.trending_score, reverse=True)
        top_tools = all_tools[:num_tools * 2]  # Get extra for filtering

        # Use AI to enhance descriptions and filter
        enhanced_tools = await self._enhance_tools_with_ai(top_tools, num_tools)

        logger.info(
            "toolai_discovery_complete",
            discovered=len(enhanced_tools)
        )

        return enhanced_tools

    async def _discover_huggingface(
        self,
        categories: List[str]
    ) -> List[DiscoveredTool]:
        """Discover trending models from HuggingFace."""
        tools = []

        # Map our categories to HuggingFace task categories
        hf_tasks = {
            "llm": ["text-generation", "text2text-generation", "conversational"],
            "image": ["text-to-image", "image-to-image", "image-classification"],
            "audio": ["text-to-audio", "audio-to-audio", "speech-recognition"],
            "video": ["text-to-video", "video-classification"],
            "code": ["code-generation", "text-to-code"],
            "multimodal": ["visual-question-answering", "image-to-text"],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for category in categories:
                if category not in hf_tasks:
                    continue

                for task in hf_tasks[category][:2]:  # Max 2 tasks per category
                    try:
                        # Get trending models for this task
                        response = await client.get(
                            f"{self.huggingface_api}/models",
                            params={
                                "pipeline_tag": task,
                                "sort": "trending",
                                "limit": 5,
                            }
                        )

                        if response.status_code != 200:
                            continue

                        models = response.json()

                        for model in models[:3]:  # Top 3 per task
                            model_id = model.get("modelId", "")
                            downloads = model.get("downloads", 0) or 0
                            likes = model.get("likes", 0) or 0

                            # Calculate trending score
                            trending_score = likes * 10 + downloads // 1000

                            tool = DiscoveredTool(
                                name=model_id.split("/")[-1] if "/" in model_id else model_id,
                                source="huggingface",
                                source_url=f"https://huggingface.co/{model_id}",
                                description_it=model.get("description", "")[:500] or f"Modello AI per {task}",
                                category=category,
                                tags=model.get("tags", [])[:5],
                                downloads=downloads,
                                trending_score=trending_score,
                            )
                            tools.append(tool)

                    except Exception as e:
                        logger.warning(
                            "huggingface_discovery_error",
                            task=task,
                            error=str(e)
                        )

        return tools

    async def _discover_github(
        self,
        categories: List[str]
    ) -> List[DiscoveredTool]:
        """Discover trending AI repositories from GitHub."""
        tools = []

        # Map categories to search queries
        github_queries = {
            "llm": "language:python topic:llm OR topic:gpt OR topic:transformer",
            "image": "language:python topic:stable-diffusion OR topic:image-generation",
            "audio": "language:python topic:text-to-speech OR topic:audio-ai",
            "code": "language:python topic:code-generation OR topic:copilot",
            "multimodal": "language:python topic:multimodal OR topic:vision-language",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for category in categories:
                if category not in github_queries:
                    continue

                try:
                    # Search for trending repos
                    response = await client.get(
                        f"{self.github_api}/search/repositories",
                        params={
                            "q": f"{github_queries[category]} created:>2024-01-01",
                            "sort": "stars",
                            "order": "desc",
                            "per_page": 5,
                        },
                        headers={
                            "Accept": "application/vnd.github.v3+json"
                        }
                    )

                    if response.status_code != 200:
                        continue

                    data = response.json()
                    repos = data.get("items", [])

                    for repo in repos[:3]:
                        stars = repo.get("stargazers_count", 0)
                        name = repo.get("name", "")

                        # Calculate trending score
                        trending_score = stars // 100

                        tool = DiscoveredTool(
                            name=name,
                            source="github",
                            source_url=repo.get("html_url", ""),
                            description_it=repo.get("description", "")[:500] or f"Repository AI {category}",
                            category=category,
                            tags=repo.get("topics", [])[:5],
                            stars=stars,
                            trending_score=trending_score,
                        )
                        tools.append(tool)

                except Exception as e:
                    logger.warning(
                        "github_discovery_error",
                        category=category,
                        error=str(e)
                    )

        return tools

    async def _enhance_tools_with_ai(
        self,
        tools: List[DiscoveredTool],
        num_tools: int
    ) -> List[DiscoveredTool]:
        """
        Use GROQ AI to enhance tool descriptions and generate Italian content.
        """
        if not tools:
            return []

        if not self.groq_api_key:
            logger.warning("groq_api_key_missing")
            return tools[:num_tools]

        # Prepare tool list for AI
        tools_text = "\n".join([
            f"- {t.name} ({t.source}): {t.description_it[:200]}"
            for t in tools
        ])

        prompt = f"""Sei un esperto di AI e machine learning. Analizza questi tool/modelli AI scoperti oggi e:

1. Seleziona i {num_tools} più interessanti e innovativi
2. Per ognuno, scrivi una descrizione PROFESSIONALE in italiano (100-150 parole)
3. Spiega perché è rilevante per aziende e sviluppatori
4. Assegna un punteggio di rilevanza (1-100)

Tool scoperti:
{tools_text}

Rispondi in formato JSON con questa struttura:
{{
    "tools": [
        {{
            "name": "nome_tool",
            "description_it": "Descrizione professionale in italiano...",
            "relevance_it": "Perché è importante...",
            "relevance_score": 85
        }}
    ]
}}"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.groq_url,
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {"role": "system", "content": "Sei un esperto di AI che scrive in italiano professionale."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000,
                    },
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code != 200:
                    logger.warning("groq_enhancement_failed", status=response.status_code)
                    return tools[:num_tools]

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Parse JSON from response
                import json
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                enhanced_data = json.loads(content.strip())

                # Match enhanced descriptions with original tools
                enhanced_tools = []
                for enhanced in enhanced_data.get("tools", []):
                    name = enhanced.get("name", "")
                    # Find matching original tool
                    for tool in tools:
                        if name.lower() in tool.name.lower() or tool.name.lower() in name.lower():
                            tool.description_it = enhanced.get("description_it", tool.description_it)
                            tool.relevance_it = enhanced.get("relevance_it")
                            tool.trending_score = enhanced.get("relevance_score", tool.trending_score)
                            enhanced_tools.append(tool)
                            break

                return enhanced_tools[:num_tools]

        except Exception as e:
            logger.error("groq_enhancement_error", error=str(e))
            return tools[:num_tools]
