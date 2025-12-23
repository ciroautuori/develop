"""
Biometrics API Router

Endpoints for recording and retrieving biometric measurements.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.infrastructure.persistence.database import get_db
from src.infrastructure.config.dependencies import get_biometric_repository, get_record_biometric_use_case
from src.application.dtos.dtos import BiometricEntryDTO, RecordBiometricRequestDTO
from src.domain.entities.biometric import BiometricType
from src.infrastructure.security.security import CurrentUser

router = APIRouter()


@router.post("/record", response_model=BiometricEntryDTO, status_code=status.HTTP_201_CREATED)
async def record_biometric(
    request: RecordBiometricRequestDTO,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Record a biometric measurement.

    Supports:
    - Strength tests (1RM, 3RM, 5RM)
    - ROM assessments (hip flexion, shoulder mobility, etc.)
    - Body composition (weight, body fat %)
    - Cardiovascular metrics (resting HR, HRV, VO2max)
    """
    try:
        record_usecase = get_record_biometric_use_case(db)

        # Add user_id to request data
        biometric_data = request.dict()

        # Execute recording
        entry = await record_usecase.execute(current_user.id, biometric_data)

        return BiometricEntryDTO(**entry.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore registrazione biometrica: {str(e)}"
        )


@router.get("/strength/{exercise_id}/progression", response_model=Dict[str, Any])
async def get_strength_progression(
    exercise_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get strength progression for a specific exercise.

    Returns historical data and progression percentage.
    """
    try:
        record_usecase = get_record_biometric_use_case(db)

        progression = await record_usecase.get_strength_progression(current_user.id, exercise_id)

        return progression

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero progressione: {str(e)}"
        )


@router.get("/rom/{rom_test}/trends", response_model=Dict[str, Any])
async def get_rom_trends(
    rom_test: str,
    current_user: CurrentUser,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """
    Get ROM trends over time.

    Returns historical ROM measurements and improvement.
    """
    try:
        record_usecase = get_record_biometric_use_case(db)

        trends = await record_usecase.get_rom_trends(current_user.id, rom_test, days)

        return trends

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero trend ROM: {str(e)}"
        )


@router.get("/history", response_model=List[BiometricEntryDTO])
async def get_biometric_history(
    current_user: CurrentUser,
    type: Optional[str] = Query(None, description="Filter by type: STRENGTH, ROM, BODY_COMP, CARDIOVASCULAR"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get biometric history for user.

    Optionally filter by type and date range.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        biometric_type = BiometricType(type) if type else None

        entries = biometric_repo.get_by_user_and_date_range(
            current_user.id,
            start_date,
            end_date,
            biometric_type
        )

        return [BiometricEntryDTO(**entry.to_dict()) for entry in entries]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo biometrico non valido: {type}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero storico: {str(e)}"
        )


# NOTE: These routes MUST be defined BEFORE /{user_id} routes
# otherwise FastAPI will match "latest"/"history" as user_id

@router.get("/latest", response_model=Optional[Dict[str, Any]])
async def get_latest_biometric_for_current_user(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get latest biometric measurement for authenticated user.

    Returns most recent measurement of any type.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        # Get all recent entries
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        entries = biometric_repo.get_by_user_and_date_range(
            current_user.id,
            start_date,
            end_date
        )

        if not entries:
            return {"success": True, "biometric": None}

        # Return the most recent one
        latest = entries[-1]
        return {"success": True, "biometric": latest.to_dict()}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero ultima biometrica: {str(e)}"
        )


@router.get("/history/summary", response_model=Dict[str, Any])
async def get_biometric_history_summary_for_current_user(
    current_user: CurrentUser,
    days: int = Query(30, ge=1, le=365),
    type: Optional[str] = Query(None, description="Filter by type: STRENGTH, ROM, BODY_COMP, CARDIOVASCULAR"),
    db: Session = Depends(get_db)
):
    """
    Get biometric history for authenticated user.

    Optionally filter by type and date range.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        biometric_type = BiometricType(type) if type else None

        entries = biometric_repo.get_by_user_and_date_range(
            current_user.id,
            start_date,
            end_date,
            biometric_type
        )

        return {
            "success": True,
            "biometrics": [entry.to_dict() for entry in entries]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo biometrico non valido: {type}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero storico: {str(e)}"
        )


# Legacy routes with user_id path parameter (keep for backward compatibility)

@router.get("/latest/{user_id}", response_model=Optional[Dict[str, Any]])
async def get_latest_biometric_by_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get latest biometric measurement for a user.

    Returns most recent measurement of any type.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        # Get all recent entries
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        entries = biometric_repo.get_by_user_and_date_range(
            user_id,
            start_date,
            end_date
        )

        if not entries:
            return None

        # Return the most recent one
        latest = entries[-1]
        return latest.to_dict()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero ultima biometrica: {str(e)}"
        )


