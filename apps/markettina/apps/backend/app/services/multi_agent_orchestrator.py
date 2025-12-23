"""
🧠 Multi-Agent Orchestrator

Il cervello centrale che coordina TUTTI gli agenti AI di MARKETTINA.

Architettura:
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Content  │  │ Social   │  │ Campaign │  │ Performance  │    │
│  │ Creator  │──│ Manager  │──│ Manager  │──│ Analyzer     │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │
│        │              │             │              │            │
│        └──────────────┴─────────────┴──────────────┘            │
│                            │                                     │
│                    ┌───────────────┐                            │
│                    │ SHARED MEMORY │                            │
│                    │ (Context/State)│                            │
│                    └───────────────┘                            │
└─────────────────────────────────────────────────────────────────┘

Features:
- Shared memory tra agenti
- Pipeline di task
- Event-driven coordination
- Feedback loop integration
- Autonomous decision making
"""

import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, Coroutine

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


# =============================================================================
# MODELS
# =============================================================================

class AgentType(str, Enum):
    """Tipi di agenti disponibili."""
    CONTENT_CREATOR = "content_creator"
    SOCIAL_MANAGER = "social_manager"
    CAMPAIGN_MANAGER = "campaign_manager"
    PERFORMANCE_ANALYZER = "performance_analyzer"
    EMAIL_MARKETER = "email_marketer"
    SEO_SPECIALIST = "seo_specialist"


class TaskStatus(str, Enum):
    """Status di un task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_INPUT = "waiting_input"


class TaskPriority(str, Enum):
    """Priorità task."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentTask(BaseModel):
    """Task assegnato a un agente."""
    task_id: str
    agent_type: AgentType
    action: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL

    # Results
    output_data: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Dependencies
    depends_on: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)


class AgentMemoryEntry(BaseModel):
    """Entry nella memoria condivisa."""
    key: str
    value: Any
    agent_source: AgentType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)


class PipelineStep(BaseModel):
    """Step di una pipeline."""
    step_id: str
    agent_type: AgentType
    action: str
    input_mapping: dict[str, str] = Field(default_factory=dict)  # Maps from context
    output_key: Optional[str] = None  # Where to store output in context
    condition: Optional[str] = None  # Condition to execute


class Pipeline(BaseModel):
    """Pipeline di task multi-agente."""
    pipeline_id: str
    name: str
    description: str
    steps: list[PipelineStep]

    # Execution state
    current_step: int = 0
    status: TaskStatus = TaskStatus.PENDING
    context: dict[str, Any] = Field(default_factory=dict)

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class OrchestratorEvent(BaseModel):
    """Evento nell'orchestrator."""
    event_type: str
    agent_source: Optional[AgentType] = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# SHARED MEMORY
# =============================================================================

