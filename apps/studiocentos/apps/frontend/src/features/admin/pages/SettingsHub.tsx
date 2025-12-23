/**
 * Settings Hub - Centro Impostazioni
 * Unifica: Utenti + Profilo + Integrazioni + Sistema
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  User,
  Settings,
  Link2,
  Shield,
  Bell,
  Database,
  Key,
  Globe,
  Mail,
  Inbox,
  Smartphone,
  Lock,
  Eye,
  EyeOff,
  Plus,
  Edit2,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  Save,
  RefreshCw,
  ExternalLink,
  Copy,
  Webhook,
  Zap,
  Cloud,
  HardDrive,
  Activity,
  Calendar,
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { EmailInbox } from '../components/EmailInbox';

// Types
interface UserAccount {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'editor' | 'viewer';
  status: 'active' | 'inactive' | 'pending';
  last_login?: string;
  created_at: string;
  two_factor_enabled: boolean;
}

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'connected' | 'disconnected' | 'error';
  lastSync?: string;
  config?: Record<string, any>;
}

interface SystemLog {
  id: number;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
  source: string;
}

const ROLES = {
  admin: { label: 'Amministratore', color: 'bg-gold' },
  editor: { label: 'Editor', color: 'bg-gold' },
  viewer: { label: 'Visualizzatore', color: 'bg-gray-500' },
};

// Tab configuration
const TABS = [
  { id: 'users', label: 'Utenti', icon: Users, color: 'from-blue-500 to-cyan-500' },
  { id: 'profile', label: 'Profilo', icon: User, color: 'from-purple-500 to-indigo-500' },
  { id: 'integrations', label: 'Integrazioni', icon: Link2, color: 'from-emerald-500 to-teal-500' },
  { id: 'email', label: 'Email', icon: Inbox, color: 'from-amber-500 to-yellow-500' },
  { id: 'system', label: 'Sistema', icon: Settings, color: 'from-gray-500 to-slate-500' },
] as const;

export function SettingsHub() {
  const [activeTab, setActiveTab] = useState<typeof TABS[number]['id']>('users');
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  // Theme classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-300 text-gray-900';
  const tabBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-100 border-gray-200';

  // State
  const [users, setUsers] = useState<UserAccount[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddUserModal, setShowAddUserModal] = useState(false);

  // Profile State - initialized empty, loaded from API
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    timezone: 'Europe/Rome',
    language: 'it',
    notifications_email: true,
    notifications_push: true,
    two_factor: false,
  });

  // Fetch data
  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const headers = { Authorization: `Bearer ${token}` };

      if (activeTab === 'users') {
        const res = await fetch('/api/v1/admin/users?page=1&page_size=50', { headers });
        if (res.ok) {
          const data = await res.json();
          setUsers(data.items || data || []);
        }
      }

      if (activeTab === 'profile') {
        // Load admin profile
        const res = await fetch('/api/v1/admin/settings', { headers });
        if (res.ok) {
          const data = await res.json();
          setProfile(prev => ({
            ...prev,
            name: data.site_name || data.company_name || prev.name,
            email: data.contact_email || prev.email,
            phone: data.contact_phone || prev.phone,
            company: data.company_name || prev.company,
          }));
        }
      }

      if (activeTab === 'integrations') {
        // Load Google connection status
        const googleRes = await fetch('/api/v1/admin/google/status', { headers });
        let googleStatus = { analytics_connected: false, business_profile_connected: false };
        if (googleRes.ok) {
          googleStatus = await googleRes.json();
        }

        // Load Google Calendar status
        const calendarRes = await fetch('/api/v1/admin/google/calendar/status', { headers });
        let calendarStatus = { connected: false };
        if (calendarRes.ok) {
          calendarStatus = await calendarRes.json();
        }

        // Load general settings
        const res = await fetch('/api/v1/admin/settings', { headers });
        let settingsData = {};
        if (res.ok) {
          settingsData = await res.json();
        }

        // Determina se Google è connesso (basta uno dei servizi)
        const googleConnected = googleStatus.analytics_connected ||
          googleStatus.business_profile_connected ||
          calendarStatus.connected;

        // Build integrations list - Google UNIFICATO in un solo blocco
        const integrationsData: Integration[] = [
          {
            id: 'google',
            name: 'Google Services',
            description: 'Analytics, Business Profile, Calendar - UN SOLO accesso',
            icon: '🔗',
            status: googleConnected ? 'connected' : 'disconnected',
            config: {
              analytics: googleStatus.analytics_connected,
              business: googleStatus.business_profile_connected,
              calendar: calendarStatus.connected,
            }
          },
          {
            id: 'stripe',
            name: 'Stripe',
            description: 'Pagamenti online',
            icon: '💳',
            status: (settingsData as any).stripe_enabled ? 'connected' : 'disconnected'
          },
          {
            id: 'meta',
            name: 'Meta Business',
            description: 'Facebook & Instagram',
            icon: '📱',
            status: (settingsData as any).meta_enabled || (settingsData as any).facebook_enabled ? 'connected' : 'disconnected'
          },
        ];
        setIntegrations(integrationsData);
      }

      if (activeTab === 'system') {
        // Load system logs
        const res = await fetch('/api/v1/admin/logs?limit=10', { headers });
        if (res.ok) {
          const data = await res.json();
          setLogs((data.items || data || []).map((log: any) => ({
            id: log.id,
            type: log.level === 'ERROR' ? 'error' : log.level === 'WARNING' ? 'warning' : 'info',
            message: log.message,
            timestamp: log.timestamp || log.created_at,
            source: log.source || log.logger || 'system',
          })));
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const handleSaveProfile = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const res = await fetch('/api/v1/admin/settings/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          display_name: profile.name,
          timezone: profile.timezone,
          language: profile.language,
        }),
      });

      if (res.ok) {
        // Also save notification preferences
        await fetch('/api/v1/admin/settings/notifications', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            email_on_new_booking: profile.notifications_email,
            push_enabled: profile.notifications_push,
          }),
        });

        toast.success('Profilo aggiornato con successo!');
      } else {
        toast.error('Errore nel salvataggio');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      toast.error('Errore di connessione');
    }
  };

  const handleToggleIntegration = async (id: string) => {
    const token = localStorage.getItem('admin_token');
    const integration = integrations.find(i => i.id === id);

    // Handle Google Services (UNIFICATO)
    if (id === 'google') {
      if (integration?.status === 'connected') {
        // Disconnect ALL Google services
        try {
          const res = await fetch('/api/v1/admin/google/disconnect', {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
          });
          if (res.ok) {
            toast.success('Google disconnesso (tutti i servizi)');
            fetchData(); // Refresh
          }
        } catch {
          toast.error('Errore nella disconnessione');
        }
      } else {
        // Connect - UN SOLO OAuth per TUTTI i servizi Google
        try {
          const res = await fetch('/api/v1/admin/google/connect', {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (res.ok) {
            const data = await res.json();
            toast.info('Connessione a Google: Analytics + Business + Calendar');
            window.location.href = data.auth_url;
          }
        } catch {
          toast.error('Errore nella connessione');
        }
      }
      return;
    }

    // Handle Meta/Stripe integrations - save to backend
    if (id === 'meta' || id === 'stripe') {
      const newEnabled = integration?.status !== 'connected';
      try {
        const res = await fetch('/api/v1/admin/settings/integrations/toggle', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            integration_id: id,
            enabled: newEnabled,
          }),
        });

        if (res.ok) {
          toast.success(`${integration?.name || id} ${newEnabled ? 'connesso' : 'disconnesso'}`);
          // Update local state
          setIntegrations(prev => prev.map(int => {
            if (int.id === id) {
              return { ...int, status: newEnabled ? 'connected' : 'disconnected' };
            }
            return int;
          }));
        } else {
          toast.error('Errore nel salvataggio');
        }
      } catch {
        toast.error('Errore di connessione');
      }
      return;
    }

    // Handle other integrations (fallback)
    setIntegrations(prev => prev.map(int => {
      if (int.id === id) {
        const newStatus = int.status === 'connected' ? 'disconnected' : 'connected';
        toast.success(`${int.name} ${newStatus === 'connected' ? 'connesso' : 'disconnesso'}`);
        return { ...int, status: newStatus };
      }
      return int;
    }));
  };

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header with Tab Navigation - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        {/* Title Row */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
            <Settings className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
              Settings Hub
            </h1>
            <p className="text-sm text-muted-foreground">
              Configurazione e gestione sistema
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-card border border-border rounded-2xl p-2 shadow-sm">
          <div className="flex gap-1 overflow-x-auto">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl transition-all',
                    isActive
                      ? `bg-gradient-to-r ${tab.color} text-white shadow-lg`
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-xs font-medium whitespace-nowrap">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Users Tab */}
      {activeTab === 'users' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          {/* Actions - Mobile First */}
          <div className={`${cardBg} rounded-xl p-3 sm:p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3`}>
            <div>
              <p className={`text-sm sm:text-base ${textSecondary}`}>Gestisci accessi e permessi del team</p>
            </div>
            <Button
              onClick={() => setShowAddUserModal(true)}
              className="bg-[#D4AF37] hover:bg-[#B8963A] text-black w-full sm:w-auto"
            >
              <Plus className="h-4 w-4 mr-2" />
              Nuovo Utente
            </Button>
          </div>

          {/* Users Table - Mobile First (Card layout on mobile) */}
          <div className={`${cardBg} rounded-xl overflow-hidden`}>
            {/* Desktop Table */}
            <table className="w-full hidden md:table">
              <thead className={isDark ? 'bg-white/5' : 'bg-gray-50'}>
                <tr>
                  <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Utente</th>
                  <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Ruolo</th>
                  <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Status</th>
                  <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase hidden lg:table-cell`}>2FA</th>
                  <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase hidden lg:table-cell`}>Ultimo Accesso</th>
                  <th className={`px-4 lg:px-6 py-3 text-right text-xs font-medium ${textSecondary} uppercase`}>Azioni</th>
                </tr>
              </thead>
              <tbody className={`divide-y ${isDark ? 'divide-white/10' : 'divide-gray-100'}`}>
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <Loader2 className={`h-8 w-8 mx-auto animate-spin ${textSecondary}`} />
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <Users className={`h-12 w-12 mx-auto mb-4 ${textSecondary} opacity-50`} />
                      <p className={textSecondary}>Nessun utente trovato</p>
                    </td>
                  </tr>
                ) : (
                  users.map(user => (
                    <tr key={user.id} className={isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'}>
                      <td className="px-4 lg:px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-[#D4AF37]/20 flex items-center justify-center flex-shrink-0">
                            <span className="text-[#D4AF37] font-medium text-sm lg:text-base">
                              {user.name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="min-w-0">
                            <p className={`font-medium ${textPrimary} truncate`}>{user.name || 'N/A'}</p>
                            <p className={`text-xs lg:text-sm ${textSecondary} truncate`}>{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 lg:px-6 py-4">
                        <span className={cn(
                          'px-2 py-1 rounded-full text-xs text-white',
                          ROLES[user.role]?.color || 'bg-gray-500'
                        )}>
                          {ROLES[user.role]?.label || user.role}
                        </span>
                      </td>
                      <td className="px-4 lg:px-6 py-4">
                        <span className={cn(
                          'flex items-center gap-1 text-xs lg:text-sm',
                          user.status === 'active' ? 'text-gold' :
                            user.status === 'pending' ? 'text-gold' : 'text-gray-500'
                        )}>
                          {user.status === 'active' ? <CheckCircle2 className="h-4 w-4" /> :
                            user.status === 'pending' ? <AlertCircle className="h-4 w-4" /> :
                              <XCircle className="h-4 w-4" />}
                          <span className="hidden lg:inline">{user.status === 'active' ? 'Attivo' :
                            user.status === 'pending' ? 'In attesa' : 'Inattivo'}</span>
                        </span>
                      </td>
                      <td className="px-4 lg:px-6 py-4 hidden lg:table-cell">
                        {user.two_factor_enabled ? (
                          <span className="text-gold flex items-center gap-1">
                            <Shield className="h-4 w-4" /> Attivo
                          </span>
                        ) : (
                          <span className={textSecondary}>Disattivato</span>
                        )}
                      </td>
                      <td className="px-4 lg:px-6 py-4 hidden lg:table-cell">
                        <span className={textSecondary}>
                          {user.last_login
                            ? new Date(user.last_login).toLocaleDateString('it-IT')
                            : 'Mai'}
                        </span>
                      </td>
                      <td className="px-4 lg:px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-1 lg:gap-2">
                          <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="text-gray-400 h-8 w-8 p-0">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>

            {/* Mobile Card View */}
            <div className="md:hidden divide-y divide-border">
              {loading ? (
                <div className="p-8 text-center">
                  <Loader2 className={`h-8 w-8 mx-auto animate-spin ${textSecondary}`} />
                </div>
              ) : users.length === 0 ? (
                <div className="p-8 text-center">
                  <Users className={`h-12 w-12 mx-auto mb-4 ${textSecondary} opacity-50`} />
                  <p className={textSecondary}>Nessun utente trovato</p>
                </div>
              ) : (
                users.map(user => (
                  <div key={user.id} className={`p-4 ${isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'}`}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="w-10 h-10 rounded-full bg-[#D4AF37]/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-[#D4AF37] font-medium">
                            {user.name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className={`font-medium ${textPrimary} truncate`}>{user.name || 'N/A'}</p>
                          <p className={`text-xs ${textSecondary} truncate`}>{user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="ghost" className="text-gray-400 h-8 w-8 p-0">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 mt-3 flex-wrap">
                      <span className={cn(
                        'px-2 py-1 rounded-full text-xs text-white',
                        ROLES[user.role]?.color || 'bg-gray-500'
                      )}>
                        {ROLES[user.role]?.label || user.role}
                      </span>
                      <span className={cn(
                        'flex items-center gap-1 text-xs',
                        user.status === 'active' ? 'text-gold' :
                          user.status === 'pending' ? 'text-gold' : 'text-gray-500'
                      )}>
                        {user.status === 'active' ? <CheckCircle2 className="h-3 w-3" /> :
                          user.status === 'pending' ? <AlertCircle className="h-3 w-3" /> :
                            <XCircle className="h-3 w-3" />}
                        {user.status === 'active' ? 'Attivo' :
                          user.status === 'pending' ? 'In attesa' : 'Inattivo'}
                      </span>
                      {user.two_factor_enabled && (
                        <span className="text-gold flex items-center gap-1 text-xs">
                          <Shield className="h-3 w-3" /> 2FA
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6"
        >
          {/* Personal Info */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <h3 className={`text-base sm:text-lg font-semibold ${textPrimary} mb-3 sm:mb-4 flex items-center gap-2`}>
              <User className="h-4 w-4 sm:h-5 sm:w-5" />
              Informazioni Personali
            </h3>

            <div className="space-y-3 sm:space-y-4">
              <div>
                <label className={`block text-xs sm:text-sm font-medium mb-1 ${textPrimary}`}>Nome Completo</label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={e => setProfile({ ...profile, name: e.target.value })}
                  className={cn('w-full px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg border text-sm sm:text-base', inputBg)}
                />
              </div>
              <div>
                <label className={`block text-xs sm:text-sm font-medium mb-1 ${textPrimary}`}>Email</label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={e => setProfile({ ...profile, email: e.target.value })}
                  className={cn('w-full px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg border text-sm sm:text-base', inputBg)}
                />
              </div>
              <div>
                <label className={`block text-xs sm:text-sm font-medium mb-1 ${textPrimary}`}>Telefono</label>
                <input
                  type="tel"
                  value={profile.phone}
                  onChange={e => setProfile({ ...profile, phone: e.target.value })}
                  className={cn('w-full px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg border text-sm sm:text-base', inputBg)}
                />
              </div>
              <div>
                <label className={`block text-xs sm:text-sm font-medium mb-1 ${textPrimary}`}>Azienda</label>
                <input
                  type="text"
                  value={profile.company}
                  onChange={e => setProfile({ ...profile, company: e.target.value })}
                  className={cn('w-full px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg border text-sm sm:text-base', inputBg)}
                />
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <h3 className={`text-base sm:text-lg font-semibold ${textPrimary} mb-3 sm:mb-4 flex items-center gap-2`}>
              <Settings className="h-4 w-4 sm:h-5 sm:w-5" />
              Preferenze
            </h3>

            <div className="space-y-4">
              <div>
                <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Fuso Orario</label>
                <select
                  value={profile.timezone}
                  onChange={e => setProfile({ ...profile, timezone: e.target.value })}
                  className={cn('w-full px-4 py-2 rounded-lg border', selectBg)}
                >
                  <option value="Europe/Rome">Europe/Rome (CET)</option>
                  <option value="Europe/London">Europe/London (GMT)</option>
                  <option value="America/New_York">America/New_York (EST)</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Lingua</label>
                <select
                  value={profile.language}
                  onChange={e => setProfile({ ...profile, language: e.target.value })}
                  className={cn('w-full px-4 py-2 rounded-lg border', selectBg)}
                >
                  <option value="it">Italiano</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Tema</label>
                <div className="flex gap-2">
                  <Button
                    variant={isDark ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => !isDark && toggleTheme()}
                    className={!isDark ? 'border-white/20' : ''}
                  >
                    🌙 Dark
                  </Button>
                  <Button
                    variant={!isDark ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => isDark && toggleTheme()}
                    className={isDark ? 'border-white/20' : ''}
                  >
                    ☀️ Light
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Security */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <h3 className={`text-base sm:text-lg font-semibold ${textPrimary} mb-3 sm:mb-4 flex items-center gap-2`}>
              <Shield className="h-4 w-4 sm:h-5 sm:w-5" />
              Sicurezza
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={textPrimary}>Autenticazione a 2 fattori</p>
                  <p className={`text-sm ${textSecondary}`}>Aggiungi un livello extra di sicurezza</p>
                </div>
                <Button
                  variant={profile.two_factor ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setProfile({ ...profile, two_factor: !profile.two_factor })}
                  className={cn(
                    profile.two_factor ? 'bg-gold hover:bg-gold' : '',
                    !profile.two_factor && isDark ? 'border-white/20' : ''
                  )}
                >
                  {profile.two_factor ? 'Attivo' : 'Attiva'}
                </Button>
              </div>

              <div className={`border-t pt-4 ${isDark ? 'border-white/10' : 'border-gray-200'}`}>
                <Button variant="outline" className={`w-full ${isDark ? 'border-white/20' : ''}`}>
                  <Key className="h-4 w-4 mr-2" />
                  Cambia Password
                </Button>
              </div>

              <Button variant="outline" className={`w-full text-gray-400 ${isDark ? 'border-white/20' : ''}`}>
                <Lock className="h-4 w-4 mr-2" />
                Disconnetti Tutte le Sessioni
              </Button>
            </div>
          </div>

          {/* Notifications */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <h3 className={`text-base sm:text-lg font-semibold ${textPrimary} mb-3 sm:mb-4 flex items-center gap-2`}>
              <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
              Notifiche
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={textPrimary}>Email</p>
                  <p className={`text-sm ${textSecondary}`}>Ricevi aggiornamenti via email</p>
                </div>
                <button
                  onClick={() => setProfile({ ...profile, notifications_email: !profile.notifications_email })}
                  className={cn(
                    'w-12 h-6 rounded-full transition-colors relative',
                    profile.notifications_email ? 'bg-gold' : isDark ? 'bg-white/20' : 'bg-gray-300'
                  )}
                >
                  <div className={cn(
                    'w-5 h-5 rounded-full bg-white absolute top-0.5 transition-transform',
                    profile.notifications_email ? 'translate-x-6' : 'translate-x-0.5'
                  )} />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className={textPrimary}>Push</p>
                  <p className={`text-sm ${textSecondary}`}>Notifiche push nel browser</p>
                </div>
                <button
                  onClick={() => setProfile({ ...profile, notifications_push: !profile.notifications_push })}
                  className={cn(
                    'w-12 h-6 rounded-full transition-colors relative',
                    profile.notifications_push ? 'bg-gold' : isDark ? 'bg-white/20' : 'bg-gray-300'
                  )}
                >
                  <div className={cn(
                    'w-5 h-5 rounded-full bg-white absolute top-0.5 transition-transform',
                    profile.notifications_push ? 'translate-x-6' : 'translate-x-0.5'
                  )} />
                </button>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="col-span-1 md:col-span-2 flex justify-end">
            <Button onClick={handleSaveProfile} className="bg-[#D4AF37] hover:bg-[#B8963A] text-black">
              <Save className="h-4 w-4 mr-2" />
              Salva Modifiche
            </Button>
          </div>
        </motion.div>
      )}

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          {/* API Keys */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <h3 className={`text-base sm:text-lg font-semibold ${textPrimary} mb-3 sm:mb-4 flex items-center gap-2`}>
              <Key className="h-4 w-4 sm:h-5 sm:w-5" />
              API Keys
            </h3>

            <div className="space-y-3">
              <div className={`flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg gap-2 ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                <div className="min-w-0">
                  <p className={`text-sm sm:text-base ${textPrimary}`}>Production API Key</p>
                  <p className={`text-xs sm:text-sm font-mono ${textSecondary} truncate`}>sk_live_****************************</p>
                </div>
                <div className="flex gap-1 sm:gap-2 flex-shrink-0">
                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                    <Copy className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className={`flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg gap-2 ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                <div className="min-w-0">
                  <p className={`text-sm sm:text-base ${textPrimary}`}>Test API Key</p>
                  <p className={`text-xs sm:text-sm font-mono ${textSecondary} truncate`}>sk_test_****************************</p>
                </div>
                <div className="flex gap-1 sm:gap-2 flex-shrink-0">
                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                    <Copy className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Integrations Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            {integrations.map(integration => (
              <div key={integration.id} className={`${cardBg} rounded-xl p-3 sm:p-4`}>
                <div className="flex items-start gap-3 mb-3">
                  <span className="text-xl sm:text-2xl">{integration.icon}</span>
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm sm:text-base font-medium ${textPrimary}`}>{integration.name}</p>
                    <p className={`text-xs sm:text-sm ${textSecondary} truncate`}>{integration.description}</p>
                  </div>
                </div>

                {/* Google Services - mostra dettaglio sub-servizi */}
                {integration.id === 'google' && integration.status === 'connected' && integration.config && (
                  <div className={`mb-3 p-2 rounded-lg text-xs space-y-1 ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                    <div className="flex items-center gap-2">
                      {integration.config.analytics ?
                        <CheckCircle2 className="h-3 w-3 text-gold" /> :
                        <XCircle className="h-3 w-3 text-gray-400" />}
                      <span className={integration.config.analytics ? 'text-gold' : textSecondary}>
                        📊 Analytics {integration.config.analytics ? '✓' : '—'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {integration.config.business ?
                        <CheckCircle2 className="h-3 w-3 text-gold" /> :
                        <XCircle className="h-3 w-3 text-gray-400" />}
                      <span className={integration.config.business ? 'text-gold' : textSecondary}>
                        🏢 Business Profile {integration.config.business ? '✓' : '—'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {integration.config.calendar ?
                        <CheckCircle2 className="h-3 w-3 text-gold" /> :
                        <XCircle className="h-3 w-3 text-gray-400" />}
                      <span className={integration.config.calendar ? 'text-gold' : textSecondary}>
                        📅 Calendar {integration.config.calendar ? '✓' : '—'}
                      </span>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between gap-2">
                  <span className={cn(
                    'flex items-center gap-1 text-xs sm:text-sm',
                    integration.status === 'connected' ? 'text-gold' :
                      integration.status === 'error' ? 'text-gray-400' : textSecondary
                  )}>
                    {integration.status === 'connected' ? <CheckCircle2 className="h-3 w-3 sm:h-4 sm:w-4" /> :
                      integration.status === 'error' ? <XCircle className="h-3 w-3 sm:h-4 sm:w-4" /> :
                        <AlertCircle className="h-3 w-3 sm:h-4 sm:w-4" />}
                    <span className="hidden sm:inline">
                      {integration.status === 'connected' ? 'Connesso' :
                        integration.status === 'error' ? 'Errore' : 'Non connesso'}
                    </span>
                  </span>
                  <Button
                    size="sm"
                    variant={integration.status === 'connected' ? 'outline' : 'default'}
                    onClick={() => handleToggleIntegration(integration.id)}
                    className={cn(
                      'text-xs sm:text-sm',
                      integration.status !== 'connected' && 'bg-[#D4AF37] hover:bg-[#B8963A] text-black',
                      integration.status === 'connected' && isDark && 'border-white/20'
                    )}
                  >
                    {integration.status === 'connected' ? 'Disconnetti' : 'Connetti'}
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Webhooks */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
              <h3 className={`text-base sm:text-lg font-semibold ${textPrimary} flex items-center gap-2`}>
                <Webhook className="h-4 w-4 sm:h-5 sm:w-5" />
                Webhooks
              </h3>
              <Button size="sm" className="bg-[#D4AF37] hover:bg-[#B8963A] text-black w-full sm:w-auto">
                <Plus className="h-4 w-4 mr-1" />
                Nuovo Webhook
              </Button>
            </div>

            <div className={`text-center py-8 ${textSecondary}`}>
              <Webhook className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Nessun webhook configurato</p>
              <p className="text-sm">Aggiungi webhook per ricevere notifiche in tempo reale</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Email Tab */}
      {activeTab === 'email' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <EmailInbox />
        </motion.div>
      )}

      {/* System Tab */}
      {activeTab === 'system' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* System Status */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-4">
            <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 rounded-lg bg-gold/20">
                  <Activity className="h-4 w-4 sm:h-5 sm:w-5 text-gold" />
                </div>
                <div>
                  <p className={`text-xs sm:text-sm ${textSecondary}`}>API</p>
                  <p className={`text-sm sm:text-base font-medium text-gold`}>Online</p>
                </div>
              </div>
            </div>
            <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 rounded-lg bg-gold/20">
                  <Database className="h-4 w-4 sm:h-5 sm:w-5 text-gold" />
                </div>
                <div>
                  <p className={`text-xs sm:text-sm ${textSecondary}`}>Database</p>
                  <p className={`text-sm sm:text-base font-medium text-gold`}>Healthy</p>
                </div>
              </div>
            </div>
            <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 rounded-lg bg-gold/20">
                  <Cloud className="h-4 w-4 sm:h-5 sm:w-5 text-gold" />
                </div>
                <div>
                  <p className={`text-xs sm:text-sm ${textSecondary}`}>Storage</p>
                  <p className={`text-xs sm:text-base font-medium ${textPrimary}`}>2.4/10GB</p>
                </div>
              </div>
            </div>
            <div className={`${cardBg} rounded-xl p-3 sm:p-4`}>
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 rounded-lg bg-gold/20">
                  <HardDrive className="h-4 w-4 sm:h-5 sm:w-5 text-gold" />
                </div>
                <div>
                  <p className={`text-xs sm:text-sm ${textSecondary}`}>Backup</p>
                  <p className={`text-xs sm:text-base font-medium ${textPrimary}`}>03:00</p>
                </div>
              </div>
            </div>
          </div>

          {/* Maintenance */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <h3 className={`text-base sm:text-lg font-semibold ${textPrimary} mb-3 sm:mb-4`}>Manutenzione</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-4">
              <Button variant="outline" className={`text-xs sm:text-sm ${isDark ? 'border-white/20' : ''}`}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Pulisci Cache
              </Button>
              <Button variant="outline" className={`text-xs sm:text-sm ${isDark ? 'border-white/20' : ''}`}>
                <Database className="h-4 w-4 mr-2" />
                Backup Manuale
              </Button>
              <Button variant="outline" className={`text-xs sm:text-sm ${isDark ? 'border-white/20' : ''}`}>
                <Activity className="h-4 w-4 mr-2" />
                Health Check
              </Button>
            </div>
          </div>

          {/* System Logs */}
          <div className={`${cardBg} rounded-xl p-4 sm:p-6`}>
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <h3 className={`text-base sm:text-lg font-semibold ${textPrimary}`}>Log di Sistema</h3>
              <Button variant="ghost" size="sm" className="text-xs sm:text-sm">
                Vedi tutti <ExternalLink className="h-4 w-4 ml-1" />
              </Button>
            </div>

            <div className={`space-y-2 max-h-64 overflow-auto`}>
              {logs.length === 0 ? (
                <p className={textSecondary}>Nessun log disponibile</p>
              ) : (
                logs.map((log, idx) => (
                  <div
                    key={log.id || idx}
                    className={cn(
                      'flex items-center gap-3 p-2 rounded-lg text-sm',
                      isDark ? 'bg-white/5' : 'bg-gray-50'
                    )}
                  >
                    <span className={cn(
                      'w-2 h-2 rounded-full flex-shrink-0',
                      log.type === 'info' ? 'bg-gold' :
                        log.type === 'warning' ? 'bg-gold' : 'bg-gray-500'
                    )} />
                    <span className={cn(textSecondary, 'whitespace-nowrap')}>
                      {new Date(log.timestamp).toLocaleTimeString('it-IT')}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs whitespace-nowrap ${isDark ? 'bg-white/10' : 'bg-gray-200'}`}>
                      {log.source}
                    </span>
                    <span className={cn(textPrimary, 'truncate flex-1 min-w-0')}>
                      {log.message}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Version Info */}
          <div className={`${cardBg} rounded-xl p-6`}>
            <h3 className={`font-semibold ${textPrimary} mb-4`}>Informazioni Versione</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
              <div>
                <p className={textSecondary}>Backend</p>
                <p className={`font-mono ${textPrimary}`}>v2.5.0</p>
              </div>
              <div>
                <p className={textSecondary}>Frontend</p>
                <p className={`font-mono ${textPrimary}`}>v2.5.0</p>
              </div>
              <div>
                <p className={textSecondary}>AI Microservice</p>
                <p className={`font-mono ${textPrimary}`}>v1.3.0</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default SettingsHub;
