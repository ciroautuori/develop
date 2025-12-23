"""Collaboration Protocols - Handoff and Consensus strategies."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HandoffStrategy(str, Enum):
    """Strategies for handing off tasks between agents."""
    IMMEDIATE = "immediate"  # Hand off immediately
    QUEUED = "queued"  # Queue for later handoff
    CONDITIONAL = "conditional"  # Hand off only if conditions met
    GRADUAL = "gradual"  # Gradual transition with overlap


class ConsensusStrategy(str, Enum):
    """Strategies for reaching consensus among agents."""
    MAJORITY = "majority"  # Simple majority vote
    UNANIMOUS = "unanimous"  # All must agree
    WEIGHTED = "weighted"  # Weighted by agent expertise
    LEADER = "leader"  # Leader makes final decision


@dataclass
class HandoffContext:
    """Context for a task handoff."""
    source_agent_id: str
    target_agent_id: str
    task_id: str
    task_state: Dict[str, Any]
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusVote:
    """A vote in a consensus process."""
    agent_id: str
    decision: str
    confidence: float
    reasoning: Optional[str] = None
    weight: float = 1.0


class CollaborationProtocol(ABC):
    """Abstract base class for collaboration protocols."""

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the protocol."""
        pass

    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> bool:
        """Validate that the protocol can be executed."""
        pass


class HandoffProtocol(CollaborationProtocol):
    """Protocol for handing off tasks between agents."""

    def __init__(
        self,
        strategy: HandoffStrategy = HandoffStrategy.IMMEDIATE,
        timeout_seconds: int = 300,
        require_acknowledgment: bool = True,
    ):
        self.strategy = strategy
        self.timeout_seconds = timeout_seconds
        self.require_acknowledgment = require_acknowledgment
        self.pending_handoffs: Dict[str, HandoffContext] = {}

    def validate(self, context: Dict[str, Any]) -> bool:
        """Validate handoff can proceed."""
        required_fields = ["source_agent_id", "target_agent_id", "task_id", "task_state"]
        return all(field in context for field in required_fields)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the handoff."""
        if not self.validate(context):
            return {"success": False, "error": "Invalid handoff context"}

        handoff = HandoffContext(
            source_agent_id=context["source_agent_id"],
            target_agent_id=context["target_agent_id"],
            task_id=context["task_id"],
            task_state=context["task_state"],
            reason=context.get("reason", "No reason provided"),
            metadata=context.get("metadata", {}),
        )

        if self.strategy == HandoffStrategy.IMMEDIATE:
            return self._immediate_handoff(handoff)
        elif self.strategy == HandoffStrategy.QUEUED:
            return self._queued_handoff(handoff)
        elif self.strategy == HandoffStrategy.CONDITIONAL:
            return self._conditional_handoff(handoff, context.get("conditions", {}))
        elif self.strategy == HandoffStrategy.GRADUAL:
            return self._gradual_handoff(handoff)
        else:
            return {"success": False, "error": f"Unknown strategy: {self.strategy}"}

    def _immediate_handoff(self, handoff: HandoffContext) -> Dict[str, Any]:
        """Perform immediate handoff."""
        logger.info(f"Immediate handoff: {handoff.source_agent_id} -> {handoff.target_agent_id}")
        return {
            "success": True,
            "handoff_id": f"ho_{handoff.task_id}_{datetime.utcnow().timestamp()}",
            "strategy": "immediate",
            "source": handoff.source_agent_id,
            "target": handoff.target_agent_id,
            "task_id": handoff.task_id,
        }

    def _queued_handoff(self, handoff: HandoffContext) -> Dict[str, Any]:
        """Queue handoff for later."""
        handoff_id = f"ho_{handoff.task_id}_{datetime.utcnow().timestamp()}"
        self.pending_handoffs[handoff_id] = handoff
        logger.info(f"Queued handoff: {handoff_id}")
        return {
            "success": True,
            "handoff_id": handoff_id,
            "strategy": "queued",
            "status": "pending",
        }

    def _conditional_handoff(
        self,
        handoff: HandoffContext,
        conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform conditional handoff."""
        # Simple condition check - can be extended
        conditions_met = all(
            handoff.task_state.get(k) == v
            for k, v in conditions.items()
        )

        if conditions_met:
            return self._immediate_handoff(handoff)
        else:
            return {
                "success": False,
                "error": "Conditions not met",
                "conditions": conditions,
            }

    def _gradual_handoff(self, handoff: HandoffContext) -> Dict[str, Any]:
        """Perform gradual handoff with overlap period."""
        handoff_id = f"ho_{handoff.task_id}_{datetime.utcnow().timestamp()}"
        self.pending_handoffs[handoff_id] = handoff
        logger.info(f"Gradual handoff initiated: {handoff_id}")
        return {
            "success": True,
            "handoff_id": handoff_id,
            "strategy": "gradual",
            "status": "transitioning",
            "overlap_period": self.timeout_seconds,
        }


