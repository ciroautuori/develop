/**
 * Custom Hook: useBusinessDNA
 * Manages Business DNA generation state and logic
 */

import { useState } from 'react';
import { toast } from 'sonner';
import type { BusinessDNARequest, BusinessDNAFormData } from '../../types/business-dna.types';
import { MarketingApiService } from '../../services/marketing-api.service';

export function useBusinessDNA() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [imageBlob, setImageBlob] = useState<Blob | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = async (formData: BusinessDNAFormData, logoFile?: File | null) => {
    setIsGenerating(true);
    setError(null);

    try {
      // Convert form data to API format
      const request: BusinessDNARequest = {
        company_name: formData.company_name.trim(),
        tagline: formData.tagline.trim(),
        business_overview: formData.business_overview.trim(),
        website: formData.website.trim() || undefined,
        fonts: formData.fonts
          .split(',')
          .map(f => f.trim())
          .filter(f => f.length > 0),
        colors: {
          primary: formData.primary_color,
          secondary: formData.secondary_color,
          accent: formData.accent_color
        },
        brand_attributes: formData.brand_attributes
          .split(',')
          .map(a => a.trim())
          .filter(a => a.length > 0),
        tone_of_voice: formData.tone_of_voice
          .split(',')
          .map(t => t.trim())
          .filter(t => t.length > 0)
      };

      const blob = await MarketingApiService.generateBusinessDNA(request, logoFile);
      setImageBlob(blob);

      // Create object URL for preview
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
      const url = URL.createObjectURL(blob);
      setImageUrl(url);

      toast.success('Business DNA generato con successo!');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Errore nella generazione';
      setError(message);
      toast.error(message);
    } finally {
      setIsGenerating(false);
    }
  };

  const download = () => {
    if (!imageBlob) return;

    const url = URL.createObjectURL(imageBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'business-dna.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success('Download avviato!');
  };

  const reset = () => {
    setImageBlob(null);
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl);
      setImageUrl(null);
    }
    setError(null);
  };

  return {
    generate,
    download,
    reset,
    isGenerating,
    imageBlob,
    imageUrl,
    error
  };
}
