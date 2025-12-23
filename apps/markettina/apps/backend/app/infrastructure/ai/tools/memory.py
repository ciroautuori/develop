"""Memory management for multi-agent conversations.

Provides conversation memory and context management for agents,
supporting short-term and long-term memory patterns.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in conversation memory.
    
    Attributes:
        role: Message role (user, assistant, system, tool)
        content: Message content
        name: Optional name (for tool/function messages)
        timestamp: Message timestamp
        metadata: Additional message metadata
    """

    role: str = Field(..., pattern="^(user|assistant|system|tool)$")
    content: str = Field(..., min_length=1)
    name: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMemory:
    """Manages conversation memory for agents.
    
    Provides short-term (recent messages) and long-term (summarized)
    memory capabilities with token budget management.
    
    Attributes:
        max_messages: Maximum messages to keep in short-term memory
        max_tokens: Maximum tokens for memory (approximate)
    """

    def __init__(
        self,
        max_messages: int = 100,
        max_tokens: int = 4000
    ) -> None:
        """Initialize agent memory.
        
        Args:
            max_messages: Maximum messages in short-term memory
            max_tokens: Maximum tokens for memory budget
        """
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self._messages: list[Message] = []
        self._summary: str | None = None

    def add_message(
        self,
        role: str,
        content: str,
        name: str | None = None,
        **metadata: Any
    ) -> None:
        """Add message to memory.
        
        Args:
            role: Message role
            content: Message content
            name: Optional name
            **metadata: Additional metadata
        """
        message = Message(
            role=role,
            content=content,
            name=name,
            metadata=metadata
        )
        self._messages.append(message)

        # Trim if exceeding max messages
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]

    def get_messages(
        self,
        limit: int | None = None,
        role: str | None = None
    ) -> list[dict[str, Any]]:
        """Get messages from memory.
        
        Args:
            limit: Maximum number of messages (most recent)
            role: Filter by role
            
        Returns:
            List of messages as dictionaries
        """
        messages = self._messages

        # Filter by role if specified
        if role:
            messages = [m for m in messages if m.role == role]

        # Apply limit
        if limit:
            messages = messages[-limit:]

        return [
            {
                "role": m.role,
                "content": m.content,
                **({"name": m.name} if m.name else {}),
            }
            for m in messages
        ]

    def get_context_window(
        self,
        max_tokens: int | None = None
    ) -> list[dict[str, Any]]:
        """Get messages that fit within token budget.
        
        Args:
            max_tokens: Token budget (uses default if not specified)
            
        Returns:
            Messages that fit within token budget
        """
        budget = max_tokens or self.max_tokens

        # Rough estimation: 4 chars per token
        context_messages = []
        current_tokens = 0

        # Add messages from most recent, working backwards
        for message in reversed(self._messages):
            # Estimate tokens
            msg_tokens = len(message.content) // 4

            if current_tokens + msg_tokens > budget:
                break

            context_messages.insert(0, {
                "role": message.role,
                "content": message.content,
                **({"name": message.name} if message.name else {}),
            })
            current_tokens += msg_tokens

        return context_messages

    def clear(self) -> None:
        """Clear all messages from memory."""
        self._messages.clear()
        self._summary = None

    def set_summary(self, summary: str) -> None:
        """Set conversation summary (for long-term memory).
        
        Args:
            summary: Conversation summary
        """
        self._summary = summary

    def get_summary(self) -> str | None:
        """Get conversation summary.
        
        Returns:
            Conversation summary or None
        """
        return self._summary

    @property
    def message_count(self) -> int:
        """Get total message count."""
        return len(self._messages)

    @property
    def estimated_tokens(self) -> int:
        """Get estimated token count (rough approximation)."""
        total_chars = sum(len(m.content) for m in self._messages)
        return total_chars // 4


class ConversationBuffer:
    """Buffer for managing multiple conversation memories.
    
    Useful for agents handling multiple conversations concurrently.
    """

    def __init__(
        self,
        max_conversations: int = 100,
        max_messages_per_conversation: int = 50
    ) -> None:
        """Initialize conversation buffer.
        
        Args:
            max_conversations: Maximum concurrent conversations
            max_messages_per_conversation: Max messages per conversation
        """
        self.max_conversations = max_conversations
        self.max_messages_per_conversation = max_messages_per_conversation
        self._conversations: dict[UUID, AgentMemory] = {}

    def get_memory(self, conversation_id: UUID) -> AgentMemory:
        """Get or create memory for conversation.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Agent memory for the conversation
        """
        if conversation_id not in self._conversations:
            # Create new memory
            if len(self._conversations) >= self.max_conversations:
                # Remove oldest conversation
                oldest_id = next(iter(self._conversations))
                del self._conversations[oldest_id]

            self._conversations[conversation_id] = AgentMemory(
                max_messages=self.max_messages_per_conversation
            )

        return self._conversations[conversation_id]

    def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete conversation memory.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            True if deleted, False if not found
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False

    def clear_all(self) -> None:
        """Clear all conversation memories."""
        self._conversations.clear()

    @property
    def conversation_count(self) -> int:
        """Get number of active conversations."""
        return len(self._conversations)
