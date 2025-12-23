from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.database import get_sync_db
from app.core.security import (
    get_current_user, 
    get_current_admin_user, 
    get_current_super_admin,
    create_user_tokens
)
from app.crud.user import user_crud
from app.models.user import User, UserRole, UserStatus, AccessibilityNeeds
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfileResponse,
    UserListResponse,
    UserStatsResponse,
    UserActivityResponse,
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse,
    PasswordChangeRequest,
    BulkUserOperation,
    BulkUserResponse
)

router = APIRouter()


# ========== PUBLIC ENDPOINTS ==========

@router.get("/stats", response_model=UserStatsResponse)
def get_user_statistics(
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Statistiche utenti (solo admin)"""
    stats = user_crud.get_user_stats(db)
    return UserStatsResponse(**stats)


# ========== USER PROFILE ENDPOINTS ==========

@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Profilo utente corrente"""
    # Aggiorna ultima attività
    user_crud.update_activity(db, current_user.id)
    return current_user


@router.put("/me", response_model=UserProfileResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Aggiorna profilo utente corrente"""
    updated_user = user_crud.update(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.post("/me/change-password")
def change_current_user_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Cambia password utente corrente"""
    success = user_crud.change_password(
        db, 
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}


@router.get("/me/activity", response_model=UserActivityResponse)
def get_current_user_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Statistiche attività utente corrente"""
    activity = user_crud.get_user_activity(db, current_user.id)
    return UserActivityResponse(**activity)


# ========== USER PREFERENCES ENDPOINTS ==========

@router.get("/me/preferences", response_model=UserPreferencesResponse)
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Preferenze utente corrente"""
    preferences = user_crud.get_preferences(db, current_user.id)
    if not preferences:
        # Crea preferenze default se non esistono
        default_prefs = UserPreferencesCreate()
        preferences = user_crud.create_preferences(db, current_user.id, default_prefs)
    
    return preferences


@router.put("/me/preferences", response_model=UserPreferencesResponse)
def update_user_preferences(
    prefs_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Aggiorna preferenze utente corrente"""
    preferences = user_crud.update_preferences(db, current_user.id, prefs_update)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    return preferences


# ========== ADMIN USER MANAGEMENT ==========

@router.get("/", response_model=List[UserListResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None,
    accessibility_needs: Optional[AccessibilityNeeds] = None,
    is_aps_only: bool = False,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Lista utenti con filtri (solo admin)"""
    users = user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        status=status,
        search=search,
        accessibility_needs=accessibility_needs,
        is_aps_only=is_aps_only
    )
    return users


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Dettagli utente per ID (solo admin)"""
    user = user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_sync_db)
):
    """Crea nuovo utente (solo super admin)"""
    # Verifica email non esistente
    existing_user = user_crud.get_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verifica username non esistente (se fornito)
    if user_in.username:
        existing_username = user_crud.get_by_username(db, user_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    user = user_crud.create(db, user_in)
    return user


@router.put("/{user_id}", response_model=UserProfileResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Aggiorna utente (solo admin)"""
    user = user_crud.update(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/{user_id}/change-role")
def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_sync_db)
):
    """Cambia ruolo utente (solo super admin)"""
    success = user_crud.change_role(db, user_id, new_role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"User role changed to {new_role.value}"}


@router.post("/{user_id}/change-status")
def change_user_status(
    user_id: int,
    new_status: UserStatus,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Cambia status utente (solo admin)"""
    success = user_crud.change_status(db, user_id, new_status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": f"User status changed to {new_status.value}"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    soft_delete: bool = Query(True, description="Soft delete (true) or permanent delete (false)"),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_sync_db)
):
    """Elimina utente (solo super admin)"""
    # Previeni auto-eliminazione
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_crud.delete(db, user_id, soft_delete)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    delete_type = "soft deleted" if soft_delete else "permanently deleted"
    return {"message": f"User {delete_type} successfully"}


@router.post("/bulk-operation", response_model=BulkUserResponse)
def bulk_user_operation(
    operation: BulkUserOperation,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_sync_db)
):
    """Operazioni bulk su utenti (solo super admin)"""
    # Previeni operazioni su se stesso
    if current_user.id in operation.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot perform bulk operations on your own account"
        )
    
    result = user_crud.bulk_operation(db, operation)
    return BulkUserResponse(**result)


# ========== ACCESSIBILITY ENDPOINTS ==========

@router.get("/accessibility/users", response_model=List[UserListResponse])
def get_accessibility_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    needs: Optional[AccessibilityNeeds] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Lista utenti con esigenze di accessibilità (solo admin)"""
    users = user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        accessibility_needs=needs
    )
    
    # Filtra solo utenti con esigenze di accessibilità
    accessibility_users = [u for u in users if u.needs_accessibility_support]
    
    return accessibility_users


@router.get("/accessibility/stats")
def get_accessibility_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Statistiche accessibilità utenti"""
    stats = user_crud.get_user_stats(db)
    
    # Conta utenti per tipo di esigenza
    accessibility_breakdown = {}
    for need in AccessibilityNeeds:
        if need != AccessibilityNeeds.NONE:
            count = db.query(User).filter(User.accessibility_needs == need).count()
            accessibility_breakdown[need.value] = count
    
    return {
        "total_accessibility_users": stats["accessibility_users"],
        "accessibility_breakdown": accessibility_breakdown,
        "percentage_of_total": (stats["accessibility_users"] / stats["total_users"]) * 100 if stats["total_users"] > 0 else 0
    }


# ========== APS ENDPOINTS ==========

@router.get("/aps/organizations", response_model=List[UserListResponse])
def get_aps_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Lista organizzazioni APS (solo admin)"""
    users = user_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        is_aps_only=True
    )
    return users


@router.get("/aps/stats")
def get_aps_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_sync_db)
):
    """Statistiche APS"""
    stats = user_crud.get_user_stats(db)
    
    # Dettagli APS
    responsabile_count = db.query(User).filter(User.role == UserRole.APS_RESPONSABILE).count()
    operatore_count = db.query(User).filter(User.role == UserRole.APS_OPERATORE).count()
    
    # Settori di attività più comuni
    settori_query = db.query(User.aps_settore_attivita).filter(
        User.aps_settore_attivita.isnot(None),
        User.role.in_([UserRole.APS_RESPONSABILE, UserRole.APS_OPERATORE])
    ).all()
    
    settori = [s[0] for s in settori_query if s[0]]
    settori_count = {}
    for settore in settori:
        settori_count[settore] = settori_count.get(settore, 0) + 1
    
    return {
        "total_aps_users": stats["aps_organizations"],
        "aps_responsabili": responsabile_count,
        "aps_operatori": operatore_count,
        "top_sectors": dict(sorted(settori_count.items(), key=lambda x: x[1], reverse=True)[:10])
    }
