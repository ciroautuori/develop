import asyncio
from datetime import datetime, time
from app.database.database import async_session_maker
from sqlalchemy import select
from app.models.bando_config import BandoConfig

async def update_config(): 
    async with async_session_maker() as db:
        result = await db.execute(select(BandoConfig).where(BandoConfig.name == "ISS Default Config"))
        config = result.scalar_one_or_none()
        if config:
            config.schedule_enabled = True
            # Set next_run to today at 16:20
            now = datetime.now()
            config.next_run = now.replace(hour=16, minute=20, second=0, microsecond=0)
            await db.commit()
            print(f"✅ Config '{config.name}' updated for 16:20 test.")
        else:
            print("❌ 'ISS Default Config' not found.")

if __name__ == "__main__":
    asyncio.run(update_config())
