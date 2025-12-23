/**
 * Batch Content Generation Types
 * Backend: /apps/ai_microservice/app/core/api/v1/marketing.py:941
 */

export interface BatchContentRequest {
  topic: string;
  platforms?: string[];
  post_count?: number; // 1-5, default 1
  story_count?: number; // 0-10, default 3
  video_count?: number; // 0-3, default 1
  style?: string;
  use_pro_quality?: boolean;
  mentions?: string[]; // @username tags to include in content
}

export interface BatchContentItem {
  platform: string;
  content_type: 'post' | 'story' | 'video';
  image_url?: string;
  video_url?: string;
  caption: string;
  hashtags: string[];
  aspect_ratio: string;
  metadata: Record<string, unknown>;
}

export interface BatchContentResponse {
  items: BatchContentItem[];
  generation_time: number;
  total_cost_estimate: number;
  metadata: Record<string, unknown>;
}

export const DEFAULT_BATCH_PLATFORMS = ['instagram', 'facebook', 'tiktok', 'linkedin'];

export const BATCH_CONTENT_LIMITS = {
  post_count: { min: 1, max: 5, default: 1 },
  story_count: { min: 0, max: 10, default: 3 },
  video_count: { min: 0, max: 3, default: 1 }
} as const;
