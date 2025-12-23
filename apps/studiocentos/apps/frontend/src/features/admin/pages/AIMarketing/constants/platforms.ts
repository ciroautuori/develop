/**
 * PLATFORMS - Configurazioni centralizzate per tutte le piattaforme social
 *
 * Single Source of Truth per:
 * - ContentStudio
 * - ContentGenerator
 * - CalendarManager
 * - EditorialCalendar
 * - VideoStoryCreator
 *
 * @module constants/platforms
 */

import {
  Instagram,
  Facebook,
  Linkedin,
  Twitter,
  Youtube,
  Video,
  MessageCircle
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface Platform {
  id: string;
  name: string;
  icon: LucideIcon;
  color: string;
  width: number;
  height: number;
  aspectRatio: string;
  maxChars: number;
  features: ContentType[];
}

export type ContentType = 'post' | 'video' | 'story' | 'email' | 'carousel';

// ============================================================================
// SOCIAL PLATFORMS - Complete Configuration
// ============================================================================

export const SOCIAL_PLATFORMS: Platform[] = [
  {
    id: 'instagram',
    name: 'Instagram',
    icon: Instagram,
    color: '#E4405F',
    width: 1080,
    height: 1080,
    aspectRatio: '1:1',
    maxChars: 2200,
    features: ['post', 'story', 'video', 'carousel']
  },
  {
    id: 'facebook',
    name: 'Facebook',
    icon: Facebook,
    color: '#1877F2',
    width: 1200,
    height: 630,
    aspectRatio: '1.91:1',
    maxChars: 63206,
    features: ['post', 'story', 'video', 'carousel']
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: Linkedin,
    color: '#0A66C2',
    width: 1200,
    height: 627,
    aspectRatio: '1.91:1',
    maxChars: 3000,
    features: ['post', 'video', 'carousel']
  },
  {
    id: 'twitter',
    name: 'X (Twitter)',
    icon: Twitter,
    color: '#000000',
    width: 1600,
    height: 900,
    aspectRatio: '16:9',
    maxChars: 280,
    features: ['post', 'video']
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: Video,
    color: '#000000',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    maxChars: 2200,
    features: ['video', 'story']
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: Youtube,
    color: '#FF0000',
    width: 1920,
    height: 1080,
    aspectRatio: '16:9',
    maxChars: 5000,
    features: ['video']
  },
  {
    id: 'threads',
    name: 'Threads',
    icon: MessageCircle,
    color: '#000000',
    width: 1440,
    height: 1920,
    aspectRatio: '3:4',
    maxChars: 500,
    features: ['post', 'carousel']
  },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get platform by ID
 */
export function getPlatformById(id: string): Platform | undefined {
  return SOCIAL_PLATFORMS.find(p => p.id === id);
}

/**
 * Get platforms that support a specific content type
 */
export function getPlatformsByContentType(contentType: ContentType): Platform[] {
  return SOCIAL_PLATFORMS.filter(p => p.features.includes(contentType));
}

/**
 * Get platform IDs for a content type
 */
export function getPlatformIdsForContentType(contentType: ContentType): string[] {
  return getPlatformsByContentType(contentType).map(p => p.id);
}

/**
 * Simple platform list for dropdowns (id/label only)
 */
export const PLATFORM_OPTIONS = SOCIAL_PLATFORMS.map(p => ({
  id: p.id,
  label: p.name,
  color: p.color,
}));

// ============================================================================
// VIDEO PLATFORMS (already in video-platforms.ts, re-export for convenience)
// ============================================================================

export { VIDEO_PLATFORMS } from './video-platforms';
