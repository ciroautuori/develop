"""
Multi-Agent Orchestrator Router - API endpoints per orchestrazione AI.

Endpoints:
- GET  /status                       - Stato orchestrator
- GET  /agents                       - Lista agenti registrati
- GET  /agents/{agent_type}          - Info agente specifico
- POST /task                         - Esegui singolo task
- GET  /workflows                    - Lista workflow disponibili
- GET  /workflows/{workflow_id}      - Dettaglio workflow
- POST /workflows/{workflow_id}/execute - Esegui workflow
- GET  /templates                    - Template workflow predefiniti
- POST /templates/{type}/execute     - Esegui da template
- GET  /executions                   - Lista esecuzioni
- GET  /executions/{id}              - Dettaglio esecuzione
- GET  /executions/{id}/progress     - Progresso esecuzione
- POST /executions/{id}/cancel       - Cancella esecuzione
- POST /executions/{id}/retry        - Riprova esecuzione
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.api.dependencies.permissions import require_admin
from app.domain.auth.models import User

router = APIRouter(prefix="/ai/orchestrator", tags=["Multi-Agent Orchestrator"])


# =============================================================================
# MODELS
# =============================================================================


class TaskRequest(BaseModel):
    """Request per esecuzione task."""
    agent_type: str = Field(..., description="Tipo agente: content_creator, seo_specialist, etc.")
    task_name: str = Field(..., description="Nome task")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Dati input per il task")
    priority: str = Field(default="normal", description="Priorità: low, normal, high, urgent")


class TaskResponse(BaseModel):
    """Response task execution."""
    task_id: str
    agent_type: str
    status: str
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class AgentInfo(BaseModel):
    """Info agente."""
    agent_type: str
    name: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    status: str = "active"
    health: Dict[str, Any] = Field(default_factory=dict)


class WorkflowInfo(BaseModel):
    """Info workflow."""
    id: str
    name: str
    description: str
    workflow_type: str
    steps_count: int
    required_inputs: List[str]
    tags: List[str] = Field(default_factory=list)
    created_at: datetime


class WorkflowExecuteRequest(BaseModel):
    """Request per esecuzione workflow."""
    inputs: Dict[str, Any] = Field(..., description="Input richiesti dal workflow")


class ExecutionInfo(BaseModel):
    """Info esecuzione workflow."""
    id: str
    workflow_id: str
    workflow_name: str
    status: str
    progress_percent: int
    steps_completed: int
    steps_total: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    errors_count: int = 0


class ExecutionProgress(BaseModel):
    """Progresso esecuzione."""
    execution_id: str
    workflow_name: str
    status: str
    progress_percent: int
    current_step: Optional[str] = None
    steps_completed: int
    steps_total: int
    estimated_remaining_seconds: Optional[int] = None
    errors: List[Dict[str, Any]] = Field(default_factory=list)


class OrchestratorStatus(BaseModel):
    """Stato orchestrator."""
    available: bool = True
    agents_count: int = 0
    registered_agents: List[str] = Field(default_factory=list)
    workflows_count: int = 0
    active_executions: int = 0
    completed_executions: int = 0
    failed_executions: int = 0


class TemplateInfo(BaseModel):
    """Info template workflow."""
    type: str
    name: str
    description: str
    required_inputs: List[str]
    steps_count: int
    recommended_for: List[str] = Field(default_factory=list)


# =============================================================================
# IN-MEMORY STATE (in produzione, integrare con AI Microservice)
# =============================================================================

# Simulazione agenti disponibili
_AVAILABLE_AGENTS: Dict[str, AgentInfo] = {
    "content_creator": AgentInfo(
        agent_type="content_creator",
        name="Content Creator Agent",
        description="Genera contenuti testuali ottimizzati per marketing",
        capabilities=["article_creation", "blog_posts", "product_descriptions", "ad_copy"],
        status="active"
    ),
    "social_media_manager": AgentInfo(
        agent_type="social_media_manager",
        name="Social Media Manager Agent",
        description="Crea e ottimizza post per social media",
        capabilities=["post_creation", "hashtag_optimization", "scheduling", "multi_platform"],
        status="active"
    ),
    "seo_specialist": AgentInfo(
        agent_type="seo_specialist",
        name="SEO Specialist Agent",
        description="Ottimizzazione SEO e analisi keywords",
        capabilities=["keyword_research", "content_audit", "competitor_analysis", "technical_seo"],
        status="active"
    ),
    "email_marketing": AgentInfo(
        agent_type="email_marketing",
        name="Email Marketing Agent",
        description="Crea campagne email e newsletter",
        capabilities=["newsletter_creation", "email_sequences", "ab_testing", "personalization"],
        status="active"
    ),
    "image_generator": AgentInfo(
        agent_type="image_generator",
        name="Image Generator Agent",
        description="Genera immagini per marketing con AI",
        capabilities=["hero_images", "social_graphics", "product_photos", "brand_assets"],
        status="active"
    ),
    "lead_intelligence": AgentInfo(
        agent_type="lead_intelligence",
        name="Lead Intelligence Agent",
        description="Analisi e scoring lead",
        capabilities=["lead_scoring", "lead_enrichment", "segmentation", "intent_analysis"],
        status="active"
    ),
    "campaign_manager": AgentInfo(
        agent_type="campaign_manager",
        name="Campaign Manager Agent",
        description="Gestione campagne marketing end-to-end",
        capabilities=["campaign_planning", "budget_optimization", "performance_tracking", "reporting"],
        status="active"
    )
}

# Workflow templates
_WORKFLOW_TEMPLATES: Dict[str, TemplateInfo] = {
    "content_campaign": TemplateInfo(
        type="content_campaign",
        name="Content Marketing Campaign",
        description="Workflow completo per creare e distribuire contenuto su tutti i canali",
        required_inputs=["topic", "target_audience", "brand_voice"],
        steps_count=7,
        recommended_for=["blog_posts", "multi_channel", "brand_awareness"]
    ),
    "social_blast": TemplateInfo(
        type="social_blast",
        name="Social Media Blast",
        description="Pubblica lo stesso contenuto su tutti i social contemporaneamente",
        required_inputs=["message", "image_url"],
        steps_count=6,
        recommended_for=["announcements", "promotions", "viral_content"]
    ),
    "seo_audit": TemplateInfo(
        type="seo_audit",
        name="SEO Audit",
        description="Audit SEO completo con raccomandazioni actionable",
        required_inputs=["website_url"],
        steps_count=4,
        recommended_for=["website_optimization", "competitor_analysis", "content_strategy"]
    ),
    "lead_nurturing": TemplateInfo(
        type="lead_nurturing",
        name="Lead Nurturing Sequence",
        description="Sequenza automatica di nurturing per lead",
        required_inputs=["lead_id", "lead_stage"],
        steps_count=3,
        recommended_for=["lead_conversion", "email_automation", "personalization"]
    )
}

# In-memory executions tracking
_executions: Dict[str, ExecutionInfo] = {}


# =============================================================================
# STATUS ENDPOINT
# =============================================================================


@router.get("/status", response_model=OrchestratorStatus)
async def get_orchestrator_status(
    current_user: User = Depends(require_admin)
):
    """
    Stato Multi-Agent Orchestrator.

    Verifica disponibilità e statistiche generali.
    """
    # Count execution states
    active = sum(1 for e in _executions.values() if e.status in ["pending", "running"])
    completed = sum(1 for e in _executions.values() if e.status == "completed")
    failed = sum(1 for e in _executions.values() if e.status == "failed")

    return OrchestratorStatus(
        available=True,
        agents_count=len(_AVAILABLE_AGENTS),
        registered_agents=list(_AVAILABLE_AGENTS.keys()),
        workflows_count=len(_WORKFLOW_TEMPLATES),
        active_executions=active,
        completed_executions=completed,
        failed_executions=failed
    )


# =============================================================================
# AGENTS ENDPOINTS
# =============================================================================


@router.get("/agents", response_model=List[AgentInfo])
async def list_agents(
    current_user: User = Depends(require_admin)
):
    """
    Lista tutti gli agenti AI registrati.

    Ogni agente ha capabilities specifiche per task marketing.
    """
    return list(_AVAILABLE_AGENTS.values())


@router.get("/agents/{agent_type}", response_model=AgentInfo)
async def get_agent_info(
    agent_type: str,
    current_user: User = Depends(require_admin)
):
    """
    Dettagli agente specifico.

    Include capabilities e stato health.
    """
    if agent_type not in _AVAILABLE_AGENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent type '{agent_type}' not found. Available: {list(_AVAILABLE_AGENTS.keys())}"
        )

    return _AVAILABLE_AGENTS[agent_type]


# =============================================================================
# TASK EXECUTION
# =============================================================================


@router.post("/task", response_model=TaskResponse)
async def execute_task(
    request: TaskRequest,
    current_user: User = Depends(require_admin)
):
    """
    Esegue singolo task con agente specificato.

    **Esempio:**
    ```json
    {
        "agent_type": "content_creator",
        "task_name": "Create Blog Post",
        "input_data": {
            "topic": "AI in Marketing",
            "tone": "professional",
            "length": "medium"
        }
    }
    ```

    **Agenti disponibili:**
    - `content_creator`: Generazione contenuti
    - `social_media_manager`: Post social media
    - `seo_specialist`: Ottimizzazione SEO
    - `email_marketing`: Email e newsletter
    - `image_generator`: Generazione immagini
    - `lead_intelligence`: Analisi lead
    - `campaign_manager`: Gestione campagne
    """
    if request.agent_type not in _AVAILABLE_AGENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent type '{request.agent_type}' not found"
        )

    import uuid
    started_at = datetime.utcnow()

    # Simulated task execution
    # In produzione, questo chiamerebbe l'AI Microservice
    task_id = str(uuid.uuid4())

    # Simulate processing time based on agent type
    import asyncio
    await asyncio.sleep(0.5)  # Simulate async processing

    completed_at = datetime.utcnow()
    duration_ms = int((completed_at - started_at).total_seconds() * 1000)

    # Simulated output based on agent type
    output = _generate_simulated_output(request.agent_type, request.input_data)

    return TaskResponse(
        task_id=task_id,
        agent_type=request.agent_type,
        status="completed",
        output_data=output,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms
    )


def _generate_simulated_output(agent_type: str, input_data: Dict) -> Dict[str, Any]:
    """Genera output simulato per testing."""
    outputs = {
        "content_creator": {
            "title": f"Generated content for: {input_data.get('topic', 'topic')}",
            "content": "AI-generated marketing content...",
            "word_count": 500,
            "seo_score": 85
        },
        "social_media_manager": {
            "post_text": f"Engaging social post about {input_data.get('topic', 'topic')} 🚀",
            "hashtags": ["#marketing", "#ai", "#growth"],
            "best_time": "09:00 AM",
            "platforms": ["instagram", "linkedin", "twitter"]
        },
        "seo_specialist": {
            "keywords": ["primary keyword", "secondary keyword"],
            "difficulty_score": 45,
            "search_volume": 12000,
            "recommendations": ["Optimize title", "Add meta description"]
        },
        "email_marketing": {
            "subject": "Your personalized newsletter",
            "preview_text": "Don't miss these updates...",
            "body_html": "<p>Newsletter content...</p>",
            "estimated_open_rate": 25.5
        },
        "image_generator": {
            "image_url": "https://generated-images.example.com/img123.jpg",
            "thumbnail_url": "https://generated-images.example.com/img123_thumb.jpg",
            "dimensions": {"width": 1200, "height": 630},
            "style": "professional"
        },
        "lead_intelligence": {
            "lead_score": 78,
            "intent_signals": ["High engagement", "Multiple visits"],
            "recommended_action": "Schedule demo call",
            "segment": "enterprise"
        },
        "campaign_manager": {
            "campaign_plan": "Multi-channel campaign",
            "budget_allocation": {"social": 40, "email": 30, "ads": 30},
            "timeline": "4 weeks",
            "expected_roi": 2.5
        }
    }

    return outputs.get(agent_type, {"result": "Task completed"})


# =============================================================================
# TEMPLATES ENDPOINTS
# =============================================================================


@router.get("/templates", response_model=List[TemplateInfo])
async def list_workflow_templates(
    current_user: User = Depends(require_admin)
):
    """
    Lista template workflow predefiniti.

    Template pronti all'uso per casi marketing comuni.
    """
    return list(_WORKFLOW_TEMPLATES.values())


@router.get("/templates/{template_type}", response_model=TemplateInfo)
async def get_template_info(
    template_type: str,
    current_user: User = Depends(require_admin)
):
    """
    Dettaglio template workflow.

    Include input richiesti e steps.
    """
    if template_type not in _WORKFLOW_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_type}' not found. Available: {list(_WORKFLOW_TEMPLATES.keys())}"
        )

    return _WORKFLOW_TEMPLATES[template_type]


@router.post("/templates/{template_type}/execute", response_model=ExecutionInfo)
async def execute_template(
    template_type: str,
    request: WorkflowExecuteRequest,
    current_user: User = Depends(require_admin)
):
    """
    Esegue workflow da template predefinito.

    **Esempio Content Campaign:**
    ```json
    {
        "inputs": {
            "topic": "AI Marketing Automation",
            "target_audience": "B2B Marketers",
            "brand_voice": "Professional but friendly"
        }
    }
    ```

    **Esempio Social Blast:**
    ```json
    {
        "inputs": {
            "message": "Excited to announce our new product! 🎉",
            "image_url": "https://example.com/announcement.jpg"
        }
    }
    ```
    """
    if template_type not in _WORKFLOW_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_type}' not found"
        )

    template = _WORKFLOW_TEMPLATES[template_type]

    # Validate required inputs
    missing = [inp for inp in template.required_inputs if inp not in request.inputs]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required inputs: {missing}"
        )

    import uuid
    execution_id = str(uuid.uuid4())

    execution = ExecutionInfo(
        id=execution_id,
        workflow_id=template_type,
        workflow_name=template.name,
        status="running",
        progress_percent=0,
        steps_completed=0,
        steps_total=template.steps_count,
        started_at=datetime.utcnow()
    )

    _executions[execution_id] = execution

    # Start async execution (in produzione, invierebbe all'AI Microservice)
    import asyncio
    asyncio.create_task(_simulate_workflow_execution(execution_id, template.steps_count))

    return execution


async def _simulate_workflow_execution(execution_id: str, total_steps: int):
    """Simula esecuzione workflow per demo."""
    import asyncio

    if execution_id not in _executions:
        return

    execution = _executions[execution_id]

    for step in range(total_steps):
        await asyncio.sleep(2)  # Simulate step execution

        if execution_id not in _executions:
            return

        execution.steps_completed = step + 1
        execution.progress_percent = int(((step + 1) / total_steps) * 100)

    execution.status = "completed"
    execution.completed_at = datetime.utcnow()


# =============================================================================
# EXECUTIONS ENDPOINTS
# =============================================================================


@router.get("/executions", response_model=List[ExecutionInfo])
async def list_executions(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin)
):
    """
    Lista esecuzioni workflow.

    Filtrabile per stato: pending, running, completed, failed, cancelled
    """
    executions = list(_executions.values())

    if status_filter:
        executions = [e for e in executions if e.status == status_filter]

    # Sort by started_at desc
    executions.sort(
        key=lambda e: e.started_at or datetime.min,
        reverse=True
    )

    return executions[:limit]


@router.get("/executions/{execution_id}", response_model=ExecutionInfo)
async def get_execution(
    execution_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Dettaglio esecuzione workflow.
    """
    if execution_id not in _executions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution '{execution_id}' not found"
        )

    return _executions[execution_id]


