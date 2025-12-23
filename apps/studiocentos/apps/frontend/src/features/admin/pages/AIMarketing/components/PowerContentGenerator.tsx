/**
 * 🚀 PowerContentGenerator Component - PRODUCTION READY
 *
 * Features:
 * - Content Format Selection (Post, Story, Carousel, Reel, Video)
 * - Brand DNA Auto-Inject
 * - Slides/Scenes Structured Output
 * - AI Image Prompts per Slide
 * - Full /generate-format API Integration
 *
 * @module components/PowerContentGenerator
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  FileText,
  Share2,
  Video,
  Mail,
  Copy,
  Check,
  Loader2,
  Send,
  ImagePlus,
  Eye,
  Zap,
  ChevronDown,
  ChevronUp,
  Layers,
  Film,
  Play,
  Clock,
  Music,
  Palette,
  Settings2,
} from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { cn } from '../../../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';

// API e Costanti
import { BrandContextAPI } from '../api/brandContext';
import { SOCIAL_QUICK_TEMPLATES } from '../constants/quick-templates';
import { SOCIAL_PLATFORMS } from '../constants/platforms';
import {
  CONTENT_FORMATS,
  CONTENT_FORMATS_LIST,
  DURATION_OPTIONS,
  SLIDES_OPTIONS,
  VIDEO_STYLES,
  MUSIC_MOODS,
  type ContentFormatType,
  type SlideContent,
  type FormatGenerationResult,
  formatHasSlides,
  formatHasScenes,
  getFormatDefaults,
} from '../constants/content-formats';

// ============================================================================
// TYPES
// ============================================================================

interface GeneratedFormatContent {
  format: ContentFormatType;
  mainContent: string;
  caption: string;
  slides: SlideContent[];
  scenes: SlideContent[];
  hashtags: string[];
  ctaOptions: string[];
  coverImagePrompt: string | null;
  platform: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

export function PowerContentGenerator() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Theme styles
  const cardBg = isDark ? 'bg-white/5 border border-white/10' : 'bg-white border border-gray-200 shadow-sm';
  const inputBg = isDark ? 'bg-white/5 border-white/10 text-white' : 'bg-white border-gray-200 text-gray-900';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  // State - Content Format
  const [contentFormat, setContentFormat] = useState<ContentFormatType>('post');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('instagram');
  const [topic, setTopic] = useState('');
  const [selectedPostType, setSelectedPostType] = useState<string>('educational');

  // State - Format Options
  const [numSlides, setNumSlides] = useState(7);
  const [durationSeconds, setDurationSeconds] = useState(30);
  const [videoStyle, setVideoStyle] = useState('educational');
  const [musicMood, setMusicMood] = useState('upbeat');

  // State - Brand & Advanced
  const [brandContext, setBrandContext] = useState<string | null>(null);
  const [sector, setSector] = useState('tech');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // State - Generation
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<GeneratedFormatContent | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [expandedSlide, setExpandedSlide] = useState<number | null>(null);

  // Load Brand Context
  useEffect(() => {
    const loadBrand = async () => {
      try {
        const ctx = await BrandContextAPI.getContext();
        setBrandContext(ctx);
      } catch {
        console.warn('Brand context not available');
      }
    };
    loadBrand();
  }, []);

  // Update defaults when format changes
  useEffect(() => {
    const defaults = getFormatDefaults(contentFormat);
    if (defaults.slides) setNumSlides(defaults.slides);
    if (defaults.duration) setDurationSeconds(defaults.duration);
  }, [contentFormat]);

  // Get current templates
  const currentTemplates = SOCIAL_QUICK_TEMPLATES.slice(0, 8);

  // Copy to clipboard
  const handleCopy = useCallback((text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
    toast.success('Copiato negli appunti!');
  }, []);

  // Generate Content
  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error('Inserisci un argomento');
      return;
    }

    setIsGenerating(true);
    setGeneratedContent(null);

    try {
      // Brand context is already a formatted string from the API
      const brandInfo = brandContext || '';

      // Call POWER endpoint
      const response = await fetch('/api/v1/copilot/marketing/generate-format', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
        body: JSON.stringify({
          content_format: contentFormat,
          post_type: selectedPostType,
          platform: selectedPlatform,
          topic,
          sector,
          num_slides: numSlides,
          duration_seconds: durationSeconds,
          video_style: videoStyle,
          music_mood: musicMood,
          generate_image_prompts: true,
          include_stickers: true,
          include_music: true,
          brand_context: brandInfo,
          language: 'it',
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Errore nella generazione');
      }

      const data: FormatGenerationResult = await response.json();

      setGeneratedContent({
        format: data.content_format as ContentFormatType,
        mainContent: data.main_content,
        caption: data.caption,
        slides: data.slides || [],
        scenes: data.scenes || [],
        hashtags: data.hashtags || [],
        ctaOptions: data.cta_options || [],
        coverImagePrompt: data.cover_image_prompt,
        platform: data.metadata?.platform || selectedPlatform,
      });

      const formatLabel = CONTENT_FORMATS[contentFormat]?.label || contentFormat;
      toast.success(`✨ ${formatLabel} generato con successo!`);
    } catch (error) {
      console.error('Generation error:', error);
      toast.error(`Errore: ${error instanceof Error ? error.message : 'Generazione fallita'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // Format-specific platforms
  const availablePlatforms = SOCIAL_PLATFORMS.filter((p) =>
    CONTENT_FORMATS[contentFormat]?.platforms.includes(p.id)
  );

  return (
    <div className="space-y-6">
      {/* Brand DNA Status */}
      {brandContext && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm',
            isDark ? 'bg-gold/10 text-gold' : 'bg-gold/10 text-gold-dark'
          )}
        >
          <Zap className="w-4 h-4" />
          <span>
            ✅ <strong>Brand DNA caricato</strong> - AI personalizzerà i contenuti
          </span>
        </motion.div>
      )}

      {/* 1. Content Format Selection */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={cn(cardBg, 'rounded-2xl p-6')}
      >
        <h2 className={cn('text-xl font-bold mb-4 flex items-center gap-2', textPrimary)}>
          <Sparkles className="w-5 h-5 text-gold" />
          1. Formato Contenuto
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {CONTENT_FORMATS_LIST.map((format) => {
            const Icon = format.icon;
            const isActive = contentFormat === format.id;
            return (
              <button
                key={format.id}
                onClick={() => setContentFormat(format.id)}
                className={cn(
                  'p-4 rounded-xl border-2 transition-all text-left relative overflow-hidden',
                  isActive
                    ? 'border-gold bg-gold/10'
                    : isDark
                      ? 'border-white/10 hover:border-white/20'
                      : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <div
                  className="absolute top-0 right-0 w-16 h-16 rounded-full opacity-10"
                  style={{ backgroundColor: format.color, transform: 'translate(30%, -30%)' }}
                />
                <Icon
                  className={cn('w-6 h-6 mb-2', isActive ? 'text-gold' : textSecondary)}
                  style={{ color: isActive ? format.color : undefined }}
                />
                <div className={cn('font-semibold text-sm', textPrimary)}>{format.label}</div>
                <div className={cn('text-xs mt-1', textSecondary)}>{format.description}</div>
              </button>
            );
          })}
        </div>

        {/* Format Features */}
        <div className="mt-4 flex flex-wrap gap-2">
          {CONTENT_FORMATS[contentFormat]?.features.map((feature, i) => (
            <span
              key={i}
              className={cn(
                'px-2 py-1 rounded-full text-xs',
                isDark ? 'bg-white/5 text-gray-300' : 'bg-gray-100 text-gray-600'
              )}
            >
              ✓ {feature}
            </span>
          ))}
        </div>
      </motion.div>

      {/* 2. Platform Selection */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.05 }}
        className={cn(cardBg, 'rounded-2xl p-6')}
      >
        <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>2. Piattaforma Target</h2>
        <div className="flex flex-wrap gap-3">
          {availablePlatforms.map((platform) => {
            const Icon = platform.icon;
            const isSelected = selectedPlatform === platform.id;
            return (
              <button
                key={platform.id}
                onClick={() => setSelectedPlatform(platform.id)}
                className={cn(
                  'px-4 py-3 rounded-xl border-2 transition-all flex items-center gap-2',
                  isSelected
                    ? 'border-gold bg-gold/10'
                    : isDark
                      ? 'border-white/10 hover:border-white/20'
                      : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <Icon
                  className="w-5 h-5"
                  style={{ color: isSelected ? platform.color : undefined }}
                />
                <span className={cn('font-medium', textPrimary)}>{platform.name}</span>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* 3. Topic & Templates */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className={cn(cardBg, 'rounded-2xl p-6 space-y-4')}
      >
        <h2 className={cn('text-xl font-bold', textPrimary)}>3. Argomento</h2>

        {/* Quick Templates */}
        <div>
          <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
            Template Veloci
          </label>
          <div className="flex flex-wrap gap-2">
            {currentTemplates.map((template) => (
              <button
                key={template.id}
                onClick={() => {
                  setTopic(template.value);
                  if (template.postType) {
                    setSelectedPostType(template.postType);
                  }
                }}
                className={cn(
                  'px-3 py-2 rounded-lg text-sm transition-all',
                  topic === template.value
                    ? 'bg-gold text-black'
                    : isDark
                      ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                )}
              >
                {template.label}
              </button>
            ))}
          </div>
        </div>

        {/* Topic Input */}
        <div>
          <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
            Argomento Personalizzato
          </label>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Es: 5 modi per automatizzare la tua PMI con l'AI..."
            className={cn(
              'w-full px-4 py-3 rounded-xl border min-h-[100px] resize-none focus:ring-2 focus:ring-gold focus:border-gold',
              inputBg
            )}
          />
        </div>
      </motion.div>

      {/* 4. Format-Specific Options */}
      {(formatHasSlides(contentFormat) || formatHasScenes(contentFormat)) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
          className={cn(cardBg, 'rounded-2xl p-6 space-y-4')}
        >
          <h2 className={cn('text-xl font-bold flex items-center gap-2', textPrimary)}>
            <Settings2 className="w-5 h-5 text-gold" />
            4. Opzioni {CONTENT_FORMATS[contentFormat]?.label}
          </h2>

          {/* Slides selector for Story/Carousel */}
          {formatHasSlides(contentFormat) && (
            <div>
              <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
                <Layers className="w-4 h-4 inline mr-1" />
                Numero Slide
              </label>
              <div className="flex flex-wrap gap-2">
                {SLIDES_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setNumSlides(opt.value)}
                    className={cn(
                      'px-4 py-2 rounded-lg text-sm transition-all',
                      numSlides === opt.value
                        ? 'bg-gold text-black font-medium'
                        : isDark
                          ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    )}
                  >
                    {opt.label}
                    <span className={cn('block text-xs', numSlides === opt.value ? 'text-black/70' : textSecondary)}>
                      {opt.description}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Duration selector for Reel/Video */}
          {formatHasScenes(contentFormat) && (
            <>
              <div>
                <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
                  <Clock className="w-4 h-4 inline mr-1" />
                  Durata
                </label>
                <div className="flex flex-wrap gap-2">
                  {DURATION_OPTIONS.filter((d) =>
                    contentFormat === 'reel' ? d.value <= 90 : true
                  ).map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setDurationSeconds(opt.value)}
                      className={cn(
                        'px-4 py-2 rounded-lg text-sm transition-all',
                        durationSeconds === opt.value
                          ? 'bg-gold text-black font-medium'
                          : isDark
                            ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                      )}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Video Style */}
                <div>
                  <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
                    <Palette className="w-4 h-4 inline mr-1" />
                    Stile Video
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {VIDEO_STYLES.map((style) => (
                      <button
                        key={style.id}
                        onClick={() => setVideoStyle(style.id)}
                        className={cn(
                          'px-3 py-2 rounded-lg text-sm transition-all',
                          videoStyle === style.id
                            ? 'bg-gold text-black'
                            : isDark
                              ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                              : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                        )}
                      >
                        {style.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Music Mood */}
                <div>
                  <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
                    <Music className="w-4 h-4 inline mr-1" />
                    Mood Musicale
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {MUSIC_MOODS.map((mood) => (
                      <button
                        key={mood.id}
                        onClick={() => setMusicMood(mood.id)}
                        className={cn(
                          'px-3 py-2 rounded-lg text-sm transition-all',
                          musicMood === mood.id
                            ? 'bg-gold text-black'
                            : isDark
                              ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                              : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                        )}
                      >
                        {mood.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </motion.div>
      )}

      {/* Generate Button */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
        <Button
          onClick={handleGenerate}
          disabled={isGenerating || !topic.trim()}
          className="w-full bg-gradient-to-r from-gold to-amber-500 hover:from-gold/90 hover:to-amber-500/90 text-black font-semibold py-6"
          size="lg"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Generando {CONTENT_FORMATS[contentFormat]?.label}...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 mr-2" />
              Genera {CONTENT_FORMATS[contentFormat]?.label} AI
            </>
          )}
        </Button>
      </motion.div>

      {/* Generated Content Results */}
      <AnimatePresence>
        {generatedContent && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Header */}
            <div className="flex items-center justify-between">
              <h2 className={cn('text-xl font-bold flex items-center gap-2', textPrimary)}>
                <Sparkles className="w-5 h-5 text-gold" />✨{' '}
                {CONTENT_FORMATS[generatedContent.format]?.label} Generato
              </h2>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(generatedContent.mainContent, 'main')}
                >
                  {copied === 'main' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  <span className="ml-1">Copia Tutto</span>
                </Button>
              </div>
            </div>

            {/* Caption */}
            <motion.div className={cn(cardBg, 'rounded-2xl p-6')}>
              <div className="flex items-center justify-between mb-3">
                <h3 className={cn('font-semibold', textPrimary)}>📝 Caption</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(generatedContent.caption, 'caption')}
                >
                  {copied === 'caption' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
              <div className={cn('p-4 rounded-xl whitespace-pre-wrap text-sm', inputBg)}>
                {generatedContent.caption}
              </div>
            </motion.div>

            {/* Slides (Story/Carousel) */}
            {generatedContent.slides.length > 0 && (
              <motion.div className={cn(cardBg, 'rounded-2xl p-6')}>
                <h3 className={cn('font-semibold mb-4 flex items-center gap-2', textPrimary)}>
                  <Layers className="w-5 h-5 text-gold" />
                  📱 Slide ({generatedContent.slides.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {generatedContent.slides.map((slide, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.05 }}
                      className={cn(
                        'rounded-xl border p-4 cursor-pointer transition-all',
                        expandedSlide === idx
                          ? 'ring-2 ring-gold'
                          : isDark
                            ? 'border-white/10 hover:border-white/20'
                            : 'border-gray-200 hover:border-gray-300'
                      )}
                      onClick={() => setExpandedSlide(expandedSlide === idx ? null : idx)}
                    >
                      {/* Slide Header */}
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={cn(
                            'px-2 py-1 rounded-full text-xs font-medium',
                            slide.slide_type === 'hook'
                              ? 'bg-red-500/20 text-red-400'
                              : slide.slide_type === 'cta'
                                ? 'bg-green-500/20 text-green-400'
                                : 'bg-blue-500/20 text-blue-400'
                          )}
                        >
                          {slide.slide_num}. {slide.slide_type.toUpperCase()}
                        </span>
                        {expandedSlide === idx ? (
                          <ChevronUp className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        )}
                      </div>

                      {/* Slide Content */}
                      {slide.title && (
                        <h4 className={cn('font-medium text-sm mb-1', textPrimary)}>{slide.title}</h4>
                      )}
                      <p className={cn('text-sm', textSecondary)}>
                        {slide.content?.slice(0, expandedSlide === idx ? undefined : 80)}
                        {slide.content?.length > 80 && expandedSlide !== idx && '...'}
                      </p>

                      {/* Expanded Details */}
                      <AnimatePresence>
                        {expandedSlide === idx && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-3 pt-3 border-t border-white/10 space-y-2"
                          >
                            {/* Bullets */}
                            {slide.bullets.length > 0 && (
                              <div>
                                <span className={cn('text-xs font-medium', textSecondary)}>Punti:</span>
                                <ul className="list-disc list-inside text-sm mt-1">
                                  {slide.bullets.map((b, i) => (
                                    <li key={i} className={textSecondary}>
                                      {b}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Visual Prompt */}
                            {slide.visual_prompt && (
                              <div>
                                <span className={cn('text-xs font-medium flex items-center gap-1', textSecondary)}>
                                  <ImagePlus className="w-3 h-3" /> Prompt Immagine:
                                </span>
                                <p className={cn('text-xs mt-1 p-2 rounded', inputBg)}>
                                  {slide.visual_prompt.slice(0, 150)}...
                                </p>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="mt-1"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleCopy(slide.visual_prompt || '', `slide-${idx}`);
                                  }}
                                >
                                  {copied === `slide-${idx}` ? (
                                    <Check className="w-3 h-3" />
                                  ) : (
                                    <Copy className="w-3 h-3" />
                                  )}
                                  <span className="ml-1 text-xs">Copia Prompt</span>
                                </Button>
                              </div>
                            )}

                            {/* Stickers */}
                            {slide.stickers.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {slide.stickers.map((s, i) => (
                                  <span
                                    key={i}
                                    className="px-2 py-0.5 rounded-full bg-pink-500/20 text-pink-400 text-xs"
                                  >
                                    {s}
                                  </span>
                                ))}
                              </div>
                            )}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Scenes (Reel/Video) */}
            {generatedContent.scenes.length > 0 && (
              <motion.div className={cn(cardBg, 'rounded-2xl p-6')}>
                <h3 className={cn('font-semibold mb-4 flex items-center gap-2', textPrimary)}>
                  <Film className="w-5 h-5 text-gold" />
                  🎬 Scene ({generatedContent.scenes.length})
                </h3>
                <div className="space-y-3">
                  {generatedContent.scenes.map((scene, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className={cn(
                        'rounded-xl border p-4',
                        isDark ? 'border-white/10' : 'border-gray-200'
                      )}
                    >
                      <div className="flex items-start gap-4">
                        {/* Timestamp */}
                        <div className="flex-shrink-0 text-center">
                          <div
                            className={cn(
                              'w-12 h-12 rounded-full flex items-center justify-center font-bold',
                              scene.slide_type === 'hook' || scene.slide_num === 1
                                ? 'bg-red-500/20 text-red-400'
                                : 'bg-gold/20 text-gold'
                            )}
                          >
                            {scene.slide_num}
                          </div>
                          {scene.text_overlay && (
                            <span className={cn('text-xs mt-1 block', textSecondary)}>
                              {scene.text_overlay}
                            </span>
                          )}
                        </div>

                        {/* Content */}
                        <div className="flex-1">
                          <h4 className={cn('font-medium', textPrimary)}>
                            {scene.title || `Scena ${scene.slide_num}`}
                          </h4>
                          <p className={cn('text-sm mt-1', textSecondary)}>
                            🎤 "{scene.content}"
                          </p>
                          {scene.visual_prompt && (
                            <p className={cn('text-xs mt-2 opacity-70', textSecondary)}>
                              🎬 Visual: {scene.visual_prompt.slice(0, 100)}...
                            </p>
                          )}
                          {scene.music_mood && (
                            <span className="inline-block mt-2 px-2 py-0.5 rounded-full bg-primary/20 text-primary text-xs">
                              🎵 {scene.music_mood}
                            </span>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Cover/Thumbnail Prompt */}
            {generatedContent.coverImagePrompt && (
              <motion.div className={cn(cardBg, 'rounded-2xl p-6')}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className={cn('font-semibold flex items-center gap-2', textPrimary)}>
                    <ImagePlus className="w-5 h-5 text-gold" />
                    🖼️ Prompt {formatHasScenes(generatedContent.format) ? 'Thumbnail' : 'Cover'}
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(generatedContent.coverImagePrompt || '', 'cover')}
                  >
                    {copied === 'cover' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    Copia
                  </Button>
                </div>
                <div className={cn('p-4 rounded-xl text-sm', inputBg)}>
                  {generatedContent.coverImagePrompt}
                </div>
              </motion.div>
            )}

            {/* Hashtags & CTAs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Hashtags */}
              <motion.div className={cn(cardBg, 'rounded-2xl p-6')}>
                <h3 className={cn('font-semibold mb-3', textPrimary)}>#️⃣ Hashtag</h3>
                <div className="flex flex-wrap gap-2">
                  {generatedContent.hashtags.map((tag, i) => (
                    <span
                      key={i}
                      className={cn(
                        'px-2 py-1 rounded text-sm cursor-pointer hover:bg-gold/20 transition-colors',
                        isDark ? 'bg-white/10 text-gray-300' : 'bg-gray-100 text-gray-600'
                      )}
                      onClick={() => handleCopy(tag, `tag-${i}`)}
                    >
                      {tag.startsWith('#') ? tag : `#${tag}`}
                    </span>
                  ))}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="mt-3"
                  onClick={() => handleCopy(generatedContent.hashtags.join(' '), 'all-tags')}
                >
                  <Copy className="w-3 h-3 mr-1" />
                  Copia tutti
                </Button>
              </motion.div>

              {/* CTAs */}
              <motion.div className={cn(cardBg, 'rounded-2xl p-6')}>
                <h3 className={cn('font-semibold mb-3', textPrimary)}>🎯 CTA Suggerite</h3>
                <div className="space-y-2">
                  {generatedContent.ctaOptions.map((cta, i) => (
                    <div
                      key={i}
                      className={cn(
                        'p-3 rounded-lg text-sm cursor-pointer hover:bg-gold/10 transition-colors flex items-center justify-between',
                        isDark ? 'bg-white/5' : 'bg-gray-50'
                      )}
                      onClick={() => handleCopy(cta, `cta-${i}`)}
                    >
                      <span className={textPrimary}>{cta}</span>
                      {copied === `cta-${i}` ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <Copy className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default PowerContentGenerator;
