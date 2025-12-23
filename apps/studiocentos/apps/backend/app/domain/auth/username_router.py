"""Username availability check router"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.auth.models import User
from app.infrastructure.database import get_db

router = APIRouter()

class UsernameCheckResponse(BaseModel):
    """Username availability check response."""

    username: str
    available: bool
    suggestion: str | None = None

@router.get("/check/{username}", response_model=UsernameCheckResponse)
async def check_username_availability(
    username: str, db: Session = Depends(get_db)
) -> UsernameCheckResponse:
    """Check if username is available (no auth required for UX).

    Args:
        username: Username to check

    Returns:
        UsernameCheckResponse with availability and optional suggestion
    """
    # Check if username exists
    existing = db.query(User).filter(User.username == username.lower()).first()

    if existing:
        # Generate suggestion
        counter = 1
        suggestion = None
        while counter < 100:
            candidate = f"{username}{counter}"
            if not db.query(User).filter(User.username == candidate.lower()).first():
                suggestion = candidate.lower()
                break
            counter += 1

        return UsernameCheckResponse(
            username=username.lower(), available=False, suggestion=suggestion
        )

    return UsernameCheckResponse(username=username.lower(), available=True, suggestion=None)
