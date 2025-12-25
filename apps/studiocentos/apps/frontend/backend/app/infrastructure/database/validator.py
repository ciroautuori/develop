"""Database URL Validation and Security Layer
Addresses D2: SQL Injection Risk via Dynamic Database URL.
"""

import re
import urllib.parse

from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import ArgumentError

class DatabaseURLValidator:
    """Validates and sanitizes database URLs to prevent injection attacks."""

    ALLOWED_SCHEMES = {"postgresql", "postgresql+psycopg", "postgresql+psycopg2", "sqlite"}
    MAX_HOST_LENGTH = 253  # RFC compliant
    MAX_DB_NAME_LENGTH = 63  # PostgreSQL limit

    @classmethod
    def validate_database_url(cls, url: str) -> str:
        """Validates database URL for security and compliance.

        Args:
            url: Database connection URL

        Returns:
            Validated and sanitized URL

        Raises:
            ValueError: If URL is invalid or potentially malicious
        """
        if not url or not isinstance(url, str):
            raise ValueError("Database URL must be a non-empty string")

        try:
            # Parse URL using SQLAlchemy's parser
            parsed_url = make_url(url)
        except ArgumentError as e:
            raise ValueError(f"Invalid database URL format: {e}")

        # Validate scheme
        if parsed_url.drivername not in cls.ALLOWED_SCHEMES:
            raise ValueError(
                f"Unsupported database scheme: {parsed_url.drivername}. "
                f"Allowed: {', '.join(cls.ALLOWED_SCHEMES)}"
            )

        # Validate host
        if parsed_url.host and len(parsed_url.host) > cls.MAX_HOST_LENGTH:
            raise ValueError(f"Host name too long: {len(parsed_url.host)} > {cls.MAX_HOST_LENGTH}")

        # Validate database name
        if parsed_url.database:
            if len(parsed_url.database) > cls.MAX_DB_NAME_LENGTH:
                raise ValueError(
                    f"Database name too long: {len(parsed_url.database)} > {cls.MAX_DB_NAME_LENGTH}"
                )

            # Check for SQL injection patterns in database name
            if cls._contains_sql_injection_patterns(parsed_url.database):
                raise ValueError("Database name contains potentially malicious patterns")

        # Validate port
        if parsed_url.port and (parsed_url.port < 1 or parsed_url.port > 65535):
            raise ValueError(f"Invalid port number: {parsed_url.port}")

        # Sanitize and reconstruct URL
        return str(cls._sanitize_url(parsed_url))

    @classmethod
    def _contains_sql_injection_patterns(cls, value: str) -> bool:
        """Check for common SQL injection patterns."""
        dangerous_patterns = [
            r";",  # Statement separator
            r"--",  # SQL comment
            r"/\*",  # Multi-line comment start
            r"\*/",  # Multi-line comment end
            r"union\s+select",  # UNION SELECT
            r"drop\s+table",  # DROP TABLE
            r"delete\s+from",  # DELETE FROM
            r"insert\s+into",  # INSERT INTO
            r"update\s+.*\s+set",  # UPDATE SET
            r"exec\s*\(",  # EXEC function
            r"sp_\w+",  # Stored procedures
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    @classmethod
    def _sanitize_url(cls, parsed_url: URL) -> URL:
        """Sanitize URL components."""
        # Solo URL encode se contengono caratteri speciali che richiedono encoding
        username = parsed_url.username
        password = parsed_url.password

        # URL encode solo se necessario per username
        if username and any(c in username for c in "@:/?#[]%"):
            username = urllib.parse.quote(username)

        # URL encode solo se necessario per password
        if password and any(c in password for c in "@:/?#[]%"):
            password = urllib.parse.quote(password)

        return parsed_url._replace(username=username, password=password)

def get_validated_database_url(url: str) -> str:
    """Public function to get validated database URL.

    Usage:
        DATABASE_URL = get_validated_database_url(os.getenv('DATABASE_URL'))
    """
    return DatabaseURLValidator.validate_database_url(url)
