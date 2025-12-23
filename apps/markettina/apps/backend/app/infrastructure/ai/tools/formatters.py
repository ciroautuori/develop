"""Output formatters for agent responses.

Provides formatting utilities for different output types (text, JSON, HTML, etc.)
with support for templates and structured data.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class OutputFormat(str, Enum):
    """Output format types."""

    TEXT = "text"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    CSV = "csv"
    XML = "xml"


class BaseFormatter:
    """Base formatter for agent outputs."""

    def format(self, data: Any) -> str:
        """Format data to string.
        
        Args:
            data: Data to format
            
        Returns:
            Formatted string
        """
        raise NotImplementedError


class TextFormatter(BaseFormatter):
    """Plain text formatter."""

    def __init__(self, template: str | None = None) -> None:
        """Initialize text formatter.
        
        Args:
            template: Optional template string with {key} placeholders
        """
        self.template = template

    def format(self, data: Any) -> str:
        """Format data as plain text.
        
        Args:
            data: Data to format (dict, list, or primitive)
            
        Returns:
            Formatted text
        """
        if self.template and isinstance(data, dict):
            return self.template.format(**data)

        if isinstance(data, (dict, list)):
            return str(data)

        return str(data)


class JSONFormatter(BaseFormatter):
    """JSON formatter with pretty printing."""

    def __init__(self, indent: int = 2, sort_keys: bool = False) -> None:
        """Initialize JSON formatter.
        
        Args:
            indent: Indentation level
            sort_keys: Whether to sort dictionary keys
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def format(self, data: Any) -> str:
        """Format data as JSON.
        
        Args:
            data: Data to format
            
        Returns:
            JSON string
        """
        # Handle Pydantic models
        if isinstance(data, BaseModel):
            data = data.model_dump()

        # Handle datetime and UUID serialization
        def default_serializer(obj: Any) -> Any:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return json.dumps(
            data,
            indent=self.indent,
            sort_keys=self.sort_keys,
            default=default_serializer,
            ensure_ascii=False
        )


class MarkdownFormatter(BaseFormatter):
    """Markdown formatter for structured content."""

    def format(self, data: Any) -> str:
        """Format data as Markdown.
        
        Args:
            data: Data to format (dict or list)
            
        Returns:
            Markdown string
        """
        if isinstance(data, dict):
            return self._format_dict(data)
        if isinstance(data, list):
            return self._format_list(data)
        return str(data)

    def _format_dict(self, data: dict[str, Any], level: int = 1) -> str:
        """Format dictionary as Markdown.
        
        Args:
            data: Dictionary to format
            level: Heading level
            
        Returns:
            Markdown string
        """
        lines = []

        for key, value in data.items():
            # Add heading
            heading = "#" * min(level, 6)
            lines.append(f"{heading} {key.replace('_', ' ').title()}")
            lines.append("")

            # Format value
            if isinstance(value, dict):
                lines.append(self._format_dict(value, level + 1))
            elif isinstance(value, list):
                lines.append(self._format_list(value))
            else:
                lines.append(str(value))

            lines.append("")

        return "\n".join(lines)

    def _format_list(self, data: list[Any]) -> str:
        """Format list as Markdown.
        
        Args:
            data: List to format
            
        Returns:
            Markdown string
        """
        lines = []

        for item in data:
            if isinstance(item, dict):
                # Format as bullet list with nested content
                lines.append("- ")
                for key, value in item.items():
                    lines.append(f"  - **{key}**: {value}")
            else:
                lines.append(f"- {item}")

        return "\n".join(lines)


