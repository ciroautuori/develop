"""Enterprise Alerting & Incident Response System
Sistema completo di monitoraggio e alerting per CV-Lab SaaS production.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Livelli di severità alert."""

    CRITICAL = "critical"  # Impatto revenue/sicurezza immediato
    HIGH = "high"  # Degrado performance significativo
    MEDIUM = "medium"  # Issue che richiedono attenzione
    LOW = "low"  # Informational
    INFO = "info"  # Metriche normali

class AlertCategory(str, Enum):
    """Categorie di alert."""

    PAYMENT = "payment"  # Payment failures
    SECURITY = "security"  # Security breaches
    PERFORMANCE = "performance"  # Performance degradation
    UPTIME = "uptime"  # Service availability
    BUSINESS = "business"  # Business metrics
    INFRASTRUCTURE = "infrastructure"  # System health

@dataclass
class Alert:
    """Model per alert enterprise."""

    id: str
    title: str
    description: str
    severity: AlertSeverity
    category: AlertCategory
    timestamp: datetime
    source: str
    metadata: dict[str, Any]
    resolved: bool = False
    resolved_at: datetime | None = None
    escalated: bool = False
    acknowledged: bool = False
    acknowledged_by: str | None = None

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
            from app.infrastructure.database import get_async_session
            from app.infrastructure.monitoring.models import (
                AlertCategoryEnum,
                AlertLog,
                AlertSeverityEnum,
            )

            # Map dataclass enums to SQLAlchemy enums
            severity_map = {
                "info": AlertSeverityEnum.INFO,
                "warning": AlertSeverityEnum.WARNING,
                "error": AlertSeverityEnum.ERROR,
                "critical": AlertSeverityEnum.CRITICAL,
            }

            category_map = {
                "payment": AlertCategoryEnum.PAYMENT,
                "security": AlertCategoryEnum.SECURITY,
                "performance": AlertCategoryEnum.PERFORMANCE,
                "availability": AlertCategoryEnum.AVAILABILITY,
                "resource": AlertCategoryEnum.RESOURCE,
            }

            async with get_async_session() as db:
                alert_log = AlertLog(
                    alert_id=alert.id,
                    title=alert.title,
                    description=alert.description,
                    severity=severity_map.get(alert.severity.value.lower(), AlertSeverityEnum.INFO),
                    category=category_map.get(alert.category.value.lower(), AlertCategoryEnum.AVAILABILITY),
                    source=alert.source,
                    resolved=alert.resolved,
                    acknowledged=alert.acknowledged,
                    escalated=alert.escalated,
                    metadata=alert.metadata,
                    timestamp=alert.timestamp,
                )

                db.add(alert_log)
                await db.commit()

                logger.info(f"Alert persisted to database: {alert.id}")

        except Exception as e:
            # Fallback to logging if database fails
            logger.error(f"Failed to persist alert to database: {e}")
            alert_data = asdict(alert)
            alert_data["timestamp"] = alert.timestamp.isoformat()
            logger.info(f"ALERT_PERSIST_FALLBACK: {json.dumps(alert_data)}")

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

