#!/usr/bin/env python3
"""
Script di inizializzazione database e creazione utente admin
"""
import asyncio
import sys
from pathlib import Path

# Aggiungi il percorso backend al PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database.database import engine, Base
from app.models.admin import AdminUser
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import async_session_maker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Crea tutte le tabelle del database"""
    async with engine.begin() as conn:
        logger.info("🔨 Creazione tabelle database...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tabelle create con successo")


async def create_admin_user(username: str = "admin", password: str = "admin123"):
    """Crea utente amministratore di default"""
    async with async_session_maker() as session:
        try:
            # Verifica se l'utente esiste già
            result = await session.execute(
                text("SELECT * FROM admin_users WHERE username = :username"),
                {"username": username}
            )
            existing_user = result.first()
            
            if existing_user:
                logger.info(f"⚠️  Utente admin '{username}' già esistente")
                return
            
            # Crea nuovo utente admin
            admin_user = AdminUser(
                username=username,
                hashed_password=get_password_hash(password)
            )
            
            session.add(admin_user)
            await session.commit()
            
            logger.info(f"✅ Utente admin creato con successo:")
            logger.info(f"   Username: {username}")
            logger.info(f"   Password: {password}")
            
        except Exception as e:
            logger.error(f"❌ Errore creazione utente admin: {e}")
            await session.rollback()
            raise


async def main():
    """Funzione principale"""
    logger.info("🚀 Inizializzazione ISS-WBS Database")
    
    # Inizializza database
    await init_database()
    
    # Crea utente admin
    await create_admin_user()
    
    logger.info("✨ Inizializzazione completata!")


if __name__ == "__main__":
    asyncio.run(main())