@router.get("/history/{user_id}", response_model=List[BiometricEntryDTO])
async def get_biometric_history_by_user(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    type: Optional[str] = Query(None, description="Filter by type: STRENGTH, ROM, BODY_COMP, CARDIOVASCULAR"),
    db: Session = Depends(get_db)
):
    """
    Get biometric history for user (path param version).

    Optionally filter by type and date range.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        biometric_type = BiometricType(type) if type else None

        entries = biometric_repo.get_by_user_and_date_range(
            user_id,
            start_date,
            end_date,
            biometric_type
        )

        return [BiometricEntryDTO(**entry.to_dict()) for entry in entries]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo biometrico non valido: {type}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero storico: {str(e)}"
        )


@router.get("/latest/exercise/{exercise_id}", response_model=Optional[BiometricEntryDTO])
async def get_latest_strength_test(
    exercise_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get latest strength test for a specific exercise.

    Returns most recent 1RM test.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        entry = biometric_repo.get_latest_by_exercise(current_user.id, exercise_id)

        if not entry:
            return None

        return BiometricEntryDTO(**entry.to_dict())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero ultimo test: {str(e)}"
        )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_biometric_entry(
    entry_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Delete a biometric entry.

    Only the owner can delete their entries.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        # Verify ownership
        entry = biometric_repo.get_by_id(entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entry {entry_id} not found"
            )

        if entry.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non autorizzato a eliminare questa entry"
            )

        success = biometric_repo.delete(entry_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entry {entry_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore eliminazione entry: {str(e)}"
        )


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_biometric_dashboard(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive biometric dashboard.

    Returns latest measurements, trends, and comparisons to baseline.
    """
    try:
        biometric_repo = get_biometric_repository(db)

        # Get last 30 days of data
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        all_entries = biometric_repo.get_by_user_and_date_range(
            current_user.id,
            start_date,
            end_date
        )

        # Separate by type
        strength_entries = [e for e in all_entries if e.type == BiometricType.STRENGTH]
        rom_entries = [e for e in all_entries if e.type == BiometricType.ROM]
        body_comp_entries = [e for e in all_entries if e.type == BiometricType.BODY_COMP]
        cardio_entries = [e for e in all_entries if e.type == BiometricType.CARDIOVASCULAR]

        # Get latest of each type
        latest_strength = strength_entries[-1] if strength_entries else None
        latest_rom = rom_entries[-1] if rom_entries else None
        latest_body_comp = body_comp_entries[-1] if body_comp_entries else None
        latest_cardio = cardio_entries[-1] if cardio_entries else None

        return {
            "user_id": current_user.id,
            "period_days": 30,
            "total_measurements": len(all_entries),
            "latest_measurements": {
                "strength": latest_strength.to_dict() if latest_strength else None,
                "rom": latest_rom.to_dict() if latest_rom else None,
                "body_comp": latest_body_comp.to_dict() if latest_body_comp else None,
                "cardiovascular": latest_cardio.to_dict() if latest_cardio else None
            },
            "counts_by_type": {
                "strength": len(strength_entries),
                "rom": len(rom_entries),
                "body_comp": len(body_comp_entries),
                "cardiovascular": len(cardio_entries)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore recupero dashboard: {str(e)}"
        )
