/**
 * 🚀 POWER CONTENT FORMATS - Sistema Formato Contenuto Avanzato
 *
 * Definisce i formati di contenuto disponibili:
 * - POST: Standard social post
 * - STORY: Multi-slide ephemeral content (IG/FB Stories)
 * - CAROUSEL: Swipeable educational content
 * - REEL: Short-form video (15-90 sec)
 * - VIDEO: Long-form video script
 *
 * @module constants/content-formats
 */

import {
  FileText,
  Film,
  Layers,
  Play,
  Video,
  type LucideIcon,
} from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export type ContentFormatType = 'post' | 'story' | 'carousel' | 'reel' | 'video';

export interface ContentFormat {
  id: ContentFormatType;
  label: string;
  icon: LucideIcon;
  description: string;
  color: string;
  platforms: string[];
  defaultSlides?: number;
  defaultDuration?: number;
  features: string[];
}

export interface SlideContent {
  slide_num: number;
  slide_type: string;
  title: string;
  content: string;
  bullets: string[];
  visual_prompt: string | null;
  text_overlay: string | null;
  duration_seconds: number | null;
  stickers: string[];
  music_mood: string | null;
  transition: string | null;
}

export interface FormatGenerationResult {
  content_format: string;
  main_content: string;
  caption: string;
  slides: SlideContent[];
  scenes: SlideContent[];
  hashtags: string[];
  cta_options: string[];
  cover_image_prompt: string | null;
  metadata: {
    content_format: string;
    post_type: string;
    platform: string;
    sector: string;
    num_slides: number;
    num_scenes: number;
    duration_seconds: number | null;
    agent: string;
    model: string;
  };
  provider: string;
}

// ============================================================================
// CONTENT FORMATS DEFINITION
// ============================================================================

export const CONTENT_FORMATS: Record<ContentFormatType, ContentFormat> = {
  post: {
    id: 'post',
    label: '📝 Post',
    icon: FileText,
    description: 'Post standard per feed',
    color: '#3B82F6', // Blue
    platforms: ['instagram', 'facebook', 'linkedin', 'twitter', 'threads'],
    features: [
      'Testo ottimizzato per piattaforma',
      'Hashtag automatici',
      'Prompt immagine AI',
      'Formattazione Brand DNA',
    ],
  },
  story: {
    id: 'story',
    label: '📱 Story',
    icon: Play,
    description: 'Multi-slide per Stories',
    color: '#EC4899', // Pink
    platforms: ['instagram', 'facebook'],
    defaultSlides: 5,
    features: [
      'Struttura HOOK → CONTENT → CTA',
      'Prompt immagine per ogni slide',
      'Suggerimenti sticker',
      'Mood musicale',
      'Transizioni consigliate',
    ],
  },
  carousel: {
    id: 'carousel',
    label: '🎠 Carousel',
    icon: Layers,
    description: 'Contenuto educativo swipeable',
    color: '#8B5CF6', // Purple
    platforms: ['instagram', 'linkedin'],
    defaultSlides: 7,
    features: [
      'Struttura COVER → CONTENT → RECAP → CTA',
      'Ogni slide con prompt immagine',
      'Caption coinvolgente',
      'Perfetto per tips & guide',
      'Alto tasso di salvataggio',
    ],
  },
  reel: {
    id: 'reel',
    label: '🎬 Reel',
    icon: Film,
    description: 'Video breve (15-90 sec)',
    color: '#EF4444', // Red
    platforms: ['instagram', 'tiktok', 'youtube'],
    defaultDuration: 30,
    features: [
      'Script con timing preciso',
      'Scene breakdown',
      'Prompt thumbnail',
      'Suggerimenti audio',
      'Caption virale',
    ],
  },
  video: {
    id: 'video',
    label: '🎥 Video',
    icon: Video,
    description: 'Video lungo (2-30 min)',
    color: '#10B981', // Green
    platforms: ['youtube', 'linkedin', 'facebook'],
    defaultDuration: 300,
    features: [
      'Script professionale',
      'Sezioni con timestamp',
      'B-roll suggestions',
      'Prompt thumbnail',
      'Descrizione SEO',
    ],
  },
};

// ============================================================================
// CONTENT FORMAT ARRAY
// ============================================================================

export const CONTENT_FORMATS_LIST: ContentFormat[] = Object.values(CONTENT_FORMATS);

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get format by ID
 */
export function getContentFormat(id: ContentFormatType): ContentFormat | undefined {
  return CONTENT_FORMATS[id];
}

/**
 * Get formats available for a platform
 */
export function getFormatsForPlatform(platform: string): ContentFormat[] {
  return CONTENT_FORMATS_LIST.filter((f) => f.platforms.includes(platform));
}

