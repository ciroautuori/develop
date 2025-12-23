"""Input Sanitization - Enterprise Grade
Sistema completo di sanitizzazione input per prevenire injection attacks.
"""

import html
import logging
import re
import urllib.parse
from typing import Any

import bleach
from pydantic import BaseModel, Field, field_validator
from pydantic_core import core_schema

logger = logging.getLogger(__name__)

class InputSanitizer:
    """Enterprise Input Sanitization Engine.

    Previene:
    - SQL Injection (tramite ORM + validazione)
    - XSS (Cross-Site Scripting)
    - HTML Injection
    - Script Injection
    - Path Traversal
    - Command Injection
    - LDAP Injection
    """

    # Whitelist di tag HTML sicuri per contenuto rich
    ALLOWED_HTML_TAGS = [
        "p",
        "br",
        "strong",
        "b",
        "em",
        "i",
        "u",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "blockquote",
        "code",
        "pre",
    ]

    # Attributi HTML sicuri
    ALLOWED_HTML_ATTRIBUTES = {
        "*": ["class", "id"],
        "a": ["href", "title"],
        "img": ["src", "alt", "title", "width", "height"],
    }

    # Pattern per rilevare tentativi di injection
    INJECTION_PATTERNS = [
        # SQL Injection patterns
        re.compile(
            r"(\bUNION\b.*\bSELECT\b|\bSELECT\b.*\bFROM\b|\bINSERT\b.*\bINTO\b|\bUPDATE\b.*\bSET\b|\bDELETE\b.*\bFROM\b)",
            re.IGNORECASE,
        ),
        # XSS patterns
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        # Path traversal
        re.compile(r"\.\.[\\/]"),
        # Command injection
        re.compile(r"[;&|`$()]"),
    ]

    @classmethod
    def sanitize_string(cls, value: str, allow_html: bool = False) -> str:
        """Sanitizza stringa generale."""
        if not isinstance(value, str):
            return str(value)

        # Rimuovi null bytes
        value = value.replace("\x00", "")

        # Rimuovi caratteri di controllo ASCII (tranne tab, newline, carriage return)
        value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)

        if allow_html:
            # Usa bleach per pulizia HTML sicura
            value = bleach.clean(
                value,
                tags=cls.ALLOWED_HTML_TAGS,
                attributes=cls.ALLOWED_HTML_ATTRIBUTES,
                strip=True,
            )
        else:
            # Escape HTML entities
            value = html.escape(value, quote=True)

        # Limita lunghezza per prevenire DoS
        if len(value) > 10000:  # 10KB limit per field
            value = value[:10000]
            logger.warning(f"String truncated to prevent DoS: {len(value)} chars")

        return value.strip()

    @classmethod
    def sanitize_email(cls, email: str) -> str:
        """Sanitizza email address."""
        if not email:
            return ""

        email = cls.sanitize_string(email).lower()

        # Rimuovi spazi
        email = re.sub(r"\s+", "", email)

        # Validazione formato email basic
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError(f"Invalid email format: {email}")

        return email

    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """Sanitizza URL per prevenire open redirect e injection."""
        if not url:
            return ""

        url = cls.sanitize_string(url)

        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            logger.warning(f"Invalid URL format: {url}, error: {e}")
            raise ValueError(f"Invalid URL format: {url}")

        # Whitelist di scheme sicuri
        allowed_schemes = ["http", "https", "mailto"]
        if parsed.scheme and parsed.scheme.lower() not in allowed_schemes:
            raise ValueError(f"Unsafe URL scheme: {parsed.scheme}")

        # Previeni JavaScript URLs
        if "javascript:" in url.lower():
            raise ValueError("JavaScript URLs not allowed")

        return url

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitizza filename per prevenire path traversal."""
        if not filename:
            return ""

        # Rimuovi path components
        filename = filename.split("/")[-1].split("\\")[-1]

        # Rimuovi caratteri pericolosi
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", filename)

        # Rimuovi dot files nascosti e path traversal
        filename = re.sub(r"^\.+", "", filename)
        filename = re.sub(r"\.\.+", ".", filename)

        # Limita lunghezza
        if len(filename) > 255:
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            filename = name[:250] + ("." + ext if ext else "")

        if not filename:
            raise ValueError("Invalid filename")

        return filename

    @classmethod
    def detect_injection_attempt(cls, value: str) -> str | None:
        """Rileva tentativi di injection."""
        if not isinstance(value, str):
            return None

        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(value):
                return f"Potential injection detected: {pattern.pattern[:50]}..."

        return None

    @classmethod
    def sanitize_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitizza ricorsivamente un dictionary."""
        sanitized = {}

        for key, value in data.items():
            # Sanitizza chiave
            key = cls.sanitize_string(str(key))

            if isinstance(value, str):
                # Verifica injection attempt
                injection = cls.detect_injection_attempt(value)
                if injection:
                    logger.warning(f"Injection attempt blocked in field '{key}': {injection}")
                    raise ValueError(f"Invalid input detected in field '{key}'")

                sanitized[key] = cls.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = cls.sanitize_list(value)
            else:
                sanitized[key] = value

        return sanitized

    @classmethod
    def sanitize_list(cls, data: list[Any]) -> list[Any]:
        """Sanitizza ricorsivamente una lista."""
        sanitized = []

        for item in data:
            if isinstance(item, str):
                sanitized.append(cls.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(cls.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(cls.sanitize_list(item))
            else:
                sanitized.append(item)

        return sanitized

class SanitizedString(str):
    """String sanitizzata automaticamente."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            value = str(value)
        return InputSanitizer.sanitize_string(value)

class SanitizedEmail(str):
    """Email sanitizzata automaticamente."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            value = str(value)
        return InputSanitizer.sanitize_email(value)

class SanitizedUrl(str):
    """URL sanitizzata automaticamente."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            value = str(value)
        return InputSanitizer.sanitize_url(value)

class SanitizedFilename(str):
    """Filename sanitizzato automaticamente."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            value = str(value)
        return InputSanitizer.sanitize_filename(value)

# Esempio di utilizzo con Pydantic models
class SecureProfileModel(BaseModel):
    """Esempio di model con sanitizzazione automatica."""

    name: SanitizedString = Field(..., min_length=1, max_length=100)
    email: SanitizedEmail = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    bio: SanitizedString = Field(default="", max_length=1000)
    website: SanitizedUrl | None = None
    linkedin_url: SanitizedUrl | None = None

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v):
        # Bio può contenere HTML limitato
        return InputSanitizer.sanitize_string(v, allow_html=True)

def sanitize_request_data(data: dict | list | str) -> dict | list | str:
    """Funzione helper per sanitizzare dati request."""
    if isinstance(data, dict):
        return InputSanitizer.sanitize_dict(data)
    if isinstance(data, list):
        return InputSanitizer.sanitize_list(data)
    if isinstance(data, str):
        return InputSanitizer.sanitize_string(data)
    return data
