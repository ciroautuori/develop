"""
Cognitive Memory Architecture - Shared episodic memory system for agents.

Provides ChromaDB-based memory storage with semantic search,
pattern recognition, and experience consolidation.

Based on BFILT AUTOMATOR's Cognitive Memory Architecture (MCA).
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum
import chromadb
from chromadb.utils import embedding_functions


class MemoryType(str, Enum):
    """Type of memory entry."""
    EPISODIC = "episodic"  # Specific experiences/events
    SEMANTIC = "semantic"  # General knowledge/facts
    PROCEDURAL = "procedural"  # How-to knowledge/solutions
    ERROR = "error"  # Error experiences
    SUCCESS = "success"  # Successful outcomes


class MemoryEntry(BaseModel):
    """Individual memory entry."""

    id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None
    relevance_score: float = 0.0


class MemoryQuery(BaseModel):
    """Memory query parameters."""

    query_text: str
    memory_types: Optional[List[MemoryType]] = None
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    time_window: Optional[timedelta] = None
    max_results: int = 10
    min_relevance: float = 0.7


class MemorySearchResult(BaseModel):
    """Memory search result."""

    memories: List[MemoryEntry] = Field(default_factory=list)
    total_found: int = 0
    query_time: float = 0.0
    patterns: List[Dict[str, Any]] = Field(default_factory=list)


class KnowledgePattern(BaseModel):
    """Identified knowledge pattern."""

    pattern_type: str
    frequency: int
    contexts: List[str] = Field(default_factory=list)
    success_rate: float = 0.0
    last_seen: datetime = Field(default_factory=datetime.now)


class CognitiveMemorySystem:
    """
    Cognitive Memory Architecture for agents.

    Provides:
        - Episodic memory storage with ChromaDB
        - Semantic search across experiences
        - Pattern recognition and consolidation
        - Shared knowledge across agents
        - Experience-based learning

    Based on BFILT AUTOMATOR's Cognitive Memory Architecture (MCA).

    Example:
        >>> memory = CognitiveMemorySystem()
        >>> await memory.initialize()
        >>>
        >>> # Store experience
        >>> await memory.store_memory(
        ...     content="Fixed bug by adding null check",
        ...     memory_type=MemoryType.SUCCESS,
        ...     metadata={"error": "NullPointerException", "solution": "null_check"}
        ... )
        >>>
        >>> # Query similar experiences
        >>> results = await memory.query_memory(
        ...     query_text="How to fix NullPointerException?",
        ...     memory_types=[MemoryType.SUCCESS, MemoryType.PROCEDURAL]
        ... )
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "agent_memory",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Cognitive Memory System.

        Args:
            persist_directory: Directory for persistent storage
            collection_name: ChromaDB collection name
            embedding_model: Sentence transformer model name
        """
        import os
        # Use CHROMADB_PERSIST_DIR from env, fallback to parameter, then default
        chromadb_base = os.getenv("CHROMADB_PERSIST_DIR", "/data/chromadb")
        self.persist_directory = persist_directory or os.path.join(chromadb_base, "memory")
        self.collection_name = collection_name
        self.embedding_model = embedding_model

        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.Collection] = None
        self.embedding_fn: Optional[Any] = None

        # Pattern cache
        self._pattern_cache: Dict[str, KnowledgePattern] = {}
        self._cache_updated: datetime = datetime.now()

    async def initialize(self) -> bool:
        """
        Initialize ChromaDB client and collection.

        Returns:
            Success status
        """
        try:
            # Create persist directory
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

            # Initialize ChromaDB client with PersistentClient for data persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)

            # Create or get collection
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model
            )

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"description": "Agent cognitive memory storage"}
            )

            return True

        except Exception as e:
            print(f"Failed to initialize CognitiveMemorySystem: {e}")
            return False

    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> str:
        """
        Store memory entry.

        Args:
            content: Memory content text
            memory_type: Type of memory
            metadata: Additional metadata
            agent_id: Agent that created memory
            task_id: Associated task ID

        Returns:
            Memory entry ID
        """
        if not self.collection:
            raise RuntimeError("CognitiveMemorySystem not initialized")

        # Generate unique ID
        memory_id = f"{memory_type}_{datetime.now().isoformat()}_{hash(content) % 10000}"

        # Prepare metadata
        full_metadata = {
            "type": memory_type.value,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }

        if agent_id:
            full_metadata["agent_id"] = agent_id
        if task_id:
            full_metadata["task_id"] = task_id

        # Store in ChromaDB
        await asyncio.to_thread(
            self.collection.add,
            ids=[memory_id],
            documents=[content],
            metadatas=[full_metadata]
        )

        return memory_id

    async def query_memory(
        self,
        query_text: str,
        memory_types: Optional[List[MemoryType]] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        time_window: Optional[timedelta] = None,
        max_results: int = 10,
        min_relevance: float = 0.7
    ) -> MemorySearchResult:
        """
        Query memories with semantic search.

        Args:
            query_text: Query text for semantic search
            memory_types: Filter by memory types
            agent_id: Filter by agent ID
            task_id: Filter by task ID
            time_window: Filter by time window
            max_results: Maximum results to return
            min_relevance: Minimum relevance score (0-1)

        Returns:
            MemorySearchResult with matching memories
        """
        if not self.collection:
            raise RuntimeError("CognitiveMemorySystem not initialized")

        start_time = datetime.now()

        # Build filter
        where_filter = {}

        if memory_types:
            where_filter["type"] = {"$in": [mt.value for mt in memory_types]}

        if agent_id:
            where_filter["agent_id"] = agent_id

        if task_id:
            where_filter["task_id"] = task_id

        if time_window:
            cutoff_time = datetime.now() - time_window
            where_filter["timestamp"] = {"$gte": cutoff_time.isoformat()}

        # Query ChromaDB
        results = await asyncio.to_thread(
            self.collection.query,
            query_texts=[query_text],
            n_results=max_results,
            where=where_filter if where_filter else None
        )

        # Parse results
        memories = []

        if results and results["ids"] and len(results["ids"]) > 0:
            for i, memory_id in enumerate(results["ids"][0]):
                # Calculate relevance score from distance
                # ChromaDB returns distances, lower is better
                distance = results["distances"][0][i] if results["distances"] else 1.0
                relevance = 1.0 - min(distance, 1.0)

                if relevance < min_relevance:
                    continue

                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""

                memory = MemoryEntry(
                    id=memory_id,
                    type=MemoryType(metadata.get("type", "episodic")),
                    content=document,
                    metadata=metadata,
                    agent_id=metadata.get("agent_id"),
                    task_id=metadata.get("task_id"),
                    timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
                    relevance_score=relevance
                )

                memories.append(memory)

        query_time = (datetime.now() - start_time).total_seconds()

        # Identify patterns
        patterns = await self._identify_patterns(memories)

        return MemorySearchResult(
            memories=memories,
            total_found=len(memories),
            query_time=query_time,
            patterns=patterns
        )

    async def consolidate_knowledge(
        self,
        time_window: Optional[timedelta] = None,
        min_frequency: int = 3
    ) -> List[KnowledgePattern]:
        """
        Consolidate memories into knowledge patterns.

        Analyzes memories to identify:
            - Recurring problems and solutions
            - Success patterns
            - Common errors and fixes
            - Effective strategies

        Args:
            time_window: Time window for analysis
            min_frequency: Minimum occurrences to be a pattern

        Returns:
            List of identified patterns
        """
        if not self.collection:
            raise RuntimeError("CognitiveMemorySystem not initialized")

        # Get all memories in time window
        where_filter = {}
        if time_window:
            cutoff_time = datetime.now() - time_window
            where_filter["timestamp"] = {"$gte": cutoff_time.isoformat()}

        # Get all memories (up to 1000)
        results = await asyncio.to_thread(
            self.collection.get,
            where=where_filter if where_filter else None,
            limit=1000
        )

        if not results or not results["ids"]:
            return []

        # Analyze memories for patterns
        patterns_dict: Dict[str, KnowledgePattern] = {}

        for i, memory_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i] if results["metadatas"] else {}

            # Extract pattern key (e.g., error type, solution type)
            pattern_key = self._extract_pattern_key(metadata)

            if pattern_key not in patterns_dict:
                patterns_dict[pattern_key] = KnowledgePattern(
                    pattern_type=pattern_key,
                    frequency=1,
                    contexts=[memory_id],
                    success_rate=0.0,
                    last_seen=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat()))
                )
            else:
                pattern = patterns_dict[pattern_key]
                pattern.frequency += 1
                pattern.contexts.append(memory_id)

                # Update last seen
                timestamp = datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat()))
                if timestamp > pattern.last_seen:
                    pattern.last_seen = timestamp

        # Filter by minimum frequency
        patterns = [
            p for p in patterns_dict.values()
            if p.frequency >= min_frequency
        ]

        # Calculate success rates
        for pattern in patterns:
            success_count = sum(
                1 for ctx in pattern.contexts
                if self._is_successful_memory(ctx, results)
            )
            pattern.success_rate = success_count / len(pattern.contexts) if pattern.contexts else 0.0

        # Sort by frequency
        patterns.sort(key=lambda p: p.frequency, reverse=True)

        # Update cache
        self._pattern_cache = {p.pattern_type: p for p in patterns}
        self._cache_updated = datetime.now()

        return patterns

    async def get_similar_solutions(
        self,
        problem_description: str,
        max_results: int = 5
    ) -> List[MemoryEntry]:
        """
        Find similar successful solutions.

        Args:
            problem_description: Description of current problem
            max_results: Maximum solutions to return

        Returns:
            List of similar successful memory entries
        """
        result = await self.query_memory(
            query_text=problem_description,
            memory_types=[MemoryType.SUCCESS, MemoryType.PROCEDURAL],
            max_results=max_results,
            min_relevance=0.6
        )

        return result.memories

    async def _identify_patterns(
        self,
        memories: List[MemoryEntry]
    ) -> List[Dict[str, Any]]:
        """Identify patterns in memory set."""
        patterns = []

        # Group by metadata keys
        metadata_groups: Dict[str, List[MemoryEntry]] = {}

        for memory in memories:
            for key in memory.metadata:
                if key not in ["timestamp", "agent_id", "task_id"]:
                    group_key = f"{key}={memory.metadata[key]}"
                    if group_key not in metadata_groups:
                        metadata_groups[group_key] = []
                    metadata_groups[group_key].append(memory)

        # Find frequent patterns
        for group_key, group_memories in metadata_groups.items():
            if len(group_memories) >= 2:  # At least 2 occurrences
                patterns.append({
                    "pattern": group_key,
                    "frequency": len(group_memories),
                    "avg_relevance": sum(m.relevance_score for m in group_memories) / len(group_memories)
                })

        return patterns

    def _extract_pattern_key(self, metadata: Dict[str, Any]) -> str:
        """Extract pattern key from metadata."""
        # Prioritize error/solution/problem keys
        if "error" in metadata:
            return f"error:{metadata['error']}"
        if "solution" in metadata:
            return f"solution:{metadata['solution']}"
        if "problem" in metadata:
            return f"problem:{metadata['problem']}"
        if "type" in metadata:
            return f"type:{metadata['type']}"

        return "generic"

    def _is_successful_memory(
        self,
        memory_id: str,
        results: Dict[str, Any]
    ) -> bool:
        """Check if memory represents a success."""
        try:
            idx = results["ids"].index(memory_id)
            metadata = results["metadatas"][idx]
            return metadata.get("type") == MemoryType.SUCCESS.value
        except (ValueError, IndexError, KeyError):
            return False

    async def clear_memories(
        self,
        memory_types: Optional[List[MemoryType]] = None,
        older_than: Optional[timedelta] = None
    ) -> int:
        """
        Clear memories by type or age.

        Args:
            memory_types: Types to clear (all if None)
            older_than: Clear memories older than this

        Returns:
            Number of memories cleared
        """
        if not self.collection:
            raise RuntimeError("CognitiveMemorySystem not initialized")

        # Build filter
        where_filter = {}

        if memory_types:
            where_filter["type"] = {"$in": [mt.value for mt in memory_types]}

        if older_than:
            cutoff_time = datetime.now() - older_than
            where_filter["timestamp"] = {"$lt": cutoff_time.isoformat()}

        # Get IDs to delete
        results = await asyncio.to_thread(
            self.collection.get,
            where=where_filter if where_filter else None
        )

        if not results or not results["ids"]:
            return 0

        # Delete memories
        await asyncio.to_thread(
            self.collection.delete,
            ids=results["ids"]
        )

        return len(results["ids"])

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.

        Returns:
            Statistics dictionary
        """
        if not self.collection:
            return {"error": "Not initialized"}

        # Get all memories
        results = await asyncio.to_thread(
            self.collection.get
        )

        total_memories = len(results["ids"]) if results and results["ids"] else 0

        # Count by type
        type_counts = {}
        if results and results["metadatas"]:
            for metadata in results["metadatas"]:
                mem_type = metadata.get("type", "unknown")
                type_counts[mem_type] = type_counts.get(mem_type, 0) + 1

        return {
            "total_memories": total_memories,
            "by_type": type_counts,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory,
            "patterns_cached": len(self._pattern_cache),
            "cache_updated": self._cache_updated.isoformat()
        }
