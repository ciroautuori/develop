/**
 * VideoStoryCreator Component
 * Complete Video & Stories Creator for Social Media
 *
 * Features:
 * - Avatar Video (HeyGen) - AI avatar that speaks
 * - Story Designer - Graphic templates with animations
 * - Video Editor - Clip/image montage
 * - Carousel/Slideshow - Image sequences
 * - Auto-Generate - AI creates everything
 *
 * DESIGN SYSTEM ALIGNED - Light/Dark mode support
 * WCAG AA Compliant - 44px touch targets
 *
 * @uses constants/video-platforms - Piattaforme video centralizzate
 * @uses constants/quick-templates - Template AI centralizzati
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Video, Sparkles, Image, Layers, Wand2, Play,
  User, Type, Music, Clock, Download, Eye,
  Instagram, Youtube, Linkedin, MessageSquare,
  Plus, Trash2, Upload, Palette, MoveUp, MoveDown,
  AlertCircle, CheckCircle, Loader2, Settings,
  Film, Camera, LayoutGrid, Mic
} from 'lucide-react';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { cn } from '../../../../../shared/lib/utils';
import { Button } from '../../../../../shared/components/ui/button';
import { BrandContextAPI } from '../api/brandContext';

// Costanti centralizzate
import { VIDEO_PLATFORMS } from '../constants/video-platforms';
import { VIDEO_SCRIPT_TEMPLATES, STORY_TEMPLATES } from '../constants/quick-templates';

// =============================================================================
// TYPES
// =============================================================================

type CreatorMode = 'avatar' | 'story' | 'video' | 'carousel' | 'auto';

interface SlideItem {
  id: string;
  type: 'image' | 'video' | 'text';
  content: string; // URL or text
  duration: number; // seconds
  animation?: 'fade' | 'slide' | 'zoom' | 'none';
  textOverlay?: string;
  textPosition?: 'top' | 'center' | 'bottom';
}

// Usa VIDEO_PLATFORMS centralizzato
const PLATFORMS = VIDEO_PLATFORMS;

// =============================================================================
// COMPONENT
// =============================================================================

export function VideoStoryCreator() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // State
  const [mode, setMode] = useState<CreatorMode>('story');
  const [platform, setPlatform] = useState<keyof typeof PLATFORMS>('instagram_story');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedUrl, setGeneratedUrl] = useState<string | null>(null);

  // Story Designer State
  const [slides, setSlides] = useState<SlideItem[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [storyText, setStoryText] = useState('');
  const [backgroundColor, setBackgroundColor] = useState('#0a0a0a');

  // Avatar Video State
  const [avatarScript, setAvatarScript] = useState('');
  const [avatarTopic, setAvatarTopic] = useState('');

  // Auto-Generate State
  const [autoPrompt, setAutoPrompt] = useState('');
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [selectedScriptTemplate, setSelectedScriptTemplate] = useState<string | null>(null);

  // Design System Classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const textLabel = isDark ? 'text-gray-300' : 'text-gray-700';

  // Mode configurations
  const MODES = [
    {
      id: 'avatar' as CreatorMode,
      label: 'Avatar Video',
      icon: User,
      description: 'Video con il tuo avatar AI che parla',
      color: 'from-gold to-gold',
    },
    {
      id: 'story' as CreatorMode,
      label: 'Story Designer',
      icon: Layers,
      description: 'Template grafici animati per stories',
      color: 'from-gold to-gray-700',
    },
    {
      id: 'video' as CreatorMode,
      label: 'Video Editor',
      icon: Film,
      description: 'Montaggio video con clip e immagini',
      color: 'from-gold to-gold',
    },
    {
      id: 'carousel' as CreatorMode,
      label: 'Carosello',
      icon: LayoutGrid,
      description: 'Slideshow di immagini per social',
      color: 'from-gold to-gold',
    },
    {
      id: 'auto' as CreatorMode,
      label: 'Auto AI',
      icon: Wand2,
      description: 'L\'AI genera tutto automaticamente',
      color: 'from-gold to-gold',
    },
  ];

  // ==========================================================================
  // HANDLERS
  // ==========================================================================

  const addSlide = (type: SlideItem['type']) => {
    const newSlide: SlideItem = {
      id: `slide-${Date.now()}`,
      type,
      content: type === 'text' ? 'Il tuo testo qui...' : '',
      duration: 3,
      animation: 'fade',
      textPosition: 'center',
    };
    setSlides([...slides, newSlide]);
  };

  const removeSlide = (id: string) => {
    setSlides(slides.filter(s => s.id !== id));
  };

  const moveSlide = (id: string, direction: 'up' | 'down') => {
    const index = slides.findIndex(s => s.id === id);
    if (index === -1) return;
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= slides.length) return;
    const newSlides = [...slides];
    [newSlides[index], newSlides[newIndex]] = [newSlides[newIndex], newSlides[index]];
    setSlides(newSlides);
  };

  const updateSlide = (id: string, updates: Partial<SlideItem>) => {
    setSlides(slides.map(s => s.id === id ? { ...s, ...updates } : s));
  };

  // HeyGen API Service
  const HeyGenApi = {
    baseUrl: '/api/v1/admin/heygen',
    getHeaders: () => ({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
    }),

    async generateVideo(script: string, avatarId: string, voiceId: string) {
      const res = await fetch(`${this.baseUrl}/video/generate`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          title: `Video ${Date.now()}`,
          script,
          avatar_id: avatarId,
          voice_id: voiceId,
          platform,
          background_type: 'color',
          background_value: backgroundColor,
        }),
      });
      if (!res.ok) throw new Error('Video generation failed');
      return res.json();
    },

    async generateScript(topic: string, tone = 'professional') {
      const res = await fetch(`${this.baseUrl}/script/generate`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ topic, tone, duration: 'short', language: 'it' }),
      });
      if (!res.ok) throw new Error('Script generation failed');
      return res.json();
    },

    async checkVideoStatus(videoId: string) {
      const res = await fetch(`${this.baseUrl}/video/${videoId}/status`, {
        headers: this.getHeaders(),
      });
      if (!res.ok) throw new Error('Status check failed');
      return res.json();
    },
  };

  const handleGenerate = async () => {
    if (!avatarScript.trim()) return;
    setIsGenerating(true);
    try {
      const result = await HeyGenApi.generateVideo(
        avatarScript,
        'c50380c835f1467689615a0e1f29e6c6', // Avatar ID configurato
        'it-IT-DiegoNeural' // Voce italiana default
      );

      // Poll for video completion
      if (result.video_id) {
        let attempts = 0;
        const maxAttempts = 60;
        const pollInterval = setInterval(async () => {
          attempts++;
          const status = await HeyGenApi.checkVideoStatus(result.video_id);
          if (status.status === 'completed' && status.video_url) {
            clearInterval(pollInterval);
            setGeneratedUrl(status.video_url);
            setIsGenerating(false);
          } else if (status.status === 'failed' || attempts >= maxAttempts) {
            clearInterval(pollInterval);
            setIsGenerating(false);
          }
        }, 5000);
      }
    } catch {
      setIsGenerating(false);
    }
  };

  const handleAutoGenerate = async () => {
    if (!autoPrompt.trim()) return;
    setIsGenerating(true);
    try {
      // First generate script from prompt
      const scriptResult = await HeyGenApi.generateScript(autoPrompt);
      if (scriptResult.script) {
        setAvatarScript(scriptResult.script);
        // Then generate video with that script
        const result = await HeyGenApi.generateVideo(
          scriptResult.script,
          'c50380c835f1467689615a0e1f29e6c6',
          'it-IT-DiegoNeural'
        );
        if (result.video_id) {
          let attempts = 0;
          const pollInterval = setInterval(async () => {
            attempts++;
            const status = await HeyGenApi.checkVideoStatus(result.video_id);
            if (status.status === 'completed' && status.video_url) {
              clearInterval(pollInterval);
              setGeneratedUrl(status.video_url);
              setIsGenerating(false);
            } else if (status.status === 'failed' || attempts >= 60) {
              clearInterval(pollInterval);
              setIsGenerating(false);
            }
          }, 5000);
        }
      }
    } catch {
      setIsGenerating(false);
    }
  };

  const handleGenerateScript = async () => {
    if (!avatarTopic.trim()) return;
    try {
      const result = await HeyGenApi.generateScript(avatarTopic);
      if (result.script) {
        setAvatarScript(result.script);
      }
    } catch {
      // Silent fail - script generation optional
    }
  };

  // 🚀 GENERATE SCRIPT FROM TEMPLATE WITH AI + BRAND DNA
  const generateScriptFromTemplate = async (templateValue: string) => {
    setIsGeneratingScript(true);
    setSelectedScriptTemplate(templateValue);

    try {
      // Fetch Brand DNA for personalized script
      const brandContext = await BrandContextAPI.getContext();
      const topicWithBrand = brandContext
        ? `${templateValue}. Contesto brand: ${brandContext}`
        : templateValue;

      const result = await HeyGenApi.generateScript(topicWithBrand);
      if (result.script) {
        setAvatarScript(result.script);
        setAvatarTopic(templateValue);
      }
    } catch (error) {
      console.error('Script generation error:', error);
      // Fallback script
      setAvatarScript(`Ciao! Sono Ciro Autuori di StudioCentOS.

Oggi voglio parlarti di: ${templateValue}

StudioCentOS è la software house di Salerno che aiuta le PMI italiane a digitalizzarsi con soluzioni su misura.

Offriamo:
- Siti web professionali da 990€
- E-commerce completi da 2.490€
- App mobile da 4.990€

Contattaci per un preventivo gratuito su studiocentos.it!`);
      setAvatarTopic(templateValue);
    } finally {
      setIsGeneratingScript(false);
      setSelectedScriptTemplate(null);
    }
  };

  // ==========================================================================
  // RENDER SECTIONS
  // ==========================================================================

  const renderAvatarMode = () => (
    <div className="space-y-6">
      {/* Your Avatar Info */}
      <div className={cn('p-4 rounded-xl', isDark ? 'bg-gold/20 border border-gold/30' : 'bg-gold/10 border border-gold/20')}>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-r from-gold to-gold flex items-center justify-center">
            <User className="w-8 h-8 text-white" />
          </div>
          <div>
            <h4 className={`font-bold ${textPrimary}`}>Il Tuo Avatar: Ciro Autuori</h4>
            <p className={cn('text-sm', textSecondary)}>
              Talking Photo configurato su HeyGen
            </p>
            <p className={cn('text-xs mt-1', textSecondary)}>
              ID: c50380c835f1467689615a0e1f29e6c6
            </p>
          </div>
          <Button variant="outline" size="sm" className="ml-auto">
            <Settings className="w-4 h-4 mr-2" />
            Configura
          </Button>
        </div>
      </div>

      {/* 🚀 TEMPLATE VELOCI - GENERA SCRIPT CON 1 CLICK */}
      <div>
        <label className={`block text-sm font-medium mb-3 ${textLabel}`}>
          ⚡ Template Veloci - Genera Script con AI
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {VIDEO_SCRIPT_TEMPLATES.map((template) => (
            <motion.button
              key={template.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => generateScriptFromTemplate(template.value)}
              disabled={isGeneratingScript}
              className={cn(
                'p-3 rounded-xl border transition-all text-left',
                selectedScriptTemplate === template.value
                  ? 'border-gold bg-gold/20'
                  : isDark
                    ? 'border-white/10 hover:border-gold/50 bg-white/5'
                    : 'border-gray-200 hover:border-gold/50 bg-gray-50',
                isGeneratingScript && selectedScriptTemplate === template.value && 'animate-pulse'
              )}
            >
              <div className="flex items-center gap-2">
                {isGeneratingScript && selectedScriptTemplate === template.value ? (
                  <Loader2 className="w-4 h-4 animate-spin text-gold" />
                ) : (
                  <Wand2 className="w-4 h-4 text-gold" />
                )}
                <span className={cn('text-sm font-medium', textPrimary)}>{template.label}</span>
              </div>
            </motion.button>
          ))}
        </div>
        {isGeneratingScript && (
          <p className={cn('text-xs mt-2', textSecondary)}>
            ✨ Generando script con AI...
          </p>
        )}
      </div>

      {/* Script Input */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className={`text-sm font-medium ${textLabel}`}>
            Cosa vuoi dire nel video?
          </label>
          <Button
            variant="outline"
            size="sm"
            onClick={handleGenerateScript}
            disabled={!avatarTopic.trim()}
          >
            <Wand2 className="w-4 h-4 mr-2" />
            Genera con AI
          </Button>
        </div>

        <div className="mb-4">
          <input
            type="text"
            value={avatarTopic}
            onChange={(e) => setAvatarTopic(e.target.value)}
            placeholder="Argomento (es: nuovo servizio di consulenza)"
            className={`w-full px-4 py-3 rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold min-h-[44px] mb-3`}
          />
          <textarea
            value={avatarScript}
            onChange={(e) => setAvatarScript(e.target.value)}
            placeholder="Ciao! Oggi voglio parlarti di qualcosa di speciale..."
            rows={6}
            className={`w-full px-4 py-3 rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold resize-none`}
            maxLength={5000}
          />
          <p className={cn('text-xs mt-1', textSecondary)}>
            {avatarScript.length}/5000 caratteri (~{Math.ceil(avatarScript.length / 150)} secondi)
          </p>
        </div>
      </div>

      {/* Voice Selection */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Voce
        </label>
        <div className={cn('p-4 rounded-xl', isDark ? 'bg-white/5' : 'bg-gray-50')}>
          <div className="flex items-center gap-3">
            <Mic className={cn('w-5 h-5', textSecondary)} />
            <div className="flex-1">
              <p className={textPrimary}>Voce Italiana - Gravitas Giovanni</p>
              <p className={cn('text-xs', textSecondary)}>Voce maschile, tono professionale</p>
            </div>
            <Button variant="outline" size="sm">Cambia</Button>
          </div>
        </div>
      </div>

      {/* Background */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Sfondo Video
        </label>
        <div className="flex gap-3">
          <input
            type="color"
            value={backgroundColor}
            onChange={(e) => setBackgroundColor(e.target.value)}
            className="w-14 h-14 rounded-lg cursor-pointer border-0"
          />
          <div className="flex gap-2 flex-wrap">
            {['#0a0a0a', '#1a1a2e', '#16213e', '#D4AF37', '#2d132c', '#ffffff'].map((color) => (
              <button
                key={color}
                onClick={() => setBackgroundColor(color)}
                className={cn(
                  'w-10 h-10 rounded-lg border-2 transition-transform hover:scale-110',
                  backgroundColor === color ? 'border-gold' : 'border-white/20'
                )}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStoryMode = () => (
    <div className="space-y-6">
      {/* Template Selection */}
      <div>
        <label className={`block text-sm font-medium mb-3 ${textLabel}`}>
          Scegli un Template
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {STORY_TEMPLATES.map((template) => (
            <button
              key={template.id}
              onClick={() => setSelectedTemplate(template.id)}
              className={cn(
                'p-4 rounded-xl border-2 transition-all text-center',
                selectedTemplate === template.id
                  ? 'border-gold bg-gold/20'
                  : isDark ? 'border-white/10 hover:border-white/30' : 'border-gray-200 hover:border-gray-300'
              )}
            >
              <span className="text-3xl">{template.preview}</span>
              <p className={cn('text-sm mt-2 font-medium', textLabel)}>{template.name}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Story Content */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Testo Principale
        </label>
        <textarea
          value={storyText}
          onChange={(e) => setStoryText(e.target.value)}
          placeholder="Scrivi il messaggio della tua story..."
          rows={4}
          className={`w-full px-4 py-3 rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold resize-none`}
        />
      </div>

      {/* Media Upload */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Immagine/Video di Sfondo (opzionale)
        </label>
        <div className={cn(
          'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer',
          isDark ? 'border-white/20 hover:border-white/40' : 'border-gray-300 hover:border-gray-400'
        )}>
          <Upload className={cn('w-10 h-10 mx-auto mb-3', textSecondary)} />
          <p className={textSecondary}>Trascina qui o clicca per caricare</p>
          <p className={cn('text-xs mt-1', textSecondary)}>PNG, JPG, MP4 (max 50MB)</p>
        </div>
      </div>

      {/* Colors & Style */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
            Colore Sfondo
          </label>
          <div className="flex gap-2">
            <input
              type="color"
              value={backgroundColor}
              onChange={(e) => setBackgroundColor(e.target.value)}
              className="w-12 h-12 rounded-lg cursor-pointer border-0"
            />
            <input
              type="text"
              value={backgroundColor}
              onChange={(e) => setBackgroundColor(e.target.value)}
              className={`flex-1 px-3 py-2 rounded-lg border ${inputBg} min-h-[44px]`}
            />
          </div>
        </div>
        <div>
          <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
            Colore Testo
          </label>
          <div className="flex gap-2">
            {['#ffffff', '#000000', '#D4AF37', '#ff6b6b', '#4ecdc4'].map((color) => (
              <button
                key={color}
                className="w-10 h-10 rounded-lg border-2 border-white/20"
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Animation */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Animazione Testo
        </label>
        <div className="flex gap-2">
          {['Fade In', 'Slide Up', 'Zoom', 'Typewriter', 'Bounce'].map((anim) => (
            <button
              key={anim}
              className={cn(
                'px-4 py-2 rounded-lg border transition-colors min-h-[44px]',
                isDark ? 'border-white/10 hover:border-white/30' : 'border-gray-200 hover:border-gray-300'
              )}
            >
              {anim}
            </button>
          ))}
        </div>
      </div>

      {/* Music */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          <Music className="w-4 h-4 inline mr-2" />
          Musica di Sottofondo
        </label>
        <select className={`w-full px-4 py-3 rounded-xl border ${inputBg} min-h-[44px]`}>
          <option value="">Nessuna musica</option>
          <option value="upbeat">🎵 Upbeat Corporate</option>
          <option value="chill">🎵 Chill Vibes</option>
          <option value="epic">🎵 Epic Cinematic</option>
          <option value="minimal">🎵 Minimal Tech</option>
        </select>
      </div>
    </div>
  );

  const renderVideoMode = () => (
    <div className="space-y-6">
      {/* Timeline */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className={`text-sm font-medium ${textLabel}`}>
            Timeline Video
          </label>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => addSlide('image')}>
              <Image className="w-4 h-4 mr-2" />
              Immagine
            </Button>
            <Button variant="outline" size="sm" onClick={() => addSlide('video')}>
              <Video className="w-4 h-4 mr-2" />
              Video
            </Button>
            <Button variant="outline" size="sm" onClick={() => addSlide('text')}>
              <Type className="w-4 h-4 mr-2" />
              Testo
            </Button>
          </div>
        </div>

        {slides.length === 0 ? (
          <div className={cn(
            'border-2 border-dashed rounded-xl p-8 text-center',
            isDark ? 'border-white/20' : 'border-gray-300'
          )}>
            <Film className={cn('w-10 h-10 mx-auto mb-3', textSecondary)} />
            <p className={textSecondary}>Aggiungi elementi alla timeline</p>
            <p className={cn('text-xs mt-1', textSecondary)}>
              Immagini, video o testo per creare il tuo video
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {slides.map((slide, index) => (
              <div
                key={slide.id}
                className={cn(
                  'flex items-center gap-3 p-3 rounded-xl',
                  isDark ? 'bg-white/5' : 'bg-gray-50'
                )}
              >
                <div className={cn(
                  'w-12 h-12 rounded-lg flex items-center justify-center',
                  isDark ? 'bg-white/10' : 'bg-gray-200'
                )}>
                  {slide.type === 'image' && <Image className="w-5 h-5" />}
                  {slide.type === 'video' && <Video className="w-5 h-5" />}
                  {slide.type === 'text' && <Type className="w-5 h-5" />}
                </div>
                <div className="flex-1">
                  <p className={cn('text-sm font-medium', textPrimary)}>
                    {slide.type === 'text' ? slide.content.substring(0, 30) : `${slide.type} ${index + 1}`}
                  </p>
                  <p className={cn('text-xs', textSecondary)}>{slide.duration}s</p>
                </div>
                <input
                  type="number"
                  value={slide.duration}
                  onChange={(e) => updateSlide(slide.id, { duration: parseInt(e.target.value) || 1 })}
                  className={cn('w-16 px-2 py-1 rounded text-center text-sm', inputBg)}
                  min="1"
                  max="60"
                />
                <span className={cn('text-xs', textSecondary)}>sec</span>
                <div className="flex gap-1">
                  <button
                    onClick={() => moveSlide(slide.id, 'up')}
                    disabled={index === 0}
                    className={cn('p-1.5 rounded', isDark ? 'hover:bg-white/10' : 'hover:bg-gray-200')}
                  >
                    <MoveUp className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => moveSlide(slide.id, 'down')}
                    disabled={index === slides.length - 1}
                    className={cn('p-1.5 rounded', isDark ? 'hover:bg-white/10' : 'hover:bg-gray-200')}
                  >
                    <MoveDown className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => removeSlide(slide.id)}
                    className="p-1.5 rounded text-gray-400 hover:bg-gray-500/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Transitions */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Transizione tra Slide
        </label>
        <div className="flex gap-2 flex-wrap">
          {['Nessuna', 'Fade', 'Slide', 'Zoom', 'Wipe'].map((trans) => (
            <button
              key={trans}
              className={cn(
                'px-4 py-2 rounded-lg border transition-colors min-h-[44px]',
                isDark ? 'border-white/10 hover:border-white/30' : 'border-gray-200 hover:border-gray-300'
              )}
            >
              {trans}
            </button>
          ))}
        </div>
      </div>

      {/* Audio */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Audio
        </label>
        <div className="grid grid-cols-2 gap-4">
          <div className={cn('p-4 rounded-xl', isDark ? 'bg-white/5' : 'bg-gray-50')}>
            <Music className={cn('w-5 h-5 mb-2', textSecondary)} />
            <p className={cn('text-sm font-medium', textPrimary)}>Musica</p>
            <p className={cn('text-xs', textSecondary)}>Aggiungi sottofondo</p>
          </div>
          <div className={cn('p-4 rounded-xl', isDark ? 'bg-white/5' : 'bg-gray-50')}>
            <Mic className={cn('w-5 h-5 mb-2', textSecondary)} />
            <p className={cn('text-sm font-medium', textPrimary)}>Voiceover</p>
            <p className={cn('text-xs', textSecondary)}>Registra o genera AI</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCarouselMode = () => (
    <div className="space-y-6">
      <div className={cn('p-4 rounded-xl', isDark ? 'bg-gold/20' : 'bg-gold/10')}>
        <p className={textSecondary}>
          📊 Crea un carosello di immagini per Instagram o LinkedIn.
          Fino a 10 slide che gli utenti possono scorrere.
        </p>
      </div>

      {/* Slides */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className={`text-sm font-medium ${textLabel}`}>
            Slide del Carosello
          </label>
          <Button variant="outline" size="sm" onClick={() => addSlide('image')}>
            <Plus className="w-4 h-4 mr-2" />
            Aggiungi Slide
          </Button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {[1, 2, 3, 4, 5].map((num) => (
            <div
              key={num}
              className={cn(
                'aspect-square rounded-xl border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-colors',
                isDark ? 'border-white/20 hover:border-white/40' : 'border-gray-300 hover:border-gray-400'
              )}
            >
              <Plus className={cn('w-8 h-8 mb-2', textSecondary)} />
              <span className={cn('text-xs', textSecondary)}>Slide {num}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Carousel settings */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
            Stile Slide
          </label>
          <select className={`w-full px-4 py-3 rounded-xl border ${inputBg} min-h-[44px]`}>
            <option>Classico</option>
            <option>Minimal</option>
            <option>Bold</option>
            <option>Gradient</option>
          </select>
        </div>
        <div>
          <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
            Indicatore Pagina
          </label>
          <select className={`w-full px-4 py-3 rounded-xl border ${inputBg} min-h-[44px]`}>
            <option>Punti</option>
            <option>Numeri</option>
            <option>Barra progresso</option>
            <option>Nessuno</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderAutoMode = () => (
    <div className="space-y-6">
      <div className={cn('p-4 rounded-xl', isDark ? 'bg-gold/20 border border-gold/30' : 'bg-gold/10 border border-gold/20')}>
        <Wand2 className="w-8 h-8 text-gold mb-3" />
        <h4 className={`font-bold ${textPrimary}`}>Generazione Automatica con AI</h4>
        <p className={cn('text-sm mt-1', textSecondary)}>
          Descrivi cosa vuoi creare e l'AI genererà automaticamente video o story completi
          con immagini, testo, animazioni e musica.
        </p>
      </div>

      <div>
        <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
          Cosa vuoi creare?
        </label>
        <textarea
          value={autoPrompt}
          onChange={(e) => setAutoPrompt(e.target.value)}
          placeholder="Es: Crea una story per promuovere il mio nuovo corso di marketing digitale. Deve essere accattivante, con colori gold e nero, e includere una call to action per iscriversi."
          rows={5}
          className={`w-full px-4 py-3 rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold resize-none`}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
            Tipo di Contenuto
          </label>
          <select className={`w-full px-4 py-3 rounded-xl border ${inputBg} min-h-[44px]`}>
            <option>Story con Testo</option>
            <option>Video Promo</option>
            <option>Avatar che Parla</option>
            <option>Carosello</option>
            <option>L'AI decide il migliore</option>
          </select>
        </div>
        <div>
          <label className={`block text-sm font-medium mb-2 ${textLabel}`}>
            Stile
          </label>
          <select className={`w-full px-4 py-3 rounded-xl border ${inputBg} min-h-[44px]`}>
            <option>Professionale</option>
            <option>Creativo</option>
            <option>Minimal</option>
            <option>Bold & Colorato</option>
            <option>Elegante</option>
          </select>
        </div>
      </div>

      <Button
        onClick={handleAutoGenerate}
        disabled={isGenerating || !autoPrompt.trim()}
        className="w-full bg-gradient-to-r from-gold to-gold min-h-[48px]"
      >
        {isGenerating ? (
          <>
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            L'AI sta creando il tuo contenuto...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5 mr-2" />
            Genera con AI
          </>
        )}
      </Button>
    </div>
  );

  // ==========================================================================
  // MAIN RENDER
  // ==========================================================================

  return (
    <div className="space-y-4 sm:space-y-6" role="region" aria-label="Video & Story Creator">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6`}
      >
        <div className="flex flex-col sm:flex-row items-start gap-3 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-gold to-gold rounded-lg flex items-center justify-center flex-shrink-0">
            <Video className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
          </div>
          <div className="flex-1">
            <h2 className={`text-xl sm:text-2xl font-bold mb-1 sm:mb-2 ${textPrimary}`}>
              Video & Stories Creator
            </h2>
            <p className={`text-sm sm:text-base ${textSecondary}`}>
              Crea contenuti video per tutti i tuoi social. Stories, Reels, Video, Caroselli.
            </p>
          </div>
        </div>

        {/* Mode Selection */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 sm:gap-3 mt-6">
          {MODES.map((m) => {
            const Icon = m.icon;
            const isSelected = mode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={cn(
                  'p-3 sm:p-4 rounded-xl border-2 transition-all text-center',
                  isSelected
                    ? `border-transparent bg-gradient-to-r ${m.color} text-white`
                    : isDark ? 'border-white/10 hover:border-white/30' : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <Icon className={cn('w-6 h-6 mx-auto mb-2', !isSelected && textSecondary)} />
                <span className={cn('text-xs sm:text-sm font-medium', !isSelected && textLabel)}>
                  {m.label}
                </span>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Platform Selection */}
      <div className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6`}>
        <h3 className={`text-lg font-bold mb-4 ${textPrimary}`}>
          📱 Piattaforma e Formato
        </h3>
        <div className="flex flex-wrap gap-2">
          {Object.entries(PLATFORMS).map(([key, { label, ratio }]) => (
            <button
              key={key}
              onClick={() => setPlatform(key as keyof typeof PLATFORMS)}
              className={cn(
                'px-3 py-2 rounded-lg border transition-colors text-sm',
                platform === key
                  ? 'border-gold bg-gold/20 text-gold'
                  : isDark ? 'border-white/10 hover:border-white/30' : 'border-gray-200 hover:border-gray-300',
                textLabel
              )}
            >
              {label} <span className={textSecondary}>({ratio})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <AnimatePresence mode="wait">
        <motion.div
          key={mode}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6`}
        >
          {mode === 'avatar' && renderAvatarMode()}
          {mode === 'story' && renderStoryMode()}
          {mode === 'video' && renderVideoMode()}
          {mode === 'carousel' && renderCarouselMode()}
          {mode === 'auto' && renderAutoMode()}
        </motion.div>
      </AnimatePresence>

      {/* Generate Button (for non-auto modes) */}
      {mode !== 'auto' && (
        <div className="flex gap-3">
          <Button
            onClick={handleGenerate}
            disabled={isGenerating}
            className={cn(
              'flex-1 min-h-[48px] text-lg',
              mode === 'avatar' && 'bg-gradient-to-r from-gold to-gold',
              mode === 'story' && 'bg-gradient-to-r from-gold to-gray-700',
              mode === 'video' && 'bg-gradient-to-r from-gold to-gold',
              mode === 'carousel' && 'bg-gradient-to-r from-gold to-gold'
            )}
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Generazione in corso...
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                Genera {MODES.find(m => m.id === mode)?.label}
              </>
            )}
          </Button>
          <Button variant="outline" className="min-h-[48px]">
            <Eye className="w-5 h-5 mr-2" />
            Anteprima
          </Button>
        </div>
      )}

      {/* Generated Result */}
      {generatedUrl && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6`}
        >
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-6 h-6 text-gold" />
            <h3 className={`text-lg font-bold ${textPrimary}`}>Contenuto Generato!</h3>
          </div>

          <div className={cn('aspect-[9/16] max-w-xs mx-auto rounded-xl overflow-hidden', isDark ? 'bg-white/10' : 'bg-gray-100')}>
            <div className="w-full h-full flex items-center justify-center">
              <Play className={cn('w-16 h-16', textSecondary)} />
            </div>
          </div>

          <div className="flex gap-3 mt-4">
            <Button className="flex-1 bg-gold hover:bg-gold/90">
              <Download className="w-5 h-5 mr-2" />
              Scarica
            </Button>
            <Button variant="outline" className="flex-1">
              <Instagram className="w-5 h-5 mr-2" />
              Pubblica
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