class SharedMemory:
    """
    Memoria condivisa tra tutti gli agenti.

    Permette agli agenti di:
    - Condividere contesto
    - Accedere a risultati di altri agenti
    - Memorizzare learnings
    """

    def __init__(self):
        self._store: dict[str, AgentMemoryEntry] = {}
        self._tags_index: dict[str, set[str]] = defaultdict(set)

    def set(
        self,
        key: str,
        value: Any,
        agent: AgentType,
        ttl_hours: Optional[int] = None,
        tags: list[str] = None
    ):
        """Store a value in shared memory."""
        expires_at = None
        if ttl_hours:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        entry = AgentMemoryEntry(
            key=key,
            value=value,
            agent_source=agent,
            expires_at=expires_at,
            tags=tags or []
        )

        self._store[key] = entry

        for tag in entry.tags:
            self._tags_index[tag].add(key)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from shared memory."""
        entry = self._store.get(key)
        if not entry:
            return None

        # Check expiration
        if entry.expires_at and datetime.utcnow() > entry.expires_at:
            del self._store[key]
            return None

        return entry.value

    def get_entry(self, key: str) -> Optional[AgentMemoryEntry]:
        """Get full entry with metadata."""
        return self._store.get(key)

    def get_by_tag(self, tag: str) -> list[AgentMemoryEntry]:
        """Get all entries with a specific tag."""
        keys = self._tags_index.get(tag, set())
        return [self._store[k] for k in keys if k in self._store]

    def get_by_agent(self, agent: AgentType) -> list[AgentMemoryEntry]:
        """Get all entries from a specific agent."""
        return [e for e in self._store.values() if e.agent_source == agent]

    def delete(self, key: str):
        """Delete a key from memory."""
        if key in self._store:
            del self._store[key]

    def cleanup_expired(self):
        """Remove expired entries."""
        now = datetime.utcnow()
        to_delete = [
            k for k, v in self._store.items()
            if v.expires_at and v.expires_at < now
        ]
        for k in to_delete:
            del self._store[k]

    def get_all_keys(self) -> list[str]:
        """Get all keys in memory."""
        return list(self._store.keys())

    def get_context_for_agent(self, agent: AgentType) -> dict[str, Any]:
        """Get relevant context for an agent."""
        context = {}

        # Get all non-expired entries
        for key, entry in self._store.items():
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                continue
            context[key] = entry.value

        return context


# =============================================================================
# AGENT REGISTRY
# =============================================================================

class AgentHandler:
    """Handler per un agente specifico."""

    def __init__(
        self,
        agent_type: AgentType,
        name: str,
        description: str,
        actions: dict[str, Callable]
    ):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.actions = actions
        self.is_active = True

    async def execute(self, action: str, input_data: dict, context: dict) -> dict:
        """Execute an action."""
        if action not in self.actions:
            raise ValueError(f"Unknown action: {action}")

        handler = self.actions[action]

        # Merge context with input
        full_input = {**context, **input_data}

        # Execute (support both sync and async)
        if asyncio.iscoroutinefunction(handler):
            return await handler(full_input)
        else:
            return handler(full_input)


# =============================================================================
# MULTI-AGENT ORCHESTRATOR
# =============================================================================

class MultiAgentOrchestrator:
    """
    Orchestratore centrale per tutti gli agenti AI.

    Responsabilità:
    - Coordinare task tra agenti
    - Gestire memoria condivisa
    - Eseguire pipeline multi-step
    - Event handling
    - Autonomous decision making
    """

    def __init__(self):
        self.memory = SharedMemory()
        self.agents: dict[AgentType, AgentHandler] = {}
        self.tasks: dict[str, AgentTask] = {}
        self.pipelines: dict[str, Pipeline] = {}
        self.event_handlers: dict[str, list[Callable]] = defaultdict(list)
        self._task_counter = 0
        self._pipeline_counter = 0

    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================

    def register_agent(self, handler: AgentHandler):
        """Registra un agente nell'orchestrator."""
        self.agents[handler.agent_type] = handler
        logger.info(
            "agent_registered",
            agent_type=handler.agent_type.value,
            name=handler.name,
            actions=list(handler.actions.keys())
        )

    def get_agent(self, agent_type: AgentType) -> Optional[AgentHandler]:
        """Ottiene un agente registrato."""
        return self.agents.get(agent_type)

    def list_agents(self) -> list[dict]:
        """Lista tutti gli agenti registrati."""
        return [
            {
                "type": a.agent_type.value,
                "name": a.name,
                "description": a.description,
                "actions": list(a.actions.keys()),
                "is_active": a.is_active
            }
            for a in self.agents.values()
        ]

    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================

    def create_task(
        self,
        agent_type: AgentType,
        action: str,
        input_data: dict = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        depends_on: list[str] = None
    ) -> AgentTask:
        """Crea un nuovo task."""
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        task = AgentTask(
            task_id=task_id,
            agent_type=agent_type,
            action=action,
            input_data=input_data or {},
            priority=priority,
            depends_on=depends_on or []
        )

        self.tasks[task_id] = task
        logger.info("task_created", task_id=task_id, agent=agent_type.value, action=action)

        return task

    async def execute_task(self, task_id: str) -> AgentTask:
        """Esegue un task."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        # Check dependencies
        for dep_id in task.depends_on:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                task.status = TaskStatus.WAITING_INPUT
                return task

        # Get agent
        agent = self.agents.get(task.agent_type)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"Agent not found: {task.agent_type}"
            return task

        # Execute
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

        try:
            context = self.memory.get_context_for_agent(task.agent_type)
            result = await agent.execute(task.action, task.input_data, context)

            task.output_data = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()

            # Store result in memory
            self.memory.set(
                f"task_result_{task_id}",
                result,
                task.agent_type,
                ttl_hours=24,
                tags=["task_result", task.action]
            )

            # Emit event
            await self._emit_event("task_completed", task.agent_type, {
                "task_id": task_id,
                "result": result
            })

            # Trigger dependent tasks
            for trigger_id in task.triggers:
                asyncio.create_task(self.execute_task(trigger_id))

            logger.info("task_completed", task_id=task_id)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            logger.error("task_failed", task_id=task_id, error=str(e))

            await self._emit_event("task_failed", task.agent_type, {
                "task_id": task_id,
                "error": str(e)
            })

        return task

    # =========================================================================
    # PIPELINE MANAGEMENT
    # =========================================================================

    def create_pipeline(
        self,
        name: str,
        description: str,
        steps: list[PipelineStep],
        initial_context: dict = None
    ) -> Pipeline:
        """Crea una nuova pipeline."""
        self._pipeline_counter += 1
        pipeline_id = f"pipeline_{self._pipeline_counter}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        pipeline = Pipeline(
            pipeline_id=pipeline_id,
            name=name,
            description=description,
            steps=steps,
            context=initial_context or {}
        )

        self.pipelines[pipeline_id] = pipeline
        logger.info("pipeline_created", pipeline_id=pipeline_id, name=name, steps=len(steps))

        return pipeline

    async def execute_pipeline(self, pipeline_id: str) -> Pipeline:
        """Esegue una pipeline step by step."""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        pipeline.status = TaskStatus.IN_PROGRESS
        pipeline.started_at = datetime.utcnow()

        logger.info("pipeline_started", pipeline_id=pipeline_id)

        try:
            for i, step in enumerate(pipeline.steps):
                pipeline.current_step = i

                # Check condition
                if step.condition and not self._evaluate_condition(step.condition, pipeline.context):
                    logger.info("step_skipped", step_id=step.step_id, reason="condition_false")
                    continue

                # Prepare input from context
                step_input = {}
                for key, context_key in step.input_mapping.items():
                    if context_key in pipeline.context:
                        step_input[key] = pipeline.context[context_key]

                # Create and execute task
                task = self.create_task(
                    agent_type=step.agent_type,
                    action=step.action,
                    input_data=step_input
                )

                result_task = await self.execute_task(task.task_id)

                if result_task.status == TaskStatus.FAILED:
                    pipeline.status = TaskStatus.FAILED
                    logger.error("pipeline_step_failed", step=step.step_id, error=result_task.error)
                    break

                # Store output in context
                if step.output_key and result_task.output_data:
                    pipeline.context[step.output_key] = result_task.output_data

                logger.info("pipeline_step_completed", step=step.step_id)

            if pipeline.status != TaskStatus.FAILED:
                pipeline.status = TaskStatus.COMPLETED

            pipeline.completed_at = datetime.utcnow()

        except Exception as e:
            pipeline.status = TaskStatus.FAILED
            pipeline.completed_at = datetime.utcnow()
            logger.error("pipeline_error", error=str(e))

        return pipeline

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        """Valuta una condizione semplice."""
        # Simple evaluation - in production use safer eval
        try:
            # Support simple conditions like "has_content == True"
            return eval(condition, {"__builtins__": {}}, context)
        except Exception:
            return True

    # =========================================================================
    # EVENT HANDLING
    # =========================================================================

    def on_event(self, event_type: str, handler: Callable):
        """Registra un handler per un tipo di evento."""
        self.event_handlers[event_type].append(handler)

    async def _emit_event(
        self,
        event_type: str,
        agent_source: Optional[AgentType],
        data: dict
    ):
        """Emette un evento."""
        event = OrchestratorEvent(
            event_type=event_type,
            agent_source=agent_source,
            data=data
        )

        for handler in self.event_handlers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.warning("event_handler_error", error=str(e))

    # =========================================================================
    # AUTONOMOUS WORKFLOWS
    # =========================================================================

    async def run_daily_content_workflow(self, brand_id: str = "default"):
        """
        Workflow autonomo giornaliero per content marketing.

        Pipeline:
        1. Analyze Performance → Ottieni insights
        2. Generate Content → Crea contenuto ottimizzato
        3. Schedule Posts → Pianifica pubblicazione
        4. Prepare Email → Prepara newsletter
        """
        steps = [
            PipelineStep(
                step_id="analyze_performance",
                agent_type=AgentType.PERFORMANCE_ANALYZER,
                action="analyze_recent",
                input_mapping={"brand_id": "brand_id"},
                output_key="performance_insights"
            ),
            PipelineStep(
                step_id="generate_content",
                agent_type=AgentType.CONTENT_CREATOR,
                action="generate_optimized",
                input_mapping={
                    "insights": "performance_insights",
                    "brand_id": "brand_id"
                },
                output_key="generated_content"
            ),
            PipelineStep(
                step_id="schedule_posts",
                agent_type=AgentType.SOCIAL_MANAGER,
                action="schedule",
                input_mapping={
                    "content": "generated_content",
                    "insights": "performance_insights"
                },
                output_key="scheduled_posts"
            ),
            PipelineStep(
                step_id="prepare_newsletter",
                agent_type=AgentType.EMAIL_MARKETER,
                action="create_digest",
                input_mapping={
                    "content": "generated_content"
                },
                output_key="newsletter",
                condition="len(generated_content.get('items', [])) > 0"
            )
        ]

        pipeline = self.create_pipeline(
            name="Daily Content Workflow",
            description="Workflow autonomo per content marketing giornaliero",
            steps=steps,
            initial_context={"brand_id": brand_id}
        )

        return await self.execute_pipeline(pipeline.pipeline_id)

    async def run_campaign_launch(self, campaign_config: dict):
        """
        Workflow per lancio campagna.

        Pipeline:
        1. Create Campaign Assets → Genera tutti i materiali
        2. Setup Social Posts → Prepara post per tutti i canali
        3. Setup Email Sequence → Prepara sequenza email
        4. Launch → Attiva tutto
        """
        steps = [
            PipelineStep(
                step_id="create_assets",
                agent_type=AgentType.CONTENT_CREATOR,
                action="create_campaign_assets",
                input_mapping={"campaign": "campaign_config"},
                output_key="campaign_assets"
            ),
            PipelineStep(
                step_id="setup_social",
                agent_type=AgentType.SOCIAL_MANAGER,
                action="create_campaign_posts",
                input_mapping={
                    "assets": "campaign_assets",
                    "campaign": "campaign_config"
                },
                output_key="social_posts"
            ),
            PipelineStep(
                step_id="setup_email",
                agent_type=AgentType.EMAIL_MARKETER,
                action="create_sequence",
                input_mapping={
                    "assets": "campaign_assets",
                    "campaign": "campaign_config"
                },
                output_key="email_sequence"
            ),
            PipelineStep(
                step_id="activate",
                agent_type=AgentType.CAMPAIGN_MANAGER,
                action="activate_campaign",
                input_mapping={
                    "social": "social_posts",
                    "email": "email_sequence",
                    "campaign": "campaign_config"
                },
                output_key="launch_result"
            )
        ]

        pipeline = self.create_pipeline(
            name="Campaign Launch",
            description="Lancio campagna multi-canale",
            steps=steps,
            initial_context={"campaign_config": campaign_config}
        )

        return await self.execute_pipeline(pipeline.pipeline_id)

    # =========================================================================
    # STATUS & MONITORING
    # =========================================================================

    def get_status(self) -> dict:
        """Ottiene status completo dell'orchestrator."""
        return {
            "agents": {
                agent_type.value: {
                    "name": handler.name,
                    "is_active": handler.is_active,
                    "actions": list(handler.actions.keys())
                }
                for agent_type, handler in self.agents.items()
            },
            "tasks": {
                "total": len(self.tasks),
                "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
                "in_progress": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
                "completed": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
                "failed": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
            },
            "pipelines": {
                "total": len(self.pipelines),
                "active": len([p for p in self.pipelines.values() if p.status == TaskStatus.IN_PROGRESS])
            },
            "memory": {
                "entries": len(self.memory._store)
            }
        }


