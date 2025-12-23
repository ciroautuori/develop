/**
 * Custom Hook: useStoryGenerator
 * Manages AI Story/Video Avatar generation state
 */

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { HeyGenApiService } from '../../services/heygen-api.service';
import type {
  HeyGenAvatar,
  HeyGenVoice,
  HeyGenVideoStatus,
  StoryGeneratorFormData,
  GeneratedStory,
} from '../../types/heygen.types';

interface UseStoryGeneratorReturn {
  // Data
  avatars: HeyGenAvatar[];
  voices: HeyGenVoice[];
  generatedVideos: GeneratedStory[];
  currentVideo: GeneratedStory | null;
  quota: { remaining: number; used: number } | null;

  // States
  isLoadingAvatars: boolean;
  isLoadingVoices: boolean;
  isGenerating: boolean;
  isPolling: boolean;
  error: string | null;

  // Actions
  loadAvatars: () => Promise<void>;
  loadVoices: (language?: string) => Promise<void>;
  generateVideo: (formData: StoryGeneratorFormData) => Promise<string | null>;
  generateScript: (topic: string, tone: string, duration: 'short' | 'medium' | 'long', language: string) => Promise<string | null>;
  checkVideoStatus: (videoId: string) => Promise<HeyGenVideoStatus>;
  loadQuota: () => Promise<void>;
  deleteVideo: (videoId: string) => Promise<void>;
  reset: () => void;
}

export function useStoryGenerator(): UseStoryGeneratorReturn {
  // Data states
  const [avatars, setAvatars] = useState<HeyGenAvatar[]>([]);
  const [voices, setVoices] = useState<HeyGenVoice[]>([]);
  const [generatedVideos, setGeneratedVideos] = useState<GeneratedStory[]>([]);
  const [currentVideo, setCurrentVideo] = useState<GeneratedStory | null>(null);
  const [quota, setQuota] = useState<{ remaining: number; used: number } | null>(null);

  // Loading states
  const [isLoadingAvatars, setIsLoadingAvatars] = useState(false);
  const [isLoadingVoices, setIsLoadingVoices] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load avatars
  const loadAvatars = useCallback(async () => {
    setIsLoadingAvatars(true);
    setError(null);
    try {
      const data = await HeyGenApiService.listAvatars();
      setAvatars(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nel caricamento avatar';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoadingAvatars(false);
    }
  }, []);

  // Load voices
  const loadVoices = useCallback(async (language?: string) => {
    setIsLoadingVoices(true);
    setError(null);
    try {
      const data = await HeyGenApiService.listVoices(language);
      setVoices(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nel caricamento voci';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoadingVoices(false);
    }
  }, []);

  // Load quota
  const loadQuota = useCallback(async () => {
    try {
      const data = await HeyGenApiService.getQuota();
      if (data.data) {
        setQuota({
          remaining: data.data.remaining_quota,
          used: data.data.used_quota,
        });
      }
    } catch (err) {
      console.error('Failed to load quota:', err);
    }
  }, []);

  // Check video status with polling
  const checkVideoStatus = useCallback(async (videoId: string): Promise<HeyGenVideoStatus> => {
    try {
      const response = await HeyGenApiService.getVideoStatus(videoId);
      const status = response.data?.status || 'pending';

      // Update current video
      if (currentVideo && currentVideo.video_id === videoId) {
        setCurrentVideo(prev => prev ? {
          ...prev,
          status,
          video_url: response.data?.video_url,
          thumbnail_url: response.data?.thumbnail_url,
          duration: response.data?.duration,
        } : null);
      }

      // Update in list
      setGeneratedVideos(prev => prev.map(v =>
        v.video_id === videoId
          ? { ...v, status, video_url: response.data?.video_url, thumbnail_url: response.data?.thumbnail_url }
          : v
      ));

      return status;
    } catch (err) {
      console.error('Failed to check video status:', err);
      return 'failed';
    }
  }, [currentVideo]);

  // Generate video
  const generateVideo = useCallback(async (formData: StoryGeneratorFormData): Promise<string | null> => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await HeyGenApiService.generateVideo(formData);
      const videoId = response.data?.video_id;

      if (!videoId) {
        throw new Error('No video_id in response');
      }

      // Create new story entry
      const newStory: GeneratedStory = {
        id: videoId,
        video_id: videoId,
        title: formData.title,
        platform: formData.platform,
        status: 'pending',
        created_at: new Date(),
        script: formData.script,
      };

      setCurrentVideo(newStory);
      setGeneratedVideos(prev => [newStory, ...prev]);

      toast.success('Video in generazione! Ti avviseremo quando sarà pronto.');

      // Start polling for status
      setIsPolling(true);
      pollVideoStatus(videoId);

      return videoId;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nella generazione video';
      setError(message);
      toast.error(message);
      return null;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  // Poll video status
  const pollVideoStatus = useCallback(async (videoId: string) => {
    const maxAttempts = 60; // 5 minutes with 5s interval
    let attempts = 0;

    const poll = async () => {
      attempts++;
      const status = await checkVideoStatus(videoId);

      if (status === 'completed') {
        setIsPolling(false);
        toast.success('🎬 Video pronto! Puoi scaricarlo ora.');
        loadQuota(); // Refresh quota
      } else if (status === 'failed') {
        setIsPolling(false);
        toast.error('Generazione video fallita');
      } else if (attempts < maxAttempts) {
        setTimeout(poll, 5000); // Poll every 5 seconds
      } else {
        setIsPolling(false);
        toast.warning('Timeout: controlla lo stato manualmente');
      }
    };

    poll();
  }, [checkVideoStatus, loadQuota]);

  // Generate script with AI
  const generateScript = useCallback(async (
    topic: string,
    tone: string,
    duration: 'short' | 'medium' | 'long',
    language: string
  ): Promise<string | null> => {
    try {
      const response = await HeyGenApiService.generateScript({ topic, tone, duration, language });
      return response.script;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nella generazione script';
      toast.error(message);
      return null;
    }
  }, []);

  // Delete video
  const deleteVideo = useCallback(async (videoId: string) => {
    try {
      await HeyGenApiService.deleteVideo(videoId);
      setGeneratedVideos(prev => prev.filter(v => v.video_id !== videoId));
      if (currentVideo?.video_id === videoId) {
        setCurrentVideo(null);
      }
      toast.success('Video eliminato');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nell\'eliminazione';
      toast.error(message);
    }
  }, [currentVideo]);

  // Reset
  const reset = useCallback(() => {
    setCurrentVideo(null);
    setError(null);
    setIsPolling(false);
  }, []);

  // Load initial data
  useEffect(() => {
    loadAvatars();
    loadVoices('it'); // Default to Italian
    loadQuota();
  }, []);

  return {
    // Data
    avatars,
    voices,
    generatedVideos,
    currentVideo,
    quota,

    // States
    isLoadingAvatars,
    isLoadingVoices,
    isGenerating,
    isPolling,
    error,

    // Actions
    loadAvatars,
    loadVoices,
    generateVideo,
    generateScript,
    checkVideoStatus,
    loadQuota,
    deleteVideo,
    reset,
  };
}
