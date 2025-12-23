"""
Advanced Workflow System for Multi-Agent Orchestration.

Sistema di workflow avanzato per orchestrazione multi-agente con:
- Workflow templates predefiniti per marketing automation
- Pipeline builder dinamico
- Conditional branching
- Error handling e recovery
- Workflow persistence
- Real-time progress tracking

REFERENCE:
- Integra con AgentOrchestrator esistente
- Estende funzionalità per use case marketing complessi
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
import structlog

from .task import Task, TaskStatus, TaskPriority, WorkflowResult
from .base_agent import BaseAgent
from .orchestrator import AgentOrchestrator, OrchestrationStrategy

logger = structlog.get_logger(__name__)


# =============================================================================
# ENUMS
# =============================================================================


class WorkflowType(str, Enum):
    """Tipi di workflow predefiniti."""
    CONTENT_CAMPAIGN = "content_campaign"
    SOCIAL_BLAST = "social_blast"
    LEAD_NURTURING = "lead_nurturing"
    SEO_AUDIT = "seo_audit"
    EMAIL_SEQUENCE = "email_sequence"
    CUSTOM = "custom"


class StepType(str, Enum):
    """Tipi di step workflow."""
    AGENT_TASK = "agent_task"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    WAIT = "wait"
    HUMAN_APPROVAL = "human_approval"
    WEBHOOK = "webhook"


class WorkflowStatus(str, Enum):
    """Stato workflow."""
    DRAFT = "draft"
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================


class WorkflowStep(BaseModel):
    """Singolo step di workflow."""
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str
    step_type: StepType = StepType.AGENT_TASK
    agent_type: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_key: Optional[str] = None  # Key per salvare output in workflow context

    # Dependencies
    depends_on: List[str] = Field(default_factory=list)  # Step IDs

    # Conditional branching
    condition: Optional[str] = None  # Python expression
    on_success: Optional[str] = None  # Step ID
    on_failure: Optional[str] = None  # Step ID

    # Retry config
    max_retries: int = 3
    retry_delay: int = 5  # seconds

    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowDefinition(BaseModel):
    """Definizione workflow."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    workflow_type: WorkflowType = WorkflowType.CUSTOM

    # Steps
    steps: List[WorkflowStep] = Field(default_factory=list)

    # Configuration
    strategy: OrchestrationStrategy = OrchestrationStrategy.DEPENDENCY
    timeout_seconds: int = 3600  # 1 hour default

    # Input schema
    required_inputs: List[str] = Field(default_factory=list)
    default_inputs: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class WorkflowExecution(BaseModel):
    """Esecuzione workflow instance."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING

    # Execution context
    context: Dict[str, Any] = Field(default_factory=dict)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)

    # Steps tracking
    steps: List[WorkflowStep] = Field(default_factory=list)
    current_step_id: Optional[str] = None

    # Progress
    progress_percent: int = 0
    steps_completed: int = 0
    steps_total: int = 0

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Errors
    errors: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    created_by: Optional[str] = None

    class Config:
        use_enum_values = True


class WorkflowProgress(BaseModel):
    """Progresso workflow per UI."""
    execution_id: str
    workflow_name: str
    status: WorkflowStatus
    progress_percent: int
    current_step: Optional[str] = None
    steps_completed: int
    steps_total: int
    started_at: Optional[datetime] = None
    estimated_remaining: Optional[int] = None  # seconds
    errors_count: int = 0


# =============================================================================
# WORKFLOW TEMPLATES
# =============================================================================


class WorkflowTemplates:
    """Template workflow predefiniti per marketing."""

    @staticmethod
    def content_campaign_workflow() -> WorkflowDefinition:
        """
        Workflow completo per campagna content marketing.

        Steps:
        1. SEO: Analisi keywords
        2. Content: Generazione articolo
        3. Image: Generazione immagine
        4. Social: Creazione post per ogni piattaforma
        5. Email: Creazione newsletter
        6. Scheduling: Programmazione pubblicazione
        """
        return WorkflowDefinition(
            name="Content Marketing Campaign",
            description="Workflow completo per creare e distribuire contenuto su tutti i canali",
            workflow_type=WorkflowType.CONTENT_CAMPAIGN,
            required_inputs=["topic", "target_audience", "brand_voice"],
            steps=[
                WorkflowStep(
                    id="seo_analysis",
                    name="SEO Keyword Analysis",
                    step_type=StepType.AGENT_TASK,
                    agent_type="seo_specialist",
                    input_data={"task": "keyword_research", "topic": "{topic}"},
                    output_key="keywords"
                ),
                WorkflowStep(
                    id="content_creation",
                    name="Content Generation",
                    step_type=StepType.AGENT_TASK,
                    agent_type="content_creator",
                    depends_on=["seo_analysis"],
                    input_data={
                        "task": "create_article",
                        "topic": "{topic}",
                        "keywords": "{keywords}",
                        "target_audience": "{target_audience}",
                        "brand_voice": "{brand_voice}"
                    },
                    output_key="article"
                ),
                WorkflowStep(
                    id="image_generation",
                    name="Image Generation",
                    step_type=StepType.AGENT_TASK,
                    agent_type="image_generator",
                    depends_on=["content_creation"],
                    input_data={
                        "task": "generate_hero_image",
                        "article_title": "{article.title}",
                        "style": "professional"
                    },
                    output_key="hero_image"
                ),
                WorkflowStep(
                    id="social_posts",
                    name="Social Media Posts",
                    step_type=StepType.PARALLEL,
                    depends_on=["content_creation", "image_generation"]
                ),
                WorkflowStep(
                    id="instagram_post",
                    name="Instagram Post",
                    step_type=StepType.AGENT_TASK,
                    agent_type="social_media_manager",
                    depends_on=["social_posts"],
                    input_data={
                        "task": "create_post",
                        "platform": "instagram",
                        "article": "{article}",
                        "image": "{hero_image}"
                    },
                    output_key="instagram_content"
                ),
                WorkflowStep(
                    id="linkedin_post",
                    name="LinkedIn Post",
                    step_type=StepType.AGENT_TASK,
                    agent_type="social_media_manager",
                    depends_on=["social_posts"],
                    input_data={
                        "task": "create_post",
                        "platform": "linkedin",
                        "article": "{article}"
                    },
                    output_key="linkedin_content"
                ),
                WorkflowStep(
                    id="email_newsletter",
                    name="Email Newsletter",
                    step_type=StepType.AGENT_TASK,
                    agent_type="email_marketing",
                    depends_on=["content_creation"],
                    input_data={
                        "task": "create_newsletter",
                        "article": "{article}",
                        "target_audience": "{target_audience}"
                    },
                    output_key="newsletter"
                )
            ],
            tags=["marketing", "content", "automation"]
        )

    @staticmethod
    def social_blast_workflow() -> WorkflowDefinition:
        """
        Workflow per pubblicazione simultanea su tutti i social.

        Steps:
        1. Content optimization per piattaforma
        2. Image resize/adaptation
        3. Pubblicazione parallela
        4. Analytics collection
        """
        return WorkflowDefinition(
            name="Social Media Blast",
            description="Pubblica lo stesso contenuto su tutti i social contemporaneamente",
            workflow_type=WorkflowType.SOCIAL_BLAST,
            required_inputs=["message", "image_url"],
            steps=[
                WorkflowStep(
                    id="optimize_instagram",
                    name="Optimize for Instagram",
                    step_type=StepType.AGENT_TASK,
                    agent_type="social_media_manager",
                    input_data={
                        "task": "optimize_post",
                        "platform": "instagram",
                        "message": "{message}",
                        "image_url": "{image_url}"
                    },
                    output_key="instagram_post"
                ),
                WorkflowStep(
                    id="optimize_linkedin",
                    name="Optimize for LinkedIn",
                    step_type=StepType.AGENT_TASK,
                    agent_type="social_media_manager",
                    input_data={
                        "task": "optimize_post",
                        "platform": "linkedin",
                        "message": "{message}"
                    },
                    output_key="linkedin_post"
                ),
                WorkflowStep(
                    id="optimize_facebook",
                    name="Optimize for Facebook",
                    step_type=StepType.AGENT_TASK,
                    agent_type="social_media_manager",
                    input_data={
                        "task": "optimize_post",
                        "platform": "facebook",
                        "message": "{message}",
                        "image_url": "{image_url}"
                    },
                    output_key="facebook_post"
                ),
                WorkflowStep(
                    id="publish_all",
                    name="Publish All Posts",
                    step_type=StepType.PARALLEL,
                    depends_on=["optimize_instagram", "optimize_linkedin", "optimize_facebook"]
                ),
                WorkflowStep(
                    id="publish_instagram",
                    name="Publish to Instagram",
                    step_type=StepType.AGENT_TASK,
                    agent_type="social_media_manager",
                    depends_on=["publish_all"],
                    input_data={
                        "task": "publish",
                        "platform": "instagram",
                        "content": "{instagram_post}"
                    },
                    output_key="instagram_result"
                ),
                WorkflowStep(
                    id="publish_linkedin",
                    name="Publish to LinkedIn",
                    step_type=StepType.AGENT_TASK,
                    agent_type="social_media_manager",
                    depends_on=["publish_all"],
                    input_data={
                        "task": "publish",
                        "platform": "linkedin",
                        "content": "{linkedin_post}"
                    },
                    output_key="linkedin_result"
                )
            ],
            tags=["social", "publishing", "automation"]
        )

    @staticmethod
    def seo_audit_workflow() -> WorkflowDefinition:
        """
        Workflow per audit SEO completo.
        """
        return WorkflowDefinition(
            name="SEO Audit",
            description="Audit SEO completo con raccomandazioni actionable",
            workflow_type=WorkflowType.SEO_AUDIT,
            required_inputs=["website_url"],
            steps=[
                WorkflowStep(
                    id="technical_audit",
                    name="Technical SEO Audit",
                    step_type=StepType.AGENT_TASK,
                    agent_type="seo_specialist",
                    input_data={
                        "task": "technical_audit",
                        "url": "{website_url}"
                    },
                    output_key="technical_issues"
                ),
                WorkflowStep(
                    id="content_audit",
                    name="Content SEO Audit",
                    step_type=StepType.AGENT_TASK,
                    agent_type="seo_specialist",
                    input_data={
                        "task": "content_audit",
                        "url": "{website_url}"
                    },
                    output_key="content_issues"
                ),
                WorkflowStep(
                    id="competitor_analysis",
                    name="Competitor Analysis",
                    step_type=StepType.AGENT_TASK,
                    agent_type="seo_specialist",
                    input_data={
                        "task": "competitor_analysis",
                        "url": "{website_url}"
                    },
                    output_key="competitor_data"
                ),
                WorkflowStep(
                    id="generate_report",
                    name="Generate Report",
                    step_type=StepType.AGENT_TASK,
                    agent_type="content_creator",
                    depends_on=["technical_audit", "content_audit", "competitor_analysis"],
                    input_data={
                        "task": "create_seo_report",
                        "technical": "{technical_issues}",
                        "content": "{content_issues}",
                        "competitors": "{competitor_data}"
                    },
                    output_key="seo_report"
                )
            ],
            tags=["seo", "audit", "analysis"]
        )

    @staticmethod
    def lead_nurturing_workflow() -> WorkflowDefinition:
        """
        Workflow per lead nurturing automatico.
        """
        return WorkflowDefinition(
            name="Lead Nurturing Sequence",
            description="Sequenza automatica di nurturing per lead",
            workflow_type=WorkflowType.LEAD_NURTURING,
            required_inputs=["lead_id", "lead_stage"],
            steps=[
                WorkflowStep(
                    id="analyze_lead",
                    name="Analyze Lead",
                    step_type=StepType.AGENT_TASK,
                    agent_type="lead_intelligence",
                    input_data={
                        "task": "analyze_lead",
                        "lead_id": "{lead_id}"
                    },
                    output_key="lead_analysis"
                ),
                WorkflowStep(
                    id="personalize_content",
                    name="Personalize Content",
                    step_type=StepType.AGENT_TASK,
                    agent_type="content_creator",
                    depends_on=["analyze_lead"],
                    input_data={
                        "task": "personalize_for_lead",
                        "lead_analysis": "{lead_analysis}",
                        "stage": "{lead_stage}"
                    },
                    output_key="personalized_content"
                ),
                WorkflowStep(
                    id="create_email",
                    name="Create Nurturing Email",
                    step_type=StepType.AGENT_TASK,
                    agent_type="email_marketing",
                    depends_on=["personalize_content"],
                    input_data={
                        "task": "create_nurturing_email",
                        "content": "{personalized_content}",
                        "lead_analysis": "{lead_analysis}"
                    },
                    output_key="email"
                )
            ],
            tags=["lead", "nurturing", "email", "automation"]
        )

    @classmethod
    def get_all_templates(cls) -> Dict[str, WorkflowDefinition]:
        """Ottiene tutti i template disponibili."""
        return {
            WorkflowType.CONTENT_CAMPAIGN.value: cls.content_campaign_workflow(),
            WorkflowType.SOCIAL_BLAST.value: cls.social_blast_workflow(),
            WorkflowType.SEO_AUDIT.value: cls.seo_audit_workflow(),
            WorkflowType.LEAD_NURTURING.value: cls.lead_nurturing_workflow()
        }


# =============================================================================
# ADVANCED WORKFLOW ENGINE
# =============================================================================


class WorkflowEngine:
    """
    Engine avanzato per esecuzione workflow.

    Features:
    - Template management
    - Dynamic step execution
    - Context variable resolution
    - Conditional branching
    - Error recovery
    - Progress tracking
    - Persistence (in-memory per ora)

    Usage:
        engine = WorkflowEngine(orchestrator)

        # Da template
        execution = await engine.execute_from_template(
            WorkflowType.CONTENT_CAMPAIGN,
            inputs={"topic": "AI Marketing", "target_audience": "marketers"}
        )

        # Progress
        progress = engine.get_progress(execution.id)
    """

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._executions: Dict[str, WorkflowExecution] = {}
        self._templates = WorkflowTemplates.get_all_templates()

        # Load templates into workflows
        for template_type, template in self._templates.items():
            self._workflows[template.id] = template

    # =========================================================================
    # WORKFLOW MANAGEMENT
    # =========================================================================

    def register_workflow(self, workflow: WorkflowDefinition) -> str:
        """Registra un workflow custom."""
        self._workflows[workflow.id] = workflow
        logger.info("workflow_registered", workflow_id=workflow.id, name=workflow.name)
        return workflow.id

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Ottiene definizione workflow."""
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[WorkflowDefinition]:
        """Lista tutti i workflow disponibili."""
        return list(self._workflows.values())

    def get_template(self, workflow_type: WorkflowType) -> Optional[WorkflowDefinition]:
        """Ottiene template per tipo."""
        return self._templates.get(workflow_type.value)

    # =========================================================================
    # EXECUTION
    # =========================================================================

    async def execute_workflow(
        self,
        workflow_id: str,
        inputs: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> WorkflowExecution:
        """
        Esegue un workflow.

        Args:
            workflow_id: ID workflow
            inputs: Input iniziali
            created_by: Utente che ha avviato

        Returns:
            WorkflowExecution con stato e risultati
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        # Validate required inputs
        missing = [inp for inp in workflow.required_inputs if inp not in inputs]
        if missing:
            raise ValueError(f"Missing required inputs: {missing}")

        # Create execution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            inputs=inputs,
            context={**workflow.default_inputs, **inputs},
            steps=[step.model_copy(deep=True) for step in workflow.steps],
            steps_total=len(workflow.steps),
            created_by=created_by
        )

        self._executions[execution.id] = execution

        # Start execution in background
        asyncio.create_task(self._run_execution(execution))

        logger.info(
            "workflow_execution_started",
            execution_id=execution.id,
            workflow=workflow.name
        )

        return execution

    async def execute_from_template(
        self,
        workflow_type: WorkflowType,
        inputs: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> WorkflowExecution:
        """
        Esegue workflow da template predefinito.

        Args:
            workflow_type: Tipo template
            inputs: Input iniziali
            created_by: Utente

        Returns:
            WorkflowExecution
        """
        template = self.get_template(workflow_type)
        if not template:
            raise ValueError(f"Template not found: {workflow_type}")

        return await self.execute_workflow(
            workflow_id=template.id,
            inputs=inputs,
            created_by=created_by
        )

    async def _run_execution(self, execution: WorkflowExecution) -> None:
        """
        Esegue workflow steps.

        Gestisce:
        - Risoluzione variabili
        - Dependency tracking
        - Error handling
        - Progress updates
        """
        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.utcnow()

        try:
            completed_steps: Set[str] = set()
            step_map = {step.id: step for step in execution.steps}

            while len(completed_steps) < len(execution.steps):
                # Find ready steps
                ready_steps = [
                    step for step in execution.steps
                    if step.id not in completed_steps
                    and step.status != TaskStatus.FAILED
                    and all(dep in completed_steps for dep in step.depends_on)
                ]

                if not ready_steps:
                    # Check if we're stuck
                    pending = [s for s in execution.steps if s.id not in completed_steps]
                    if pending and all(s.status == TaskStatus.FAILED for s in pending):
                        break
                    if not pending:
                        break

                    # Wait a bit and retry
                    await asyncio.sleep(1)
                    continue

                # Execute ready steps (parallel where possible)
                parallel_steps = [s for s in ready_steps if s.step_type != StepType.PARALLEL]

                for step in parallel_steps:
                    execution.current_step_id = step.id

                    try:
                        await self._execute_step(execution, step)
                        completed_steps.add(step.id)
                        execution.steps_completed = len(completed_steps)
                        execution.progress_percent = int(
                            (execution.steps_completed / execution.steps_total) * 100
                        )
                    except Exception as e:
                        step.status = TaskStatus.FAILED
                        step.error = str(e)
                        execution.errors.append({
                            "step_id": step.id,
                            "error": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        })

                        # Check if we should continue
                        if step.on_failure:
                            # Branch to failure handler
                            pass
                        else:
                            completed_steps.add(step.id)

            # Determine final status
            failed_steps = [s for s in execution.steps if s.status == TaskStatus.FAILED]
            if failed_steps:
                execution.status = WorkflowStatus.FAILED
            else:
                execution.status = WorkflowStatus.COMPLETED
                execution.progress_percent = 100

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            logger.error("workflow_execution_failed", execution_id=execution.id, error=str(e))

        finally:
            execution.completed_at = datetime.utcnow()
            execution.current_step_id = None

            logger.info(
                "workflow_execution_completed",
                execution_id=execution.id,
                status=execution.status,
                duration=(execution.completed_at - execution.started_at).total_seconds()
            )

    async def _execute_step(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep
    ) -> None:
        """Esegue singolo step."""
        step.status = TaskStatus.IN_PROGRESS
        step.started_at = datetime.utcnow()

        if step.step_type == StepType.AGENT_TASK:
            await self._execute_agent_step(execution, step)
        elif step.step_type == StepType.PARALLEL:
            # Parallel è un marker, non esegue nulla
            step.status = TaskStatus.COMPLETED
        elif step.step_type == StepType.WAIT:
            await self._execute_wait_step(execution, step)
        elif step.step_type == StepType.CONDITIONAL:
            await self._execute_conditional_step(execution, step)
        else:
            step.status = TaskStatus.COMPLETED

        step.completed_at = datetime.utcnow()

    async def _execute_agent_step(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep
    ) -> None:
        """Esegue step con agent."""
        if not step.agent_type:
            raise ValueError(f"Step {step.id} missing agent_type")

        # Resolve variables in input_data
        resolved_input = self._resolve_variables(step.input_data, execution.context)

        # Create task
        task = Task(
            name=step.name,
            agent_type=step.agent_type,
            input_data=resolved_input,
            priority=TaskPriority.NORMAL
        )

        # Execute via orchestrator
        try:
            agent = self.orchestrator.get_agent(step.agent_type)
            result_task = await agent.run(task)

            step.result = result_task.output_data
            step.status = result_task.status

            # Store output in context
            if step.output_key and result_task.output_data:
                execution.context[step.output_key] = result_task.output_data
                execution.outputs[step.output_key] = result_task.output_data

        except Exception as e:
            step.status = TaskStatus.FAILED
            step.error = str(e)
            raise

    async def _execute_wait_step(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep
    ) -> None:
        """Esegue step wait."""
        wait_seconds = step.input_data.get("seconds", 0)
        await asyncio.sleep(wait_seconds)
        step.status = TaskStatus.COMPLETED

    async def _execute_conditional_step(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep
    ) -> None:
        """Esegue step condizionale."""
        if not step.condition:
            step.status = TaskStatus.COMPLETED
            return

        try:
            # Evaluate condition in context
            result = eval(step.condition, {"__builtins__": {}}, execution.context)
            step.result = {"condition_result": bool(result)}
            step.status = TaskStatus.COMPLETED
        except Exception as e:
            step.status = TaskStatus.FAILED
            step.error = f"Condition evaluation failed: {e}"
            raise

    def _resolve_variables(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Risolve variabili {var} nel contesto."""
        resolved = {}

        for key, value in data.items():
            if isinstance(value, str):
                resolved[key] = self._resolve_string(value, context)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_variables(value, context)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_string(v, context) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                resolved[key] = value

        return resolved

    def _resolve_string(self, value: str, context: Dict[str, Any]) -> Any:
        """Risolve singola stringa con variabili."""
        if not value.startswith("{") or not value.endswith("}"):
            return value

        var_path = value[1:-1]  # Remove { }

        # Support nested access: {article.title}
        parts = var_path.split(".")
        current = context

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part, value)
            else:
                return value

        return current

    # =========================================================================
    # STATUS & PROGRESS
    # =========================================================================

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Ottiene execution by ID."""
        return self._executions.get(execution_id)

    def get_progress(self, execution_id: str) -> Optional[WorkflowProgress]:
        """Ottiene progresso execution."""
        execution = self.get_execution(execution_id)
        if not execution:
            return None

        # Estimate remaining time
        estimated_remaining = None
        if execution.started_at and execution.status == WorkflowStatus.RUNNING:
            elapsed = (datetime.utcnow() - execution.started_at).total_seconds()
            if execution.steps_completed > 0:
                avg_per_step = elapsed / execution.steps_completed
                remaining_steps = execution.steps_total - execution.steps_completed
                estimated_remaining = int(avg_per_step * remaining_steps)

        # Get current step name
        current_step_name = None
        if execution.current_step_id:
            for step in execution.steps:
                if step.id == execution.current_step_id:
                    current_step_name = step.name
                    break

        return WorkflowProgress(
            execution_id=execution.id,
            workflow_name=execution.workflow_name,
            status=WorkflowStatus(execution.status),
            progress_percent=execution.progress_percent,
            current_step=current_step_name,
            steps_completed=execution.steps_completed,
            steps_total=execution.steps_total,
            started_at=execution.started_at,
            estimated_remaining=estimated_remaining,
            errors_count=len(execution.errors)
        )

    def list_executions(
        self,
        status: Optional[WorkflowStatus] = None,
        limit: int = 50
    ) -> List[WorkflowExecution]:
        """Lista executions con filtri."""
        executions = list(self._executions.values())

        if status:
            executions = [e for e in executions if e.status == status.value]

        # Sort by started_at desc
        executions.sort(key=lambda e: e.started_at or datetime.min, reverse=True)

        return executions[:limit]

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancella execution in corso."""
        execution = self.get_execution(execution_id)
        if not execution:
            return False

        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return False

        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.utcnow()

        logger.info("workflow_execution_cancelled", execution_id=execution_id)

        return True

    async def retry_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Riprova execution fallita."""
        old_execution = self.get_execution(execution_id)
        if not old_execution:
            return None

        if old_execution.status not in [WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return None

        # Create new execution with same inputs
        return await self.execute_workflow(
            workflow_id=old_execution.workflow_id,
            inputs=old_execution.inputs,
            created_by=old_execution.created_by
        )


# =============================================================================
# SINGLETON FACTORY
# =============================================================================


_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine(orchestrator: Optional[AgentOrchestrator] = None) -> WorkflowEngine:
    """Get singleton WorkflowEngine instance."""
    global _workflow_engine

    if _workflow_engine is None:
        if orchestrator is None:
            orchestrator = AgentOrchestrator()
        _workflow_engine = WorkflowEngine(orchestrator)

    return _workflow_engine
