/**
 * SocialPublisherPro Component
 * Multi-platform social media publishing with scheduling, media upload, and AI optimization
 *
 * @uses constants/image-sizes - Dimensioni immagini social centralizzate
 * @uses constants/quick-templates - Template AI centralizzati
 * @uses types/social.types - Types centralizzati
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
  Loader2,
  Send,
  Calendar,
  Image as ImageIcon,
  X,
  CheckCircle2,
  AlertCircle,
  Clock,
  Upload,
  Sparkles,
  RefreshCw,
  Eye,
  Trash2,
  Link2,
  Hash,
  Wand2,
  Zap,
  ImagePlus,
  Palette,
  AtSign,
} from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { BrandContextAPI } from '../api/brandContext';

// Costanti e Types centralizzati
import { SOCIAL_IMAGE_SIZES } from '../constants/image-sizes';
import { SOCIAL_QUICK_TEMPLATES } from '../constants/quick-templates';
import type { SocialPlatform, ScheduledPost, PublishResult } from '../types/social.types';

// Re-export per compatibilità
type Platform = SocialPlatform;

// API Service inline
const SocialApiService = {
  baseUrl: '/api/v1',

  async getPlatforms(): Promise<Platform[]> {
    const res = await fetch(`${this.baseUrl}/social/platforms`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
    });
    if (!res.ok) throw new Error('Failed to get platforms');
    const data = await res.json();
    return data.platforms || [];
  },

  async publish(content: string, platforms: string[], mediaUrls?: string[]): Promise<PublishResult[]> {
    const res = await fetch(`${this.baseUrl}/social/publish`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify({ content, platforms, media_urls: mediaUrls }),
    });
    if (!res.ok) throw new Error('Failed to publish');
    const data = await res.json();
    return data.results || [];
  },

  async schedule(
    content: string,
    platforms: string[],
    scheduleTime: string,
    mediaUrls?: string[]
  ): Promise<{ scheduled_id: string }> {
    const res = await fetch(`${this.baseUrl}/social/schedule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify({
        content,
        platforms,
        schedule_time: scheduleTime,
        media_urls: mediaUrls,
      }),
    });
    if (!res.ok) throw new Error('Failed to schedule');
    return res.json();
  },

  async cancelScheduled(scheduledId: string): Promise<void> {
    const res = await fetch(`${this.baseUrl}/social/scheduled/${scheduledId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
    });
    if (!res.ok) throw new Error('Failed to cancel');
  },

  async uploadMedia(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${this.baseUrl}/social/upload-media`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload');
    return res.json();
  },

  async optimizeContent(content: string, platform: string): Promise<{ optimized: string }> {
    const res = await fetch(`${this.baseUrl}/marketing/optimize-for-platform`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
      },
      body: JSON.stringify({ content, platform }),
    });
    if (!res.ok) return { optimized: content };
    return res.json();
  },
};

// Usa SOCIAL_QUICK_TEMPLATES centralizzato
const QUICK_TEMPLATES = SOCIAL_QUICK_TEMPLATES;

// Usa SOCIAL_IMAGE_SIZES centralizzato
const IMAGE_SIZES = SOCIAL_IMAGE_SIZES;

// Default platforms
const DEFAULT_PLATFORMS: Platform[] = [
  {
    id: 'facebook',
    label: 'Facebook',
    icon: Facebook,
    color: '#D4AF37',
    bgColor: 'rgba(24, 119, 242, 0.1)',
    configured: false,
    maxChars: 63206,
    features: ['text', 'image', 'video', 'link'],
  },
  {
    id: 'instagram',
    label: 'Instagram',
    icon: Instagram,
    color: '#B8963A',
    bgColor: 'rgba(228, 64, 95, 0.1)',
    configured: false,
    maxChars: 2200,
    features: ['image', 'video', 'reels'],
  },
  {
    id: 'linkedin',
    label: 'LinkedIn',
    icon: Linkedin,
    color: '#9A7D30',
    bgColor: 'rgba(10, 102, 194, 0.1)',
    configured: false,
    maxChars: 3000,
    features: ['text', 'image', 'video', 'link', 'document'],
  },
  {
    id: 'twitter',
    label: 'X (Twitter)',
    icon: Twitter,
    color: '#000000',
    bgColor: 'rgba(0, 0, 0, 0.1)',
    configured: false,
    maxChars: 280,
    features: ['text', 'image', 'video', 'poll'],
  },
];

export default function SocialPublisherPro() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const fileInputRef = useRef<HTMLInputElement>(null);

  // State
  const [platforms, setPlatforms] = useState<Platform[]>(DEFAULT_PLATFORMS);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [content, setContent] = useState('');
  const [mediaFiles, setMediaFiles] = useState<{ file: File; preview: string }[]>([]);
  const [uploadedUrls, setUploadedUrls] = useState<string[]>([]);
  const [isPublishing, setIsPublishing] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [publishResults, setPublishResults] = useState<PublishResult[]>([]);
  const [showScheduler, setShowScheduler] = useState(false);
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [hashtagInput, setHashtagInput] = useState('');
  const [mentions, setMentions] = useState<string[]>([]);
  const [mentionInput, setMentionInput] = useState('');
  const [loadingPlatforms, setLoadingPlatforms] = useState(true);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [imagePrompt, setImagePrompt] = useState('');
  const [showImageGenerator, setShowImageGenerator] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<{ platform: string; url: string }[]>([]);

  // Styles
  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-[#1A1A1A] border-gray-600 text-white placeholder-gray-400'
    : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400';

  // Load platforms on mount
  useEffect(() => {
    loadPlatforms();
  }, []);

  const loadPlatforms = async () => {
    setLoadingPlatforms(true);
    try {
      const data = await SocialApiService.getPlatforms();
      if (data.length > 0) {
        setPlatforms(
          DEFAULT_PLATFORMS.map((p) => ({
            ...p,
            configured: data.some((d: any) => d.id === p.id && d.configured),
          }))
        );
      }
    } catch (error) {
      console.error('Error loading platforms:', error);
    } finally {
      setLoadingPlatforms(false);
    }
  };

  // Toggle platform selection
  const togglePlatform = (platformId: string) => {
    const platform = platforms.find((p) => p.id === platformId);
    if (!platform?.configured) {
      toast.error(`${platform?.label} non è configurato. Aggiungi le credenziali API.`);
      return;
    }
    setSelectedPlatforms((prev) =>
      prev.includes(platformId) ? prev.filter((p) => p !== platformId) : [...prev, platformId]
    );
  };

  // Character count for selected platforms
  const getMinMaxChars = useCallback(() => {
    const selected = platforms.filter((p) => selectedPlatforms.includes(p.id));
    if (selected.length === 0) return { min: 0, max: Infinity };
    return {
      min: Math.min(...selected.map((p) => p.maxChars)),
      max: Math.max(...selected.map((p) => p.maxChars)),
    };
  }, [platforms, selectedPlatforms]);

  const charLimit = getMinMaxChars();
  // Build final content with mentions and hashtags
  const mentionsText = mentions.length > 0 ? mentions.map((m) => `@${m}`).join(' ') + '\n\n' : '';
  const hashtagsText = hashtags.length > 0 ? '\n\n' + hashtags.map((h) => `#${h}`).join(' ') : '';
  const contentWithHashtags = mentionsText + content + hashtagsText;
  const charCount = contentWithHashtags.length;
  const isOverLimit = charCount > charLimit.min;

  // Handle file selection
  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`${file.name} è troppo grande (max 10MB)`);
        return;
      }

      const preview = URL.createObjectURL(file);
      setMediaFiles((prev) => [...prev, { file, preview }]);
    });
  }, []);

  // Remove media file
  const removeMedia = (index: number) => {
    setMediaFiles((prev) => {
      URL.revokeObjectURL(prev[index].preview);
      return prev.filter((_, i) => i !== index);
    });
  };

  // Upload all media files
  const uploadAllMedia = async (): Promise<string[]> => {
    if (mediaFiles.length === 0) return [];

    setIsUploading(true);
    const urls: string[] = [];

    try {
      for (const { file } of mediaFiles) {
        const result = await SocialApiService.uploadMedia(file);
        urls.push(result.url);
      }
      setUploadedUrls(urls);
      toast.success(`${urls.length} file caricati`);
      return urls;
    } catch (error) {
      toast.error('Errore nel caricamento media');
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  // Add hashtag
  const addHashtag = () => {
    const tag = hashtagInput.trim().replace(/^#/, '');
    if (tag && !hashtags.includes(tag)) {
      setHashtags((prev) => [...prev, tag]);
      setHashtagInput('');
    }
  };

  // Remove hashtag
  const removeHashtag = (tag: string) => {
    setHashtags((prev) => prev.filter((h) => h !== tag));
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

  // AI optimize content
  const optimizeContent = async () => {
    if (!content.trim()) {
      toast.error('Inserisci prima il contenuto');
      return;
    }

    setIsOptimizing(true);
    try {
      // Optimize for the most restrictive platform
      const targetPlatform = selectedPlatforms[0] || 'linkedin';
      const result = await SocialApiService.optimizeContent(content, targetPlatform);
      setContent(result.optimized);
      toast.success('Contenuto ottimizzato con AI');
    } catch (error) {
      toast.error('Errore ottimizzazione');
    } finally {
      setIsOptimizing(false);
    }
  };

  // 🎨 GENERATE AI IMAGES FOR SELECTED PLATFORMS
  const generateAIImages = async () => {
    if (!imagePrompt.trim()) {
      toast.error('Inserisci una descrizione per l\'immagine');
      return;
    }

    if (selectedPlatforms.length === 0) {
      toast.error('Seleziona almeno una piattaforma');
      return;
    }

    setIsGeneratingImage(true);
    const newImages: { platform: string; url: string }[] = [];

    try {
      // Generate image for each selected platform with correct dimensions
      for (const platformId of selectedPlatforms) {
        const size = IMAGE_SIZES[platformId] || IMAGE_SIZES.instagram;

        const res = await fetch('/api/v1/copilot/image/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
          },
          body: JSON.stringify({
            prompt: imagePrompt,
            style: 'professional',
            platform: platformId,
            width: size.width,
            height: size.height,
            apply_branding: true,
            branding_position: 'top_center',
            post_type: 'lancio_prodotto',
            sector: 'tech',
          }),
        });

        if (res.ok) {
          const data = await res.json();
          if (data.image_url) {
            newImages.push({ platform: platformId, url: data.image_url });
          }
        }
      }

      if (newImages.length > 0) {
        setGeneratedImages(newImages);
        // Add first image to media files
        setUploadedUrls(newImages.map(img => img.url));
        toast.success(`✨ ${newImages.length} immagini generate per ${selectedPlatforms.length} social!`);
      } else {
        toast.error('Errore nella generazione immagini');
      }
    } catch (error) {
      console.error('Image generation error:', error);
      toast.error('Errore nella generazione');
    } finally {
      setIsGeneratingImage(false);
      setShowImageGenerator(false);
    }
  };

  // 🚀 GENERATE CONTENT FROM TEMPLATE WITH AI + BRAND DNA
  const generateFromTemplate = async (templateValue: string) => {
    setIsGeneratingAI(true);
    setSelectedTemplate(templateValue);

    try {
      // Fetch Brand DNA context for personalization
      const brandContext = await BrandContextAPI.getContext();

      const targetPlatform = selectedPlatforms[0] || 'linkedin';
      const res = await fetch('/api/v1/copilot/marketing/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
        body: JSON.stringify({
          topic: templateValue,
          type: 'social',
          subtype: 'post',
          post_type: 'lancio_prodotto', // Use specific post_type for PRO!
          platform: targetPlatform,
          tone: 'professional',
          length: 'medium',
          include_hashtags: true,
          include_emoji: true,
          sector: 'tech',
          brand_context: brandContext ? JSON.stringify(brandContext) : '', // 🧬 Inject Brand DNA
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setContent(data.content || '');
        toast.success('✨ Contenuto generato con AI!');
      } else {
        throw new Error('Generation failed');
      }
    } catch (error) {
      console.error('AI generation error:', error);
      // Fallback template
      setContent(`🚀 ${templateValue}\n\nStudioCentOS ti aiuta a digitalizzare il tuo business!\n\n💼 Soluzioni su misura per PMI\n📱 App, Web, AI\n\n👉 Contattaci: studiocentos.it\n\n#PMI #Digitalizzazione #StudioCentOS`);
      toast.success('Contenuto generato (template)');
    } finally {
      setIsGeneratingAI(false);
      setSelectedTemplate(null);
    }
  };

  // Publish now
  const handlePublish = async () => {
    if (selectedPlatforms.length === 0) {
      toast.error('Seleziona almeno una piattaforma');
      return;
    }

    if (!content.trim()) {
      toast.error('Inserisci il contenuto');
      return;
    }

    setIsPublishing(true);
    setPublishResults([]);

    try {
      // Upload media first if any
      const mediaUrls = mediaFiles.length > 0 ? await uploadAllMedia() : uploadedUrls;

      // Publish
      const results = await SocialApiService.publish(contentWithHashtags, selectedPlatforms, mediaUrls);
      setPublishResults(results);

      const successCount = results.filter((r) => r.success).length;
      const failCount = results.filter((r) => !r.success).length;

      if (successCount > 0) {
        toast.success(`Pubblicato su ${successCount} piattaforme!`);
      }
      if (failCount > 0) {
        toast.error(`Errore su ${failCount} piattaforme`);
      }

      // Clear form on full success
      if (failCount === 0) {
        setContent('');
        setMediaFiles([]);
        setUploadedUrls([]);
        setHashtags([]);
        setSelectedPlatforms([]);
      }
    } catch (error) {
      console.error('Publish error:', error);
      toast.error('Errore di pubblicazione');
    } finally {
      setIsPublishing(false);
    }
  };

  // Schedule post
  const handleSchedule = async () => {
    if (selectedPlatforms.length === 0) {
      toast.error('Seleziona almeno una piattaforma');
      return;
    }

    if (!content.trim()) {
      toast.error('Inserisci il contenuto');
      return;
    }

    if (!scheduleDate || !scheduleTime) {
      toast.error('Seleziona data e ora');
      return;
    }

    const scheduledDateTime = new Date(`${scheduleDate}T${scheduleTime}`);
    if (scheduledDateTime <= new Date()) {
      toast.error('La data deve essere nel futuro');
      return;
    }

    setIsPublishing(true);

    try {
      const mediaUrls = mediaFiles.length > 0 ? await uploadAllMedia() : uploadedUrls;

      const result = await SocialApiService.schedule(
        contentWithHashtags,
        selectedPlatforms,
        scheduledDateTime.toISOString(),
        mediaUrls
      );

      // Add to scheduled posts
      setScheduledPosts((prev) => [
        ...prev,
        {
          id: result.scheduled_id,
          content: contentWithHashtags,
          platforms: selectedPlatforms,
          scheduledTime: scheduledDateTime,
          status: 'pending',
          mediaUrls,
        },
      ]);

      toast.success('Post programmato!');
      setShowScheduler(false);
      setContent('');
      setMediaFiles([]);
      setUploadedUrls([]);
      setHashtags([]);
      setSelectedPlatforms([]);
      setScheduleDate('');
      setScheduleTime('');
    } catch (error) {
      toast.error('Errore nella programmazione');
    } finally {
      setIsPublishing(false);
    }
  };

  // Cancel scheduled post
  const cancelScheduledPost = async (id: string) => {
    try {
      await SocialApiService.cancelScheduled(id);
      setScheduledPosts((prev) => prev.filter((p) => p.id !== id));
      toast.success('Post cancellato');
    } catch (error) {
      toast.error('Errore nella cancellazione');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-2xl font-bold ${textPrimary}`}>Social Publisher Pro</h2>
          <p className={`${textSecondary} mt-1`}>
            Pubblica e programma contenuti su più piattaforme
          </p>
        </div>
        <Button
          variant="outline"
          onClick={loadPlatforms}
          disabled={loadingPlatforms}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loadingPlatforms ? 'animate-spin' : ''}`} />
          Aggiorna
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Editor */}
        <div className={`lg:col-span-2 ${cardBg} rounded-2xl p-6 space-y-6`}>
          {/* Platform Selection */}
          <div>
            <label className={`block text-sm font-medium mb-3 ${textSecondary}`}>
              Piattaforme
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {platforms.map((platform) => {
                const Icon = platform.icon;
                const isSelected = selectedPlatforms.includes(platform.id);
                const isConfigured = platform.configured;

                return (
                  <motion.button
                    key={platform.id}
                    whileHover={{ scale: isConfigured ? 1.02 : 1 }}
                    whileTap={{ scale: isConfigured ? 0.98 : 1 }}
                    onClick={() => togglePlatform(platform.id)}
                    disabled={!isConfigured}
                    className={`
                      relative p-4 rounded-xl border-2 transition-all duration-200
                      ${isSelected
                        ? 'border-gold bg-gold/10'
                        : isDark
                          ? 'border-gray-600 hover:border-gray-500 bg-[#1A1A1A]/50'
                          : 'border-gray-200 hover:border-gray-300 bg-gray-50'
                      }
                      ${!isConfigured ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                  >
                    <Icon
                      className="w-8 h-8 mb-2 mx-auto"
                      style={{ color: isSelected ? platform.color : undefined }}
                    />
                    <div className={`text-sm font-medium ${textPrimary}`}>{platform.label}</div>
                    <div className={`text-xs ${textSecondary} mt-1`}>
                      {isConfigured ? `Max ${platform.maxChars} char` : 'Non configurato'}
                    </div>

                    {!isConfigured && (
                      <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-xl">
                        <AlertCircle className="w-6 h-6 text-gold" />
                      </div>
                    )}

                    {isSelected && (
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-gold rounded-full flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </motion.button>
                );
              })}
            </div>
          </div>

          {/* 🚀 TEMPLATE VELOCI - GENERA CON 1 CLICK */}
          <div>
            <label className={`block text-sm font-medium mb-3 ${textSecondary}`}>
              ⚡ Template Veloci - Genera con AI
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {QUICK_TEMPLATES.map((template) => (
                <motion.button
                  key={template.value}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => generateFromTemplate(template.value)}
                  disabled={isGeneratingAI}
                  className={`
                    p-3 rounded-xl border transition-all text-left
                    ${selectedTemplate === template.value
                      ? 'border-gold bg-gold/20'
                      : isDark
                        ? 'border-gray-600 hover:border-gold/50 bg-[#1A1A1A]/50'
                        : 'border-gray-200 hover:border-gold/50 bg-gray-50'
                    }
                    ${isGeneratingAI && selectedTemplate === template.value ? 'animate-pulse' : ''}
                  `}
                >
                  <div className="flex items-center gap-2">
                    {isGeneratingAI && selectedTemplate === template.value ? (
                      <Loader2 className="w-4 h-4 animate-spin text-gold" />
                    ) : (
                      <Wand2 className="w-4 h-4 text-gold" />
                    )}
                    <span className={`text-sm font-medium ${textPrimary}`}>{template.label}</span>
                  </div>
                </motion.button>
              ))}
            </div>
            {isGeneratingAI && (
              <p className={`text-xs mt-2 ${textSecondary}`}>
                ✨ Generando contenuto con AI...
              </p>
            )}
          </div>

          {/* Content Editor */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className={`block text-sm font-medium ${textSecondary}`}>Contenuto</label>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={optimizeContent}
                  disabled={isOptimizing || !content.trim()}
                  className="flex items-center gap-1 text-gold"
                >
                  {isOptimizing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  Ottimizza con AI
                </Button>
                <span className={`text-sm ${isOverLimit ? 'text-gray-400' : textSecondary}`}>
                  {charCount}
                  {selectedPlatforms.length > 0 && ` / ${charLimit.min}`}
                </span>
              </div>
            </div>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Scrivi il tuo post..."
              rows={6}
              className={`w-full rounded-xl p-4 resize-none focus:ring-2 focus:ring-gold ${inputBg} border`}
            />
          </div>

          {/* Hashtags */}
          <div>
            <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>Hashtag</label>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex-1 relative">
                <Hash className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${textSecondary}`} />
                <input
                  type="text"
                  value={hashtagInput}
                  onChange={(e) => setHashtagInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addHashtag()}
                  placeholder="Aggiungi hashtag..."
                  className={`w-full pl-9 pr-4 py-2 rounded-lg ${inputBg} border focus:ring-2 focus:ring-gold`}
                />
              </div>
              <Button onClick={addHashtag} variant="outline" size="sm">
                Aggiungi
              </Button>
            </div>
            {hashtags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {hashtags.map((tag) => (
                  <span
                    key={tag}
                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${isDark ? 'bg-gold/20 text-gold/80' : 'bg-gold/10 text-gold'
                      }`}
                  >
                    #{tag}
                    <button onClick={() => removeHashtag(tag)} className="hover:text-gray-400">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Mentions / Tag Persone */}
          <div>
            <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
              Tag Persone / Account
            </label>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex-1 relative">
                <AtSign className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${textSecondary}`} />
                <input
                  type="text"
                  value={mentionInput}
                  onChange={(e) => setMentionInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addMention()}
                  placeholder="@username da taggare..."
                  className={`w-full pl-9 pr-4 py-2 rounded-lg ${inputBg} border focus:ring-2 focus:ring-gold`}
                />
              </div>
              <Button onClick={addMention} variant="outline" size="sm">
                Aggiungi
              </Button>
            </div>
            <p className={`text-xs mb-2 ${textSecondary}`}>
              💡 Inserisci username senza @ (es: studiocentos, nomeutente)
            </p>
            {mentions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {mentions.map((mention) => (
                  <span
                    key={mention}
                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${isDark ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-100 text-blue-600'
                      }`}
                  >
                    @{mention}
                    <button onClick={() => removeMention(mention)} className="hover:text-gray-400">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Media Upload & AI Generation */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className={`block text-sm font-medium ${textSecondary}`}>Media</label>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowImageGenerator(!showImageGenerator)}
                className="flex items-center gap-1 text-gold"
              >
                <ImagePlus className="w-4 h-4" />
                Genera con AI
              </Button>
            </div>

            {/* 🎨 AI Image Generator Panel */}
            <AnimatePresence>
              {showImageGenerator && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className={`mb-4 p-4 rounded-xl ${isDark ? 'bg-gold/10 border border-gold/20' : 'bg-gold/5 border border-gold/20'}`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Palette className="w-5 h-5 text-gold" />
                    <h4 className={`font-semibold ${textPrimary}`}>Genera Immagine AI per ogni Social</h4>
                  </div>

                  <p className={`text-xs mb-3 ${textSecondary}`}>
                    L'AI creerà immagini con le dimensioni perfette per ogni social selezionato:
                    {selectedPlatforms.map(p => ` ${IMAGE_SIZES[p]?.label || p}`).join(', ') || ' (seleziona piattaforme)'}
                  </p>

                  <textarea
                    value={imagePrompt}
                    onChange={(e) => setImagePrompt(e.target.value)}
                    placeholder="Descrivi l'immagine da generare..."
                    rows={3}
                    className={`w-full rounded-xl p-3 resize-none focus:ring-2 focus:ring-gold ${inputBg} border mb-3`}
                  />

                  <Button
                    onClick={generateAIImages}
                    disabled={isGeneratingImage || !imagePrompt.trim() || selectedPlatforms.length === 0}
                    className="w-full bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
                  >
                    {isGeneratingImage ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generando {selectedPlatforms.length} immagini...
                      </>
                    ) : (
                      <>
                        <ImagePlus className="w-4 h-4 mr-2" />
                        Genera Immagini ({selectedPlatforms.length} social)
                      </>
                    )}
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Generated Images Preview */}
            {generatedImages.length > 0 && (
              <div className={`mb-4 p-3 rounded-xl ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                <p className={`text-xs mb-2 ${textSecondary}`}>✨ Immagini generate:</p>
                <div className="flex flex-wrap gap-2">
                  {generatedImages.map((img, idx) => (
                    <div key={idx} className="relative">
                      <img src={img.url} alt={img.platform} className="w-16 h-16 rounded-lg object-cover" />
                      <span className={`absolute bottom-0 left-0 right-0 text-center text-xs bg-black/50 text-white rounded-b-lg py-0.5`}>
                        {img.platform}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*,video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className={`
                  w-24 h-24 rounded-xl border-2 border-dashed flex flex-col items-center justify-center gap-1
                  transition-colors
                  ${isDark
                    ? 'border-gray-600 hover:border-gray-500 text-gray-400'
                    : 'border-gray-300 hover:border-gray-400 text-gray-400'
                  }
                `}
              >
                {isUploading ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  <>
                    <Upload className="w-6 h-6" />
                    <span className="text-xs">Carica</span>
                  </>
                )}
              </button>

              {mediaFiles.map((media, index) => (
                <div key={index} className="relative w-24 h-24 rounded-xl overflow-hidden group">
                  <img
                    src={media.preview}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                  <button
                    onClick={() => removeMedia(index)}
                    className="absolute top-1 right-1 w-6 h-6 bg-gray-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-4 h-4 text-white" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={handlePublish}
              disabled={isPublishing || selectedPlatforms.length === 0 || !content.trim()}
              className="flex-1 bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
            >
              {isPublishing ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Pubblicando...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Pubblica Ora
                </>
              )}
            </Button>

            <Button
              variant="outline"
              onClick={() => setShowScheduler(!showScheduler)}
              className="flex items-center gap-2"
            >
              <Calendar className="w-5 h-5" />
              Programma
            </Button>

            <Button
              variant="outline"
              onClick={() => setShowPreview(!showPreview)}
              className="flex items-center gap-2"
            >
              <Eye className="w-5 h-5" />
              Anteprima
            </Button>
          </div>

          {/* Scheduler */}
          <AnimatePresence>
            {showScheduler && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className={`rounded-xl p-4 ${isDark ? 'bg-[#1A1A1A]/50' : 'bg-gray-50'}`}
              >
                <h4 className={`font-semibold mb-3 ${textPrimary}`}>Programma Pubblicazione</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className={`block text-sm mb-1 ${textSecondary}`}>Data</label>
                    <input
                      type="date"
                      value={scheduleDate}
                      onChange={(e) => setScheduleDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className={`w-full rounded-lg p-2 ${inputBg} border focus:ring-2 focus:ring-gold`}
                    />
                  </div>
                  <div>
                    <label className={`block text-sm mb-1 ${textSecondary}`}>Ora</label>
                    <input
                      type="time"
                      value={scheduleTime}
                      onChange={(e) => setScheduleTime(e.target.value)}
                      className={`w-full rounded-lg p-2 ${inputBg} border focus:ring-2 focus:ring-gold`}
                    />
                  </div>
                </div>
                <Button
                  onClick={handleSchedule}
                  disabled={isPublishing || !scheduleDate || !scheduleTime}
                  className="w-full mt-3 bg-gold hover:bg-gold/90"
                >
                  <Clock className="w-4 h-4 mr-2" />
                  Conferma Programmazione
                </Button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Preview */}
          <AnimatePresence>
            {showPreview && content.trim() && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className={`rounded-xl p-4 ${isDark ? 'bg-[#1A1A1A]/50' : 'bg-gray-50'}`}
              >
                <h4 className={`font-semibold mb-3 ${textPrimary}`}>Anteprima Post</h4>
                <div className="space-y-3">
                  {selectedPlatforms.map((platformId) => {
                    const platform = platforms.find((p) => p.id === platformId);
                    if (!platform) return null;
                    const Icon = platform.icon;

                    return (
                      <div
                        key={platformId}
                        className={`p-3 rounded-lg border ${isDark ? 'border-gray-600 bg-[#1A1A1A]' : 'border-gray-200 bg-white'
                          }`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <Icon className="w-5 h-5" style={{ color: platform.color }} />
                          <span className={`font-medium ${textPrimary}`}>{platform.label}</span>
                        </div>
                        <p className={`text-sm whitespace-pre-wrap ${textPrimary}`}>
                          {contentWithHashtags.slice(0, platform.maxChars)}
                          {contentWithHashtags.length > platform.maxChars && '...'}
                        </p>
                        {mediaFiles.length > 0 && (
                          <div className="flex gap-2 mt-2">
                            {mediaFiles.slice(0, 4).map((media, i) => (
                              <img
                                key={i}
                                src={media.preview}
                                alt=""
                                className="w-12 h-12 rounded object-cover"
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Publish Results */}
          <AnimatePresence>
            {publishResults.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-2"
              >
                <h4 className={`font-semibold ${textPrimary}`}>Risultati Pubblicazione</h4>
                {publishResults.map((result, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg flex items-center justify-between ${result.success
                      ? 'bg-gold/10 border border-gold/20'
                      : 'bg-gray-500/10 border border-gray-500/20'
                      }`}
                  >
                    <div className="flex items-center gap-2">
                      {result.success ? (
                        <CheckCircle2 className="w-5 h-5 text-gold" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-gray-400" />
                      )}
                      <span className={`font-medium ${textPrimary}`}>{result.platform}</span>
                    </div>
                    {result.postUrl && (
                      <a
                        href={result.postUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gold hover:underline flex items-center gap-1"
                      >
                        <Link2 className="w-4 h-4" />
                        Vedi Post
                      </a>
                    )}
                    {result.error && <span className="text-gray-400 text-sm">{result.error}</span>}
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar - Scheduled Posts */}
        <div className={`${cardBg} rounded-2xl p-6`}>
          <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>Post Programmati</h3>

          {scheduledPosts.length === 0 ? (
            <div className={`text-center py-8 ${textSecondary}`}>
              <Calendar className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Nessun post programmato</p>
            </div>
          ) : (
            <div className="space-y-3">
              {scheduledPosts.map((post) => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`p-3 rounded-lg ${isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-1">
                      {post.platforms.map((pId) => {
                        const platform = platforms.find((p) => p.id === pId);
                        if (!platform) return null;
                        const Icon = platform.icon;
                        return (
                          <Icon
                            key={pId}
                            className="w-4 h-4"
                            style={{ color: platform.color }}
                          />
                        );
                      })}
                    </div>
                    <button
                      onClick={() => cancelScheduledPost(post.id)}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <p className={`text-sm line-clamp-2 mb-2 ${textPrimary}`}>{post.content}</p>
                  <div className={`flex items-center gap-1 text-xs ${textSecondary}`}>
                    <Clock className="w-3 h-3" />
                    {new Date(post.scheduledTime).toLocaleString('it-IT')}
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {/* Quick Stats */}
          <div className={`mt-6 pt-6 border-t ${isDark ? 'border-white/10' : 'border-gray-200'}`}>
            <h4 className={`text-sm font-semibold mb-3 ${textSecondary}`}>Piattaforme Connesse</h4>
            <div className="space-y-2">
              {platforms.map((platform) => {
                const Icon = platform.icon;
                return (
                  <div
                    key={platform.id}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4" style={{ color: platform.color }} />
                      <span className={`text-sm ${textPrimary}`}>{platform.label}</span>
                    </div>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${platform.configured
                        ? 'bg-gold/20 text-gold'
                        : 'bg-gold/20 text-gold'
                        }`}
                    >
                      {platform.configured ? 'Attivo' : 'Da configurare'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
