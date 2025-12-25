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
import logging

# Configure logging for CLI execution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("daily_automation_cli")


async def main():
    """Esegui tutti i job di automazione."""
    logger.info("=" * 60)
    logger.info("🤖 STUDIOCENTOS - DAILY AUTOMATION")
    logger.info("=" * 60)

    db = SessionLocal()

    try:
        await DailyAutomation.run_all_jobs(db)

        logger.info("=" * 60)
        logger.info("✅ ALL JOBS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ ERROR: {e}", exc_info=True)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
