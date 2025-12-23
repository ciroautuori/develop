"""
Workflow API Router - Gestione workflow CONFIGURABILI.

Supporta configurazioni dinamiche complete da UI.
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.domain.marketing.workflow_engine import (
    ActionConfig,
    TriggerConfig,
    Workflow,
    WorkflowStatus,
    get_workflow_templates,
    workflow_engine,
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TriggerConfigRequest(BaseModel):
    """Configurazione trigger da UI."""
    type: str = "schedule"
    frequency: str = "weekly"
    days: list[int] = Field(default_factory=lambda: [1])
    hour: int = 9
    minute: int = 0
    filters: dict[str, Any] = Field(default_factory=dict)


class ActionConfigRequest(BaseModel):
    """Configurazione azione da UI."""
    id: str
    type: str
    # Email
    emailTemplate: str | None = None
    emailSubject: str | None = None
    # Wait
    waitHours: int | None = None
    waitDays: int | None = None
    # Content
    contentType: str | None = None
    contentTone: str | None = None
    # Social
    platforms: list[str] | None = None
    postCount: int | None = None
    generateImage: bool | None = None
    # Notify
    notifyChannel: str | None = None
    notifyMessage: str | None = None
    # Lead
    leadStatus: str | None = None
    leadTags: list[str] | None = None
    # Task
    taskTitle: str | None = None
    taskAssignee: str | None = None
    # Legacy
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreate(BaseModel):
    """Request per creazione workflow."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    trigger: TriggerConfigRequest
    actions: list[ActionConfigRequest]


class WorkflowUpdate(BaseModel):
    """Request per aggiornamento workflow."""
    name: str | None = None
    description: str | None = None
    trigger: TriggerConfigRequest | None = None
    actions: list[ActionConfigRequest] | None = None


class TriggerRequest(BaseModel):
    """Request per trigger manuale."""
    context: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/")
async def list_workflows(status: str | None = None):
    """Lista tutti i workflow."""
    status_enum = WorkflowStatus(status) if status else None
    workflows = workflow_engine.list_workflows(status_enum)
    return [w.model_dump() for w in workflows]


@router.get("/templates")
async def get_templates():
    """Ottieni template workflow predefiniti (configurazioni di default modificabili)."""
    templates = get_workflow_templates()
    return [t.model_dump() for t in templates]


@router.post("/")
async def create_workflow(data: WorkflowCreate):
    """Crea nuovo workflow con configurazione personalizzata."""
    workflow_id = f"wf_{uuid.uuid4().hex[:12]}"

    # Converti trigger
    trigger = TriggerConfig(**data.trigger.model_dump())

    # Converti actions
    actions = [ActionConfig(**a.model_dump()) for a in data.actions]

    workflow = Workflow(
        id=workflow_id,
        name=data.name,
        description=data.description,
        trigger=trigger,
        actions=actions,
        status=WorkflowStatus.DRAFT,
    )

    created = workflow_engine.create_workflow(workflow)
    return created.model_dump()


@router.post("/from-template/{template_id}")
async def create_from_template(template_id: str, name: str | None = None):
    """Crea workflow da template (poi configurabile da UI)."""
    templates = get_workflow_templates()
    template = next((t for t in templates if t.id == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    workflow = Workflow(
        id=f"wf_{uuid.uuid4().hex[:12]}",
        name=name or f"{template.name} (Copy)",
        description=template.description,
        trigger=template.trigger.model_copy(),
        actions=[a.model_copy() for a in template.actions],
        status=WorkflowStatus.DRAFT,
    )

    created = workflow_engine.create_workflow(workflow)
    return created.model_dump()


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Ottieni workflow per ID."""
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.model_dump()


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, data: WorkflowUpdate):
    """Aggiorna workflow con nuove configurazioni."""
    updates = {}

    if data.name is not None:
        updates["name"] = data.name
    if data.description is not None:
        updates["description"] = data.description
    if data.trigger is not None:
        updates["trigger"] = data.trigger.model_dump()
    if data.actions is not None:
        updates["actions"] = [a.model_dump() for a in data.actions]

    workflow = workflow_engine.update_workflow(workflow_id, updates)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow.model_dump()


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Elimina workflow."""
    if not workflow_engine.delete_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "deleted", "id": workflow_id}


@router.post("/{workflow_id}/activate")
async def activate_workflow(workflow_id: str):
    """Attiva workflow."""
    if not workflow_engine.activate_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "active", "id": workflow_id}


@router.post("/{workflow_id}/pause")
async def pause_workflow(workflow_id: str):
    """Pausa workflow."""
    if not workflow_engine.pause_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "paused", "id": workflow_id}


@router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: str, data: TriggerRequest):
    """Esegui workflow manualmente."""
    exec_id = await workflow_engine.run_workflow(workflow_id, data.context)

    if not exec_id:
        raise HTTPException(status_code=404, detail="Workflow not found")

    execution = workflow_engine.get_execution(exec_id)
    return execution.model_dump()


@router.get("/{workflow_id}/executions")
async def list_executions(workflow_id: str):
    """Lista esecuzioni di un workflow."""
    executions = workflow_engine.list_executions(workflow_id)
    return [e.model_dump() for e in executions]


@router.get("/executions/{exec_id}")
async def get_execution(exec_id: str):
    """Ottieni dettagli esecuzione."""
    execution = workflow_engine.get_execution(exec_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution.model_dump()


# ============================================================================
# META ENDPOINTS - Per UI dropdown
# ============================================================================

@router.get("/meta/trigger-types")
async def get_trigger_types():
    """Lista tipi di trigger disponibili."""
    return [
        {"value": "schedule", "label": "⏰ Schedulato"},
        {"value": "lead_created", "label": "👤 Nuovo Lead"},
        {"value": "email_opened", "label": "📧 Email Aperta"},
        {"value": "manual", "label": "🖱️ Manuale"},
    ]


@router.get("/meta/action-types")
async def get_action_types():
    """Lista tipi di azione disponibili."""
    return [
        {"value": "generate_content", "label": "📝 Genera Contenuto"},
        {"value": "publish_social", "label": "📱 Pubblica Social"},
        {"value": "send_email", "label": "📧 Invia Email"},
        {"value": "wait", "label": "⏳ Attesa"},
        {"value": "notify", "label": "🔔 Notifica"},
        {"value": "update_lead", "label": "👤 Aggiorna Lead"},
        {"value": "create_task", "label": "✅ Crea Task"},
    ]


@router.get("/meta/platforms")
async def get_platforms():
    """Lista piattaforme social disponibili."""
    return [
        {"value": "linkedin", "label": "LinkedIn"},
        {"value": "instagram", "label": "Instagram"},
        {"value": "facebook", "label": "Facebook"},
        {"value": "twitter", "label": "Twitter/X"},
    ]


@router.get("/meta/email-templates")
async def get_email_templates():
    """Lista template email disponibili."""
    return [
        {"value": "welcome", "label": "Benvenuto"},
        {"value": "follow_up", "label": "Follow-up"},
        {"value": "case_study", "label": "Case Study"},
        {"value": "offer", "label": "Offerta Speciale"},
        {"value": "newsletter", "label": "Newsletter"},
        {"value": "reengagement", "label": "Re-engagement"},
    ]
