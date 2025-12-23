"""
Centralized Logging Service for IronRep Backend.

Provides structured logging with:
- Environment-aware configuration (dev vs prod)
- Multiple handlers (console, file, Sentry optional)
- Structured formatters
- Context injection
"""
import logging
import sys
from pathlib import Path
from typing import Optional
import os


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output in development."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_sentry: bool = False
) -> None:
    """
    Setup centralized logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_sentry: Enable Sentry integration for error tracking
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Use colored formatter in development, structured in production
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_format = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # File Handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)

    # Sentry Handler (optional, for error tracking in production)
    if enable_sentry:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=os.getenv("SENTRY_DSN"),
                environment=env,
                traces_sample_rate=0.1,
            )
            root_logger.info("Sentry error tracking enabled")
        except ImportError:
            root_logger.warning("Sentry SDK not installed, skipping Sentry integration")

    root_logger.info(f"Logging initialized at {level} level")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Usage:
        from src.infrastructure.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Message")
        logger.error("Error occurred", exc_info=True)

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Logging should be setup explicitly in main.py entry point
pass
