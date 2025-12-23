/**
 * LeadFinderInline - VERSIONE INLINE (NO MODAL)
 * Componente per tab "Trova Clienti" - Design System Compliant
 *
 * STEP 1: Ricerca Lead (Google Places + filtri)
 * STEP 2: Selezione e Arricchimento
 * STEP 3: Azione (Salva CRM / Crea Email Campaign)
 * STEP 4: Statistiche Conversione
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Target, Building2, MapPin, Phone, Mail,
  Globe, Star, Loader2, Save, CheckCircle2, XCircle,
  RefreshCw, ExternalLink, Zap, TrendingUp, ArrowRight,
  Filter, Users, Sparkles, BarChart3, Send, UserPlus,
  CheckSquare, Square, AlertCircle, ArrowLeft
} from 'lucide-react';
import { cn } from '../../../../../shared/lib/utils';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';

// Centralizzati
import { ITALIAN_REGIONS } from '../constants/locations';

// Hook per CRM persistence
import { useLeadSearch } from '../../../hooks/marketing/useLeadSearch';

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

interface LeadFinderInlineProps {
  onCreateEmailCampaign?: (leads: LeadWithScore[]) => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const BUSINESS_SECTORS = [
  { value: 'restaurant', label: 'Ristoranti', icon: '🍽️', query: 'ristorante' },
  { value: 'hotel', label: 'Hotel', icon: '🏨', query: 'hotel' },
  { value: 'beauty', label: 'Beauty', icon: '💅', query: 'centro estetico' },
  { value: 'fitness', label: 'Fitness', icon: '💪', query: 'palestra' },
  { value: 'medical', label: 'Medici', icon: '🏥', query: 'studio medico' },
  { value: 'legal', label: 'Avvocati', icon: '⚖️', query: 'studio legale' },
  { value: 'accounting', label: 'Commercialisti', icon: '📊', query: 'commercialista' },
  { value: 'real_estate', label: 'Immobiliare', icon: '🏠', query: 'agenzia immobiliare' },
  { value: 'auto', label: 'Auto', icon: '🚗', query: 'concessionaria auto' },
  { value: 'retail', label: 'Negozi', icon: '🛍️', query: 'negozio' },
  { value: 'tech', label: 'Tech', icon: '💻', query: 'azienda informatica' },
  { value: 'construction', label: 'Edilizia', icon: '🏗️', query: 'impresa edile' },
];

// Opzioni raggio di ricerca
const RADIUS_OPTIONS = [
  { value: 5, label: '5 km', description: 'Quartiere' },
  { value: 10, label: '10 km', description: 'Città' },
  { value: 25, label: '25 km', description: 'Provincia' },
  { value: 50, label: '50 km', description: 'Regione' },
  { value: 100, label: '100 km', description: 'Multi-regione' },
];

// API Service
const LeadAPI = {
  async searchPlaces(query: string, location: string, lat?: number, lng?: number, radius?: number): Promise<PlaceResult[]> {
    const token = localStorage.getItem('admin_token');
    let url = `/api/v1/marketing/acquisition/search?query=${encodeURIComponent(query)}`;

    // Se abbiamo coordinate, usa ricerca geolocalizzata
    if (lat && lng && radius) {
      url += `&lat=${lat}&lng=${lng}&radius=${radius * 1000}`; // radius in metri
    } else {
      url += `&city=${encodeURIComponent(location)}`;
    }

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Search failed');
    const data = await res.json();
    return data.results || [];
  },

  async enrichLead(placeId: string): Promise<EnrichmentScore> {
    const token = localStorage.getItem('admin_token');
    const res = await fetch(`/api/v1/marketing/acquisition/enrich/${placeId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Enrichment failed');
    return res.json();
  },

  async saveToCRM(leads: LeadWithScore[]): Promise<{ created: number; skipped: number }> {
    const token = localStorage.getItem('admin_token');
    const res = await fetch('/api/v1/marketing/acquisition/save-leads', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ leads }),
    });
    if (!res.ok) throw new Error('Save failed');
    return res.json();
  },

  async getLeadStats(): Promise<LeadStats> {
    const token = localStorage.getItem('admin_token');
    const res = await fetch('/api/v1/marketing/acquisition/stats', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Stats failed');
    return res.json();
  },

  async getRecentLeads(): Promise<any[]> {
    const token = localStorage.getItem('admin_token');
    const res = await fetch('/api/v1/marketing/acquisition/pipeline?limit=10', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.leads || [];
  },

  async runAutoPilot(sector: string, city: string, minScore: number): Promise<any> {
    const token = localStorage.getItem('admin_token');
    const res = await fetch('/api/v1/marketing/acquisition/auto-pilot', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ sector, city, min_score: minScore }),
    });
    if (!res.ok) throw new Error('Auto-pilot failed');
    return res.json();
  },
};

// ============================================================================
// STEP INDICATOR COMPONENT
// ============================================================================

const StepIndicator = ({
  currentStep,
  onStepClick,
}: {
  currentStep: Step;
  onStepClick: (step: Step) => void;
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
    <div className="flex gap-2 p-1 rounded-xl bg-muted/50 mb-6">
      {steps.map((step, index) => (
        <button
          key={step.id}
          onClick={() => index <= currentIndex && onStepClick(step.id)}
          disabled={index > currentIndex}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg text-sm font-medium transition-all',
            currentStep === step.id
              ? 'bg-primary text-primary-foreground shadow-sm'
              : index < currentIndex
                ? 'bg-primary/20 text-primary cursor-pointer hover:bg-primary/30'
                : 'text-muted-foreground'
          )}
        >
          {step.icon}
          <span className="hidden sm:inline">{step.label}</span>
        </button>
      ))}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function LeadFinderInline({ onCreateEmailCampaign }: LeadFinderInlineProps) {
  // Hook centralizzato per CRM persistence
  const { saveToCRM: saveToCRMHook } = useLeadSearch();

  // Navigation
  const [step, setStep] = useState<Step>('search');

  // Search state - GEOLOCALIZZATO
  const [selectedSectors, setSelectedSectors] = useState<Set<string>>(new Set());
  const [minRating, setMinRating] = useState(0);
  const [isSearching, setIsSearching] = useState(false);

  // Geolocation state
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number; city: string } | null>(null);
  const [isLocating, setIsLocating] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [searchRadius, setSearchRadius] = useState(25); // default 25km
  const [customLocation, setCustomLocation] = useState(''); // input manuale opzionale

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
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  // Auto-Pilot state
  const [autoPilotRunning, setAutoPilotRunning] = useState(false);

  // ========================================
  // GEOLOCATION LOGIC
  // ========================================

  // Geocoding: converte nome città → coordinate
  const geocodeLocation = async (locationName: string): Promise<{ lat: number; lng: number; city: string } | null> => {
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(locationName)}&format=json&limit=1&countrycodes=it&accept-language=it`
      );
      const data = await res.json();
      if (data && data.length > 0) {
        return {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon),
          city: data[0].display_name.split(',')[0] // Primo elemento del nome
        };
      }
      return null;
    } catch {
      return null;
    }
  };

  // Cerca località inserita manualmente
  const searchCustomLocation = async () => {
    if (!customLocation.trim()) {
      toast.error('Inserisci una località');
      return;
    }

    setIsLocating(true);
    setLocationError(null);

    const result = await geocodeLocation(customLocation.trim());

    if (result) {
      setUserLocation(result);
      setCustomLocation(''); // Pulisci input
      toast.success(`📍 Località trovata: ${result.city}`);
    } else {
      setLocationError(`Località "${customLocation}" non trovata. Prova con un nome più specifico.`);
      toast.error('Località non trovata');
    }

    setIsLocating(false);
  };

  const requestLocation = () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocalizzazione non supportata dal browser');
      return;
    }

    setIsLocating(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        // Reverse geocoding per ottenere il nome della città - più preciso
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&accept-language=it&zoom=14`
          );
          const data = await res.json();
          // Priorità: suburb > village > town > city > municipality
          const city = data.address?.suburb ||
            data.address?.village ||
            data.address?.town ||
            data.address?.city ||
            data.address?.municipality ||
            data.address?.county ||
            'Posizione attuale';

          setUserLocation({ lat: latitude, lng: longitude, city });
          toast.success(`📍 Posizione rilevata: ${city}`);
        } catch {
          setUserLocation({ lat: latitude, lng: longitude, city: 'Posizione attuale' });
        }

        setIsLocating(false);
      },
      (error) => {
        setIsLocating(false);
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setLocationError('Permesso negato. Abilita la geolocalizzazione nelle impostazioni del browser.');
            break;
          case error.POSITION_UNAVAILABLE:
            setLocationError('Posizione non disponibile.');
            break;
          case error.TIMEOUT:
            setLocationError('Timeout nella richiesta di posizione. Usa l\'input manuale.');
            break;
          default:
            setLocationError('Errore sconosciuto nella geolocalizzazione.');
        }
        toast.error('Impossibile rilevare la posizione');
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
    );
  };

  // ========================================
  // SEARCH LOGIC
  // ========================================

  // Toggle sector selection
  const toggleSector = (sectorValue: string) => {
    setSelectedSectors(prev => {
      const next = new Set(prev);
      if (next.has(sectorValue)) {
        next.delete(sectorValue);
      } else {
        next.add(sectorValue);
      }
      return next;
    });
  };

  const handleSearch = async () => {
    if (selectedSectors.size === 0) {
      toast.error('Seleziona almeno un settore');
      return;
    }

    if (!userLocation && !customLocation.trim()) {
      toast.error('Rileva la tua posizione o inserisci una località');
      return;
    }

    setIsSearching(true);
    const allResults: LeadWithScore[] = [];

    try {
      // Search all sectors nella zona
      for (const sector of selectedSectors) {
        const sectorData = BUSINESS_SECTORS.find(s => s.value === sector);
        try {
          let results: PlaceResult[];

          if (userLocation) {
            // Ricerca geolocalizzata con raggio
            results = await LeadAPI.searchPlaces(
              sectorData?.query || sector,
              userLocation.city,
              userLocation.lat,
              userLocation.lng,
              searchRadius
            );
          } else {
            // Ricerca per località inserita manualmente
            results = await LeadAPI.searchPlaces(sectorData?.query || sector, customLocation.trim());
          }

          const filtered = results.filter(r => (r.rating || 0) >= minRating);
          allResults.push(...filtered.map(r => ({
            ...r,
            selected: false,
            enriching: false,
            saved: false,
            industry: sector
          })));
        } catch (e) {
          console.warn(`Search failed for ${sector}`);
        }
      }

      // Deduplicate by place_id
      const uniqueResults = Array.from(
        new Map(allResults.map(r => [r.place_id, r])).values()
      );

      setLeads(uniqueResults);
      const locationName = userLocation?.city || customLocation;
      toast.success(`Trovati ${uniqueResults.length} lead entro ${searchRadius}km da ${locationName}!`);
      setStep('select');
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Errore durante la ricerca');
      setLeads([]);
    } finally {
      setIsSearching(false);
    }
  };

  // ========================================
  // AUTO-PILOT LOGIC
  // ========================================

  const handleAutoPilot = async () => {
    if (selectedSectors.size === 0) {
      toast.error('Seleziona almeno un settore per attivare Auto-Pilot');
      return;
    }

    if (!userLocation && !customLocation.trim()) {
      toast.error('Rileva la tua posizione o inserisci una località');
      return;
    }

    setAutoPilotRunning(true);
    const locationName = userLocation?.city || customLocation;
    toast.loading(`🤖 Auto-Pilot attivo su ${locationName} (${searchRadius}km)...`, { id: 'autopilot' });

    let totalSaved = 0;
    try {
      for (const sector of selectedSectors) {
        try {
          const result = await LeadAPI.runAutoPilot(sector, locationName, 75);
          totalSaved += result.leads_saved || 0;
        } catch (e) {
          console.warn(`Auto-pilot failed for ${sector}`);
        }
      }

      if (totalSaved > 0) {
        toast.success(
          `✅ Auto-Pilot completato! ${totalSaved} lead salvati.`,
          { id: 'autopilot', duration: 6000 }
        );
        setStep('stats');
      } else {
        toast.info('Nessun lead trovato per questa ricerca.', { id: 'autopilot' });
      }
    } catch (error) {
      console.error('Auto-Pilot error:', error);
      toast.error('❌ Auto-Pilot fallito.', { id: 'autopilot' });
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
        setLeads(prev => prev.map(l =>
          l.place_id === lead.place_id ? { ...l, enriching: false } : l
        ));
      }

      processed++;
      setEnrichProgress(Math.round((processed / leadsToEnrich.length) * 100));
      await new Promise(r => setTimeout(r, 500));
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
      const result = await LeadAPI.saveToCRM(selected);
      setSaveResult(result);

      setLeads(prev => prev.map(l =>
        selectedLeads.has(l.place_id) ? { ...l, saved: true } : l
      ));

      toast.success(`${result.created} lead salvati nel CRM!`);
      setStep('action');
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Errore durante il salvataggio');
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
    }
  };

  // ========================================
  // STATS LOGIC
  // ========================================

  const loadStats = async () => {
    setIsLoadingStats(true);
    try {
      const statsData = await LeadAPI.getLeadStats();
      setStats(statsData);
    } catch (error) {
      console.error('Stats error:', error);
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

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-green-500 bg-green-500/10';
      case 'B': return 'text-blue-500 bg-blue-500/10';
      case 'C': return 'text-yellow-500 bg-yellow-500/10';
      default: return 'text-muted-foreground bg-muted';
    }
  };

  // ========================================
  // RENDER
  // ========================================

  return (
    <div className="space-y-6">
      {/* Step Indicator */}
      <StepIndicator currentStep={step} onStepClick={setStep} />

      {/* STEP 1: SEARCH */}
      {step === 'search' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mb-4">
              <Target className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">
              Configura la Ricerca
            </h3>
            <p className="text-sm text-muted-foreground">
              Seleziona settore e città per trovare lead qualificati
            </p>
          </div>

          {/* Sector Selection - MULTI-SELECT */}
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-medium text-foreground">
                Settori di Business <span className="text-primary">({selectedSectors.size} selezionati)</span>
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedSectors(selectedSectors.size === BUSINESS_SECTORS.length ? new Set() : new Set(BUSINESS_SECTORS.map(s => s.value)))}
              >
                {selectedSectors.size === BUSINESS_SECTORS.length ? 'Deseleziona tutti' : 'Seleziona tutti'}
              </Button>
            </div>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
              {BUSINESS_SECTORS.map((s) => (
                <button
                  key={s.value}
                  onClick={() => toggleSector(s.value)}
                  className={cn(
                    'p-4 rounded-xl border text-center transition-all relative',
                    selectedSectors.has(s.value)
                      ? 'border-primary bg-primary/10 ring-2 ring-primary/20'
                      : 'border-border bg-card hover:border-primary/50'
                  )}
                >
                  {selectedSectors.has(s.value) && (
                    <CheckCircle2 className="w-4 h-4 absolute top-2 right-2 text-primary" />
                  )}
                  <span className="text-2xl block mb-2">{s.icon}</span>
                  <p className="text-xs font-medium text-foreground">{s.label}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Location - GEOLOCALIZZAZIONE */}
          <div className="bg-card border border-border rounded-xl p-6">
            <label className="block text-sm font-medium text-foreground mb-4">
              📍 La Tua Posizione
            </label>

            <div className="space-y-4">
              {/* Geolocation Button */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={requestLocation}
                  disabled={isLocating}
                  variant={userLocation ? 'outline' : 'default'}
                  className={cn(
                    'flex-1',
                    userLocation && 'border-green-500 bg-green-500/10 text-green-600'
                  )}
                  size="lg"
                >
                  {isLocating ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Rilevamento...
                    </>
                  ) : userLocation ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 mr-2" />
                      {userLocation.city}
                    </>
                  ) : (
                    <>
                      <MapPin className="w-5 h-5 mr-2" />
                      Rileva la mia posizione
                    </>
                  )}
                </Button>

                {userLocation && (
                  <Button
                    variant="ghost"
                    size="lg"
                    onClick={() => setUserLocation(null)}
                  >
                    <XCircle className="w-4 h-4 mr-1" />
                    Reset
                  </Button>
                )}
              </div>

              {locationError && (
                <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 p-3 rounded-lg">
                  <AlertCircle className="w-4 h-4" />
                  {locationError}
                </div>
              )}

              {/* Oppure input manuale */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">oppure inserisci manualmente</span>
                </div>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={customLocation}
                  onChange={(e) => {
                    setCustomLocation(e.target.value);
                    if (e.target.value.trim()) setUserLocation(null); // reset geolocation se scrivi
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') searchCustomLocation();
                  }}
                  placeholder="Es: Salerno, Roma Centro, Milano..."
                  className="flex-1 px-4 py-3 rounded-xl border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
                <Button
                  onClick={searchCustomLocation}
                  disabled={!customLocation.trim() || isLocating}
                  variant="default"
                  size="lg"
                >
                  {isLocating ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Search className="w-5 h-5" />
                  )}
                </Button>
              </div>
            </div>
          </div>

          {/* Raggio di Ricerca */}
          <div className="bg-card border border-border rounded-xl p-6">
            <label className="block text-sm font-medium text-foreground mb-4">
              🎯 Raggio di Ricerca: <span className="text-primary font-bold">{searchRadius} km</span>
            </label>
            <div className="grid grid-cols-5 gap-2">
              {RADIUS_OPTIONS.map((r) => (
                <button
                  key={r.value}
                  onClick={() => setSearchRadius(r.value)}
                  className={cn(
                    'p-3 rounded-xl border text-center transition-all',
                    searchRadius === r.value
                      ? 'border-primary bg-primary/10 ring-2 ring-primary/20'
                      : 'border-border bg-card hover:border-primary/50'
                  )}
                >
                  <p className="text-lg font-bold text-foreground">{r.label}</p>
                  <p className="text-[10px] text-muted-foreground">{r.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Rating Filter */}
          <div className="bg-card border border-border rounded-xl p-6">
            <label className="block text-sm font-medium text-foreground mb-4">
              Rating Minimo: {minRating} stelle
            </label>
            <div className="flex items-center gap-2">
              {[0, 3, 3.5, 4, 4.5].map((r) => (
                <button
                  key={r}
                  onClick={() => setMinRating(r)}
                  className={cn(
                    'flex items-center gap-1 px-4 py-2 rounded-lg border transition-all',
                    minRating === r
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  )}
                >
                  <Star className={cn('w-4 h-4', minRating === r ? 'text-primary fill-primary' : 'text-muted-foreground')} />
                  <span className="text-sm">{r === 0 ? 'Tutti' : `${r}+`}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Search Summary */}
          {(selectedSectors.size > 0 && (userLocation || customLocation.trim())) && (
            <div className="bg-primary/5 border border-primary/20 rounded-xl p-4">
              <p className="text-sm text-foreground">
                <span className="font-medium">Ricerca:</span>{' '}
                <span className="text-primary">{selectedSectors.size} settori</span>
                {' entro '}
                <span className="text-primary">{searchRadius}km</span>
                {' da '}
                <span className="text-primary">{userLocation?.city || customLocation}</span>
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              onClick={handleSearch}
              disabled={selectedSectors.size === 0 || (!userLocation && !customLocation.trim()) || isSearching}
              className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white"
              size="lg"
            >
              {isSearching ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Ricerca in corso...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5 mr-2" />
                  Cerca Lead ({searchRadius}km)
                </>
              )}
            </Button>

            <Button
              onClick={handleAutoPilot}
              disabled={selectedSectors.size === 0 || (!userLocation && !customLocation.trim()) || autoPilotRunning}
              variant="outline"
              size="lg"
              className="flex-1"
            >
              {autoPilotRunning ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Auto-Pilot...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 mr-2" />
                  🤖 Auto-Pilot Multi-Zona
                </>
              )}
            </Button>
          </div>
        </motion.div>
      )}

      {/* STEP 2: SELECT */}
      {step === 'select' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" onClick={() => setStep('search')}>
                <ArrowLeft className="w-4 h-4 mr-1" />
                Indietro
              </Button>
              <span className="text-sm text-muted-foreground">
                {leads.length} lead trovati • {selectedLeads.size} selezionati
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={selectAll}>
                {selectedLeads.size === leads.length ? 'Deseleziona tutti' : 'Seleziona tutti'}
              </Button>
              <Button
                onClick={handleEnrichSelected}
                disabled={selectedLeads.size === 0 || isEnriching}
                size="sm"
              >
                {isEnriching ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    {enrichProgress}%
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-1" />
                    Arricchisci
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Lead List */}
          <div className="space-y-3">
            {leads.map((lead) => (
              <div
                key={lead.place_id}
                className={cn(
                  'p-4 rounded-xl border transition-all cursor-pointer',
                  selectedLeads.has(lead.place_id)
                    ? 'border-primary bg-primary/5'
                    : 'border-border bg-card hover:border-primary/50'
                )}
                onClick={() => toggleSelectLead(lead.place_id)}
              >
                <div className="flex items-start gap-4">
                  <div className="pt-1">
                    {selectedLeads.has(lead.place_id) ? (
                      <CheckSquare className="w-5 h-5 text-primary" />
                    ) : (
                      <Square className="w-5 h-5 text-muted-foreground" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h4 className="font-medium text-foreground">{lead.name}</h4>
                        <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
                          <MapPin className="w-3 h-3" />
                          {lead.address}
                        </p>
                      </div>

                      {lead.enrichment_score && (
                        <div className={cn('px-3 py-1 rounded-full text-sm font-bold', getGradeColor(lead.enrichment_score.grade))}>
                          {lead.enrichment_score.grade} • {lead.enrichment_score.score}
                        </div>
                      )}

                      {lead.enriching && (
                        <Loader2 className="w-5 h-5 animate-spin text-primary" />
                      )}
                    </div>

                    <div className="flex items-center gap-4 mt-3 text-sm">
                      {lead.rating && (
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                          {lead.rating}
                        </span>
                      )}
                      {lead.phone && (
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <Phone className="w-4 h-4" />
                          {lead.phone}
                        </span>
                      )}
                      {lead.website && (
                        <a
                          href={lead.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-primary hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Globe className="w-4 h-4" />
                          Website
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <Button
              onClick={handleSaveToCRM}
              disabled={selectedLeads.size === 0 || isSaving}
              className="flex-1"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Salvataggio...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Salva nel CRM ({selectedLeads.size})
                </>
              )}
            </Button>
            <Button
              onClick={() => setStep('action')}
              disabled={selectedLeads.size === 0}
              variant="outline"
              className="flex-1"
            >
              <ArrowRight className="w-4 h-4 mr-2" />
              Continua
            </Button>
          </div>
        </motion.div>
      )}

      {/* STEP 3: ACTION */}
      {step === 'action' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">
              Azione sui Lead
            </h3>
            <p className="text-sm text-muted-foreground">
              {saveResult ? `${saveResult.created} lead salvati` : `${selectedLeads.size} lead selezionati`}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button
              onClick={handleCreateEmailCampaign}
              variant="outline"
              className="h-auto py-6 flex flex-col items-center gap-3"
            >
              <Mail className="w-8 h-8 text-blue-500" />
              <div className="text-center">
                <p className="font-medium">Crea Campagna Email</p>
                <p className="text-xs text-muted-foreground">Invia email automatiche ai lead</p>
              </div>
            </Button>

            <Button
              onClick={() => setStep('stats')}
              variant="outline"
              className="h-auto py-6 flex flex-col items-center gap-3"
            >
              <BarChart3 className="w-8 h-8 text-purple-500" />
              <div className="text-center">
                <p className="font-medium">Vedi Statistiche</p>
                <p className="text-xs text-muted-foreground">Analizza conversioni e performance</p>
              </div>
            </Button>
          </div>

          <Button
            onClick={() => { setStep('search'); setLeads([]); setSelectedLeads(new Set()); }}
            variant="ghost"
            className="w-full"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Nuova Ricerca
          </Button>
        </motion.div>
      )}

      {/* STEP 4: STATS */}
      {step === 'stats' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {isLoadingStats ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : stats ? (
            <>
              {/* KPI Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-card border border-border rounded-xl p-4">
                  <p className="text-sm text-muted-foreground">Lead Trovati</p>
                  <p className="text-2xl font-bold text-foreground">{stats.total_found}</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-4">
                  <p className="text-sm text-muted-foreground">Salvati CRM</p>
                  <p className="text-2xl font-bold text-blue-500">{stats.saved_to_crm}</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-4">
                  <p className="text-sm text-muted-foreground">Convertiti</p>
                  <p className="text-2xl font-bold text-green-500">{stats.converted_to_customer}</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-4">
                  <p className="text-sm text-muted-foreground">Tasso Conversione</p>
                  <p className="text-2xl font-bold text-primary">{stats.conversion_rate.toFixed(1)}%</p>
                </div>
              </div>

              {/* Recent Leads */}
              {stats.recent_leads && stats.recent_leads.length > 0 && (
                <div className="bg-card border border-border rounded-xl p-6">
                  <h4 className="font-medium text-foreground mb-4">Lead Recenti</h4>
                  <div className="space-y-3">
                    {stats.recent_leads.slice(0, 5).map((lead) => (
                      <div key={lead.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                        <div>
                          <p className="font-medium text-foreground">{lead.company}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(lead.created_at).toLocaleDateString('it-IT')}
                          </p>
                        </div>
                        <span className={cn(
                          'px-2 py-1 rounded text-xs',
                          lead.status === 'converted' ? 'bg-green-500/10 text-green-500' :
                            lead.status === 'rejected' ? 'bg-red-500/10 text-red-500' :
                              'bg-muted text-muted-foreground'
                        )}>
                          {lead.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">Nessuna statistica disponibile</p>
            </div>
          )}

          <Button
            onClick={() => { setStep('search'); setLeads([]); setSelectedLeads(new Set()); }}
            className="w-full"
          >
            <Search className="w-4 h-4 mr-2" />
            Nuova Ricerca
          </Button>
        </motion.div>
      )}
    </div>
  );
}

export default LeadFinderInline;
