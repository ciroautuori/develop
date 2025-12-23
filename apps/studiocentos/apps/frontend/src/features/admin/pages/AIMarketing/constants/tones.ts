/**
 * TONES - Configurazioni centralizzate per i toni di voce
 *
 * Single Source of Truth per:
 * - ContentStudio
 * - ContentGenerator
 * - EmailCampaignPro (usa EMAIL_TONES)
 *
 * @module constants/tones
 */

// ============================================================================
// TYPES
// ============================================================================

export interface Tone {
  id: string;
  label: string;
  description?: string;
}

export interface TonePrompt {
  textStyle: string;
  visualMood: string;
}

// ============================================================================
// SOCIAL TONES - For social media content
// ============================================================================

export const SOCIAL_TONES: Tone[] = [
  { id: 'professional', label: '💼 Professionale', description: 'Business-oriented, authoritative' },
  { id: 'friendly', label: '😊 Amichevole', description: 'Warm, conversational' },
  { id: 'persuasive', label: '🎯 Persuasivo', description: 'Action-oriented, compelling' },
  { id: 'educational', label: '📚 Educativo', description: 'Informative, expert positioning' },
  { id: 'inspiring', label: '✨ Ispirante', description: 'Motivational, uplifting' },
  { id: 'humorous', label: '😄 Umoristico', description: 'Witty, memorable' },
];

// ============================================================================
// EMAIL TONES EXPANDED - Full config for email campaigns
// NOTE: Simple EMAIL_TONES array is exported from email-styles.ts
// ============================================================================

export const EMAIL_TONES_EXPANDED: Tone[] = [
  { id: 'professional', label: '💼 Professionale', description: 'Formal business communication' },
  { id: 'friendly', label: '😊 Amichevole', description: 'Personal, warm approach' },
  { id: 'persuasive', label: '🎯 Persuasivo', description: 'Sales-focused, compelling' },
  { id: 'educational', label: '📚 Educativo', description: 'Informative, value-driven' },
  { id: 'urgent', label: '⚡ Urgente', description: 'Time-sensitive, action required' },
];

// ============================================================================
// TONE PROMPTS - AI prompt instructions per tone
// ============================================================================

export const TONE_PROMPTS: Record<string, TonePrompt> = {
  'professional': {
    textStyle: 'Tono PROFESSIONALE e autorevole. Linguaggio formale ma accessibile. Credibilità e competenza.',
    visualMood: 'corporate professional, clean lines, sophisticated, trustworthy, business aesthetic'
  },
  'friendly': {
    textStyle: 'Tono AMICHEVOLE e conversazionale. Come un amico esperto che consiglia. Emoji moderate, linguaggio semplice.',
    visualMood: 'warm and friendly, approachable, soft colors, welcoming, human connection'
  },
  'persuasive': {
    textStyle: 'Tono PERSUASIVO e orientato all\'azione. Urgenza, benefici, obiezioni anticipate. Copy da venditore esperto.',
    visualMood: 'bold and impactful, attention-grabbing, dynamic composition, action-oriented'
  },
  'educational': {
    textStyle: 'Tono EDUCATIVO e informativo. Spiega concetti, usa esempi, condividi valore. Posizionamento come esperto.',
    visualMood: 'educational and informative, infographic style, clear hierarchy, knowledge-sharing'
  },
  'inspiring': {
    textStyle: 'Tono ISPIRANTE e motivazionale. Visione, possibilità, trasformazione. Emotivo ma non sdolcinato.',
    visualMood: 'inspirational and uplifting, sunrise/light imagery, aspirational, motivating'
  },
  'humorous': {
    textStyle: 'Tono UMORISTICO e leggero. Battute intelligenti, meme-style, autoironia professionale. Memorabile.',
    visualMood: 'playful and fun, bright colors, quirky elements, memorable and shareable'
  },
  'urgent': {
    textStyle: 'Tono URGENTE e diretto. Enfasi sulla scadenza, azione immediata richiesta. Chiaro e conciso.',
    visualMood: 'urgent and impactful, red accents, countdown feel, action-required'
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get tone by ID
 */
export function getToneById(id: string, type: 'social' | 'email' = 'social'): Tone | undefined {
  const tones = type === 'email' ? EMAIL_TONES_EXPANDED : SOCIAL_TONES;
  return tones.find(t => t.id === id);
}

/**
 * Get tone prompt by ID
 */
export function getTonePrompt(id: string): TonePrompt {
  return TONE_PROMPTS[id] || TONE_PROMPTS['professional'];
}

// ============================================================================
// DEFAULT EXPORTS
// ============================================================================

// Backward compatibility - default to SOCIAL_TONES
export const TONES = SOCIAL_TONES;
