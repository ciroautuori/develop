"""Servizio completo per gestione utenti multi-ruolo
Supporta Admin, Customer, User con portfolio personalizzati.
"""

import re
from datetime import UTC
from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.auth.models import User, UserRole
from app.domain.auth.schemas import UserCreate, UserUpdate
from app.domain.auth.services import AuthService

if TYPE_CHECKING:
    # Profile model removed - merged into User
    from app.domain.portfolio.schemas import UserProfileCreate

class UserService:
    """Servizio completo per operazioni CRUD su utenti."""

    @staticmethod
    def generate_unique_username(db: Session, email: str, base_username: str | None = None) -> str:
        """Generate unique username from email or base_username.

        Args:
            db: Database session
            email: User email
            base_username: Optional base username to use

        Returns:
            Unique username
        """
        if base_username:
            # Clean and validate base username
            base = re.sub(r"[^a-z0-9_]", "", base_username.lower())
        else:
            # Extract from email: john.doe@gmail.com -> johndoe
            base = email.split("@")[0].lower()
            base = re.sub(r"[^a-z0-9]", "", base)

        # Ensure minimum length
        if len(base) < 3:
            base = base + "user"

        # Truncate if too long
        base = base[:25]

        # Check if username exists
        username = base
        counter = 1

        while db.query(User).filter(User.username == username).first():
            # Add incrementing suffix
            suffix = str(counter)
            username = base[: 30 - len(suffix) - 1] + "_" + suffix
            counter += 1

            # Safety: prevent infinite loop
            if counter > 9999:
                import secrets

                username = base[:20] + "_" + secrets.token_hex(4)
                break

        return username

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Crea un nuovo utente con ruolo specificato.

        Args:
            db: Sessione database
            user_data: Dati utente da creare

        Returns:
            User creato

        Raises:
            HTTPException: Se email già esistente
        """
        # Verifica email univoca
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

        # Generate username if not provided
        if not user_data.username:
            username = UserService.generate_unique_username(db, user_data.email)
        else:
            # Verify username is unique
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
                )
            username = user_data.username

        # Hash della password
        hashed_password = AuthService.get_password_hash(user_data.password)

        # Crea utente
        user_dict = user_data.model_dump()
        user_dict.pop("password")  # Rimuovi password in chiaro
        user_dict["username"] = username  # Set generated or validated username

        db_user = User(**user_dict, password=hashed_password)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def create_trial_user_with_profile(
        db: Session,
        user_data: UserCreate,
        profile_data: Optional["UserProfileCreate"] = None,
        trial_days: int = 30,
    ) -> User:
        """Crea un utente TRIAL con portfolio e scadenza 30 giorni.

        Args:
            db: Sessione database
            user_data: Dati utente
            profile_data: Dati portfolio opzionali
            trial_days: Giorni di trial (default 30)

        Returns:
            User TRIAL con Profile collegato
        """
        from datetime import datetime, timedelta

        # Forza ruolo TRIAL
        user_data.role = UserRole.TRIAL

        # Crea utente
        user = UserService.create_user(db, user_data)

        # Imposta scadenza trial
        trial_expiry = datetime.now(UTC) + timedelta(days=trial_days)
        user.trial_expires_at = trial_expiry

        # NOTE: Profile model removed - merged into User model
        # profile_data parameter kept for backward compatibility but not used

        # Salva modifiche utente
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_customer_with_profile(
        db: Session, user_data: UserCreate, profile_data: Optional["UserProfileCreate"] = None
    ) -> User:
        """Crea un Customer con portfolio automatico (utente pagante).

        Args:
            db: Sessione database
            user_data: Dati utente
            profile_data: Dati portfolio opzionali

        Returns:
            User Customer con Profile collegato
        """
        # Forza ruolo Customer
        user_data.role = UserRole.CUSTOMER

        # Crea utente
        user = UserService.create_user(db, user_data)

        # NOTE: Profile model removed - merged into User model
        # profile_data parameter kept for backward compatibility but not used

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_pro_user_with_profile(
        db: Session, user_data: UserCreate, profile_data: Optional["UserProfileCreate"] = None
    ) -> User:
        """Crea un utente PRO con portfolio automatico (premium).

        Args:
            db: Sessione database
            user_data: Dati utente
            profile_data: Dati portfolio opzionali

        Returns:
            User PRO con Profile collegato
        """
        # Forza ruolo PRO
        user_data.role = UserRole.PRO

        # Crea utente
        user = UserService.create_user(db, user_data)

        # Crea profile collegato se fornito
        if profile_data:
            # Profile model removed - merged into User

            profile_dict = profile_data.model_dump()
            profile_dict["user_id"] = user.id

            # Se email non specificata nel profile, usa quella dell'utente
            if not profile_dict.get("email"):
                profile_dict["email"] = user.email

            db_profile = Profile(**profile_dict)
            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)

        # Ricarica utente con profile
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        """Ottieni utente per ID con profile caricato.

        Args:
            db: Sessione database
            user_id: ID utente

        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Ottieni utente per email con profile caricato.

        Args:
            db: Sessione database
            email: Email utente

        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> list[User]:
        """Ottieni lista utenti con filtri.

        Args:
            db: Sessione database
            skip: Record da saltare
            limit: Limite record
            role: Filtra per ruolo
            is_active: Filtra per stato attivo

        Returns:
            Lista utenti
        """
        query = db.query(User)

        if role:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_customers_with_profiles(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Ottieni Customer con i loro portfolio.

        Args:
            db: Sessione database
            skip: Record da saltare
            limit: Limite record

        Returns:
            Lista Customer con profile
        """
        return (
            db.query(User)
            .filter(
                User.role == UserRole.CUSTOMER
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User | None:
        """Aggiorna utente esistente.

        Args:
            db: Sessione database
            user_id: ID utente da aggiornare
            user_data: Dati aggiornamento

        Returns:
            User aggiornato o None se non trovato
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        # Hash password se fornita
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])

        # Applica aggiornamenti
        for key, value in update_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Elimina utente (cascade su profile).

        Args:
            db: Sessione database
            user_id: ID utente da eliminare

        Returns:
            True se eliminato, False se non trovato
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def toggle_user_status(db: Session, user_id: int) -> User | None:
        """Attiva/disattiva utente.

        Args:
            db: Sessione database
            user_id: ID utente

        Returns:
            User aggiornato o None se non trovato
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        db_user.is_active = not db_user.is_active
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def change_user_role(db: Session, user_id: int, new_role: UserRole) -> User | None:
        """Cambia ruolo utente (solo Admin).

        Args:
            db: Sessione database
            user_id: ID utente
            new_role: Nuovo ruolo

        Returns:
            User aggiornato o None se non trovato
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        old_role = db_user.role
        db_user.role = new_role

        # NOTE: Profile model removed - merged into User model
        # Profile creation/deletion logic no longer needed

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_statistics(db: Session) -> dict:
        """Ottieni statistiche utenti per dashboard admin.

        Args:
            db: Sessione database

        Returns:
            Dict con statistiche utenti
        """
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active).count()
        admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
        customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
        customers_with_profiles = (
            db.query(User).filter(User.role == UserRole.CUSTOMER, User.user.has()).count()
        )

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admins": admins,
            "customers": customers,
            "customers_with_profiles": customers_with_profiles,
            "customers_without_profiles": customers - customers_with_profiles,
        }
