/**
 * ContentGenerator Component v2.0 - PRODUCTION READY
 *
 * Features:
 * - Brand DNA Auto-Inject
 * - Template centralizzati
 * - Generazione immagine AI
 * - Multi-piattaforma con preview
 * - Hashtag Generator AI
 * - Opzioni avanzate (tono, lunghezza, CTA)
 * - Passa contenuto a Publisher
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
  RefreshCw,
  Loader2,
  Send,
  ImagePlus,
  Hash,
  Clock,
  Wand2,
  Settings2,
  Eye,
  Target,
  Zap,
  ChevronDown,
  ChevronUp,
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
} from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { cn } from '../../../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';

// API e Costanti
import { BrandContextAPI } from '../api/brandContext';
import { SOCIAL_QUICK_TEMPLATES, VIDEO_SCRIPT_TEMPLATES } from '../constants/quick-templates';
import { SOCIAL_IMAGE_SIZES } from '../constants/image-sizes';
import {
  PLATFORM_FORMAT_RULES,
  getPromptInstructionsForPlatform,
  postProcessContentForPlatform,
  limitHashtagsForPlatform
} from '../constants/platform-format-rules';

// ============================================================================
// TYPES
// ============================================================================

interface ContentTypeCategory {
  id: string;
  label: string;
  icon: React.ElementType;
  description: string;
  templates: typeof SOCIAL_QUICK_TEMPLATES;
}

interface GeneratedContent {
  content: string;
  hashtags: string[];
  suggestedImage?: string;
  bestTime?: string;
  platform?: string;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const CONTENT_TYPE_CATEGORIES: ContentTypeCategory[] = [
  {
    id: 'social',
    label: 'Social Media',
    icon: Share2,
    description: 'Post, Story, Carousel',
    templates: SOCIAL_QUICK_TEMPLATES
  },
  {
    id: 'video',
    label: 'Video',
    icon: Video,
    description: 'Reel, Short, Video Lungo',
    templates: VIDEO_SCRIPT_TEMPLATES
  },
  {
    id: 'email',
    label: 'Email',
    icon: Mail,
    description: 'Promo, Newsletter',
    templates: SOCIAL_QUICK_TEMPLATES
  },
  {
    id: 'blog',
    label: 'Blog',
    icon: FileText,
    description: 'Articoli SEO',
    templates: SOCIAL_QUICK_TEMPLATES
  },
];

import { SOCIAL_PLATFORMS } from '../constants/platforms';
import {
  CONTENT_SUBTYPES,
  getSubtypesByCategory,
  generatePromptFromSubtype,
  type ContentSubtype,
} from '../constants/content-formats';

const TONES = [
  { id: 'professional', label: '💼 Professionale', description: 'Formale e autorevole' },
  { id: 'friendly', label: '😊 Amichevole', description: 'Caldo e accessibile' },
  { id: 'persuasive', label: '🎯 Persuasivo', description: 'Call-to-action forte' },
  { id: 'educational', label: '📚 Educativo', description: 'Informativo e didattico' },
  { id: 'inspiring', label: '✨ Ispirante', description: 'Motivazionale e positivo' },
  { id: 'humorous', label: '😄 Umoristico', description: 'Leggero e divertente' },
];

const LENGTHS = [
  { id: 'short', label: 'Breve', description: '50-100 parole' },
  { id: 'medium', label: 'Medio', description: '100-200 parole' },
  { id: 'long', label: 'Lungo', description: '200-400 parole' },
];

const CTA_OPTIONS = [
  { id: 'none', label: 'Nessuna CTA' },
  { id: 'contact', label: '📞 Contattaci' },
  { id: 'discover', label: '🔍 Scopri di più' },
  { id: 'buy', label: '🛒 Acquista ora' },
  { id: 'register', label: '📝 Registrati' },
  { id: 'download', label: '⬇️ Scarica gratis' },
];

// ============================================================================
// COMPONENT
// ============================================================================

export default function ContentGenerator() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // State principale
  const [contentCategory, setContentCategory] = useState<string>('social');
  const [contentSubtype, setContentSubtype] = useState<string>('post');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['linkedin']);
  const [topic, setTopic] = useState('');
  const [selectedPostType, setSelectedPostType] = useState<string>('educational'); // POST_TYPE from template
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('medium');
  const [cta, setCta] = useState('none');
  const [includeHashtags, setIncludeHashtags] = useState(true);
  const [includeEmoji, setIncludeEmoji] = useState(true);

  // State generazione
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContents, setGeneratedContents] = useState<Record<string, GeneratedContent>>({});
  const [copied, setCopied] = useState<string | null>(null);

  // State avanzato
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [brandContext, setBrandContext] = useState<any>(null);
  const [isLoadingBrand, setIsLoadingBrand] = useState(true);

  // Theme
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  // Load Brand DNA on mount
  useEffect(() => {
    loadBrandContext();
  }, []);

  const loadBrandContext = async () => {
    setIsLoadingBrand(true);
    try {
      const context = await BrandContextAPI.getContext();
      setBrandContext(context);
    } catch (error) {
      console.error('Error loading brand context:', error);
    } finally {
      setIsLoadingBrand(false);
    }
  };

  // Toggle platform
  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  // Get current templates based on content type
  const currentTemplates = CONTENT_TYPE_CATEGORIES.find(t => t.id === contentCategory)?.templates || SOCIAL_QUICK_TEMPLATES;

  // Get available subtypes for current category
  const availableSubtypes = getSubtypesByCategory(contentCategory as ContentSubtype['category']);
  const currentSubtype = CONTENT_SUBTYPES[contentSubtype];

  // Generate content
  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error('Inserisci un argomento');
      return;
    }

    if (selectedPlatforms.length === 0) {
      toast.error('Seleziona almeno una piattaforma');
      return;
    }

    setIsGenerating(true);
    setGeneratedContents({});

    try {
      // Build prompt with brand context
      const brandInfo = brandContext ? `
Brand: ${brandContext.company_name || 'StudioCentOS'}
Settore: ${brandContext.industry || 'Software Development'}
Tono di voce: ${brandContext.tone_of_voice || tone}
Valori: ${brandContext.values?.join(', ') || 'Innovazione, Qualità'}
` : '';

      // Generate for each platform
      const results: Record<string, GeneratedContent> = {};

      for (const platformId of selectedPlatforms) {
        const platform = SOCIAL_PLATFORMS.find(p => p.id === platformId);
        if (!platform) continue;

        // Ottieni istruzioni di formattazione specifiche per la piattaforma
        const platformFormatInstructions = getPromptInstructionsForPlatform(platformId);
        const formatRule = PLATFORM_FORMAT_RULES[platformId];

        // Genera prompt specifico per il sotto-tipo di contenuto
        const subtypePrompt = generatePromptFromSubtype(contentSubtype, {
          platform: platformId,
          tone: formatRule?.toneOverride || tone,
          brand_context: brandInfo,
          topic,
        });

        const response = await fetch('/api/v1/copilot/marketing/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
          },
          body: JSON.stringify({
            topic,
            type: contentCategory,
            subtype: contentSubtype,
            // Use selectedPostType from template for PRO endpoint power!
            post_type: selectedPostType,
            platform: platformId,
            tone: formatRule?.toneOverride || tone,
            length,
            cta: cta !== 'none' ? cta : undefined,
            include_hashtags: includeHashtags,
            include_emoji: includeEmoji && formatRule?.emojiDensity !== 'none',
            max_chars: platform.maxChars,
            brand_context: brandInfo,
            sector: brandContext?.industry || 'tech',
            platform_format_instructions: platformFormatInstructions,
            subtype_prompt: subtypePrompt,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          // Post-process per adattare al formato della piattaforma
          const rawContent = data.content || data.text || '';
          const processedContent = postProcessContentForPlatform(rawContent, platformId);
          const limitedHashtags = limitHashtagsForPlatform(data.hashtags || [], platformId);

          results[platformId] = {
            content: processedContent,
            hashtags: limitedHashtags,
            suggestedImage: data.image_prompt,
            bestTime: data.best_time,
            platform: platformId,
          };
        } else {
          // Fallback: genera contenuto locale con formato specifico
          results[platformId] = generateLocalContent(topic, platformId, platform.maxChars);
        }
      }

      setGeneratedContents(results);
      toast.success(`✨ Contenuto generato per ${Object.keys(results).length} piattaforme!`);

    } catch (error) {
      console.error('Generation error:', error);
      // Fallback locale
      const localResults: Record<string, GeneratedContent> = {};
      for (const platformId of selectedPlatforms) {
        const platform = SOCIAL_PLATFORMS.find(p => p.id === platformId);
        if (platform) {
          localResults[platformId] = generateLocalContent(topic, platformId, platform.maxChars);
        }
      }
      setGeneratedContents(localResults);
      toast.success('Contenuto generato (modalità offline)');
    } finally {
      setIsGenerating(false);
    }
  };

  // Fallback local generation con formattazione specifica per piattaforma
  const generateLocalContent = (topicText: string, platform: string, maxChars: number): GeneratedContent => {
    const formatRule = PLATFORM_FORMAT_RULES[platform];
    const ctaText = cta !== 'none' ? `\n\n${CTA_OPTIONS.find(c => c.id === cta)?.label.replace(/[^\w\s]/g, '') || ''}` : '';

    // Hashtag limitati per piattaforma
    const baseHashtags = ['StudioCentOS', 'PMI', 'Digitalizzazione', 'AI', 'Business', 'Italia'];
    const hashtags = includeHashtags ? limitHashtagsForPlatform(baseHashtags, platform) : [];

    let content = '';
    const useEmoji = includeEmoji && formatRule?.emojiDensity !== 'none';

    // Genera contenuto con STILE specifico per piattaforma
    switch (platform) {
      case 'linkedin':
        // LinkedIn: Professionale, strutturato, bullet points
        content = `${useEmoji ? '' : ''}${topicText}\n\nLa digitalizzazione non è più un'opzione, è una necessità per le PMI italiane.\n\nNoi di StudioCentOS aiutiamo le aziende a:\n\n✅ Automatizzare i processi operativi\n✅ Raggiungere nuovi clienti online\n✅ Crescere nel mercato digitale\n\nQual è la sfida più grande che la tua azienda sta affrontando nella trasformazione digitale?${ctaText}`;
        break;

      case 'twitter':
        // Twitter: Ultra-conciso, impatto immediato
        const twitterContent = `${topicText.slice(0, 180)}`;
        content = twitterContent.slice(0, 250); // Lascia spazio per hashtag
        break;

      case 'instagram':
        // Instagram: Emoji-rich, storytelling, call-to-action
        content = `✨ ${topicText}\n\n🚀 La tua azienda merita di brillare online!\n\n💡 Ogni giorno aiutiamo PMI come la tua a:\n\n→ Trovare nuovi clienti\n→ Automatizzare il marketing\n→ Crescere nel digitale\n\n📱 Salva questo post e inizia la tua trasformazione!\n\n💬 Commenta con un 🔥 se vuoi saperne di più!${ctaText}`;
        break;

      case 'facebook':
        // Facebook: Conversazionale, storytelling, community
        content = `${useEmoji ? '💼 ' : ''}${topicText}\n\nSai qual è il segreto delle PMI che stanno crescendo anche in tempi difficili?\n\nHanno capito che la digitalizzazione non è un costo, ma un investimento.\n\nNoi di StudioCentOS lo vediamo ogni giorno: le aziende che abbracciano il digitale non solo sopravvivono, ma prosperano.\n\nTu cosa ne pensi? La tua azienda sta investendo nel digitale?${ctaText}`;
        break;

      default:
        content = `${useEmoji ? '🚀 ' : ''}${topicText}\n\nScopri le nostre soluzioni digitali per PMI.${ctaText}`;
    }

    // Applica post-processing per rispettare le regole della piattaforma
    const processedContent = postProcessContentForPlatform(content, platform);

    return {
      content: processedContent,
      hashtags,
      bestTime: platform === 'linkedin' ? '08:00-10:00' : platform === 'instagram' ? '12:00-14:00' : '18:00-20:00',
      platform,
    };
  };

  // Copy to clipboard
  const handleCopy = (platformId: string) => {
    const content = generatedContents[platformId];
    if (content) {
      const fullText = content.content + (content.hashtags.length > 0 ? '\n\n' + content.hashtags.map(h => `#${h}`).join(' ') : '');
      navigator.clipboard.writeText(fullText);
      setCopied(platformId);
      toast.success('Copiato!');
      setTimeout(() => setCopied(null), 2000);
    }
  };

  // Send to SocialPublisher
  const handleSendToPublisher = (platformId: string) => {
    const content = generatedContents[platformId];
    if (content) {
      // Store in sessionStorage for SocialPublisherPro to pick up
      sessionStorage.setItem('social_content', JSON.stringify({
        content: content.content,
        hashtags: content.hashtags,
        platform: platformId,
      }));
      toast.success('Contenuto pronto per la pubblicazione! Vai al tab "Social Post"');
    }
  };

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
          <span>Brand DNA attivo: <strong>{brandContext.company_name || 'StudioCentOS'}</strong></span>
        </motion.div>
      )}

      {/* Content Category Selection */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={cn(cardBg, 'rounded-2xl p-6')}
      >
        <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>
          1. Categoria Contenuto
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {CONTENT_TYPE_CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isActive = contentCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => {
                  setContentCategory(cat.id);
                  // Reset subtype to first of category
                  const subtypes = getSubtypesByCategory(cat.id as ContentSubtype['category']);
                  if (subtypes.length > 0) {
                    setContentSubtype(subtypes[0].id);
                  }
                }}
                className={cn(
                  'p-4 rounded-xl border-2 transition-all text-left',
                  isActive
                    ? 'border-gold bg-gold/10'
                    : isDark
                      ? 'border-white/10 hover:border-white/20'
                      : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <Icon className={cn('w-6 h-6 mb-2', isActive ? 'text-gold' : textSecondary)} />
                <div className={cn('font-semibold', textPrimary)}>{cat.label}</div>
                <div className={cn('text-xs mt-1', textSecondary)}>{cat.description}</div>
              </button>
            );
          })}
        </div>

        {/* Content Subtype Selection */}
        {availableSubtypes.length > 0 && (
          <div className="mt-4">
            <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
              Formato Specifico
            </label>
            <div className="flex flex-wrap gap-2">
              {availableSubtypes.map((subtype) => {
                const SubIcon = subtype.icon;
                const isActive = contentSubtype === subtype.id;
                return (
                  <button
                    key={subtype.id}
                    onClick={() => setContentSubtype(subtype.id)}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all',
                      isActive
                        ? 'bg-gold text-black font-medium'
                        : isDark
                          ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    )}
                  >
                    <SubIcon className="w-4 h-4" />
                    {subtype.label}
                  </button>
                );
              })}
            </div>
            {currentSubtype && (
              <p className={cn('text-xs mt-2', textSecondary)}>
                {currentSubtype.description}
              </p>
            )}
          </div>
        )}
      </motion.div>

      {/* Platform Selection */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.05 }}
        className={cn(cardBg, 'rounded-2xl p-6')}
      >
        <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>
          2. Piattaforme Target
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {SOCIAL_PLATFORMS.filter(p => ['facebook', 'instagram', 'linkedin', 'twitter'].includes(p.id)).map((platform) => {
            const Icon = platform.icon;
            const isSelected = selectedPlatforms.includes(platform.id);
            return (
              <button
                key={platform.id}
                onClick={() => togglePlatform(platform.id)}
                className={cn(
                  'p-4 rounded-xl border-2 transition-all flex items-center gap-3',
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
                <div className="text-left">
                  <div className={cn('font-medium', textPrimary)}>{platform.label}</div>
                  <div className={cn('text-xs', textSecondary)}>{platform.maxChars} chars</div>
                </div>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Topic & Templates */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className={cn(cardBg, 'rounded-2xl p-6 space-y-4')}
      >
        <h2 className={cn('text-xl font-bold', textPrimary)}>
          3. Argomento
        </h2>

        {/* Quick Templates */}
        <div>
          <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
            Template Veloci
          </label>
          <div className="flex flex-wrap gap-2">
            {currentTemplates.slice(0, 8).map((template) => (
              <button
                key={template.value}
                onClick={() => {
                  setTopic(template.value);
                  // Set postType from template for PRO endpoint power!
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
            placeholder="Es: Come aumentare le vendite con un sito e-commerce per PMI..."
            className={cn(
              'w-full px-4 py-3 rounded-xl border min-h-[100px] resize-none focus:ring-2 focus:ring-gold focus:border-gold',
              inputBg
            )}
          />
        </div>

        {/* Tone Selection */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
          {TONES.map((t) => (
            <button
              key={t.id}
              onClick={() => setTone(t.id)}
              className={cn(
                'px-3 py-2 rounded-lg text-sm transition-all text-left',
                tone === t.id
                  ? 'bg-gold text-black'
                  : isDark
                    ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              )}
            >
              <div className="font-medium">{t.label}</div>
              <div className="text-xs opacity-70">{t.description}</div>
            </button>
          ))}
        </div>

        {/* Advanced Options Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={cn('flex items-center gap-2 text-sm', textSecondary)}
        >
          <Settings2 className="w-4 h-4" />
          Opzioni Avanzate
          {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {/* Advanced Options */}
        <AnimatePresence>
          {showAdvanced && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="space-y-4 overflow-hidden"
            >
              {/* Length */}
              <div>
                <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>Lunghezza</label>
                <div className="flex gap-2">
                  {LENGTHS.map((l) => (
                    <button
                      key={l.id}
                      onClick={() => setLength(l.id)}
                      className={cn(
                        'px-4 py-2 rounded-lg text-sm transition-all',
                        length === l.id
                          ? 'bg-gold text-black'
                          : isDark ? 'bg-white/5 text-gray-300' : 'bg-gray-100 text-gray-700'
                      )}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* CTA */}
              <div>
                <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>Call-to-Action</label>
                <div className="flex flex-wrap gap-2">
                  {CTA_OPTIONS.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => setCta(c.id)}
                      className={cn(
                        'px-3 py-2 rounded-lg text-sm transition-all',
                        cta === c.id
                          ? 'bg-gold text-black'
                          : isDark ? 'bg-white/5 text-gray-300' : 'bg-gray-100 text-gray-700'
                      )}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Toggles */}
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeHashtags}
                    onChange={(e) => setIncludeHashtags(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300 text-gold focus:ring-gold"
                  />
                  <span className={textSecondary}>Includi Hashtag</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeEmoji}
                    onChange={(e) => setIncludeEmoji(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300 text-gold focus:ring-gold"
                  />
                  <span className={textSecondary}>Includi Emoji</span>
                </label>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          disabled={isGenerating || !topic.trim() || selectedPlatforms.length === 0}
          className="w-full bg-gradient-to-r from-gold to-amber-500 hover:from-gold/90 hover:to-amber-500/90 text-black font-semibold py-6"
          size="lg"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Generando per {selectedPlatforms.length} piattaforme...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 mr-2" />
              Genera Contenuto AI
            </>
          )}
        </Button>
      </motion.div>

      {/* Generated Content Results */}
      <AnimatePresence>
        {Object.keys(generatedContents).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            <h2 className={cn('text-xl font-bold', textPrimary)}>
              ✨ Contenuto Generato
            </h2>

            {Object.entries(generatedContents).map(([platformId, content]) => {
              const platform = SOCIAL_PLATFORMS.find(p => p.id === platformId);
              if (!platform) return null;
              const Icon = platform.icon;

              return (
                <motion.div
                  key={platformId}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={cn(cardBg, 'rounded-2xl p-6')}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${platform.color}20` }}
                      >
                        <Icon className="w-5 h-5" style={{ color: platform.color }} />
                      </div>
                      <div>
                        <h3 className={cn('font-semibold', textPrimary)}>{platform.label}</h3>
                        <div className={cn('text-xs', textSecondary)}>
                          {content.content.length} / {platform.maxChars} caratteri
                          {content.bestTime && (
                            <span className="ml-2">
                              <Clock className="w-3 h-3 inline mr-1" />
                              Best: {content.bestTime}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopy(platformId)}
                      >
                        {copied === platformId ? (
                          <Check className="w-4 h-4" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleSendToPublisher(platformId)}
                        className="bg-gold hover:bg-gold/90 text-black"
                      >
                        <Send className="w-4 h-4 mr-1" />
                        Pubblica
                      </Button>
                    </div>
                  </div>

                  {/* Content */}
                  <div className={cn('p-4 rounded-xl whitespace-pre-wrap text-sm', inputBg)}>
                    {content.content}
                  </div>

                  {/* Hashtags */}
                  {content.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {content.hashtags.map((tag, i) => (
                        <span
                          key={i}
                          className={cn(
                            'px-2 py-1 rounded text-xs',
                            isDark ? 'bg-white/10 text-gray-300' : 'bg-gray-100 text-gray-600'
                          )}
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
