"""State management for multi-agent systems.

This module provides state persistence and management for agents,
including conversation state, execution context, and checkpointing.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Persistent state for an agent instance.
    
    Stores agent configuration, execution history, and runtime state
    that persists across invocations.
    
    Attributes:
        agent_id: Unique agent identifier
        agent_type: Type of agent
        state_data: Agent-specific state data
        config: Agent configuration
        last_updated: Last state update timestamp
        metadata: Additional metadata
    """
    
    agent_id: str = Field(..., min_length=1, max_length=200)
    agent_type: str = Field(..., min_length=1, max_length=100)
    state_data: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update state data.
        
        Args:
            data: New state data to merge
        """
        self.state_data.update(data)
        self.last_updated = datetime.utcnow()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value by key.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        return self.state_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set state value by key.
        
        Args:
            key: State key
            value: State value
        """
        self.state_data[key] = value
        self.last_updated = datetime.utcnow()
    
    def clear(self) -> None:
        """Clear all state data."""
        self.state_data.clear()
        self.last_updated = datetime.utcnow()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "agent_id": "marketing_content_creator_001",
                    "agent_type": "marketing_content_creator",
                    "state_data": {
                        "last_brand_voice": "professional",
                        "generated_count": 42
                    },
                    "config": {
                        "model": "gpt-4o",
                        "temperature": 0.7
                    }
                }
            ]
        }
    }


class ConversationState(BaseModel):
    """State for multi-turn conversations.
    
    Maintains conversation history and context for agents that
    interact in multiple turns with users or other agents.
    
    Attributes:
        conversation_id: Unique conversation identifier
        agent_id: Agent participating in conversation
        messages: Conversation messages
        context: Conversation context
        created_at: Conversation creation timestamp
        last_message_at: Last message timestamp
        metadata: Additional metadata
    """
    
    conversation_id: UUID = Field(default_factory=uuid4)
    agent_id: str = Field(..., min_length=1, max_length=200)
    messages: list[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_message(
        self,
        role: str,
        content: str,
        **kwargs: Any
    ) -> None:
        """Add message to conversation.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            **kwargs: Additional message metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.messages.append(message)
        self.last_message_at = datetime.utcnow()
    
    def get_history(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        """Get conversation history.
        
        Args:
            limit: Maximum number of messages to return (most recent)
            
        Returns:
            List of messages
        """
        if limit is None:
            return self.messages
        return self.messages[-limit:]
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.messages.clear()
        self.last_message_at = None
    
    @property
    def message_count(self) -> int:
        """Get total message count."""
        return len(self.messages)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "agent_id": "support_frontline_001",
                    "messages": [
                        {"role": "user", "content": "I need help with login"},
                        {"role": "assistant", "content": "I can help with that..."}
                    ],
                    "context": {
                        "user_id": "U123",
                        "session_id": "S456"
                    }
                }
            ]
        }
    }


class ExecutionCheckpoint(BaseModel):
    """Checkpoint for resumable execution.
    
    Allows long-running agent workflows to be paused and resumed
    by saving execution state at specific points.
    
    Attributes:
        checkpoint_id: Unique checkpoint identifier
        workflow_id: Associated workflow ID
        task_id: Associated task ID
        checkpoint_data: Checkpoint state data
        created_at: Checkpoint creation timestamp
        metadata: Additional metadata
    """
    
    checkpoint_id: UUID = Field(default_factory=uuid4)
    workflow_id: UUID
    task_id: Optional[UUID] = None
    checkpoint_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                    "checkpoint_data": {
                        "completed_steps": ["research", "outline"],
                        "current_step": "draft",
                        "partial_results": {"outline": "..."}
                    }
                }
            ]
        }
    }


class StateManager:
    """Manages agent state persistence and retrieval.
    
    Provides in-memory state management with support for
    external persistence backends (database, cache, etc.).
    """
    
    def __init__(self) -> None:
        """Initialize state manager."""
        self._agent_states: Dict[str, AgentState] = {}
        self._conversation_states: Dict[UUID, ConversationState] = {}
        self._checkpoints: Dict[UUID, ExecutionCheckpoint] = {}
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get agent state by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent state or None if not found
        """
        return self._agent_states.get(agent_id)
    
    def save_agent_state(self, state: AgentState) -> None:
        """Save agent state.
        
        Args:
            state: Agent state to save
        """
        self._agent_states[state.agent_id] = state
    
    def delete_agent_state(self, agent_id: str) -> bool:
        """Delete agent state.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if state was deleted, False if not found
        """
        if agent_id in self._agent_states:
            del self._agent_states[agent_id]
            return True
        return False
    
    def get_conversation_state(
        self,
        conversation_id: UUID
    ) -> Optional[ConversationState]:
        """Get conversation state by ID.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation state or None if not found
        """
        return self._conversation_states.get(conversation_id)
    
    def save_conversation_state(self, state: ConversationState) -> None:
        """Save conversation state.
        
        Args:
            state: Conversation state to save
        """
        self._conversation_states[state.conversation_id] = state
    
    def delete_conversation_state(self, conversation_id: UUID) -> bool:
        """Delete conversation state.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            True if state was deleted, False if not found
        """
        if conversation_id in self._conversation_states:
            del self._conversation_states[conversation_id]
            return True
        return False
    
    def save_checkpoint(self, checkpoint: ExecutionCheckpoint) -> None:
        """Save execution checkpoint.
        
        Args:
            checkpoint: Checkpoint to save
        """
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
    
    def get_checkpoint(self, checkpoint_id: UUID) -> Optional[ExecutionCheckpoint]:
        """Get execution checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Checkpoint or None if not found
        """
        return self._checkpoints.get(checkpoint_id)
    
    def get_workflow_checkpoints(
        self,
        workflow_id: UUID
    ) -> list[ExecutionCheckpoint]:
        """Get all checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of checkpoints for the workflow
        """
        return [
            cp for cp in self._checkpoints.values()
            if cp.workflow_id == workflow_id
        ]
    
    def clear_all(self) -> None:
        """Clear all stored states."""
        self._agent_states.clear()
        self._conversation_states.clear()
        self._checkpoints.clear()
