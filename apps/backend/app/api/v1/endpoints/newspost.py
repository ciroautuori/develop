"""
API Endpoints ISS - Area in sviluppo
"""

from typing import Any, Optional
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
def get_items(
    *,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
) -> Any:
    """
    Area in sviluppo
    """
    return {
        "items": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "message": "Area in fase di sviluppo. Presto disponibile!"
    }


@router.get("/stats/overview")
def get_stats() -> Any:
    return {
        "totali": 0,
        "message": "Area in sviluppo"
    }


@router.get("/featured")
def get_featured() -> Any:
    return {"items": []}