# =============================================================================
# SINGLETON & INITIALIZATION
# =============================================================================

orchestrator = MultiAgentOrchestrator()


def _register_default_agents():
    """Registra gli agenti di default."""

    # Content Creator Agent
    async def content_generate(input_data: dict) -> dict:
        """Genera contenuto."""
        from app.services.ai_feedback_loop import get_optimized_prompt_for_platform

        topic = input_data.get("topic", "marketing")
        platform = input_data.get("platform", "instagram")

        # Get optimized prompt
        base_prompt = f"Create engaging content about {topic}"
        optimized = await get_optimized_prompt_for_platform(base_prompt, platform)

        return {
            "prompt": optimized,
            "topic": topic,
            "platform": platform,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def content_generate_optimized(input_data: dict) -> dict:
        """Genera contenuto ottimizzato basato su insights."""
        insights = input_data.get("insights", {})

        # Use insights to inform content
        best_topics = insights.get("best_topics", [])

        return {
            "items": [
                {"type": "post", "topic": t, "status": "ready"}
                for t in best_topics[:3]
            ],
            "optimized_by_insights": True
        }

    orchestrator.register_agent(AgentHandler(
        agent_type=AgentType.CONTENT_CREATOR,
        name="Content Creator",
        description="Genera contenuti ottimizzati per social media",
        actions={
            "generate": content_generate,
            "generate_optimized": content_generate_optimized,
            "create_campaign_assets": lambda x: {"assets": [], "status": "created"}
        }
    ))

    # Social Manager Agent
    orchestrator.register_agent(AgentHandler(
        agent_type=AgentType.SOCIAL_MANAGER,
        name="Social Manager",
        description="Gestisce pubblicazione e scheduling sui social",
        actions={
            "schedule": lambda x: {"scheduled": True, "count": len(x.get("content", {}).get("items", []))},
            "publish": lambda x: {"published": True},
            "create_campaign_posts": lambda x: {"posts": [], "status": "scheduled"}
        }
    ))

    # Campaign Manager Agent
    orchestrator.register_agent(AgentHandler(
        agent_type=AgentType.CAMPAIGN_MANAGER,
        name="Campaign Manager",
        description="Gestisce campagne marketing multi-canale",
        actions={
            "create": lambda x: {"campaign_id": "new_campaign"},
            "activate_campaign": lambda x: {"activated": True, "status": "live"},
            "analyze": lambda x: {"performance": {"score": 85}}
        }
    ))

    # Performance Analyzer Agent
    async def analyze_recent(input_data: dict) -> dict:
        """Analizza performance recente."""
        from app.services.ai_feedback_loop import feedback_loop, Platform

        try:
            signals = await feedback_loop.generate_learning_signals(Platform.INSTAGRAM)
            return {
                "best_hours": signals.best_hours,
                "best_days": signals.best_days,
                "optimal_caption_length": signals.optimal_caption_length,
                "best_topics": ["product", "lifestyle", "tips"],
                "confidence": signals.confidence_score
            }
        except Exception:
            return {"best_topics": ["marketing", "tips"], "confidence": 0.5}

    orchestrator.register_agent(AgentHandler(
        agent_type=AgentType.PERFORMANCE_ANALYZER,
        name="Performance Analyzer",
        description="Analizza performance e genera insights",
        actions={
            "analyze_recent": analyze_recent,
            "get_recommendations": lambda x: {"recommendations": []}
        }
    ))

    # Email Marketer Agent
    orchestrator.register_agent(AgentHandler(
        agent_type=AgentType.EMAIL_MARKETER,
        name="Email Marketer",
        description="Gestisce email marketing e newsletter",
        actions={
            "create_digest": lambda x: {"newsletter": {"status": "draft"}},
            "create_sequence": lambda x: {"sequence": [], "status": "ready"},
            "send": lambda x: {"sent": True}
        }
    ))

    # SEO Specialist Agent
    orchestrator.register_agent(AgentHandler(
        agent_type=AgentType.SEO_SPECIALIST,
        name="SEO Specialist",
        description="Ottimizza contenuti per SEO",
        actions={
            "optimize": lambda x: {"optimized": True, "keywords": []},
            "analyze_keywords": lambda x: {"keywords": [], "opportunities": []}
        }
    ))

    logger.info("default_agents_registered", count=len(orchestrator.agents))


# Initialize default agents
_register_default_agents()
