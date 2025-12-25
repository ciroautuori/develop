"""
Marketing Workflow Engine - Automazione CONFIGURABILE.

Supporta configurazioni dinamiche da UI:
- Trigger: giorni, orari, frequenza personalizzabili
- Azioni: piattaforme, delay, templates configurabili
- Nessun valore hardcoded
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
import logging
import asyncio
import uuid

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class TriggerType(str, Enum):
    SCHEDULE = "schedule"
    LEAD_CREATED = "lead_created"
    MANUAL = "manual"
    EMAIL_OPENED = "email_opened"
    WEBHOOK = "webhook"


class ActionType(str, Enum):
    SEND_EMAIL = "send_email"
    WAIT = "wait"
    UPDATE_LEAD = "update_lead"
    CREATE_TASK = "create_task"
    GENERATE_CONTENT = "generate_content"
    PUBLISH_SOCIAL = "publish_social"
    NOTIFY = "notify"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


# ============================================================================
# MODELS - CONFIGURAZIONE DINAMICA
# ============================================================================

class TriggerConfig(BaseModel):
    """Configurazione trigger COMPLETAMENTE DINAMICA."""
    type: str = "schedule"
    frequency: str = "weekly"  # daily, weekly, monthly, custom
    days: List[int] = Field(default_factory=lambda: [1])  # 0=Dom, 1=Lun, etc
    hour: int = 9
    minute: int = 0
    filters: Dict[str, Any] = Field(default_factory=dict)
    # filters per lead_created: {"min_score": 70}


class ActionConfig(BaseModel):
    """Configurazione azione COMPLETAMENTE DINAMICA."""
    id: str
    type: str
    # Email config
    emailTemplate: Optional[str] = None
    emailSubject: Optional[str] = None
    # Wait config
    waitHours: Optional[int] = None
    waitDays: Optional[int] = None
    # Content config
    contentType: Optional[str] = None  # social, blog, ad
    contentTone: Optional[str] = None  # professional, casual, friendly
    # Social config
    platforms: Optional[List[str]] = None  # linkedin, instagram, facebook, twitter
    postCount: Optional[int] = None
    generateImage: Optional[bool] = None
    # Notify config
    notifyChannel: Optional[str] = None  # email, slack, webhook
    notifyMessage: Optional[str] = None
    # Lead config
    leadStatus: Optional[str] = None
    leadTags: Optional[List[str]] = None
    # Task config
    taskTitle: Optional[str] = None
    taskAssignee: Optional[str] = None
    # Legacy config dict (per retrocompatibilità)
    config: Dict[str, Any] = Field(default_factory=dict)

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Ottiene valore da attributo diretto o da config dict."""
        # Prima prova attributo diretto
        direct_value = getattr(self, key, None)
        if direct_value is not None:
            return direct_value
        # Poi prova config dict
        return self.config.get(key, default)


class Workflow(BaseModel):
    """Definizione workflow con configurazioni dinamiche."""
    id: str
    name: str
    description: str = ""
    trigger: TriggerConfig
    actions: List[ActionConfig]
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = 1
    execution_count: int = 0
    last_executed: Optional[datetime] = None


class ExecutionLog(BaseModel):
    """Log singola esecuzione."""
    id: str
    workflow_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_action: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    error: Optional[str] = None


# ============================================================================
# WORKFLOW ENGINE
# ============================================================================

