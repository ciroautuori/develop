"""
Script per creare l'utente ADMIN nel database di produzione
"""
import sys
import os
sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from passlib.context import CryptContext

from app.domain.auth.models import User

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database URL from env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://markettina:markettina2025@postgres:5432/markettina")

print("🔧 Creazione utente ADMIN...")
print(f"Database: {DATABASE_URL.split('@')[1]}")

# Connect to DB
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Check if admin exists
    existing_admin = db.query(User).filter(User.email == "admin@markettina.it").first()

    if existing_admin:
        print("⚠️  Admin già esistente. Aggiorno la password...")
        existing_admin.password = pwd_context.hash("Admin2025!")
        db.commit()
        print("✅ Password admin aggiornata!")
    else:
        print("➕ Creazione nuovo utente admin...")
        admin_user = User(
            email="admin@markettina.it",
            username="admin",
            full_name="MARKETTINA Admin",
            password=pwd_context.hash("Admin2025!"),
            role="ADMIN",
            is_active=True,
            email_verified=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(admin_user)
        db.commit()
        print("✅ Utente admin creato con successo!")

    print("\n📋 Credenziali:")
    print("   Email: admin@markettina.it")
    print("   Password: Admin2025!")

except Exception as e:
    print(f"❌ Errore: {e}")
    db.rollback()
finally:
    db.close()
