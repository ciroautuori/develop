"""AlertManager - Core alert management and notifications.

HIGH-005: Extracted from alerting.py (split 2/7)
"""

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import UTC, datetime

import aiohttp

from app.core.config import settings
from app.infrastructure.monitoring.alerting.models import Alert, AlertSeverity

logger = logging.getLogger(__name__)


class AlertManager:
    """Enterprise Alert Management System."""

    def __init__(self):
        self.alert_thresholds = {
            # Payment Alerts
            "payment_failure_rate": 0.05,  # 5% failure rate
            "payment_amount_loss": 500.00,  # €500 loss threshold
            "stripe_webhook_delay": 300,  # 5 min webhook delay
            # Performance Alerts
            "api_response_time": 1000,  # 1s response time
            "database_query_time": 500,  # 500ms query time
            "error_rate": 0.01,  # 1% error rate
            "cpu_usage": 80,  # 80% CPU usage
            "memory_usage": 85,  # 85% memory usage
            # Uptime Alerts
            "availability_sla": 99.99,  # 99.99% uptime SLA
            "health_check_failures": 3,  # 3 consecutive failures
            # Security Alerts
            "failed_login_attempts": 10,  # 10 failed attempts/min
            "suspicious_ip_requests": 100,  # 100 req/min from single IP
            "malformed_requests": 50,  # 50 malformed requests/min
        }

        self.notification_channels = {
            "slack_webhook": getattr(settings, "SLACK_WEBHOOK_URL", None),
            "email_alerts": getattr(settings, "ALERT_EMAIL", None),
            "pagerduty": getattr(settings, "PAGERDUTY_API_KEY", None),
            "discord_webhook": getattr(settings, "DISCORD_WEBHOOK_URL", None),
        }

    async def trigger_alert(self, alert: Alert) -> bool:
        """Trigger alert attraverso tutti i canali configurati."""
        try:
            logger.warning(f"ALERT TRIGGERED: {alert.severity.upper()} - {alert.title}")

            # Log alert to database/storage
            await self._persist_alert(alert)

            # Send notifications based on severity
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                await self._send_critical_notifications(alert)
            else:
                await self._send_standard_notifications(alert)

            # Auto-escalate critical alerts after 15 minutes
            if alert.severity == AlertSeverity.CRITICAL:
                asyncio.create_task(self._auto_escalate(alert, delay_minutes=15))

            return True

        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            return False

    async def _send_critical_notifications(self, alert: Alert):
        """Send critical alerts to all channels immediately."""
        tasks = []

        # Slack notification
        if self.notification_channels["slack_webhook"]:
            tasks.append(self._send_slack_alert(alert))

        # Email notification
        if self.notification_channels["email_alerts"]:
            tasks.append(self._send_email_alert(alert))

        # PagerDuty for critical issues
        if self.notification_channels["pagerduty"] and alert.severity == AlertSeverity.CRITICAL:
            tasks.append(self._send_pagerduty_alert(alert))

        # Execute all notifications concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_standard_notifications(self, alert: Alert):
        """Send standard alerts to configured channels."""
        # Only Slack for medium/low alerts to avoid spam
        if self.notification_channels["slack_webhook"]:
            await self._send_slack_alert(alert)

    async def _send_slack_alert(self, alert: Alert):
        """Send alert to Slack via webhook."""
        if not self.notification_channels["slack_webhook"]:
            return

        # Color coding based on severity
        color_map = {
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.HIGH: "warning",
            AlertSeverity.MEDIUM: "#ff9900",
            AlertSeverity.LOW: "good",
            AlertSeverity.INFO: "#0099ff",
        }

        emoji_map = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "🔶",
            AlertSeverity.LOW: "🔵",
            AlertSeverity.INFO: "ℹ️",
        }

        payload = {
            "attachments": [
                {
                    "color": color_map.get(alert.severity, "good"),
                    "title": f"{emoji_map.get(alert.severity, '🔔')} CV-Lab Alert: {alert.title}",
                    "text": alert.description,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.upper(), "short": True},
                        {"title": "Category", "value": alert.category.upper(), "short": True},
                        {"title": "Source", "value": alert.source, "short": True},
                        {
                            "title": "Time",
                            "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "short": True,
                        },
                    ],
                    "footer": "CV-Lab Monitoring",
                    "ts": int(alert.timestamp.timestamp()),
                }
            ]
        }

        try:
            async with aiohttp.ClientSession() as session, session.post(
                self.notification_channels["slack_webhook"],
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    logger.info(f"Slack alert sent: {alert.id}")
                else:
                    logger.error(f"Failed to send Slack alert: {response.status}")
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")

    async def _send_email_alert(self, alert: Alert):
        """Send alert via email."""
        # Email implementation placeholder
        logger.info(f"Email alert would be sent: {alert.id}")

    async def _send_pagerduty_alert(self, alert: Alert):
        """Send critical alert to PagerDuty."""
        if not self.notification_channels["pagerduty"]:
            return

        payload = {
            "routing_key": self.notification_channels["pagerduty"],
            "event_action": "trigger",
            "dedup_key": f"cv-lab-{alert.category}-{alert.id}",
            "payload": {
                "summary": f"CV-Lab: {alert.title}",
                "source": alert.source,
                "severity": alert.severity,
                "component": "cv-lab-saas",
                "group": alert.category,
                "class": "production-alert",
                "custom_details": alert.metadata,
            },
        }

        try:
            async with aiohttp.ClientSession() as session, session.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 202:
                    logger.info(f"PagerDuty alert sent: {alert.id}")
                else:
                    logger.error(f"Failed to send PagerDuty alert: {response.status}")
        except Exception as e:
            logger.error(f"PagerDuty notification failed: {e}")

    async def _persist_alert(self, alert: Alert):
        """Persist alert to database for tracking and reporting."""
        try:
            # Fallback to logging if database unavailable
            alert_data = asdict(alert)
            alert_data["timestamp"] = alert.timestamp.isoformat()
            logger.info(f"ALERT_PERSIST: {json.dumps(alert_data)}")

        except Exception as e:
            logger.error(f"Failed to persist alert: {e}")

    async def _auto_escalate(self, alert: Alert, delay_minutes: int = 15):
        """Auto-escalate unacknowledged critical alerts."""
        await asyncio.sleep(delay_minutes * 60)

        # Check if alert is still unresolved and unacknowledged
        if not alert.resolved and not alert.acknowledged:
            escalated_alert = Alert(
                id=f"{alert.id}-escalated",
                title=f"ESCALATED: {alert.title}",
                description=f"Alert not acknowledged after {delay_minutes} minutes. Original: {alert.description}",
                severity=AlertSeverity.CRITICAL,
                category=alert.category,
                timestamp=datetime.now(UTC),
                source=f"escalation-{alert.source}",
                metadata={**alert.metadata, "escalated_from": alert.id},
                escalated=True,
            )

            await self.trigger_alert(escalated_alert)
