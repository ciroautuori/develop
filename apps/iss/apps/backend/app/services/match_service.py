import asyncio
import logging
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai_bandi_agent import ai_bandi_agent
from app.crud.bando import bando_crud
from app.schemas.bando import BandoRead

logger = logging.getLogger(__name__)

# Profilo statico ISS estratto dai documenti operativi
ISS_PROFILE = """
NOME: Innovazione Sociale Salernitana APS (ISS)
MISSION: Promuovere l'innovazione sociale e l'inclusione digitale a Salerno.
TARGET: Over 65 (alfabetizzazione digitale), Persone con disabilità, Giovani NEET.
ATTIVITÀ PRINCIPALI:
1. "Cittadini Digitali": Laboratori di alfabetizzazione digitale (SPID, smartphone) per anziani e fragili.
2. "Hackathon Accessibilità": Eventi Tech4Good per creare soluzioni inclusive.
3. Sportello di supporto digitale permanente.
AREA GEOGRAFICA: Salerno e Provincia, Regione Campania.
TEMI CHIAVE: Inclusione digitale, Accessibilità, Educazione, Terzo Settore, Giovani, Volontariato.
BUDGET PROGETTI TIPICO: 5.000€ - 50.000€.
"""

class MatchService:
    """
    Servizio per analizzare la compatibilità tra bandi e profilo associazione.
    """
    
    def __init__(self):
        self._semaphore = asyncio.Semaphore(3) # Limita la concorrenza per non sovraccaricare Ollama

    async def _analyze_single_bando(self, agent, bando, profile: str) -> Optional[Dict]:
        """Analizza un singolo bando con gestione errori e semaphore."""
        async with self._semaphore:
            try:
                # Costruisci testo per analisi
                tender_text = f"""
                TITOLO: {bando.title}
                ENTE: {bando.ente}
                DESCRIZIONE: {bando.descrizione or ''}
                CATEGORIA: {bando.categoria or ''}
                IMPORTO: {bando.importo or ''}
                LINK: {bando.link}
                """
                
                # Esegui analisi AI
                analysis = await agent.analyze_match(tender_text, profile)
                
                score = analysis.get('score', 0)
                if score >= 60: # Filtra solo match decenti
                    return {
                        **bando.__dict__,
                        "match_score": score,
                        "match_reasoning": analysis.get('reasoning'),
                        "match_strengths": analysis.get('strengths', []),
                        "match_weaknesses": analysis.get('weaknesses', [])
                    }
            except Exception as e:
                logger.error(f"Errore analisi bando {bando.id}: {e}")
            return None

    async def get_perfect_matches(self, db: AsyncSession, limit: int = 5) -> List[Dict]:
        """
        Trova i bandi 'perfetti' analizzando quelli attivi nel DB in parallelo.
        """
        # 1. Recupera bandi attivi e recenti
        bandi = await bando_crud.get_recent_bandi(db, limit=15) # Ridotto leggermente per performance
        
        async with ai_bandi_agent as agent:
            # Crea task per analisi parallela
            tasks = [self._analyze_single_bando(agent, bando, ISS_PROFILE) for bando in bandi]
            results = await asyncio.gather(*tasks)
            
            # Filtra i None (errori o score basso)
            matches = [r for r in results if r is not None]
        
        # Ordina per score decrescente
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches[:limit]

match_service = MatchService()
