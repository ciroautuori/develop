"""
API Endpoints per Eventi ISS
"""

from typing import Any, Optional
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
def get_eventi(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
) -> Any:
    """
    Recupera lista eventi - Area in sviluppo
    """
    return {
        "items": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "message": "Area eventi in fase di sviluppo. Presto disponibile!"
    }


@router.get("/stats/overview")
def get_eventi_stats() -> Any:
    """
    Statistiche eventi
    """
    return {
        "totali": 0,
        "prossimi": 0,
        "message": "Area in sviluppo"
    }
