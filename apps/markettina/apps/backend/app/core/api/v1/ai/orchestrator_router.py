"""
🎯 Multi-Agent Orchestrator Router

API per controllare e monitorare l'orchestrator multi-agente.

Endpoints:
- GET /status - Status completo
- GET /agents - Lista agenti
- POST /tasks - Crea task
- POST /pipelines - Crea ed esegui pipeline
- POST /workflows/* - Workflow predefiniti
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.multi_agent_orchestrator import (
    orchestrator,
    AgentType,
    AgentTask,
    Pipeline,
    PipelineStep,
    TaskPriority,
    TaskStatus,
)

router = APIRouter(prefix="/orchestrator", tags=["multi-agent-orchestrator"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class CreateTaskRequest(BaseModel):
    """Request per creare un task."""
    agent_type: AgentType
    action: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    execute_immediately: bool = True


class CreatePipelineRequest(BaseModel):
    """Request per creare una pipeline."""
    name: str
    description: str
    steps: list[dict[str, Any]]
    initial_context: dict[str, Any] = Field(default_factory=dict)
    execute_immediately: bool = True


class CampaignLaunchRequest(BaseModel):
    """Request per lancio campagna."""
    campaign_name: str
    target_platforms: list[str] = Field(default_factory=lambda: ["instagram", "facebook", "linkedin"])
    content_themes: list[str] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None


class OrchestratorStatusResponse(BaseModel):
    """Status dell'orchestrator."""
    agents: dict[str, dict]
    tasks: dict[str, int]
    pipelines: dict[str, int]
    memory: dict[str, int]


# =============================================================================
# STATUS ENDPOINTS
# =============================================================================

@router.get("/status", response_model=OrchestratorStatusResponse)
async def get_orchestrator_status():
    """
    Ottiene lo status completo dell'orchestrator.

    Mostra:
    - Agenti registrati
    - Task in corso
    - Pipeline attive
    - Memoria condivisa
    """
    return orchestrator.get_status()


@router.get("/agents")
async def list_agents():
    """
    Lista tutti gli agenti registrati.
    """
    return {
        "agents": orchestrator.list_agents(),
        "count": len(orchestrator.agents)
    }


@router.get("/agents/{agent_type}")
async def get_agent_details(agent_type: AgentType):
    """
    Ottiene dettagli di un agente specifico.
    """
    agent = orchestrator.get_agent(agent_type)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent not found: {agent_type}"
        )

    return {
        "type": agent.agent_type.value,
        "name": agent.name,
        "description": agent.description,
        "actions": list(agent.actions.keys()),
        "is_active": agent.is_active
    }


# =============================================================================
# TASK ENDPOINTS
# =============================================================================

@router.post("/tasks")
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks
):
    """
    Crea e opzionalmente esegue un task.
    """
    task = orchestrator.create_task(
        agent_type=request.agent_type,
        action=request.action,
        input_data=request.input_data,
        priority=request.priority
    )

    if request.execute_immediately:
        result = await orchestrator.execute_task(task.task_id)
        return {
            "task_id": result.task_id,
            "status": result.status.value,
            "output": result.output_data,
            "error": result.error
        }

    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "message": "Task created. Use /tasks/{task_id}/execute to run."
    }


