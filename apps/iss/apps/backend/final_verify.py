import asyncio
from app.database.database import async_session_maker
from sqlalchemy import select, text
from app.models.user import User

async def verify(): 
    async with async_session_maker() as db:
        # Check users
        result = await db.execute(select(User))
        users = result.scalars().all()
        print("--- USERS ---")
        for u in users: 
            print(f'Email: {u.email}, Role: {u.role}, Status: {u.status}')
        
        # Check tables
        tables = [
            "users", "aps_users", "bandi", "bando_configs", 
            "bando_applications", "bando_watchlists", "ai_recommendations",
            "projects", "events", "news_posts"
        ]
        print("\n--- TABLES CHECK ---")
        for table in tables:
            try:
                res = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"Table '{table}': {count} records found. ✅")
            except Exception as e:
                print(f"Table '{table}': ERROR - {e} ❌")

if __name__ == "__main__":
    asyncio.run(verify())
