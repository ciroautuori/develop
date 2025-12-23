"""
MARKETTINA v2.0 - Workflow Context Models
Persistent workflow engine with execution tracking.
"""

import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.shared.base_model import SoftDeleteMixin, TimestampMixin, VersionMixin
from app.infrastructure.database import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow definition status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, enum.Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TriggerType(str, enum.Enum):
    """Workflow trigger types."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    API = "api"


class WorkflowDefinition(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """
    WorkflowDefinition - Reusable workflow templates.

    Defines the steps, triggers, and configuration for automated workflows.
    """
    __tablename__ = "workflow_definitions"
    __table_args__ = (
        Index("ix_workflow_definitions_account", "account_id", "status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign key
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Workflow info
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Status
    status = Column(SQLEnum(WorkflowStatus), nullable=False, default=WorkflowStatus.DRAFT)

    # Trigger configuration
    trigger_type = Column(SQLEnum(TriggerType), nullable=False, default=TriggerType.MANUAL)
    trigger_config = Column(JSONB, nullable=True)
    # Examples:
    # SCHEDULED: {"cron": "0 9 * * 1", "timezone": "Europe/Rome"}
    # EVENT: {"event_type": "post_published", "filters": {...}}
    # WEBHOOK: {"secret": "...", "url_suffix": "..."}

    # Workflow steps (ordered array)
    steps = Column(JSONB, nullable=False, default=list)
    # Example step:
    # {"id": "1", "type": "content_generation", "config": {...}, "on_success": "2", "on_failure": "error_handler"}

    # Settings
    settings = Column(JSONB, nullable=False, default=dict)
    # {"max_retries": 3, "retry_delay_seconds": 60, "timeout_seconds": 3600}

    # Metadata
    tags = Column(JSONB, nullable=True)  # ["marketing", "social", "automation"]

    # Stats
    total_executions = Column(Integer, nullable=False, default=0)
    successful_executions = Column(Integer, nullable=False, default=0)
    failed_executions = Column(Integer, nullable=False, default=0)
    last_execution_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow", lazy="dynamic")
    schedules = relationship("WorkflowSchedule", back_populates="workflow", lazy="dynamic")

    def __repr__(self):
        return f"<WorkflowDefinition {self.name} ({self.status.value})>"


class WorkflowExecution(Base, TimestampMixin):
    """
    WorkflowExecution - Individual workflow run instance.

    Tracks the execution state, progress, and results of a workflow run.
    """
    __tablename__ = "workflow_executions"
    __table_args__ = (
        Index("ix_workflow_executions_workflow_status", "workflow_id", "status"),
        Index("ix_workflow_executions_account_date", "account_id", "started_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign keys
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Execution info
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING)
    trigger_type = Column(SQLEnum(TriggerType), nullable=False)

    # Progress tracking
    current_step_id = Column(String(100), nullable=True)
    current_step_index = Column(Integer, nullable=False, default=0)
    total_steps = Column(Integer, nullable=False, default=0)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Results
    step_results = Column(JSONB, nullable=False, default=list)
    # [{"step_id": "1", "status": "completed", "output": {...}, "duration_ms": 1234}]

    output = Column(JSONB, nullable=True)  # Final workflow output
    error_message = Column(Text, nullable=True)
    error_stack = Column(Text, nullable=True)

    # Retry tracking
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)

    # Input data
    input_data = Column(JSONB, nullable=True)  # Data passed to workflow

    # Context snapshot (workflow definition at execution time)
    workflow_snapshot = Column(JSONB, nullable=True)

    # Relationships
    workflow = relationship("WorkflowDefinition", back_populates="executions")

    def __repr__(self):
        return f"<WorkflowExecution {self.id} ({self.status.value})>"


class WorkflowSchedule(Base, TimestampMixin, SoftDeleteMixin):
    """
    WorkflowSchedule - Scheduled workflow runs.

    Manages CRON-based scheduling for workflows.
    """
    __tablename__ = "workflow_schedules"
    __table_args__ = (
        UniqueConstraint("workflow_id", "cron_expression", name="uq_workflow_schedule"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign key
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Schedule configuration
    cron_expression = Column(String(100), nullable=False)  # "0 9 * * 1" (Monday 9am)
    timezone = Column(String(50), nullable=False, default="Europe/Rome")

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Tracking
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_status = Column(SQLEnum(ExecutionStatus), nullable=True)

    # Relationships
    workflow = relationship("WorkflowDefinition", back_populates="schedules")

    def __repr__(self):
        return f"<WorkflowSchedule {self.cron_expression}>"


class WorkflowStepLog(Base, TimestampMixin):
    """
    WorkflowStepLog - Detailed step execution logs.

    Provides granular logging for debugging and auditing.
    """
    __tablename__ = "workflow_step_logs"
    __table_args__ = (
        Index("ix_workflow_step_logs_execution", "execution_id", "step_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign key
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Step info
    step_id = Column(String(100), nullable=False)
    step_type = Column(String(100), nullable=False)
    step_name = Column(String(255), nullable=True)

    # Execution
    status = Column(SQLEnum(ExecutionStatus), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Input/Output
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)

    # Errors
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)

    # Metrics
    tokens_consumed = Column(Integer, nullable=True)
    api_calls_made = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<WorkflowStepLog {self.step_id} ({self.status.value})>"
