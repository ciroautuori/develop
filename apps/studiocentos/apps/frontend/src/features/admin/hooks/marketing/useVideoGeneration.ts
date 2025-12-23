/**
 * Custom Hook: useVideoGeneration
 * Manages AI video generation state and logic
 * Backend: Google Veo 3.1 via /api/v1/marketing/video/generate
 */

import { useState } from 'react';
import { toast } from 'sonner';
import type { VideoGenerationRequest, VideoGenerationResponse } from '../../types/video-generation.types';
import { MarketingApiService } from '../../services/marketing-api.service';

export function useVideoGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoResult, setVideoResult] = useState<VideoGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = async (request: VideoGenerationRequest) => {
    setIsGenerating(true);
    setError(null);

    try {
      const result = await MarketingApiService.generateVideo(request);
      setVideoResult(result);
      toast.success(`Video generato in ${result.generation_time.toFixed(1)}s!`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nella generazione video';
      setError(message);
      toast.error(message);
    } finally {
      setIsGenerating(false);
    }
  };

  const reset = () => {
    setVideoResult(null);
    setError(null);
  };

  return {
    generate,
    reset,
    isGenerating,
    videoResult,
    error
  };
}
