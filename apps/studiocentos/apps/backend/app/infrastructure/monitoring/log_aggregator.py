"""Log Aggregation and Analysis Tools.

LOW-008: Log aggregation, search, and retention policy.
"""

import gzip
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from collections import defaultdict
import shutil

logger = logging.getLogger(__name__)


class LogAggregator:
    """Aggregate and analyze structured log files."""

    def __init__(self, log_directory: str = "logs"):
        """Initialize log aggregator.

        Args:
            log_directory: Directory containing log files
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

    def parse_log_file(self, file_path: Path) -> list[dict]:
        """Parse JSON log file.

        Args:
            file_path: Path to log file

        Returns:
            List of parsed log entries
        """
        logs = []

        try:
            # Handle gzipped files
            if file_path.suffix == ".gz":
                with gzip.open(file_path, "rt") as f:
                    for line in f:
                        try:
                            logs.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            else:
                with open(file_path, "r") as f:
                    for line in f:
                        try:
                            logs.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Failed to parse log file {file_path}: {e}")

        return logs

    def search_logs(
        self,
        level: Optional[str] = None,
        service: Optional[str] = None,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Search logs with filters.

        Args:
            level: Log level filter (INFO, WARNING, ERROR)
            service: Service name filter
            user_id: User ID filter
            request_id: Request ID filter
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of results

        Returns:
            List of matching log entries
        """
        results = []

        # Scan all log files
        for log_file in sorted(self.log_directory.glob("*.log*")):
            logs = self.parse_log_file(log_file)

            for log_entry in logs:
                # Apply filters
                if level and log_entry.get("level") != level:
                    continue

                if service and log_entry.get("service") != service:
                    continue

                if user_id and log_entry.get("user_id") != user_id:
                    continue

                if request_id and log_entry.get("request_id") != request_id:
                    continue

                # Time range filter
                if start_time or end_time:
                    log_time = datetime.fromisoformat(log_entry.get("timestamp", ""))
                    if start_time and log_time < start_time:
                        continue
                    if end_time and log_time > end_time:
                        continue

                results.append(log_entry)

                if len(results) >= limit:
                    return results

        return results

    def aggregate_errors(
        self, days: int = 7
    ) -> dict[str, dict[str, Any]]:
        """Aggregate error statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with error statistics
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        error_counts = defaultdict(int)
        error_examples = defaultdict(list)

        for log_file in sorted(self.log_directory.glob("*.log*")):
            logs = self.parse_log_file(log_file)

            for log_entry in logs:
                # Only process errors and warnings
                if log_entry.get("level") not in ["ERROR", "WARNING"]:
                    continue

                # Check time range
                log_time = datetime.fromisoformat(log_entry.get("timestamp", ""))
                if log_time < cutoff_time:
                    continue

                # Aggregate by logger and message
                key = f"{log_entry.get('logger')}:{log_entry.get('message')[:100]}"
                error_counts[key] += 1

                # Store first 3 examples
                if len(error_examples[key]) < 3:
                    error_examples[key].append(
                        {
                            "timestamp": log_entry.get("timestamp"),
                            "level": log_entry.get("level"),
                            "message": log_entry.get("message"),
                            "file": log_entry.get("file"),
                        }
                    )

        # Format results
        return {
            "period_days": days,
            "total_errors": sum(error_counts.values()),
            "unique_errors": len(error_counts),
            "top_errors": [
                {
                    "key": key,
                    "count": count,
                    "examples": error_examples[key],
                }
                for key, count in sorted(
                    error_counts.items(), key=lambda x: x[1], reverse=True
                )[:20]
            ],
        }

    def analyze_request_performance(
        self, days: int = 1
    ) -> dict[str, Any]:
        """Analyze request performance from logs.

        Args:
            days: Number of days to analyze

        Returns:
            Performance statistics
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        request_times = defaultdict(list)

        for log_file in sorted(self.log_directory.glob("*.log*")):
            logs = self.parse_log_file(log_file)

            for log_entry in logs:
                # Look for request timing events
                extra = log_entry.get("extra", {})
                if extra.get("event_type") != "request_timing":
                    continue

                # Check time range
                log_time = datetime.fromisoformat(log_entry.get("timestamp", ""))
                if log_time < cutoff_time:
                    continue

                # Aggregate by endpoint
                path = extra.get("http_path", "unknown")
                duration = extra.get("duration_ms", 0)
                request_times[path].append(duration)

        # Calculate statistics
        stats = {}
        for path, durations in request_times.items():
            if not durations:
                continue

            sorted_durations = sorted(durations)
            count = len(durations)

            stats[path] = {
                "count": count,
                "avg_ms": sum(durations) / count,
                "min_ms": min(durations),
                "max_ms": max(durations),
                "p50_ms": sorted_durations[count // 2],
                "p95_ms": sorted_durations[int(count * 0.95)] if count > 20 else max(durations),
                "p99_ms": sorted_durations[int(count * 0.99)] if count > 100 else max(durations),
            }

        return {
            "period_days": days,
            "total_requests": sum(len(d) for d in request_times.values()),
            "endpoints": stats,
        }


class LogRetentionPolicy:
    """Manage log file retention and compression."""

    def __init__(self, log_directory: str = "logs"):
        """Initialize retention policy.

        Args:
            log_directory: Directory containing log files
        """
        self.log_directory = Path(log_directory)

    def compress_old_logs(self, days_old: int = 7):
        """Compress log files older than specified days.

        Args:
            days_old: Age threshold for compression

        Returns:
            Number of files compressed
        """
        cutoff_time = datetime.now() - timedelta(days=days_old)
        compressed_count = 0

        for log_file in self.log_directory.glob("*.log"):
            # Skip already compressed files
            if log_file.suffix == ".gz":
                continue

            # Check file modification time
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_time:
                try:
                    # Compress file
                    gz_path = log_file.with_suffix(log_file.suffix + ".gz")
                    with open(log_file, "rb") as f_in:
                        with gzip.open(gz_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # Remove original
                    log_file.unlink()
                    compressed_count += 1

                    logger.info(f"Compressed log file: {log_file.name}")

                except Exception as e:
                    logger.error(f"Failed to compress {log_file}: {e}")

        return compressed_count

    def delete_old_logs(self, days_old: int = 90):
        """Delete log files older than specified days.

        Args:
            days_old: Age threshold for deletion

        Returns:
            Number of files deleted
        """
        cutoff_time = datetime.now() - timedelta(days=days_old)
        deleted_count = 0

        for log_file in self.log_directory.glob("*.log*"):
            # Check file modification time
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_time:
                try:
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old log file: {log_file.name}")

                except Exception as e:
                    logger.error(f"Failed to delete {log_file}: {e}")

        return deleted_count

    def get_retention_stats(self) -> dict[str, Any]:
        """Get statistics about log retention.

        Returns:
            Retention statistics
        """
        total_size = 0
        file_count = 0
        compressed_count = 0
        oldest_file = None

        for log_file in self.log_directory.glob("*.log*"):
            file_count += 1
            total_size += log_file.stat().st_size

            if log_file.suffix == ".gz":
                compressed_count += 1

            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if oldest_file is None or mtime < oldest_file:
                oldest_file = mtime

        return {
            "total_files": file_count,
            "compressed_files": compressed_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_file_days": (
                (datetime.now() - oldest_file).days if oldest_file else 0
            ),
        }


# Export utilities
def get_log_aggregator(log_dir: str = "logs") -> LogAggregator:
    """Get log aggregator instance."""
    return LogAggregator(log_dir)


def get_retention_policy(log_dir: str = "logs") -> LogRetentionPolicy:
    """Get retention policy instance."""
    return LogRetentionPolicy(log_dir)
