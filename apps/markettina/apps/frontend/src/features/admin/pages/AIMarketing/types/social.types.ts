/**
 * Types per Social Publisher centralizzati
 * @module types/social
 */

import type { LucideIcon } from 'lucide-react';

export interface SocialPlatform {
  id: string;
  label: string;
  icon: LucideIcon;
  color: string;
  bgColor: string;
  configured: boolean;
  maxChars: number;
  features: string[];
}

export interface ScheduledPost {
  id: string;
  content: string;
  platforms: string[];
  scheduledTime: Date;
  status: 'pending' | 'published' | 'failed';
  mediaUrls?: string[];
  hashtags?: string[];
}

export interface PublishResult {
  platform: string;
  success: boolean;
  postId?: string;
  postUrl?: string;
  error?: string;
}

export interface GeneratedImage {
  platform: string;
  url: string;
  aspectRatio: string;
  success: boolean;
}

export interface MultiPlatformPostRequest {
  content: string;
  cta?: string;
  hashtags: string[];
  platforms: string[];
  base_image_prompt: string;
  publish_immediately: boolean;
  schedule_time?: string;
  image_style?: string;
  image_provider?: string;
}

export interface MultiPlatformPostResult {
  status: 'published' | 'scheduled' | 'partial' | 'failed';
  total_platforms: number;
  successful: number;
  platforms: {
    platform: string;
    success: boolean;
    post_url?: string;
    image_url?: string;
    error?: string;
  }[];
}

export interface SocialApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
