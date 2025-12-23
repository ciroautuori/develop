/**
 * useImageGeneration Hook
 * Manages AI image generation state
 */

import { useState } from 'react';
import { toast } from 'sonner';
import { MarketingApiService, ImageParams, ImageResult } from '../../services/marketing-api.service';

export function useImageGeneration() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async (params: ImageParams): Promise<ImageResult | null> => {
    setIsGenerating(true);
    setError(null);

    try {
      const result = await MarketingApiService.generateImage(params);
      setImageUrl(result.image_url);
      toast.success('Immagine generata!');
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Errore nella generazione';
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setIsGenerating(false);
    }
  };

  const reset = () => {
    setImageUrl(null);
    setError(null);
  };

  return {
    imageUrl,
    isGenerating,
    error,
    generate,
    reset
  };
}
