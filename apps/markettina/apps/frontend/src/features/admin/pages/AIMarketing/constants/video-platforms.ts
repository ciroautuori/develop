/**
 * Costanti piattaforme video centralizzate per Marketing Hub
 * @module constants/video-platforms
 */

export interface VideoPlatformConfig {
  label: string;
  width: number;
  height: number;
  ratio: string;
  durationOptimal?: number;
  description?: string;
}

export const VIDEO_PLATFORMS: Record<string, VideoPlatformConfig> = {
  instagram_story: { label: 'Instagram Story', width: 1080, height: 1920, ratio: '9:16', durationOptimal: 15 },
  instagram_reel: { label: 'Instagram Reel', width: 1080, height: 1920, ratio: '9:16', durationOptimal: 30 },
  instagram_post: { label: 'Instagram Post', width: 1080, height: 1080, ratio: '1:1', durationOptimal: 60 },
  tiktok: { label: 'TikTok', width: 1080, height: 1920, ratio: '9:16', durationOptimal: 30 },
  youtube_shorts: { label: 'YouTube Shorts', width: 1080, height: 1920, ratio: '9:16', durationOptimal: 60 },
  youtube: { label: 'YouTube', width: 1920, height: 1080, ratio: '16:9', durationOptimal: 300 },
  linkedin_post: { label: 'LinkedIn Post', width: 1200, height: 1200, ratio: '1:1', durationOptimal: 60 },
  linkedin_video: { label: 'LinkedIn Video', width: 1920, height: 1080, ratio: '16:9', durationOptimal: 120 },
  facebook_story: { label: 'Facebook Story', width: 1080, height: 1920, ratio: '9:16', durationOptimal: 15 },
  facebook_post: { label: 'Facebook Post', width: 1200, height: 630, ratio: '1.91:1', durationOptimal: 60 },
} as const;

export const VIDEO_STYLES = [
  'professional',
  'creative',
  'minimal',
  'bold',
  'elegant',
  'cinematic',
  'documentary',
] as const;

export type VideoPlatformKey = keyof typeof VIDEO_PLATFORMS;
export type VideoStyle = typeof VIDEO_STYLES[number];
