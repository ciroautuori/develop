/**
 * LeadFinderProModal - SISTEMA COMPLETO A STEP
 *
 * STEP 1: Ricerca Lead (Google Places + filtri)
 * STEP 2: Selezione e Arricchimento
 * STEP 3: Azione (Salva CRM / Crea Email Campaign)
 * STEP 4: Statistiche Conversione
 *
 * @uses types/lead.types - Types centralizzati
 * @uses constants/locations - Città italiane
 * @uses constants/industries - Settori business
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X, Search, Target, Building2, MapPin, Phone, Mail,
  Globe, Star, Loader2, Save, CheckCircle2, XCircle,
  RefreshCw, ExternalLink, Zap, TrendingUp, ArrowRight,
  Filter, ChevronDown, ChevronUp, Users, Sparkles,
  BarChart3, Send, UserPlus, Calendar, Clock, Tag,
  CheckSquare, Square, AlertCircle, ArrowLeft, FileText
} from 'lucide-react';
import { cn } from '../../../../../../shared/lib/utils';
import { useTheme } from '../../../../../../shared/contexts/ThemeContext';
import { toast } from 'sonner';

// Centralizzati
import { ITALIAN_REGIONS } from '../../constants/locations';
import type { LeadCampaignStats } from '../../types/lead.types';

// Hook per CRM persistence
import { useLeadSearch } from '../../../../hooks/marketing/useLeadSearch';

// ============================================================================
// TYPES
// ============================================================================

type Step = 'search' | 'select' | 'action' | 'stats';

interface PlaceResult {
  place_id: string;
  name: string;
  address: string;
  phone: string | null;
  website: string | null;
  email?: string | null;
  rating: number | null;
  reviews_count: number;
  status: string;
  types: string[];
  primary_type: string | null;
  maps_url: string;
  source: string;
}

interface EnrichmentScore {
  score: number;
  grade: string;
  breakdown: Record<string, number>;
  recommendation: string;
  email?: string;
}

interface LeadWithScore extends PlaceResult {
  enrichment_score?: EnrichmentScore;
  selected?: boolean;
  enriching?: boolean;
  saved?: boolean;
  industry?: string;
}

interface LeadStats {
  total_found: number;
  saved_to_crm: number;
  email_campaigns_sent: number;
  converted_to_customer: number;
  rejected: number;
  pending: number;
  conversion_rate: number;
  by_industry: Record<string, { total: number; converted: number; rejected: number }>;
  by_city: Record<string, { total: number; converted: number }>;
  recent_leads: Array<{
    id: number;
    company: string;
    status: string;
    created_at: string;
  }>;
}

interface LeadFinderProModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateEmailCampaign?: (leads: LeadWithScore[]) => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const ITALIAN_CITIES = [
  { name: 'Salerno', region: 'Campania', priority: true },
  { name: 'Napoli', region: 'Campania', priority: true },
  { name: 'Caserta', region: 'Campania', priority: true },
  { name: 'Avellino', region: 'Campania', priority: true },
  { name: 'Benevento', region: 'Campania', priority: true },
  { name: 'Roma', region: 'Lazio', priority: false },
  { name: 'Milano', region: 'Lombardia', priority: false },
  { name: 'Torino', region: 'Piemonte', priority: false },
  { name: 'Bologna', region: 'Emilia-Romagna', priority: false },
  { name: 'Firenze', region: 'Toscana', priority: false },
  { name: 'Bari', region: 'Puglia', priority: false },
  { name: 'Palermo', region: 'Sicilia', priority: false },
];

const BUSINESS_SECTORS = [
  { value: 'ristorante', label: 'Ristoranti', icon: '🍽️', query: 'ristorante' },
  { value: 'hotel', label: 'Hotel', icon: '🏨', query: 'hotel' },
  { value: 'avvocato', label: 'Avvocati', icon: '⚖️', query: 'studio legale avvocato' },
  { value: 'commercialista', label: 'Commercialisti', icon: '📊', query: 'studio commercialista' },
  { value: 'medico', label: 'Studi Medici', icon: '🏥', query: 'studio medico' },
  { value: 'dentista', label: 'Dentisti', icon: '🦷', query: 'dentista' },
  { value: 'parrucchiere', label: 'Parrucchieri', icon: '💇', query: 'parrucchiere' },
  { value: 'estetista', label: 'Centri Estetici', icon: '💅', query: 'centro estetico' },
  { value: 'palestra', label: 'Palestre', icon: '🏋️', query: 'palestra fitness' },
  { value: 'immobiliare', label: 'Agenzie Immobiliari', icon: '🏠', query: 'agenzia immobiliare' },
  { value: 'autofficina', label: 'Autofficine', icon: '🔧', query: 'autofficina carrozzeria' },
  { value: 'negozio', label: 'Negozi', icon: '🛍️', query: 'negozio abbigliamento' },
];

const SIZE_FILTERS = [
  { value: 'all', label: 'Tutte' },
  { value: 'micro', label: 'Micro (1-9)' },
  { value: 'piccola', label: 'Piccola (10-49)' },
  { value: 'media', label: 'Media (50-249)' },
];

const RATING_FILTERS = [
  { value: 0, label: 'Qualsiasi' },
  { value: 3, label: '3+ ⭐' },
  { value: 4, label: '4+ ⭐⭐' },
  { value: 4.5, label: '4.5+ ⭐⭐⭐' },
];

// ============================================================================
// API
// ============================================================================

const LeadAPI = {
  async searchPlaces(query: string, city: string): Promise<PlaceResult[]> {
    const res = await fetch(
      `/api/v1/marketing/leads/google-places?query=${encodeURIComponent(query)}&city=${encodeURIComponent(city)}`,
      { headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` } }
    );
    if (!res.ok) throw new Error('Failed to search');
    const data = await res.json();
    return data.results || [];
  },

  async enrichLead(placeId: string): Promise<EnrichmentScore> {
    const res = await fetch(`/api/v1/marketing/leads/${placeId}/enrich`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to enrich');
    return res.json();
  },

  async saveToCRM(leads: LeadWithScore[]): Promise<{ created: number; skipped: number }> {
    const res = await fetch('/api/v1/customers/bulk-create-from-leads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify({
        leads: leads.map(l => ({
          company: l.name,
          industry: l.industry || l.primary_type || 'general',
          size: 'micro',
          location: l.address.split(',').pop()?.trim() || '',
          address: l.address,
          phone: l.phone || '',
          email: l.enrichment_score?.email || l.email || '',
          website: l.website || '',
          need: 'marketing_digitale',
          need_reason: 'Lead trovato via Google Places',
          score: l.enrichment_score?.score || 50,
          google_rating: l.rating || 0,
          reviews_count: l.reviews_count || 0,
        })),
      }),
    });
    if (!res.ok) throw new Error('Failed to save');
    const data = await res.json();
    return { created: data.created_count, skipped: data.skipped_count };
  },

  async getLeadStats(): Promise<LeadStats> {
    const res = await fetch('/api/v1/marketing/leads/stats', {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to get stats');
    return res.json();
  },

  async getRecentLeads(): Promise<any[]> {
    const res = await fetch('/api/v1/customers?source=advertising&limit=10&sort=-created_at', {
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
    });
    if (!res.ok) throw new Error('Failed to get leads');
    const data = await res.json();
    return data.items || [];
  },

  async runAutoPilot(sector: string, city: string, minScore: number = 75): Promise<any> {
    const res = await fetch('/api/v1/marketing/acquisition/auto-pilot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify({
        sector,
        city,
        min_score: minScore,
        max_leads: 20,
        auto_campaign: true,
        radius_km: 25
      }),
    });
    if (!res.ok) throw new Error('Auto-Pilot failed');
    return res.json();
  },
};

// ============================================================================
// STEP INDICATOR
// ============================================================================

const StepIndicator = ({
  currentStep,
  onStepClick,
  isDark
}: {
  currentStep: Step;
  onStepClick: (step: Step) => void;
  isDark: boolean;
}) => {
  const steps: { id: Step; label: string; icon: React.ReactNode }[] = [
    { id: 'search', label: 'Cerca', icon: <Search className="w-4 h-4" /> },
    { id: 'select', label: 'Seleziona', icon: <CheckSquare className="w-4 h-4" /> },
    { id: 'action', label: 'Azione', icon: <Zap className="w-4 h-4" /> },
    { id: 'stats', label: 'Statistiche', icon: <BarChart3 className="w-4 h-4" /> },
  ];

  const getStepIndex = (step: Step) => steps.findIndex(s => s.id === step);
  const currentIndex = getStepIndex(currentStep);

  return (
    <div className="flex items-center justify-center gap-2 mb-6">
      {steps.map((step, index) => (
        <button
          key={step.id}
          onClick={() => onStepClick(step.id)}
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg transition-all',
            currentStep === step.id
              ? 'bg-gold text-white'
              : index < currentIndex
                ? 'bg-gold/20 text-gold cursor-pointer hover:bg-gold/30'
                : isDark
                  ? 'bg-white/5 text-gray-500'
                  : 'bg-gray-100 text-gray-400'
          )}
          disabled={index > currentIndex}
        >
          {step.icon}
          <span className="text-sm font-medium hidden sm:inline">{step.label}</span>
        </button>
      ))}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function LeadFinderProModal({
  isOpen,
  onClose,
  onCreateEmailCampaign
}: LeadFinderProModalProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Hook centralizzato per CRM persistence
  const { saveToCRM: saveToCRMHook } = useLeadSearch();

  // Navigation
  const [step, setStep] = useState<Step>('search');

  // Search state
  const [sector, setSector] = useState('');
  const [city, setCity] = useState('');
  const [minRating, setMinRating] = useState(0);
  const [sizeFilter, setSizeFilter] = useState('all');
  const [isSearching, setIsSearching] = useState(false);

  // Results state
  const [leads, setLeads] = useState<LeadWithScore[]>([]);
  const [selectedLeads, setSelectedLeads] = useState<Set<string>>(new Set());
  const [isEnriching, setIsEnriching] = useState(false);
  const [enrichProgress, setEnrichProgress] = useState(0);

  // Action state
  const [isSaving, setIsSaving] = useState(false);
  const [saveResult, setSaveResult] = useState<{ created: number; skipped: number } | null>(null);

  // Stats state
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [recentLeads, setRecentLeads] = useState<any[]>([]);
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  // Auto-Pilot state
  const [autoPilotEnabled, setAutoPilotEnabled] = useState(false);
  const [autoPilotRunning, setAutoPilotRunning] = useState(false);
  const [autoPilotResult, setAutoPilotResult] = useState<{
    run_id: string;
    leads_found: number;
    leads_saved: number;
    leads_campaigned: number;
    high_value_leads: any[];
  } | null>(null);

  // Theme colors
  const overlayBg = isDark ? 'bg-black/80' : 'bg-black/60';
  const modalBg = isDark ? 'bg-[#0A0A0A]' : 'bg-white';
  const cardBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200';

  // ========================================
  // SEARCH LOGIC
  // ========================================

  const handleSearch = async () => {
    if (!sector || !city) {
      toast.error('Seleziona settore e città');
      return;
    }

    setIsSearching(true);
    try {
      const sectorData = BUSINESS_SECTORS.find(s => s.value === sector);
      const results = await LeadAPI.searchPlaces(sectorData?.query || sector, city);

      // Apply rating filter
      const filtered = results.filter(r => (r.rating || 0) >= minRating);

      setLeads(filtered.map(r => ({
        ...r,
        selected: false,
        enriching: false,
        saved: false,
        industry: sector
      })));

      toast.success(`Trovati ${filtered.length} lead!`);
      setStep('select');
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Errore durante la ricerca. Riprova più tardi.');
      setLeads([]);
    } finally {
      setIsSearching(false);
    }
  };

  // ========================================
  // AUTO-PILOT LOGIC (HUNTER-KILLER LOOP)
  // ========================================

  const handleAutoPilot = async () => {
    if (!sector || !city) {
      toast.error('Seleziona settore e città per attivare Auto-Pilot');
      return;
    }

    setAutoPilotRunning(true);
    toast.loading('🤖 Auto-Pilot attivo: ricerca e salvataggio automatico...', { id: 'autopilot' });

    try {
      const result = await LeadAPI.runAutoPilot(sector, city, 75);
      setAutoPilotResult(result);

      if (result.leads_saved > 0) {
        toast.success(
          `✅ Auto-Pilot completato! ${result.leads_saved} lead salvati, ${result.leads_campaigned} aggiunti a campagna.`,
          { id: 'autopilot', duration: 6000 }
        );
      } else if (result.leads_found > 0) {
        toast.info(
          `ℹ️ Trovati ${result.leads_found} lead ma nessuno ha superato il punteggio minimo.`,
          { id: 'autopilot' }
        );
      } else {
        toast.info('Nessun lead trovato per questa ricerca.', { id: 'autopilot' });
      }

      // Show high-value leads if any
      if (result.high_value_leads?.length > 0) {
        setLeads(result.high_value_leads.map((l: any) => ({
          place_id: l.name,
          name: l.name,
          address: '',
          phone: l.phone,
          website: l.website,
          rating: l.rating,
          reviews_count: 0,
          status: 'OPERATIONAL',
          types: [],
          primary_type: sector,
          maps_url: '',
          source: 'auto_pilot',
          selected: false,
          enriching: false,
          saved: true,
          enrichment_score: { score: l.score, grade: l.grade },
          industry: sector
        })));
        setStep('select');
      }
    } catch (error) {
      console.error('Auto-Pilot error:', error);
      toast.error('❌ Auto-Pilot fallito. Riprova più tardi.', { id: 'autopilot' });
    } finally {
      setAutoPilotRunning(false);
    }
  };

  // ========================================
  // ENRICHMENT LOGIC
  // ========================================

  const handleEnrichSelected = async () => {
    if (selectedLeads.size === 0) {
      toast.error('Seleziona almeno un lead');
      return;
    }

    setIsEnriching(true);
    setEnrichProgress(0);

    const leadsToEnrich = leads.filter(l => selectedLeads.has(l.place_id) && !l.enrichment_score);
    let processed = 0;

    for (const lead of leadsToEnrich) {
      setLeads(prev => prev.map(l =>
        l.place_id === lead.place_id ? { ...l, enriching: true } : l
      ));

      try {
        const score = await LeadAPI.enrichLead(lead.place_id);
        setLeads(prev => prev.map(l =>
          l.place_id === lead.place_id
            ? { ...l, enrichment_score: score, enriching: false }
            : l
        ));
      } catch (error) {
        console.error('Enrichment error:', error);
        toast.error(`Errore nell'arricchimento di ${lead.name}`);
        setLeads(prev => prev.map(l =>
          l.place_id === lead.place_id
            ? { ...l, enriching: false } // Reset enriching state
            : l
        ));
      }

      processed++;
      setEnrichProgress(Math.round((processed / leadsToEnrich.length) * 100));
      await new Promise(r => setTimeout(r, 500)); // Rate limit
    }

    setIsEnriching(false);
    toast.success(`${processed} lead arricchiti!`);
  };

  // ========================================
  // ACTION LOGIC
  // ========================================

  const handleSaveToCRM = async () => {
    const selected = leads.filter(l => selectedLeads.has(l.place_id));
    if (selected.length === 0) {
      toast.error('Nessun lead selezionato');
      return;
    }

    setIsSaving(true);
    try {
      // Salva via API specializzata per Google Places leads
      const result = await LeadAPI.saveToCRM(selected);
      setSaveResult(result);

      // Mark as saved
      setLeads(prev => prev.map(l =>
        selectedLeads.has(l.place_id) ? { ...l, saved: true } : l
      ));

      // Log anche via hook centralizzato (per tracking)
      try {
        const leadsForHook = selected.map(l => ({
          name: l.name,
          address: l.address,
          phone: l.phone || undefined,
          website: l.website || undefined,
          rating: l.rating || undefined,
          review_count: l.reviews_count,
          category: l.industry || l.primary_type || 'general',
          lat: 0, // Non disponibile da Google Places
          lng: 0,
          distance_km: 0,
          score: l.enrichment_score?.score || 50,
          needs_match: ['marketing_digitale'],
          opportunity_level: ((l.enrichment_score?.score || 50) > 75 ? 'high' : 'medium') as 'high' | 'medium' | 'low'
        }));
        await saveToCRMHook(leadsForHook);
      } catch {
        // Hook fallback silenzioso - l'API principale ha già salvato
      }

      toast.success(`${result.created} lead salvati nel CRM!`);
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Errore durante il salvataggio nel CRM');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCreateEmailCampaign = () => {
    const selected = leads.filter(l => selectedLeads.has(l.place_id));
    if (selected.length === 0) {
      toast.error('Nessun lead selezionato');
      return;
    }

    if (onCreateEmailCampaign) {
      onCreateEmailCampaign(selected);
      toast.success(`Creazione campagna email per ${selected.length} lead...`);
      onClose();
    } else {
      toast.info('Funzione Email Campaign in arrivo!');
    }
  };

  // ========================================
  // STATS LOGIC
  // ========================================

  const loadStats = async () => {
    setIsLoadingStats(true);
    try {
      const [statsData, leadsData] = await Promise.all([
        LeadAPI.getLeadStats(),
        LeadAPI.getRecentLeads(),
      ]);
      setStats(statsData);
      setRecentLeads(leadsData);
    } catch (error) {
      console.error('Stats error:', error);
      toast.error('Errore caricamento statistiche');
      // No fallback - dashboard should show empty or error state
    } finally {
      setIsLoadingStats(false);
    }
  };

  useEffect(() => {
    if (step === 'stats') {
      loadStats();
    }
  }, [step]);

  // ========================================
  // HELPERS
  // ========================================

  const toggleSelectLead = (placeId: string) => {
    setSelectedLeads(prev => {
      const next = new Set(prev);
      if (next.has(placeId)) {
        next.delete(placeId);
      } else {
        next.add(placeId);
      }
      return next;
    });
  };

  const selectAll = () => {
    if (selectedLeads.size === leads.length) {
      setSelectedLeads(new Set());
    } else {
      setSelectedLeads(new Set(leads.map(l => l.place_id)));
    }
  };

  const handleClose = () => {
    setStep('search');
    setSector('');
    setCity('');
    setLeads([]);
    setSelectedLeads(new Set());
    setSaveResult(null);
    setStats(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className={cn('fixed inset-0 z-50 flex items-center justify-center p-4', overlayBg)}
        onClick={handleClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className={cn(
            'w-full max-w-5xl max-h-[90vh] overflow-hidden rounded-2xl shadow-2xl',
            modalBg
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 sm:p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gold/20 flex items-center justify-center">
                <Target className="w-5 h-5 text-gold" />
              </div>
              <div>
                <h2 className={cn('text-lg font-semibold', textPrimary)}>
                  Lead Finder Pro
                </h2>
                <p className={cn('text-sm', textSecondary)}>
                  Trova, arricchisci e converti lead in clienti
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

          {/* Step Indicator */}
          <div className="px-4 sm:px-6 pt-4">
            <StepIndicator
              currentStep={step}
              onStepClick={setStep}
              isDark={isDark}
            />
          </div>

          {/* Content */}
          <div className="p-4 sm:p-6 overflow-y-auto max-h-[calc(90vh-280px)]">
            {/* STEP 1: SEARCH */}
            {step === 'search' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <Sparkles className="w-12 h-12 mx-auto text-gold mb-3" />
                  <h3 className={cn('text-xl font-semibold mb-2', textPrimary)}>
                    Configura la Ricerca
                  </h3>
                  <p className={cn('text-sm', textSecondary)}>
                    Seleziona settore, città e filtri per trovare lead qualificati
                  </p>
                </div>

                {/* Sector Selection */}
                <div>
                  <label className={cn('block text-sm font-medium mb-3', textSecondary)}>
                    Settore di Business
                  </label>
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                    {BUSINESS_SECTORS.map((s) => (
                      <button
                        key={s.value}
                        onClick={() => setSector(s.value)}
                        className={cn(
                          'p-3 rounded-lg border text-center transition-all',
                          sector === s.value
                            ? 'border-gold bg-gold/10'
                            : cardBg,
                          'hover:border-gold/50'
                        )}
                      >
                        <span className="text-2xl block mb-1">{s.icon}</span>
                        <p className={cn('text-xs', textPrimary)}>{s.label}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* City Selection */}
                <div>
                  <label className={cn('block text-sm font-medium mb-3', textSecondary)}>
                    Città
                  </label>
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                    {ITALIAN_CITIES.map((c) => (
                      <button
                        key={c.name}
                        onClick={() => setCity(c.name)}
                        className={cn(
                          'px-3 py-2 rounded-lg border text-sm transition-all relative',
                          city === c.name
                            ? 'border-gold bg-gold/10 text-gold'
                            : cardBg,
                          textPrimary,
                          c.priority && 'ring-1 ring-gold/30'
                        )}
                      >
                        {c.name}
                        {c.priority && (
                          <Star className="w-3 h-3 absolute top-1 right-1 text-gold fill-gold" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Filters */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                      Rating Minimo
                    </label>
                    <select
                      value={minRating}
                      onChange={(e) => setMinRating(Number(e.target.value))}
                      className={cn(
                        'w-full px-3 py-2 rounded-lg border',
                        inputBg,
                        textPrimary
                      )}
                    >
                      {RATING_FILTERS.map((f) => (
                        <option key={f.value} value={f.value}>{f.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className={cn('block text-sm font-medium mb-2', textSecondary)}>
                      Dimensione Azienda
                    </label>
                    <select
                      value={sizeFilter}
                      onChange={(e) => setSizeFilter(e.target.value)}
                      className={cn(
                        'w-full px-3 py-2 rounded-lg border',
                        inputBg,
                        textPrimary
                      )}
                    >
                      {SIZE_FILTERS.map((f) => (
                        <option key={f.value} value={f.value}>{f.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Auto-Pilot Toggle */}
                <div className={cn('p-4 rounded-xl border-2 border-dashed', autoPilotEnabled ? 'border-gold bg-gold/5' : 'border-white/10')}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', autoPilotEnabled ? 'bg-gold/20' : 'bg-white/5')}>
                        <Zap className={cn('w-5 h-5', autoPilotEnabled ? 'text-gold' : textSecondary)} />
                      </div>
                      <div>
                        <h4 className={cn('font-medium', textPrimary)}>🤖 Auto-Pilot Mode</h4>
                        <p className={cn('text-xs', textSecondary)}>
                          Cerca, arricchisci e salva automaticamente i lead migliori
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setAutoPilotEnabled(!autoPilotEnabled)}
                      className={cn(
                        'w-12 h-6 rounded-full relative transition-colors',
                        autoPilotEnabled ? 'bg-gold' : 'bg-white/20'
                      )}
                    >
                      <div className={cn(
                        'w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all',
                        autoPilotEnabled ? 'right-0.5' : 'left-0.5'
                      )} />
                    </button>
                  </div>

                  {autoPilotEnabled && (
                    <div className={cn('p-3 rounded-lg text-sm', 'bg-gold/10 border border-gold/20')}>
                      <p className="text-gold mb-2">⚡ Quando attivo, Auto-Pilot:</p>
                      <ul className={cn('text-xs space-y-1', textSecondary)}>
                        <li>• Cerca fino a 20 lead nel settore e città selezionati</li>
                        <li>• Arricchisce ogni lead con email, telefono, rating</li>
                        <li>• Salva automaticamente lead con punteggio ≥ 75</li>
                        <li>• Aggiunge i lead salvati alla campagna "Welcome"</li>
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* STEP 2: SELECT */}
            {step === 'select' && (
              <div className="space-y-4">
                {/* Toolbar */}
                <div className={cn(
                  'flex items-center justify-between p-3 rounded-lg',
                  cardBg
                )}>
                  <div className="flex items-center gap-4">
                    <button
                      onClick={selectAll}
                      className={cn('text-sm flex items-center gap-2', textSecondary, 'hover:text-gold')}
                    >
                      {selectedLeads.size === leads.length ? (
                        <CheckSquare className="w-4 h-4 text-gold" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                      {selectedLeads.size === leads.length ? 'Deseleziona Tutti' : 'Seleziona Tutti'}
                    </button>
                    <span className={cn('text-sm', textSecondary)}>
                      {selectedLeads.size} di {leads.length} selezionati
                    </span>
                  </div>
                  <button
                    onClick={handleEnrichSelected}
                    disabled={isEnriching || selectedLeads.size === 0}
                    className={cn(
                      'px-4 py-2 rounded-lg text-sm flex items-center gap-2',
                      'bg-gold/20 text-gold hover:bg-gold/30',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
                    )}
                  >
                    {isEnriching ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        {enrichProgress}%
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4" />
                        Arricchisci Selezionati
                      </>
                    )}
                  </button>
                </div>

                {/* Lead List */}
                <div className="space-y-3">
                  {leads.map((lead) => (
                    <motion.div
                      key={lead.place_id}
                      layout
                      className={cn(
                        'p-4 rounded-xl border transition-all',
                        selectedLeads.has(lead.place_id)
                          ? 'border-gold bg-gold/5'
                          : cardBg,
                        lead.saved && 'opacity-60'
                      )}
                    >
                      <div className="flex items-start gap-4">
                        {/* Checkbox */}
                        <button
                          onClick={() => !lead.saved && toggleSelectLead(lead.place_id)}
                          disabled={lead.saved}
                          className="flex-shrink-0 mt-1"
                        >
                          {selectedLeads.has(lead.place_id) ? (
                            <CheckSquare className="w-5 h-5 text-gold" />
                          ) : (
                            <Square className={cn('w-5 h-5', textSecondary)} />
                          )}
                        </button>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h4 className={cn('font-semibold', textPrimary)}>
                                {lead.name}
                                {lead.saved && (
                                  <span className="ml-2 text-xs text-gold">✓ Salvato</span>
                                )}
                              </h4>
                              <p className={cn('text-sm flex items-center gap-1', textSecondary)}>
                                <MapPin className="w-3 h-3" />
                                {lead.address}
                              </p>
                            </div>
                            {lead.rating && (
                              <div className="flex items-center gap-1 text-gold">
                                <Star className="w-4 h-4 fill-current" />
                                <span className="text-sm font-medium">{lead.rating}</span>
                                <span className={cn('text-xs', textSecondary)}>
                                  ({lead.reviews_count})
                                </span>
                              </div>
                            )}
                          </div>

                          <div className="flex flex-wrap items-center gap-3 text-sm">
                            {lead.phone && (
                              <span className={cn('flex items-center gap-1', textSecondary)}>
                                <Phone className="w-3 h-3" />
                                {lead.phone}
                              </span>
                            )}
                            {lead.website && (
                              <a
                                href={lead.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-gold hover:underline"
                              >
                                <Globe className="w-3 h-3" />
                                Website
                              </a>
                            )}
                            {lead.enrichment_score?.email && (
                              <span className={cn('flex items-center gap-1', textSecondary)}>
                                <Mail className="w-3 h-3" />
                                {lead.enrichment_score.email}
                              </span>
                            )}
                            <span className={cn(
                              'px-2 py-0.5 rounded text-xs',
                              isDark ? 'bg-white/10' : 'bg-gray-200'
                            )}>
                              {BUSINESS_SECTORS.find(s => s.value === lead.industry)?.icon} {lead.industry}
                            </span>
                          </div>

                          {/* Enrichment Score */}
                          {lead.enrichment_score && (
                            <div className={cn(
                              'mt-3 p-3 rounded-lg flex items-center justify-between',
                              isDark ? 'bg-white/5' : 'bg-gray-100'
                            )}>
                              <div className="flex items-center gap-3">
                                <div className={cn(
                                  'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold',
                                  lead.enrichment_score.score >= 80
                                    ? 'bg-gold/20 text-gold'
                                    : lead.enrichment_score.score >= 60
                                      ? 'bg-gold/20 text-gold'
                                      : 'bg-gray-500/20 text-gray-400'
                                )}>
                                  {lead.enrichment_score.score}
                                </div>
                                <div>
                                  <p className={cn('text-sm font-medium', textPrimary)}>
                                    Grade: {lead.enrichment_score.grade}
                                  </p>
                                  <p className={cn('text-xs', textSecondary)}>
                                    {lead.enrichment_score.recommendation}
                                  </p>
                                </div>
                              </div>
                            </div>
                          )}

                          {lead.enriching && (
                            <div className={cn('mt-3 flex items-center gap-2', textSecondary)}>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span className="text-sm">Arricchimento in corso...</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* STEP 3: ACTION */}
            {step === 'action' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <Zap className="w-12 h-12 mx-auto text-gold mb-3" />
                  <h3 className={cn('text-xl font-semibold mb-2', textPrimary)}>
                    Cosa vuoi fare con i {selectedLeads.size} lead selezionati?
                  </h3>
                  <p className={cn('text-sm', textSecondary)}>
                    Scegli un'azione da eseguire
                  </p>
                </div>

                {saveResult && (
                  <div className={cn(
                    'p-4 rounded-lg border mb-6',
                    'border-gold/30 bg-gold/10'
                  )}>
                    <div className="flex items-center gap-3">
                      <CheckCircle2 className="w-6 h-6 text-gold" />
                      <div>
                        <p className={cn('font-medium', textPrimary)}>
                          {saveResult.created} lead salvati nel CRM!
                        </p>
                        {saveResult.skipped > 0 && (
                          <p className={cn('text-sm', textSecondary)}>
                            {saveResult.skipped} duplicati saltati
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Save to CRM */}
                  <button
                    onClick={handleSaveToCRM}
                    disabled={isSaving || selectedLeads.size === 0}
                    className={cn(
                      'p-6 rounded-xl border text-left transition-all',
                      cardBg,
                      'hover:border-gold group',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
                    )}
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <UserPlus className="w-6 h-6 text-gold" />
                      </div>
                      <div className="flex-1">
                        <h4 className={cn('font-semibold mb-1', textPrimary)}>
                          Salva nel CRM
                        </h4>
                        <p className={cn('text-sm', textSecondary)}>
                          Aggiungi i lead al database clienti per follow-up manuali
                        </p>
                        {isSaving && (
                          <div className="flex items-center gap-2 mt-2 text-gold">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span className="text-sm">Salvataggio...</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </button>

                  {/* Create Email Campaign */}
                  <button
                    onClick={handleCreateEmailCampaign}
                    disabled={selectedLeads.size === 0}
                    className={cn(
                      'p-6 rounded-xl border text-left transition-all',
                      cardBg,
                      'hover:border-gold group',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
                    )}
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Send className="w-6 h-6 text-gold" />
                      </div>
                      <div className="flex-1">
                        <h4 className={cn('font-semibold mb-1', textPrimary)}>
                          Crea Email Campaign
                        </h4>
                        <p className={cn('text-sm', textSecondary)}>
                          Genera una campagna email automatica con AI
                        </p>
                      </div>
                    </div>
                  </button>

                  {/* Schedule Follow-up */}
                  <button
                    disabled
                    className={cn(
                      'p-6 rounded-xl border text-left transition-all opacity-50 cursor-not-allowed',
                      cardBg
                    )}
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center">
                        <Calendar className="w-6 h-6 text-gold" />
                      </div>
                      <div className="flex-1">
                        <h4 className={cn('font-semibold mb-1', textPrimary)}>
                          Pianifica Follow-up
                        </h4>
                        <p className={cn('text-sm', textSecondary)}>
                          Crea task di follow-up per il team sales
                        </p>
                        <span className="text-xs text-gold">Coming Soon</span>
                      </div>
                    </div>
                  </button>

                  {/* Export */}
                  <button
                    disabled
                    className={cn(
                      'p-6 rounded-xl border text-left transition-all opacity-50 cursor-not-allowed',
                      cardBg
                    )}
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center">
                        <FileText className="w-6 h-6 text-gold" />
                      </div>
                      <div className="flex-1">
                        <h4 className={cn('font-semibold mb-1', textPrimary)}>
                          Esporta CSV
                        </h4>
                        <p className={cn('text-sm', textSecondary)}>
                          Scarica i lead in formato CSV/Excel
                        </p>
                        <span className="text-xs text-gold">Coming Soon</span>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            )}

            {/* STEP 4: STATS */}
            {step === 'stats' && (
              <div className="space-y-6">
                {isLoadingStats ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-gold" />
                  </div>
                ) : stats ? (
                  <>
                    {/* KPI Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className={cn('p-4 rounded-xl border', cardBg)}>
                        <div className="flex items-center gap-2 mb-2">
                          <Target className="w-5 h-5 text-gold" />
                          <span className={cn('text-sm', textSecondary)}>Lead Trovati</span>
                        </div>
                        <p className={cn('text-2xl font-bold', textPrimary)}>
                          {stats.total_found}
                        </p>
                      </div>
                      <div className={cn('p-4 rounded-xl border', cardBg)}>
                        <div className="flex items-center gap-2 mb-2">
                          <UserPlus className="w-5 h-5 text-gold" />
                          <span className={cn('text-sm', textSecondary)}>Salvati CRM</span>
                        </div>
                        <p className={cn('text-2xl font-bold', textPrimary)}>
                          {stats.saved_to_crm}
                        </p>
                      </div>
                      <div className={cn('p-4 rounded-xl border', cardBg)}>
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle2 className="w-5 h-5 text-gold" />
                          <span className={cn('text-sm', textSecondary)}>Convertiti</span>
                        </div>
                        <p className={cn('text-2xl font-bold text-gold')}>
                          {stats.converted_to_customer}
                        </p>
                      </div>
                      <div className={cn('p-4 rounded-xl border', cardBg)}>
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="w-5 h-5 text-gold" />
                          <span className={cn('text-sm', textSecondary)}>Conversion Rate</span>
                        </div>
                        <p className={cn('text-2xl font-bold text-gold')}>
                          {stats.conversion_rate.toFixed(1)}%
                        </p>
                      </div>
                    </div>

                    {/* By Industry */}
                    <div className={cn('p-4 rounded-xl border', cardBg)}>
                      <h4 className={cn('font-semibold mb-4', textPrimary)}>
                        Performance per Settore
                      </h4>
                      <div className="space-y-3">
                        {Object.entries(stats.by_industry).map(([industry, data]) => {
                          const sector = BUSINESS_SECTORS.find(s => s.value === industry);
                          const convRate = data.total > 0 ? (data.converted / data.total * 100) : 0;
                          return (
                            <div key={industry} className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span>{sector?.icon || '📊'}</span>
                                <span className={textPrimary}>{sector?.label || industry}</span>
                              </div>
                              <div className="flex items-center gap-4">
                                <span className={cn('text-sm', textSecondary)}>
                                  {data.total} lead
                                </span>
                                <span className="text-sm text-gold">
                                  {data.converted} ✓
                                </span>
                                <span className="text-sm text-gray-400">
                                  {data.rejected} ✗
                                </span>
                                <div className="w-20 h-2 rounded-full bg-white/10 overflow-hidden">
                                  <div
                                    className="h-full bg-gold"
                                    style={{ width: `${convRate}%` }}
                                  />
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* By City */}
                    <div className={cn('p-4 rounded-xl border', cardBg)}>
                      <h4 className={cn('font-semibold mb-4', textPrimary)}>
                        Performance per Città
                      </h4>
                      <div className="grid grid-cols-3 gap-4">
                        {Object.entries(stats.by_city).map(([city, data]) => (
                          <div
                            key={city}
                            className={cn(
                              'p-3 rounded-lg',
                              isDark ? 'bg-white/5' : 'bg-gray-100'
                            )}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <MapPin className="w-4 h-4 text-gold" />
                              <span className={cn('font-medium', textPrimary)}>{city}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                              <span className={textSecondary}>{data.total} lead</span>
                              <span className="text-gold">{data.converted} convertiti</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Recent Activity */}
                    <div className={cn('p-4 rounded-xl border', cardBg)}>
                      <h4 className={cn('font-semibold mb-4', textPrimary)}>
                        Attività Recente
                      </h4>
                      <div className="space-y-2">
                        {stats.recent_leads.map((lead) => (
                          <div
                            key={lead.id}
                            className={cn(
                              'flex items-center justify-between p-2 rounded-lg',
                              isDark ? 'bg-white/5' : 'bg-gray-100'
                            )}
                          >
                            <div className="flex items-center gap-3">
                              <Building2 className={cn('w-4 h-4', textSecondary)} />
                              <span className={textPrimary}>{lead.company}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className={cn(
                                'px-2 py-0.5 rounded text-xs',
                                lead.status === 'WON' ? 'bg-gold/20 text-gold' :
                                  lead.status === 'LOST' ? 'bg-gray-500/20 text-gray-400' :
                                    'bg-gold/20 text-gold'
                              )}>
                                {lead.status}
                              </span>
                              <span className={cn('text-xs', textSecondary)}>
                                {lead.created_at}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <AlertCircle className={cn('w-12 h-12 mx-auto mb-4', textSecondary)} />
                    <p className={textSecondary}>Impossibile caricare le statistiche</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-4 sm:p-6 border-t border-white/10">
            <button
              onClick={() => {
                const steps: Step[] = ['search', 'select', 'action', 'stats'];
                const currentIndex = steps.indexOf(step);
                if (currentIndex > 0) {
                  setStep(steps[currentIndex - 1]);
                }
              }}
              disabled={step === 'search'}
              className={cn(
                'px-4 py-2 rounded-lg flex items-center gap-2 transition-colors',
                step === 'search'
                  ? 'opacity-50 cursor-not-allowed'
                  : isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100',
                textSecondary
              )}
            >
              <ArrowLeft className="w-4 h-4" />
              Indietro
            </button>

            {step === 'search' && (
              <div className="flex items-center gap-3">
                {autoPilotEnabled ? (
                  <button
                    onClick={handleAutoPilot}
                    disabled={autoPilotRunning || !sector || !city}
                    className="px-6 py-2 bg-gradient-to-r from-gold to-yellow-500 text-black font-semibold rounded-lg hover:from-gold/90 hover:to-yellow-500/90 disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-gold/20"
                  >
                    {autoPilotRunning ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Zap className="w-4 h-4" />
                    )}
                    🤖 Avvia Auto-Pilot
                  </button>
                ) : (
                  <button
                    onClick={handleSearch}
                    disabled={isSearching || !sector || !city}
                    className="px-6 py-2 bg-gold text-white rounded-lg hover:bg-gold/90 disabled:opacity-50 flex items-center gap-2"
                  >
                    {isSearching ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                    Cerca Lead
                  </button>
                )}
              </div>
            )}

            {step === 'select' && (
              <button
                onClick={() => setStep('action')}
                disabled={selectedLeads.size === 0}
                className="px-6 py-2 bg-gold text-white rounded-lg hover:bg-gold/90 disabled:opacity-50 flex items-center gap-2"
              >
                Continua
                <ArrowRight className="w-4 h-4" />
              </button>
            )}

            {step === 'action' && (
              <button
                onClick={() => setStep('stats')}
                className="px-6 py-2 bg-gold text-white rounded-lg hover:bg-gold/90 flex items-center gap-2"
              >
                <BarChart3 className="w-4 h-4" />
                Vedi Statistiche
              </button>
            )}

            {step === 'stats' && (
              <button
                onClick={() => {
                  setStep('search');
                  setSector('');
                  setCity('');
                  setLeads([]);
                  setSelectedLeads(new Set());
                  setSaveResult(null);
                }}
                className="px-6 py-2 bg-gold text-white rounded-lg hover:bg-gold/90 flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Nuova Ricerca
              </button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// ============================================================================
// DEMO DATA GENERATOR
// ============================================================================

// Demo generator removed

export default LeadFinderProModal;
