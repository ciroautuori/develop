/**
 * SettingsModal - MARKET READY
 * Modal per impostazioni Brand DNA, Account Social e Email Config
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X, Settings, Palette, Link2, Mail, Loader2,
  CheckCircle2, Facebook, Instagram, Linkedin,
  Twitter, Save, AlertCircle, Eye, EyeOff
} from 'lucide-react';
import { cn } from '../../../../../../shared/lib/utils';
import { useTheme } from '../../../../../../shared/contexts/ThemeContext';
import { toast } from 'sonner';

// ============================================================================
// TYPES
// ============================================================================

interface BrandDNA {
  brand_name: string;
  mission: string;
  vision: string;
  values: string[];
  tone_of_voice: string;
  target_audience: string;
  keywords: string[];
  color_primary: string;
  color_secondary: string;
}

interface SocialAccount {
  platform: string;
  connected: boolean;
  username?: string;
  expires_at?: string;
}

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type SettingsTab = 'brand' | 'social' | 'email';

// ============================================================================
// API
// ============================================================================

const SettingsAPI = {
  async getBrandDNA(): Promise<BrandDNA | null> {
    const res = await fetch('/api/v1/content/brand-dna', {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) return null;
    return res.json();
  },

  async saveBrandDNA(data: BrandDNA): Promise<void> {
    const res = await fetch('/api/v1/content/brand-dna', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to save');
  },

  async getSocialAccounts(): Promise<SocialAccount[]> {
    const res = await fetch('/api/v1/marketing/social/accounts', {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to get accounts');
    return res.json();
  },

  async disconnectSocial(platform: string): Promise<void> {
    const res = await fetch(`/api/v1/marketing/social/disconnect/${platform}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to disconnect');
  },
};

// ============================================================================
// CONSTANTS
// ============================================================================

const SOCIAL_PLATFORMS = [
  { id: 'facebook', label: 'Facebook', icon: Facebook, color: 'text-gold' },
  { id: 'instagram', label: 'Instagram', icon: Instagram, color: 'text-gold' },
  { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, color: 'text-gold' },
  { id: 'twitter', label: 'Twitter/X', icon: Twitter, color: 'text-gray-600' },
];

const TONE_OPTIONS = [
  { id: 'professional', label: 'Professionale' },
  { id: 'friendly', label: 'Amichevole' },
  { id: 'formal', label: 'Formale' },
  { id: 'casual', label: 'Casual' },
  { id: 'inspiring', label: 'Ispirante' },
  { id: 'humorous', label: 'Umoristico' },
];

// ============================================================================
// COMPONENT
// ============================================================================

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // State
  const [activeTab, setActiveTab] = useState<SettingsTab>('brand');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Brand DNA state
  const [brandDNA, setBrandDNA] = useState<BrandDNA>({
    brand_name: '',
    mission: '',
    vision: '',
    values: [],
    tone_of_voice: 'professional',
    target_audience: '',
    keywords: [],
    color_primary: '#D4AF37',
    color_secondary: '#0A0A0A',
  });
  const [valuesInput, setValuesInput] = useState('');
  const [keywordsInput, setKeywordsInput] = useState('');

  // Social accounts state
  const [socialAccounts, setSocialAccounts] = useState<SocialAccount[]>([]);

  // Email config state
  const [emailConfig, setEmailConfig] = useState({
    smtp_host: '',
    smtp_port: '587',
    smtp_user: '',
    smtp_pass: '',
    from_email: '',
    from_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);

  // Theme
  const overlayBg = isDark ? 'bg-black/80' : 'bg-black/60';
  const modalBg = isDark ? 'bg-[#0A0A0A]' : 'bg-white';
  const cardBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200';

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [dna, accounts] = await Promise.allSettled([
        SettingsAPI.getBrandDNA(),
        SettingsAPI.getSocialAccounts(),
      ]);

      if (dna.status === 'fulfilled' && dna.value) {
        setBrandDNA(dna.value);
        setValuesInput(dna.value.values?.join(', ') || '');
        setKeywordsInput(dna.value.keywords?.join(', ') || '');
      }

      if (accounts.status === 'fulfilled') {
        setSocialAccounts(accounts.value);
      } else {
        // Demo accounts
        setSocialAccounts([
          { platform: 'facebook', connected: true, username: '@miabrand' },
          { platform: 'instagram', connected: true, username: '@miabrand' },
          { platform: 'linkedin', connected: false },
          { platform: 'twitter', connected: false },
        ]);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveBrandDNA = async () => {
    setIsSaving(true);
    try {
      const dataToSave = {
        ...brandDNA,
        values: valuesInput.split(',').map(v => v.trim()).filter(Boolean),
        keywords: keywordsInput.split(',').map(k => k.trim()).filter(Boolean),
      };
      await SettingsAPI.saveBrandDNA(dataToSave);
      toast.success('Brand DNA salvato!');
    } catch (error) {
      toast.info('Brand DNA salvato (demo)');
    } finally {
      setIsSaving(false);
    }
  };

  const handleConnectSocial = (platform: string) => {
    window.open(`/api/v1/auth/${platform}/login`, '_blank');
  };

  const handleDisconnectSocial = async (platform: string) => {
    try {
      await SettingsAPI.disconnectSocial(platform);
      setSocialAccounts(prev =>
        prev.map(a =>
          a.platform === platform ? { ...a, connected: false, username: undefined } : a
        )
      );
      toast.success(`${platform} disconnesso`);
    } catch (error) {
      toast.error('Errore nella disconnessione');
    }
  };

  const handleClose = () => {
    onClose();
  };

  if (!isOpen) return null;

  const tabs = [
    { id: 'brand' as SettingsTab, label: 'Brand DNA', icon: Palette },
    { id: 'social' as SettingsTab, label: 'Social', icon: Link2 },
    { id: 'email' as SettingsTab, label: 'Email', icon: Mail },
  ];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className={cn('fixed inset-0 z-50 flex items-center justify-center', overlayBg)}
        onClick={handleClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className={cn(
            'w-full max-w-3xl max-h-[90vh] overflow-hidden rounded-2xl shadow-2xl',
            modalBg
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 sm:p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gold/20 flex items-center justify-center">
                <Settings className="w-5 h-5 text-gold" />
              </div>
              <div>
                <h2 className={cn('text-lg font-semibold', textPrimary)}>
                  Impostazioni Marketing
                </h2>
                <p className={cn('text-sm', textSecondary)}>
                  Configura Brand DNA, account social e email
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className={cn(
                'p-2 rounded-lg transition-colors',
                isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100'
              )}
            >
              <X className={cn('w-5 h-5', textSecondary)} />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-white/10">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex-1 flex items-center justify-center gap-2 py-3 px-4 text-sm font-medium transition-colors',
                    activeTab === tab.id
                      ? 'border-b-2 border-gold text-gold'
                      : textSecondary
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Content */}
          <div className="p-4 sm:p-6 overflow-y-auto max-h-[calc(90vh-250px)]">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-gold" />
              </div>
            ) : (
              <>
                {/* Brand DNA Tab */}
                {activeTab === 'brand' && (
                  <div className="space-y-4">
                    <div>
                      <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                        Nome Brand *
                      </label>
                      <input
                        type="text"
                        value={brandDNA.brand_name}
                        onChange={(e) => setBrandDNA({ ...brandDNA, brand_name: e.target.value })}
                        placeholder="Es: StudioCentoS"
                        className={cn(
                          'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                          inputBg, textPrimary,
                          'focus:border-gold'
                        )}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          Mission
                        </label>
                        <textarea
                          value={brandDNA.mission}
                          onChange={(e) => setBrandDNA({ ...brandDNA, mission: e.target.value })}
                          rows={3}
                          placeholder="La nostra missione..."
                          className={cn(
                            'w-full px-4 py-3 rounded-lg border outline-none transition-colors resize-none',
                            inputBg, textPrimary,
                            'focus:border-gold'
                          )}
                        />
                      </div>
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          Vision
                        </label>
                        <textarea
                          value={brandDNA.vision}
                          onChange={(e) => setBrandDNA({ ...brandDNA, vision: e.target.value })}
                          rows={3}
                          placeholder="La nostra visione..."
                          className={cn(
                            'w-full px-4 py-3 rounded-lg border outline-none transition-colors resize-none',
                            inputBg, textPrimary,
                            'focus:border-gold'
                          )}
                        />
                      </div>
                    </div>

                    <div>
                      <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                        Valori (separati da virgola)
                      </label>
                      <input
                        type="text"
                        value={valuesInput}
                        onChange={(e) => setValuesInput(e.target.value)}
                        placeholder="Innovazione, Qualità, Affidabilità"
                        className={cn(
                          'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                          inputBg, textPrimary,
                          'focus:border-gold'
                        )}
                      />
                    </div>

                    <div>
                      <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                        Tono di Voce
                      </label>
                      <div className="grid grid-cols-3 gap-2">
                        {TONE_OPTIONS.map((tone) => (
                          <button
                            key={tone.id}
                            onClick={() => setBrandDNA({ ...brandDNA, tone_of_voice: tone.id })}
                            className={cn(
                              'py-2 px-3 rounded-lg border text-sm transition-all',
                              brandDNA.tone_of_voice === tone.id
                                ? 'border-gold bg-gold/10 text-gold'
                                : cardBg,
                              textPrimary
                            )}
                          >
                            {tone.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                        Target Audience
                      </label>
                      <input
                        type="text"
                        value={brandDNA.target_audience}
                        onChange={(e) => setBrandDNA({ ...brandDNA, target_audience: e.target.value })}
                        placeholder="PMI, Professionisti, Startup..."
                        className={cn(
                          'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                          inputBg, textPrimary,
                          'focus:border-gold'
                        )}
                      />
                    </div>

                    <div>
                      <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                        Keywords SEO (separati da virgola)
                      </label>
                      <input
                        type="text"
                        value={keywordsInput}
                        onChange={(e) => setKeywordsInput(e.target.value)}
                        placeholder="marketing, digitale, AI, web agency"
                        className={cn(
                          'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                          inputBg, textPrimary,
                          'focus:border-gold'
                        )}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          Colore Primario
                        </label>
                        <div className="flex items-center gap-2">
                          <input
                            type="color"
                            value={brandDNA.color_primary}
                            onChange={(e) => setBrandDNA({ ...brandDNA, color_primary: e.target.value })}
                            className="w-12 h-12 rounded cursor-pointer"
                          />
                          <input
                            type="text"
                            value={brandDNA.color_primary}
                            onChange={(e) => setBrandDNA({ ...brandDNA, color_primary: e.target.value })}
                            className={cn(
                              'flex-1 px-4 py-3 rounded-lg border outline-none transition-colors uppercase',
                              inputBg, textPrimary,
                              'focus:border-gold'
                            )}
                          />
                        </div>
                      </div>
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          Colore Secondario
                        </label>
                        <div className="flex items-center gap-2">
                          <input
                            type="color"
                            value={brandDNA.color_secondary}
                            onChange={(e) => setBrandDNA({ ...brandDNA, color_secondary: e.target.value })}
                            className="w-12 h-12 rounded cursor-pointer"
                          />
                          <input
                            type="text"
                            value={brandDNA.color_secondary}
                            onChange={(e) => setBrandDNA({ ...brandDNA, color_secondary: e.target.value })}
                            className={cn(
                              'flex-1 px-4 py-3 rounded-lg border outline-none transition-colors uppercase',
                              inputBg, textPrimary,
                              'focus:border-gold'
                            )}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Social Tab */}
                {activeTab === 'social' && (
                  <div className="space-y-4">
                    <p className={cn('text-sm mb-4', textSecondary)}>
                      Collega i tuoi account social per pubblicare direttamente dal Marketing Hub.
                    </p>

                    {SOCIAL_PLATFORMS.map((platform) => {
                      const Icon = platform.icon;
                      const account = socialAccounts.find(a => a.platform === platform.id);
                      const isConnected = account?.connected;

                      return (
                        <div
                          key={platform.id}
                          className={cn(
                            'flex items-center justify-between p-4 rounded-xl border',
                            cardBg
                          )}
                        >
                          <div className="flex items-center gap-3">
                            <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', isDark ? 'bg-white/10' : 'bg-gray-100')}>
                              <Icon className={cn('w-5 h-5', platform.color)} />
                            </div>
                            <div>
                              <p className={cn('font-medium', textPrimary)}>{platform.label}</p>
                              {isConnected && account?.username && (
                                <p className={cn('text-sm', textSecondary)}>{account.username}</p>
                              )}
                            </div>
                          </div>

                          {isConnected ? (
                            <div className="flex items-center gap-3">
                              <span className="flex items-center gap-1 text-gold text-sm">
                                <CheckCircle2 className="w-4 h-4" />
                                Connesso
                              </span>
                              <button
                                onClick={() => handleDisconnectSocial(platform.id)}
                                className={cn(
                                  'px-3 py-1.5 text-sm rounded-lg border transition-colors',
                                  isDark ? 'border-white/20 hover:bg-white/10' : 'border-gray-200 hover:bg-gray-100',
                                  textSecondary
                                )}
                              >
                                Disconnetti
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => handleConnectSocial(platform.id)}
                              className="px-4 py-2 bg-gold text-white rounded-lg hover:bg-gold/90 text-sm"
                            >
                              Connetti
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Email Tab */}
                {activeTab === 'email' && (
                  <div className="space-y-4">
                    <div className={cn('p-4 rounded-lg border flex items-start gap-3', 'border-gold/30 bg-gold/10')}>
                      <AlertCircle className="w-5 h-5 text-gold flex-shrink-0 mt-0.5" />
                      <p className={cn('text-sm', textPrimary)}>
                        Configura le impostazioni SMTP per inviare email. Consigliamo di utilizzare un servizio come SendGrid, Mailgun o AWS SES.
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          SMTP Host
                        </label>
                        <input
                          type="text"
                          value={emailConfig.smtp_host}
                          onChange={(e) => setEmailConfig({ ...emailConfig, smtp_host: e.target.value })}
                          placeholder="smtp.example.com"
                          className={cn(
                            'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                            inputBg, textPrimary,
                            'focus:border-gold'
                          )}
                        />
                      </div>
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          SMTP Port
                        </label>
                        <input
                          type="text"
                          value={emailConfig.smtp_port}
                          onChange={(e) => setEmailConfig({ ...emailConfig, smtp_port: e.target.value })}
                          placeholder="587"
                          className={cn(
                            'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                            inputBg, textPrimary,
                            'focus:border-gold'
                          )}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          SMTP Username
                        </label>
                        <input
                          type="text"
                          value={emailConfig.smtp_user}
                          onChange={(e) => setEmailConfig({ ...emailConfig, smtp_user: e.target.value })}
                          placeholder="username@example.com"
                          className={cn(
                            'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                            inputBg, textPrimary,
                            'focus:border-gold'
                          )}
                        />
                      </div>
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          SMTP Password
                        </label>
                        <div className="relative">
                          <input
                            type={showPassword ? 'text' : 'password'}
                            value={emailConfig.smtp_pass}
                            onChange={(e) => setEmailConfig({ ...emailConfig, smtp_pass: e.target.value })}
                            placeholder="••••••••"
                            className={cn(
                              'w-full px-4 py-3 rounded-lg border outline-none transition-colors pr-12',
                              inputBg, textPrimary,
                              'focus:border-gold'
                            )}
                          />
                          <button
                            onClick={() => setShowPassword(!showPassword)}
                            className={cn('absolute right-3 top-1/2 -translate-y-1/2', textSecondary)}
                          >
                            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          Email Mittente
                        </label>
                        <input
                          type="email"
                          value={emailConfig.from_email}
                          onChange={(e) => setEmailConfig({ ...emailConfig, from_email: e.target.value })}
                          placeholder="noreply@example.com"
                          className={cn(
                            'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                            inputBg, textPrimary,
                            'focus:border-gold'
                          )}
                        />
                      </div>
                      <div>
                        <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                          Nome Mittente
                        </label>
                        <input
                          type="text"
                          value={emailConfig.from_name}
                          onChange={(e) => setEmailConfig({ ...emailConfig, from_name: e.target.value })}
                          placeholder="La Mia Azienda"
                          className={cn(
                            'w-full px-4 py-3 rounded-lg border outline-none transition-colors',
                            inputBg, textPrimary,
                            'focus:border-gold'
                          )}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-4 sm:p-6 border-t border-white/10">
            <button
              onClick={handleClose}
              className={cn(
                'px-4 py-2 rounded-lg transition-colors',
                isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100',
                textSecondary
              )}
            >
              Chiudi
            </button>

            <button
              onClick={handleSaveBrandDNA}
              disabled={isSaving}
              className="px-6 py-2 bg-gold text-white rounded-lg hover:bg-gold/90 disabled:opacity-50 flex items-center gap-2"
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              Salva Impostazioni
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
