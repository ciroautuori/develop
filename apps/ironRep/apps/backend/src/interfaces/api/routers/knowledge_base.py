"""
Router API per gestione Knowledge Base RAG.

Endpoints per:
- Stato del knowledge base
- Trigger aggiornamenti manuali
- Test ricerche
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

from src.infrastructure.ai.rag_service import get_rag_service
from src.infrastructure.logging import get_logger
from src.infrastructure.config.settings import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


class KBStatus(BaseModel):
    """Stato del Knowledge Base."""
    total_documents: int
    by_category: Dict[str, int]
    by_type: Dict[str, int]
    last_check: str


class SearchRequest(BaseModel):
    """Richiesta di ricerca."""
    query: str
    k: int = 5
    category: Optional[str] = None


class SearchResult(BaseModel):
    """Risultato singolo di ricerca."""
    content: str
    source: str
    type: str
    score: float
    metadata: Dict


class UpdateResponse(BaseModel):
    """Risposta aggiornamento."""
    status: str
    message: str
    task_id: Optional[str] = None


# Stato globale per tracking aggiornamenti
_update_status = {
    "in_progress": False,
    "last_update": None,
    "last_result": None
}


@router.get("/status", response_model=KBStatus)
async def get_kb_status():
    """
    Ottieni stato attuale del Knowledge Base.

    Ritorna:
    - Numero totale documenti
    - Distribuzione per categoria
    - Distribuzione per tipo
    """
    try:
        rag = get_rag_service()
        data = rag.collection.get()

        categories = {}
        types = {}

        for meta in data.get('metadatas', []):
            cat = meta.get('category', 'unknown')
            typ = meta.get('type', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            types[typ] = types.get(typ, 0) + 1

        return KBStatus(
            total_documents=len(data['ids']),
            by_category=categories,
            by_type=types,
            last_check=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Errore status KB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search_knowledge_base(request: SearchRequest):
    """
    Cerca nel Knowledge Base.

    Parametri:
    - query: Testo di ricerca
    - k: Numero risultati (default 5)
    - category: Filtra per categoria (opzionale)
    """
    try:
        rag = get_rag_service()

        filter_meta = {"category": request.category} if request.category else None

        results = rag.retrieve_context(
            query=request.query,
            k=request.k,
            filter_metadata=filter_meta
        )

        return [
            SearchResult(
                content=r['content'][:500] + "..." if len(r['content']) > 500 else r['content'],
                source=r['metadata'].get('source', 'unknown'),
                type=r['metadata'].get('type', 'unknown'),
                score=r['relevance_score'],
                metadata=r['metadata']
            )
            for r in results
        ]
    except Exception as e:
        logger.error(f"Errore ricerca KB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_update_task(include_usda: bool, include_off: bool):
    """Task background per aggiornamento KB."""
    global _update_status

    try:
        _update_status["in_progress"] = True
        logger.info("🔄 Avvio aggiornamento Knowledge Base...")

        rag = get_rag_service()
        total = 0

        # Re-inizializza core (esercizi, ricette, medical)
        logger.info("   1. Re-inizializzando core KB...")
        core_count = rag.reinitialize_knowledge_base(settings.data_dir)
        total += core_count
        logger.info(f"   ✅ Core: {core_count} documenti")

        if include_usda:
            logger.info("   2. Ingerendo USDA (delegato a script)...")
            # Per USDA usiamo lo script dedicato
            # TODO: Integrare logica direttamente qui

        if include_off:
            logger.info("   3. Ingerendo Open Food Facts (delegato a script)...")
            # Per OFF usiamo lo script dedicato
            # TODO: Integrare logica direttamente qui

        _update_status["last_update"] = datetime.now().isoformat()
        _update_status["last_result"] = {"total": total, "status": "success"}
        logger.info(f"✅ Aggiornamento completato! Totale: {total} documenti")

    except Exception as e:
        logger.error(f"❌ Errore aggiornamento: {e}")
        _update_status["last_result"] = {"error": str(e), "status": "failed"}
    finally:
        _update_status["in_progress"] = False


@router.post("/update", response_model=UpdateResponse)
async def trigger_update(
    background_tasks: BackgroundTasks,
    include_usda: bool = False,
    include_off: bool = False
):
    """
    Trigger aggiornamento Knowledge Base.

    Esegue in background:
    - Re-inizializzazione core (esercizi, ricette, medical)
    - Opzionale: Ingestione USDA
    - Opzionale: Ingestione Open Food Facts

    Parametri:
    - include_usda: Include dati USDA
    - include_off: Include Open Food Facts
    """
    global _update_status

    if _update_status["in_progress"]:
        return UpdateResponse(
            status="in_progress",
            message="Aggiornamento già in corso"
        )

    background_tasks.add_task(_run_update_task, include_usda, include_off)

    return UpdateResponse(
        status="started",
        message="Aggiornamento avviato in background",
        task_id=datetime.now().strftime("%Y%m%d_%H%M%S")
    )


@router.get("/update-status")
async def get_update_status():
    """Ottieni stato dell'ultimo aggiornamento."""
    return {
        "in_progress": _update_status["in_progress"],
        "last_update": _update_status["last_update"],
        "last_result": _update_status["last_result"]
    }


@router.post("/reinitialize")
async def reinitialize_kb():
    """
    Re-inizializza completamente il Knowledge Base.

    ⚠️ ATTENZIONE: Cancella tutti i dati esistenti e ricarica da zero.
    """
    try:
        rag = get_rag_service()
        count = rag.reinitialize_knowledge_base(settings.data_dir)

        return {
            "status": "success",
            "documents_loaded": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Errore reinizializzazione: {e}")
        raise HTTPException(status_code=500, detail=str(e))
