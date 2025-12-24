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
                logger.info(f"Bando: {bando.title} - Score: {score}")
                if score >= 40: # Soglia abbassata per dare più risultati in fase di test
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
        Trova i bandi 'perfetti' leggendo i punteggi pre-calcolati nel DB.
        Evita il bottleneck dell'AI in tempo reale.
        """
        # CERCA NEL DB BANDI GIÀ ANALIZZATI DALL'AI CON SCORE > 40
        from app.models.bando import Bando, BandoStatus
        from sqlalchemy import select, desc
        
        query = select(Bando).where(
            Bando.ai_score >= 40,
            Bando.status == BandoStatus.ATTIVO
        ).order_by(desc(Bando.ai_score), desc(Bando.data_trovato)).limit(limit)
        
        result = await db.execute(query)
        bandi = result.scalars().all()
        
        matches = []
        for bando in bandi:
            matches.append({
                **bando.__dict__,
                "match_score": bando.ai_score,
                "match_reasoning": bando.ai_reasoning,
                "match_strengths": [], # Eventualmente da estrarre da reasoning se strutturato
                "match_weaknesses": []
            })
            
        logger.info(f"Recuperati {len(matches)} match pre-calcolati dal database.")
        
        # Se non ci sono match pre-calcolati, prova a recuperare gli ultimi per analisi rapida (max 3 per evitare timeout)
        if not matches:
            logger.info("Nessun match pre-calcolato trovato. Eseguo analisi rapida (max 3).")
            recent_bandi = await bando_crud.get_recent_bandi(db, limit=3)
            async with ai_bandi_agent as agent:
                tasks = [self._analyze_single_bando(agent, b, ISS_PROFILE) for b in recent_bandi]
                quick_results = await asyncio.gather(*tasks)
                matches = [r for r in quick_results if r is not None]
                
                # In background (optional), salva questi risultati se vuoi
                # qui li restituiamo e basta per velocità
        
        return matches[:limit]

match_service = MatchService()
