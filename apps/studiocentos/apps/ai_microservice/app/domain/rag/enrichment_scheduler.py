"""
Vector DB Enrichment Scheduler.

Scheduler automatico per arricchire il Vector Database con dati da API esterne.
Può essere eseguito come cron job o background task.
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from app.domain.rag.service import rag_service
from app.domain.rag.models import Document

logger = logging.getLogger(__name__)


class EnrichmentScheduler:
    """
    Scheduler per arricchimento automatico del Vector Database.

    Features:
        - Carica nuovi documenti da directory
        - Integra dati da API esterne (Apollo, Semrush, etc.)
        - Consolida knowledge patterns
        - Esegue cleanup di dati obsoleti
    """

    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = Path(data_dir)
        self.case_studies_dir = self.data_dir / "case_studies"
        self.last_run: Optional[datetime] = None

    async def run_enrichment(self) -> Dict[str, Any]:
        """
        Esegue ciclo completo di arricchimento.

        Returns:
            Report di esecuzione
        """
        start_time = datetime.now()
        report = {
            "timestamp": start_time.isoformat(),
            "documents_added": 0,
            "api_data_enriched": 0,
            "errors": [],
        }

        logger.info("🚀 Starting Vector DB enrichment cycle")

        # 1. Carica nuovi case studies
        try:
            added = await self._load_new_case_studies()
            report["documents_added"] = added
            logger.info(f"📄 Added {added} new documents")
        except Exception as e:
            report["errors"].append(f"Case studies: {e}")
            logger.error(f"Error loading case studies: {e}")

        # 2. Arricchisci da API (se configurate)
        try:
            enriched = await self._enrich_from_apis()
            report["api_data_enriched"] = enriched
            logger.info(f"🔗 Enriched {enriched} records from APIs")
        except Exception as e:
            report["errors"].append(f"API enrichment: {e}")
            logger.error(f"Error enriching from APIs: {e}")

        # 3. Log risultati
        elapsed = (datetime.now() - start_time).total_seconds()
        report["elapsed_seconds"] = elapsed
        self.last_run = datetime.now()

        logger.info(f"✅ Enrichment completed in {elapsed:.2f}s")

        return report

    async def _load_new_case_studies(self) -> int:
        """Carica nuovi case studies dal filesystem."""
        if not self.case_studies_dir.exists():
            logger.warning(f"Case studies directory not found: {self.case_studies_dir}")
            return 0

        added = 0
        existing_docs = await rag_service.list_documents()
        existing_filenames = {d.get("filename", "") for d in existing_docs}

        md_files = list(self.case_studies_dir.rglob("*.md"))

        for md_file in md_files:
            sector = md_file.parent.name
            filename = f"{sector}_{md_file.name}"

            # Skip if already indexed
            if filename in existing_filenames:
                continue

            try:
                content = md_file.read_text(encoding="utf-8")

                result = await rag_service.upload_document(
                    filename=filename,
                    content=content,
                    metadata={
                        "type": "case_study",
                        "sector": sector,
                        "source": "studiocentos",
                        "indexed_at": datetime.now().isoformat(),
                    },
                    user_id=1,
                )

                if result.get("status") == "indexed":
                    added += 1
                    logger.info(f"Indexed: {filename} ({result.get('chunks_count', 0)} chunks)")

            except Exception as e:
                logger.error(f"Error indexing {filename}: {e}")

        return added

    async def _enrich_from_apis(self) -> int:
        """
        Arricchisce Vector DB con dati da API esterne.

        Supporta:
            - Apollo.io: Lead data
            - Semrush: SEO keywords
            - Deepgram: Transcriptions
        """
        enriched = 0

        # Apollo.io enrichment
        apollo_key = os.getenv("APOLLO_API_KEY")
        if apollo_key:
            try:
                enriched += await self._enrich_apollo()
            except Exception as e:
                logger.warning(f"Apollo enrichment failed: {e}")

        # Semrush enrichment
        semrush_key = os.getenv("SEMRUSH_API_KEY")
        if semrush_key:
            try:
                enriched += await self._enrich_semrush()
            except Exception as e:
                logger.warning(f"Semrush enrichment failed: {e}")

        return enriched

    async def _enrich_apollo(self) -> int:
        """Arricchisce con dati lead da Apollo.io."""
        # TODO: Implement when Apollo API is integrated
        return 0

    async def _enrich_semrush(self) -> int:
        """Arricchisce con dati SEO da Semrush."""
        # TODO: Implement when Semrush API is integrated
        return 0

    async def get_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche del Vector DB."""
        docs = await rag_service.list_documents()

        # Count by type/sector
        by_sector = {}
        for doc in docs:
            sector = doc.get("metadata", {}).get("sector", "unknown")
            by_sector[sector] = by_sector.get(sector, 0) + 1

        return {
            "total_documents": len(docs),
            "by_sector": by_sector,
            "last_enrichment": self.last_run.isoformat() if self.last_run else None,
        }


# Singleton instance
enrichment_scheduler = EnrichmentScheduler()


async def run_daily_enrichment():
    """Entry point per cron job giornaliero."""
    report = await enrichment_scheduler.run_enrichment()
    print(f"Enrichment Report: {report}")
    return report


if __name__ == "__main__":
    # Per test manuale
    asyncio.run(run_daily_enrichment())
