/**
 * BusinessDNAGenerator Component
 * DESIGN SYSTEM ALIGNED - Light/Dark mode support
 * WCAG AA Compliant
 * NOW WITH DATABASE PERSISTENCE!
 */

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Download, RotateCcw, Info, Loader2, Upload, X, Image as ImageIcon, Save, Cloud, CloudOff } from 'lucide-react';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { cn } from '../../../../../shared/lib/utils';
import { Button } from '../../../../../shared/components/ui/button';
import { useBusinessDNA } from '../../../hooks/marketing/useBusinessDNA';
import { useBrandSettings } from '../../../hooks/marketing/useBrandSettings';
import { DEFAULT_DNA_VALUES, TONE_OF_VOICE_OPTIONS, type BusinessDNAFormData, type ToneOfVoice } from '../../../types/business-dna.types';

export function BusinessDNAGenerator() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [formData, setFormData] = useState<BusinessDNAFormData>(DEFAULT_DNA_VALUES);
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { generate, download, reset, isGenerating, imageUrl, error } = useBusinessDNA();

  // NEW: Brand Settings persistence
  const {
    brandSettings,
    isLoading: isLoadingSettings,
    isSaving,
    load: loadSettings,
    save: saveSettings,
    hasSettings
  } = useBrandSettings();

  // Load saved settings on mount
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  // Populate form from saved settings
  useEffect(() => {
    if (brandSettings) {
      setFormData(prev => ({
        ...prev,
        company_name: brandSettings.company_name || '',
        tagline: brandSettings.tagline || '',
        business_overview: brandSettings.description || '',
        primary_color: brandSettings.primary_color,
        secondary_color: brandSettings.secondary_color,
        accent_color: brandSettings.accent_color || '#FAFAFA',
        brand_attributes: brandSettings.values.join(', '),
        tone_of_voice: brandSettings.tone_of_voice
      }));
      if (brandSettings.logo_url) {
        setLogoPreview(brandSettings.logo_url);
      }
    }
  }, [brandSettings]);

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
  const borderColor = isDark ? 'border-white/10' : 'border-gray-200';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await generate(formData, logoFile);
  };

  // NEW: Save to database
  const handleSave = async () => {
    // Map free-text tone to valid enum value, default to 'professional'
    const validTones: ToneOfVoice[] = ['professional', 'casual', 'enthusiastic', 'formal', 'friendly', 'authoritative'];
    const toneValue = formData.tone_of_voice.toLowerCase();
    const mappedTone: ToneOfVoice = validTones.find(t => toneValue.includes(t)) || 'professional';

    await saveSettings({
      company_name: formData.company_name.trim() || null,
      tagline: formData.tagline.trim() || null,
      description: formData.business_overview.trim() || null,
      primary_color: formData.primary_color,
      secondary_color: formData.secondary_color,
      accent_color: formData.accent_color,
      tone_of_voice: mappedTone,
      values: formData.brand_attributes.split(',').map(v => v.trim()).filter(Boolean),
      logo_url: logoPreview || null
    });
  };

  const handleReset = () => {
    setFormData(DEFAULT_DNA_VALUES);
    setLogoFile(null);
    setLogoPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    reset();
  };

  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error('Per favore carica un\'immagine valida (PNG, JPG, SVG)');
        return;
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Il file è troppo grande. Massimo 5MB.');
        return;
      }
      setLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeLogo = () => {
    setLogoFile(null);
    setLogoPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const updateField = (field: keyof BusinessDNAFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-4 sm:space-y-6" role="region" aria-label="Business DNA Generator">
      {/* Header Card */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6`}
      >
        <div className="flex flex-col sm:flex-row items-start gap-3 sm:gap-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-gold to-gold rounded-lg flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" aria-hidden="true" />
          </div>
          <div>
            <h2 className={`text-xl sm:text-2xl font-bold mb-1 sm:mb-2 ${textPrimary}`}>
              Business DNA Profile Generator
            </h2>
            <p className={`text-sm sm:text-base ${textSecondary}`}>
              Genera un'identità visiva professionale per il tuo brand.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Info Banner */}
      <div
        className={cn(
          'p-3 sm:p-4 rounded-lg sm:rounded-xl flex gap-2 sm:gap-3',
          isDark ? 'bg-gold/10 border border-gold/30' : 'bg-gold border border-gold'
        )}
      >
        <Info className={cn('w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0 mt-0.5', isDark ? 'text-gold' : 'text-gold')} />
        <p className={cn('text-xs sm:text-sm', isDark ? 'text-gold/90' : 'text-gold')}>
          <strong>Consiglio:</strong> Usa colori esadecimali (#RRGGBB), separa font e attributi con virgole.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
        {/* Company Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}
        >
          <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Informazioni Aziendali</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="company_name" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
                Nome Azienda <span className="text-gray-400">*</span>
              </label>
              <input
                id="company_name"
                type="text"
                required
                value={formData.company_name}
                onChange={(e) => updateField('company_name', e.target.value)}
                placeholder="Es. StudioCentOS"
                className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold min-h-[44px]`}
              />
            </div>
            <div>
              <label htmlFor="tagline" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
                Tagline <span className="text-gray-400">*</span>
              </label>
              <input
                id="tagline"
                type="text"
                required
                value={formData.tagline}
                onChange={(e) => updateField('tagline', e.target.value)}
                placeholder="Es. Innovazione Digitale per le PMI"
                className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold min-h-[44px]`}
              />
            </div>
          </div>

          <div>
            <label htmlFor="website" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
              Sito Web
            </label>
            <input
              id="website"
              type="url"
              value={formData.website}
              onChange={(e) => updateField('website', e.target.value)}
              placeholder="https://studiocentos.com"
              className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold min-h-[44px]`}
            />
          </div>

          {/* Logo Upload */}
          <div>
            <label className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
              Logo Aziendale
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/svg+xml,image/webp"
              onChange={handleLogoUpload}
              className="hidden"
              id="logo-upload"
            />

            {!logoPreview ? (
              <label
                htmlFor="logo-upload"
                className={cn(
                  'flex flex-col items-center justify-center w-full h-32 sm:h-40 rounded-lg sm:rounded-xl border-2 border-dashed cursor-pointer transition-colors',
                  isDark
                    ? 'border-white/20 hover:border-gold/50 bg-white/5'
                    : 'border-gray-300 hover:border-gold bg-gray-50'
                )}
              >
                <div className="flex flex-col items-center justify-center pt-2 pb-3">
                  <Upload className={cn('w-8 h-8 sm:w-10 sm:h-10 mb-2', textSecondary)} />
                  <p className={cn('text-sm font-medium', textLabel)}>Clicca o trascina il logo</p>
                  <p className={cn('text-xs mt-1', textSecondary)}>PNG, JPG, SVG, WebP (max 5MB)</p>
                </div>
              </label>
            ) : (
              <div className={cn(
                'relative rounded-lg sm:rounded-xl overflow-hidden border',
                borderColor
              )}>
                <img
                  src={logoPreview}
                  alt="Logo preview"
                  className={cn(
                    'w-full h-32 sm:h-40 object-contain p-4',
                    isDark ? 'bg-[#1A1A1A]' : 'bg-gray-50'
                  )}
                />
                <button
                  type="button"
                  onClick={removeLogo}
                  className="absolute top-2 right-2 p-1.5 rounded-full bg-gray-500 hover:bg-gray-500 text-white transition-colors"
                  aria-label="Rimuovi logo"
                >
                  <X className="w-4 h-4" />
                </button>
                <div className={cn(
                  'absolute bottom-0 left-0 right-0 px-3 py-2 text-xs truncate',
                  isDark ? 'bg-black/60 text-gray-300' : 'bg-white/80 text-gray-600'
                )}>
                  <ImageIcon className="w-3 h-3 inline mr-1" />
                  {logoFile?.name}
                </div>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="business_overview" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
              Descrizione Business <span className="text-gray-400">*</span>
            </label>
            <textarea
              id="business_overview"
              required
              rows={3}
              value={formData.business_overview}
              onChange={(e) => updateField('business_overview', e.target.value)}
              placeholder="Breve descrizione dell'azienda..."
              className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold resize-none`}
            />
          </div>
        </motion.div>

        {/* Visual Identity */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}
        >
          <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Identità Visiva</h3>

          <div>
            <label htmlFor="fonts" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
              Font del Brand
            </label>
            <input
              id="fonts"
              type="text"
              value={formData.fonts}
              onChange={(e) => updateField('fonts', e.target.value)}
              placeholder="Es. Basecold, Montserrat"
              className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold min-h-[44px]`}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
            <div>
              <label className={`block text-sm font-medium mb-1.5 ${textLabel}`}>Primario</label>
              <div className="flex gap-2">
                <input
                  type="color"
                  value={formData.primary_color}
                  onChange={(e) => updateField('primary_color', e.target.value)}
                  className={`w-12 h-[44px] border rounded-lg cursor-pointer ${borderColor}`}
                />
                <input
                  type="text"
                  value={formData.primary_color}
                  onChange={(e) => updateField('primary_color', e.target.value)}
                  className={`flex-1 px-3 py-2.5 rounded-lg border ${inputBg} min-h-[44px] text-sm`}
                />
              </div>
            </div>
            <div>
              <label className={`block text-sm font-medium mb-1.5 ${textLabel}`}>Secondario</label>
              <div className="flex gap-2">
                <input
                  type="color"
                  value={formData.secondary_color}
                  onChange={(e) => updateField('secondary_color', e.target.value)}
                  className={`w-12 h-[44px] border rounded-lg cursor-pointer ${borderColor}`}
                />
                <input
                  type="text"
                  value={formData.secondary_color}
                  onChange={(e) => updateField('secondary_color', e.target.value)}
                  className={`flex-1 px-3 py-2.5 rounded-lg border ${inputBg} min-h-[44px] text-sm`}
                />
              </div>
            </div>
            <div>
              <label className={`block text-sm font-medium mb-1.5 ${textLabel}`}>Accent</label>
              <div className="flex gap-2">
                <input
                  type="color"
                  value={formData.accent_color}
                  onChange={(e) => updateField('accent_color', e.target.value)}
                  className={`w-12 h-[44px] border rounded-lg cursor-pointer ${borderColor}`}
                />
                <input
                  type="text"
                  value={formData.accent_color}
                  onChange={(e) => updateField('accent_color', e.target.value)}
                  className={`flex-1 px-3 py-2.5 rounded-lg border ${inputBg} min-h-[44px] text-sm`}
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Brand Personality */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}
        >
          <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Personalità del Brand</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="brand_attributes" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
                Attributi
              </label>
              <input
                id="brand_attributes"
                type="text"
                value={formData.brand_attributes}
                onChange={(e) => updateField('brand_attributes', e.target.value)}
                placeholder="Professional, Modern, Innovative"
                className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold min-h-[44px]`}
              />
            </div>
            <div>
              <label htmlFor="tone_of_voice" className={`block text-sm font-medium mb-1.5 ${textLabel}`}>
                Tone of Voice
              </label>
              <input
                id="tone_of_voice"
                type="text"
                value={formData.tone_of_voice}
                onChange={(e) => updateField('tone_of_voice', e.target.value)}
                placeholder="Confident, Authentic, Friendly"
                className={`w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg sm:rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold min-h-[44px]`}
              />
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Save to Database Button */}
          <Button
            type="button"
            onClick={handleSave}
            disabled={isSaving || isGenerating}
            variant="outline"
            className={cn(
              "min-h-[44px] border-2",
              hasSettings
                ? "border-gold text-gold hover:bg-gold/10 dark:hover:bg-gold/20"
                : "border-gold text-gold hover:bg-gold/10"
            )}
          >
            {isSaving ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Salvataggio...
              </>
            ) : (
              <>
                {hasSettings ? <Cloud className="w-5 h-5 mr-2" /> : <Save className="w-5 h-5 mr-2" />}
                {hasSettings ? 'Sincronizzato' : 'Salva DNA'}
              </>
            )}
          </Button>

          <Button
            type="submit"
            disabled={isGenerating}
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
                Genera Business DNA
              </>
            )}
          </Button>
          <Button type="button" variant="outline" onClick={handleReset} disabled={isGenerating} className="min-h-[44px]">
            <RotateCcw className="w-5 h-5 mr-2" />
            Reset
          </Button>
        </div>

        {/* Sync Status Indicator */}
        {isLoadingSettings && (
          <div className={cn(
            'flex items-center gap-2 p-3 rounded-lg',
            isDark ? 'bg-white/5' : 'bg-gray-50'
          )}>
            <Loader2 className={cn('w-4 h-4 animate-spin', textSecondary)} />
            <span className={cn('text-sm', textSecondary)}>Caricamento impostazioni salvate...</span>
          </div>
        )}

        {hasSettings && !isLoadingSettings && (
          <div className={cn(
            'flex items-center gap-2 p-3 rounded-lg',
            isDark ? 'bg-gold/20 border border-gold' : 'bg-gold/10 border border-gold/20'
          )}>
            <Cloud className={cn('w-4 h-4', isDark ? 'text-gold' : 'text-gold')} />
            <span className={cn('text-sm', isDark ? 'text-gold' : 'text-gold')}>
              Impostazioni caricate dal database
            </span>
          </div>
        )}
      </form>

      {/* Error */}
      {error && (
        <div className={cn('p-3 sm:p-4 rounded-lg', isDark ? 'bg-white/10/20 border border-gray-600' : 'bg-gray-50 border border-gray-300')} role="alert">
          <p className={cn('text-sm', isDark ? 'text-gray-300' : 'text-gray-600')}>{error}</p>
        </div>
      )}

      {/* Preview */}
      {imageUrl && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className={`${cardBg} rounded-xl sm:rounded-2xl p-4 sm:p-6 space-y-4`}>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <h3 className={`text-lg sm:text-xl font-bold ${textPrimary}`}>Preview</h3>
            <Button onClick={download} className="bg-gold hover:bg-gold/90 min-h-[44px] w-full sm:w-auto">
              <Download className="w-5 h-5 mr-2" />
              Scarica PNG
            </Button>
          </div>
          <div className={cn('rounded-lg overflow-hidden', isDark ? 'bg-[#0A0A0A]' : 'bg-gray-100')}>
            <img src={imageUrl} alt={`Business DNA per ${formData.company_name}`} className="w-full h-auto" />
          </div>
        </motion.div>
      )}
    </div>
  );
}
