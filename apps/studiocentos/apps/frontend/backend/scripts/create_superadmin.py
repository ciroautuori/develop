"""
Script per creare il primo SuperAdmin.
Esegui: uv run python scripts/create_superadmin.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.auth.models import User, UserRole
from app.domain.auth.services import get_password_hash
from app.core.config import settings

def create_superadmin():
    """Crea il primo superadmin."""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"⚠️  Admin già esistente: {existing_admin.email}")
            response = input("Vuoi crearne un altro? (y/n): ")
            if response.lower() != 'y':
                print("❌ Operazione annullata")
                return
        
        # Get admin details
        print("\n🔐 CREAZIONE SUPERADMIN")
        print("=" * 50)
        
        email = input("Email admin: ").strip()
        if not email:
            print("❌ Email obbligatoria!")
            return
            
        password = input("Password (min 8 caratteri): ").strip()
        if len(password) < 8:
            print("❌ Password troppo corta! Minimo 8 caratteri.")
            return
            
        full_name = input("Nome completo (opzionale): ").strip() or "Admin"
        username = input("Username (opzionale): ").strip() or email.split("@")[0]
        
        # Create admin user
        admin = User(
            email=email,
            password=get_password_hash(password),
            username=username,
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_public=False,
            slug=username.lower().replace(" ", "-")
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n✅ SUPERADMIN CREATO CON SUCCESSO!")
        print("=" * 50)
        print(f"📧 Email: {admin.email}")
        print(f"👤 Username: {admin.username}")
        print(f"🔑 Role: {admin.role.value}")
        print(f"🆔 ID: {admin.id}")
        print("\n🚀 ACCESSO DASHBOARD ADMIN:")
        print("=" * 50)
        print("1. Vai su: http://localhost:3000/login")
        print(f"2. Login con: {admin.email}")
        print("3. Dopo il login, accedi a:")
        print("   - Dashboard Admin: http://localhost:3000/admin")
        print("   - Gestione Portfolio: http://localhost:3000/admin/portfolio")
        print("   - Gestione Progetti: http://localhost:3000/admin/projects")
        print("   - Gestione Servizi: http://localhost:3000/admin/services")
        print("\n💡 API Endpoints disponibili:")
        print("   - GET  /api/v1/portfolio/projects (lista progetti)")
        print("   - POST /api/v1/portfolio/projects (crea progetto)")
        print("   - GET  /api/v1/portfolio/services (lista servizi)")
        print("   - POST /api/v1/portfolio/services (crea servizio)")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_superadmin()
