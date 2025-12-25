"""Metrics endpoints for Prometheus-style monitoring.

LOW-007: Metrics collection and export endpoints.
"""

from fastapi import APIRouter, Depends, Response
from typing import Annotated

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.infrastructure.monitoring.metrics import get_metrics_registry
from app.infrastructure.monitoring.log_aggregator import (
    get_log_aggregator,
    get_retention_policy,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/prometheus")
async def prometheus_metrics():
    """Export metrics in Prometheus format (no auth required for scraping).

    Returns:
        Plain text metrics in Prometheus exposition format
    """
    registry = get_metrics_registry()
    all_metrics = registry.get_all_metrics()

    lines = []

    for name, metric in all_metrics.items():
        # Add HELP and TYPE
        lines.append(f"# HELP {name} {metric['description']}")
        lines.append(f"# TYPE {name} {metric['type']}")

        # Add value(s)
        if metric["type"] in ["counter", "gauge"]:
            lines.append(f"{name} {metric['value']}")

        elif metric["type"] == "histogram":
            # Export histogram buckets
            for bucket, count in metric.get("buckets", {}).items():
                lines.append(f'{name}_bucket{{le="{bucket}"}} {count}')
            lines.append(f'{name}_bucket{{le="+Inf"}} {metric["count"]}')
            lines.append(f"{name}_sum {metric['sum']}")
            lines.append(f"{name}_count {metric['count']}")

        elif metric["type"] == "summary":
            # Export summary quantiles
            for quantile, value in metric.get("quantiles", {}).items():
                lines.append(f'{name}{{quantile="{quantile}"}} {value}')
            lines.append(f"{name}_sum {metric['sum']}")
            lines.append(f"{name}_count {metric['count']}")

        lines.append("")  # Empty line between metrics

    return Response(content="\n".join(lines), media_type="text/plain")


@router.get("/json")
async def json_metrics(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get all metrics in JSON format (requires auth).

    Returns:
        JSON with all metrics
    """
    # Only admins can access
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    registry = get_metrics_registry()
    all_metrics = registry.get_all_metrics()

    return {
        "status": "success",
        "data": all_metrics,
        "timestamp": None,  # Will be added by middleware
    }


@router.get("/logs/errors")
async def get_error_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    days: int = 7,
):
    """Get aggregated error statistics from logs.

    Args:
        days: Number of days to analyze

    Returns:
        Error statistics
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    aggregator = get_log_aggregator()
    stats = aggregator.aggregate_errors(days=days)

    return {
        "status": "success",
        "data": stats,
    }


@router.get("/logs/performance")
async def get_performance_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    days: int = 1,
):
    """Get request performance statistics from logs.

    Args:
        days: Number of days to analyze

    Returns:
        Performance statistics
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    aggregator = get_log_aggregator()
    stats = aggregator.analyze_request_performance(days=days)

    return {
        "status": "success",
        "data": stats,
    }


@router.get("/logs/retention")
async def get_log_retention_stats(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get log retention statistics.

    Returns:
        Retention statistics
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    retention = get_retention_policy()
    stats = retention.get_retention_stats()

    return {
        "status": "success",
        "data": stats,
    }


@router.post("/logs/compress")
async def compress_old_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    days_old: int = 7,
):
    """Compress logs older than specified days.

    Args:
        days_old: Age threshold for compression

    Returns:
        Number of files compressed
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    retention = get_retention_policy()
    count = retention.compress_old_logs(days_old=days_old)

    return {
        "status": "success",
        "message": f"Compressed {count} log files",
        "files_compressed": count,
    }