class PaymentAlertMonitor:
    """Monitor payment-related metrics and trigger alerts."""

    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager

    async def check_payment_failures(self, db: AsyncSession) -> Alert | None:
        """Check for payment failure rate spikes."""
        try:
            from sqlalchemy import func, select

            from app.domain.billing.models import Payment

            # Query payment failures in last hour
            one_hour_ago = datetime.now(UTC) - timedelta(hours=1)

            # Query actual payment data
            total_result = await db.execute(
                select(func.count(Payment.id)).where(Payment.created_at >= one_hour_ago)
            )
            total_payments = total_result.scalar() or 0

            failed_result = await db.execute(
                select(func.count(Payment.id)).where(
                    Payment.created_at >= one_hour_ago,
                    Payment.status == "failed"
                )
            )
            failed_payments = failed_result.scalar() or 0

            if total_payments > 10:  # Only alert if meaningful volume
                failure_rate = failed_payments / total_payments

                if failure_rate > self.alert_manager.alert_thresholds["payment_failure_rate"]:
                    return Alert(
                        id=f"payment-failure-{int(datetime.now(UTC).timestamp())}",
                        title="High Payment Failure Rate Detected",
                        description=f"Payment failure rate is {failure_rate:.2%} ({failed_payments}/{total_payments}) in the last hour. Threshold: {self.alert_manager.alert_thresholds['payment_failure_rate']:.1%}",
                        severity=AlertSeverity.CRITICAL,
                        category=AlertCategory.PAYMENT,
                        timestamp=datetime.now(UTC),
                        source="payment-monitor",
                        metadata={
                            "failure_rate": failure_rate,
                            "failed_count": failed_payments,
                            "total_count": total_payments,
                            "threshold": self.alert_manager.alert_thresholds[
                                "payment_failure_rate"
                            ],
                        },
                    )

        except Exception as e:
            logger.error(f"Error checking payment failures: {e}")

        return None

    async def check_revenue_loss(self, db: AsyncSession) -> Alert | None:
        """Check for significant revenue loss due to payment failures."""
        try:
            from sqlalchemy import func, select

            from app.domain.billing.models import Payment

            # Query failed payments in last 24 hours
            twenty_four_hours_ago = datetime.now(UTC) - timedelta(hours=24)

            # Calculate actual revenue loss
            result = await db.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.created_at >= twenty_four_hours_ago,
                    Payment.status == "failed"
                )
            )

            revenue_loss = float(result.scalar() or 0)

            if revenue_loss > self.alert_manager.alert_thresholds["payment_amount_loss"]:
                return Alert(
                    id=f"revenue-loss-{int(datetime.now(UTC).timestamp())}",
                    title="Significant Revenue Loss Detected",
                    description=f"Revenue loss from payment failures: €{revenue_loss:.2f} in the last hour. Threshold: €{self.alert_manager.alert_thresholds['payment_amount_loss']:.2f}",
                    severity=AlertSeverity.CRITICAL,
                    category=AlertCategory.PAYMENT,
                    timestamp=datetime.now(UTC),
                    source="revenue-monitor",
                    metadata={
                        "revenue_loss": revenue_loss,
                        "threshold": self.alert_manager.alert_thresholds["payment_amount_loss"],
                        "currency": "EUR",
                    },
                )

        except Exception as e:
            logger.error(f"Error checking revenue loss: {e}")

        return None

class SecurityAlertMonitor:
    """Monitor security-related events and trigger alerts."""

    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager

    async def check_suspicious_login_attempts(self, db: AsyncSession) -> Alert | None:
        """Check for suspicious login attempt patterns."""
        try:
            from sqlalchemy import func, select

            from app.domain.gdpr.models import AuditActionEnum, DataAuditLog

            # Query actual failed login attempts from audit logs
            one_minute_ago = datetime.now(UTC) - timedelta(minutes=1)

            result = await db.execute(
                select(func.count(DataAuditLog.id)).where(
                    DataAuditLog.timestamp >= one_minute_ago,
                    DataAuditLog.action == AuditActionEnum.LOGIN,
                    DataAuditLog.response_status.in_([401, 403])  # Failed logins
                )
            )

            failed_attempts_last_minute = result.scalar() or 0

            if (
                failed_attempts_last_minute
                > self.alert_manager.alert_thresholds["failed_login_attempts"]
            ):
                return Alert(
                    id=f"suspicious-login-{int(datetime.now(UTC).timestamp())}",
                    title="Suspicious Login Activity Detected",
                    description=f"High number of failed login attempts: {failed_attempts_last_minute} in the last minute. Possible brute force attack.",
                    severity=AlertSeverity.HIGH,
                    category=AlertCategory.SECURITY,
                    timestamp=datetime.now(UTC),
                    source="security-monitor",
                    metadata={
                        "failed_attempts": failed_attempts_last_minute,
                        "threshold": self.alert_manager.alert_thresholds["failed_login_attempts"],
                        "time_window": "1_minute",
                    },
                )

        except Exception as e:
            logger.error(f"Error checking login attempts: {e}")

        return None

    async def check_rate_limit_violations(self, db: AsyncSession) -> Alert | None:
        """Check for rate limiting violations indicating attacks."""
        try:
            from sqlalchemy import func, select

            from app.domain.gdpr.models import DataAuditLog

            # Query rate limit violations from audit logs (HTTP 429 responses)
            one_minute_ago = datetime.now(UTC) - timedelta(minutes=1)

            result = await db.execute(
                select(func.count(DataAuditLog.id)).where(
                    DataAuditLog.timestamp >= one_minute_ago,
                    DataAuditLog.response_status == 429  # Rate limited
                )
            )

            violations_per_minute = result.scalar() or 0

            if (
                violations_per_minute
                > self.alert_manager.alert_thresholds["suspicious_ip_requests"]
            ):
                return Alert(
                    id=f"rate-limit-violation-{int(datetime.now(UTC).timestamp())}",
                    title="Rate Limit Violations Detected",
                    description=f"Suspicious request patterns: {violations_per_minute} requests/minute from single IP. Possible DDoS attack.",
                    severity=AlertSeverity.HIGH,
                    category=AlertCategory.SECURITY,
                    timestamp=datetime.now(UTC),
                    source="rate-limit-monitor",
                    metadata={
                        "requests_per_minute": violations_per_minute,
                        "threshold": self.alert_manager.alert_thresholds["suspicious_ip_requests"],
                        "source_ip": "xxx.xxx.xxx.xxx",  # Would contain actual IP
                    },
                )

        except Exception as e:
            logger.error(f"Error checking rate limit violations: {e}")

        return None

