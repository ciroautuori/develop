/**
 * useContentGeneration Hook
 * Manages AI content generation state and actions
 */

import { useState } from 'react';
import { toast } from 'sonner';
import { MarketingApiService, ContentParams, ContentResult } from '../../services/marketing-api.service';

export function useContentGeneration() {
  const [content, setContent] = useState<ContentResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async (params: ContentParams) => {
    setIsGenerating(true);
    setError(null);

    try {
      const result = await MarketingApiService.generateContent(params);
      setContent(result);
      toast.success('Contenuto generato con successo!');
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Errore durante la generazione';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsGenerating(false);
    }
  };

  const reset = () => {
    setContent(null);
    setError(null);
  };

  return {
    content,
    isGenerating,
    error,
    generate,
    reset
  };
}
