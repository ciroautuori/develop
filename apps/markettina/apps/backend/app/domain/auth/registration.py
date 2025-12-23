"""Sistema registrazione utenti completo
Supporta registrazione Admin, Customer con portfolio personalizzati.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.core.api.dependencies.permissions import PermissionChecker, require_admin
from app.domain.auth.models import User, UserRole
from app.domain.auth.schemas import UserCreate, UserRead
from app.domain.auth.user_service import UserService
from app.infrastructure.database import get_db

router = APIRouter()  # Tags in api/v1/__init__.py

class CustomerRegisterRequest(BaseModel):
    """Flat request body for customer registration to match frontend payload."""

    email: EmailStr
    password: str
    username: str | None = None  # Optional: auto-generated from email if not provided
    full_name: str | None = None
    createPortfolio: bool | None = False
    # Future: createPortfolio: bool = False  # not used here, dedicated endpoint exists

@router.post("/customer", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_customer(payload: CustomerRegisterRequest, db: Session = Depends(get_db)):
    """Registrazione Customer con corpo JSON piatto (email, password, full_name).
    Compatibile con il payload inviato dal frontend.
    """
    # Mappa al modello esistente UserCreate
    user_data = UserCreate(
        email=payload.email,
        password=payload.password,
        username=payload.username,  # Auto-generated if None
        full_name=payload.full_name,
        role=UserRole.CUSTOMER,
        is_active=True,
    )

    try:
        user = UserService.create_user(db, user_data)

        # Optionally set up profile data for the new customer (profile fields now in User model)
        if payload.createPortfolio:
            # Generate slug and profile data (simple slugify)
            import re
            base_username = payload.username or user.email.split("@")[0]
            base_slug = re.sub(r"[^\w\s-]", "", base_username.lower()).strip().replace(" ", "-")

            # Update user with profile information
            user.username = payload.username or user.email.split("@")[0]
            user.slug = base_slug
            user.title = "New Customer"
            user.bio = ""
            user.public_email = None  # Keep private initially
            user.is_public = False  # Private by default for new customers

            db.commit()
            db.refresh(user)

        return user
    except HTTPException:
        raise
    except Exception:
        logger.error("Operation failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Operation failed. Please try again later.",
        )

@router.post("/admin", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_admin(
    user_data: UserCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Registrazione Admin - Solo Admin esistenti possono creare altri Admin."""
    if not PermissionChecker.can_manage_users(current_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create admin accounts"
        )

    # Forza ruolo Admin
    user_data.role = UserRole.ADMIN

    try:
        user = UserService.create_user(db, user_data)
        return user

    except HTTPException:
        raise
    except Exception:
        logger.error("Operation failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Operation failed. Please try again later.",
        )

@router.post("/customer-with-portfolio", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_customer_with_full_portfolio(
    user_data: UserCreate, profile_data: dict, db: Session = Depends(get_db)
):
    """Registrazione Customer con portfolio completo (profile fields now in User model)
    Endpoint dedicato per onboarding completo.
    """
    # Forza ruolo Customer
    user_data.role = UserRole.CUSTOMER

    try:
        # Crea Customer con dati profile integrati
        user = UserService.create_user(db, user_data)

        # Aggiorna i campi profile del user
        import re
        base_username = profile_data.get("username", user.email.split("@")[0])
        base_slug = re.sub(r"[^\w\s-]", "", base_username.lower()).strip().replace(" ", "-")

        user.username = base_username
        user.slug = base_slug
        user.title = profile_data.get("title", "Professional")
        user.bio = profile_data.get("bio", "")
        user.public_email = profile_data.get("public_email")
        user.phone_number = profile_data.get("phone_number")
        user.linkedin_url = profile_data.get("linkedin_url")
        user.github_url = profile_data.get("github_url")
        user.avatar = profile_data.get("avatar")
        user.is_public = profile_data.get("is_public", False)

        db.commit()
        db.refresh(user)

        # Risposta completa con informazioni utente (profile fields now integrated)
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "slug": user.slug,
                "full_name": user.full_name,
                "title": user.title,
                "bio": user.bio,
                "role": user.role.value,
                "is_active": user.is_active,
                "is_public": user.is_public,
                "created_at": user.created_at.isoformat(),
                "bio": user.user.bio,
                "is_public": user.user.is_public,
                "created_at": user.user.created_at.isoformat(),
            },
            "message": "Customer account and portfolio created successfully",
            "next_steps": [
                "Complete your portfolio by adding experiences, education, and skills",
                "Set your portfolio visibility (public/private)",
                "Generate your CV PDF when ready",
            ],
        }

    except HTTPException:
        raise
    except Exception:
        logger.error("Operation failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Operation failed. Please try again later.",
        )

@router.get("/check-email/{email}")
def check_email_availability(email: str, db: Session = Depends(get_db)):
    """Verifica disponibilità email prima della registrazione."""
    existing_user = UserService.get_user_by_email(db, email)

    return {
        "email": email,
        "available": existing_user is None,
        "message": "Email is available" if existing_user is None else "Email already registered",
    }

@router.get("/registration-info")
def get_registration_info():
    """Informazioni sui tipi di registrazione disponibili."""
    return {
        "available_registrations": [
            {
                "type": "customer",
                "endpoint": "/register/customer",
                "description": "Register as Customer (can create portfolio)",
                "public": True,
                "requires_auth": False,
            },
            {
                "type": "customer_with_portfolio",
                "endpoint": "/register/customer-with-portfolio",
                "description": "Register as Customer with immediate portfolio creation",
                "public": True,
                "requires_auth": False,
            },
            {
                "type": "admin",
                "endpoint": "/register/admin",
                "description": "Create Admin account (Admin only)",
                "public": False,
                "requires_auth": True,
                "requires_role": "admin",
            },
        ],
        "user_roles": [
            {
                "role": "admin",
                "description": "Super admin with full system access",
                "capabilities": ["manage_users", "access_admin_panel", "manage_all_portfolios"],
            },
            {
                "role": "customer",
                "description": "Registered user with personal portfolio",
                "capabilities": ["create_portfolio", "manage_own_portfolio", "generate_cv"],
            },
            {
                "role": "user",
                "description": "Basic user (reserved for future features)",
                "capabilities": ["view_public_portfolios"],
            },
        ],
    }