@router.get("/tasks")
async def list_tasks(
    status: Optional[TaskStatus] = None,
    limit: int = 50
):
    """
    Lista task recenti.
    """
    tasks = list(orchestrator.tasks.values())

    if status:
        tasks = [t for t in tasks if t.status == status]

    tasks.sort(key=lambda x: x.created_at, reverse=True)
    tasks = tasks[:limit]

    return {
        "count": len(tasks),
        "tasks": [
            {
                "task_id": t.task_id,
                "agent": t.agent_type.value,
                "action": t.action,
                "status": t.status.value,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ]
    }


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """
    Ottiene dettagli di un task specifico.
    """
    task = orchestrator.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    return task


@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    """
    Esegue un task esistente.
    """
    try:
        result = await orchestrator.execute_task(task_id)
        return {
            "task_id": result.task_id,
            "status": result.status.value,
            "output": result.output_data,
            "error": result.error
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# PIPELINE ENDPOINTS
# =============================================================================

@router.post("/pipelines")
async def create_pipeline(request: CreatePipelineRequest):
    """
    Crea e opzionalmente esegue una pipeline.
    """
    steps = []
    for step_data in request.steps:
        steps.append(PipelineStep(
            step_id=step_data.get("step_id", f"step_{len(steps)}"),
            agent_type=AgentType(step_data["agent_type"]),
            action=step_data["action"],
            input_mapping=step_data.get("input_mapping", {}),
            output_key=step_data.get("output_key"),
            condition=step_data.get("condition")
        ))

    pipeline = orchestrator.create_pipeline(
        name=request.name,
        description=request.description,
        steps=steps,
        initial_context=request.initial_context
    )

    if request.execute_immediately:
        result = await orchestrator.execute_pipeline(pipeline.pipeline_id)
        return {
            "pipeline_id": result.pipeline_id,
            "status": result.status.value,
            "context": result.context,
            "current_step": result.current_step
        }

    return {
        "pipeline_id": pipeline.pipeline_id,
        "status": pipeline.status.value,
        "message": "Pipeline created. Use /pipelines/{id}/execute to run."
    }


@router.get("/pipelines")
async def list_pipelines(
    status: Optional[TaskStatus] = None,
    limit: int = 20
):
    """
    Lista pipeline recenti.
    """
    pipelines = list(orchestrator.pipelines.values())

    if status:
        pipelines = [p for p in pipelines if p.status == status]

    pipelines.sort(key=lambda x: x.created_at, reverse=True)
    pipelines = pipelines[:limit]

    return {
        "count": len(pipelines),
        "pipelines": [
            {
                "pipeline_id": p.pipeline_id,
                "name": p.name,
                "status": p.status.value,
                "steps": len(p.steps),
                "current_step": p.current_step,
                "created_at": p.created_at.isoformat()
            }
            for p in pipelines
        ]
    }


@router.get("/pipelines/{pipeline_id}")
async def get_pipeline(pipeline_id: str):
    """
    Ottiene dettagli di una pipeline.
    """
    pipeline = orchestrator.pipelines.get(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Pipeline not found: {pipeline_id}")

    return pipeline


@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(pipeline_id: str):
    """
    Esegue una pipeline esistente.
    """
    try:
        result = await orchestrator.execute_pipeline(pipeline_id)
        return {
            "pipeline_id": result.pipeline_id,
            "status": result.status.value,
            "context": result.context
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# WORKFLOW ENDPOINTS
# =============================================================================

@router.post("/workflows/daily-content")
async def run_daily_content_workflow(brand_id: str = "default"):
    """
    Esegue il workflow giornaliero per content marketing.

    Pipeline:
    1. Analyze Performance → Ottieni insights
    2. Generate Content → Crea contenuto ottimizzato
    3. Schedule Posts → Pianifica pubblicazione
    4. Prepare Email → Prepara newsletter
    """
    result = await orchestrator.run_daily_content_workflow(brand_id)

    return {
        "pipeline_id": result.pipeline_id,
        "name": result.name,
        "status": result.status.value,
        "steps_completed": result.current_step + 1,
        "total_steps": len(result.steps),
        "context": result.context
    }


@router.post("/workflows/campaign-launch")
async def run_campaign_launch(request: CampaignLaunchRequest):
    """
    Esegue il workflow per lancio campagna.

    Pipeline:
    1. Create Campaign Assets → Genera tutti i materiali
    2. Setup Social Posts → Prepara post per tutti i canali
    3. Setup Email Sequence → Prepara sequenza email
    4. Launch → Attiva tutto
    """
    campaign_config = {
        "name": request.campaign_name,
        "platforms": request.target_platforms,
        "themes": request.content_themes,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "budget": request.budget
    }

    result = await orchestrator.run_campaign_launch(campaign_config)

    return {
        "pipeline_id": result.pipeline_id,
        "name": result.name,
        "status": result.status.value,
        "steps_completed": result.current_step + 1,
        "total_steps": len(result.steps),
        "launch_result": result.context.get("launch_result")
    }


# =============================================================================
# MEMORY ENDPOINTS
# =============================================================================

@router.get("/memory")
async def get_memory_contents():
    """
    Visualizza contenuti della memoria condivisa.
    """
    entries = []
    for key in orchestrator.memory.get_all_keys():
        entry = orchestrator.memory.get_entry(key)
        if entry:
            entries.append({
                "key": entry.key,
                "agent_source": entry.agent_source.value,
                "timestamp": entry.timestamp.isoformat(),
                "tags": entry.tags,
                "value_type": type(entry.value).__name__
            })

    return {
        "count": len(entries),
        "entries": entries
    }


@router.post("/memory/{key}")
async def set_memory_value(
    key: str,
    value: dict[str, Any],
    agent_type: AgentType = AgentType.CONTENT_CREATOR,
    ttl_hours: Optional[int] = None
):
    """
    Imposta un valore nella memoria condivisa.
    """
    orchestrator.memory.set(
        key=key,
        value=value,
        agent=agent_type,
        ttl_hours=ttl_hours
    )

    return {"success": True, "key": key}


@router.get("/memory/{key}")
async def get_memory_value(key: str):
    """
    Ottiene un valore dalla memoria condivisa.
    """
    value = orchestrator.memory.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Key not found: {key}")

    entry = orchestrator.memory.get_entry(key)
    return {
        "key": key,
        "value": value,
        "metadata": {
            "agent_source": entry.agent_source.value if entry else None,
            "timestamp": entry.timestamp.isoformat() if entry else None
        }
    }


@router.delete("/memory/{key}")
async def delete_memory_value(key: str):
    """
    Elimina un valore dalla memoria condivisa.
    """
    orchestrator.memory.delete(key)
    return {"success": True, "key": key}
