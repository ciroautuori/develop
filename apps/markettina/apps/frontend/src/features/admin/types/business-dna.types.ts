/**
 * Business DNA Generator Types
 * Matches backend: /apps/ai_microservice/app/core/api/v1/marketing.py:1413
 */

export interface BusinessDNARequest {
  company_name: string;
  tagline: string;
  business_overview: string;
  website?: string;
  fonts?: string[];
  colors?: {
    primary: string;
    secondary: string;
    accent: string;
  };
  brand_attributes?: string[];
  tone_of_voice?: string[];
}

export interface BusinessDNAFormData {
  company_name: string;
  tagline: string;
  business_overview: string;
  website: string;
  fonts: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  brand_attributes: string;
  tone_of_voice: string;
}

export const DEFAULT_DNA_VALUES: BusinessDNAFormData = {
  company_name: '',
  tagline: '',
  business_overview: '',
  website: '',
  fonts: 'Basecold, Montserrat',
  primary_color: '#D4AF37',
  secondary_color: '#0A0A0A',
  accent_color: '#FAFAFA',
  brand_attributes: 'Professional, Modern',
  tone_of_voice: 'Confident, Authentic'
};


// ============================================================================
// BRAND SETTINGS (Persistence) Types
// Matches backend: /apps/backend/app/domain/marketing/schemas.py
// ============================================================================

export type ToneOfVoice =
  | 'professional'
  | 'casual'
  | 'enthusiastic'
  | 'formal'
  | 'friendly'
  | 'authoritative';

export interface BrandSettings {
  id: number;
  admin_id: number;

  // Logo & Visual
  logo_url: string | null;
  favicon_url: string | null;

  // Colors
  primary_color: string;
  secondary_color: string;
  accent_color: string | null;

  // Company Info
  company_name: string | null;
  tagline: string | null;
  description: string | null;

  // Voice & Tone
  tone_of_voice: ToneOfVoice;

  // Target & Positioning
  target_audience: string | null;
  unique_value_proposition: string | null;

  // Structured Data
  keywords: string[];
  values: string[];
  competitors: string[];
  content_pillars: string[];

  // Social
  social_handles: Record<string, string>;

  // AI Configuration
  ai_persona: string | null;
  forbidden_words: string[];
  preferred_hashtags: string[];

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface BrandSettingsCreate {
  logo_url?: string | null;
  favicon_url?: string | null;

  primary_color?: string;
  secondary_color?: string;
  accent_color?: string | null;

  company_name?: string | null;
  tagline?: string | null;
  description?: string | null;

  tone_of_voice?: ToneOfVoice;

  target_audience?: string | null;
  unique_value_proposition?: string | null;

  keywords?: string[];
  values?: string[];
  competitors?: string[];
  content_pillars?: string[];

  social_handles?: Record<string, string>;

  ai_persona?: string | null;
  forbidden_words?: string[];
  preferred_hashtags?: string[];
}

export const DEFAULT_BRAND_SETTINGS: Omit<BrandSettings, 'id' | 'admin_id' | 'created_at' | 'updated_at'> = {
  logo_url: null,
  favicon_url: null,
  primary_color: '#D4AF37',
  secondary_color: '#0A0A0A',
  accent_color: '#FAFAFA',
  company_name: null,
  tagline: null,
  description: null,
  tone_of_voice: 'professional',
  target_audience: null,
  unique_value_proposition: null,
  keywords: [],
  values: [],
  competitors: [],
  content_pillars: [],
  social_handles: {},
  ai_persona: null,
  forbidden_words: [],
  preferred_hashtags: []
};

export const TONE_OF_VOICE_OPTIONS: { value: ToneOfVoice; label: string }[] = [
  { value: 'professional', label: 'Professionale' },
  { value: 'casual', label: 'Casual' },
  { value: 'enthusiastic', label: 'Entusiasta' },
  { value: 'formal', label: 'Formale' },
  { value: 'friendly', label: 'Amichevole' },
  { value: 'authoritative', label: 'Autorevole' }
];