/**
 * Check if format supports slides
 */
export function formatHasSlides(format: ContentFormatType): boolean {
  return format === 'story' || format === 'carousel';
}

/**
 * Check if format supports scenes (video)
 */
export function formatHasScenes(format: ContentFormatType): boolean {
  return format === 'reel' || format === 'video';
}

/**
 * Get default settings for format
 */
export function getFormatDefaults(format: ContentFormatType): {
  slides?: number;
  duration?: number;
} {
  const f = CONTENT_FORMATS[format];
  return {
    slides: f.defaultSlides,
    duration: f.defaultDuration,
  };
}

// ============================================================================
// CONTENT SUBTYPES (Legacy support)
// ============================================================================

export interface ContentSubtype {
  id: string;
  label: string;
  category: 'social' | 'video' | 'email' | 'blog';
  description: string;
  icon: LucideIcon;
}

export const CONTENT_SUBTYPES: Record<string, ContentSubtype> = {
  post: {
    id: 'post',
    label: 'Post',
    category: 'social',
    description: 'Post standard per feed',
    icon: FileText,
  },
  story: {
    id: 'story',
    label: 'Story',
    category: 'social',
    description: 'Contenuto effimero multi-slide',
    icon: Play,
  },
  carousel: {
    id: 'carousel',
    label: 'Carousel',
    category: 'social',
    description: 'Carousel educativo swipeable',
    icon: Layers,
  },
  reel: {
    id: 'reel',
    label: 'Reel',
    category: 'video',
    description: 'Video breve 15-90 secondi',
    icon: Film,
  },
  video: {
    id: 'video',
    label: 'Video',
    category: 'video',
    description: 'Video lungo con script',
    icon: Video,
  },
};

/**
 * Get subtypes by category
 */
export function getSubtypesByCategory(category: ContentSubtype['category']): ContentSubtype[] {
  return Object.values(CONTENT_SUBTYPES).filter((s) => s.category === category);
}

/**
 * Generate prompt from subtype
 */
export function generatePromptFromSubtype(
  subtypeId: string,
  context: {
    platform?: string;
    tone?: string;
    brand_context?: string;
    topic?: string;
  }
): string {
  const subtype = CONTENT_SUBTYPES[subtypeId];
  if (!subtype) return '';

  return `
Genera un ${subtype.label} per ${context.platform || 'social media'}.
Tono: ${context.tone || 'professionale'}
Argomento: ${context.topic || ''}
${context.brand_context || ''}
  `.trim();
}

// ============================================================================
// SLIDER DURATION OPTIONS
// ============================================================================

export const DURATION_OPTIONS = [
  { value: 15, label: '15 sec', description: 'Ultra-short hook' },
  { value: 30, label: '30 sec', description: 'Reel standard' },
  { value: 60, label: '60 sec', description: 'Reel extended' },
  { value: 90, label: '90 sec', description: 'Max Reel IG' },
  { value: 180, label: '3 min', description: 'TikTok extended' },
  { value: 300, label: '5 min', description: 'Short video' },
  { value: 600, label: '10 min', description: 'Tutorial' },
  { value: 900, label: '15 min', description: 'Deep dive' },
];

export const SLIDES_OPTIONS = [
  { value: 3, label: '3 slide', description: 'Quick tip' },
  { value: 5, label: '5 slide', description: 'Story standard' },
  { value: 7, label: '7 slide', description: 'Carousel completo' },
  { value: 10, label: '10 slide', description: 'Guida dettagliata' },
];

// ============================================================================
// VIDEO STYLES
// ============================================================================

export const VIDEO_STYLES = [
  { id: 'educational', label: '📚 Educativo', description: 'Tutorial e how-to' },
  { id: 'promotional', label: '🎯 Promozionale', description: 'Lancio prodotto/servizio' },
  { id: 'entertaining', label: '🎭 Intrattenimento', description: 'Trend e meme' },
  { id: 'tutorial', label: '🛠️ Tutorial', description: 'Step-by-step dettagliato' },
  { id: 'testimonial', label: '⭐ Testimonial', description: 'Case study e recensioni' },
];

export const MUSIC_MOODS = [
  { id: 'upbeat', label: '🎵 Upbeat', description: 'Energico e positivo' },
  { id: 'chill', label: '🎶 Chill', description: 'Rilassato e calmo' },
  { id: 'dramatic', label: '🎬 Dramatic', description: 'Tensione e impatto' },
  { id: 'trending', label: '🔥 Trending', description: 'Sound virali del momento' },
  { id: 'corporate', label: '💼 Corporate', description: 'Professionale e neutro' },
];
