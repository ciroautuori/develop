"""
Log Scrubber - Remove PII and sensitive data from logs
GDPR/Privacy compliance for CV-Lab SaaS
"""

import re
from typing import Any, Dict, Pattern

class LogScrubber:
    """Scrub sensitive data from log messages for GDPR compliance"""

    # Patterns for sensitive data detection
    PATTERNS: Dict[str, str] = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "api_key": r"(Bearer |api[_-]?key[_-]?=)[A-Za-z0-9_\-]{20,}",
        "password": r'(password["\s:=]+)[^\s"]{6,}',
        "jwt": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
        "phone": r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "iban": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b",
        "db_url": r"(postgresql|mysql|sqlite)://[^:]+:[^@]+@[^/]+",  # DB connection strings
        "generic_url_password": r"://[^:]+:([^@]+)@",  # Any URL with password
    }

    _compiled_patterns: Dict[str, Pattern] = {}

    @classmethod
    def _get_compiled_patterns(cls) -> Dict[str, Pattern]:
        """Lazy compile regex patterns for performance"""
        if not cls._compiled_patterns:
            cls._compiled_patterns = {
                name: re.compile(pattern, re.IGNORECASE) for name, pattern in cls.PATTERNS.items()
            }
        return cls._compiled_patterns

    @classmethod
    def scrub(cls, message: str) -> str:
        """
        Remove sensitive data from log message

        Args:
            message: Original log message

        Returns:
            Scrubbed message with sensitive data redacted
        """
        if not isinstance(message, str):
            return str(message)

        patterns = cls._get_compiled_patterns()
        scrubbed_message = message

        for pattern_name, pattern in patterns.items():
            scrubbed_message = pattern.sub(f"[REDACTED_{pattern_name.upper()}]", scrubbed_message)

        return scrubbed_message

    @classmethod
    def scrub_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively scrub sensitive data from dictionary

        Args:
            data: Dictionary to scrub

        Returns:
            Scrubbed dictionary
        """
        if not isinstance(data, dict):
            return data

        scrubbed = {}
        for key, value in data.items():
            if isinstance(value, str):
                scrubbed[key] = cls.scrub(value)
            elif isinstance(value, dict):
                scrubbed[key] = cls.scrub_dict(value)
            elif isinstance(value, list):
                scrubbed[key] = [
                    (
                        cls.scrub(item)
                        if isinstance(item, str)
                        else cls.scrub_dict(item) if isinstance(item, dict) else item
                    )
                    for item in value
                ]
            else:
                scrubbed[key] = value

        return scrubbed
