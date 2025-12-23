from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
import secrets
import json

from app.models.user import User, UserRole, UserStatus, UserSession, UserPreferences, AccessibilityNeeds
from app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserPreferencesCreate, 
    UserPreferencesUpdate,
    BulkUserOperation
)
from app.core.security import get_password_hash, verify_password


class CRUDUser:
    """CRUD operations per User model"""
    
    def __init__(self):
        self.model = User

    # ========== BASIC CRUD ==========
    
    def get(self, db: Session, user_id: int) -> Optional[User]:
        """Recupera utente per ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Recupera utente per email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Recupera utente per username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None,
        accessibility_needs: Optional[AccessibilityNeeds] = None,
        is_aps_only: bool = False
    ) -> List[User]:
        """Recupera lista utenti con filtri"""
        query = db.query(User)
        
        # Filtri
        if role:
            query = query.filter(User.role == role)
        
        if status:
            query = query.filter(User.status == status)
            
        if accessibility_needs:
            query = query.filter(User.accessibility_needs == accessibility_needs)
            
        if is_aps_only:
            query = query.filter(User.role.in_([UserRole.APS_RESPONSABILE, UserRole.APS_OPERATORE]))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.nome.ilike(search_term),
                    User.cognome.ilike(search_term),
                    User.email.ilike(search_term),
                    User.username.ilike(search_term),
                    User.aps_nome_organizzazione.ilike(search_term)
                )
            )
        
        return query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user_in: UserCreate) -> User:
        """Crea nuovo utente"""
        # Hash password
        hashed_password = get_password_hash(user_in.password)
        
        # Prepara dati utente
        user_data = user_in.dict(exclude={'password'})
        user_data['hashed_password'] = hashed_password
        user_data['privacy_policy_accepted_at'] = datetime.utcnow() if user_in.privacy_policy_accepted else None
        
        # Genera token verifica email
        user_data['email_verification_token'] = secrets.token_urlsafe(32)
        
        # Crea utente
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Crea preferenze default
        self._create_default_preferences(db, db_user.id)
        
        return db_user
    
    def update(self, db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """Aggiorna utente"""
        db_user = self.get(db, user_id)
        if not db_user:
            return None
        
        update_data = user_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def delete(self, db: Session, user_id: int, soft_delete: bool = True) -> bool:
        """Elimina utente (soft o hard delete)"""
        db_user = self.get(db, user_id)
        if not db_user:
            return False
        
        if soft_delete:
            # Soft delete - marca come cancellato
            db_user.status = UserStatus.DELETED
            db_user.email = f"deleted_{user_id}_{db_user.email}"  # Evita conflitti
            db.commit()
        else:
            # Hard delete
            db.delete(db_user)
            db.commit()
        
        return True

    # ========== AUTH OPERATIONS ==========
    
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        """Autentica utente"""
        user = self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if user.status != UserStatus.ACTIVE:
            return None
        
        # Aggiorna stats login
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        user.login_count += 1
        db.commit()
        
        return user
    
    def change_password(self, db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """Cambia password utente"""
        user = self.get(db, user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user.hashed_password):
            return False
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
    
    def reset_password_request(self, db: Session, email: str) -> Optional[str]:
        """Genera token per reset password"""
        user = self.get_by_email(db, email)
        if not user or user.status != UserStatus.ACTIVE:
            return None
        
        # Genera token con scadenza
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        db.commit()
        return reset_token
    
    def reset_password_confirm(self, db: Session, token: str, new_password: str) -> bool:
        """Conferma reset password"""
        user = db.query(User).filter(
            and_(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.utcnow()
            )
        ).first()
        
        if not user:
            return False
        
        # Aggiorna password e pulisce token
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        db.commit()
        return True
    
    def verify_email(self, db: Session, token: str) -> bool:
        """Verifica email con token"""
        user = db.query(User).filter(User.email_verification_token == token).first()
        if not user:
            return False
        
        user.is_email_verified = True
        user.email_verification_token = None
        user.status = UserStatus.ACTIVE  # Attiva account
        
        db.commit()
        return True
    
    def resend_verification(self, db: Session, email: str) -> Optional[str]:
        """Rigenera token verifica email"""
        user = self.get_by_email(db, email)
        if not user or user.is_email_verified:
            return None
        
        new_token = secrets.token_urlsafe(32)
        user.email_verification_token = new_token
        
        db.commit()
        return new_token

    # ========== ADMIN OPERATIONS ==========
    
    def change_role(self, db: Session, user_id: int, new_role: UserRole) -> bool:
        """Cambia ruolo utente (solo admin)"""
        user = self.get(db, user_id)
        if not user:
            return False
        
        user.role = new_role
        db.commit()
        return True
    
    def change_status(self, db: Session, user_id: int, new_status: UserStatus) -> bool:
        """Cambia status utente (solo admin)"""
        user = self.get(db, user_id)
        if not user:
            return False
        
        user.status = new_status
        db.commit()
        return True
    
    def bulk_operation(self, db: Session, operation: BulkUserOperation) -> Dict[str, Any]:
        """Operazioni bulk su utenti"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "errors": [],
            "processed_users": []
        }
        
        users = db.query(User).filter(User.id.in_(operation.user_ids)).all()
        
        for user in users:
            try:
                if operation.action == "activate":
                    user.status = UserStatus.ACTIVE
                elif operation.action == "suspend":
                    user.status = UserStatus.SUSPENDED
                elif operation.action == "delete":
                    user.status = UserStatus.DELETED
                elif operation.action == "change_role":
                    if operation.parameters and "role" in operation.parameters:
                        user.role = UserRole(operation.parameters["role"])
                
                results["processed_users"].append(user.id)
                results["success_count"] += 1
                
            except Exception as e:
                results["error_count"] += 1
                results["errors"].append({
                    "user_id": user.id,
                    "error": str(e)
                })
        
        db.commit()
        return results

    # ========== USER PREFERENCES ==========
    
    def get_preferences(self, db: Session, user_id: int) -> Optional[UserPreferences]:
        """Recupera preferenze utente"""
        return db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    
    def create_preferences(self, db: Session, user_id: int, prefs_in: UserPreferencesCreate) -> UserPreferences:
        """Crea preferenze utente"""
        prefs_data = prefs_in.dict()
        
        # Converti liste in JSON
        for field in ['preferred_bandi_sources', 'preferred_categories', 'custom_keywords']:
            if field in prefs_data and prefs_data[field] is not None:
                prefs_data[field] = json.dumps(prefs_data[field])
        
        prefs_data['user_id'] = user_id
        db_prefs = UserPreferences(**prefs_data)
        
        db.add(db_prefs)
        db.commit()
        db.refresh(db_prefs)
        
        return db_prefs
    
    def update_preferences(self, db: Session, user_id: int, prefs_in: UserPreferencesUpdate) -> Optional[UserPreferences]:
        """Aggiorna preferenze utente"""
        db_prefs = self.get_preferences(db, user_id)
        if not db_prefs:
            return None
        
        update_data = prefs_in.dict(exclude_unset=True)
        
        # Converti liste in JSON
        for field in ['preferred_bandi_sources', 'preferred_categories', 'custom_keywords']:
            if field in update_data and update_data[field] is not None:
                update_data[field] = json.dumps(update_data[field])
        
        for field, value in update_data.items():
            setattr(db_prefs, field, value)
        
        db.commit()
        db.refresh(db_prefs)
        return db_prefs
    
    def _create_default_preferences(self, db: Session, user_id: int):
        """Crea preferenze default per nuovo utente"""
        default_prefs = UserPreferences(
            user_id=user_id,
            theme="light",
            font_size="medium",
            notify_new_bandi=True,
            notify_bandi_expiring=True,
            alert_frequency="daily"
        )
        
        db.add(default_prefs)
        db.commit()

    # ========== STATISTICS ==========
    
    def get_user_stats(self, db: Session) -> Dict[str, Any]:
        """Statistiche utenti per admin"""
        total_users = db.query(func.count(User.id)).scalar()
        
        # Utenti per ruolo
        users_by_role = {}
        for role in UserRole:
            count = db.query(func.count(User.id)).filter(User.role == role).scalar()
            users_by_role[role.value] = count
        
        # Utenti per status
        users_by_status = {}
        for status in UserStatus:
            count = db.query(func.count(User.id)).filter(User.status == status).scalar()
            users_by_status[status.value] = count
        
        # Registrazioni recenti
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        new_today = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == today
        ).scalar()
        
        new_week = db.query(func.count(User.id)).filter(
            User.created_at >= week_ago
        ).scalar()
        
        new_month = db.query(func.count(User.id)).filter(
            User.created_at >= month_ago
        ).scalar()
        
        # Utenti attivi
        active_today = db.query(func.count(User.id)).filter(
            func.date(User.last_activity) == today
        ).scalar()
        
        active_week = db.query(func.count(User.id)).filter(
            User.last_activity >= week_ago
        ).scalar()
        
        # APS e accessibilità
        aps_count = db.query(func.count(User.id)).filter(
            User.role.in_([UserRole.APS_RESPONSABILE, UserRole.APS_OPERATORE])
        ).scalar()
        
        accessibility_count = db.query(func.count(User.id)).filter(
            User.accessibility_needs != AccessibilityNeeds.NONE
        ).scalar()
        
        return {
            "total_users": total_users,
            "users_by_role": users_by_role,
            "users_by_status": users_by_status,
            "new_registrations_today": new_today,
            "new_registrations_week": new_week,
            "new_registrations_month": new_month,
            "active_users_today": active_today,
            "active_users_week": active_week,
            "aps_organizations": aps_count,
            "accessibility_users": accessibility_count
        }
    
    def get_user_activity(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Statistiche attività utente singolo"""
        user = self.get(db, user_id)
        if not user:
            return {}
        
        return {
            "user_id": user_id,
            "bandi_viewed": 0,  # TODO: implementare tracking
            "bandi_saved": 0,   # TODO: implementare quando avremo saved bandi
            "searches_performed": 0,  # TODO: implementare tracking
            "exports_generated": 0,   # TODO: implementare tracking
            "corsi_attended": 0,      # TODO: implementare quando avremo corsi
            "eventi_participated": 0, # TODO: implementare quando avremo eventi
            "last_activity": user.last_activity,
            "total_points": user.points,
            "current_level": user.level
        }
    
    def update_activity(self, db: Session, user_id: int):
        """Aggiorna timestamp ultima attività"""
        user = self.get(db, user_id)
        if user:
            user.last_activity = datetime.utcnow()
            db.commit()


# Istanza singleton
user_crud = CRUDUser()