class ConsensusProtocol(CollaborationProtocol):
    """Protocol for reaching consensus among agents."""

    def __init__(
        self,
        strategy: ConsensusStrategy = ConsensusStrategy.MAJORITY,
        min_participants: int = 2,
        timeout_seconds: int = 60,
    ):
        self.strategy = strategy
        self.min_participants = min_participants
        self.timeout_seconds = timeout_seconds
        self.active_votes: Dict[str, List[ConsensusVote]] = {}

    def validate(self, context: Dict[str, Any]) -> bool:
        """Validate consensus can proceed."""
        return "topic" in context and "options" in context

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute consensus process."""
        if not self.validate(context):
            return {"success": False, "error": "Invalid consensus context"}

        topic = context["topic"]
        votes = context.get("votes", [])

        if len(votes) < self.min_participants:
            return {
                "success": False,
                "error": f"Need at least {self.min_participants} votes",
                "current_votes": len(votes),
            }

        if self.strategy == ConsensusStrategy.MAJORITY:
            return self._majority_consensus(topic, votes)
        elif self.strategy == ConsensusStrategy.UNANIMOUS:
            return self._unanimous_consensus(topic, votes)
        elif self.strategy == ConsensusStrategy.WEIGHTED:
            return self._weighted_consensus(topic, votes)
        elif self.strategy == ConsensusStrategy.LEADER:
            leader_id = context.get("leader_id")
            return self._leader_consensus(topic, votes, leader_id)
        else:
            return {"success": False, "error": f"Unknown strategy: {self.strategy}"}

    def _majority_consensus(
        self,
        topic: str,
        votes: List[ConsensusVote]
    ) -> Dict[str, Any]:
        """Simple majority vote."""
        vote_counts: Dict[str, int] = {}
        for vote in votes:
            vote_counts[vote.decision] = vote_counts.get(vote.decision, 0) + 1

        winner = max(vote_counts, key=vote_counts.get)
        total = len(votes)

        return {
            "success": True,
            "topic": topic,
            "strategy": "majority",
            "decision": winner,
            "vote_count": vote_counts[winner],
            "total_votes": total,
            "percentage": vote_counts[winner] / total * 100,
        }

    def _unanimous_consensus(
        self,
        topic: str,
        votes: List[ConsensusVote]
    ) -> Dict[str, Any]:
        """Unanimous agreement required."""
        decisions = set(v.decision for v in votes)

        if len(decisions) == 1:
            return {
                "success": True,
                "topic": topic,
                "strategy": "unanimous",
                "decision": decisions.pop(),
                "total_votes": len(votes),
            }
        else:
            return {
                "success": False,
                "topic": topic,
                "strategy": "unanimous",
                "error": "No unanimous agreement",
                "decisions": list(decisions),
            }

    def _weighted_consensus(
        self,
        topic: str,
        votes: List[ConsensusVote]
    ) -> Dict[str, Any]:
        """Weighted vote by confidence and weight."""
        weighted_scores: Dict[str, float] = {}

        for vote in votes:
            score = vote.confidence * vote.weight
            weighted_scores[vote.decision] = weighted_scores.get(vote.decision, 0) + score

        winner = max(weighted_scores, key=weighted_scores.get)

        return {
            "success": True,
            "topic": topic,
            "strategy": "weighted",
            "decision": winner,
            "weighted_score": weighted_scores[winner],
            "all_scores": weighted_scores,
        }

    def _leader_consensus(
        self,
        topic: str,
        votes: List[ConsensusVote],
        leader_id: Optional[str]
    ) -> Dict[str, Any]:
        """Leader makes final decision."""
        if not leader_id:
            return {"success": False, "error": "No leader specified"}

        leader_vote = next((v for v in votes if v.agent_id == leader_id), None)

        if leader_vote:
            return {
                "success": True,
                "topic": topic,
                "strategy": "leader",
                "decision": leader_vote.decision,
                "leader_id": leader_id,
                "leader_confidence": leader_vote.confidence,
            }
        else:
            return {
                "success": False,
                "error": f"Leader {leader_id} did not vote",
            }
