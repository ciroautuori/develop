/**
 * Custom Hook: useBatchContent
 * Manages batch content generation for social media campaigns
 */

import { useState } from 'react';
import { toast } from 'sonner';
import type { BatchContentRequest, BatchContentResponse } from '../../types/batch-content.types';
import { MarketingApiService } from '../../services/marketing-api.service';

export function useBatchContent() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<BatchContentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = async (request: BatchContentRequest) => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await MarketingApiService.generateBatchContent(request);
      setResult(response);

      const totalItems = response.items.length;
      const costEstimate = response.total_cost_estimate.toFixed(2);

      toast.success(
        `${totalItems} contenuti generati in ${response.generation_time.toFixed(1)}s! Costo stimato: $${costEstimate}`
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nella generazione batch';
      setError(message);
      toast.error(message);
    } finally {
      setIsGenerating(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return {
    generate,
    reset,
    isGenerating,
    result,
    error
  };
}
