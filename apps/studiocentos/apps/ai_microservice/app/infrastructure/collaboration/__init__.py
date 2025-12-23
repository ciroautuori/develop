"""Collaboration module for multi-agent communication and coordination."""

from .team import (
    AgentTeam,
    MessageType,
    AgentMessage,
    DelegationRequest,
    AssistanceRequest,
    KnowledgeShare,
)
from .protocol import (
    CollaborationProtocol,
    HandoffStrategy,
    ConsensusStrategy,
    HandoffProtocol,
    ConsensusProtocol,
)

__all__ = [
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
