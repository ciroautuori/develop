"""Data validators for agent inputs and outputs.

Provides Pydantic-based validation schemas for common agent data patterns.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class Priority(str, Enum):
    """Priority levels."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Sentiment(str, Enum):
    """Sentiment values."""
    
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class ContentType(str, Enum):
    """Content types."""
    
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"


class BaseValidator(BaseModel):
    """Base validator with common validation rules."""
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "use_enum_values": False,
    }


class TextInput(BaseValidator):
    """Validator for text input.
    
    Attributes:
        text: Input text
        language: Language code (ISO 639-1)
        max_length: Maximum text length
        content_type: Content type
    """
    
    text: str = Field(..., min_length=1)
    language: str = Field(default="en", pattern="^[a-z]{2}$")
    max_length: Optional[int] = Field(default=None, gt=0)
    content_type: ContentType = ContentType.TEXT
    
    @field_validator("text")
    @classmethod
    def validate_text_length(cls, v: str, info) -> str:
        """Validate text doesn't exceed max_length."""
        max_length = info.data.get("max_length")
        if max_length and len(v) > max_length:
            raise ValueError(f"Text exceeds maximum length of {max_length}")
        return v


class URLInput(BaseValidator):
    """Validator for URL input.
    
    Attributes:
        url: URL string
        scheme: Required URL scheme (http, https, etc.)
    """
    
    url: str = Field(..., min_length=1)
    scheme: Optional[str] = Field(default=None, pattern="^https?$")
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str, info) -> str:
        """Validate URL format and scheme."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        
        scheme = info.data.get("scheme")
        if scheme and not v.startswith(f"{scheme}://"):
            raise ValueError(f"URL must use {scheme}:// scheme")
        
        return v


class EmailInput(BaseValidator):
    """Validator for email input.
    
    Attributes:
        email: Email address
        name: Optional recipient name
    """
    
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    name: Optional[str] = None


class DateTimeRange(BaseValidator):
    """Validator for date/time ranges.
    
    Attributes:
        start: Start datetime
        end: End datetime
    """
    
    start: datetime
    end: datetime
    
    @model_validator(mode="after")
    def validate_range(self) -> "DateTimeRange":
        """Validate end is after start."""
        if self.end <= self.start:
            raise ValueError("End datetime must be after start datetime")
        return self


class KeyValuePairs(BaseValidator):
    """Validator for key-value pairs with type constraints.
    
    Attributes:
        pairs: Dictionary of key-value pairs
        required_keys: List of required keys
        allowed_keys: List of allowed keys (None = any)
    """
    
    pairs: Dict[str, Any] = Field(default_factory=dict)
    required_keys: List[str] = Field(default_factory=list)
    allowed_keys: Optional[List[str]] = None
    
    @model_validator(mode="after")
    def validate_keys(self) -> "KeyValuePairs":
        """Validate required and allowed keys."""
        # Check required keys
        missing = set(self.required_keys) - set(self.pairs.keys())
        if missing:
            raise ValueError(f"Missing required keys: {missing}")
        
        # Check allowed keys
        if self.allowed_keys is not None:
            invalid = set(self.pairs.keys()) - set(self.allowed_keys)
            if invalid:
                raise ValueError(f"Invalid keys: {invalid}")
        
        return self


class ListInput(BaseValidator):
    """Validator for list input with constraints.
    
    Attributes:
        items: List of items
        min_items: Minimum number of items
        max_items: Maximum number of items
        unique: Whether items must be unique
    """
    
    items: List[Any] = Field(default_factory=list)
    min_items: int = Field(default=0, ge=0)
    max_items: Optional[int] = Field(default=None, gt=0)
    unique: bool = False
    
    @model_validator(mode="after")
    def validate_list(self) -> "ListInput":
        """Validate list constraints."""
        # Check min items
        if len(self.items) < self.min_items:
            raise ValueError(
                f"List must contain at least {self.min_items} items"
            )
        
        # Check max items
        if self.max_items and len(self.items) > self.max_items:
            raise ValueError(
                f"List must contain at most {self.max_items} items"
            )
        
        # Check uniqueness
        if self.unique and len(self.items) != len(set(self.items)):
            raise ValueError("List items must be unique")
        
        return self


class NumericRange(BaseValidator):
    """Validator for numeric values with range constraints.
    
    Attributes:
        value: Numeric value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    """
    
    value: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    @model_validator(mode="after")
    def validate_range(self) -> "NumericRange":
        """Validate value is within range."""
        if self.min_value is not None and self.value < self.min_value:
            raise ValueError(f"Value must be at least {self.min_value}")
        
        if self.max_value is not None and self.value > self.max_value:
            raise ValueError(f"Value must be at most {self.max_value}")
        
        return self


class FileInput(BaseValidator):
    """Validator for file input.
    
    Attributes:
        filename: File name
        content: File content (bytes or string)
        content_type: MIME type
        max_size: Maximum file size in bytes
    """
    
    filename: str = Field(..., min_length=1)
    content: Any
    content_type: str = "application/octet-stream"
    max_size: Optional[int] = Field(default=None, gt=0)
    
    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename format."""
        # Check for path traversal
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Filename contains invalid characters")
        return v
    
    @model_validator(mode="after")
    def validate_size(self) -> "FileInput":
        """Validate file size."""
        if self.max_size:
            content_size = (
                len(self.content)
                if isinstance(self.content, (str, bytes))
                else 0
            )
            if content_size > self.max_size:
                raise ValueError(
                    f"File size ({content_size}) exceeds maximum ({self.max_size})"
                )
        return self


class IDValidator(BaseValidator):
    """Validator for various ID formats.
    
    Attributes:
        value: ID value
        id_type: Type of ID (uuid, int, string)
    """
    
    value: str | int | UUID
    id_type: str = Field(default="string", pattern="^(uuid|int|string)$")
    
    @model_validator(mode="after")
    def validate_id_type(self) -> "IDValidator":
        """Validate ID matches expected type."""
        if self.id_type == "uuid":
            if not isinstance(self.value, (UUID, str)):
                raise ValueError("UUID expected")
            if isinstance(self.value, str):
                try:
                    UUID(self.value)
                except ValueError as e:
                    raise ValueError(f"Invalid UUID format: {e}") from e
        
        elif self.id_type == "int":
            if not isinstance(self.value, int):
                raise ValueError("Integer ID expected")
        
        return self
