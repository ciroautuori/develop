"""
Automated Retention Cleanup Task
Runs daily to clean expired wizard analytics events
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.domain.analytics.services.retention_service import RetentionService
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

async def cleanup_expired_wizard_events():
    """
    Cleanup expired wizard analytics events
    Runs daily at 2 AM
    """
    logger.info("Starting automated retention cleanup...")

    try:
        # Get database session
        async for db in get_db():
            try:
                result = await RetentionService.cleanup_expired_events(db)

                logger.info(
                    f"✅ Retention cleanup completed: {result['total_deleted']} events deleted"
                )

                if result["by_type"]:
                    for event_type, count in result["by_type"].items():
                        logger.info(f"   - {event_type}: {count} events")

                break  # Exit after first successful execution

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                raise

    except Exception as e:
        logger.error(f"Fatal error in retention cleanup: {e}")

def start_retention_cleanup_scheduler():
    """
    Initialize and start the retention cleanup scheduler
    """
    # Schedule cleanup to run daily at 2:00 AM
    scheduler.add_job(
        cleanup_expired_wizard_events,
        CronTrigger(hour=2, minute=0),  # Every day at 2:00 AM
        id="wizard_retention_cleanup",
        name="Wizard Analytics Retention Cleanup",
        replace_existing=True,
        misfire_grace_time=3600,  # Allow 1 hour grace period
    )

    # Optional: Also run weekly archival (Sundays at 3:00 AM)
    scheduler.add_job(
        archive_old_wizard_events,
        CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="wizard_archival",
        name="Wizard Analytics Archival",
        replace_existing=True,
    )

    # Start scheduler
    scheduler.start()
    logger.info("✅ Retention cleanup scheduler started")
    logger.info("   - Daily cleanup: 2:00 AM")
    logger.info("   - Weekly archival: Sunday 3:00 AM")

async def archive_old_wizard_events():
    """
    Archive wizard events older than 1 year
    Runs weekly on Sundays at 3 AM
    """
    logger.info("Starting weekly archival task...")

    try:
        async for db in get_db():
            try:
                result = await RetentionService.archive_old_events(db, days_old=365)

                logger.info(
                    f"✅ Archival task completed: "
                    f"{result['events_to_archive']} events ready for archival"
                )

                break

            except Exception as e:
                logger.error(f"Error in archival task: {e}")
                raise

    except Exception as e:
        logger.error(f"Fatal error in archival: {e}")

def stop_retention_cleanup_scheduler():
    """
    Stop the retention cleanup scheduler
    """
    scheduler.shutdown(wait=True)
    logger.info("Retention cleanup scheduler stopped")

# Manual execution for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Running manual retention cleanup...")
    asyncio.run(cleanup_expired_wizard_events())
    print("Done!")
