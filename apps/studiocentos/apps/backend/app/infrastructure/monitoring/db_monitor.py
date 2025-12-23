"""Database Connection Pool Monitor
P1: Database Connection Pooling Implementation.
"""

from typing import Any

from sqlalchemy.engine import Engine

from app.infrastructure.monitoring.logging import get_logger

logger = get_logger("database.monitor")

class DatabaseMonitor:
    """Monitor database connection pool health and metrics."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def get_pool_status(self) -> dict[str, Any]:
        """Get current connection pool status."""
        pool = self.engine.pool

        status = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": getattr(pool, "invalidated", lambda: 0)(),
        }

        # Calculate utilization percentage
        total_capacity = status["pool_size"] + status["overflow"]
        active_connections = status["checked_out"]
        status["utilization_percent"] = (
            (active_connections / total_capacity * 100) if total_capacity > 0 else 0
        )

        return status

    def log_pool_metrics(self):
        """Log current pool metrics for monitoring."""
        status = self.get_pool_status()

        logger.info(
            "Database pool metrics",
            extra={
                "event_type": "db_pool_metrics",
                "pool_size": status["pool_size"],
                "checked_in": status["checked_in"],
                "checked_out": status["checked_out"],
                "overflow": status["overflow"],
                "invalid": status["invalid"],
                "utilization_percent": round(status["utilization_percent"], 2),
            },
        )

        # Log warnings for high utilization
        if status["utilization_percent"] > 80:
            logger.warning(
                "High database pool utilization detected",
                extra={
                    "event_type": "db_pool_high_utilization",
                    "utilization_percent": status["utilization_percent"],
                    "recommendation": "Consider increasing pool_size or max_overflow",
                },
            )

    def health_check(self) -> dict[str, Any]:
        """Perform database health check."""
        try:
            from sqlalchemy import text

            # Test basic connectivity
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as health_check"))
                health_value = result.scalar()

            # Get pool status
            pool_status = self.get_pool_status()

            return {
                "status": "healthy",
                "connectivity": "ok",
                "health_check_value": health_value,
                "pool_metrics": pool_status,
                "recommendations": self._get_recommendations(pool_status),
            }

        except Exception as e:
            logger.error(
                "Database health check failed",
                extra={"event_type": "db_health_check_failed", "error": str(e)},
                exc_info=True,
            )

            return {
                "status": "unhealthy",
                "connectivity": "failed",
                "error": str(e),
                "pool_metrics": self.get_pool_status(),
            }

    def _get_recommendations(self, status: dict[str, Any]) -> list:
        """Generate recommendations based on pool status."""
        recommendations = []

        if status["utilization_percent"] > 90:
            recommendations.append(
                "Critical: Pool utilization > 90%. Increase pool size immediately."
            )
        elif status["utilization_percent"] > 80:
            recommendations.append(
                "Warning: Pool utilization > 80%. Consider increasing pool size."
            )

        if status["invalid"] > 0:
            recommendations.append(
                f"Warning: {status['invalid']} invalid connections detected. Check network stability."
            )

        if status["overflow"] > status["pool_size"] * 0.5:
            recommendations.append("High overflow usage. Consider increasing base pool_size.")

        if not recommendations:
            recommendations.append("Pool operating within normal parameters.")

        return recommendations

def create_db_monitor(engine: Engine) -> DatabaseMonitor:
    """Factory function to create database monitor."""
    return DatabaseMonitor(engine)