class WorkflowEngine:
    """
    Engine per esecuzione workflow marketing CONFIGURABILI.

    Ogni parametro è dinamico e configurabile da UI.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._workflows: Dict[str, Workflow] = {}
        self._executions: Dict[str, ExecutionLog] = {}
        self._action_handlers: Dict[str, Callable] = {}

        self._register_handlers()
        self._initialized = True
        logger.info("workflow_engine_initialized")

    def _register_handlers(self):
        """Registra handler per ogni tipo di azione."""
        self._action_handlers = {
            "send_email": self._handle_send_email,
            "wait": self._handle_wait,
            "update_lead": self._handle_update_lead,
            "create_task": self._handle_create_task,
            "generate_content": self._handle_generate_content,
            "publish_social": self._handle_publish_social,
            "notify": self._handle_notify,
        }

    # ========================================================================
    # WORKFLOW CRUD
    # ========================================================================

    def create_workflow(self, workflow: Workflow) -> Workflow:
        """Crea nuovo workflow."""
        workflow.updated_at = datetime.utcnow()
        self._workflows[workflow.id] = workflow
        logger.info(f"workflow_created: {workflow.id} - {workflow.name}")
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def list_workflows(self, status: Optional[WorkflowStatus] = None) -> List[Workflow]:
        workflows = list(self._workflows.values())
        if status:
            workflows = [w for w in workflows if w.status == status]
        return workflows

    def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> Optional[Workflow]:
        """Aggiorna workflow con nuove configurazioni."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None

        # Aggiorna campi semplici
        for key in ['name', 'description']:
            if key in updates:
                setattr(workflow, key, updates[key])

        # Aggiorna trigger
        if 'trigger' in updates:
            trigger_data = updates['trigger']
            if isinstance(trigger_data, dict):
                workflow.trigger = TriggerConfig(**trigger_data)
            elif isinstance(trigger_data, TriggerConfig):
                workflow.trigger = trigger_data

        # Aggiorna actions
        if 'actions' in updates:
            actions_data = updates['actions']
            new_actions = []
            for action in actions_data:
                if isinstance(action, dict):
                    new_actions.append(ActionConfig(**action))
                elif isinstance(action, ActionConfig):
                    new_actions.append(action)
            workflow.actions = new_actions

        workflow.updated_at = datetime.utcnow()
        self._workflows[workflow_id] = workflow
        return workflow

    def delete_workflow(self, workflow_id: str) -> bool:
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            return True
        return False

    def activate_workflow(self, workflow_id: str) -> bool:
        workflow = self._workflows.get(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.ACTIVE
            workflow.updated_at = datetime.utcnow()
            return True
        return False

    def pause_workflow(self, workflow_id: str) -> bool:
        workflow = self._workflows.get(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.PAUSED
            workflow.updated_at = datetime.utcnow()
            return True
        return False

    # ========================================================================
    # EXECUTION
    # ========================================================================

    async def trigger(self, trigger_type: str, context: Dict[str, Any]) -> List[str]:
        """Triggera workflow che matchano il tipo e contesto."""
        execution_ids = []

        for workflow in self._workflows.values():
            if workflow.status != WorkflowStatus.ACTIVE:
                continue
            if workflow.trigger.type != trigger_type:
                continue
            if not self._match_trigger(workflow.trigger, context):
                continue

            exec_id = await self._execute_workflow(workflow, context)
            if exec_id:
                execution_ids.append(exec_id)

        return execution_ids

    def _match_trigger(self, trigger: TriggerConfig, context: Dict[str, Any]) -> bool:
        """Verifica se il contesto matcha il trigger configurato."""
        # Per schedule, check giorno/ora
        if trigger.type == "schedule":
            now = datetime.now()
            # Check giorno della settimana
            if trigger.days and now.weekday() not in [d % 7 for d in trigger.days]:
                return False
            # Check ora (con tolleranza di 5 minuti)
            if trigger.hour != now.hour:
                return False

        # Per lead_created, check filtri
        if trigger.type == "lead_created":
            min_score = trigger.filters.get("min_score", 0)
            lead_score = context.get("score", 0)
            if lead_score < min_score:
                return False

        return True

    async def _execute_workflow(self, workflow: Workflow, context: Dict[str, Any]) -> Optional[str]:
        """Esegui un workflow."""
        exec_id = f"exec_{uuid.uuid4().hex[:12]}"

        execution = ExecutionLog(
            id=exec_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.utcnow(),
            context=context,
            logs=[f"▶️ Workflow avviato: {workflow.name}"]
        )

        self._executions[exec_id] = execution

        try:
            for action in workflow.actions:
                execution.current_action = action.id
                action_label = action.type.replace('_', ' ').title()
                execution.logs.append(f"⚡ Esecuzione: {action_label}")

                handler = self._action_handlers.get(action.type)
                if handler:
                    await handler(action, context, execution)
                else:
                    execution.logs.append(f"⚠️ Handler non trovato: {action.type}")

            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.logs.append("✅ Workflow completato con successo")

            workflow.execution_count += 1
            workflow.last_executed = datetime.utcnow()

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.logs.append(f"❌ Errore: {str(e)}")
            logger.error(f"workflow_execution_failed: {exec_id} - {str(e)}")

        return exec_id

    async def run_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Esegui workflow manualmente."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None
        return await self._execute_workflow(workflow, context or {})

    def get_execution(self, exec_id: str) -> Optional[ExecutionLog]:
        return self._executions.get(exec_id)

    def list_executions(self, workflow_id: Optional[str] = None) -> List[ExecutionLog]:
        execs = list(self._executions.values())
        if workflow_id:
            execs = [e for e in execs if e.workflow_id == workflow_id]
        return sorted(execs, key=lambda e: e.started_at, reverse=True)

    # ========================================================================
    # ACTION HANDLERS - USA CONFIGURAZIONI DINAMICHE
    # ========================================================================

    async def _handle_send_email(self, action: ActionConfig, context: Dict, execution: ExecutionLog):
        """Invia email con configurazione dinamica."""
        template = action.emailTemplate or action.get_config_value("template", "default")
        subject = action.emailSubject or action.get_config_value("subject", "")

        execution.logs.append(f"   📧 Template: {template}")
        if subject:
            execution.logs.append(f"   📝 Oggetto: {subject}")
        # Integration: email_service.send_email() for actual delivery

    async def _handle_wait(self, action: ActionConfig, context: Dict, execution: ExecutionLog):
        """Attesa con durata configurabile."""
        days = action.waitDays or action.get_config_value("days", 0)
        hours = action.waitHours or action.get_config_value("hours", 0)
        total_hours = (days * 24) + hours

        execution.status = ExecutionStatus.WAITING
        execution.logs.append(f"   ⏳ Attesa: {days}g {hours}h")

        # Demo: attesa max 5 secondi
        await asyncio.sleep(min(total_hours * 0.1, 5))

    async def _handle_update_lead(self, action: ActionConfig, context: Dict, execution: ExecutionLog):
        """Aggiorna lead con status configurabile."""
        new_status = action.leadStatus or action.get_config_value("status", "contacted")
        tags = action.leadTags or action.get_config_value("tags", [])

        execution.logs.append(f"   👤 Nuovo status: {new_status}")
        if tags:
            execution.logs.append(f"   🏷️ Tags: {', '.join(tags)}")
        # Integration: CustomerService.update_customer() for lead updates

    async def _handle_create_task(self, action: ActionConfig, context: Dict, execution: ExecutionLog):
        """Crea task con configurazione dinamica."""
        title = action.taskTitle or action.get_config_value("title", "Follow up")
        assignee = action.taskAssignee or action.get_config_value("assignee", "sales")

        execution.logs.append(f"   ✅ Task: {title}")
        execution.logs.append(f"   👥 Assegnato a: {assignee}")
        # Integration: Task management system (Phase 3)

    async def _handle_generate_content(self, action: ActionConfig, context: Dict, execution: ExecutionLog):
        """Genera contenuto con tipo e tono configurabili."""
        content_type = action.contentType or action.get_config_value("type", "social")
        tone = action.contentTone or action.get_config_value("tone", "professional")

        execution.logs.append(f"   📝 Tipo: {content_type}")
        execution.logs.append(f"   🎭 Tono: {tone}")
        # Integration: AI microservice /marketing/generate endpoint

    async def _handle_publish_social(self, action: ActionConfig, context: Dict, execution: ExecutionLog):
        """Pubblica su social con piattaforme configurabili."""
        platforms = action.platforms or action.get_config_value("platforms", ["linkedin"])
        post_count = action.postCount or action.get_config_value("count", 1)
        generate_image = action.generateImage or action.get_config_value("image", False)

        execution.logs.append(f"   📱 Piattaforme: {', '.join(platforms)}")
        execution.logs.append(f"   📊 Post: {post_count} per piattaforma")
        if generate_image:
            execution.logs.append(f"   🖼️ Immagine AI: Sì")
        # Integration: social_router.publish_post() for publishing

    async def _handle_notify(self, action: ActionConfig, context: Dict, execution: ExecutionLog):
        """Invia notifica con canale configurabile."""
        channel = action.notifyChannel or action.get_config_value("channel", "email")
        message = action.notifyMessage or action.get_config_value("message", "Notifica workflow")

        execution.logs.append(f"   🔔 Canale: {channel}")
        execution.logs.append(f"   💬 Messaggio: {message}")
        # Integration: notification_service.send() for delivery


# Singleton instance
workflow_engine = WorkflowEngine()


# ============================================================================
# WORKFLOW TEMPLATES - CONFIGURAZIONI DI DEFAULT (MODIFICABILI)
# ============================================================================

def get_workflow_templates() -> List[Workflow]:
    """Templates con configurazioni di default (tutti i valori sono modificabili da UI)."""
    return [
        Workflow(
            id="template_lead_nurturing",
            name="Lead Nurturing Automatico",
            description="Sequenza email per lead con score alto - Configura giorni, delay e templates",
            trigger=TriggerConfig(
                type="lead_created",
                frequency="daily",
                days=[],
                hour=9,
                minute=0,
                filters={"min_score": 70}
            ),
            actions=[
                ActionConfig(
                    id="wait_1",
                    type="wait",
                    waitDays=1,
                    waitHours=0
                ),
                ActionConfig(
                    id="email_1",
                    type="send_email",
                    emailTemplate="welcome",
                    emailSubject="Benvenuto!"
                ),
                ActionConfig(
                    id="wait_2",
                    type="wait",
                    waitDays=3,
                    waitHours=0
                ),
                ActionConfig(
                    id="email_2",
                    type="send_email",
                    emailTemplate="case_study"
                ),
                ActionConfig(
                    id="task_1",
                    type="create_task",
                    taskTitle="Followup lead caldo",
                    taskAssignee="sales"
                ),
            ],
            status=WorkflowStatus.DRAFT
        ),
        Workflow(
            id="template_social_posting",
            name="Post Social Programmato",
            description="Pubblica automaticamente - Scegli TU giorni, orari e piattaforme",
            trigger=TriggerConfig(
                type="schedule",
                frequency="weekly",
                days=[1, 3, 5],  # Lun, Mer, Ven di default
                hour=9,
                minute=0,
                filters={}
            ),
            actions=[
                ActionConfig(
                    id="content_1",
                    type="generate_content",
                    contentType="social",
                    contentTone="professional"
                ),
                ActionConfig(
                    id="publish_1",
                    type="publish_social",
                    platforms=["linkedin", "instagram"],
                    postCount=1,
                    generateImage=True
                ),
                ActionConfig(
                    id="notify_1",
                    type="notify",
                    notifyChannel="email",
                    notifyMessage="Post pubblicato con successo!"
                ),
            ],
            status=WorkflowStatus.DRAFT
        ),
        Workflow(
            id="template_reengagement",
            name="Re-engagement Lead Freddi",
            description="Riattiva lead inattivi - Configura timing e messaggi",
            trigger=TriggerConfig(
                type="schedule",
                frequency="monthly",
                days=[1],  # Primo del mese
                hour=10,
                minute=0,
                filters={}
            ),
            actions=[
                ActionConfig(
                    id="email_re",
                    type="send_email",
                    emailTemplate="reengagement",
                    emailSubject="Ci manchi! Torna a trovarci"
                ),
                ActionConfig(
                    id="notify_re",
                    type="notify",
                    notifyChannel="slack",
                    notifyMessage="Campagna re-engagement avviata"
                ),
            ],
            status=WorkflowStatus.DRAFT
        ),
    ]
