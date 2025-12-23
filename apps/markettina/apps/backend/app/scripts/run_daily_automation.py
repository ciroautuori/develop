"""
Script per eseguire manualmente automation jobs
Uso: python -m app.scripts.run_daily_automation
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.infrastructure.database.session import SessionLocal
from app.jobs.daily_automation import DailyAutomation


async def main():
    """Esegui tutti i job di automazione."""
    print("=" * 60)
    print("🤖 markettina - DAILY AUTOMATION")
    print("=" * 60)

    db = SessionLocal()

    try:
        await DailyAutomation.run_all_jobs(db)

        print("\n" + "=" * 60)
        print("✅ ALL JOBS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
