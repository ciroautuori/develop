/**
 * ImageGenerator Component
 * AI image generation with Google Gemini and DALL-E
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Image, Loader2, Download, RefreshCw } from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { useImageGeneration } from '../../../hooks/marketing/useImageGeneration';

export default function ImageGenerator() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const { imageUrl, isGenerating, generate, reset } = useImageGeneration();

  const [prompt, setPrompt] = useState('');
  const [provider, setProvider] = useState<'google_ai' | 'dalle' | 'pollinations'>('google_ai');

  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-300 text-gray-900';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Inserisci una descrizione');
      return;
    }

    await generate({ prompt, provider });
  };

  const handleDownload = () => {
    if (imageUrl) {
      const link = document.createElement('a');
      link.href = imageUrl;
      link.download = 'generated-image.png';
      link.click();
      toast.success('Download avviato!');
    }
  };

  const promptSuggestions = [
    'Immagine professionale di un ufficio moderno con computer',
    'Team che collabora in uno spazio coworking luminoso',
    'Dashboard digitale con grafici e metriche di business',
    'Smartphone che mostra una app di e-commerce',
    'Persona che lavora da casa con setup minimale',
  ];

  return (
    <div className="space-y-6" role="region" aria-label="Generatore di immagini AI">
      {/* Input Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`${cardBg} rounded-2xl p-6 space-y-4`}
      >
        <h2 className={`text-2xl font-bold ${textPrimary}`}>
          Genera Immagine AI
        </h2>

        <div>
          <label htmlFor="prompt-input" className={`block text-sm font-medium mb-2 ${textSecondary}`}>
            Descrizione Immagine
          </label>
          <textarea
            id="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Descrivi l'immagine che vuoi generare..."
            aria-describedby="prompt-hint"
            className={`w-full px-4 py-3 rounded-xl border ${inputBg} min-h-[120px] resize-none focus:ring-2 focus:ring-gold`}
          />
          <span id="prompt-hint" className="sr-only">Descrivi in dettaglio l'immagine che l'AI dovrà generare</span>
        </div>

        {/* Prompt Suggestions */}
        <div>
          <label id="suggestions-label" className={`block text-sm font-medium mb-2 ${textSecondary}`}>
            Suggerimenti Veloci
          </label>
          <div
            className="flex flex-wrap gap-2"
            role="group"
            aria-labelledby="suggestions-label"
          >
            {promptSuggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => setPrompt(suggestion)}
                aria-label={`Usa suggerimento: ${suggestion}`}
                className={`px-3 py-3 rounded-lg text-xs transition-all focus:outline-none focus:ring-2 focus:ring-gold ${
                  isDark
                    ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                {suggestion.slice(0, 40)}...
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="provider-select" className={`block text-sm font-medium mb-2 ${textSecondary}`}>
              Provider AI
            </label>
            <select
              id="provider-select"
              value={provider}
              onChange={(e) => setProvider(e.target.value as any)}
              aria-label="Seleziona il provider AI per generare l'immagine"
              className={`w-full px-4 py-3 rounded-xl border ${selectBg} focus:ring-2 focus:ring-gold`}
            >
              <option value="google_ai">Google Gemini (Imagen 3)</option>
              <option value="dalle">DALL-E 3 (OpenAI)</option>
              <option value="pollinations">Pollinations (Flux)</option>
            </select>
          </div>

          <div className="flex items-end">
            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              aria-label="Genera immagine con AI"
              aria-busy={isGenerating}
              className="w-full bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" aria-hidden="true" />
                  Generando...
                </>
              ) : (
                <>
                  <Image className="w-5 h-5 mr-2" aria-hidden="true" />
                  Genera Immagine
                </>
              )}
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Generated Image Preview */}
      {imageUrl && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`${cardBg} rounded-2xl p-6 space-y-4`}
          role="region"
          aria-label="Anteprima immagine generata"
          aria-live="polite"
        >
          <div className="flex items-center justify-between">
            <h3 className={`text-xl font-bold ${textPrimary}`}>Immagine Generata</h3>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={reset}
                size="sm"
                aria-label="Rigenera immagine"
              >
                <RefreshCw className="w-4 h-4" aria-hidden="true" />
              </Button>
              <Button
                onClick={handleDownload}
                size="sm"
                className="bg-gold hover:bg-gold/90"
                aria-label="Scarica immagine generata"
              >
                <Download className="w-4 h-4 mr-2" aria-hidden="true" />
                Download
              </Button>
            </div>
          </div>

          <div className="relative aspect-video rounded-xl overflow-hidden bg-black/20">
            <img
              src={imageUrl}
              alt={`Immagine AI generata: ${prompt}`}
              className="w-full h-full object-contain"
            />
          </div>

          <div className="flex gap-4 text-sm">
            <span className={textSecondary}>
              Provider: <strong className={textPrimary}>{provider.toUpperCase()}</strong>
            </span>
            <span className={textSecondary}>
              Prompt: <strong className={textPrimary}>{prompt.slice(0, 50)}...</strong>
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}
