/**
 * Video Generation Types
 * Matches backend: /apps/ai_microservice/app/core/api/v1/marketing.py:679
 */

export interface VideoGenerationRequest {
  prompt: string;
  duration?: number; // 1-60 seconds, default 8
  aspect_ratio?: '9:16' | '16:9' | '1:1';
  platform?: 'instagram' | 'tiktok' | 'facebook' | 'youtube' | 'linkedin';
  style?: string;
  input_image?: string;
  use_google_search?: boolean;
}

export interface VideoGenerationResponse {
  video_url: string;
  thumbnail_url: string;
  prompt_used: string;
  generation_time: number;
  metadata: Record<string, unknown>;
}

export const PLATFORM_SPECS = {
  instagram: {
    label: 'Instagram Reels/Stories',
    icon: '📸',
    aspectRatio: '9:16' as const,
    durationOptimal: 15,
    description: 'Vertical, trendy, mobile-first'
  },
  tiktok: {
    label: 'TikTok',
    icon: '🎵',
    aspectRatio: '9:16' as const,
    durationOptimal: 15,
    description: 'Dynamic, fast-paced, viral-worthy'
  },
  facebook: {
    label: 'Facebook',
    icon: '👍',
    aspectRatio: '16:9' as const,
    durationOptimal: 30,
    description: 'Engaging, shareable, landscape'
  },
  youtube: {
    label: 'YouTube',
    icon: '▶️',
    aspectRatio: '16:9' as const,
    durationOptimal: 60,
    description: 'Cinematic, storytelling, high-production'
  },
  linkedin: {
    label: 'LinkedIn',
    icon: '💼',
    aspectRatio: '1:1' as const,
    durationOptimal: 30,
    description: 'Professional, business-focused'
  }
} as const;

export const VIDEO_STYLES = [
  'professional',
  'modern',
  'cinematic',
  'minimalist',
  'dynamic',
  'vintage',
  'futuristic',
  'elegant'
] as const;
