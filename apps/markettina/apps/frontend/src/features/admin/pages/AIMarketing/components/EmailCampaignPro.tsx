/**
 * EmailCampaignPro Component
 * Full email marketing with campaign management, sending, and analytics
 *
 * @uses constants/locations - Regioni target
 * @uses constants/industries - Settori target
 * @uses constants/email-styles - Toni email
 * @uses types/email.types - Types centralizzati
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mail,
  Sparkles,
  Send,
  Loader2,
  Users,
  BarChart3,
  Clock,
  CheckCircle2,
  AlertCircle,
  Eye,
  Code,
  Copy,
  Trash2,
  Play,
  Plus,
  RefreshCw,
  TrendingUp,
  MousePointer,
  X,
} from 'lucide-react';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { Button } from '../../../../../shared/components/ui/button';

// Costanti e Types centralizzati
import { TARGET_REGIONS } from '../constants/locations';
import { TARGET_INDUSTRIES } from '../constants/industries';
import { EMAIL_TONES } from '../constants/email-styles';
import type { Campaign, CampaignStats } from '../types/email.types';

// Hook centralizzato per generazione email AI
import { useEmailCampaign } from '../../../hooks/marketing/useEmailCampaign';

// Brand DNA API
import { BrandContextAPI } from '../api/brandContext';

// API Service
const EmailApiService = {
  baseUrl: '/api/v1/marketing/email',

  async getCampaigns(): Promise<Campaign[]> {
    const res = await fetch(`${this.baseUrl}/campaigns`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to get campaigns');
    return res.json();
  },

  async createCampaign(data: any): Promise<Campaign> {
    const res = await fetch(`${this.baseUrl}/campaigns`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create campaign');
    return res.json();
  },

  async sendCampaign(campaignId: number): Promise<any> {
    const res = await fetch(`${this.baseUrl}/campaigns/${campaignId}/send`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to send campaign');
    return res.json();
  },

  async getCampaignStats(campaignId: number): Promise<CampaignStats> {
    const res = await fetch(`${this.baseUrl}/campaigns/${campaignId}/stats`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to get stats');
    return res.json();
  },

  async deleteCampaign(campaignId: number): Promise<void> {
    const res = await fetch(`${this.baseUrl}/campaigns/${campaignId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to delete campaign');
  },

  async sendTestEmail(email: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/test?to_email=${encodeURIComponent(email)}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to send test');
    return res.json();
  },

  async generateEmailAI(data: any): Promise<any> {
    const res = await fetch('/api/v1/marketing/emails/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to generate email');
    return res.json();
  },
};

// Costanti importate da constants/
const REGIONS = TARGET_REGIONS;
const INDUSTRIES = TARGET_INDUSTRIES;
const TONES = EMAIL_TONES;

export function EmailCampaignPro() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Hook centralizzato per generazione AI
  const { generate: generateEmailWithHook, isGenerating: isHookGenerating, result: hookResult } = useEmailCampaign();

  // State
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [stats, setStats] = useState<CampaignStats | null>(null);
  const [showNewCampaign, setShowNewCampaign] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  // isGenerating ora viene dall'hook: isHookGenerating
  const [previewMode, setPreviewMode] = useState<'html' | 'text' | 'code'>('html');

  // Form state
  const [campaignName, setCampaignName] = useState('');
  const [subject, setSubject] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const [textContent, setTextContent] = useState('');
  const [targetRegion, setTargetRegion] = useState('Salerno');
  const [targetIndustry, setTargetIndustry] = useState('Software & IT');
  const [tone, setTone] = useState<(typeof TONES)[number]>('professional');
  const [testEmail, setTestEmail] = useState('');

  // Brand DNA state
  const [brandContext, setBrandContext] = useState<any>(null);
  const [isLoadingBrand, setIsLoadingBrand] = useState(true);

  // Styles
  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-[#1A1A1A] border-gray-600 text-white placeholder-gray-400'
    : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400';

  // Load Brand DNA and campaigns on mount
  useEffect(() => {
    loadCampaigns();
    loadBrandContext();
  }, []);

  const loadBrandContext = async () => {
    setIsLoadingBrand(true);
    try {
      const context = await BrandContextAPI.getContext();
      setBrandContext(context);
    } catch (error) {
      console.error('Error loading brand context:', error);
    } finally {
      setIsLoadingBrand(false);
    }
  };

  const loadCampaigns = async () => {
    setIsLoading(true);
    try {
      const data = await EmailApiService.getCampaigns();
      setCampaigns(data);
    } catch (error) {
      console.error('Error loading campaigns:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async (campaignId: number) => {
    try {
      const data = await EmailApiService.getCampaignStats(campaignId);
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  // Generate email with AI (usa hook centralizzato + Brand DNA)
  const handleGenerateAI = async () => {
    if (!campaignName.trim()) {
      toast.error('Inserisci il nome della campagna');
      return;
    }

    // Build brand context string for injection
    const brandInfo = brandContext ? `
Azienda: ${brandContext.company_name || 'StudioCentOS'}
Settore: ${brandContext.industry || 'Software Development'}
Tono di voce: ${brandContext.tone_of_voice || tone}
Valori: ${brandContext.values?.join(', ') || 'Innovazione, Qualità, Professionalità'}
Servizi: ${brandContext.services?.join(', ') || 'Sviluppo Software, App, AI'}
` : '';

    // Usa hook centralizzato per generazione con Brand DNA
    await generateEmailWithHook({
      campaign_name: campaignName,
      target_region: targetRegion,
      target_industry: targetIndustry,
      tone,
      language: 'it',
      brand_context: brandInfo, // 🧬 Inject Brand DNA
    });
  };

  // Aggiorna contenuto quando l'hook restituisce risultato
  useEffect(() => {
    if (hookResult) {
      setSubject(hookResult.subject);
      setHtmlContent(hookResult.html_content);
      setTextContent(hookResult.text_content);
    }
  }, [hookResult]);

  // Create campaign
  const handleCreateCampaign = async () => {
    if (!campaignName.trim() || !subject.trim() || !htmlContent.trim()) {
      toast.error('Compila tutti i campi obbligatori');
      return;
    }

    try {
      const campaign = await EmailApiService.createCampaign({
        name: campaignName,
        subject,
        html_content: htmlContent,
        text_content: textContent,
        target_region: targetRegion,
        target_industry: targetIndustry,
        ai_generated: true,
      });

      setCampaigns((prev) => [campaign, ...prev]);
      setShowNewCampaign(false);
      resetForm();
      toast.success('Campagna creata!');
    } catch (error) {
      toast.error('Errore nella creazione');
    }
  };

  // Send campaign
  const handleSendCampaign = async (campaign: Campaign) => {
    if (campaign.is_sent) {
      toast.error('Campagna già inviata');
      return;
    }

    setIsSending(true);
    try {
      const result = await EmailApiService.sendCampaign(campaign.id);
      toast.success(`Campagna inviata! ${result.total_sent} email inviate`);
      loadCampaigns();
    } catch (error) {
      toast.error('Errore nell\'invio');
    } finally {
      setIsSending(false);
    }
  };

  // Send test email
  const handleSendTest = async () => {
    if (!testEmail.trim()) {
      toast.error('Inserisci email di test');
      return;
    }

    try {
      const result = await EmailApiService.sendTestEmail(testEmail);
      if (result.success) {
        toast.success('Email di test inviata!');
      } else {
        toast.error(`Errore: ${result.error}`);
      }
    } catch (error) {
      toast.error('Errore nell\'invio test');
    }
  };

  // Delete campaign
  const handleDeleteCampaign = async (campaignId: number) => {
    try {
      await EmailApiService.deleteCampaign(campaignId);
      setCampaigns((prev) => prev.filter((c) => c.id !== campaignId));
      if (selectedCampaign?.id === campaignId) {
        setSelectedCampaign(null);
        setStats(null);
      }
      toast.success('Campagna eliminata');
    } catch (error) {
      toast.error('Errore nell\'eliminazione');
    }
  };

  const resetForm = () => {
    setCampaignName('');
    setSubject('');
    setHtmlContent('');
    setTextContent('');
    setTargetRegion('Salerno');
    setTargetIndustry('Software & IT');
    setTone('professional');
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copiato!`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-2xl font-bold ${textPrimary}`}>Email Marketing Pro</h2>
          <p className={`${textSecondary} mt-1`}>
            Crea, invia e analizza campagne email con AI
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={loadCampaigns} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Aggiorna
          </Button>
          <Button onClick={() => setShowNewCampaign(true)} className="bg-gold hover:bg-gold/90">
            <Plus className="w-4 h-4 mr-2" />
            Nuova Campagna
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Campaign List */}
        <div className={`lg:col-span-1 ${cardBg} rounded-2xl p-6`}>
          <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>Campagne</h3>

          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-gold" />
            </div>
          ) : campaigns.length === 0 ? (
            <div className={`text-center py-8 ${textSecondary}`}>
              <Mail className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Nessuna campagna</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {campaigns.map((campaign) => (
                <motion.div
                  key={campaign.id}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => {
                    setSelectedCampaign(campaign);
                    loadStats(campaign.id);
                  }}
                  className={`p-3 rounded-xl cursor-pointer transition-colors ${selectedCampaign?.id === campaign.id
                    ? 'bg-gold/20 border border-gold/50'
                    : isDark
                      ? 'bg-[#1A1A1A] hover:bg-white/10'
                      : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className={`font-medium line-clamp-1 ${textPrimary}`}>{campaign.name}</h4>
                    {campaign.is_sent ? (
                      <CheckCircle2 className="w-4 h-4 text-gold flex-shrink-0" />
                    ) : (
                      <Clock className="w-4 h-4 text-gold flex-shrink-0" />
                    )}
                  </div>
                  <p className={`text-xs line-clamp-1 mb-2 ${textSecondary}`}>{campaign.subject}</p>
                  <div className="flex items-center gap-3 text-xs">
                    <span className={textSecondary}>
                      <Users className="w-3 h-3 inline mr-1" />
                      {campaign.total_sent}
                    </span>
                    <span className="text-gold">
                      <Eye className="w-3 h-3 inline mr-1" />
                      {campaign.open_rate}%
                    </span>
                    <span className="text-gold">
                      <MousePointer className="w-3 h-3 inline mr-1" />
                      {campaign.click_rate}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Campaign Details / New Campaign */}
        <div className={`lg:col-span-2 ${cardBg} rounded-2xl p-6`}>
          <AnimatePresence mode="wait">
            {showNewCampaign ? (
              <motion.div
                key="new-campaign"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className={`text-lg font-bold ${textPrimary}`}>Nuova Campagna</h3>
                  <button onClick={() => setShowNewCampaign(false)}>
                    <X className={`w-5 h-5 ${textSecondary}`} />
                  </button>
                </div>

                {/* Campaign Name */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${textSecondary}`}>
                    Nome Campagna *
                  </label>
                  <input
                    type="text"
                    value={campaignName}
                    onChange={(e) => setCampaignName(e.target.value)}
                    placeholder="Es. Lancio Q1 2025"
                    className={`w-full rounded-lg p-3 ${inputBg} border focus:ring-2 focus:ring-gold`}
                  />
                </div>

                {/* Target Settings */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${textSecondary}`}>
                      Regione Target
                    </label>
                    <select
                      value={targetRegion}
                      onChange={(e) => setTargetRegion(e.target.value)}
                      className={`w-full rounded-lg p-3 ${inputBg} border focus:ring-2 focus:ring-gold`}
                    >
                      {REGIONS.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${textSecondary}`}>
                      Settore Target
                    </label>
                    <select
                      value={targetIndustry}
                      onChange={(e) => setTargetIndustry(e.target.value)}
                      className={`w-full rounded-lg p-3 ${inputBg} border focus:ring-2 focus:ring-gold`}
                    >
                      {INDUSTRIES.map((i) => (
                        <option key={i} value={i}>{i}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className={`block text-sm font-medium mb-1 ${textSecondary}`}>Tone</label>
                  <div className="flex gap-2">
                    {TONES.map((t) => (
                      <button
                        key={t}
                        onClick={() => setTone(t)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tone === t
                          ? 'bg-gold text-white'
                          : isDark
                            ? 'bg-white/10 text-gray-300'
                            : 'bg-gray-100 text-gray-700'
                          }`}
                      >
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* AI Generate Button */}
                <Button
                  onClick={handleGenerateAI}
                  disabled={isHookGenerating || !campaignName.trim()}
                  className="w-full bg-gold hover:bg-gold/90"
                >
                  {isHookGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generazione AI...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Genera con AI
                    </>
                  )}
                </Button>

                {/* Subject */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${textSecondary}`}>
                    Subject *
                  </label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="Oggetto email..."
                    className={`w-full rounded-lg p-3 ${inputBg} border focus:ring-2 focus:ring-gold`}
                  />
                </div>

                {/* Content Preview */}
                {htmlContent && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className={`block text-sm font-medium ${textSecondary}`}>
                        Contenuto
                      </label>
                      <div className="flex gap-1">
                        {['html', 'text', 'code'].map((mode) => (
                          <button
                            key={mode}
                            onClick={() => setPreviewMode(mode as typeof previewMode)}
                            className={`px-2 py-1 text-xs rounded ${previewMode === mode
                              ? 'bg-gold text-white'
                              : isDark
                                ? 'bg-white/10 text-gray-300'
                                : 'bg-gray-100 text-gray-600'
                              }`}
                          >
                            {mode.toUpperCase()}
                          </button>
                        ))}
                        <button
                          onClick={() =>
                            copyToClipboard(
                              previewMode === 'text' ? textContent : htmlContent,
                              'Contenuto'
                            )
                          }
                          className={`px-2 py-1 rounded ${isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100'
                            }`}
                        >
                          <Copy className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                    <div
                      className={`p-4 rounded-xl max-h-[300px] overflow-y-auto ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'
                        }`}
                    >
                      {previewMode === 'html' && (
                        <div
                          dangerouslySetInnerHTML={{ __html: htmlContent }}
                          className="prose prose-sm max-w-none dark:prose-invert"
                        />
                      )}
                      {previewMode === 'text' && (
                        <pre className={`whitespace-pre-wrap text-sm ${textPrimary}`}>
                          {textContent}
                        </pre>
                      )}
                      {previewMode === 'code' && (
                        <pre className="whitespace-pre-wrap text-xs font-mono overflow-x-auto">
                          {htmlContent}
                        </pre>
                      )}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    onClick={handleCreateCampaign}
                    disabled={!subject.trim() || !htmlContent.trim()}
                    className="flex-1 bg-gold hover:bg-gold/90"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Crea Campagna
                  </Button>
                  <Button variant="outline" onClick={resetForm}>
                    Reset
                  </Button>
                </div>
              </motion.div>
            ) : selectedCampaign ? (
              <motion.div
                key="campaign-detail"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className={`text-xl font-bold ${textPrimary}`}>{selectedCampaign.name}</h3>
                    <p className={`text-sm ${textSecondary}`}>{selectedCampaign.subject}</p>
                  </div>
                  <div className="flex gap-2">
                    {!selectedCampaign.is_sent && (
                      <Button
                        onClick={() => handleSendCampaign(selectedCampaign)}
                        disabled={isSending}
                        className="bg-gold hover:bg-gold/90"
                      >
                        {isSending ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            Invia
                          </>
                        )}
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      onClick={() => handleDeleteCampaign(selectedCampaign.id)}
                      className="text-gray-400 border-gray-500 hover:bg-gray-500/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Stats */}
                {stats && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className={`p-4 rounded-xl ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'}`}>
                      <div className={`text-2xl font-bold ${textPrimary}`}>{stats.total_sent}</div>
                      <div className={`text-xs ${textSecondary}`}>Email Inviate</div>
                    </div>
                    <div className={`p-4 rounded-xl ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'}`}>
                      <div className="text-2xl font-bold text-gold">{stats.open_rate}%</div>
                      <div className={`text-xs ${textSecondary}`}>Open Rate</div>
                    </div>
                    <div className={`p-4 rounded-xl ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'}`}>
                      <div className="text-2xl font-bold text-gold">{stats.click_rate}%</div>
                      <div className={`text-xs ${textSecondary}`}>Click Rate</div>
                    </div>
                    <div className={`p-4 rounded-xl ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'}`}>
                      <div className="text-2xl font-bold text-gray-400">{stats.bounce_rate}%</div>
                      <div className={`text-xs ${textSecondary}`}>Bounce Rate</div>
                    </div>
                  </div>
                )}

                {/* Target Info */}
                <div className={`p-4 rounded-xl ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'}`}>
                  <div className="flex items-center gap-4 text-sm">
                    <span className={textSecondary}>
                      <strong>Regione:</strong> {selectedCampaign.target_region || 'Tutte'}
                    </span>
                    <span className={textSecondary}>
                      <strong>Settore:</strong> {selectedCampaign.target_industry || 'Tutti'}
                    </span>
                    <span className={textSecondary}>
                      <strong>Creata:</strong>{' '}
                      {new Date(selectedCampaign.created_at).toLocaleDateString('it-IT')}
                    </span>
                  </div>
                </div>

                {/* Test Email */}
                <div className={`p-4 rounded-xl ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'}`}>
                  <h4 className={`font-semibold mb-2 ${textPrimary}`}>Invia Email di Test</h4>
                  <div className="flex gap-2">
                    <input
                      type="email"
                      value={testEmail}
                      onChange={(e) => setTestEmail(e.target.value)}
                      placeholder="test@example.com"
                      className={`flex-1 rounded-lg p-2 ${inputBg} border`}
                    />
                    <Button onClick={handleSendTest} variant="outline">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center py-12"
              >
                <Mail className={`w-16 h-16 mb-4 ${textSecondary} opacity-50`} />
                <h3 className={`text-lg font-medium mb-2 ${textPrimary}`}>
                  Seleziona una campagna
                </h3>
                <p className={`text-sm ${textSecondary}`}>
                  Oppure crea una nuova campagna per iniziare
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default EmailCampaignPro;