class PerformanceAlertMonitor:
    """Monitor performance metrics and trigger alerts."""

    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager

    async def check_api_response_times(self, db: AsyncSession) -> Alert | None:
        """Check for API response time degradation."""
        try:
            from sqlalchemy import func, select

            from app.infrastructure.monitoring.models import MetricLog

            # Query actual API response times from metrics (last 5 minutes)
            five_minutes_ago = datetime.now(UTC) - timedelta(minutes=5)

            result = await db.execute(
                select(func.avg(MetricLog.value)).where(
                    MetricLog.metric_name == "api_response_time",
                    MetricLog.timestamp >= five_minutes_ago
                )
            )

            avg_response_time = result.scalar() or 0

            # If no metrics yet, skip alert (returns 0)
            if avg_response_time == 0:
                return None

            if avg_response_time > self.alert_manager.alert_thresholds["api_response_time"]:
                return Alert(
                    id=f"api-performance-{int(datetime.now(UTC).timestamp())}",
                    title="API Performance Degradation",
                    description=f"API response time degraded: {avg_response_time}ms average (last 5 min). Threshold: {self.alert_manager.alert_thresholds['api_response_time']}ms",
                    severity=AlertSeverity.MEDIUM,
                    category=AlertCategory.PERFORMANCE,
                    timestamp=datetime.now(UTC),
                    source="performance-monitor",
                    metadata={
                        "avg_response_time": avg_response_time,
                        "threshold": self.alert_manager.alert_thresholds["api_response_time"],
                        "time_window": "5_minutes",
                    },
                )

        except Exception as e:
            logger.error(f"Error checking API response times: {e}")

        return None

    async def check_error_rates(self, db: AsyncSession) -> Alert | None:
        """Check for elevated error rates."""
        try:
            from sqlalchemy import func, select

            from app.domain.gdpr.models import DataAuditLog

            # Query actual error rates from audit logs (last 10 minutes)
            ten_minutes_ago = datetime.now(UTC) - timedelta(minutes=10)

            # Total requests
            total_result = await db.execute(
                select(func.count(DataAuditLog.id)).where(
                    DataAuditLog.timestamp >= ten_minutes_ago
                )
            )
            total_requests = total_result.scalar() or 0

            # Error responses (5xx status codes)
            error_result = await db.execute(
                select(func.count(DataAuditLog.id)).where(
                    DataAuditLog.timestamp >= ten_minutes_ago,
                    DataAuditLog.response_status >= 500,
                    DataAuditLog.response_status < 600
                )
            )
            error_requests = error_result.scalar() or 0

            # Calculate error rate
            if total_requests == 0:
                return None

            error_rate = error_requests / total_requests

            if error_rate > self.alert_manager.alert_thresholds["error_rate"]:
                return Alert(
                    id=f"error-rate-{int(datetime.now(UTC).timestamp())}",
                    title="Elevated Error Rate Detected",
                    description=f"Error rate increased: {error_rate:.2%} in the last 10 minutes. Threshold: {self.alert_manager.alert_thresholds['error_rate']:.2%}",
                    severity=AlertSeverity.MEDIUM,
                    category=AlertCategory.PERFORMANCE,
                    timestamp=datetime.now(UTC),
                    source="error-rate-monitor",
                    metadata={
                        "error_rate": error_rate,
                        "threshold": self.alert_manager.alert_thresholds["error_rate"],
                        "time_window": "10_minutes",
                    },
                )

        except Exception as e:
            logger.error(f"Error checking error rates: {e}")

        return None

