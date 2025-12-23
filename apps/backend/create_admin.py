"""
Script per creare account ADMIN ISS Platform
Esegui: python create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Aggiungi app al path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import async_session_maker
from app.models.admin_user import AdminUser
from sqlalchemy import select


async def create_admin():
    """Crea account admin se non esiste"""
    
    async with async_session_maker() as db:
        try:
            # Controlla se admin esiste già
            result = await db.execute(
                select(AdminUser).where(AdminUser.username == "admin")
            )
            existing_admin = result.scalars().first()
            
            if existing_admin:
                print("✅ Admin già esistente!")
                print(f"   Username: {existing_admin.username}")
                print(f"   Email: {existing_admin.email}")
                print(f"   Creato: {existing_admin.created_at}")
                return
            
            # Crea nuovo admin
            admin = AdminUser(
                username="admin",
                email="admin@innovazionesocialesalernitana.it",
                full_name="ISS Administrator",
                is_active=True,
                is_superuser=True
            )
            
            # Hash password (usa il metodo del modello se esiste, altrimenti plain)
            if hasattr(admin, 'set_password'):
                admin.set_password("ISSAdmin2024!")
            else:
                # Fallback: usa bcrypt direttamente
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                admin.hashed_password = pwd_context.hash("ISSAdmin2024!")
            
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            
            print("🎉 ADMIN CREATO CON SUCCESSO!")
            print("=" * 50)
            print(f"👤 Username: admin")
            print(f"🔑 Password: ISSAdmin2024!")
            print(f"📧 Email: admin@innovazionesocialesalernitana.it")
            print(f"🆔 ID: {admin.id}")
            print("=" * 50)
            print("\n🔐 IMPORTANTE: Cambia la password al primo accesso!")
            
        except Exception as e:
            print(f"❌ Errore creazione admin: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Creazione account ADMIN ISS Platform...")
    asyncio.run(create_admin())
