/**
 * Marketing API Service
 * Centralizza tutte le API calls per Marketing Hub
 * Elimina duplicazioni e standardizza error handling
 */

import { toast } from 'sonner';
import type { BusinessDNARequest } from '../types/business-dna.types';
import type { VideoGenerationRequest, VideoGenerationResponse } from '../types/video-generation.types';
import type { BatchContentRequest, BatchContentResponse } from '../types/batch-content.types';
import type { EmailGenerateRequest, EmailGenerateResponse } from '../types/email-campaign.types';

// ==================== TYPES ====================

export interface ContentParams {
  type: string;
  topic: string;
  tone: string;
  platform?: string;
}

export interface ContentResult {
  content: string;
  metadata: {
    type: string;
    tone: string;
    platform?: string;
    topic: string;
  };
  provider: string;
}

export interface ImageParams {
  prompt: string;
  style?: string;
  platform?: string;
  provider?: string;
}

export interface ImageResult {
  image_url: string;
  prompt: string;
  provider: string;
}

export interface PublishParams {
  content: string;
  platforms: string[];
  imageUrl?: string;
  scheduledAt?: string;
}

export interface PublishResult {
  success: boolean;
  results: Array<{
    platform: string;
    status: 'success' | 'error';
    post_id?: string;
    error?: string;
  }>;
}

export interface ScheduledPost {
  id: number;
  content: string;
  title?: string;
  hashtags: string[];
  mentions: string[];
  media_urls: string[];
  media_type: string;
  platforms: string[];
  scheduled_at: string;
  published_at?: string;
  status: 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed' | 'cancelled';
  platform_results: Record<string, any>;
  error_message?: string;
  retry_count: number;
  ai_generated: boolean;
  metrics: Record<string, any>;
  created_at: string;
}

export interface PostFilters {
  status?: string;
  platform?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  limit?: number;
}

export interface CreatePostDto {
  content: string;
  platforms: string[];
  scheduled_at: string;
  title?: string;
  media_urls?: string[];
  hashtags?: string[];
}

export interface UpdatePostDto {
  content?: string;
  platforms?: string[];
  scheduled_at?: string;
  status?: string;
}

// ==================== ERROR HANDLER ====================

function getAuthToken(): string {
  const token = localStorage.getItem('admin_token');
  if (!token) {
    throw new Error('Authentication required');
  }
  return token;
}

