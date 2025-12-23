/**
 * HeyGen API Types
 * Integration for AI Avatar Video Generation
 */

// ===== AVATAR TYPES =====
export interface HeyGenAvatar {
  avatar_id: string;
  avatar_name: string;
  gender: 'male' | 'female' | 'other';
  preview_image_url: string;
  preview_video_url?: string;
  type: 'public' | 'private' | 'instant';
}

export interface HeyGenAvatarGroup {
  group_id: string;
  group_name: string;
  avatars: HeyGenAvatar[];
}

// ===== VOICE TYPES =====
export interface HeyGenVoice {
  voice_id: string;
  name: string;
  language: string;
  gender: 'male' | 'female';
  preview_audio?: string;
  support_pause: boolean;
  emotion_support: boolean;
}

// ===== VIDEO GENERATION =====
export interface HeyGenVideoClip {
  avatar_id?: string;
  avatar_style?: 'normal' | 'circle' | 'closeUp';
  input_text: string;
  voice_id: string;
  scale?: number;
  offset?: { x: number; y: number };
  voice_settings?: {
    speed?: number; // 0.5 - 2.0
    pitch?: number; // -50 to 50
  };
}

export interface HeyGenVideoRequest {
  video_inputs: Array<{
    character: {
      type: 'avatar' | 'talking_photo';
      avatar_id?: string;
      avatar_style?: 'normal' | 'circle' | 'closeUp';
      scale?: number;
      offset?: { x: number; y: number };
    };
    voice: {
      type: 'text' | 'audio';
      input_text?: string;
      voice_id?: string;
      speed?: number;
      pitch?: number;
    };
    background?: {
      type: 'color' | 'image' | 'video';
      value?: string;
      url?: string;
    };
  }>;
  dimension?: {
    width: number;
    height: number;
  };
  aspect_ratio?: '16:9' | '9:16' | '1:1';
  callback_id?: string;
  title?: string;
}

export interface HeyGenVideoResponse {
  error: null | string;
  data: {
    video_id: string;
  };
}

// ===== VIDEO STATUS =====
export type HeyGenVideoStatus = 'pending' | 'waiting' | 'processing' | 'completed' | 'failed';

export interface HeyGenVideoStatusResponse {
  error: null | string;
  data: {
    video_id: string;
    status: HeyGenVideoStatus;
    video_url?: string;
    video_url_caption?: string;
    thumbnail_url?: string;
    duration?: number;
    gif_url?: string;
    created_at?: number;
    callback_id?: string;
    error?: string;
  };
}

// ===== QUOTA =====
export interface HeyGenQuotaResponse {
  error: null | string;
  data: {
    remaining_quota: number;
    used_quota: number;
  };
}

// ===== FRONTEND FORM =====
export interface StoryGeneratorFormData {
  title: string;
  script: string;
  avatar_id: string;
  voice_id: string;
  platform: 'instagram_story' | 'tiktok' | 'linkedin' | 'youtube_shorts' | 'facebook_story';
  background_type: 'color' | 'image' | 'gradient';
  background_value: string;
  voice_speed: number;
  voice_pitch: number;
  avatar_style: 'normal' | 'circle' | 'closeUp';
}

export const DEFAULT_STORY_VALUES: StoryGeneratorFormData = {
  title: '',
  script: '',
  avatar_id: '',
  voice_id: '',
  platform: 'instagram_story',
  background_type: 'color',
  background_value: '#0a0a0a',
  voice_speed: 1.0,
  voice_pitch: 0,
  avatar_style: 'normal',
};

// Platform dimensions
export const PLATFORM_DIMENSIONS: Record<string, { width: number; height: number; label: string }> = {
  instagram_story: { width: 1080, height: 1920, label: 'Instagram Story (9:16)' },
  tiktok: { width: 1080, height: 1920, label: 'TikTok (9:16)' },
  youtube_shorts: { width: 1080, height: 1920, label: 'YouTube Shorts (9:16)' },
  facebook_story: { width: 1080, height: 1920, label: 'Facebook Story (9:16)' },
  linkedin: { width: 1920, height: 1080, label: 'LinkedIn (16:9)' },
};

// ===== GENERATED VIDEO =====
export interface GeneratedStory {
  id: string;
  video_id: string;
  title: string;
  platform: string;
  status: HeyGenVideoStatus;
  video_url?: string;
  thumbnail_url?: string;
  duration?: number;
  created_at: Date;
  script: string;
}