@router.get("/executions/{execution_id}/progress", response_model=ExecutionProgress)
async def get_execution_progress(
    execution_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Progresso real-time esecuzione.

    Poll questo endpoint ogni 2-5 secondi durante l'esecuzione.
    """
    if execution_id not in _executions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution '{execution_id}' not found"
        )

    execution = _executions[execution_id]

    # Estimate remaining time
    estimated_remaining = None
    if execution.started_at and execution.status == "running" and execution.steps_completed > 0:
        elapsed = (datetime.utcnow() - execution.started_at).total_seconds()
        avg_per_step = elapsed / execution.steps_completed
        remaining_steps = execution.steps_total - execution.steps_completed
        estimated_remaining = int(avg_per_step * remaining_steps)

    return ExecutionProgress(
        execution_id=execution.id,
        workflow_name=execution.workflow_name,
        status=execution.status,
        progress_percent=execution.progress_percent,
        current_step=f"Step {execution.steps_completed + 1}" if execution.status == "running" else None,
        steps_completed=execution.steps_completed,
        steps_total=execution.steps_total,
        estimated_remaining_seconds=estimated_remaining,
        errors=[]
    )


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Cancella esecuzione in corso.
    """
    if execution_id not in _executions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution '{execution_id}' not found"
        )

    execution = _executions[execution_id]

    if execution.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel execution with status '{execution.status}'"
        )

    execution.status = "cancelled"
    execution.completed_at = datetime.utcnow()

    return {"success": True, "message": "Execution cancelled"}


@router.post("/executions/{execution_id}/retry", response_model=ExecutionInfo)
async def retry_execution(
    execution_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Riprova esecuzione fallita o cancellata.
    """
    if execution_id not in _executions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution '{execution_id}' not found"
        )

    old_execution = _executions[execution_id]

    if old_execution.status not in ["failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry execution with status '{old_execution.status}'"
        )

    # Get template info
    if old_execution.workflow_id not in _WORKFLOW_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original workflow template not found"
        )

    template = _WORKFLOW_TEMPLATES[old_execution.workflow_id]

    import uuid
    new_execution_id = str(uuid.uuid4())

    new_execution = ExecutionInfo(
        id=new_execution_id,
        workflow_id=old_execution.workflow_id,
        workflow_name=old_execution.workflow_name,
        status="running",
        progress_percent=0,
        steps_completed=0,
        steps_total=template.steps_count,
        started_at=datetime.utcnow()
    )

    _executions[new_execution_id] = new_execution

    import asyncio
    asyncio.create_task(_simulate_workflow_execution(new_execution_id, template.steps_count))

    return new_execution