class UptimeAlertMonitor:
    """Monitor uptime and availability metrics."""

    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager

    async def check_service_availability(self, db: AsyncSession) -> Alert | None:
        """Check service availability and SLA compliance."""
        try:
            from sqlalchemy import func, select

            from app.infrastructure.monitoring.models import MetricLog

            # Calculate actual uptime from health check metrics (last 24 hours)
            twenty_four_hours_ago = datetime.now(UTC) - timedelta(hours=24)

            # Count successful health checks
            success_result = await db.execute(
                select(func.count(MetricLog.id)).where(
                    MetricLog.metric_name == "health_check",
                    MetricLog.timestamp >= twenty_four_hours_ago,
                    MetricLog.value == 1.0  # 1 = healthy, 0 = unhealthy
                )
            )
            successful_checks = success_result.scalar() or 0

            # Count total health checks
            total_result = await db.execute(
                select(func.count(MetricLog.id)).where(
                    MetricLog.metric_name == "health_check",
                    MetricLog.timestamp >= twenty_four_hours_ago
                )
            )
            total_checks = total_result.scalar() or 0

            # Calculate uptime percentage
            if total_checks == 0:
                return None  # No data yet

            current_uptime = (successful_checks / total_checks) * 100

            if current_uptime < self.alert_manager.alert_thresholds["availability_sla"]:
                return Alert(
                    id=f"uptime-sla-{int(datetime.now(UTC).timestamp())}",
                    title="SLA Uptime Threshold Breached",
                    description=f"Service uptime dropped below SLA: {current_uptime:.3f}% (last 24h). SLA target: {self.alert_manager.alert_thresholds['availability_sla']}%",
                    severity=AlertSeverity.CRITICAL,
                    category=AlertCategory.UPTIME,
                    timestamp=datetime.now(UTC),
                    source="uptime-monitor",
                    metadata={
                        "current_uptime": current_uptime,
                        "sla_target": self.alert_manager.alert_thresholds["availability_sla"],
                        "time_window": "24_hours",
                    },
                )

        except Exception as e:
            logger.error(f"Error checking service availability: {e}")

        return None

class AlertingService:
    """Main alerting service orchestrator."""

    def __init__(self):
        self.alert_manager = AlertManager()
        self.payment_monitor = PaymentAlertMonitor(self.alert_manager)
        self.security_monitor = SecurityAlertMonitor(self.alert_manager)
        self.performance_monitor = PerformanceAlertMonitor(self.alert_manager)
        self.uptime_monitor = UptimeAlertMonitor(self.alert_manager)

    async def run_monitoring_cycle(self, db: AsyncSession):
        """Execute complete monitoring cycle for all alert types."""
        alerts_to_trigger = []

        try:
            # Payment monitoring
            payment_alerts = await asyncio.gather(
                self.payment_monitor.check_payment_failures(db),
                self.payment_monitor.check_revenue_loss(db),
                return_exceptions=True,
            )
            alerts_to_trigger.extend([a for a in payment_alerts if isinstance(a, Alert)])

            # Security monitoring
            security_alerts = await asyncio.gather(
                self.security_monitor.check_suspicious_login_attempts(db),
                self.security_monitor.check_rate_limit_violations(db),
                return_exceptions=True,
            )
            alerts_to_trigger.extend([a for a in security_alerts if isinstance(a, Alert)])

            # Performance monitoring
            performance_alerts = await asyncio.gather(
                self.performance_monitor.check_api_response_times(db),
                self.performance_monitor.check_error_rates(db),
                return_exceptions=True,
            )
            alerts_to_trigger.extend([a for a in performance_alerts if isinstance(a, Alert)])

            # Uptime monitoring
            uptime_alert = await self.uptime_monitor.check_service_availability(db)
            if uptime_alert:
                alerts_to_trigger.append(uptime_alert)

            # Trigger all identified alerts
            for alert in alerts_to_trigger:
                await self.alert_manager.trigger_alert(alert)

            logger.info(f"Monitoring cycle complete: {len(alerts_to_trigger)} alerts triggered")

        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")

# Singleton instances
alerting_service = AlertingService()

# Helper functions
async def trigger_payment_failure_alert(failure_rate: float, failed_count: int, total_count: int):
    """Helper per trigger payment failure alert."""
    alert = Alert(
        id=f"payment-failure-{int(datetime.now(UTC).timestamp())}",
        title="Payment Failure Alert",
        description=f"High payment failure rate detected: {failure_rate:.2%}",
        severity=AlertSeverity.CRITICAL,
        category=AlertCategory.PAYMENT,
        timestamp=datetime.now(UTC),
        source="payment-system",
        metadata={
            "failure_rate": failure_rate,
            "failed_count": failed_count,
            "total_count": total_count,
        },
    )
    await alerting_service.alert_manager.trigger_alert(alert)

async def trigger_security_breach_alert(breach_type: str, details: str):
    """Helper per trigger security breach alert."""
    alert = Alert(
        id=f"security-breach-{int(datetime.now(UTC).timestamp())}",
        title=f"Security Breach Detected: {breach_type}",
        description=details,
        severity=AlertSeverity.CRITICAL,
        category=AlertCategory.SECURITY,
        timestamp=datetime.now(UTC),
        source="security-system",
        metadata={"breach_type": breach_type},
    )
    await alerting_service.alert_manager.trigger_alert(alert)
