"""
Tool Content Agent

Generates SEO-optimized content for ToolAI posts:
- Italian title and content (primary)
- English and Spanish translations
- SEO metadata
- Practical insights

Uses GROQ for content generation.
"""

import os
import json
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ...core.logging import get_logger
from .discovery_agent import DiscoveredTool
from ..brand_context import get_brand_context

logger = get_logger(__name__)


class GeneratedContent(BaseModel):
    """Schema for generated post content."""
    # Titles
    title_it: str
    title_en: Optional[str] = None
    title_es: Optional[str] = None

    # Summaries
    summary_it: str
    summary_en: Optional[str] = None
    summary_es: Optional[str] = None

    # Full content
    content_it: str
    content_en: Optional[str] = None
    content_es: Optional[str] = None

    # Insights
    insights_it: Optional[str] = None
    insights_en: Optional[str] = None
    insights_es: Optional[str] = None

    # Takeaway
    takeaway_it: Optional[str] = None
    takeaway_en: Optional[str] = None
    takeaway_es: Optional[str] = None

    # SEO
    meta_description: str
    meta_keywords: List[str] = []

    # AI info
    ai_model: str = "groq"


class ToolContentAgent:
    """
    Agent for generating ToolAI post content.

    Creates professional Italian content with SEO optimization
    and optional multi-language translations.
    """

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate_content(
        self,
        tools: List[DiscoveredTool],
        target_date: datetime,
        translate: bool = True,
    ) -> GeneratedContent:
        """
        Generate SEO-optimized content for a ToolAI post.

        Args:
            tools: List of discovered tools to feature
            target_date: Date for the post
            translate: Whether to generate EN/ES translations

        Returns:
            Complete content structure for the post
        """
        logger.info(
            "toolai_content_generation_start",
            num_tools=len(tools),
            target_date=target_date.isoformat()
        )

        if not self.groq_api_key:
            return self._generate_fallback_content(tools, target_date)

        # Step 1: Generate Italian content
        italian_content = await self._generate_italian_content(tools, target_date)

        # Step 2: Generate translations if requested
        if translate and italian_content:
            italian_content = await self._add_translations(italian_content)

        # Step 3: Generate SEO metadata
        if italian_content:
            italian_content = await self._generate_seo_metadata(italian_content)

        logger.info("toolai_content_generation_complete")

        return italian_content or self._generate_fallback_content(tools, target_date)

    async def _generate_italian_content(
        self,
        tools: List[DiscoveredTool],
        target_date: datetime
    ) -> Optional[GeneratedContent]:
        """Generate the main Italian content."""

        date_str = target_date.strftime("%d %B %Y")

        # Build tools description
        tools_text = ""
        for i, tool in enumerate(tools, 1):
            tools_text += f"""
**{i}. {tool.name}** ({tool.source})
- URL: {tool.source_url}
- Categoria: {tool.category}
- Descrizione: {tool.description_it}
- Rilevanza: {tool.relevance_it or 'Da analizzare'}
"""

        prompt = f"""Sei un esperto di AI che scrive articoli professionali per StudioCentos, una software house italiana.

Scrivi un articolo COMPLETO in italiano sulla scoperta di questi tool AI del {date_str}.

TOOL SCOPERTI OGGI:
{tools_text}

L'articolo deve includere:

1. **TITOLO** (max 60 caratteri): Accattivante, SEO-friendly, include "AI" e data

2. **SOMMARIO** (150-200 parole): Introduzione che spiega cosa sono questi tool e perché sono importanti

3. **CONTENUTO** (400-600 parole): Analisi dettagliata di ogni tool con:
   - Cosa fa e come funziona
   - Casi d'uso pratici
   - Perché è innovativo
   - Link alla fonte

4. **APPROFONDIMENTI PRATICI** (150-200 parole): Consigli su come le aziende possono usare questi tool

5. **CONCLUSIONE** (50-100 parole): Takeaway finale e call-to-action

Usa un tono professionale ma accessibile. Includi emoji dove appropriato.

Rispondi in formato JSON:
{{
    "title_it": "...",
    "summary_it": "...",
    "content_it": "...",
    "insights_it": "...",
    "takeaway_it": "..."
}}"""

        try:
            # Get brand context from RAG for consistent brand voice
            brand_ctx = await get_brand_context("content")

            system_prompt = f"""Sei un content writer esperto che scrive articoli SEO-ottimizzati in italiano professionale per StudioCentOS.

{brand_ctx}

Applica sempre il tono di voce e le linee guida del brand sopra."""

            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    self.groq_url,
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 3000,
                    },
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code != 200:
                    logger.error("groq_content_failed", status=response.status_code)
                    return None

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Parse JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                parsed = json.loads(content.strip())

                return GeneratedContent(
                    title_it=parsed.get("title_it", f"Tool AI del Giorno - {date_str}"),
                    summary_it=parsed.get("summary_it", ""),
                    content_it=parsed.get("content_it", ""),
                    insights_it=parsed.get("insights_it"),
                    takeaway_it=parsed.get("takeaway_it"),
                    meta_description="",
                    meta_keywords=[],
                    ai_model="groq/llama-3.1-8b-instant"
                )

        except Exception as e:
            logger.error("groq_content_error", error=str(e))
            return None

    async def _add_translations(
        self,
        content: GeneratedContent
    ) -> GeneratedContent:
        """Add English and Spanish translations."""

        translation_prompt = f"""Traduci il seguente contenuto italiano in inglese e spagnolo.

TITOLO ITALIANO:
{content.title_it}

SOMMARIO ITALIANO:
{content.summary_it}

CONTENUTO ITALIANO:
{content.content_it[:1500]}

APPROFONDIMENTI ITALIANO:
{content.insights_it or 'N/A'}

CONCLUSIONE ITALIANO:
{content.takeaway_it or 'N/A'}

Rispondi in formato JSON:
{{
    "title_en": "...",
    "title_es": "...",
    "summary_en": "...",
    "summary_es": "...",
    "content_en": "...",
    "content_es": "...",
    "insights_en": "...",
    "insights_es": "...",
    "takeaway_en": "...",
    "takeaway_es": "..."
}}"""

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    self.groq_url,
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Sei un traduttore professionale che traduce in inglese e spagnolo."
                            },
                            {"role": "user", "content": translation_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 3000,
                    },
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code != 200:
                    logger.warning("translation_failed", status=response.status_code)
                    return content

                data = response.json()
                text = data["choices"][0]["message"]["content"]

                # Parse JSON
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]

                parsed = json.loads(text.strip())

                # Update content with translations
                content.title_en = parsed.get("title_en")
                content.title_es = parsed.get("title_es")
                content.summary_en = parsed.get("summary_en")
                content.summary_es = parsed.get("summary_es")
                content.content_en = parsed.get("content_en")
                content.content_es = parsed.get("content_es")
                content.insights_en = parsed.get("insights_en")
                content.insights_es = parsed.get("insights_es")
                content.takeaway_en = parsed.get("takeaway_en")
                content.takeaway_es = parsed.get("takeaway_es")

                return content

        except Exception as e:
            logger.warning("translation_error", error=str(e))
            return content

    async def _generate_seo_metadata(
        self,
        content: GeneratedContent
    ) -> GeneratedContent:
        """Generate SEO metadata for the content."""

        seo_prompt = f"""Genera metadati SEO per questo articolo:

TITOLO: {content.title_it}
SOMMARIO: {content.summary_it[:300]}

Rispondi in formato JSON:
{{
    "meta_description": "Descrizione meta di max 155 caratteri",
    "meta_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.groq_url,
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Sei un esperto SEO."
                            },
                            {"role": "user", "content": seo_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 300,
                    },
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code != 200:
                    content.meta_description = content.summary_it[:155]
                    content.meta_keywords = ["AI", "tool", "machine learning", "innovazione"]
                    return content

                data = response.json()
                text = data["choices"][0]["message"]["content"]

                # Parse JSON
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]

                parsed = json.loads(text.strip())

                content.meta_description = parsed.get("meta_description", content.summary_it[:155])
                content.meta_keywords = parsed.get("meta_keywords", ["AI", "tool", "machine learning"])

                return content

        except Exception as e:
            logger.warning("seo_generation_error", error=str(e))
            content.meta_description = content.summary_it[:155]
            content.meta_keywords = ["AI", "tool", "machine learning", "innovazione"]
            return content

    def _generate_fallback_content(
        self,
        tools: List[DiscoveredTool],
        target_date: datetime
    ) -> GeneratedContent:
        """Generate fallback content when AI is unavailable."""

        date_str = target_date.strftime("%d %B %Y")

        # Build content from tools
        tools_content = ""
        for i, tool in enumerate(tools, 1):
            tools_content += f"""
### {i}. {tool.name}

**Fonte:** [{tool.source}]({tool.source_url})
**Categoria:** {tool.category}

{tool.description_it}

---
"""

        return GeneratedContent(
            title_it=f"🤖 Scoperta AI del {date_str}: I Tool del Giorno",
            summary_it=f"Oggi {date_str} abbiamo scoperto {len(tools)} nuovi tool AI innovativi che possono rivoluzionare il tuo workflow.",
            content_it=f"""# Tool AI del Giorno

Ecco i tool AI più interessanti scoperti oggi:

{tools_content}

## Come usare questi tool

Ogni tool può essere integrato nel tuo workflow per aumentare la produttività e automatizzare compiti ripetitivi.
""",
            insights_it="Questi tool rappresentano l'avanguardia dell'AI moderna. Ti consigliamo di provarli per capire come possono migliorare i tuoi processi.",
            takeaway_it="L'AI sta evolvendo rapidamente. Resta aggiornato con StudioCentos per scoprire ogni giorno le ultime novità.",
            meta_description=f"Scopri i {len(tools)} tool AI più innovativi del {date_str}. Analisi e guide pratiche.",
            meta_keywords=["AI", "tool", "machine learning", "innovazione", "tecnologia"],
            ai_model="fallback"
        )
