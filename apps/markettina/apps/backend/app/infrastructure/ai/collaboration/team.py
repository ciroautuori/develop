"""Agent Team - Multi-agent collaboration and communication."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages agents can exchange."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    DELEGATION = "delegation"
    ASSISTANCE = "assistance"
    KNOWLEDGE_SHARE = "knowledge_share"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    HANDOFF = "handoff"


@dataclass
class AgentMessage:
    """Message exchanged between agents."""
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str | None = None
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "priority": self.priority,
        }


@dataclass
class DelegationRequest:
    """Request to delegate a task to another agent."""
    task_id: str
    task_type: str
    task_data: dict[str, Any]
    delegator_id: str
    target_agent_id: str | None = None
    required_capabilities: list[str] = field(default_factory=list)
    deadline: datetime | None = None
    priority: int = 0


@dataclass
class AssistanceRequest:
    """Request for assistance from another agent."""
    requester_id: str
    task_id: str
    problem_description: str
    context: dict[str, Any] = field(default_factory=dict)
    required_expertise: list[str] = field(default_factory=list)


@dataclass
class KnowledgeShare:
    """Knowledge shared between agents."""
    source_agent_id: str
    knowledge_type: str
    content: dict[str, Any]
    relevance_tags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AgentTeam:
    """Manages a team of collaborating agents."""

    def __init__(self, team_id: str, name: str = "Default Team"):
        self.team_id = team_id
        self.name = name
        self.agents: dict[str, Any] = {}
        self.message_queue: list[AgentMessage] = []
        self.shared_knowledge: list[KnowledgeShare] = []
        self.active_delegations: dict[str, DelegationRequest] = {}

    def register_agent(self, agent_id: str, agent: Any, capabilities: list[str] = None):
        """Register an agent with the team."""
        self.agents[agent_id] = {
            "agent": agent,
            "capabilities": capabilities or [],
            "status": "active",
            "registered_at": datetime.utcnow(),
        }
        logger.info(f"Agent {agent_id} registered with team {self.team_id}")

    def unregister_agent(self, agent_id: str):
        """Remove an agent from the team."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered from team {self.team_id}")

    def get_agent(self, agent_id: str) -> Any | None:
        """Get an agent by ID."""
        agent_info = self.agents.get(agent_id)
        return agent_info["agent"] if agent_info else None

    def find_agent_by_capability(self, capability: str) -> str | None:
        """Find an agent with a specific capability."""
        for agent_id, info in self.agents.items():
            if capability in info.get("capabilities", []):
                return agent_id
        return None

    def send_message(self, message: AgentMessage):
        """Send a message to another agent."""
        self.message_queue.append(message)
        logger.debug(f"Message queued: {message.sender_id} -> {message.receiver_id}")

    def get_messages(self, agent_id: str) -> list[AgentMessage]:
        """Get all pending messages for an agent."""
        messages = [m for m in self.message_queue if m.receiver_id == agent_id]
        self.message_queue = [m for m in self.message_queue if m.receiver_id != agent_id]
        return messages

    def delegate_task(self, request: DelegationRequest) -> bool:
        """Delegate a task to another agent."""
        target_id = request.target_agent_id

        # Find suitable agent if not specified
        if not target_id and request.required_capabilities:
            for cap in request.required_capabilities:
                target_id = self.find_agent_by_capability(cap)
                if target_id:
                    break

        if not target_id:
            logger.warning(f"No suitable agent found for delegation: {request.task_id}")
            return False

        self.active_delegations[request.task_id] = request

        # Send delegation message
        message = AgentMessage(
            sender_id=request.delegator_id,
            receiver_id=target_id,
            message_type=MessageType.DELEGATION,
            content={
                "task_id": request.task_id,
                "task_type": request.task_type,
                "task_data": request.task_data,
            },
            priority=request.priority,
        )
        self.send_message(message)

        logger.info(f"Task {request.task_id} delegated to {target_id}")
        return True

    def share_knowledge(self, knowledge: KnowledgeShare):
        """Share knowledge with the team."""
        self.shared_knowledge.append(knowledge)
        logger.debug(f"Knowledge shared by {knowledge.source_agent_id}: {knowledge.knowledge_type}")

    def query_knowledge(
        self,
        knowledge_type: str | None = None,
        tags: list[str] | None = None,
        min_confidence: float = 0.0
    ) -> list[KnowledgeShare]:
        """Query shared knowledge."""
        results = []

        for k in self.shared_knowledge:
            if knowledge_type and k.knowledge_type != knowledge_type:
                continue
            if k.confidence < min_confidence:
                continue
            if tags and not any(t in k.relevance_tags for t in tags):
                continue
            results.append(k)

        return results

    def get_team_status(self) -> dict[str, Any]:
        """Get current team status."""
        return {
            "team_id": self.team_id,
            "name": self.name,
            "agent_count": len(self.agents),
            "agents": {
                agent_id: {
                    "capabilities": info["capabilities"],
                    "status": info["status"],
                }
                for agent_id, info in self.agents.items()
            },
            "pending_messages": len(self.message_queue),
            "active_delegations": len(self.active_delegations),
            "shared_knowledge_count": len(self.shared_knowledge),
        }
