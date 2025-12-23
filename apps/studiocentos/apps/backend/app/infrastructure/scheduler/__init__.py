"""
Scheduler Module - Background Jobs & Automation

Includes:
- Post Scheduler: Pubblicazione automatica social media
- Trial Reminder: Promemoria scadenza trial
- ToolAI Scheduler: Generazione quotidiana post ToolAI
- Marketing Content Scheduler: Generazione batch daily content (1 post + 3 stories + 1 video)
"""

from app.infrastructure.scheduler.post_scheduler import (
    post_scheduler,
    start_post_scheduler,
    stop_post_scheduler,
    PostScheduler
)
from app.infrastructure.scheduler.toolai_scheduler import (
    toolai_scheduler,
    start_toolai_scheduler,
    stop_toolai_scheduler,
    ToolAIScheduler
)
from app.infrastructure.scheduler.marketing_content_scheduler import (
    marketing_content_scheduler,
    start_marketing_scheduler,
    stop_marketing_scheduler,
    MarketingContentScheduler,
    trigger_marketing_generation
)


async def start_trial_reminder_scheduler():
    """Placeholder per trial reminders."""
    pass


async def stop_trial_reminder_scheduler():
    """Placeholder per trial reminders."""
    pass


async def start_all_schedulers():
    """Avvia tutti gli scheduler."""
    await start_post_scheduler()
    await start_trial_reminder_scheduler()
    await start_toolai_scheduler()  # ToolAI daily generation
    await start_marketing_scheduler()  # Marketing batch daily content


async def stop_all_schedulers():
    """Ferma tutti gli scheduler."""
    await stop_post_scheduler()
    await stop_trial_reminder_scheduler()
    await stop_toolai_scheduler()  # ToolAI scheduler
    await stop_marketing_scheduler()  # Marketing scheduler


__all__ = [
    'post_scheduler',
    'start_post_scheduler',
    'stop_post_scheduler',
    'PostScheduler',
    'toolai_scheduler',
    'start_toolai_scheduler',
    'stop_toolai_scheduler',
    'ToolAIScheduler',
    'marketing_content_scheduler',
    'start_marketing_scheduler',
    'stop_marketing_scheduler',
    'MarketingContentScheduler',
    'trigger_marketing_generation',
    'start_all_schedulers',
    'stop_all_schedulers',
]
