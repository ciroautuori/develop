from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai_bandi_agent import ai_bandi_agent
from app.crud.bando import bando_crud
from app.schemas.bando import BandoRead

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
    
    async def get_perfect_matches(self, db: AsyncSession, limit: int = 5) -> List[Dict]:
        """
        Trova i bandi 'perfetti' analizzando quelli attivi nel DB.
        """
        # 1. Recupera bandi attivi e recenti
        bandi = await bando_crud.get_recent_bandi(db, limit=20) # Analizza gli ultimi 20
        
        matches = []
        
        async with ai_bandi_agent as agent:
            for bando in bandi:
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
                analysis = await agent.analyze_match(tender_text, ISS_PROFILE)
                
                if analysis.get('score', 0) >= 60: # Filtra solo match decenti
                    matches.append({
                        **bando.__dict__,
                        "match_score": analysis.get('score'),
                        "match_reasoning": analysis.get('reasoning'),
                        "match_strengths": analysis.get('strengths', []),
                        "match_weaknesses": analysis.get('weaknesses', [])
                    })
        
        # Ordina per score decrescente
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches[:limit]

match_service = MatchService()
