/**
 * Workflow Builder - Automazione Marketing CONFIGURABILE
 *
 * Funzionalità:
 * - Creazione workflow personalizzati
 * - Configurazione trigger (giorni, orari, frequenza)
 * - Configurazione azioni (piattaforme, delay, templates)
 * - Gestione completa parametri
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Workflow,
  Play,
  Pause,
  Trash2,
  RefreshCw,
  Plus,
  ChevronRight,
  ChevronDown,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  X,
  Save,
  Zap,
  Mail,
  Users,
  Calendar,
  Settings,
  Edit,
  GripVertical,
  Bell,
  Share2,
  FileText
} from 'lucide-react';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';

// ============================================================================
// TYPES
// ============================================================================

interface TriggerConfig {
  type: 'schedule' | 'lead_created' | 'manual' | 'email_opened';
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom';
  days: number[]; // 0=Dom, 1=Lun, etc
  hour: number;
  minute: number;
  filters: Record<string, any>;
}

interface ActionConfig {
  id: string;
  type: 'send_email' | 'wait' | 'generate_content' | 'publish_social' | 'notify' | 'update_lead' | 'create_task';
  // Email config
  emailTemplate?: string;
  emailSubject?: string;
  // Wait config
  waitHours?: number;
  waitDays?: number;
  // Content config
  contentType?: 'social' | 'blog' | 'ad';
  contentTone?: 'professional' | 'casual' | 'friendly';
  // Social config
  platforms?: string[];
  postCount?: number;
  generateImage?: boolean;
  // Notify config
  notifyChannel?: 'email' | 'slack' | 'webhook';
  notifyMessage?: string;
  // Lead config
  leadStatus?: string;
  leadTags?: string[];
  // Task config
  taskTitle?: string;
  taskAssignee?: string;
}

interface WorkflowData {
  id: string;
  name: string;
  description: string;
  trigger: TriggerConfig;
  actions: ActionConfig[];
  status: 'draft' | 'active' | 'paused' | 'archived';
  execution_count: number;
  last_executed: string | null;
  created_at: string;
}

interface ExecutionLog {
  id: string;
  workflow_id: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  logs: string[];
  error: string | null;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const DAYS_OF_WEEK = [
  { value: 0, label: 'Dom', short: 'D' },
  { value: 1, label: 'Lun', short: 'L' },
  { value: 2, label: 'Mar', short: 'M' },
  { value: 3, label: 'Mer', short: 'M' },
  { value: 4, label: 'Gio', short: 'G' },
  { value: 5, label: 'Ven', short: 'V' },
  { value: 6, label: 'Sab', short: 'S' },
];

const SOCIAL_PLATFORMS = [
  { value: 'linkedin', label: 'LinkedIn', color: 'bg-blue-600' },
  { value: 'instagram', label: 'Instagram', color: 'bg-pink-600' },
  { value: 'facebook', label: 'Facebook', color: 'bg-blue-500' },
  { value: 'twitter', label: 'Twitter/X', color: 'bg-gray-800' },
];

const EMAIL_TEMPLATES = [
  { value: 'welcome', label: 'Benvenuto' },
  { value: 'follow_up', label: 'Follow-up' },
  { value: 'case_study', label: 'Case Study' },
  { value: 'offer', label: 'Offerta Speciale' },
  { value: 'newsletter', label: 'Newsletter' },
  { value: 'reengagement', label: 'Re-engagement' },
];

const CONTENT_TONES = [
  { value: 'professional', label: 'Professionale' },
  { value: 'casual', label: 'Casual' },
  { value: 'friendly', label: 'Amichevole' },
  { value: 'urgent', label: 'Urgente' },
];

const ACTION_TYPES = [
  { value: 'generate_content', label: 'Genera Contenuto', icon: FileText },
  { value: 'publish_social', label: 'Pubblica Social', icon: Share2 },
  { value: 'send_email', label: 'Invia Email', icon: Mail },
  { value: 'wait', label: 'Attesa', icon: Clock },
  { value: 'notify', label: 'Notifica', icon: Bell },
  { value: 'update_lead', label: 'Aggiorna Lead', icon: Users },
  { value: 'create_task', label: 'Crea Task', icon: CheckCircle },
];

// ============================================================================
// API SERVICE
// ============================================================================

const WorkflowApiService = {
  baseUrl: '/api/v1/marketing/workflows',

  getHeaders(): HeadersInit {
    return {
      'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
      'Content-Type': 'application/json',
    };
  },

  async listWorkflows(): Promise<WorkflowData[]> {
    const res = await fetch(this.baseUrl, { headers: this.getHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  async getTemplates(): Promise<WorkflowData[]> {
    const res = await fetch(`${this.baseUrl}/templates`, { headers: this.getHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  async createWorkflow(data: Partial<WorkflowData>): Promise<WorkflowData> {
    const res = await fetch(this.baseUrl, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create workflow');
    return res.json();
  },

  async updateWorkflow(id: string, data: Partial<WorkflowData>): Promise<WorkflowData> {
    const res = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update workflow');
    return res.json();
  },

  async activateWorkflow(id: string): Promise<void> {
    const res = await fetch(`${this.baseUrl}/${id}/activate`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to activate');
  },

  async pauseWorkflow(id: string): Promise<void> {
    const res = await fetch(`${this.baseUrl}/${id}/pause`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to pause');
  },

  async runWorkflow(id: string): Promise<ExecutionLog> {
    const res = await fetch(`${this.baseUrl}/${id}/run`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ context: {} }),
    });
    if (!res.ok) throw new Error('Failed to run');
    return res.json();
  },

  async deleteWorkflow(id: string): Promise<void> {
    const res = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete');
  },

  async getExecutions(workflowId: string): Promise<ExecutionLog[]> {
    const res = await fetch(`${this.baseUrl}/${workflowId}/executions`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  },
};

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

function StatusBadge({ status }: { status: string }) {
  const configs: Record<string, { bg: string; text: string; icon: typeof CheckCircle }> = {
    active: { bg: 'bg-green-500/20', text: 'text-green-400', icon: CheckCircle },
    draft: { bg: 'bg-gray-500/20', text: 'text-gray-400', icon: Clock },
    paused: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: Pause },
    archived: { bg: 'bg-red-500/20', text: 'text-red-400', icon: AlertCircle },
  };
  const config = configs[status] || configs.draft;
  const Icon = config.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${config.bg} ${config.text}`}>
      <Icon className="w-3 h-3" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

// ============================================================================
// TRIGGER EDITOR
// ============================================================================

interface TriggerEditorProps {
  trigger: TriggerConfig;
  onChange: (trigger: TriggerConfig) => void;
  isDark: boolean;
}

function TriggerEditor({ trigger, onChange, isDark }: TriggerEditorProps) {
  const inputBg = isDark ? 'bg-[#1A1A1A] border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  const toggleDay = (day: number) => {
    const newDays = trigger.days.includes(day)
      ? trigger.days.filter(d => d !== day)
      : [...trigger.days, day].sort();
    onChange({ ...trigger, days: newDays });
  };

  return (
    <div className="space-y-4">
      <h4 className={`font-medium flex items-center gap-2 ${textPrimary}`}>
        <Zap className="w-4 h-4 text-orange-400" />
        Trigger - Quando si attiva
      </h4>

      {/* Tipo Trigger */}
      <div>
        <label className={`block text-sm mb-2 ${textSecondary}`}>Tipo di attivazione</label>
        <select
          value={trigger.type}
          onChange={(e) => onChange({ ...trigger, type: e.target.value as TriggerConfig['type'] })}
          className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
        >
          <option value="schedule">⏰ Schedulato (Orari specifici)</option>
          <option value="lead_created">👤 Nuovo Lead Creato</option>
          <option value="email_opened">📧 Email Aperta</option>
          <option value="manual">🖱️ Esecuzione Manuale</option>
        </select>
      </div>

      {trigger.type === 'schedule' && (
        <>
          {/* Frequenza */}
          <div>
            <label className={`block text-sm mb-2 ${textSecondary}`}>Frequenza</label>
            <div className="flex gap-2">
              {['daily', 'weekly', 'monthly'].map((freq) => (
                <button
                  key={freq}
                  onClick={() => onChange({ ...trigger, frequency: freq as TriggerConfig['frequency'] })}
                  className={`px-4 py-2 rounded-lg text-sm transition-colors ${trigger.frequency === freq
                      ? 'bg-orange-500 text-white'
                      : isDark
                        ? 'bg-white/10 text-gray-300 hover:bg-white/20'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                >
                  {freq === 'daily' && 'Giornaliero'}
                  {freq === 'weekly' && 'Settimanale'}
                  {freq === 'monthly' && 'Mensile'}
                </button>
              ))}
            </div>
          </div>

          {/* Giorni della settimana */}
          {(trigger.frequency === 'weekly' || trigger.frequency === 'daily') && (
            <div>
              <label className={`block text-sm mb-2 ${textSecondary}`}>
                Giorni {trigger.frequency === 'daily' ? '(tutti se non selezionati)' : ''}
              </label>
              <div className="flex gap-2">
                {DAYS_OF_WEEK.map((day) => (
                  <button
                    key={day.value}
                    onClick={() => toggleDay(day.value)}
                    className={`w-10 h-10 rounded-lg font-medium transition-colors ${trigger.days.includes(day.value)
                        ? 'bg-orange-500 text-white'
                        : isDark
                          ? 'bg-white/10 text-gray-300 hover:bg-white/20'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    title={day.label}
                  >
                    {day.short}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Orario */}
          <div>
            <label className={`block text-sm mb-2 ${textSecondary}`}>Orario</label>
            <div className="flex items-center gap-2">
              <select
                value={trigger.hour}
                onChange={(e) => onChange({ ...trigger, hour: parseInt(e.target.value) })}
                className={`px-3 py-2 rounded-lg border ${inputBg}`}
              >
                {Array.from({ length: 24 }, (_, i) => (
                  <option key={i} value={i}>{i.toString().padStart(2, '0')}</option>
                ))}
              </select>
              <span className={textPrimary}>:</span>
              <select
                value={trigger.minute}
                onChange={(e) => onChange({ ...trigger, minute: parseInt(e.target.value) })}
                className={`px-3 py-2 rounded-lg border ${inputBg}`}
              >
                {[0, 15, 30, 45].map(m => (
                  <option key={m} value={m}>{m.toString().padStart(2, '0')}</option>
                ))}
              </select>
            </div>
          </div>
        </>
      )}

      {trigger.type === 'lead_created' && (
        <div>
          <label className={`block text-sm mb-2 ${textSecondary}`}>Filtro Score Minimo</label>
          <input
            type="number"
            value={trigger.filters.min_score || 0}
            onChange={(e) => onChange({
              ...trigger,
              filters: { ...trigger.filters, min_score: parseInt(e.target.value) }
            })}
            className={`w-32 px-3 py-2 rounded-lg border ${inputBg}`}
            min={0}
            max={100}
          />
          <span className={`ml-2 text-sm ${textSecondary}`}>
            (0 = tutti i lead)
          </span>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// ACTION EDITOR
// ============================================================================

interface ActionEditorProps {
  action: ActionConfig;
  onChange: (action: ActionConfig) => void;
  onRemove: () => void;
  index: number;
  isDark: boolean;
}

function ActionEditor({ action, onChange, onRemove, index, isDark }: ActionEditorProps) {
  const inputBg = isDark ? 'bg-[#1A1A1A] border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const [expanded, setExpanded] = useState(true);

  const ActionTypeIcon = ACTION_TYPES.find(t => t.value === action.type)?.icon || Zap;

  return (
    <div className={`rounded-lg border ${isDark ? 'border-white/10 bg-white/5' : 'border-gray-200 bg-gray-50'}`}>
      {/* Header */}
      <div
        className="flex items-center justify-between p-3 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <GripVertical className={`w-4 h-4 ${textSecondary}`} />
          <span className={`text-sm font-medium ${textSecondary}`}>{index + 1}.</span>
          <ActionTypeIcon className="w-4 h-4 text-orange-400" />
          <span className={isDark ? 'text-white' : 'text-gray-900'}>
            {ACTION_TYPES.find(t => t.value === action.type)?.label || action.type}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          <button
            onClick={(e) => { e.stopPropagation(); onRemove(); }}
            className="text-red-400 hover:text-red-300 p-1"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="p-4 pt-0 space-y-4">
              {/* Tipo Azione */}
              <div>
                <label className={`block text-sm mb-2 ${textSecondary}`}>Tipo Azione</label>
                <select
                  value={action.type}
                  onChange={(e) => onChange({ ...action, type: e.target.value as ActionConfig['type'] })}
                  className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                >
                  {ACTION_TYPES.map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>

              {/* PUBLISH SOCIAL CONFIG */}
              {action.type === 'publish_social' && (
                <>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Piattaforme</label>
                    <div className="flex flex-wrap gap-2">
                      {SOCIAL_PLATFORMS.map((platform) => (
                        <button
                          key={platform.value}
                          onClick={() => {
                            const platforms = action.platforms || [];
                            const newPlatforms = platforms.includes(platform.value)
                              ? platforms.filter(p => p !== platform.value)
                              : [...platforms, platform.value];
                            onChange({ ...action, platforms: newPlatforms });
                          }}
                          className={`px-3 py-2 rounded-lg text-sm transition-colors ${(action.platforms || []).includes(platform.value)
                              ? `${platform.color} text-white`
                              : isDark
                                ? 'bg-white/10 text-gray-300 hover:bg-white/20'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                          {platform.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className={`block text-sm mb-2 ${textSecondary}`}>Post per Piattaforma</label>
                      <input
                        type="number"
                        value={action.postCount || 1}
                        onChange={(e) => onChange({ ...action, postCount: parseInt(e.target.value) })}
                        className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                        min={1}
                        max={10}
                      />
                    </div>
                    <div className="flex items-center gap-2 pt-6">
                      <input
                        type="checkbox"
                        id={`img-${action.id}`}
                        checked={action.generateImage || false}
                        onChange={(e) => onChange({ ...action, generateImage: e.target.checked })}
                        className="w-4 h-4"
                      />
                      <label htmlFor={`img-${action.id}`} className={`text-sm ${textSecondary}`}>
                        Genera Immagine AI
                      </label>
                    </div>
                  </div>
                </>
              )}

              {/* GENERATE CONTENT CONFIG */}
              {action.type === 'generate_content' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Tipo Contenuto</label>
                    <select
                      value={action.contentType || 'social'}
                      onChange={(e) => onChange({ ...action, contentType: e.target.value as 'social' | 'blog' | 'ad' })}
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    >
                      <option value="social">Post Social</option>
                      <option value="blog">Articolo Blog</option>
                      <option value="ad">Testo Ads</option>
                    </select>
                  </div>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Tono</label>
                    <select
                      value={action.contentTone || 'professional'}
                      onChange={(e) => onChange({ ...action, contentTone: e.target.value as ActionConfig['contentTone'] })}
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    >
                      {CONTENT_TONES.map(t => (
                        <option key={t.value} value={t.value}>{t.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* SEND EMAIL CONFIG */}
              {action.type === 'send_email' && (
                <>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Template Email</label>
                    <select
                      value={action.emailTemplate || 'welcome'}
                      onChange={(e) => onChange({ ...action, emailTemplate: e.target.value })}
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    >
                      {EMAIL_TEMPLATES.map(t => (
                        <option key={t.value} value={t.value}>{t.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Oggetto Email (opzionale)</label>
                    <input
                      type="text"
                      value={action.emailSubject || ''}
                      onChange={(e) => onChange({ ...action, emailSubject: e.target.value })}
                      placeholder="Lascia vuoto per usare quello del template"
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    />
                  </div>
                </>
              )}

              {/* WAIT CONFIG */}
              {action.type === 'wait' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Giorni</label>
                    <input
                      type="number"
                      value={action.waitDays || 0}
                      onChange={(e) => onChange({ ...action, waitDays: parseInt(e.target.value) })}
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                      min={0}
                      max={365}
                    />
                  </div>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Ore</label>
                    <input
                      type="number"
                      value={action.waitHours || 0}
                      onChange={(e) => onChange({ ...action, waitHours: parseInt(e.target.value) })}
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                      min={0}
                      max={23}
                    />
                  </div>
                </div>
              )}

              {/* NOTIFY CONFIG */}
              {action.type === 'notify' && (
                <>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Canale</label>
                    <select
                      value={action.notifyChannel || 'email'}
                      onChange={(e) => onChange({ ...action, notifyChannel: e.target.value as 'email' | 'slack' | 'webhook' })}
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    >
                      <option value="email">Email</option>
                      <option value="slack">Slack</option>
                      <option value="webhook">Webhook</option>
                    </select>
                  </div>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Messaggio</label>
                    <input
                      type="text"
                      value={action.notifyMessage || ''}
                      onChange={(e) => onChange({ ...action, notifyMessage: e.target.value })}
                      placeholder="Messaggio di notifica"
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    />
                  </div>
                </>
              )}

              {/* CREATE TASK CONFIG */}
              {action.type === 'create_task' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Titolo Task</label>
                    <input
                      type="text"
                      value={action.taskTitle || ''}
                      onChange={(e) => onChange({ ...action, taskTitle: e.target.value })}
                      placeholder="es: Follow-up cliente"
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    />
                  </div>
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Assegna a</label>
                    <select
                      value={action.taskAssignee || 'sales'}
                      onChange={(e) => onChange({ ...action, taskAssignee: e.target.value })}
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    >
                      <option value="sales">Team Vendite</option>
                      <option value="marketing">Team Marketing</option>
                      <option value="support">Team Supporto</option>
                    </select>
                  </div>
                </div>
              )}

              {/* UPDATE LEAD CONFIG */}
              {action.type === 'update_lead' && (
                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>Nuovo Status</label>
                  <select
                    value={action.leadStatus || 'contacted'}
                    onChange={(e) => onChange({ ...action, leadStatus: e.target.value })}
                    className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                  >
                    <option value="new">Nuovo</option>
                    <option value="contacted">Contattato</option>
                    <option value="qualified">Qualificato</option>
                    <option value="proposal">Proposta Inviata</option>
                    <option value="negotiation">Negoziazione</option>
                    <option value="won">Vinto</option>
                    <option value="lost">Perso</option>
                  </select>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ============================================================================
// WORKFLOW EDITOR MODAL
// ============================================================================

interface WorkflowEditorProps {
  workflow: WorkflowData | null;
  onSave: (workflow: Partial<WorkflowData>) => Promise<void>;
  onClose: () => void;
  isDark: boolean;
}

function WorkflowEditorModal({ workflow, onSave, onClose, isDark }: WorkflowEditorProps) {
  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-xl';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark ? 'bg-[#1A1A1A] border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';

  const [name, setName] = useState(workflow?.name || '');
  const [description, setDescription] = useState(workflow?.description || '');
  const [trigger, setTrigger] = useState<TriggerConfig>(
    workflow?.trigger || {
      type: 'schedule',
      frequency: 'weekly',
      days: [1], // Lunedì default
      hour: 9,
      minute: 0,
      filters: {},
    }
  );
  const [actions, setActions] = useState<ActionConfig[]>(
    workflow?.actions || []
  );
  const [isSaving, setIsSaving] = useState(false);

  const addAction = () => {
    const newAction: ActionConfig = {
      id: `action_${Date.now()}`,
      type: 'generate_content',
      contentType: 'social',
      contentTone: 'professional',
    };
    setActions([...actions, newAction]);
  };

  const updateAction = (index: number, action: ActionConfig) => {
    const newActions = [...actions];
    newActions[index] = action;
    setActions(newActions);
  };

  const removeAction = (index: number) => {
    setActions(actions.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error('Inserisci un nome per il workflow');
      return;
    }
    if (actions.length === 0) {
      toast.error('Aggiungi almeno un\'azione');
      return;
    }

    setIsSaving(true);
    try {
      await onSave({
        id: workflow?.id,
        name,
        description,
        trigger,
        actions,
      });
      onClose();
    } catch (error) {
      toast.error('Errore nel salvataggio');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className={`${cardBg} rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className={`text-xl font-bold ${textPrimary}`}>
            {workflow ? 'Modifica Workflow' : 'Nuovo Workflow'}
          </h2>
          <button onClick={onClose} className={textSecondary}>
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Nome e Descrizione */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                Nome Workflow *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="es: Post Settimanale LinkedIn"
                className={`w-full px-4 py-2 rounded-lg border ${inputBg}`}
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                Descrizione
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Breve descrizione..."
                className={`w-full px-4 py-2 rounded-lg border ${inputBg}`}
              />
            </div>
          </div>

          {/* Trigger Editor */}
          <div className={`p-4 rounded-xl ${isDark ? 'bg-white/5' : 'bg-orange-50'}`}>
            <TriggerEditor trigger={trigger} onChange={setTrigger} isDark={isDark} />
          </div>

          {/* Actions */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className={`font-medium flex items-center gap-2 ${textPrimary}`}>
                <Settings className="w-4 h-4 text-orange-400" />
                Azioni ({actions.length})
              </h4>
              <Button size="sm" onClick={addAction} className="bg-orange-600 hover:bg-orange-700">
                <Plus className="w-4 h-4 mr-1" />
                Aggiungi Azione
              </Button>
            </div>

            {actions.length === 0 ? (
              <div className={`text-center py-8 border-2 border-dashed rounded-xl ${isDark ? 'border-white/20' : 'border-gray-300'}`}>
                <p className={textSecondary}>Nessuna azione configurata</p>
                <p className={`text-sm ${textSecondary}`}>Clicca "Aggiungi Azione" per iniziare</p>
              </div>
            ) : (
              <div className="space-y-3">
                {actions.map((action, index) => (
                  <ActionEditor
                    key={action.id}
                    action={action}
                    onChange={(a) => updateAction(index, a)}
                    onRemove={() => removeAction(index)}
                    index={index}
                    isDark={isDark}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-white/10">
          <Button variant="outline" onClick={onClose}>
            Annulla
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="bg-orange-600 hover:bg-orange-700"
          >
            {isSaving ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Salvataggio...</>
            ) : (
              <><Save className="w-4 h-4 mr-2" /> Salva Workflow</>
            )}
          </Button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function WorkflowBuilder() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // State
  const [workflows, setWorkflows] = useState<WorkflowData[]>([]);
  const [templates, setTemplates] = useState<WorkflowData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowData | null>(null);
  const [executions, setExecutions] = useState<ExecutionLog[]>([]);
  const [isRunning, setIsRunning] = useState<string | null>(null);
  const [showEditor, setShowEditor] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<WorkflowData | null>(null);

  // Styles
  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  // Load data
  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [wfs, tpls] = await Promise.all([
        WorkflowApiService.listWorkflows(),
        WorkflowApiService.getTemplates(),
      ]);
      setWorkflows(wfs);
      setTemplates(tpls);
    } catch (error) {
      console.error('Error loading workflows:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  useEffect(() => {
    if (selectedWorkflow) {
      WorkflowApiService.getExecutions(selectedWorkflow.id)
        .then(setExecutions)
        .catch(() => setExecutions([]));
    }
  }, [selectedWorkflow]);

  // Handlers
  const handleSaveWorkflow = async (data: Partial<WorkflowData>) => {
    if (data.id) {
      await WorkflowApiService.updateWorkflow(data.id, data);
      toast.success('Workflow aggiornato!');
    } else {
      await WorkflowApiService.createWorkflow(data);
      toast.success('Workflow creato!');
    }
    await loadData();
  };

  const handleEdit = (workflow: WorkflowData) => {
    setEditingWorkflow(workflow);
    setShowEditor(true);
  };

  const handleCreate = () => {
    setEditingWorkflow(null);
    setShowEditor(true);
  };

  const handleToggleStatus = async (workflow: WorkflowData) => {
    try {
      if (workflow.status === 'active') {
        await WorkflowApiService.pauseWorkflow(workflow.id);
        toast.success('Workflow in pausa');
      } else {
        await WorkflowApiService.activateWorkflow(workflow.id);
        toast.success('Workflow attivato!');
      }
      await loadData();
    } catch (error) {
      toast.error('Errore nel cambio stato');
    }
  };

  const handleRun = async (workflow: WorkflowData) => {
    setIsRunning(workflow.id);
    try {
      const exec = await WorkflowApiService.runWorkflow(workflow.id);
      toast.success(`Esecuzione: ${exec.status}`);
      await loadData();
    } catch (error) {
      toast.error('Errore nell\'esecuzione');
    } finally {
      setIsRunning(null);
    }
  };

  const handleDelete = async (workflow: WorkflowData) => {
    if (!confirm(`Eliminare "${workflow.name}"?`)) return;
    try {
      await WorkflowApiService.deleteWorkflow(workflow.id);
      toast.success('Workflow eliminato');
      if (selectedWorkflow?.id === workflow.id) setSelectedWorkflow(null);
      await loadData();
    } catch (error) {
      toast.error('Errore nell\'eliminazione');
    }
  };

  const formatTrigger = (trigger: TriggerConfig) => {
    if (trigger.type === 'schedule') {
      const days = trigger.days?.map(d => DAYS_OF_WEEK[d]?.short).join(', ') || 'Tutti i giorni';
      return `${trigger.frequency === 'daily' ? 'Ogni giorno' : trigger.frequency === 'weekly' ? 'Settimanale' : 'Mensile'} - ${days} ore ${trigger.hour}:${trigger.minute?.toString().padStart(2, '0')}`;
    }
    return trigger.type;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-orange-500/20">
              <Workflow className="w-6 h-6 text-orange-400" />
            </div>
            <div>
              <h2 className={`text-xl font-bold ${textPrimary}`}>Workflow Automation</h2>
              <p className={textSecondary}>Crea e gestisci automazioni personalizzate</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={loadData} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Aggiorna
            </Button>
            <Button onClick={handleCreate} className="bg-orange-600 hover:bg-orange-700">
              <Plus className="w-4 h-4 mr-2" />
              Crea Workflow
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>{workflows.length}</div>
            <div className={textSecondary}>Totali</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-green-400">
              {workflows.filter(w => w.status === 'active').length}
            </div>
            <div className={textSecondary}>Attivi</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>
              {workflows.reduce((sum, w) => sum + w.execution_count, 0)}
            </div>
            <div className={textSecondary}>Esecuzioni</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>{templates.length}</div>
            <div className={textSecondary}>Templates</div>
          </div>
        </div>
      </div>

      {/* Workflow List */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <h3 className={`font-semibold mb-4 ${textPrimary}`}>📋 I Tuoi Workflow</h3>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-orange-400" />
          </div>
        ) : workflows.length === 0 ? (
          <div className={`text-center py-8 ${textSecondary}`}>
            <Workflow className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Nessun workflow creato</p>
            <p className="text-sm mt-1">Clicca "Crea Workflow" per iniziare</p>
          </div>
        ) : (
          <div className="space-y-3">
            {workflows.map((workflow) => (
              <motion.div
                key={workflow.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-4 rounded-lg transition-colors ${isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'
                  }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className={`font-medium ${textPrimary}`}>{workflow.name}</span>
                      <StatusBadge status={workflow.status} />
                    </div>
                    <p className={`text-sm ${textSecondary}`}>
                      {formatTrigger(workflow.trigger as TriggerConfig)} • {workflow.actions.length} azioni • {workflow.execution_count} esecuzioni
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleEdit(workflow)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleToggleStatus(workflow)}
                      className={workflow.status === 'active' ? 'text-yellow-400' : 'text-green-400'}
                    >
                      {workflow.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRun(workflow)}
                      disabled={isRunning === workflow.id}
                    >
                      {isRunning === workflow.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Zap className="w-4 h-4" />
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(workflow)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Editor Modal */}
      <AnimatePresence>
        {showEditor && (
          <WorkflowEditorModal
            workflow={editingWorkflow}
            onSave={handleSaveWorkflow}
            onClose={() => setShowEditor(false)}
            isDark={isDark}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default WorkflowBuilder;
