import asyncio
from app.database.database import async_session_maker
from sqlalchemy import select
from app.models.bando_config import BandoConfig

async def check(): 
    async with async_session_maker() as db:
        result = await db.execute(select(BandoConfig));
        configs = result.scalars().all();
        for c in configs: 
            print(f'ID: {c.id}, Name: {c.name}, Active: {c.is_active}, Schedule: {c.schedule_enabled}, Next Run: {c.next_run}')

if __name__ == "__main__":
    asyncio.run(check())
