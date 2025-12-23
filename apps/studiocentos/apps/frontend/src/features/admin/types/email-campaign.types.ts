/**
 * Email Campaign Types
 * Backend: /apps/backend/app/domain/marketing/schemas.py:170
 */

export interface EmailGenerateRequest {
  campaign_name: string;
  target_region: string;
  target_industry: string;
  tone?: 'professional' | 'friendly' | 'casual';
  language?: 'it' | 'en';
  company_name?: string;
  contact_name?: string;
  brand_context?: string; // Brand DNA context for AI personalization
}

export interface EmailGenerateResponse {
  subject: string;
  html_content: string;
  text_content: string;
  ai_model: string;
}

export const EMAIL_TONES = ['professional', 'friendly', 'casual'] as const;

export const EMAIL_LANGUAGES = [
  { code: 'it', label: 'Italiano' },
  { code: 'en', label: 'English' }
] as const;

export const SAMPLE_INDUSTRIES = [
  'Software & IT',
  'E-commerce',
  'Servizi Professionali',
  'Consulenza',
  'Marketing & Pubblicità',
  'Ristorazione',
  'Turismo & Hospitality',
  'Immobiliare',
  'Salute & Benessere',
  'Formazione',
  'Manifattura',
  'Retail'
];

export const SAMPLE_REGIONS = [
  'Salerno',
  'Napoli',
  'Campania',
  'Lazio',
  'Lombardia',
  'Veneto',
  'Emilia-Romagna',
  'Piemonte',
  'Toscana',
  'Puglia',
  'Sicilia',
  'Italia'
];
