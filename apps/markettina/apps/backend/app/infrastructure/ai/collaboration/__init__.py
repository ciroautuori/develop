"""Collaboration module for multi-agent communication and coordination."""

from .protocol import (
    CollaborationProtocol,
    ConsensusProtocol,
    ConsensusStrategy,
    HandoffProtocol,
    HandoffStrategy,
)
from .team import (
    AgentMessage,
    AgentTeam,
    AssistanceRequest,
    DelegationRequest,
    KnowledgeShare,
    MessageType,
)

__all__ = [
    "AgentMessage",
    "AgentTeam",
    "AssistanceRequest",
    "CollaborationProtocol",
    "ConsensusProtocol",
    "ConsensusStrategy",
    "DelegationRequest",
    "HandoffProtocol",
    "HandoffStrategy",
    "KnowledgeShare",
    "MessageType",
]
