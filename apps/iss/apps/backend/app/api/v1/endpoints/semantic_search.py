"""
Endpoint per ricerca semantica e matching intelligente
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from fastapi_cache.decorator import cache

from app.database.database import get_db
from app.schemas.bando import BandoRead
from app.crud.bando import bando_crud

# Lazy import to avoid loading AI model at module import
def get_semantic_service():
    from app.services.semantic_search import semantic_search_service
    return semantic_search_service

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    """Richiesta ricerca semantica"""
    query: str
    limit: Optional[int] = 10
    threshold: Optional[float] = 0.3


class SemanticSearchResult(BaseModel):
    """Risultato ricerca semantica"""
    bando: BandoRead
    similarity_score: float
    match_explanation: str


class ProfileMatchRequest(BaseModel):
    """Richiesta match profilo organizzazione"""
    organization_type: Optional[str] = None  # "APS", "ODV", "Cooperativa", etc.
    sectors: Optional[List[str]] = []  # ["sociale", "cultura", "ambiente"]
    target_groups: Optional[List[str]] = []  # ["giovani", "anziani", "disabili"]
    keywords: Optional[List[str]] = []  # Parole chiave interesse
    geographical_area: Optional[str] = None  # "Salerno", "Campania", etc.
    max_amount: Optional[float] = None  # Importo massimo ricercato
    limit: Optional[int] = 10


class SuggestionsRequest(BaseModel):
    """Richiesta suggerimenti intelligenti"""
    search_history: Optional[List[str]] = []
    current_context: Optional[str] = None
    limit: Optional[int] = 5


@router.post("/search", response_model=List[SemanticSearchResult])
async def semantic_search(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    🔍 Ricerca semantica avanzata sui bandi

    Utilizza AI per trovare bandi semanticamente simili alla query,
    andando oltre la semplice ricerca per parole chiave.
    """
    try:
        results = await get_semantic_service().semantic_search(
            query=request.query,
            db=db,
            limit=request.limit,
            threshold=request.threshold
        )

        # Formatta risultati con spiegazione del match
        formatted_results = []
        for bando, similarity in results:
            explanation = _generate_match_explanation(bando, request.query, similarity)

            formatted_results.append(SemanticSearchResult(
                bando=bando,
                similarity_score=round(similarity, 3),
                match_explanation=explanation
            ))

        return formatted_results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore ricerca semantica: {str(e)}"
        )


@router.post("/match-profile", response_model=List[SemanticSearchResult])
async def match_profile_to_bandi(
    request: ProfileMatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    🎯 Match automatico profilo organizzazione con bandi rilevanti

    Analizza il profilo dell'organizzazione e trova automaticamente
    i bandi più adatti utilizzando AI semantica.
    """
    try:
        # Converti richiesta in profilo dict
        profile = request.dict(exclude_unset=True)

        results = await get_semantic_service().match_profile_to_bandi(
            profile=profile,
            db=db,
            limit=request.limit
        )

        # Formatta risultati
        formatted_results = []
        for bando, similarity in results:
            explanation = _generate_profile_match_explanation(bando, profile, similarity)

            formatted_results.append(SemanticSearchResult(
                bando=bando,
                similarity_score=round(similarity, 3),
                match_explanation=explanation
            ))

        return formatted_results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore match profilo: {str(e)}"
        )


@router.get("/suggestions", response_model=List[str])
@cache(expire=300)  # Cache 5 minuti
async def get_intelligent_suggestions(
    search_history: str = Query("", description="Storico ricerche (comma-separated)"),
    context: Optional[str] = Query(None, description="Contesto corrente"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    💡 Suggerimenti intelligenti per ricerche

    Genera suggerimenti basati su storico ricerche e context AI.
    """
    try:
        # Parsing storico
        history = [s.strip() for s in search_history.split(",") if s.strip()] if search_history else []

        suggestions = get_semantic_service().get_intelligent_suggestions(
            search_history=history,
            limit=limit
        )

        return suggestions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore generazione suggerimenti: {str(e)}"
        )


