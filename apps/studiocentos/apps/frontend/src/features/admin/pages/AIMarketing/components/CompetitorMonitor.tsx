/**
 * Competitor Monitor - Tracciamento competitor marketing.
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Eye, Plus, Trash2, RefreshCw, ChevronRight, ExternalLink,
  Loader2, X, Bell, TrendingUp, Users, Globe, AlertTriangle,
  Linkedin, Instagram, Facebook, Twitter
} from 'lucide-react';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';

// Types
interface CompetitorMetrics {
  followers: number;
  engagement: number;
}

interface Competitor {
  id: string;
  name: string;
  website: string;
  status: string;
  social_profiles: Record<string, string>;
  keywords: string[];
  last_checked?: string;
  metrics_summary: Record<string, CompetitorMetrics>;
}

interface Alert {
  id: string;
  competitor_id: string;
  type: string;
  title: string;
  description: string;
  severity: string;
  read: boolean;
  created_at: string;
}

// API Service
const CompetitorApi = {
  baseUrl: '/api/v1/marketing/competitors',

  getHeaders() {
    return {
      'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
      'Content-Type': 'application/json',
    };
  },

  async list(): Promise<Competitor[]> {
    const res = await fetch(this.baseUrl, { headers: this.getHeaders() });
    return res.ok ? res.json() : [];
  },

  async getSummary(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/summary`, { headers: this.getHeaders() });
    return res.ok ? res.json() : {};
  },

  async create(data: any): Promise<Competitor> {
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

  async getAlerts(unreadOnly = false): Promise<Alert[]> {
    const res = await fetch(`${this.baseUrl}/alerts/?unread_only=${unreadOnly}`, { headers: this.getHeaders() });
    return res.ok ? res.json() : [];
  },

  async markAlertRead(id: string): Promise<void> {
    await fetch(`${this.baseUrl}/alerts/${id}/read`, { method: 'POST', headers: this.getHeaders() });
  },

  async getComparison(): Promise<any> {
    const res = await fetch(`${this.baseUrl}/compare`, { headers: this.getHeaders() });
    return res.ok ? res.json() : {};
  },
};

// Platform Icon
function PlatformIcon({ platform }: { platform: string }) {
  const icons: Record<string, typeof Globe> = {
    linkedin: Linkedin,
    instagram: Instagram,
    facebook: Facebook,
    twitter: Twitter,
  };
  const Icon = icons[platform] || Globe;
  return <Icon className="w-4 h-4" />;
}

export function CompetitorMonitor() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<any>({});
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showAlerts, setShowAlerts] = useState(false);
  const [selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null);

  // Create form
  const [newName, setNewName] = useState('');
  const [newWebsite, setNewWebsite] = useState('');
  const [newKeywords, setNewKeywords] = useState('');
  const [newProfiles, setNewProfiles] = useState({ linkedin: '', instagram: '', facebook: '', twitter: '' });

  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark ? 'bg-[#1A1A1A] border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [comps, summ, alts] = await Promise.all([
        CompetitorApi.list(),
        CompetitorApi.getSummary(),
        CompetitorApi.getAlerts(true),
      ]);
      setCompetitors(comps);
      setSummary(summ);
      setAlerts(alts);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleCreate = async () => {
    if (!newName.trim()) {
      toast.error('Inserisci nome competitor');
      return;
    }
    try {
      const profiles: Record<string, string> = {};
      Object.entries(newProfiles).forEach(([k, v]) => {
        if (v.trim()) profiles[k] = v;
      });

      await CompetitorApi.create({
        name: newName,
        website: newWebsite,
        social_profiles: profiles,
        keywords: newKeywords.split(',').map(k => k.trim()).filter(Boolean),
      });

      toast.success('Competitor aggiunto!');
      setShowCreate(false);
      setNewName('');
      setNewWebsite('');
      setNewKeywords('');
      setNewProfiles({ linkedin: '', instagram: '', facebook: '', twitter: '' });
      await loadData();
    } catch (e) {
      toast.error('Errore');
    }
  };

  const handleDelete = async (comp: Competitor) => {
    if (!confirm(`Eliminare "${comp.name}"?`)) return;
    await CompetitorApi.delete(comp.id);
    toast.success('Eliminato');
    setSelectedCompetitor(null);
    await loadData();
  };

  const handleMarkRead = async (alert: Alert) => {
    await CompetitorApi.markAlertRead(alert.id);
    setAlerts(alerts.filter(a => a.id !== alert.id));
  };

  const formatNumber = (n: number) => {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-cyan-500/20">
              <Eye className="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <h2 className={`text-xl font-bold ${textPrimary}`}>Competitor Monitor</h2>
              <p className={textSecondary}>Traccia e analizza i tuoi competitor</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAlerts(true)}
              className="relative"
            >
              <Bell className="w-4 h-4 mr-2" />
              Alert
              {alerts.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center text-white">
                  {alerts.length}
                </span>
              )}
            </Button>
            <Button variant="outline" size="sm" onClick={loadData} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button onClick={() => setShowCreate(true)} className="bg-cyan-600 hover:bg-cyan-700">
              <Plus className="w-4 h-4 mr-2" />
              Aggiungi
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>{summary.total_competitors || 0}</div>
            <div className={textSecondary}>Competitor</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-green-400">{summary.active_competitors || 0}</div>
            <div className={textSecondary}>Attivi</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-orange-400">{summary.unread_alerts || 0}</div>
            <div className={textSecondary}>Alert</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>{summary.recent_content_count || 0}</div>
            <div className={textSecondary}>Contenuti 7gg</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Competitor List */}
        <div className={`lg:col-span-2 ${cardBg} rounded-xl p-6`}>
          <h3 className={`font-semibold mb-4 ${textPrimary}`}>👁️ Competitor Tracciati</h3>

          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            </div>
          ) : competitors.length === 0 ? (
            <div className={`text-center py-8 ${textSecondary}`}>
              <Eye className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Nessun competitor</p>
              <p className="text-sm">Aggiungi il tuo primo competitor</p>
            </div>
          ) : (
            <div className="space-y-3">
              {competitors.map(comp => (
                <motion.div
                  key={comp.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-4 rounded-lg cursor-pointer transition-colors ${selectedCompetitor?.id === comp.id
                      ? 'bg-cyan-500/20 border border-cyan-500/50'
                      : isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  onClick={() => setSelectedCompetitor(comp)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg ${isDark ? 'bg-white/10' : 'bg-gray-200'} flex items-center justify-center`}>
                        <span className="text-lg font-bold">{comp.name[0]}</span>
                      </div>
                      <div>
                        <div className={`font-medium ${textPrimary}`}>{comp.name}</div>
                        {comp.website && (
                          <a href={comp.website} target="_blank" rel="noopener noreferrer"
                            className={`text-sm ${textSecondary} flex items-center gap-1 hover:text-cyan-400`}>
                            <Globe className="w-3 h-3" />
                            {comp.website.replace(/https?:\/\//, '').split('/')[0]}
                          </a>
                        )}
                      </div>
                    </div>
                    <ChevronRight className={`w-4 h-4 ${textSecondary}`} />
                  </div>

                  {/* Social metrics preview */}
                  <div className="flex gap-3 mt-2">
                    {Object.entries(comp.metrics_summary || {}).map(([platform, metrics]) => (
                      <div key={platform} className={`flex items-center gap-1 text-xs ${textSecondary}`}>
                        <PlatformIcon platform={platform} />
                        <span>{formatNumber(metrics.followers)}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Detail Panel */}
        <div className={`${cardBg} rounded-xl p-6`}>
          {selectedCompetitor ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <h3 className={`font-semibold ${textPrimary}`}>{selectedCompetitor.name}</h3>
                <Button size="sm" variant="ghost" onClick={() => handleDelete(selectedCompetitor)} className="text-red-400">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              {selectedCompetitor.website && (
                <a href={selectedCompetitor.website} target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-2 text-cyan-400 mb-4 text-sm">
                  <ExternalLink className="w-4 h-4" />
                  {selectedCompetitor.website}
                </a>
              )}

              {/* Keywords */}
              {selectedCompetitor.keywords?.length > 0 && (
                <div className="mb-4">
                  <h4 className={`text-sm font-medium mb-2 ${textSecondary}`}>Keywords</h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedCompetitor.keywords.map((kw, i) => (
                      <span key={i} className="px-2 py-1 text-xs rounded bg-cyan-500/20 text-cyan-400">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Social Metrics */}
              <div>
                <h4 className={`text-sm font-medium mb-2 ${textSecondary}`}>Metriche Social</h4>
                <div className="space-y-2">
                  {Object.entries(selectedCompetitor.metrics_summary || {}).map(([platform, metrics]) => (
                    <div key={platform} className={`p-3 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <PlatformIcon platform={platform} />
                          <span className={textPrimary}>{platform}</span>
                        </div>
                        <div className="text-right">
                          <div className={`font-medium ${textPrimary}`}>
                            <Users className="w-3 h-3 inline mr-1" />
                            {formatNumber(metrics.followers)}
                          </div>
                          <div className={`text-xs ${textSecondary}`}>
                            <TrendingUp className="w-3 h-3 inline mr-1" />
                            {metrics.engagement?.toFixed(1)}% eng
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {Object.keys(selectedCompetitor.metrics_summary || {}).length === 0 && (
                    <p className={`text-sm ${textSecondary}`}>Nessuna metrica ancora</p>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className={`text-center py-8 ${textSecondary}`}>
              <Eye className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Seleziona un competitor</p>
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
            onClick={() => setShowCreate(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className={`${cardBg} rounded-2xl p-6 w-full max-w-lg`}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className={`text-lg font-bold ${textPrimary}`}>Aggiungi Competitor</h3>
                <button onClick={() => setShowCreate(false)}><X className="w-5 h-5" /></button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>Nome *</label>
                  <input
                    type="text"
                    value={newName}
                    onChange={e => setNewName(e.target.value)}
                    placeholder="es: Competitor XYZ"
                    className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                  />
                </div>

                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>Website</label>
                  <input
                    type="url"
                    value={newWebsite}
                    onChange={e => setNewWebsite(e.target.value)}
                    placeholder="https://competitor.com"
                    className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                  />
                </div>

                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>Profili Social</label>
                  <div className="grid grid-cols-2 gap-2">
                    {(['linkedin', 'instagram', 'facebook', 'twitter'] as const).map(p => (
                      <input
                        key={p}
                        type="text"
                        value={newProfiles[p]}
                        onChange={e => setNewProfiles({ ...newProfiles, [p]: e.target.value })}
                        placeholder={p}
                        className={`px-3 py-2 rounded-lg border text-sm ${inputBg}`}
                      />
                    ))}
                  </div>
                </div>

                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>Keywords (comma-separated)</label>
                  <input
                    type="text"
                    value={newKeywords}
                    onChange={e => setNewKeywords(e.target.value)}
                    placeholder="marketing, digital, AI"
                    className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                  />
                </div>
              </div>

              <div className="flex gap-2 mt-6">
                <Button variant="outline" onClick={() => setShowCreate(false)} className="flex-1">Annulla</Button>
                <Button onClick={handleCreate} className="flex-1 bg-cyan-600 hover:bg-cyan-700">Aggiungi</Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Alerts Modal */}
      <AnimatePresence>
        {showAlerts && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
            onClick={() => setShowAlerts(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className={`${cardBg} rounded-2xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto`}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className={`text-lg font-bold ${textPrimary}`}>🔔 Alert Competitor</h3>
                <button onClick={() => setShowAlerts(false)}><X className="w-5 h-5" /></button>
              </div>

              {alerts.length === 0 ? (
                <p className={`text-center py-8 ${textSecondary}`}>Nessun alert</p>
              ) : (
                <div className="space-y-3">
                  {alerts.map(alert => (
                    <div key={alert.id} className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-2">
                          <AlertTriangle className={`w-4 h-4 mt-1 ${alert.severity === 'important' ? 'text-red-400' :
                              alert.severity === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                            }`} />
                          <div>
                            <div className={`font-medium ${textPrimary}`}>{alert.title}</div>
                            <p className={`text-sm ${textSecondary}`}>{alert.description}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => handleMarkRead(alert)}
                          className={`text-xs ${textSecondary} hover:text-green-400`}
                        >
                          ✓ Letto
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default CompetitorMonitor;
