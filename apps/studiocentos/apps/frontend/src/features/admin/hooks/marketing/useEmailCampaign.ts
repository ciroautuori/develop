/**
 * Custom Hook: useEmailCampaign
 * Manages AI email generation for marketing campaigns
 */

import { useState } from 'react';
import { toast } from 'sonner';
import type { EmailGenerateRequest, EmailGenerateResponse } from '../../types/email-campaign.types';
import { MarketingApiService } from '../../services/marketing-api.service';

export function useEmailCampaign() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<EmailGenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = async (request: EmailGenerateRequest) => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await MarketingApiService.generateEmail(request);
      setResult(response);
      toast.success(`Email generata con ${response.ai_model}!`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nella generazione email';
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
