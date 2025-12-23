// API Response Types for ISS Platform

// ========== BANDI SYSTEM TYPES ==========

export type BandoSource =
  | 'comune_salerno'
  | 'regione_campania'
  | 'csv_salerno'
  | 'fondazione_comunita'
  | 'invitalia'
  | 'ministero_lavoro'
  | 'pnrr_italia_domani'
  | 'agenzia_coesione'
  | 'terzo_settore'
  | 'altro';

export type BandoStatus = 'attivo' | 'scaduto' | 'archiviato';

export interface Bando {
  id: number;
  title: string;
  ente: string;
  descrizione?: string;
  link: string;
  fonte: BandoSource;
  status: BandoStatus;
  scadenza?: string; // ISO datetime
  scadenza_raw?: string;
  importo?: string;
  categoria?: string;
  keyword_match?: string;
  hash_identifier: string;
  data_trovato: string; // ISO datetime
  data_aggiornamento?: string; // ISO datetime
  notificato_email: boolean;
  notificato_telegram: boolean;
}

export interface BandoSearchParams {
  query?: string;
  fonte?: BandoSource;
  status?: BandoStatus;
  skip?: number;
  limit?: number;
  sort?: 'created_at' | '-created_at' | 'scadenza' | '-scadenza';
}

export interface BandoSearchResponse {
  items: Bando[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface BandoStats {
  // Campi principali
  totali: number;
  attivi: number;
  scaduti: number;
  in_scadenza: number;
  importo_totale: number;
  importo_medio: number;
  nuovi_settimana: number;
  fonti: Record<string, number>;
  categorie: Record<string, number>;
  trend_mensile: Array<{
    mese: string;
    count: number;
    importo: number;
  }>;
  // Campi legacy per compatibilità
  total_bandi?: number;
  bandi_attivi?: number;
  bandi_scaduti?: number;
  bandi_per_fonte?: Record<string, number>;
  ultimi_trovati?: number;
  media_giornaliera?: number;
}

export interface BandoFilters {
  fonti: Array<{
    value: BandoSource;
    label: string;
    count: number;
  }>;
  status: Array<{
    value: BandoStatus;
    label: string;
    count: number;
  }>;
  keywords_popolari: string[];
}

// ========== AI SEMANTIC SEARCH TYPES ==========

export interface SemanticSearchResult {
  bando: Bando;
  similarity_score: number;
  match_explanation: string;
}

export interface SemanticSearchRequest {
  query: string;
  limit?: number;
  threshold?: number;
}

export interface ProfileMatchRequest {
  organization_type?: string;
  sectors?: string[];
  target_groups?: string[];
  keywords?: string[];
  geographical_area?: string;
  max_amount?: number;
  limit?: number;
}

export interface SuggestionsRequest {
  search_history?: string[];
  current_context?: string;
  limit?: number;
}

// ========== ISS APS ACTIVITIES TYPES ==========

export type CorsoCategoria = 'alfabetizzazione' | 'professionale' | 'assistive' | 'avanzato';
export type CorsoLivello = 'base' | 'intermedio' | 'avanzato';
export type EventoTipo = 'hackathon' | 'workshop' | 'conferenza' | 'laboratorio';
export type ProgettoTipo = 'inclusione' | 'formazione' | 'innovazione' | 'community';
export type ProgettoStatus = 'pianificazione' | 'in_progress' | 'completato' | 'sospeso';
export type VolontariatoArea = 'formazione' | 'eventi' | 'progetti' | 'comunicazione';
export type VolontariatoTipo = 'occasionale' | 'continuativo' | 'progetto_specifico';

export interface Corso {
  id: number;
  titolo: string;
  categoria: CorsoCategoria;
  livello: CorsoLivello;
  descrizione: string;
  data_inizio: string; // ISO datetime
  data_fine: string; // ISO datetime
  durata_ore: number;
  posti_disponibili: number;
  posti_totali: number;
  prezzo: number;
  docente: string;
  sede: string;
  requisiti: string[];
  materiali_inclusi: boolean;
  certificazione: boolean;
  programma_dettagliato?: string;
  competenze_acquisite?: string[];
}

export interface Evento {
  id: number;
  titolo: string;
  tipo: EventoTipo;
  descrizione: string;
  data_evento: string; // ISO datetime
  data_fine: string; // ISO datetime
  luogo: string;
  partecipanti_max: number;
  partecipanti_attuali?: number;
  iscrizioni_aperte: boolean;
  quota_partecipazione: number;
  premi?: Array<{
    posizione: number;
    premio: string;
  }>;
  sponsor?: string[];
  tema?: string;
  agenda_dettagliata?: string;
  speaker?: string[];
  requisiti_partecipazione?: string[];
}

export interface Progetto {
  id: number;
  nome: string;
  tipo: ProgettoTipo;
  descrizione: string;
  obiettivi: string[];
  data_inizio: string; // ISO datetime
  data_fine: string; // ISO datetime
  budget: number;
  partner: string[];
  beneficiari_target: number;
  beneficiari_raggiunti: number;
  status: ProgettoStatus;
  referente: string;
  progress_percentage?: number;
  milestone?: Array<{
    nome: string;
    data_prevista: string;
    completato: boolean;
  }>;
  come_contribuire?: string;
  volontari_necessari?: number;
}

export interface OpportunitaVolontariato {
  id: number;
  titolo: string;
  area: VolontariatoArea;
  tipo: VolontariatoTipo;
  descrizione: string;
  competenze_richieste: string[];
  tempo_richiesto: string;
  sede: string;
  formazione_prevista: boolean;
  contatto: string;
  scadenza_candidatura?: string; // ISO datetime
  posti_disponibili?: number;
  benefici?: string[];
}

// ========== SEARCH & FILTERING ==========

export interface ISSSearchParams {
  query?: string;
  categoria?: CorsoCategoria | EventoTipo | ProgettoTipo | VolontariatoArea;
  tipo?: string;
  data_da?: string;
  data_a?: string;
  skip?: number;
  limit?: number;
}

export interface ISSSearchResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages?: number;
  filters?: Record<string, any>;
}

// ========== STATS & ANALYTICS ==========

export interface ISSStats {
  studenti_formati: number;
  corsi_completati: number;
  eventi_organizzati: number;
  progetti_attivi: number;
  volontari_attivi: number;
  ore_formazione_erogate: number;
  partner_collaborazioni: number;
  impatto_sociale: {
    persone_raggiunte: number;
    competenze_certificate: number;
    progetti_finanziati: number;
  };
  trends: {
    iscrizioni_mensili: Array<{
      mese: string;
      iscrizioni: number;
    }>;
    corsi_per_categoria: Record<CorsoCategoria, number>;
    eventi_per_tipo: Record<EventoTipo, number>;
  };
}

// ========== USER & AUTH ==========

export type UserRole = 'cittadino' | 'aps_esterno' | 'volontario' | 'admin';

export interface User {
  id: number;
  email: string;
  nome: string;
  cognome: string;
  role: UserRole;
  organizzazione?: string; // For APS external users
  competenze?: string[];
  interessi?: string[];
  created_at: string;
  last_login?: string;
  profile_completed: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// ========== API ERROR HANDLING ==========

export interface APIError {
  detail: string | Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
  status_code?: number;
}

// ========== UTILITY TYPES ==========

export interface PaginationInfo {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface SelectOption {
  value: string;
  label: string;
  count?: number;
  disabled?: boolean;
}

export interface NotificationSettings {
  bandi_keywords: string[];
  bandi_fonti: BandoSource[];
  corsi_categorie: CorsoCategoria[];
  eventi_tipi: EventoTipo[];
  frequency: 'immediate' | 'daily' | 'weekly';
  channels: Array<'email' | 'telegram' | 'push'>;
}
