/**
 * Webhook Manager - Gestione integrazioni webhook.
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Webhook, Plus, Trash2, RefreshCw, ChevronRight, CheckCircle,
  XCircle, Loader2, X, Play, Pause, Zap, Copy, Eye, EyeOff
} from 'lucide-react';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';

// Types
interface WebhookData {
  id: string;
  name: string;
  url: string;
  events: string[];
  status: string;
  success_count: number;
  failure_count: number;
  last_triggered?: string;
  created_at: string;
  secret?: string;
}

interface Delivery {
  id: string;
  event: string;
  success: boolean;
  response_status?: number;
  duration_ms: number;
  created_at: string;
  error?: string;
}

// API Service
const WebhookApi = {
  baseUrl: '/api/v1/marketing/webhooks',

  getHeaders() {
    return {
      'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
      'Content-Type': 'application/json',
    };
  },

  async list(): Promise<WebhookData[]> {
    const res = await fetch(this.baseUrl, { headers: this.getHeaders() });
    return res.ok ? res.json() : [];
  },

  async create(data: any): Promise<WebhookData> {
    const res = await fetch(this.baseUrl, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed');
    return res.json();
  },

  async delete(id: string): Promise<void> {
    await fetch(`${this.baseUrl}/${id}`, { method: 'DELETE', headers: this.getHeaders() });
  },

  async toggle(id: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/${id}/toggle`, { method: 'POST', headers: this.getHeaders() });
    return res.json();
  },

  async test(id: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/${id}/test`, { method: 'POST', headers: this.getHeaders() });
    return res.json();
  },

  async getDeliveries(id: string): Promise<Delivery[]> {
    const res = await fetch(`${this.baseUrl}/${id}/deliveries`, { headers: this.getHeaders() });
    return res.ok ? res.json() : [];
  },

  async getEvents(): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/meta/events`, { headers: this.getHeaders() });
    return res.ok ? res.json() : [];
  },
};

// Event options
const EVENTS = [
  { value: 'lead.created', label: '👤 Lead Creato' },
  { value: 'lead.updated', label: '✏️ Lead Aggiornato' },
  { value: 'lead.converted', label: '🎯 Lead Convertito' },
  { value: 'campaign.sent', label: '📧 Campagna Inviata' },
  { value: 'email.opened', label: '👁️ Email Aperta' },
  { value: 'email.clicked', label: '🖱️ Email Cliccata' },
  { value: 'post.published', label: '📱 Post Pubblicato' },
  { value: 'workflow.completed', label: '⚡ Workflow Completato' },
  { value: 'ab_test.completed', label: '🧪 A/B Test Completato' },
];

export function WebhookManager() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [webhooks, setWebhooks] = useState<WebhookData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedWebhook, setSelectedWebhook] = useState<WebhookData | null>(null);
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [isTesting, setIsTesting] = useState<string | null>(null);
  const [showSecret, setShowSecret] = useState(false);

  // Create form
  const [newName, setNewName] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [newEvents, setNewEvents] = useState<string[]>([]);
  const [createdSecret, setCreatedSecret] = useState('');

  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark ? 'bg-[#1A1A1A] border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await WebhookApi.list();
      setWebhooks(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  useEffect(() => {
    if (selectedWebhook) {
      WebhookApi.getDeliveries(selectedWebhook.id).then(setDeliveries);
    }
  }, [selectedWebhook]);

  const handleCreate = async () => {
    if (!newName.trim() || !newUrl.trim() || newEvents.length === 0) {
      toast.error('Compila tutti i campi e seleziona almeno un evento');
      return;
    }
    try {
      const created = await WebhookApi.create({
        name: newName,
        url: newUrl,
        events: newEvents,
      });
      toast.success('Webhook creato!');
      setCreatedSecret(created.secret || '');
      setNewName('');
      setNewUrl('');
      setNewEvents([]);
      await loadData();
    } catch (e) {
      toast.error('Errore');
    }
  };

  const handleToggle = async (webhook: WebhookData) => {
    await WebhookApi.toggle(webhook.id);
    toast.success(webhook.status === 'active' ? 'Webhook disattivato' : 'Webhook attivato');
    await loadData();
  };

  const handleTest = async (webhook: WebhookData) => {
    setIsTesting(webhook.id);
    try {
      const result = await WebhookApi.test(webhook.id);
      if (result.success) {
        toast.success(`Test OK! Status: ${result.response_status}, ${result.duration_ms}ms`);
      } else {
        toast.error(`Test fallito: ${result.error || 'Errore sconosciuto'}`);
      }
    } catch (e) {
      toast.error('Errore nel test');
    } finally {
      setIsTesting(null);
    }
  };

  const handleDelete = async (webhook: WebhookData) => {
    if (!confirm(`Eliminare "${webhook.name}"?`)) return;
    await WebhookApi.delete(webhook.id);
    toast.success('Eliminato');
    setSelectedWebhook(null);
    await loadData();
  };

  const toggleEvent = (event: string) => {
    setNewEvents(prev =>
      prev.includes(event) ? prev.filter(e => e !== event) : [...prev, event]
    );
  };

  const copySecret = () => {
    navigator.clipboard.writeText(createdSecret);
    toast.success('Secret copiato!');
  };

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString('it-IT', {
      day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-indigo-500/20">
              <Webhook className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h2 className={`text-xl font-bold ${textPrimary}`}>Webhook Manager</h2>
              <p className={textSecondary}>Integra con servizi esterni</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={loadData} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button onClick={() => setShowCreate(true)} className="bg-indigo-600 hover:bg-indigo-700">
              <Plus className="w-4 h-4 mr-2" />
              Nuovo Webhook
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>{webhooks.length}</div>
            <div className={textSecondary}>Totali</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-green-400">
              {webhooks.filter(w => w.status === 'active').length}
            </div>
            <div className={textSecondary}>Attivi</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-green-400">
              {webhooks.reduce((sum, w) => sum + w.success_count, 0)}
            </div>
            <div className={textSecondary}>Successi</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-red-400">
              {webhooks.reduce((sum, w) => sum + w.failure_count, 0)}
            </div>
            <div className={textSecondary}>Falliti</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Webhook List */}
        <div className={`lg:col-span-2 ${cardBg} rounded-xl p-6`}>
          <h3 className={`font-semibold mb-4 ${textPrimary}`}>🔗 I Tuoi Webhook</h3>

          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
            </div>
          ) : webhooks.length === 0 ? (
            <div className={`text-center py-8 ${textSecondary}`}>
              <Webhook className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Nessun webhook configurato</p>
            </div>
          ) : (
            <div className="space-y-3">
              {webhooks.map(webhook => (
                <motion.div
                  key={webhook.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-4 rounded-lg cursor-pointer transition-colors ${selectedWebhook?.id === webhook.id
                      ? 'bg-indigo-500/20 border border-indigo-500/50'
                      : isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  onClick={() => setSelectedWebhook(webhook)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`font-medium ${textPrimary}`}>{webhook.name}</span>
                        <span className={`w-2 h-2 rounded-full ${webhook.status === 'active' ? 'bg-green-400' : 'bg-gray-400'
                          }`} />
                      </div>
                      <div className={`text-sm ${textSecondary} truncate`}>{webhook.url}</div>
                      <div className="flex gap-2 mt-2">
                        {webhook.events.slice(0, 3).map(e => (
                          <span key={e} className="px-2 py-0.5 text-xs rounded bg-indigo-500/20 text-indigo-300">
                            {e.split('.')[1]}
                          </span>
                        ))}
                        {webhook.events.length > 3 && (
                          <span className={`text-xs ${textSecondary}`}>+{webhook.events.length - 3}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right text-xs mr-2">
                        <div className="text-green-400">{webhook.success_count} ✓</div>
                        <div className="text-red-400">{webhook.failure_count} ✗</div>
                      </div>
                      <ChevronRight className={`w-4 h-4 ${textSecondary}`} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Detail Panel */}
        <div className={`${cardBg} rounded-xl p-6`}>
          {selectedWebhook ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <h3 className={`font-semibold ${textPrimary}`}>{selectedWebhook.name}</h3>
                <span className={`w-2 h-2 rounded-full ${selectedWebhook.status === 'active' ? 'bg-green-400' : 'bg-gray-400'
                  }`} />
              </div>

              <div className={`text-sm mb-4 p-2 rounded ${isDark ? 'bg-white/5' : 'bg-gray-100'} ${textSecondary} truncate`}>
                {selectedWebhook.url}
              </div>

              {/* Actions */}
              <div className="flex gap-2 mb-6">
                <Button
                  size="sm"
                  onClick={() => handleToggle(selectedWebhook)}
                  className={selectedWebhook.status === 'active' ? 'bg-yellow-600' : 'bg-green-600'}
                >
                  {selectedWebhook.status === 'active' ? <Pause className="w-4 h-4 mr-1" /> : <Play className="w-4 h-4 mr-1" />}
                  {selectedWebhook.status === 'active' ? 'Disattiva' : 'Attiva'}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleTest(selectedWebhook)}
                  disabled={isTesting === selectedWebhook.id}
                >
                  {isTesting === selectedWebhook.id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <><Zap className="w-4 h-4 mr-1" /> Test</>
                  )}
                </Button>
                <Button size="sm" variant="ghost" onClick={() => handleDelete(selectedWebhook)} className="text-red-400">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              {/* Events */}
              <div className="mb-6">
                <h4 className={`text-sm font-medium mb-2 ${textSecondary}`}>Eventi ({selectedWebhook.events.length})</h4>
                <div className="flex flex-wrap gap-1">
                  {selectedWebhook.events.map(e => (
                    <span key={e} className="px-2 py-1 text-xs rounded bg-indigo-500/20 text-indigo-300">
                      {EVENTS.find(ev => ev.value === e)?.label || e}
                    </span>
                  ))}
                </div>
              </div>

              {/* Recent Deliveries */}
              <div>
                <h4 className={`text-sm font-medium mb-2 ${textSecondary}`}>Ultimi Invii</h4>
                {deliveries.length === 0 ? (
                  <p className={`text-sm ${textSecondary}`}>Nessun invio</p>
                ) : (
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {deliveries.slice(0, 10).map(d => (
                      <div
                        key={d.id}
                        className={`text-xs p-2 rounded flex items-center justify-between ${isDark ? 'bg-white/5' : 'bg-gray-50'
                          }`}
                      >
                        <div className="flex items-center gap-2">
                          {d.success ? (
                            <CheckCircle className="w-3 h-3 text-green-400" />
                          ) : (
                            <XCircle className="w-3 h-3 text-red-400" />
                          )}
                          <span className={textSecondary}>{d.event}</span>
                        </div>
                        <span className={textSecondary}>{d.duration_ms}ms</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className={`text-center py-8 ${textSecondary}`}>
              <Webhook className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Seleziona un webhook</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      <AnimatePresence>
        {showCreate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
            onClick={() => { setShowCreate(false); setCreatedSecret(''); }}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className={`${cardBg} rounded-2xl p-6 w-full max-w-lg`}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className={`text-lg font-bold ${textPrimary}`}>Nuovo Webhook</h3>
                <button onClick={() => { setShowCreate(false); setCreatedSecret(''); }}>
                  <X className="w-5 h-5" />
                </button>
              </div>

              {createdSecret ? (
                // Secret display after creation
                <div className="space-y-4">
                  <div className={`p-4 rounded-lg bg-green-500/10 border border-green-500/50`}>
                    <p className="text-green-400 font-medium mb-2">✅ Webhook creato!</p>
                    <p className={`text-sm ${textSecondary} mb-3`}>
                      Salva questo secret per verificare le richieste (mostrato solo ora):
                    </p>
                    <div className="flex items-center gap-2">
                      <code className={`flex-1 p-2 rounded text-sm ${isDark ? 'bg-black' : 'bg-gray-100'}`}>
                        {showSecret ? createdSecret : '••••••••••••••••'}
                      </code>
                      <button onClick={() => setShowSecret(!showSecret)}>
                        {showSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button onClick={copySecret}>
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <Button
                    onClick={() => { setShowCreate(false); setCreatedSecret(''); }}
                    className="w-full bg-indigo-600"
                  >
                    Chiudi
                  </Button>
                </div>
              ) : (
                // Create form
                <div className="space-y-4">
                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Nome *</label>
                    <input
                      type="text"
                      value={newName}
                      onChange={e => setNewName(e.target.value)}
                      placeholder="es: Slack Notifications"
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    />
                  </div>

                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>URL Endpoint *</label>
                    <input
                      type="url"
                      value={newUrl}
                      onChange={e => setNewUrl(e.target.value)}
                      placeholder="https://your-service.com/webhook"
                      className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                    />
                  </div>

                  <div>
                    <label className={`block text-sm mb-2 ${textSecondary}`}>Eventi *</label>
                    <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                      {EVENTS.map(event => (
                        <button
                          key={event.value}
                          onClick={() => toggleEvent(event.value)}
                          className={`p-2 text-left text-sm rounded-lg transition-colors ${newEvents.includes(event.value)
                              ? 'bg-indigo-500 text-white'
                              : isDark ? 'bg-white/5 text-gray-300 hover:bg-white/10' : 'bg-gray-100 hover:bg-gray-200'
                            }`}
                        >
                          {event.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2 mt-6">
                    <Button variant="outline" onClick={() => setShowCreate(false)} className="flex-1">
                      Annulla
                    </Button>
                    <Button onClick={handleCreate} className="flex-1 bg-indigo-600 hover:bg-indigo-700">
                      Crea Webhook
                    </Button>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default WebhookManager;
