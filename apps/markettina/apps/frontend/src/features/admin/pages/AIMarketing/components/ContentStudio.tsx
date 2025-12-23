/**
 * 🚀 CONTENT STUDIO - FLUSSO UNICO POTENTE
 *
 * UN SOLO COMPONENTE per creare TUTTO:
 * - Post social
 * - Video/Reels
 * - Stories
 * - Email
 * - Carousel
 *
 * Con AI per TUTTO:
 * - Generazione testo
 * - Generazione immagini
 * - Adattamento per piattaforma
 * - Scheduling
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, Video, Image, Mail, Layers,
  Sparkles, Wand2, ImagePlus, Send, Clock, Save,
  Check, Copy, RefreshCw, Loader2, ChevronRight,
  Facebook, Instagram, Linkedin, Twitter, Youtube,
  Hash, Calendar, Eye, Edit3, Trash2, Plus,
  Zap, Target, Settings2, MessageCircle, AtSign, User, X
} from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { cn } from '../../../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';

// API e Costanti
import { BrandContextAPI } from '../api/brandContext';
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

type ContentType = 'post' | 'video' | 'story' | 'email' | 'carousel';
type PublishMode = 'now' | 'schedule' | 'draft';

interface Platform {
  id: string;
  name: string;
  icon: React.ElementType;
  color: string;
  width: number;
  height: number;
  aspectRatio: string;
  maxChars: number;
  features: string[];
}

interface GeneratedContent {
  text: string;
  hashtags: string[];
  imageUrl?: string;
  imagePrompt?: string;
}

interface PlatformContent {
  platformId: string;
  text: string;
  hashtags: string[];
  mentions: string[];
  imageUrl?: string;
  edited: boolean;
}

// Prompt strutturali specifici per TIPO CONTENUTO
const CONTENT_TYPE_PROMPTS: Record<ContentType, string> = {
  post: "Genera un POST SOCIAL coinvolgente. Struttura: HOOK (cattura attenzione), CORPO (valore/storia), CTA (azione chiara).",
  carousel: "Genera il testo per un CAROUSEL di 5-7 slide. Per ogni slide indica: SLIDE N (Titolo), TESTO BREVE (max 30 parole), ELEMENTO VISIVO SUGGERITO.",
  story: "Genera una sequenza di 3-5 STORIE. Per ogni storia indica: TESTO OVERLAY, SFONDO/VISUAL, INTERAZIONE (sondaggio/domanda/link).",
  video: "Genera uno SCRIPT VIDEO (Reel/TikTok/Short) di 30-60 secondi. Indica: TIMING (es. 0-3s), TESTO A VIDEO, PARLATO (Speaker), AZIONE VISIVA.",
  email: "Genera una EMAIL MARKETING. Struttura: OGGETTO (curiosità), PREHEADER, SALUTO, PROBLEMA, SOLUZIONE, CTA, P.S."
};

// ============================================================================
// CONSTANTS
// ============================================================================

const CONTENT_TYPES = [
  { id: 'post' as ContentType, label: 'Post', icon: FileText, description: 'Post per social media' },
  { id: 'video' as ContentType, label: 'Video', icon: Video, description: 'Reels, TikTok, Shorts' },
  { id: 'story' as ContentType, label: 'Story', icon: Image, description: 'Stories 24h' },
  { id: 'email' as ContentType, label: 'Email', icon: Mail, description: 'Email marketing' },
  { id: 'carousel' as ContentType, label: 'Carousel', icon: Layers, description: 'Slideshow di immagini' },
];

const PLATFORMS: Platform[] = [
  {
    id: 'instagram',
    name: 'Instagram',
    icon: Instagram,
    color: '#E4405F',
    width: 1080, height: 1080, aspectRatio: '1:1',
    maxChars: 2200,
    features: ['post', 'story', 'video', 'carousel']
  },
  {
    id: 'facebook',
    name: 'Facebook',
    icon: Facebook,
    color: '#1877F2',
    width: 1200, height: 630, aspectRatio: '1.91:1',
    maxChars: 63206,
    features: ['post', 'story', 'video', 'carousel']
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: Linkedin,
    color: '#0A66C2',
    width: 1200, height: 627, aspectRatio: '1.91:1',
    maxChars: 3000,
    features: ['post', 'video', 'carousel']
  },
  {
    id: 'twitter',
    name: 'X (Twitter)',
    icon: Twitter,
    color: '#000000',
    width: 1600, height: 900, aspectRatio: '16:9',
    maxChars: 280,
    features: ['post', 'video']
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: Video,
    color: '#000000',
    width: 1080, height: 1920, aspectRatio: '9:16',
    maxChars: 2200,
    features: ['video', 'story']
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: Youtube,
    color: '#FF0000',
    width: 1920, height: 1080, aspectRatio: '16:9',
    maxChars: 5000,
    features: ['video']
  },
  {
    id: 'threads',
    name: 'Threads',
    icon: MessageCircle,
    color: '#000000',
    width: 1440, height: 1920, aspectRatio: '3:4',
    maxChars: 500,
    features: ['post', 'carousel']
  },
];

const TONES = [
  { id: 'professional', label: '💼 Professionale' },
  { id: 'friendly', label: '😊 Amichevole' },
  { id: 'persuasive', label: '🎯 Persuasivo' },
  { id: 'educational', label: '📚 Educativo' },
  { id: 'inspiring', label: '✨ Ispirante' },
  { id: 'humorous', label: '😄 Umoristico' },
];

// Template definitions con prompt engineering specifici
const QUICK_TEMPLATES = [
  {
    id: 'lancio-prodotto',
    label: '🚀 Lancio Prodotto',
    textPrompt: 'Crea un post di LANCIO PRODOTTO eccitante. Usa urgenza, esclusività, benefici chiave. Struttura: hook potente, 3 benefici, call-to-action forte.',
    imageStyle: 'product launch announcement, sleek modern design, spotlight effect, premium feel, bold typography, excitement and innovation vibe',
    mood: 'exciting, premium, innovative'
  },
  {
    id: 'tip-giorno',
    label: '💡 Tip del Giorno',
    textPrompt: 'Crea un post TIP/CONSIGLIO pratico e utile. Formato: problema comune -> soluzione rapida -> risultato. Breve e actionable.',
    imageStyle: 'educational infographic style, lightbulb concept, clean minimal design, helpful and informative, bright colors, easy to read',
    mood: 'helpful, educational, practical'
  },
  {
    id: 'caso-successo',
    label: '🌟 Caso di Successo',
    textPrompt: 'Crea un post CASE STUDY/TESTIMONIAL. Struttura: sfida cliente, soluzione implementata, risultati concreti con numeri. Social proof.',
    imageStyle: 'success story visualization, before/after concept, growth charts, trophy or achievement symbols, professional corporate style, trust-building',
    mood: 'trustworthy, successful, professional'
  },
  {
    id: 'trend-settore',
    label: '📈 Trend del Settore',
    textPrompt: 'Crea un post su TREND/NOVITÀ del settore tech/AI. Posiziona il brand come thought leader. Dati, statistiche, visione futura.',
    imageStyle: 'futuristic trend visualization, data analytics style, rising graphs, tech innovation aesthetic, blue and purple gradients, forward-thinking',
    mood: 'innovative, thought-leading, futuristic'
  },
  {
    id: 'offerta-speciale',
    label: '🎯 Offerta Speciale',
    textPrompt: 'Crea un post PROMO/OFFERTA. Urgenza + scarsità + valore. Prezzo barrato, deadline, bonus esclusivi. CTA immediata.',
    imageStyle: 'promotional sale design, bold discount badges, urgency elements, red and gold accents, eye-catching offer visualization, limited time feel',
    mood: 'urgent, valuable, exclusive'
  },
  {
    id: 'ai-business',
    label: '🤖 AI per Business',
    textPrompt: 'Crea un post su AI/INTELLIGENZA ARTIFICIALE per aziende. Benefici concreti, casi d uso pratici, ROI. Demistifica la tecnologia.',
    imageStyle: 'artificial intelligence visualization, neural network patterns, futuristic robot or AI assistant, glowing circuits, blue and cyan colors, high-tech professional',
    mood: 'cutting-edge, intelligent, transformative'
  },
  {
    id: 'app-mobile',
    label: '📱 App Mobile',
    textPrompt: 'Crea un post su APP MOBILE/sviluppo. Features chiave, UX, disponibilità store. Screenshot mockup o benefici utente.',
    imageStyle: 'mobile app showcase, smartphone mockup, clean UI design, app store style, modern interface preview, fingers touching screen',
    mood: 'modern, user-friendly, accessible'
  },
  {
    id: 'sito-web',
    label: '🌐 Sito Web',
    textPrompt: 'Crea un post su SITO WEB/presenza online. Design, velocità, conversioni, SEO. Perché un sito professionale fa la differenza.',
    imageStyle: 'website design showcase, browser mockup, responsive design visualization, modern web interface, clean layout preview, professional web presence',
    mood: 'professional, modern, effective'
  },
];

// Tone definitions per prompt engineering
const TONE_PROMPTS: Record<string, { textStyle: string; visualMood: string }> = {
  'professional': {
    textStyle: 'Tono PROFESSIONALE e autorevole. Linguaggio formale ma accessibile. Credibilità e competenza.',
    visualMood: 'corporate professional, clean lines, sophisticated, trustworthy, business aesthetic'
  },
  'friendly': {
    textStyle: 'Tono AMICHEVOLE e conversazionale. Come un amico esperto che consiglia. Emoji moderate, linguaggio semplice.',
    visualMood: 'warm and friendly, approachable, soft colors, welcoming, human connection'
  },
  'persuasive': {
    textStyle: 'Tono PERSUASIVO e orientato all azione. Urgenza, benefici, obiezioni anticipate. Copy da venditore esperto.',
    visualMood: 'bold and impactful, attention-grabbing, dynamic composition, action-oriented'
  },
  'educational': {
    textStyle: 'Tono EDUCATIVO e informativo. Spiega concetti, usa esempi, condividi valore. Posizionamento come esperto.',
    visualMood: 'educational and informative, infographic style, clear hierarchy, knowledge-sharing'
  },
  'inspiring': {
    textStyle: 'Tono ISPIRANTE e motivazionale. Visione, possibilità, trasformazione. Emotivo ma non sdolcinato.',
    visualMood: 'inspirational and uplifting, sunrise/light imagery, aspirational, motivating'
  },
  'humorous': {
    textStyle: 'Tono UMORISTICO e leggero. Battute intelligenti, meme-style, autoironia professionale. Memorabile.',
    visualMood: 'playful and fun, bright colors, quirky elements, memorable and shareable'
  },
};

// ============================================================================
// COMPONENT
// ============================================================================

export default function ContentStudio() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Step tracking
  const [currentStep, setCurrentStep] = useState(1);

  // Step 1: Content Type
  const [contentType, setContentType] = useState<ContentType>('post');

  // Step 2: Platforms
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['instagram', 'facebook', 'linkedin']);

  // Step 3: Topic & Generation
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('professional');
  const [quickTemplate, setQuickTemplate] = useState<string | null>(null);
  const [isGeneratingText, setIsGeneratingText] = useState(false);
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [isGeneratingAll, setIsGeneratingAll] = useState(false);

  // Step 4: Content per platform
  const [platformContents, setPlatformContents] = useState<Record<string, PlatformContent>>({});
  const [editingPlatform, setEditingPlatform] = useState<string | null>(null);

  // Step 5: Publishing
  const [publishMode, setPublishMode] = useState<PublishMode>('schedule');
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('09:00');
  const [isPublishing, setIsPublishing] = useState(false);

  // Brand DNA
  const [brandContext, setBrandContext] = useState<any>(null);

  // Theme classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';

  // Load Brand DNA
  useEffect(() => {
    BrandContextAPI.getContext().then(setBrandContext).catch(console.error);
  }, []);

  // Filter platforms by content type
  const availablePlatforms = PLATFORMS.filter(p => p.features.includes(contentType));

  // Toggle platform selection
  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  // ============================================================================
  // AI GENERATION
  // ============================================================================

  const generateTextAI = async () => {
    if (!topic.trim()) {
      toast.error('Inserisci un argomento');
      return;
    }

    setIsGeneratingText(true);

    try {
      const brandInfo = brandContext
        ? `Brand: ${brandContext.company_name}. Valori: ${brandContext.values?.join(', ')}. Tono di voce: ${brandContext.tone_of_voice || 'professionale'}.`
        : 'Brand: StudioCentOS - Software House Salerno. Valori: innovazione, qualità, Made in Italy.';

      // Get template and tone prompts
      const selectedTemplate = QUICK_TEMPLATES.find(t => t.id === quickTemplate);
      const tonePrompt = TONE_PROMPTS[tone] || TONE_PROMPTS['professional'];

      // Build MASTER prompt for text generation
      // Ottieni istruzioni specifiche per ogni piattaforma
      const getPlatformSpecificPrompt = (platformId: string) => {
        const platformFormatInstructions = getPromptInstructionsForPlatform(platformId);
        const formatRule = PLATFORM_FORMAT_RULES[platformId];
        const structuralInstruction = CONTENT_TYPE_PROMPTS[contentType];

        return `
${structuralInstruction}

${selectedTemplate?.textPrompt || 'Crea un contenuto efficace e coinvolgente.'}

ARGOMENTO SPECIFICO: ${topic}

STILE E TONO:
${tonePrompt.textStyle}

BRAND CONTEXT:
${brandInfo}

=== REGOLE FORMATTAZIONE ${platformId.toUpperCase()} ===
${platformFormatInstructions}

REQUISITI:
- Scrivi in ITALIANO
- Max ${formatRule?.maxChars || 2000} caratteri
- Emoji: ${formatRule?.emojiDensity === 'high' ? 'usa molte emoji' : formatRule?.emojiDensity === 'low' ? 'emoji minime' : 'emoji moderate'}
- Hashtag: max ${formatRule?.maxHashtags || 5}
- Stile interruzione riga: ${formatRule?.lineBreakStyle || 'normale'}
- Termina con call-to-action chiara
`.trim();
      };

      // Generate for each platform
      const newContents: Record<string, PlatformContent> = {};

      for (const platformId of selectedPlatforms) {
        const platform = PLATFORMS.find(p => p.id === platformId);
        if (!platform) continue;

        const response = await fetch('/api/v1/copilot/content/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
          },
          body: JSON.stringify({
            prompt: getPlatformSpecificPrompt(platformId),
            topic,
            type: contentType,
            platform: platformId,
            tone,
            template: quickTemplate,
            max_chars: PLATFORM_FORMAT_RULES[platformId]?.maxChars || platform.maxChars,
            brand_context: brandInfo,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          // Post-processing per piattaforma specifica
          const rawText = data.content || data.text || generateFallbackText(topic, platform);
          const processedText = postProcessContentForPlatform(rawText, platformId);
          const rawHashtags = data.hashtags || ['StudioCentOS', 'PMI', 'AI'];
          const limitedHashtags = limitHashtagsForPlatform(rawHashtags, platformId);

          newContents[platformId] = {
            platformId,
            text: processedText,
            hashtags: limitedHashtags,
            mentions: [],
            edited: false,
          };
        } else {
          // Fallback con post-processing
          const rawText = generateFallbackText(topic, platform);
          const processedText = postProcessContentForPlatform(rawText, platformId);

          newContents[platformId] = {
            platformId,
            text: processedText,
            hashtags: limitHashtagsForPlatform(['StudioCentOS', 'PMI', 'Digitalizzazione'], platformId),
            mentions: [],
            edited: false,
          };
        }
      }

      setPlatformContents(newContents);
      setCurrentStep(4);
      toast.success(`✨ Testo generato per ${selectedPlatforms.length} piattaforme!`);

    } catch (error) {
      console.error('Text generation error:', error);
      // Fallback
      const fallbackContents: Record<string, PlatformContent> = {};
      selectedPlatforms.forEach(platformId => {
        const platform = PLATFORMS.find(p => p.id === platformId);
        if (platform) {
          fallbackContents[platformId] = {
            platformId,
            text: generateFallbackText(topic, platform),
            hashtags: ['StudioCentOS', 'PMI', 'Digitalizzazione'],
            mentions: [],
            edited: false,
          };
        }
      });
      setPlatformContents(fallbackContents);
      setCurrentStep(4);
      toast.success('Testo generato (offline)');
    } finally {
      setIsGeneratingText(false);
    }
  };

  const generateFallbackText = (topic: string, platform: Platform): string => {
    const emoji = '🚀';
    let text = `${emoji} ${topic}\n\nLa digitalizzazione è la chiave per il successo delle PMI italiane.\n\nNoi di StudioCentOS aiutiamo le aziende a:\n✅ Automatizzare i processi\n✅ Raggiungere nuovi clienti\n✅ Crescere nel digitale\n\n👉 Contattaci: studiocentos.it`;

    // Trim for platform
    if (text.length > platform.maxChars) {
      text = text.slice(0, platform.maxChars - 3) + '...';
    }

    return text;
  };

  const generateImageAI = async () => {
    if (!topic.trim()) {
      toast.error('Inserisci un argomento');
      return;
    }

    setIsGeneratingImage(true);

    try {
      // Get template and tone for MASTER prompt engineering
      const selectedTemplate = QUICK_TEMPLATES.find(t => t.id === quickTemplate);
      const tonePrompt = TONE_PROMPTS[tone] || TONE_PROMPTS['professional'];

      for (const platformId of selectedPlatforms) {
        const platform = PLATFORMS.find(p => p.id === platformId);
        if (!platform) continue;

        // Get generated text for context
        const platformText = platformContents[platformId]?.text || topic;

        // Extract key concepts from the topic for visual representation
        const topicKeywords = topic.toLowerCase().split(' ').filter(w => w.length > 3).slice(0, 5).join(', ');

        // ============================================================
        // MASTER PROMPT ENGINEERING - Professional Image Generation
        // ============================================================
        const visualFormat = contentType === 'post' ? 'Social Media Post Format (Square/Portrait), text-overlay ready' : 'Cinematic/Photography';

        const masterImagePrompt = `
A high-end, professional marketing visual designed for ${platform.name} (${platform.width}x${platform.height} pixels).
FORMAT: ${visualFormat}

VISUAL CONCEPT:
${selectedTemplate?.imageStyle || 'modern professional marketing design, clean and impactful'}

SUBJECT & THEME:
Main subject: ${topic}
Key elements to visualize: ${topicKeywords}
Content context: ${platformText.slice(0, 150)}

MOOD & ATMOSPHERE:
${selectedTemplate?.mood || 'professional and trustworthy'}
Visual mood: ${tonePrompt.visualMood}

BRAND IDENTITY - StudioCentOS:
- Primary color: Deep black (#0A0A0A) for backgrounds
- Accent color: Luxury gold (#D4AF37) for highlights and CTAs
- Secondary: Pure white for contrast and text
- Style: Premium Italian tech company, sophisticated, innovative

TECHNICAL SPECIFICATIONS:
- Composition: Rule of thirds, clear focal point
- Lighting: Professional studio lighting, subtle gradients
- Quality: Ultra-high resolution, sharp details, no artifacts
- Style: NOT stock photography, unique and memorable
- Text: Minimal or none (logo will be added separately)

AVOID:
- Generic stock photo aesthetics
- Cluttered compositions
- Low contrast elements
- Cliché business imagery (handshakes, generic laptops)
- Watermarks or text overlays

FINAL OUTPUT:
Create a scroll-stopping, share-worthy image that represents "${topic}" in a ${tone} style, perfect for ${platform.name} marketing campaigns.
`.trim();

        const response = await fetch('/api/v1/copilot/image/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
          },
          body: JSON.stringify({
            prompt: masterImagePrompt,
            style: selectedTemplate?.id || 'professional_marketing',
            platform: platformId,
            width: platform.width,
            height: platform.height,
            apply_branding: true,
            branding_position: 'top_center',
            template: quickTemplate,
            tone: tone,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          if (data.image_url) {
            setPlatformContents(prev => ({
              ...prev,
              [platformId]: {
                ...prev[platformId],
                imageUrl: data.image_url,
              },
            }));
          }
        }
      }

      toast.success('🎨 Immagini generate con prompt MASTER!');
    } catch (error) {
      console.error('Image generation error:', error);
      toast.error('Errore generazione immagini');
    } finally {
      setIsGeneratingImage(false);
    }
  };

  const generateAll = async () => {
    setIsGeneratingAll(true);
    await generateTextAI();
    await generateImageAI();
    setIsGeneratingAll(false);
  };

  // ============================================================================
  // PUBLISHING
  // ============================================================================

  const handlePublish = async () => {
    if (Object.keys(platformContents).length === 0) {
      toast.error('Genera prima il contenuto');
      return;
    }

    setIsPublishing(true);

    try {
      const scheduledTime = publishMode === 'schedule' && scheduleDate && scheduleTime
        ? new Date(`${scheduleDate}T${scheduleTime}`).toISOString()
        : undefined;

      const results = await Promise.all(
        Object.entries(platformContents).map(async ([platformId, content]) => {
          const mentionsText = content.mentions.length > 0
            ? '\n\nCon: ' + content.mentions.map(m => `@${m}`).join(' ')
            : '';

          const response = await fetch('/api/v1/social/publish', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
            },
            body: JSON.stringify({
              content: content.text + mentionsText + '\n\n' + content.hashtags.map(h => `#${h}`).join(' '),
              platforms: [platformId],
              media_url: content.imageUrl,
              scheduled_time: scheduledTime,
            }),
          });

          let errorMessage = '';
          if (!response.ok) {
            try {
              const errorData = await response.json();
              errorMessage = errorData.detail || errorData.message || 'Errore sconosciuto';
            } catch {
              errorMessage = `HTTP ${response.status}`;
            }
          } else {
            // Check response body for actual publish status
            try {
              const data = await response.json();
              if (data.published_count === 0 || !data.success) {
                errorMessage = data.results?.[0]?.error || 'Pubblicazione fallita - verifica token API';
              }
            } catch { }
          }

          return { platformId, success: response.ok && !errorMessage, error: errorMessage };
        })
      );

      const successCount = results.filter(r => r.success).length;
      const failedResults = results.filter(r => !r.success);

      if (failedResults.length > 0) {
        failedResults.forEach(r => {
          const platformName = PLATFORMS.find(p => p.id === r.platformId)?.name || r.platformId;
          toast.error(`❌ ${platformName}: ${r.error || 'Token scaduto - riconnetti nelle Impostazioni'}`);
        });
      }

      if (publishMode === 'draft') {
        toast.success('💾 Salvato come bozza!');
      } else if (publishMode === 'schedule' && successCount > 0) {
        toast.success(`📅 Programmato su ${successCount} piattaforme!`);
      } else if (successCount > 0) {
        toast.success(`🚀 Pubblicato su ${successCount} piattaforme!`);
      } else if (failedResults.length > 0) {
        toast.error('⚠️ Nessuna pubblicazione riuscita - verifica le connessioni social nelle Impostazioni');
      }

      // Reset
      if (successCount > 0) {
        setTopic('');
        setPlatformContents({});
        setCurrentStep(1);
      }

    } catch (error) {
      console.error('Publish error:', error);
      toast.error('Errore nella pubblicazione');
    } finally {
      setIsPublishing(false);
    }
  };

  // Update platform content
  const updatePlatformContent = (platformId: string, updates: Partial<PlatformContent>) => {
    setPlatformContents(prev => ({
      ...prev,
      [platformId]: {
        ...prev[platformId],
        ...updates,
        edited: true,
      },
    }));
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-gold to-amber-500 flex items-center justify-center">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className={cn('text-2xl font-bold', textPrimary)}>Content Studio</h1>
          <p className={cn('text-sm', textSecondary)}>Crea contenuti potenti con AI per ogni piattaforma</p>
        </div>
        {brandContext && (
          <div className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gold/10 text-gold text-sm">
            <Zap className="w-4 h-4" />
            Brand DNA: {brandContext.company_name || 'Attivo'}
          </div>
        )}
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-2">
        {[1, 2, 3, 4, 5].map((step) => (
          <div key={step} className="flex items-center">
            <button
              onClick={() => step <= currentStep && setCurrentStep(step)}
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all',
                currentStep >= step
                  ? 'bg-gold text-black'
                  : isDark ? 'bg-white/10 text-gray-400' : 'bg-gray-200 text-gray-500'
              )}
            >
              {currentStep > step ? <Check className="w-4 h-4" /> : step}
            </button>
            {step < 5 && (
              <div className={cn(
                'w-12 h-1 mx-1 rounded',
                currentStep > step ? 'bg-gold' : isDark ? 'bg-white/10' : 'bg-gray-200'
              )} />
            )}
          </div>
        ))}
      </div>

      {/* STEP 1: Content Type */}
      <AnimatePresence mode="wait">
        {currentStep === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className={cn(cardBg, 'rounded-2xl p-6')}
          >
            <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>
              Step 1: Cosa vuoi creare?
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {CONTENT_TYPES.map((type) => {
                const Icon = type.icon;
                const isSelected = contentType === type.id;
                return (
                  <button
                    key={type.id}
                    onClick={() => setContentType(type.id)}
                    className={cn(
                      'p-4 rounded-xl border-2 transition-all text-center',
                      isSelected
                        ? 'border-gold bg-gold/10'
                        : isDark ? 'border-white/10 hover:border-white/20' : 'border-gray-200 hover:border-gray-300'
                    )}
                  >
                    <Icon className={cn('w-8 h-8 mx-auto mb-2', isSelected ? 'text-gold' : textSecondary)} />
                    <div className={cn('font-semibold', textPrimary)}>{type.label}</div>
                    <div className={cn('text-xs mt-1', textSecondary)}>{type.description}</div>
                  </button>
                );
              })}
            </div>
            <Button
              onClick={() => setCurrentStep(2)}
              className="mt-6 w-full bg-gold hover:bg-gold/90 text-black"
            >
              Continua <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </motion.div>
        )}

        {/* STEP 2: Platforms */}
        {currentStep === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className={cn(cardBg, 'rounded-2xl p-6')}
          >
            <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>
              Step 2: Per quali piattaforme?
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {availablePlatforms.map((platform) => {
                const Icon = platform.icon;
                const isSelected = selectedPlatforms.includes(platform.id);
                return (
                  <button
                    key={platform.id}
                    onClick={() => togglePlatform(platform.id)}
                    className={cn(
                      'p-4 rounded-xl border-2 transition-all text-left flex items-center gap-3',
                      isSelected
                        ? 'border-gold bg-gold/10'
                        : isDark ? 'border-white/10 hover:border-white/20' : 'border-gray-200 hover:border-gray-300'
                    )}
                  >
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${platform.color}20` }}
                    >
                      <Icon className="w-5 h-5" style={{ color: platform.color }} />
                    </div>
                    <div>
                      <div className={cn('font-semibold', textPrimary)}>{platform.name}</div>
                      <div className={cn('text-xs', textSecondary)}>
                        {platform.width}×{platform.height} ({platform.aspectRatio})
                      </div>
                    </div>
                    {isSelected && <Check className="w-5 h-5 text-gold ml-auto" />}
                  </button>
                );
              })}
            </div>
            <div className="flex gap-3 mt-6">
              <Button variant="outline" onClick={() => setCurrentStep(1)}>Indietro</Button>
              <Button
                onClick={() => setCurrentStep(3)}
                disabled={selectedPlatforms.length === 0}
                className="flex-1 bg-gold hover:bg-gold/90 text-black"
              >
                Continua ({selectedPlatforms.length} selezionate) <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </motion.div>
        )}

        {/* STEP 3: Topic & AI Generation */}
        {currentStep === 3 && (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className={cn(cardBg, 'rounded-2xl p-6')}
          >
            <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>
              Step 3: Argomento + Generazione AI
            </h2>

            {/* Quick Templates */}
            <div className="mb-4">
              <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>
                Template Veloci <span className="text-gold">(seleziona per prompt ottimizzato)</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {QUICK_TEMPLATES.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => {
                      setQuickTemplate(template.id);
                      // Pre-fill topic if empty
                      if (!topic.trim()) {
                        setTopic(template.label.replace(/[^\w\s]/g, '').trim());
                      }
                    }}
                    className={cn(
                      'px-3 py-1.5 rounded-lg text-sm transition-all border',
                      quickTemplate === template.id
                        ? 'bg-gold text-black border-gold font-medium'
                        : isDark
                          ? 'bg-white/5 hover:bg-white/10 text-gray-300 border-white/10'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border-gray-200'
                    )}
                  >
                    {template.label}
                  </button>
                ))}
              </div>
              {quickTemplate && (
                <p className={cn('text-xs mt-2', textSecondary)}>
                  ✨ Template attivo: <span className="text-gold">{QUICK_TEMPLATES.find(t => t.id === quickTemplate)?.label}</span>
                </p>
              )}
            </div>

            {/* Topic Input */}
            <div className="mb-4">
              <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>Argomento</label>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Es: Nuovo servizio AI per automatizzare il business delle PMI..."
                className={cn('w-full px-4 py-3 rounded-xl border min-h-[100px]', inputBg)}
              />
            </div>

            {/* Tone */}
            <div className="mb-6">
              <label className={cn('text-sm font-medium mb-2 block', textSecondary)}>Tono</label>
              <div className="flex flex-wrap gap-2">
                {TONES.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTone(t.id)}
                    className={cn(
                      'px-3 py-2 rounded-lg text-sm transition-all',
                      tone === t.id
                        ? 'bg-gold text-black'
                        : isDark ? 'bg-white/5 text-gray-300' : 'bg-gray-100 text-gray-700'
                    )}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* AI Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
              <Button
                onClick={generateTextAI}
                disabled={isGeneratingText || !topic.trim()}
                variant="outline"
                className="h-14"
              >
                {isGeneratingText ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Wand2 className="w-5 h-5 mr-2" />}
                Genera Testo AI
              </Button>
              <Button
                onClick={generateImageAI}
                disabled={isGeneratingImage || !topic.trim()}
                variant="outline"
                className="h-14"
              >
                {isGeneratingImage ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <ImagePlus className="w-5 h-5 mr-2" />}
                Genera Immagine AI
              </Button>
              <Button
                onClick={generateAll}
                disabled={isGeneratingAll || !topic.trim()}
                className="h-14 bg-gradient-to-r from-gold to-amber-500 text-black hover:from-gold/90 hover:to-amber-500/90"
              >
                {isGeneratingAll ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Sparkles className="w-5 h-5 mr-2" />}
                GENERA TUTTO
              </Button>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setCurrentStep(2)}>Indietro</Button>
            </div>
          </motion.div>
        )}

        {/* STEP 4: Preview per Platform */}
        {currentStep === 4 && (
          <motion.div
            key="step4"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className={cn(cardBg, 'rounded-2xl p-6')}
          >
            <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>
              Step 4: Preview per ogni piattaforma
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {selectedPlatforms.map((platformId) => {
                const platform = PLATFORMS.find(p => p.id === platformId);
                const content = platformContents[platformId];
                if (!platform || !content) return null;
                const Icon = platform.icon;

                return (
                  <div
                    key={platformId}
                    className={cn(
                      'rounded-xl p-4 border',
                      isDark ? 'bg-black/30 border-white/10' : 'bg-gray-50 border-gray-200'
                    )}
                  >
                    {/* Platform Header */}
                    <div className="flex items-center gap-2 mb-3">
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${platform.color}20` }}
                      >
                        <Icon className="w-4 h-4" style={{ color: platform.color }} />
                      </div>
                      <div>
                        <div className={cn('font-semibold text-sm', textPrimary)}>{platform.name}</div>
                        <div className={cn('text-xs', textSecondary)}>
                          {platform.width}×{platform.height}
                        </div>
                      </div>
                      <button
                        onClick={() => setEditingPlatform(editingPlatform === platformId ? null : platformId)}
                        className="ml-auto p-1.5 rounded-lg hover:bg-white/10"
                      >
                        <Edit3 className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>

                    {/* Image Preview */}
                    <div
                      className={cn(
                        'rounded-lg mb-3 flex items-center justify-center overflow-hidden',
                        isDark ? 'bg-white/5' : 'bg-gray-200'
                      )}
                      style={{
                        aspectRatio: `${platform.width}/${platform.height}`,
                        maxHeight: '200px',
                      }}
                    >
                      {content.imageUrl ? (
                        <img src={content.imageUrl} alt="Preview" className="w-full h-full object-cover" />
                      ) : (
                        <div className="text-center p-4">
                          <ImagePlus className={cn('w-8 h-8 mx-auto mb-2', textSecondary)} />
                          <span className={cn('text-xs', textSecondary)}>Nessuna immagine</span>
                        </div>
                      )}
                    </div>

                    {/* Text */}
                    {editingPlatform === platformId ? (
                      <textarea
                        value={content.text}
                        onChange={(e) => updatePlatformContent(platformId, { text: e.target.value })}
                        className={cn('w-full p-2 rounded-lg text-sm min-h-[100px]', inputBg)}
                      />
                    ) : (
                      <div className={cn('text-sm whitespace-pre-wrap line-clamp-4', textPrimary)}>
                        {content.text}
                      </div>
                    )}

                    {/* 🏷️ TAG PERSONE - UI MIGLIORATA */}
                    <div className={cn('mt-3 p-3 rounded-lg border', isDark ? 'bg-blue-500/5 border-blue-500/20' : 'bg-blue-50 border-blue-200')}>
                      <div className="flex items-center gap-2 mb-2">
                        <AtSign className="w-4 h-4 text-blue-500" />
                        <span className={cn('text-xs font-semibold', isDark ? 'text-blue-400' : 'text-blue-600')}>Tag Persone</span>
                      </div>

                      {/* Tags già aggiunti */}
                      <div className="flex flex-wrap gap-1.5 mb-2">
                        {content.mentions.map((mention, i) => (
                          <span key={i} className="flex items-center gap-1 text-xs bg-blue-500/20 text-blue-500 px-2 py-1 rounded-full">
                            @{mention}
                            <button
                              onClick={() => {
                                const newMentions = [...content.mentions];
                                newMentions.splice(i, 1);
                                updatePlatformContent(platformId, { mentions: newMentions });
                              }}
                              className="hover:text-blue-700 ml-0.5"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </span>
                        ))}
                        {content.mentions.length === 0 && (
                          <span className="text-xs text-muted-foreground italic">Nessun tag aggiunto</span>
                        )}
                      </div>

                      {/* Input per aggiungere tag */}
                      <div className="flex gap-2">
                        <input
                          type="text"
                          placeholder="@username + Invio"
                          className={cn('flex-1 text-xs px-3 py-2 rounded-lg border bg-transparent outline-none focus:ring-2 focus:ring-blue-500',
                            isDark ? 'border-white/10 placeholder-gray-500' : 'border-gray-300'
                          )}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault();
                              const val = e.currentTarget.value.trim().replace(/^@/, '');
                              if (val && !content.mentions.includes(val)) {
                                updatePlatformContent(platformId, {
                                  mentions: [...content.mentions, val]
                                });
                                e.currentTarget.value = '';
                              }
                            }
                          }}
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-xs px-2"
                          onClick={(e) => {
                            const input = (e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement);
                            const val = input?.value.trim().replace(/^@/, '');
                            if (val && !content.mentions.includes(val)) {
                              updatePlatformContent(platformId, {
                                mentions: [...content.mentions, val]
                              });
                              input.value = '';
                            }
                          }}
                        >
                          <Plus className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>

                    {/* Hashtags */}
                    <div className="flex flex-wrap gap-1 mt-3">
                      {content.hashtags.slice(0, 5).map((tag, i) => (
                        <span key={i} className="text-xs text-gold">#{tag}</span>
                      ))}
                    </div>

                    {/* Character count */}
                    <div className={cn('text-xs mt-2',
                      content.text.length > platform.maxChars ? 'text-red-400' : textSecondary
                    )}>
                      {content.text.length}/{platform.maxChars} caratteri
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex gap-3 mt-6">
              <Button variant="outline" onClick={() => setCurrentStep(3)}>Indietro</Button>
              <Button
                onClick={() => setCurrentStep(5)}
                className="flex-1 bg-gold hover:bg-gold/90 text-black"
              >
                Continua <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </motion.div>
        )}

        {/* STEP 5: Publish */}
        {currentStep === 5 && (
          <motion.div
            key="step5"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className={cn(cardBg, 'rounded-2xl p-6')}
          >
            <h2 className={cn('text-xl font-bold mb-4', textPrimary)}>
              Step 5: Pubblica o Programma
            </h2>

            {/* Riepilogo Tag (solo visualizzazione) */}
            {Object.values(platformContents).some(c => c.mentions.length > 0) && (
              <div className={cn('p-3 rounded-lg border mb-4 flex items-center gap-2', isDark ? 'bg-blue-500/5 border-blue-500/20' : 'bg-blue-50 border-blue-200')}>
                <AtSign className="w-4 h-4 text-blue-500" />
                <span className={cn('text-sm', textSecondary)}>Tag aggiunti:</span>
                <div className="flex flex-wrap gap-1">
                  {[...new Set(Object.values(platformContents).flatMap(c => c.mentions))].map((m, i) => (
                    <span key={i} className="text-xs bg-blue-500/20 text-blue-500 px-2 py-0.5 rounded-full">@{m}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-3 mb-6">
              {/* Publish Now */}
              <label className={cn(
                'flex items-center gap-3 p-4 rounded-xl border cursor-pointer transition-all',
                publishMode === 'now'
                  ? 'border-gold bg-gold/10'
                  : isDark ? 'border-white/10' : 'border-gray-200'
              )}>
                <input
                  type="radio"
                  name="publishMode"
                  checked={publishMode === 'now'}
                  onChange={() => setPublishMode('now')}
                  className="hidden"
                />
                <div className={cn('w-5 h-5 rounded-full border-2 flex items-center justify-center',
                  publishMode === 'now' ? 'border-gold' : 'border-gray-400'
                )}>
                  {publishMode === 'now' && <div className="w-2.5 h-2.5 rounded-full bg-gold" />}
                </div>
                <Send className="w-5 h-5 text-gold" />
                <span className={textPrimary}>Pubblica ORA su tutte le piattaforme</span>
              </label>

              {/* Schedule */}
              <label className={cn(
                'flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all',
                publishMode === 'schedule'
                  ? 'border-gold bg-gold/10'
                  : isDark ? 'border-white/10' : 'border-gray-200'
              )}>
                <input
                  type="radio"
                  name="publishMode"
                  checked={publishMode === 'schedule'}
                  onChange={() => setPublishMode('schedule')}
                  className="hidden"
                />
                <div className={cn('w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5',
                  publishMode === 'schedule' ? 'border-gold' : 'border-gray-400'
                )}>
                  {publishMode === 'schedule' && <div className="w-2.5 h-2.5 rounded-full bg-gold" />}
                </div>
                <Clock className="w-5 h-5 text-gold mt-0.5" />
                <div className="flex-1">
                  <span className={textPrimary}>Programma per:</span>
                  <div className="flex gap-2 mt-2">
                    <input
                      type="date"
                      value={scheduleDate}
                      onChange={(e) => setScheduleDate(e.target.value)}
                      className={cn('px-3 py-2 rounded-lg border text-sm', inputBg)}
                    />
                    <input
                      type="time"
                      value={scheduleTime}
                      onChange={(e) => setScheduleTime(e.target.value)}
                      className={cn('px-3 py-2 rounded-lg border text-sm', inputBg)}
                    />
                  </div>
                </div>
              </label>

              {/* Draft */}
              <label className={cn(
                'flex items-center gap-3 p-4 rounded-xl border cursor-pointer transition-all',
                publishMode === 'draft'
                  ? 'border-gold bg-gold/10'
                  : isDark ? 'border-white/10' : 'border-gray-200'
              )}>
                <input
                  type="radio"
                  name="publishMode"
                  checked={publishMode === 'draft'}
                  onChange={() => setPublishMode('draft')}
                  className="hidden"
                />
                <div className={cn('w-5 h-5 rounded-full border-2 flex items-center justify-center',
                  publishMode === 'draft' ? 'border-gold' : 'border-gray-400'
                )}>
                  {publishMode === 'draft' && <div className="w-2.5 h-2.5 rounded-full bg-gold" />}
                </div>
                <Save className="w-5 h-5 text-gray-400" />
                <span className={textPrimary}>Salva come bozza</span>
              </label>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setCurrentStep(4)}>Indietro</Button>
              <Button
                onClick={handlePublish}
                disabled={isPublishing || (publishMode === 'schedule' && (!scheduleDate || !scheduleTime))}
                className="flex-1 bg-gradient-to-r from-gold to-amber-500 text-black hover:from-gold/90 hover:to-amber-500/90 h-14 text-lg"
              >
                {isPublishing ? (
                  <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Pubblicando...</>
                ) : publishMode === 'now' ? (
                  <><Send className="w-5 h-5 mr-2" /> PUBBLICA ORA</>
                ) : publishMode === 'schedule' ? (
                  <><Calendar className="w-5 h-5 mr-2" /> PROGRAMMA</>
                ) : (
                  <><Save className="w-5 h-5 mr-2" /> SALVA BOZZA</>
                )}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div >
  );
}
