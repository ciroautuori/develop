# 📊 CV-LAB ENTERPRISE MONITORING SYSTEM
# Advanced monitoring, alerting and performance analytics

import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import psutil
import redis
from fastapi import Request, Response
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.auth.models import User
from app.infrastructure.database import engine

# Configure monitoring logger
monitor_logger = logging.getLogger("cv_lab_monitoring")
handler = logging.FileHandler("logs/monitoring.log")
formatter = logging.Formatter("%(asctime)s - MONITOR - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
monitor_logger.addHandler(handler)
monitor_logger.setLevel(logging.INFO)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    component: str
    metric_name: str
    current_value: float
    threshold: float
    resolved: bool = False
    resolved_at: datetime | None = None

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: dict[str, str]

@dataclass
class SystemHealth:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    response_time_avg: float
    error_rate: float
    uptime_seconds: float
    timestamp: datetime

class CVLabMonitoring:
    """Enterprise monitoring system for CV-Lab."""

    def __init__(self):
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()

        # Internal metrics storage
        self.metrics_history: deque = deque(maxlen=10000)
        self.alerts: list[Alert] = []
        self.performance_history: deque = deque(maxlen=1000)

        # Monitoring state
        self.start_time = datetime.now(UTC)
        self.is_monitoring = False
        self.alert_handlers: list[Callable] = []

        # Thresholds
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 2000.0,  # ms
            "error_rate": 5.0,  # %
            "db_connections": 50,
        }

        # Request tracking
        self.request_times: deque = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})

        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
            )
        except:
            self.redis_client = None
            monitor_logger.warning("Redis not available for monitoring")

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        self.http_requests_total = Counter(
            "cv_lab_http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.http_request_duration = Histogram(
            "cv_lab_http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"],
            registry=self.registry,
        )

        self.active_users = Gauge(
            "cv_lab_active_users", "Number of active users", registry=self.registry
        )

        self.database_connections = Gauge(
            "cv_lab_database_connections", "Active database connections", registry=self.registry
        )

        self.system_cpu_usage = Gauge(
            "cv_lab_system_cpu_usage_percent", "System CPU usage percentage", registry=self.registry
        )

        self.system_memory_usage = Gauge(
            "cv_lab_system_memory_usage_percent",
            "System memory usage percentage",
            registry=self.registry,
        )

        self.system_disk_usage = Gauge(
            "cv_lab_system_disk_usage_percent",
            "System disk usage percentage",
            registry=self.registry,
        )

        self.api_errors = Counter(
            "cv_lab_api_errors_total",
            "Total API errors",
            ["endpoint", "error_type"],
            registry=self.registry,
        )

    # === MIDDLEWARE INTEGRATION ===

    @asynccontextmanager
    async def track_request(self, request: Request):
        """Context manager to track request performance."""
        start_time = time.time()
        endpoint = request.url.path
        method = request.method

        try:
            yield

            # Track successful request
            duration = time.time() - start_time
            self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
            self.request_times.append(duration * 1000)  # Convert to ms

            self.endpoint_stats[endpoint]["count"] += 1
            self.endpoint_stats[endpoint]["total_time"] += duration

        except Exception as e:
            # Track error
            duration = time.time() - start_time
            self.api_errors.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
            self.endpoint_stats[endpoint]["errors"] += 1

            monitor_logger.error(f"Request error - {method} {endpoint}: {e!s}")
            raise

    def record_request(self, request: Request, response: Response, duration: float):
        """Record request metrics."""
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code

        # Update Prometheus metrics
        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

        # Track for internal analytics
        self.request_times.append(duration * 1000)

        # Update endpoint statistics
        self.endpoint_stats[endpoint]["count"] += 1
        self.endpoint_stats[endpoint]["total_time"] += duration

        if status_code >= 400:
            self.endpoint_stats[endpoint]["errors"] += 1
            self.error_counts[f"{status_code}"] += 1

    # === SYSTEM MONITORING ===

    def collect_system_metrics(self) -> SystemHealth:
        """Collect current system health metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk usage
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent

        # Database connections
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT count(*) FROM pg_stat_activity"))
                active_connections = result.scalar()
        except:
            active_connections = 0

        # Calculate average response time
        recent_times = list(self.request_times)[-100:]
        response_time_avg = sum(recent_times) / len(recent_times) if recent_times else 0

        # Calculate error rate
        total_requests = sum(stats["count"] for stats in self.endpoint_stats.values())
        total_errors = sum(stats["errors"] for stats in self.endpoint_stats.values())
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0

        # System uptime
        uptime_seconds = (datetime.now(UTC) - self.start_time).total_seconds()

        health = SystemHealth(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            active_connections=active_connections,
            response_time_avg=response_time_avg,
            error_rate=error_rate,
            uptime_seconds=uptime_seconds,
            timestamp=datetime.now(UTC),
        )

        # Update Prometheus metrics
        self.system_cpu_usage.set(cpu_percent)
        self.system_memory_usage.set(memory_percent)
        self.system_disk_usage.set(disk_percent)
        self.database_connections.set(active_connections)

        # Store in history
        self.performance_history.append(health)

        # Check thresholds and create alerts
        self._check_thresholds(health)

        return health

    def _check_thresholds(self, health: SystemHealth):
        """Check if any thresholds are exceeded."""
        checks = [
            ("cpu_usage", health.cpu_percent, "CPU usage"),
            ("memory_usage", health.memory_percent, "Memory usage"),
            ("disk_usage", health.disk_percent, "Disk usage"),
            ("response_time", health.response_time_avg, "Response time"),
            ("error_rate", health.error_rate, "Error rate"),
            ("db_connections", health.active_connections, "Database connections"),
        ]

        for metric_name, current_value, display_name in checks:
            threshold = self.thresholds.get(metric_name, 100)

            if current_value > threshold:
                self._create_alert(
                    level=(
                        AlertLevel.WARNING if current_value < threshold * 1.2 else AlertLevel.ERROR
                    ),
                    title=f"High {display_name}",
                    message=f"{display_name} is {current_value:.2f}, exceeding threshold of {threshold}",
                    component="system",
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold=threshold,
                )

    # === DATABASE MONITORING ===

    def get_database_stats(self) -> dict[str, Any]:
        """Get detailed database statistics."""
        try:
            with engine.connect() as conn:
                # Active connections
                connections_result = conn.execute(
                    text(
                        """
                    SELECT count(*) as total,
                           count(*) FILTER (WHERE state = 'active') as active,
                           count(*) FILTER (WHERE state = 'idle') as idle
                    FROM pg_stat_activity
                """
                    )
                )
                connections = connections_result.fetchone()

                # Database size
                size_result = conn.execute(
                    text(
                        """
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size
                """
                    )
                )
                db_size = size_result.scalar()

                # Slow queries (if enabled)
                slow_queries_result = conn.execute(
                    text(
                        """
                    SELECT count(*) FROM pg_stat_statements
                    WHERE mean_exec_time > 1000
                """
                    )
                )
                slow_queries = slow_queries_result.scalar() or 0

                # Table statistics
                table_stats_result = conn.execute(
                    text(
                        """
                    SELECT schemaname, relname as tablename, n_tup_ins, n_tup_upd, n_tup_del
                    FROM pg_stat_user_tables
                    ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC
                    LIMIT 10
                """
                    )
                )
                table_stats = [dict(row._mapping) for row in table_stats_result.fetchall()]

                return {
                    "connections": {
                        "total": connections.total,
                        "active": connections.active,
                        "idle": connections.idle,
                    },
                    "database_size": db_size,
                    "slow_queries_count": slow_queries,
                    "top_tables": table_stats,
                    "timestamp": datetime.now(UTC).isoformat(),
                }

        except Exception as e:
            monitor_logger.error(f"Database stats collection failed: {e}")
            return {"error": str(e)}

    # === APPLICATION METRICS ===

    def get_application_metrics(self, db: Session) -> dict[str, Any]:
        """Get application-specific metrics."""
        try:
            # User statistics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active).count()

            # Recent activity (last 24 hours)
            yesterday = datetime.now(UTC) - timedelta(days=1)
            recent_users = db.query(User).filter(User.created_at >= yesterday).count()

            # Update Prometheus gauge
            self.active_users.set(active_users)

            # API endpoint performance
            endpoint_performance = {}
            for endpoint, stats in self.endpoint_stats.items():
                if stats["count"] > 0:
                    avg_response_time = (stats["total_time"] / stats["count"]) * 1000
                    error_rate = (stats["errors"] / stats["count"]) * 100

                    endpoint_performance[endpoint] = {
                        "request_count": stats["count"],
                        "avg_response_time_ms": round(avg_response_time, 2),
                        "error_rate_percent": round(error_rate, 2),
                        "total_errors": stats["errors"],
                    }

            return {
                "users": {"total": total_users, "active": active_users, "new_today": recent_users},
                "api_performance": endpoint_performance,
                "system_uptime_hours": round(
                    (datetime.now(UTC) - self.start_time).total_seconds() / 3600, 2
                ),
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            monitor_logger.error(f"Application metrics collection failed: {e}")
            return {"error": str(e)}

    # === ALERTING SYSTEM ===

    def _create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        component: str,
        metric_name: str,
        current_value: float,
        threshold: float,
    ):
        """Create and process alert."""
        alert_id = f"{component}_{metric_name}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(UTC),
            component=component,
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold,
        )

        # Check if similar alert already exists and is not resolved
        existing_alert = None
        for existing in self.alerts:
            if (
                existing.component == component
                and existing.metric_name == metric_name
                and not existing.resolved
            ):
                existing_alert = existing
                break

        if not existing_alert:
            self.alerts.append(alert)
            monitor_logger.warning(f"Alert created: {title} - {message}")

            # Trigger alert handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    monitor_logger.error(f"Alert handler failed: {e}")

        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now(UTC)
                monitor_logger.info(f"Alert resolved: {alert.title}")
                return True
        return False

    def get_active_alerts(self) -> list[Alert]:
        """Get all active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]

    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add alert handler function."""
        self.alert_handlers.append(handler)

    # === REPORTING ===

    def generate_health_report(self, db: Session) -> dict[str, Any]:
        """Generate comprehensive health report."""
        current_health = self.collect_system_metrics()
        app_metrics = self.get_application_metrics(db)
        db_stats = self.get_database_stats()

        # Calculate health score
        health_factors = {
            "cpu": max(0, 100 - current_health.cpu_percent),
            "memory": max(0, 100 - current_health.memory_percent),
            "disk": max(0, 100 - current_health.disk_percent),
            "response_time": max(0, 100 - (current_health.response_time_avg / 10)),
            "error_rate": max(0, 100 - (current_health.error_rate * 10)),
        }

        overall_health = sum(health_factors.values()) / len(health_factors)

        return {
            "overall_health_score": round(overall_health, 2),
            "health_grade": self._get_health_grade(overall_health),
            "system_metrics": asdict(current_health),
            "application_metrics": app_metrics,
            "database_stats": db_stats,
            "active_alerts": [asdict(alert) for alert in self.get_active_alerts()],
            "performance_trends": self._get_performance_trends(),
            "recommendations": self._generate_recommendations(current_health),
            "report_timestamp": datetime.now(UTC).isoformat(),
        }

    def _get_health_grade(self, score: float) -> str:
        """Convert health score to grade."""
        if score >= 90:
            return "Excellent"
        if score >= 80:
            return "Good"
        if score >= 70:
            return "Fair"
        if score >= 60:
            return "Poor"
        return "Critical"

    def _get_performance_trends(self) -> dict[str, Any]:
        """Analyze performance trends."""
        if len(self.performance_history) < 10:
            return {"status": "insufficient_data"}

        recent = list(self.performance_history)[-10:]
        older = (
            list(self.performance_history)[-20:-10] if len(self.performance_history) >= 20 else []
        )

        if not older:
            return {"status": "insufficient_historical_data"}

        # Calculate trends
        cpu_trend = sum(h.cpu_percent for h in recent) / len(recent) - sum(
            h.cpu_percent for h in older
        ) / len(older)
        memory_trend = sum(h.memory_percent for h in recent) / len(recent) - sum(
            h.memory_percent for h in older
        ) / len(older)
        response_time_trend = sum(h.response_time_avg for h in recent) / len(recent) - sum(
            h.response_time_avg for h in older
        ) / len(older)

        return {
            "cpu_trend": round(cpu_trend, 2),
            "memory_trend": round(memory_trend, 2),
            "response_time_trend": round(response_time_trend, 2),
            "analysis_period_minutes": 20,
        }

    def _generate_recommendations(self, health: SystemHealth) -> list[str]:
        """Generate performance recommendations."""
        recommendations = []

        if health.cpu_percent > 70:
            recommendations.append("Consider CPU optimization or scaling")

        if health.memory_percent > 80:
            recommendations.append("Monitor memory usage and consider increasing RAM")

        if health.response_time_avg > 1000:
            recommendations.append("Investigate slow API endpoints")

        if health.error_rate > 2:
            recommendations.append("Review error logs and fix failing endpoints")

        if health.active_connections > 30:
            recommendations.append("Optimize database connection pooling")

        if not recommendations:
            recommendations.append("System performance is optimal")

        return recommendations

    # === PROMETHEUS INTEGRATION ===

    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode("utf-8")

    # === MONITORING LIFECYCLE ===

    def start_monitoring(self):
        """Start continuous monitoring."""
        self.is_monitoring = True
        monitor_logger.info("CV-Lab monitoring started")

        # Start background monitoring thread
        def monitoring_loop():
            while self.is_monitoring:
                try:
                    # Collect metrics every 60 seconds
                    self.collect_system_metrics()
                    time.sleep(60)
                except Exception as e:
                    monitor_logger.error(f"Monitoring loop error: {e}")
                    time.sleep(30)

        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()

    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_monitoring = False
        monitor_logger.info("CV-Lab monitoring stopped")

# Global monitoring instance
cv_lab_monitor = CVLabMonitoring()

# Alert handlers
def slack_alert_handler(alert: Alert):
    """Send alert to Slack (placeholder)."""
    # In production, implement actual Slack integration
    monitor_logger.info(f"SLACK ALERT: {alert.title} - {alert.message}")

def email_alert_handler(alert: Alert):
    """Send alert via email (placeholder)."""
    # In production, implement actual email integration
    monitor_logger.info(f"EMAIL ALERT: {alert.title} - {alert.message}")

# Register alert handlers
cv_lab_monitor.add_alert_handler(slack_alert_handler)
cv_lab_monitor.add_alert_handler(email_alert_handler)
