"""Task definitions and workflow management for multi-agent systems.

This module provides the core Task abstraction used across all agent types.
Tasks represent units of work that agents can execute, with support for
dependencies, priority, retry logic, and metadata.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Task execution status."""
    
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class TaskPriority(int, Enum):
    """Task priority levels (lower number = higher priority)."""
    
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskInput(BaseModel):
    """Input data for task execution."""
    
    data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {"query": "Generate blog post about AI"},
                    "context": {"user_id": "123", "brand_voice": "professional"}
                }
            ]
        }
    }


class TaskOutput(BaseModel):
    """Output data from task execution."""
    
    result: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "result": {"content": "AI blog post...", "word_count": 1500},
                    "metadata": {"model": "gpt-4o", "tokens": 2000},
                    "artifacts": ["blog_post_draft.md"]
                }
            ]
        }
    }


class Task(BaseModel):
    """Represents a unit of work for an agent to execute.
    
    Tasks are the fundamental unit of work in the multi-agent system.
    Each task has a unique ID, type, input/output, status, and metadata.
    
    Attributes:
        id: Unique task identifier
        task_type: Type of task (e.g., "content_creation", "ticket_triage")
        agent_type: Type of agent that should handle this task
        input: Input data for task execution
        output: Output data from task execution (populated after completion)
        status: Current task status
        priority: Task priority level
        dependencies: IDs of tasks that must complete before this one
        retry_count: Number of retry attempts
        max_retries: Maximum number of retry attempts
        created_at: Task creation timestamp
        started_at: Task start timestamp
        completed_at: Task completion timestamp
        metadata: Additional task metadata
    """
    
    id: UUID = Field(default_factory=uuid4)
    task_type: str = Field(..., min_length=1, max_length=100)
    agent_type: str = Field(..., min_length=1, max_length=100)
    input: TaskInput = Field(default_factory=TaskInput)
    output: Optional[TaskOutput] = None
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    dependencies: List[UUID] = Field(default_factory=list)
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("task_type", "agent_type")
    @classmethod
    def validate_type_format(cls, v: str) -> str:
        """Validate type strings are lowercase with underscores."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Type must contain only alphanumeric characters and underscores")
        return v.lower()
    
    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
    
    def complete(self, output: TaskOutput) -> None:
        """Mark task as completed with output."""
        self.status = TaskStatus.COMPLETED
        self.output = output
        self.completed_at = datetime.utcnow()
    
    def fail(self, error: str) -> None:
        """Mark task as failed with error message."""
        self.error = error
        
        if self.retry_count < self.max_retries:
            self.status = TaskStatus.RETRY
            self.retry_count += 1
        else:
            self.status = TaskStatus.FAILED
            self.completed_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel task execution."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def is_ready(self, completed_tasks: set[UUID]) -> bool:
        """Check if task is ready to execute based on dependencies.
        
        Args:
            completed_tasks: Set of completed task IDs
            
        Returns:
            True if all dependencies are satisfied
        """
        return all(dep_id in completed_tasks for dep_id in self.dependencies)
    
    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED
        }
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_type": "content_creation",
                    "agent_type": "marketing_content_creator",
                    "input": {
                        "data": {"topic": "AI trends 2024"},
                        "context": {"brand": "TechCorp"}
                    },
                    "priority": 1,
                    "max_retries": 3
                }
            ]
        }
    }


class WorkflowResult(BaseModel):
    """Result from a multi-task workflow execution.
    
    Aggregates results from multiple tasks executed as part of a workflow.
    
    Attributes:
        workflow_id: Unique workflow identifier
        tasks: List of tasks in the workflow
        status: Overall workflow status
        started_at: Workflow start timestamp
        completed_at: Workflow completion timestamp
        metadata: Additional workflow metadata
    """
    
    workflow_id: UUID = Field(default_factory=uuid4)
    tasks: List[Task] = Field(default_factory=list)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def completed_count(self) -> int:
        """Get number of completed tasks."""
        return sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
    
    @property
    def failed_count(self) -> int:
        """Get number of failed tasks."""
        return sum(1 for task in self.tasks if task.status == TaskStatus.FAILED)
    
    @property
    def success_rate(self) -> float:
        """Get workflow success rate (0.0 to 1.0)."""
        if not self.tasks:
            return 0.0
        terminal_tasks = [t for t in self.tasks if t.is_terminal]
        if not terminal_tasks:
            return 0.0
        return self.completed_count / len(terminal_tasks)
    
    @property
    def duration(self) -> Optional[float]:
        """Get workflow duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
