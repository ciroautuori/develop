"""
API Endpoints per Corsi ISS
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, Query

router = APIRouter()


@router.get("/")
def get_corsi(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
) -> Any:
    """
    Recupera lista corsi - Area in sviluppo
    """
    return {
        "items": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "message": "Area corsi in fase di sviluppo. Presto disponibile!"
    }


@router.get("/stats/overview")
def get_corsi_stats() -> Any:
    """
    Statistiche corsi
    """
    return {
        "totali": 0,
        "attivi": 0,
        "message": "Area in sviluppo"
    }
