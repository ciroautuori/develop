"""Base agent abstraction for multi-agent systems.

This module provides the abstract base class that all specialized agents
inherit from, ensuring consistent interface and behavior across agent types.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, Field

from .state import AgentState, StateManager
from .task import Task, TaskInput, TaskOutput, TaskStatus

if TYPE_CHECKING:
    from .cognitive_memory import CognitiveMemorySystem, MemoryType


class AgentCapability(BaseModel):
    """Represents a capability that an agent can perform.
    
    Capabilities define what an agent can do, including input/output
    schemas and any required tools or integrations.
    
    Attributes:
        name: Capability name
        description: Capability description
        input_schema: Expected input schema
        output_schema: Expected output schema
        required_tools: Tools required for this capability
        metadata: Additional metadata
    """
    
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    required_tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Configuration for an agent instance.
    
    Attributes:
        agent_id: Unique agent identifier
        agent_type: Type of agent
        model: LLM model to use
        temperature: LLM temperature (0.0-2.0)
        max_tokens: Maximum tokens per request
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts on failure
        capabilities: List of enabled capabilities
        tools: List of available tools
        metadata: Additional configuration
    """
    
    agent_id: str = Field(default_factory=lambda: f"agent_{uuid4().hex[:8]}")
    agent_type: str = Field(..., min_length=1, max_length=100)
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, gt=0, le=128000)
    timeout: int = Field(default=30, gt=0, le=300)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "agent_type": "marketing_content_creator",
                    "model": "gpt-4o",
                    "temperature": 0.8,
                    "capabilities": ["blog_generation", "seo_optimization"],
                    "tools": ["content_generator", "seo_analyzer"]
                }
            ]
        }
    }


class AgentMetrics(BaseModel):
    """Metrics for agent performance tracking.
    
    Attributes:
        tasks_executed: Total tasks executed
        tasks_succeeded: Tasks completed successfully
        tasks_failed: Tasks that failed
        avg_execution_time: Average execution time in seconds
        total_tokens_used: Total LLM tokens used
        total_cost: Total cost in USD
        last_executed_at: Last execution timestamp
        metadata: Additional metrics
    """
    
    tasks_executed: int = Field(default=0, ge=0)
    tasks_succeeded: int = Field(default=0, ge=0)
    tasks_failed: int = Field(default=0, ge=0)
    avg_execution_time: float = Field(default=0.0, ge=0.0)
    total_tokens_used: int = Field(default=0, ge=0)
    total_cost: float = Field(default=0.0, ge=0.0)
    last_executed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.tasks_executed == 0:
            return 0.0
        return self.tasks_succeeded / self.tasks_executed
    
    def update_from_task(
        self,
        task: Task,
        tokens_used: int = 0,
        cost: float = 0.0
    ) -> None:
        """Update metrics from a completed task.
        
        Args:
            task: Completed task
            tokens_used: Tokens used for task execution
            cost: Cost of task execution in USD
        """
        self.tasks_executed += 1
        
        if task.status == TaskStatus.COMPLETED:
            self.tasks_succeeded += 1
        elif task.status == TaskStatus.FAILED:
            self.tasks_failed += 1
        
        if task.duration:
            # Update average execution time
            total_time = self.avg_execution_time * (self.tasks_executed - 1)
            self.avg_execution_time = (total_time + task.duration) / self.tasks_executed
        
        self.total_tokens_used += tokens_used
        self.total_cost += cost
        self.last_executed_at = datetime.utcnow()


