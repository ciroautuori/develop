"""Shared tools and utilities for agent systems.

This package provides reusable tools used across different agent types:
- Memory: Conversation memory and context management
- KnowledgeBase: Vector stores and knowledge retrieval
- APIClient: HTTP client for external integrations
- Validators: Input/output validation schemas
- Formatters: Output formatting utilities
- FileTools: File operations (read, write, search)
- ExecutionTools: Command and script execution
- QualityTools: Code quality checks (lint, format, test)
- DockerTools: Container operations
- GitTools: Version control operations
- DatabaseTools: Database operations
"""

from .api_client import (
    APIResponse,
    ExternalAPIClient,
    HTTPMethod,
    RateLimiter,
)
from .database_tools import (
    BackupResult,
    DatabaseTools,
    MigrationResult,
    QueryResult,
    RestoreResult,
)
from .docker_tools import (
    BuildResult,
    ContainerInfo,
    DockerImage,
    DockerTools,
    ValidationIssue,
    ValidationResult,
)
from .execution_tools import (
    CommandResult,
    ExecutionTools,
    TestResult,
)
from .file_tools import (
    FileInfo,
    FileTools,
    SearchMatch,
)
from .formatters import (
    BaseFormatter,
    CSVFormatter,
    FormatterFactory,
    HTMLFormatter,
    JSONFormatter,
    MarkdownFormatter,
    OutputFormat,
    TextFormatter,
)
from .git_tools import (
    CommitResult,
    FileStatus,
    GitDiff,
    GitFileChange,
    GitStatus,
    GitTools,
    PullResult,
    PushResult,
)
from .knowledge_base import (
    Document,
    KnowledgeBase,
    SearchResult,
    VectorStore,
)
from .memory import (
    AgentMemory,
    ConversationBuffer,
    Message,
)
from .quality_tools import (
    ComplexityMetric,
    ComplexityResult,
    CoverageResult,
    FormatResult,
    LintIssue,
    LintResult,
    QualityTools,
    SecurityIssue,
    SecurityScanResult,
    Severity,
    TypeCheckResult,
)
from .validators import (
    BaseValidator,
    ContentType,
    DateTimeRange,
    EmailInput,
    FileInput,
    IDValidator,
    KeyValuePairs,
    ListInput,
    NumericRange,
    Priority,
    Sentiment,
    TextInput,
    URLInput,
)

__all__ = [
    # API Client
    "ExternalAPIClient",
    "APIResponse",
    "HTTPMethod",
    "RateLimiter",
    # Formatters
    "BaseFormatter",
    "TextFormatter",
    "JSONFormatter",
    "MarkdownFormatter",
    "HTMLFormatter",
    "CSVFormatter",
    "FormatterFactory",
    "OutputFormat",
    # Knowledge Base
    "Document",
    "SearchResult",
    "KnowledgeBase",
    "VectorStore",
    # Memory
    "Message",
    "AgentMemory",
    "ConversationBuffer",
    # Validators
    "BaseValidator",
    "TextInput",
    "URLInput",
    "EmailInput",
    "DateTimeRange",
    "KeyValuePairs",
    "ListInput",
    "NumericRange",
    "FileInput",
    "IDValidator",
    "Priority",
    "Sentiment",
    "ContentType",
    # File Tools
    "FileTools",
    "FileInfo",
    "SearchMatch",
    # Execution Tools
    "ExecutionTools",
    "CommandResult",
    "TestResult",
    # Quality Tools
    "QualityTools",
    "LintResult",
    "LintIssue",
    "FormatResult",
    "TypeCheckResult",
    "SecurityScanResult",
    "SecurityIssue",
    "CoverageResult",
    "ComplexityResult",
    "ComplexityMetric",
    "Severity",
    # Docker Tools
    "DockerTools",
    "DockerImage",
    "ContainerInfo",
    "BuildResult",
    "ValidationResult",
    "ValidationIssue",
    # Git Tools
    "GitTools",
    "GitStatus",
    "GitDiff",
    "GitFileChange",
    "CommitResult",
    "PushResult",
    "PullResult",
    "FileStatus",
    # Database Tools
    "DatabaseTools",
    "QueryResult",
    "MigrationResult",
    "BackupResult",
    "RestoreResult",
]
