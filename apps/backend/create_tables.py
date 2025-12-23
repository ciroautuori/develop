import asyncio
from app.database.database import Base, engine

# Import ALL models to register them with Base
from app.models import *

async def create_tables():
    print(f"📊 Tabelle da creare: {len(Base.metadata.tables)}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tabelle create!")

if __name__ == "__main__":
    asyncio.run(create_tables())
