/**
 * HeyGen API Service
 * Integration for AI Avatar Video Generation
 *
 * API Reference: https://docs.heygen.com/reference
 */

import type {
  HeyGenAvatar,
  HeyGenVoice,
  HeyGenVideoRequest,
  HeyGenVideoResponse,
  HeyGenVideoStatusResponse,
  HeyGenQuotaResponse,
  StoryGeneratorFormData,
  PLATFORM_DIMENSIONS,
} from '../types/heygen.types';
import { STORAGE_KEYS } from '../../../shared/config/constants';

const BASE_URL = '/api/v1';

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string {
  const token = localStorage.getItem(STORAGE_KEYS.adminToken);
  if (!token) {
    console.warn('[HeyGenAPI] No access token found');
  }
  return token || '';
}

/**
 * HeyGen API Service
 * Proxies requests through our backend for security (API key stored server-side)
 */
export class HeyGenApiService {

  // ========== AVATARS ==========

  /**
   * Get list of available avatars
   */
  static async listAvatars(): Promise<HeyGenAvatar[]> {
    try {
      const response = await fetch(`${BASE_URL}/heygen/avatars`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to list avatars: ${response.statusText}`);
      }

      const data = await response.json();
      return data.avatars || [];
    } catch (error) {
      console.error('[HeyGenAPI] listAvatars error:', error);
      throw error;
    }
  }

  // ========== VOICES ==========

  /**
   * Get list of available voices
   */
  static async listVoices(language?: string): Promise<HeyGenVoice[]> {
    try {
      const params = new URLSearchParams();
      if (language) params.append('language', language);

      const response = await fetch(`${BASE_URL}/heygen/voices?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to list voices: ${response.statusText}`);
      }

      const data = await response.json();
      return data.voices || [];
    } catch (error) {
      console.error('[HeyGenAPI] listVoices error:', error);
      throw error;
    }
  }

  // ========== VIDEO GENERATION ==========

  /**
   * Generate an avatar video
   */
  static async generateVideo(formData: StoryGeneratorFormData): Promise<HeyGenVideoResponse> {
    try {
      const response = await fetch(`${BASE_URL}/heygen/video/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
        body: JSON.stringify({
          title: formData.title,
          script: formData.script,
          avatar_id: formData.avatar_id,
          voice_id: formData.voice_id,
          platform: formData.platform,
          background_type: formData.background_type,
          background_value: formData.background_value,
          voice_speed: formData.voice_speed,
          voice_pitch: formData.voice_pitch,
          avatar_style: formData.avatar_style,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to generate video: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[HeyGenAPI] generateVideo error:', error);
      throw error;
    }
  }

  /**
   * Check video generation status
   */
  static async getVideoStatus(videoId: string): Promise<HeyGenVideoStatusResponse> {
    try {
      const response = await fetch(`${BASE_URL}/heygen/video/${videoId}/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get video status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[HeyGenAPI] getVideoStatus error:', error);
      throw error;
    }
  }

  /**
   * Get list of generated videos
   */
  static async listVideos(): Promise<HeyGenVideoStatusResponse[]> {
    try {
      const response = await fetch(`${BASE_URL}/heygen/videos`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to list videos: ${response.statusText}`);
      }

      const data = await response.json();
      return data.videos || [];
    } catch (error) {
      console.error('[HeyGenAPI] listVideos error:', error);
      throw error;
    }
  }

  /**
   * Delete a video
   */
  static async deleteVideo(videoId: string): Promise<void> {
    try {
      const response = await fetch(`${BASE_URL}/heygen/video/${videoId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete video: ${response.statusText}`);
      }
    } catch (error) {
      console.error('[HeyGenAPI] deleteVideo error:', error);
      throw error;
    }
  }

  // ========== QUOTA ==========

  /**
   * Get remaining API quota
   */
  static async getQuota(): Promise<HeyGenQuotaResponse> {
    try {
      const response = await fetch(`${BASE_URL}/heygen/quota`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get quota: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[HeyGenAPI] getQuota error:', error);
      throw error;
    }
  }

  // ========== AI SCRIPT GENERATION ==========

  /**
   * Generate script using AI
   */
  static async generateScript(params: {
    topic: string;
    tone: string;
    duration: 'short' | 'medium' | 'long';
    language: string;
  }): Promise<{ script: string }> {
    try {
      const response = await fetch(`${BASE_URL}/heygen/script/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate script: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[HeyGenAPI] generateScript error:', error);
      throw error;
    }
  }
}
