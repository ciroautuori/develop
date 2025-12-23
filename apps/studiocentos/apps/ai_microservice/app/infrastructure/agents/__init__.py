"""Core multi-agent system components.

This package provides the foundational classes for building multi-agent systems:
- BaseAgent: Abstract base class for all agents
- AgentOrchestrator: Coordinates multiple agents in workflows
- Task, TaskInput, TaskOutput: Task definitions and execution
- AgentState, StateManager: State persistence and management
- CognitiveMemorySystem: Shared episodic memory with semantic search
- UnifiedLLMManager: Multi-provider LLM management with fallback
"""

from .base_agent import (
    AgentCapability,
    AgentConfig,
    AgentMetrics,
    BaseAgent,
)
from .orchestrator import (
    AgentNotFoundError,
    AgentOrchestrator,
    OrchestrationStrategy,
    OrchestratorError,
    WorkflowExecutionError,
)
from .state import (
    AgentState,
    ConversationState,
    ExecutionCheckpoint,
    StateManager,
)
from .task import (
    Task,
    TaskInput,
    TaskOutput,
    TaskPriority,
    TaskStatus,
    WorkflowResult,
)
from .cognitive_memory import (
    CognitiveMemorySystem,
    MemoryEntry,
    MemoryQuery,
    MemorySearchResult,
    MemoryType,
    KnowledgePattern,
)
from .llm_manager import (
    UnifiedLLMManager,
    LLMProvider,
    LLMConfig,
    LLMResponse,
    TaskComplexity,
    ModelSelection,
)
from ..collaboration.team import (
    AgentTeam,
    MessageType,
    AgentMessage,
    DelegationRequest,
    AssistanceRequest,
    KnowledgeShare,
)
from ..collaboration.protocol import (
    CollaborationProtocol,
    HandoffStrategy,
    ConsensusStrategy,
    HandoffProtocol,
    ConsensusProtocol,
)

__all__ = [
    # Base Agent
    "BaseAgent",
    "AgentConfig",
    "AgentCapability",
    "AgentMetrics",
    # Orchestrator
    "AgentOrchestrator",
    "OrchestrationStrategy",
    "OrchestratorError",
    "AgentNotFoundError",
    "WorkflowExecutionError",
    # Task
    "Task",
    "TaskInput",
    "TaskOutput",
    "TaskStatus",
    "TaskPriority",
    "WorkflowResult",
    # State
    "AgentState",
    "ConversationState",
    "ExecutionCheckpoint",
    "StateManager",
    # Cognitive Memory
    "CognitiveMemorySystem",
    "MemoryEntry",
    "MemoryQuery",
    "MemorySearchResult",
    "MemoryType",
    "KnowledgePattern",
    # LLM Manager
    "UnifiedLLMManager",
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "TaskComplexity",
    "ModelSelection",
    # Collaboration
    "AgentTeam",
    "MessageType",
    "AgentMessage",
    "DelegationRequest",
    "AssistanceRequest",
    "KnowledgeShare",
    "CollaborationProtocol",
    "HandoffStrategy",
    "ConsensusStrategy",
    "HandoffProtocol",
    "ConsensusProtocol",
]
