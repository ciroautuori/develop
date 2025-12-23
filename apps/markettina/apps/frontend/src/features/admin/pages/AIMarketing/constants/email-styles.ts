/**
 * Stili email centralizzati per Marketing Hub
 * @module constants/email-styles
 */

export interface EmailStyleConfig {
  id: string;
  label: string;
  emoji: string;
  description?: string;
}

export const EMAIL_STYLES: EmailStyleConfig[] = [
  { id: 'professional', label: 'Professionale', emoji: '💼', description: 'Tono formale e business' },
  { id: 'friendly', label: 'Amichevole', emoji: '😊', description: 'Tono caldo e personale' },
  { id: 'promotional', label: 'Promozionale', emoji: '🎯', description: 'Focus su offerte e CTA' },
  { id: 'newsletter', label: 'Newsletter', emoji: '📰', description: 'Formato informativo' },
  { id: 'announcement', label: 'Annuncio', emoji: '📢', description: 'News e comunicazioni' },
  { id: 'casual', label: 'Informale', emoji: '👋', description: 'Tono leggero e diretto' },
] as const;

export const EMAIL_TONES = ['professional', 'friendly', 'casual'] as const;

export const EMAIL_LANGUAGES = [
  { code: 'it', label: 'Italiano' },
  { code: 'en', label: 'English' },
  { code: 'es', label: 'Español' },
  { code: 'fr', label: 'Français' },
  { code: 'de', label: 'Deutsch' },
] as const;

export type EmailStyleId = typeof EMAIL_STYLES[number]['id'];
export type EmailTone = typeof EMAIL_TONES[number];
export type EmailLanguageCode = typeof EMAIL_LANGUAGES[number]['code'];
