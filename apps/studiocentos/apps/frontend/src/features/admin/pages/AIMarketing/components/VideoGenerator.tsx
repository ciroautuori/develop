/**
 * VideoGenerator Component
 * DESIGN SYSTEM ALIGNED - Light/Dark mode support
 * WCAG AA Compliant
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Video, Download, RotateCcw, Sparkles, Loader2 } from 'lucide-react';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { cn } from '../../../../../shared/lib/utils';
import { Button } from '../../../../../shared/components/ui/button';
import { useVideoGeneration } from '../../../hooks/marketing/useVideoGeneration';
import { PLATFORM_SPECS, VIDEO_STYLES, type VideoGenerationRequest } from '../../../types/video-generation.types';

export function VideoGenerator() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [prompt, setPrompt] = useState('');
  const [platform, setPlatform] = useState<keyof typeof PLATFORM_SPECS>('instagram');
  const [style, setStyle] = useState('professional');
  const [useGoogleSearch, setUseGoogleSearch] = useState(false);

  const { generate, reset, isGenerating, videoResult, error } = useVideoGeneration();

  // Design System Classes
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
  const textLabel = isDark ? 'text-gray-300' : 'text-gray-700';

  const platformConfig = PLATFORM_SPECS[platform];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const request: VideoGenerationRequest = {
      prompt,
      duration: platformConfig.durationOptimal,
      aspect_ratio: platformConfig.aspectRatio,
      platform,
      style,
      use_google_search: useGoogleSearch
    };
    await generate(request);
  };

  const handleReset = () => {
    setPrompt('');
    setPlatform('instagram');
    setStyle('professional');
    setUseGoogleSearch(false);
    reset();
  };

  return (
    <div className="space-y-4 sm:space-y-6" role="region" aria-label="Video Generator">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6`}
      >
        <div className="flex flex-col sm:flex-row items-start gap-3 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-gold to-gold rounded-lg flex items-center justify-center flex-shrink-0">
            <Video className="w-5 h-5 sm:w-6 sm:h-6 text-white" aria-hidden="true" />
          </div>
          <div>
            <h2 className={`text-xl sm:text-2xl font-bold mb-1 sm:mb-2 ${textPrimary}`}>
              AI Video Generator
            </h2>
            <p className={`text-sm sm:text-base ${textSecondary}`}>
              Genera video professionali con Google Veo 3.1. Perfetto per Reels, TikTok, YouTube Shorts.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
        {/* Prompt */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}
        >
          <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Descrizione Video</h3>
          <div>
            <label htmlFor="video-prompt" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
              Prompt <span className="text-gray-400">*</span>
            </label>
            <textarea
              id="video-prompt"
              required
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Es. Un time-lapse di una città moderna al tramonto, con grattacieli illuminati..."
              className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold resize-none`}
            />
            <p className={`text-xs mt-1.5 ${textSecondary}`}>
              Descrivi in dettaglio cosa vuoi vedere nel video
            </p>
          </div>
        </motion.div>

        {/* Platform Selection */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}
        >
          <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Piattaforma Target</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 sm:gap-3">
            {(Object.keys(PLATFORM_SPECS) as Array<keyof typeof PLATFORM_SPECS>).map((p) => {
              const spec = PLATFORM_SPECS[p];
              const isSelected = platform === p;
              return (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPlatform(p)}
                  className={cn(
                    'p-3 sm:p-4 rounded-lg sm:rounded-xl border-2 transition-all min-h-[80px] flex flex-col items-center justify-center',
                    isSelected
                      ? 'border-gold bg-gold/10'
                      : isDark
                      ? 'border-white/10 hover:border-white/20 bg-white/5'
                      : 'border-gray-200 hover:border-gray-300 bg-gray-50',
                    'focus:outline-none focus:ring-2 focus:ring-gold'
                  )}
                >
                  <div className="text-2xl mb-1">{spec.icon}</div>
                  <div className={`text-xs sm:text-sm font-medium ${textPrimary}`}>{spec.label}</div>
                  <div className={`text-xs ${textSecondary}`}>{spec.aspectRatio}</div>
                </button>
              );
            })}
          </div>
          <p className={`text-xs sm:text-sm ${textSecondary}`}>
            Durata ottimale: {platformConfig.durationOptimal}s • {platformConfig.description}
          </p>
        </motion.div>

        {/* Style & Options */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}
        >
          <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Stile e Opzioni</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="video-style" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
                Stile Visivo
              </label>
              <select
                id="video-style"
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${selectBg} focus:ring-2 focus:ring-gold min-h-[44px]`}
              >
                {VIDEO_STYLES.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center">
              <label className={cn(
                'flex items-center gap-3 p-3 sm:p-4 rounded-lg sm:rounded-xl border w-full cursor-pointer',
                useGoogleSearch
                  ? 'border-gold bg-gold/10'
                  : isDark
                  ? 'border-white/10 bg-white/5'
                  : 'border-gray-200 bg-gray-50'
              )}>
                <input
                  type="checkbox"
                  checked={useGoogleSearch}
                  onChange={(e) => setUseGoogleSearch(e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-gold focus:ring-gold"
                />
                <div>
                  <span className={`font-medium text-sm ${textPrimary}`}>Google Search Grounding</span>
                  <p className={`text-xs ${textSecondary}`}>Dati real-time</p>
                </div>
              </label>
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            type="submit"
            disabled={isGenerating || !prompt.trim()}
            className="flex-1 bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold min-h-[44px]"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Generazione...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Genera Video
              </>
            )}
          </Button>
          <Button type="button" variant="outline" onClick={handleReset} disabled={isGenerating} className="min-h-[44px]">
            <RotateCcw className="w-5 h-5 mr-2" />
            Reset
          </Button>
        </div>
      </form>

      {/* Error */}
      {error && (
        <div className={cn('p-3 sm:p-4 rounded-lg', isDark ? 'bg-white/10/20 border border-gray-600' : 'bg-gray-50 border border-gray-300')} role="alert">
          <p className={cn('text-sm', isDark ? 'text-gray-300' : 'text-gray-600')}>{error}</p>
        </div>
      )}

      {/* Video Result */}
      {videoResult && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Video Generato</h3>
              <p className={`text-xs sm:text-sm ${textSecondary}`}>
                Generato in {videoResult.generation_time.toFixed(1)}s • {platformConfig.aspectRatio}
              </p>
            </div>
            <a
              href={videoResult.video_url}
              download
              className="inline-flex items-center px-4 py-2.5 bg-gold hover:bg-gold/90 text-white rounded-lg font-medium min-h-[44px] w-full sm:w-auto justify-center"
            >
              <Download className="w-5 h-5 mr-2" />
              Scarica
            </a>
          </div>
          <div className={cn('rounded-lg overflow-hidden', isDark ? 'bg-black' : 'bg-[#0A0A0A]')}>
            <video
              controls
              preload="metadata"
              className="w-full max-h-[400px] mx-auto"
              poster={videoResult.thumbnail_url || undefined}
            >
              <source src={videoResult.video_url} type="video/mp4" />
              <track kind="captions" />
            </video>
          </div>
          <div className={cn('p-3 sm:p-4 rounded-lg', isDark ? 'bg-white/5' : 'bg-gray-50')}>
            <h4 className={`text-sm font-medium mb-1.5 ${textLabel}`}>Prompt Utilizzato</h4>
            <p className={`text-sm ${textSecondary}`}>{videoResult.prompt_used}</p>
          </div>
        </motion.div>
      )}
    </div>
  );
}