@router.get("/similar/{bando_id}", response_model=List[SemanticSearchResult])
@cache(expire=600)  # Cache 10 minuti
async def get_similar_bandi(
    bando_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    🔗 Trova bandi simili a uno specifico

    Utilizza AI per trovare bandi semanticamente simili a quello selezionato.
    """
    try:
        # Verifica esistenza bando
        target_bando = await bando_crud.get_bando(db, bando_id=bando_id)
        if not target_bando:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bando non trovato"
            )

        results = await get_semantic_service().suggest_similar_bandi(
            bando_id=bando_id,
            db=db,
            limit=limit
        )

        # Formatta risultati
        formatted_results = []
        for bando, similarity in results:
            explanation = _generate_similarity_explanation(target_bando, bando, similarity)

            formatted_results.append(SemanticSearchResult(
                bando=bando,
                similarity_score=round(similarity, 3),
                match_explanation=explanation
            ))

        return formatted_results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore ricerca bandi simili: {str(e)}"
        )


@router.post("/refresh-embeddings")
async def refresh_embeddings(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    🔄 Aggiorna embedding di tutti i bandi

    Rigenera gli embedding AI per tutti i bandi (operazione in background).
    """
    async def refresh_task():
        try:
            await get_semantic_service().generate_embeddings(db, force_refresh=True)
        except Exception as e:
            print(f"Errore refresh embedding: {e}")

    background_tasks.add_task(refresh_task)

    return {"message": "Refresh embedding avviato in background"}


@router.get("/stats")
async def get_semantic_search_stats():
    """
    📊 Statistiche sistema ricerca semantica
    """
    return {
        "total_embeddings": len(get_semantic_service().bando_embeddings),
        "last_update": get_semantic_service().last_update,
        "model_name": get_semantic_service().model_name,
        "cache_valid": get_semantic_service()._is_cache_valid()
    }


# Helper functions per spiegazioni match

def _generate_match_explanation(bando: Any, query: str, similarity: float) -> str:
    """Genera spiegazione del match per ricerca semantica"""
    if similarity > 0.8:
        return f"Match molto forte con '{query}' - alta compatibilità tematica"
    elif similarity > 0.6:
        return f"Buon match con '{query}' - temi correlati identificati"
    elif similarity > 0.4:
        return f"Match moderato con '{query}' - alcune affinità tematiche"
    else:
        return f"Match basilare con '{query}' - affinità semantica limitata"


def _generate_profile_match_explanation(bando: Any, profile: Dict, similarity: float) -> str:
    """Genera spiegazione match profilo organizzazione"""
    matches = []

    if profile.get('sectors') and bando.categoria:
        if bando.categoria.lower() in [s.lower() for s in profile['sectors']]:
            matches.append("settore")

    if profile.get('geographical_area') and bando.ente:
        if profile['geographical_area'].lower() in bando.ente.lower():
            matches.append("area geografica")

    if profile.get('keywords'):
        bando_text = f"{bando.title} {bando.descrizione or ''}".lower()
        matching_keywords = [k for k in profile['keywords'] if k.lower() in bando_text]
        if matching_keywords:
            matches.append("keywords")

    if matches:
        return f"Match su: {', '.join(matches)} (score: {similarity:.1%})"
    else:
        return f"Match semantico generale (score: {similarity:.1%})"


def _generate_similarity_explanation(target_bando: Any, similar_bando: Any, similarity: float) -> str:
    """Genera spiegazione similarità tra bandi"""
    common_aspects = []

    if target_bando.categoria and similar_bando.categoria:
        if target_bando.categoria == similar_bando.categoria:
            common_aspects.append("stessa categoria")

    if target_bando.ente and similar_bando.ente:
        if target_bando.ente == similar_bando.ente:
            common_aspects.append("stesso ente")

    if target_bando.fonte and similar_bando.fonte:
        if target_bando.fonte == similar_bando.fonte:
            common_aspects.append("stessa fonte")

    if common_aspects:
        return f"Simile per: {', '.join(common_aspects)} (score: {similarity:.1%})"
    else:
        return f"Similarità semantica nel contenuto (score: {similarity:.1%})"