class HTMLFormatter(BaseFormatter):
    """HTML formatter for structured content."""

    def __init__(self, css_class: str = "agent-output") -> None:
        """Initialize HTML formatter.
        
        Args:
            css_class: CSS class for root element
        """
        self.css_class = css_class

    def format(self, data: Any) -> str:
        """Format data as HTML.
        
        Args:
            data: Data to format
            
        Returns:
            HTML string
        """
        html = f'<div class="{self.css_class}">'

        if isinstance(data, dict):
            html += self._format_dict(data)
        elif isinstance(data, list):
            html += self._format_list(data)
        else:
            html += f"<p>{self._escape_html(str(data))}</p>"

        html += "</div>"
        return html

    def _format_dict(self, data: dict[str, Any]) -> str:
        """Format dictionary as HTML.
        
        Args:
            data: Dictionary to format
            
        Returns:
            HTML string
        """
        html = "<dl>"

        for key, value in data.items():
            html += f"<dt>{self._escape_html(str(key))}</dt>"
            html += "<dd>"

            if isinstance(value, dict):
                html += self._format_dict(value)
            elif isinstance(value, list):
                html += self._format_list(value)
            else:
                html += self._escape_html(str(value))

            html += "</dd>"

        html += "</dl>"
        return html

    def _format_list(self, data: list[Any]) -> str:
        """Format list as HTML.
        
        Args:
            data: List to format
            
        Returns:
            HTML string
        """
        html = "<ul>"

        for item in data:
            html += "<li>"

            if isinstance(item, dict):
                html += self._format_dict(item)
            elif isinstance(item, list):
                html += self._format_list(item)
            else:
                html += self._escape_html(str(item))

            html += "</li>"

        html += "</ul>"
        return html

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )


class CSVFormatter(BaseFormatter):
    """CSV formatter for tabular data."""

    def __init__(self, delimiter: str = ",", include_header: bool = True) -> None:
        """Initialize CSV formatter.
        
        Args:
            delimiter: Field delimiter
            include_header: Whether to include header row
        """
        self.delimiter = delimiter
        self.include_header = include_header

    def format(self, data: Any) -> str:
        """Format data as CSV.
        
        Args:
            data: Data to format (list of dicts or list of lists)
            
        Returns:
            CSV string
        """
        if not isinstance(data, list):
            raise ValueError("CSV formatter requires list input")

        if not data:
            return ""

        lines = []

        # Handle list of dicts
        if isinstance(data[0], dict):
            keys = list(data[0].keys())

            # Add header
            if self.include_header:
                lines.append(self.delimiter.join(keys))

            # Add rows
            for row in data:
                values = [str(row.get(k, "")) for k in keys]
                lines.append(self.delimiter.join(self._escape_csv(v) for v in values))

        # Handle list of lists
        elif isinstance(data[0], (list, tuple)):
            for row in data:
                values = [str(v) for v in row]
                lines.append(self.delimiter.join(self._escape_csv(v) for v in values))

        return "\n".join(lines)

    def _escape_csv(self, value: str) -> str:
        """Escape CSV special characters.
        
        Args:
            value: Value to escape
            
        Returns:
            Escaped value
        """
        # Quote if contains delimiter, quotes, or newlines
        if self.delimiter in value or '"' in value or "\n" in value:
            escaped_value = value.replace('"', '""')
            return f'"{escaped_value}"'
        return value


class FormatterFactory:
    """Factory for creating formatters."""

    _formatters = {
        OutputFormat.TEXT: TextFormatter,
        OutputFormat.JSON: JSONFormatter,
        OutputFormat.MARKDOWN: MarkdownFormatter,
        OutputFormat.HTML: HTMLFormatter,
        OutputFormat.CSV: CSVFormatter,
    }

    @classmethod
    def create(
        cls,
        format_type: OutputFormat,
        **kwargs: Any
    ) -> BaseFormatter:
        """Create formatter instance.
        
        Args:
            format_type: Type of formatter to create
            **kwargs: Formatter-specific arguments
            
        Returns:
            Formatter instance
            
        Raises:
            ValueError: If format type not supported
        """
        if format_type not in cls._formatters:
            raise ValueError(f"Unsupported format: {format_type}")

        formatter_class = cls._formatters[format_type]
        return formatter_class(**kwargs)

    @classmethod
    def format_output(
        cls,
        data: Any,
        format_type: OutputFormat = OutputFormat.JSON,
        **kwargs: Any
    ) -> str:
        """Format data using specified formatter.
        
        Args:
            data: Data to format
            format_type: Output format
            **kwargs: Formatter-specific arguments
            
        Returns:
            Formatted string
        """
        formatter = cls.create(format_type, **kwargs)
        return formatter.format(data)