class BaseAgent(ABC):
    """Abstract base class for all agents in the multi-agent system.
    
    All specialized agents (Marketing, Support, Security, etc.) inherit from
    this base class to ensure consistent interface and behavior.
    
    Attributes:
        config: Agent configuration
        state_manager: State management system
        metrics: Agent performance metrics
    """
    
    def __init__(
        self,
        config: AgentConfig,
        state_manager: Optional[StateManager] = None,
        memory_system: Optional["CognitiveMemorySystem"] = None
    ) -> None:
        """Initialize base agent.
        
        Args:
            config: Agent configuration
            state_manager: State manager (creates new if not provided)
            memory_system: Cognitive memory system for shared learning
        """
        self.config = config
        self.state_manager = state_manager or StateManager()
        self.memory_system = memory_system
        self.metrics = AgentMetrics()
        
        # Load existing state if available
        existing_state = self.state_manager.get_agent_state(config.agent_id)
        if existing_state:
            self._state = existing_state
        else:
            self._state = AgentState(
                agent_id=config.agent_id,
                agent_type=config.agent_type,
                config=config.model_dump()
            )
            self.state_manager.save_agent_state(self._state)
    
    @property
    def agent_id(self) -> str:
        """Get agent unique identifier."""
        return self.config.agent_id
    
    @property
    def agent_type(self) -> str:
        """Get agent type."""
        return self.config.agent_type
    
    @property
    def state(self) -> AgentState:
        """Get agent state."""
        return self._state
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of agent capabilities.
        
        Returns:
            List of capabilities this agent can perform
        """
        pass
    
    @abstractmethod
    async def execute(self, task: Task) -> TaskOutput:
        """Execute a task.
        
        Args:
            task: Task to execute
            
        Returns:
            Task output
            
        Raises:
            Exception: If task execution fails
        """
        pass
    
    async def run(self, task: Task) -> Task:
        """Run a task with full lifecycle management.
        
        Handles task status updates, error handling, metrics collection,
        and state persistence.
        
        Args:
            task: Task to run
            
        Returns:
            Updated task with results
        """
        # Validate task type matches agent
        if task.agent_type != self.agent_type:
            task.fail(
                f"Task agent_type '{task.agent_type}' does not match "
                f"agent type '{self.agent_type}'"
            )
            return task
        
        # Start task
        task.start()
        
        try:
            # Execute task
            output = await self.execute(task)
            
            # Complete task
            task.complete(output)
            
            # Update metrics
            self.metrics.update_from_task(
                task,
                tokens_used=output.metadata.get("tokens_used", 0),
                cost=output.metadata.get("cost", 0.0)
            )
            
            # Store successful execution in memory
            if self.memory_system and task.status == TaskStatus.COMPLETED:
                await self._store_task_memory(task, output, success=True)
            
        except Exception as e:
            # Fail task
            error_msg = f"{type(e).__name__}: {str(e)}"
            task.fail(error_msg)
            
            # Update metrics
            self.metrics.update_from_task(task)
            
            # Store error in memory for learning
            if self.memory_system:
                await self._store_task_memory(task, error=error_msg)
        
        return task
    
    async def execute_with_memory(
        self,
        task: Task,
        use_similar_solutions: bool = True
    ) -> TaskOutput:
        """Execute task with memory-augmented context.
        
        Queries cognitive memory for similar past experiences before execution,
        providing the agent with relevant context and solutions.
        
        Args:
            task: Task to execute
            use_similar_solutions: Whether to query memory for similar solutions
            
        Returns:
            Task output
        """
        similar_memories = []
        
        # Query memory for similar experiences
        if self.memory_system and use_similar_solutions:
            from .cognitive_memory import MemoryType
            
            # Build query from task
            query_text = f"{task.input.instruction} {task.input.context}"
            
            result = await self.memory_system.query_memory(
                query_text=query_text,
                memory_types=[MemoryType.SUCCESS, MemoryType.PROCEDURAL],
                agent_id=self.agent_id,
                max_results=5,
                min_relevance=0.7
            )
            
            similar_memories = result.memories
        
        # Augment task context with similar solutions
        if similar_memories:
            memory_context = "\n\n**Similar Past Solutions:**\n"
            for i, mem in enumerate(similar_memories[:3], 1):
                memory_context += f"\n{i}. {mem.content} (relevance: {mem.relevance_score:.2f})\n"
            
            # Add to task context
            task.input.context = (task.input.context or "") + memory_context
        
        # Execute task normally
        return await self.execute(task)
    
    async def _store_task_memory(
        self,
        task: Task,
        output: Optional[TaskOutput] = None,
        error: Optional[str] = None,
        success: bool = False
    ) -> None:
        """Store task execution in cognitive memory.
        
        Args:
            task: Executed task
            output: Task output (if successful)
            error: Error message (if failed)
            success: Whether execution was successful
        """
        if not self.memory_system:
            return
        
        from .cognitive_memory import MemoryType
        
        # Prepare memory content
        if success and output:
            content = f"Task: {task.input.instruction}\nResult: {output.result}\n"
            if output.metadata:
                content += f"Metadata: {output.metadata}\n"
            memory_type = MemoryType.SUCCESS
        else:
            content = f"Task: {task.input.instruction}\nError: {error}\n"
            memory_type = MemoryType.ERROR
        
        # Prepare metadata
        metadata = {
            "task_id": task.task_id,
            "agent_type": self.agent_type,
            "duration": task.duration or 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if task.input.metadata:
            metadata.update(task.input.metadata)
        
        # Store in memory
        await self.memory_system.store_memory(
            content=content,
            memory_type=memory_type,
            metadata=metadata,
            agent_id=self.agent_id,
            task_id=task.task_id
        )
    
    def update_state(self, data: Dict[str, Any]) -> None:
        """Update agent state.
        
        Args:
            data: State data to update
        """
        self._state.update(data)
        self.state_manager.save_agent_state(self._state)
    
    def get_state_value(self, key: str, default: Any = None) -> Any:
        """Get value from agent state.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        return self._state.get(key, default)
    
    def set_state_value(self, key: str, value: Any) -> None:
        """Set value in agent state.
        
        Args:
            key: State key
            value: State value
        """
        self._state.set(key, value)
        self.state_manager.save_agent_state(self._state)
    
    def reset_state(self) -> None:
        """Reset agent state."""
        self._state.clear()
        self.state_manager.save_agent_state(self._state)
    
    def get_health(self) -> Dict[str, Any]:
        """Get agent health status.
        
        Returns:
            Health status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": "healthy" if self.metrics.success_rate >= 0.9 else "degraded",
            "success_rate": self.metrics.success_rate,
            "tasks_executed": self.metrics.tasks_executed,
            "last_executed_at": (
                self.metrics.last_executed_at.isoformat()
                if self.metrics.last_executed_at
                else None
            )
        }
    
    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"{self.__class__.__name__}("
            f"agent_id='{self.agent_id}', "
            f"agent_type='{self.agent_type}')"
        )
