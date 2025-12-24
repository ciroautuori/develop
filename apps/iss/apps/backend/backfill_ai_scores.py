
import asyncio
import logging
from sqlalchemy import select
from app.database.database import async_session_maker
from app.models.bando import Bando
from app.services.ai_bandi_agent import ai_bandi_agent
from app.services.match_service import ISS_PROFILE
from app.schemas.bando import BandoUpdate
from app.crud.bando import bando_crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def backfill_ai_scores():
    async with async_session_maker() as db:
        # Recupera tutti i bandi che non hanno ancora uno score
        query = select(Bando).where(Bando.ai_score == None)
        result = await db.execute(query)
        bandi = result.scalars().all()
        
        logger.info(f"Trovati {len(bandi)} bandi da analizzare.")
        
        async with ai_bandi_agent as agent:
            for bando in bandi:
                try:
                    logger.info(f"Analizzando: {bando.title}")
                    tender_text = f"TITOLO: {bando.title}\nENTE: {bando.ente}\nDESCRIZIONE: {bando.descrizione or ''}"
                    
                    analysis = await agent.analyze_match(tender_text, ISS_PROFILE)
                    score = analysis.get('score', 0)
                    
                    await bando_crud.update_bando(db, bando.id, BandoUpdate(
                        ai_score=score,
                        ai_reasoning=analysis.get('reasoning', '')
                    ))
                    logger.info(f"✅ Completato: {bando.title} -> Score: {score}")
                    
                    # Piccolo sleep per non martellare Ollama se troppo veloce (anche se Ollama è lento di suo)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"❌ Errore bando {bando.id}: {e}")

if __name__ == "__main__":
    asyncio.run(backfill_ai_scores())
