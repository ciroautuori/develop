
import logging
import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class DraftService:
    def __init__(self):
        self.ollama_url = f"http://{settings.ollama_host}:11434/api/generate"
        self.ollama_model = settings.ollama_model

    async def generate_draft(self, bando_text: str, association_profile: str) -> str:
        """
        Generate a project draft for a specific bando.
        """
        logger.info("✍️ Generating Project Draft...")
        
        # Step 1: Query RAG for templates and similar projects
        rag_results = await rag_service.query("template progetto finanziamento lettera presentazione", n_results=3)
        rag_context = ""
        if rag_results and "documents" in rag_results and rag_results["documents"]:
            rag_context = "\n".join(rag_results["documents"][0])
            
        # Step 2: Generate Draft
        prompt = f"""Sei un Grant Writer professionista. Scrivi una bozza di progetto dettagliata per questo bando.

--- PROFILO ASSOCIAZIONE ---
{association_profile}

--- TEMPLATE E LINEE GUIDA ---
{rag_context}

--- BANDO ---
{bando_text[:4000]}

--- TASK ---
Scrivi una bozza strutturata in Markdown che includa:
1. Obiettivo del Progetto
2. Attività previste
3. Budget stimato
4. Impatto sociale
5. Lettera di presentazione elegante.

Fornisci solo il contenuto Markdown.
"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.ollama_url, json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }, timeout=300.0) # Long timeout for drafting
                
                if resp.status_code == 200:
                    return resp.json()["response"]
        except Exception as e:
            logger.error(f"Error generating draft: {e}")
            return f"Errore durante la generazione della bozza: {str(e)}"
            
        return "Generazione fallita."

draft_service = DraftService()