async function handleApiResponse<T>(response: Response, context: string): Promise<T> {
  if (!response.ok) {
    const error = await response.text();
    console.error(`[MarketingAPI] ${context} failed:`, error);

    if (response.status === 401) {
      toast.error('Sessione scaduta. Effettua nuovamente il login.');
      // Redirect to login or refresh token
    } else if (response.status === 429) {
      toast.error('Troppe richieste. Riprova tra qualche secondo.');
    } else {
      toast.error(`Errore: ${context}`);
    }

    throw new Error(`${context}: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// ==================== API SERVICE ====================

export class MarketingApiService {
  private static readonly BASE_URL = '/api/v1';

  // ========== CONTENT GENERATION ==========

  static async generateContent(params: ContentParams): Promise<ContentResult> {
    try {
      const response = await fetch(`${this.BASE_URL}/copilot/marketing/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(params)
      });

      return handleApiResponse<ContentResult>(response, 'Content generation');
    } catch (error) {
      console.error('[MarketingAPI] generateContent error:', error);
      throw error;
    }
  }

  static async generateQuickContent(topic: string, type: string = 'social'): Promise<ContentResult> {
    try {
      const response = await fetch(`${this.BASE_URL}/copilot/content/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ topic, type })
      });

      return handleApiResponse<ContentResult>(response, 'Quick content generation');
    } catch (error) {
      console.error('[MarketingAPI] generateQuickContent error:', error);
      throw error;
    }
  }

  // ========== IMAGE GENERATION ==========

  static async generateImage(params: ImageParams): Promise<ImageResult> {
    try {
      const response = await fetch(`${this.BASE_URL}/copilot/image/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(params)
      });

      return handleApiResponse<ImageResult>(response, 'Image generation');
    } catch (error) {
      console.error('[MarketingAPI] generateImage error:', error);
      throw error;
    }
  }

  // ========== SOCIAL PUBLISHING ==========

  static async publishToSocial(params: PublishParams): Promise<PublishResult> {
    try {
      const response = await fetch(`${this.BASE_URL}/copilot/marketing/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(params)
      });

      return handleApiResponse<PublishResult>(response, 'Social media publishing');
    } catch (error) {
      console.error('[MarketingAPI] publishToSocial error:', error);
      throw error;
    }
  }

  // ========== SCHEDULED POSTS (CALENDAR) ==========

  static async getScheduledPosts(filters?: PostFilters): Promise<{ items: ScheduledPost[]; total: number }> {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.platform) params.append('platform', filters.platform);
      if (filters?.dateFrom) params.append('date_from', filters.dateFrom);
      if (filters?.dateTo) params.append('date_to', filters.dateTo);
      if (filters?.page) params.append('page', filters.page.toString());
      if (filters?.limit) params.append('limit', filters.limit.toString());

      const queryString = params.toString();
      const url = `${this.BASE_URL}/marketing/calendar/posts${queryString ? `?${queryString}` : ''}`;

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });

      return handleApiResponse(response, 'Fetch scheduled posts');
    } catch (error) {
      console.error('[MarketingAPI] getScheduledPosts error:', error);
      throw error;
    }
  }

  static async createScheduledPost(post: CreatePostDto): Promise<ScheduledPost> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/calendar/posts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(post)
      });

      return handleApiResponse<ScheduledPost>(response, 'Create scheduled post');
    } catch (error) {
      console.error('[MarketingAPI] createScheduledPost error:', error);
      throw error;
    }
  }

  static async updatePost(id: number, updates: UpdatePostDto): Promise<ScheduledPost> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/calendar/posts/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(updates)
      });

      return handleApiResponse<ScheduledPost>(response, 'Update post');
    } catch (error) {
      console.error('[MarketingAPI] updatePost error:', error);
      throw error;
    }
  }

  static async deletePost(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/calendar/posts/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });

      await handleApiResponse(response, 'Delete post');
    } catch (error) {
      console.error('[MarketingAPI] deletePost error:', error);
      throw error;
    }
  }

  static async publishPostNow(id: number): Promise<ScheduledPost> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/calendar/posts/${id}/publish-now`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });

      return handleApiResponse<ScheduledPost>(response, 'Publish post now');
    } catch (error) {
      console.error('[MarketingAPI] publishPostNow error:', error);
      throw error;
    }
  }

  static async cancelPost(id: number): Promise<ScheduledPost> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/calendar/posts/${id}/cancel`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });

      return handleApiResponse<ScheduledPost>(response, 'Cancel post');
    } catch (error) {
      console.error('[MarketingAPI] cancelPost error:', error);
      throw error;
    }
  }

  // ========== EMAIL CAMPAIGNS ==========

  static async generateEmail(request: EmailGenerateRequest): Promise<EmailGenerateResponse> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/emails/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(request)
      });

      return handleApiResponse<EmailGenerateResponse>(response, 'Generate email');
    } catch (error) {
      console.error('[MarketingAPI] generateEmail error:', error);
      throw error;
    }
  }

  // ========== BUSINESS DNA ==========

  static async generateBusinessDNA(request: BusinessDNARequest, logoFile?: File | null): Promise<Blob> {
    try {
      // Convert to FormData for multipart/form-data
      const formData = new FormData();
      formData.append('company_name', request.company_name);
      formData.append('tagline', request.tagline);
      formData.append('business_overview', request.business_overview);

      // Append logo file if provided
      if (logoFile) {
        formData.append('logo', logoFile);
      }

      if (request.website) {
        formData.append('website', request.website);
      }

      if (request.fonts && request.fonts.length > 0) {
        request.fonts.forEach(font => {
          formData.append('fonts', font);
        });
      }

      if (request.colors) {
        formData.append('colors', JSON.stringify(request.colors));
      }

      if (request.brand_attributes && request.brand_attributes.length > 0) {
        request.brand_attributes.forEach(attr => {
          formData.append('brand_attributes', attr);
        });
      }

      if (request.tone_of_voice && request.tone_of_voice.length > 0) {
        request.tone_of_voice.forEach(tone => {
          formData.append('tone_of_voice', tone);
        });
      }

      const response = await fetch(`${this.BASE_URL}/marketing/business-dna/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Business DNA generation failed: ${errorText}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('[MarketingAPI] generateBusinessDNA error:', error);
      throw error;
    }
  }

  // ========== VIDEO GENERATION ==========

  static async generateVideo(request: VideoGenerationRequest): Promise<VideoGenerationResponse> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/video/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(request)
      });

      return handleApiResponse<VideoGenerationResponse>(response, 'Generate video');
    } catch (error) {
      console.error('[MarketingAPI] generateVideo error:', error);
      throw error;
    }
  }

  // ========== BATCH CONTENT GENERATION ==========

  static async generateBatchContent(request: BatchContentRequest): Promise<BatchContentResponse> {
    try {
      // Chiamata diretta all'AI Microservice via /ai/ proxy
      const response = await fetch('/ai/marketing/content/batch/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${import.meta.env.VITE_AI_SERVICE_API_KEY || 'dev-api-key-change-in-production'}`
        },
        body: JSON.stringify(request)
      });

      return handleApiResponse<BatchContentResponse>(response, 'Batch generate content');
    } catch (error) {
      console.error('[MarketingAPI] generateBatchContent error:', error);
      throw error;
    }
  }

  // ========== ANALYTICS ==========

  static async getStats(): Promise<{
    status_counts: Record<string, number>;
    upcoming_week: number;
    platform_stats_last_30_days: Record<string, number>;
    total_posts: number;
  }> {
    try {
      const response = await fetch(`${this.BASE_URL}/marketing/calendar/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });

      return handleApiResponse(response, 'Get marketing stats');
    } catch (error) {
      console.error('[MarketingAPI] getStats error:', error);
      throw error;
    }
  }
}
