"""
Jobs Package - Automation & Scheduled Tasks
"""

from .daily_automation import DailyAutomation, setup_cron_jobs

__all__ = ['DailyAutomation', 'setup_cron_jobs']
