/**
 * BatchContentModal Component
 * Generate complete social media campaigns in batch
 * Backend: /apps/ai_microservice/app/core/api/v1/marketing.py:970
 * WCAG AA Compliant
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Calendar, Image, Video, FileText, AtSign } from 'lucide-react';
import { useBatchContent } from '../../../hooks/marketing/useBatchContent';
import { DEFAULT_BATCH_PLATFORMS, BATCH_CONTENT_LIMITS } from '../../../types/batch-content.types';
import type { BatchContentItem } from '../../../types/batch-content.types';

interface BatchContentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (items: BatchContentItem[]) => void;
}

export function BatchContentModal({ isOpen, onClose, onSuccess }: BatchContentModalProps) {
  const [topic, setTopic] = useState('');
  const [platforms, setPlatforms] = useState<string[]>(DEFAULT_BATCH_PLATFORMS);
  const [postCount, setPostCount] = useState<number>(BATCH_CONTENT_LIMITS.post_count.default);
  const [storyCount, setStoryCount] = useState<number>(BATCH_CONTENT_LIMITS.story_count.default);
  const [videoCount, setVideoCount] = useState<number>(BATCH_CONTENT_LIMITS.video_count.default);
  const [style, setStyle] = useState('professional');
  const [useProQuality, setUseProQuality] = useState(false);
  const [mentions, setMentions] = useState<string[]>([]);
  const [mentionInput, setMentionInput] = useState('');

  const { generate, reset, isGenerating, result, error } = useBatchContent();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await generate({
      topic,
      platforms,
      post_count: postCount,
      story_count: storyCount,
      video_count: videoCount,
      style,
      use_pro_quality: useProQuality,
      mentions: mentions.length > 0 ? mentions : undefined
    });
  };

  const handleClose = () => {
    if (result && onSuccess) {
      onSuccess(result.items);
    }
    reset();
    setTopic('');
    setPlatforms(DEFAULT_BATCH_PLATFORMS);
    setPostCount(BATCH_CONTENT_LIMITS.post_count.default);
    setStoryCount(BATCH_CONTENT_LIMITS.story_count.default);
    setVideoCount(BATCH_CONTENT_LIMITS.video_count.default);
    setStyle('professional');
    setUseProQuality(false);
    setMentions([]);
    setMentionInput('');
    onClose();
  };

  const togglePlatform = (platform: string) => {
    setPlatforms(prev =>
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  // Add mention (tag person/account)
  const addMention = () => {
    const mention = mentionInput.trim().replace(/^@/, '');
    if (mention && !mentions.includes(mention)) {
      setMentions((prev) => [...prev, mention]);
      setMentionInput('');
    }
  };

  // Remove mention
  const removeMention = (mention: string) => {
    setMentions((prev) => prev.filter((m) => m !== mention));
  };

  const totalContent = postCount * platforms.length + storyCount + videoCount;

  const platformOptions = [
    { id: 'instagram', label: 'Instagram', icon: '📸' },
    { id: 'facebook', label: 'Facebook', icon: '👍' },
    { id: 'tiktok', label: 'TikTok', icon: '🎵' },
    { id: 'linkedin', label: 'LinkedIn', icon: '💼' }
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/50 z-50"
            aria-hidden="true"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="batch-modal-title"
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-[#0A0A0A] rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="sticky top-0 bg-gradient-to-r from-gold to-gold p-6 text-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Calendar className="w-6 h-6" aria-hidden="true" />
                  <h2 id="batch-modal-title" className="text-xl font-bold">
                    Generazione Batch Contenuti
                  </h2>
                </div>
                <button
                  onClick={handleClose}
                  disabled={isGenerating}
                  className="w-10 h-10 rounded-lg hover:bg-white/20 flex items-center justify-center
                           transition-colors disabled:opacity-50 focus:ring-2 focus:ring-white"
                  aria-label="Chiudi modal"
                >
                  <X className="w-5 h-5" aria-hidden="true" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {!result ? (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Topic */}
                    <div>
                      <label htmlFor="batch-topic" className="block text-sm font-medium mb-2">
                        Topic Campagna <span className="text-gray-400" aria-label="obbligatorio">*</span>
                      </label>
                      <input
                        id="batch-topic"
                        type="text"
                        required
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="Es. Lancio nuovo prodotto Digital Marketing"
                        className="w-full px-4 py-3 border border-gray-300 dark:border-white/10 rounded-lg
                                 bg-white dark:bg-[#1A1A1A] focus:ring-2 focus:ring-gold focus:border-transparent
                                 min-h-[44px]"
                        aria-required="true"
                      />
                    </div>

                    {/* Platforms */}
                    <fieldset>
                      <legend className="text-sm font-medium mb-3">Piattaforme Target</legend>
                      <div className="grid grid-cols-2 gap-3">
                        {platformOptions.map((platform) => {
                          const isChecked = platforms.includes(platform.id);
                          return (
                            <button
                              key={platform.id}
                              type="button"
                              onClick={() => togglePlatform(platform.id)}
                              role="checkbox"
                              aria-checked={isChecked}
                              className={`p-4 rounded-lg border-2 transition-all min-h-[44px] flex items-center gap-3
                                ${isChecked
                                  ? 'border-gold bg-gold/10 dark:bg-gold/20'
                                  : 'border-gray-300 dark:border-white/10'
                                }
                                hover:border-gold focus:ring-2 focus:ring-gold focus:ring-offset-2`}
                            >
                              <span className="text-2xl" aria-hidden="true">{platform.icon}</span>
                              <span className="font-medium">{platform.label}</span>
                            </button>
                          );
                        })}
                      </div>
                      {platforms.length === 0 && (
                        <p className="text-sm text-gray-500 mt-2" role="alert">
                          Seleziona almeno una piattaforma
                        </p>
                      )}
                    </fieldset>

                    {/* Content Counts */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label htmlFor="post-count" className="block text-sm font-medium mb-2 flex items-center gap-2">
                          <FileText className="w-4 h-4" aria-hidden="true" />
                          Post per piattaforma
                        </label>
                        <input
                          id="post-count"
                          type="number"
                          min={BATCH_CONTENT_LIMITS.post_count.min}
                          max={BATCH_CONTENT_LIMITS.post_count.max}
                          value={postCount}
                          onChange={(e) => setPostCount(parseInt(e.target.value))}
                          className="w-full px-4 py-3 border border-gray-300 dark:border-white/10 rounded-lg
                                   bg-white dark:bg-[#1A1A1A] focus:ring-2 focus:ring-gold min-h-[44px]"
                        />
                        <p className="text-xs text-gray-500 mt-1">1-5 post</p>
                      </div>

                      <div>
                        <label htmlFor="story-count" className="block text-sm font-medium mb-2 flex items-center gap-2">
                          <Image className="w-4 h-4" aria-hidden="true" />
                          Stories
                        </label>
                        <input
                          id="story-count"
                          type="number"
                          min={BATCH_CONTENT_LIMITS.story_count.min}
                          max={BATCH_CONTENT_LIMITS.story_count.max}
                          value={storyCount}
                          onChange={(e) => setStoryCount(parseInt(e.target.value))}
                          className="w-full px-4 py-3 border border-gray-300 dark:border-white/10 rounded-lg
                                   bg-white dark:bg-[#1A1A1A] focus:ring-2 focus:ring-gold min-h-[44px]"
                        />
                        <p className="text-xs text-gray-500 mt-1">0-10 stories</p>
                      </div>

                      <div>
                        <label htmlFor="video-count" className="block text-sm font-medium mb-2 flex items-center gap-2">
                          <Video className="w-4 h-4" aria-hidden="true" />
                          Video/Reels
                        </label>
                        <input
                          id="video-count"
                          type="number"
                          min={BATCH_CONTENT_LIMITS.video_count.min}
                          max={BATCH_CONTENT_LIMITS.video_count.max}
                          value={videoCount}
                          onChange={(e) => setVideoCount(parseInt(e.target.value))}
                          className="w-full px-4 py-3 border border-gray-300 dark:border-white/10 rounded-lg
                                   bg-white dark:bg-[#1A1A1A] focus:ring-2 focus:ring-gold min-h-[44px]"
                        />
                        <p className="text-xs text-gray-500 mt-1">0-3 video</p>
                      </div>
                    </div>

                    {/* Style */}
                    <div>
                      <label htmlFor="batch-style" className="block text-sm font-medium mb-2">
                        Stile Visivo
                      </label>
                      <select
                        id="batch-style"
                        value={style}
                        onChange={(e) => setStyle(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-white/10 rounded-lg
                                 bg-white dark:bg-[#1A1A1A] focus:ring-2 focus:ring-gold min-h-[44px]"
                      >
                        <option value="professional">Professional</option>
                        <option value="modern">Modern</option>
                        <option value="elegant">Elegant</option>
                        <option value="dynamic">Dynamic</option>
                        <option value="minimalist">Minimalist</option>
                      </select>
                    </div>

                    {/* Tag Persone / Mentions */}
                    <div>
                      <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                        <AtSign className="w-4 h-4" aria-hidden="true" />
                        Tag Persone / Account (opzionale)
                      </label>
                      <div className="flex items-center gap-2 mb-2">
                        <input
                          type="text"
                          value={mentionInput}
                          onChange={(e) => setMentionInput(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addMention())}
                          placeholder="@username da taggare..."
                          className="flex-1 px-4 py-3 border border-gray-300 dark:border-white/10 rounded-lg
                                   bg-white dark:bg-[#1A1A1A] focus:ring-2 focus:ring-gold min-h-[44px]"
                        />
                        <button
                          type="button"
                          onClick={addMention}
                          className="px-4 py-3 bg-gold/20 text-gold rounded-lg hover:bg-gold/30 transition-colors min-h-[44px]"
                        >
                          Aggiungi
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mb-2">
                        💡 Inserisci username senza @ - verranno aggiunti a tutti i contenuti generati
                      </p>
                      {mentions.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {mentions.map((mention) => (
                            <span
                              key={mention}
                              className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-blue-500/20 text-blue-400"
                            >
                              @{mention}
                              <button
                                type="button"
                                onClick={() => removeMention(mention)}
                                className="hover:text-gray-400"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Pro Quality */}
                    <div className="flex items-start gap-3 p-4 bg-gold/10 dark:bg-gold/20/20 border border-gold dark:border-gold rounded-lg">
                      <input
                        id="pro-quality"
                        type="checkbox"
                        checked={useProQuality}
                        onChange={(e) => setUseProQuality(e.target.checked)}
                        className="w-5 h-5 mt-0.5 rounded border-gray-300 text-gold focus:ring-gold"
                      />
                      <label htmlFor="pro-quality" className="text-sm">
                        <span className="font-medium">Qualità PRO (4K)</span>
                        <span className="text-gray-600 dark:text-gray-400 block">
                          Usa Nano Banana Pro per immagini 4K ultra-dettagliate (costo maggiore)
                        </span>
                      </label>
                    </div>

                    {/* Summary */}
                    <div className="bg-gold/10 dark:bg-gold/20 border border-gold/30 dark:border-gold/40 p-4 rounded-lg">
                      <p className="text-sm font-medium mb-2">Contenuti da generare:</p>
                      <ul className="text-sm space-y-1 text-gray-600 dark:text-gray-400">
                        <li>📝 {postCount * platforms.length} post ({postCount} per piattaforma × {platforms.length})</li>
                        <li>📸 {storyCount} stories</li>
                        <li>🎥 {videoCount} video/reels</li>
                        <li className="font-bold text-gold dark:text-gold pt-2 mt-2 border-t">
                          Totale: {totalContent} contenuti
                        </li>
                      </ul>
                    </div>

                    {/* Error */}
                    {error && (
                      <div
                        className="bg-gray-50 dark:bg-white/10/20 border border-gray-300 dark:border-gray-600 p-4 rounded-lg"
                        role="alert"
                        aria-live="assertive"
                      >
                        <p className="text-gray-600 dark:text-gray-300 text-sm">{error}</p>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-3 pt-4">
                      <button
                        type="submit"
                        disabled={isGenerating || platforms.length === 0}
                        className="flex-1 px-6 py-3 bg-gradient-to-r from-gold to-gold
                                 text-white rounded-lg font-medium hover:from-gold/90 hover:to-gold
                                 disabled:opacity-50 disabled:cursor-not-allowed transition-all
                                 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl
                                 min-h-[44px] focus:ring-2 focus:ring-gold focus:ring-offset-2"
                      >
                        <Sparkles className={`w-5 h-5 ${isGenerating ? 'animate-spin' : ''}`} aria-hidden="true" />
                        {isGenerating ? 'Generazione in corso...' : 'Genera Campagna'}
                      </button>
                      <button
                        type="button"
                        onClick={handleClose}
                        disabled={isGenerating}
                        className="px-6 py-3 border border-gray-300 dark:border-white/10 rounded-lg
                                 hover:bg-gray-50 dark:hover:bg-[#1A1A1A] disabled:opacity-50
                                 transition-colors min-h-[44px] focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                      >
                        Annulla
                      </button>
                    </div>
                  </form>
                ) : (
                  /* Results */
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                  >
                    <div className="text-center">
                      <div className="w-16 h-16 bg-gold/10 dark:bg-gold/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Sparkles className="w-8 h-8 text-gold dark:text-gold" aria-hidden="true" />
                      </div>
                      <h3 className="text-xl font-bold mb-2">Campagna Generata!</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {result.items.length} contenuti pronti in {result.generation_time.toFixed(1)}s
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        Costo stimato: ${result.total_cost_estimate.toFixed(2)}
                      </p>
                    </div>

                    {/* Content Summary */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-gold/10 dark:bg-gold/20 rounded-lg">
                        <FileText className="w-8 h-8 mx-auto mb-2 text-gold" aria-hidden="true" />
                        <div className="text-2xl font-bold">
                          {result.items.filter(i => i.content_type === 'post').length}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Post</div>
                      </div>
                      <div className="text-center p-4 bg-gold/10 dark:bg-gold/20 rounded-lg">
                        <Image className="w-8 h-8 mx-auto mb-2 text-gold" aria-hidden="true" />
                        <div className="text-2xl font-bold">
                          {result.items.filter(i => i.content_type === 'story').length}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Stories</div>
                      </div>
                      <div className="text-center p-4 bg-gold/10 dark:bg-gold/20 rounded-lg">
                        <Video className="w-8 h-8 mx-auto mb-2 text-gold" aria-hidden="true" />
                        <div className="text-2xl font-bold">
                          {result.items.filter(i => i.content_type === 'video').length}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Video</div>
                      </div>
                    </div>

                    <button
                      onClick={handleClose}
                      className="w-full px-6 py-3 bg-gradient-to-r from-gold to-gold
                               text-white rounded-lg font-medium hover:from-gold/90 hover:to-gold
                               transition-all shadow-lg hover:shadow-xl min-h-[44px]
                               focus:ring-2 focus:ring-gold focus:ring-offset-2"
                    >
                      Aggiungi al Calendario
                    </button>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
