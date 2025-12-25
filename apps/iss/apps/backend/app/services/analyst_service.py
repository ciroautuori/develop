
import json
import logging
from typing import Dict, Any, List
from app.core.config import settings
from app.services.rag_service import rag_service
import httpx

logger = logging.getLogger(__name__)

class DeepAnalystService:
    def __init__(self):
        self.ollama_url = f"http://{settings.ollama_host}:11434/api/generate"
        self.ollama_model = settings.ollama_model

    async def analyze_bando(self, bando_text: str, association_profile: str) -> Dict[str, Any]:
        """
        Perform a multi-step deep analysis of a bando.
        """
        logger.info("🚀 Starting Deep Analysis for Bando...")
        
        # Step 1: Extract Key Requirements
        requirements = await self._extract_requirements(bando_text)
        logger.info(f"📍 Extracted {len(requirements)} key requirements.")

        # Step 2: Query RAG for Internal Guidelines
        context_query = " ".join(requirements[:5])
        rag_results = await rag_service.query(context_query, n_results=5)
        rag_context = ""
        if rag_results and "documents" in rag_results and rag_results["documents"]:
            rag_context = "\n".join(rag_results["documents"][0])
        logger.info("📚 RAG Context loaded.")

        # Step 3: Comprehensive Evaluation (SWOT + Strategy)
        final_analysis = await self._perform_reasoning(
            bando_text=bando_text,
            association_profile=association_profile,
            rag_context=rag_context,
            requirements=requirements
        )
        
        return final_analysis

    async def _extract_requirements(self, text: str) -> List[str]:
        """Extract technical/legal requirements from the bando text."""
        prompt = f"""Analizza questo bando di finanziamento ed estrai i requisiti tecnici e legali fondamentali (max 10).
BANDO:
{text[:4000]}

Rispondi SOLO con una lista JSON di stringhe:
["requisito 1", "requisito 2", ...]
"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.ollama_url, json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }, timeout=60.0)
                if resp.status_code == 200:
                    return json.loads(resp.json()["response"])
        except Exception as e:
            logger.error(f"Error extracting requirements: {e}")
        return []

    async def _perform_reasoning(self, bando_text: str, association_profile: str, rag_context: str, requirements: List[str]) -> Dict[str, Any]:
        """Final multi-pronged analysis."""
        prompt = f"""Sei l'Agente Analista Senior di ISS. Il tuo compito è fornire una valutazione STRATEGICA e TECNICA di questo bando.

--- PROFILO ASSOCIAZIONE ---
{association_profile}

--- CONTESTO OPERATIVO (KNOWLEDGE BASE) ---
{rag_context}

--- REQUISITI ESTRATTI ---
{json.dumps(requirements, indent=2)}

--- TESTO BANDO (ESTRATTO) ---
{bando_text[:3000]}

--- TASK ---
Produci un report di analisi profonda che includa:
1. Valutazione di Fattibilità (0-100) basata sulla KB interna.
2. Analisi SWOT (Punti di forza, Debolezze, Opportunità, Minacce).
3. Strategia di approccio (Come dovremmo rispondere?).
4. Checklist documenti necessari (secondo le nostre guide).

Rispondi SOLO in JSON con questa struttura:
{{
  "feasibility_score": <int>,
  "swot": {{
    "strengths": [], "weaknesses": [], "opportunities": [], "threats": []
  }},
  "strategy": "<testo strategico>",
  "documents_checklist": [],
  "internal_notes": "<note basate sul contesto operativo>"
}}
"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.ollama_url, json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }, timeout=120.0)
                if resp.status_code == 200:
                    return json.loads(resp.json()["response"])
        except Exception as e:
            logger.error(f"Error in deep reasoning: {e}")
            return {"error": str(e)}
            
        return {"error": "Unknown error during analysis"}

analyst_service = DeepAnalystService()
