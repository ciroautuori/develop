"""Multi-agent orchestrator for coordinating agent workflows.

This module provides the orchestrator that manages multiple agents,
coordinates task execution, handles dependencies, and manages workflows.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from uuid import UUID

from .base_agent import BaseAgent
from .state import StateManager
from .task import Task, TaskStatus, WorkflowResult

logger = logging.getLogger(__name__)


class OrchestrationStrategy(str, Enum):
    """Strategy for orchestrating multiple agents."""

    SEQUENTIAL = "sequential"  # Execute tasks one at a time
    PARALLEL = "parallel"  # Execute all tasks in parallel
    PRIORITY = "priority"  # Execute by priority
    DEPENDENCY = "dependency"  # Execute based on dependencies


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""


class AgentNotFoundError(OrchestratorError):
    """Raised when requested agent is not found."""


class WorkflowExecutionError(OrchestratorError):
    """Raised when workflow execution fails."""


class AgentOrchestrator:
    """Orchestrates multiple agents to execute complex workflows.

    The orchestrator manages agent registration, task routing, dependency
    resolution, and workflow execution with support for multiple strategies.

    Attributes:
        strategy: Orchestration strategy to use
        state_manager: Shared state manager for all agents
        agents: Registered agents by type
    """

    def __init__(
        self,
        strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL,
        state_manager: StateManager | None = None
    ) -> None:
        """Initialize orchestrator.

        Args:
            strategy: Orchestration strategy
            state_manager: State manager (creates new if not provided)
        """
        self.strategy = strategy
        self.state_manager = state_manager or StateManager()
        self._agents: dict[str, BaseAgent] = {}
        self._running_workflows: dict[UUID, WorkflowResult] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator.

        Args:
            agent: Agent to register

        Raises:
            ValueError: If agent type already registered
        """
        if agent.agent_type in self._agents:
            raise ValueError(
                f"Agent type '{agent.agent_type}' already registered"
            )
        self._agents[agent.agent_type] = agent

    def unregister_agent(self, agent_type: str) -> bool:
        """Unregister an agent.

        Args:
            agent_type: Type of agent to unregister

        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_type in self._agents:
            del self._agents[agent_type]
            return True
        return False

    def get_agent(self, agent_type: str) -> BaseAgent:
        """Get registered agent by type.

        Args:
            agent_type: Type of agent to get

        Returns:
            Agent instance

        Raises:
            AgentNotFoundError: If agent type not registered
        """
        if agent_type not in self._agents:
            raise AgentNotFoundError(
                f"Agent type '{agent_type}' not registered. "
                f"Available types: {list(self._agents.keys())}"
            )
        return self._agents[agent_type]

    def get_registered_agents(self) -> list[str]:
        """Get list of registered agent types.

        Returns:
            List of agent type names
        """
        return list(self._agents.keys())

    async def execute_task(self, task: Task) -> Task:
        """Execute a single task using appropriate agent.

        Args:
            task: Task to execute

        Returns:
            Completed task

        Raises:
            AgentNotFoundError: If agent for task not found
        """
        agent = self.get_agent(task.agent_type)
        return await agent.run(task)

    async def execute_workflow(
        self,
        tasks: list[Task],
        strategy: OrchestrationStrategy | None = None
    ) -> WorkflowResult:
        """Execute a workflow of multiple tasks.

        Args:
            tasks: List of tasks to execute
            strategy: Orchestration strategy (uses default if not provided)

        Returns:
            Workflow result with all task results

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        if not tasks:
            raise WorkflowExecutionError("Cannot execute empty workflow")

        strategy = strategy or self.strategy

        # Create workflow result
        result = WorkflowResult(tasks=tasks)
        result.started_at = datetime.utcnow()
        self._running_workflows[result.workflow_id] = result

        try:
            # Execute tasks based on strategy
            if strategy == OrchestrationStrategy.SEQUENTIAL:
                await self._execute_sequential(tasks)
            elif strategy == OrchestrationStrategy.PARALLEL:
                await self._execute_parallel(tasks)
            elif strategy == OrchestrationStrategy.PRIORITY:
                await self._execute_by_priority(tasks)
            elif strategy == OrchestrationStrategy.DEPENDENCY:
                await self._execute_by_dependency(tasks)

            # Update workflow status
            if all(t.status == TaskStatus.COMPLETED for t in tasks):
                result.status = TaskStatus.COMPLETED
            elif any(t.status == TaskStatus.FAILED for t in tasks):
                result.status = TaskStatus.FAILED
            else:
                result.status = TaskStatus.COMPLETED  # Partial completion

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.metadata["error"] = str(e)
            raise WorkflowExecutionError(f"Workflow execution failed: {e}") from e

        finally:
            result.completed_at = datetime.utcnow()
            del self._running_workflows[result.workflow_id]

        return result

    async def _execute_sequential(self, tasks: list[Task]) -> None:
        """Execute tasks sequentially.

        Args:
            tasks: Tasks to execute
        """
        for task in tasks:
            await self.execute_task(task)

    async def _execute_parallel(self, tasks: list[Task]) -> None:
        """Execute tasks in parallel.

        Args:
            tasks: Tasks to execute
        """
        await asyncio.gather(
            *[self.execute_task(task) for task in tasks],
            return_exceptions=True
        )

    async def _execute_by_priority(self, tasks: list[Task]) -> None:
        """Execute tasks by priority (highest first).

        Args:
            tasks: Tasks to execute
        """
        # Sort by priority (lower value = higher priority)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority.value)
        await self._execute_sequential(sorted_tasks)

    async def _execute_by_dependency(self, tasks: list[Task]) -> None:
        """Execute tasks based on dependencies.

        Args:
            tasks: Tasks to execute

        Raises:
            WorkflowExecutionError: If circular dependencies detected
        """
        completed: set[UUID] = set()
        remaining = {task.id: task for task in tasks}
        max_iterations = len(tasks) * 2  # Prevent infinite loops
        iteration = 0

        while remaining and iteration < max_iterations:
            iteration += 1

            # Find tasks ready to execute
            ready_tasks = [
                task for task in remaining.values()
                if task.is_ready(completed)
            ]

            if not ready_tasks:
                # No tasks ready - possible circular dependency
                raise WorkflowExecutionError(
                    f"Circular dependency detected or missing dependencies. "
                    f"Remaining tasks: {list(remaining.keys())}"
                )

            # Execute ready tasks in parallel
            await asyncio.gather(
                *[self.execute_task(task) for task in ready_tasks],
                return_exceptions=True
            )

            # Mark completed
            for task in ready_tasks:
                if task.status in {TaskStatus.COMPLETED, TaskStatus.FAILED}:
                    completed.add(task.id)
                    remaining.pop(task.id, None)

        if remaining:
            raise WorkflowExecutionError(
                f"Workflow did not complete. Remaining tasks: {list(remaining.keys())}"
            )

    def get_agent_status(self) -> dict[str, dict]:
        """Get status of all registered agents.

        Returns:
            Dictionary mapping agent type to health status
        """
        return {
            agent_type: agent.get_health()
            for agent_type, agent in self._agents.items()
        }

    def get_workflow_status(self, workflow_id: UUID) -> WorkflowResult | None:
        """Get status of running workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow result or None if not found
        """
        return self._running_workflows.get(workflow_id)

    def handle_agent_failure(
        self,
        agent_type: str,
        error: Exception
    ) -> None:
        """Handle agent failure.

        Args:
            agent_type: Type of failed agent
            error: Exception that caused failure
        """
        # Log error (would integrate with logging system)
        logger.error(f"Agent {agent_type} failed: {error}")

        # Could implement recovery strategies here:
        # - Restart agent
        # - Switch to backup agent
        # - Alert monitoring system
        # - Etc.

    async def shutdown(self) -> None:
        """Gracefully shutdown orchestrator.

        Waits for running workflows to complete and cleans up resources.
        """
        # Wait for running workflows to complete (with timeout)
        if self._running_workflows:
            logger.info(f"Waiting for {len(self._running_workflows)} workflows to complete...")

            # Wait up to 60 seconds for workflows to complete
            timeout = 60
            start_time = datetime.utcnow()

            while self._running_workflows:
                if (datetime.utcnow() - start_time).seconds > timeout:
                    logger.warning("Shutdown timeout - forcefully terminating")
                    break
                await asyncio.sleep(1)

        # Clear agents
        self._agents.clear()
        logger.info("Orchestrator shutdown complete")

    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"AgentOrchestrator("
            f"strategy={self.strategy}, "
            f"agents={len(self._agents)}, "
            f"running_workflows={len(self._running_workflows)})"
        )
