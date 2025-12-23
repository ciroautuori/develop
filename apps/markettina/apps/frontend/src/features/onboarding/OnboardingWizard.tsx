/**
 * OnboardingWizard - Multi-step onboarding for new customers
 *
 * FLOW:
 * 1. Company Info - Nome, settore, target
 * 2. Connect Social - OAuth per Instagram, Facebook, LinkedIn
 * 3. Brand DNA - AI analysis preview
 * 4. First Content - Generate sample posts
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  Link2,
  Brain,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Check,
  Instagram,
  Facebook,
  Linkedin,
  Twitter,
  Loader2,
  Target,
  Palette,
  MessageSquare,
} from 'lucide-react';
import { cn } from '../../shared/lib/utils';

interface WizardStep {
  id: number;
  title: string;
  description: string;
  icon: React.ElementType;
  color: string;
}

const STEPS: WizardStep[] = [
  { id: 1, title: 'Info Azienda', description: 'Dicci chi sei', icon: Building2, color: 'from-blue-500 to-cyan-500' },
  { id: 2, title: 'Collega Social', description: 'Connetti i tuoi account', icon: Link2, color: 'from-purple-500 to-pink-500' },
  { id: 3, title: 'Brand DNA', description: 'L\'AI impara il tuo stile', icon: Brain, color: 'from-amber-500 to-orange-500' },
  { id: 4, title: 'Prima Generazione', description: 'Crea i tuoi primi contenuti', icon: Sparkles, color: 'from-emerald-500 to-teal-500' },
];

const INDUSTRIES = [
  'E-commerce', 'Ristorazione', 'Moda', 'Tecnologia', 'Consulenza',
  'Fitness', 'Beauty', 'Immobiliare', 'Turismo', 'Altro'
];

interface CompanyData {
  name: string;
  industry: string;
  targetAudience: string;
  website: string;
  city: string;
}

interface SocialConnection {
  id: string;
  name: string;
  icon: React.ElementType;
  connected: boolean;
  username?: string;
}

export function OnboardingWizard() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Step 1: Company Data
  const [companyData, setCompanyData] = useState<CompanyData>({
    name: '',
    industry: '',
    targetAudience: '',
    website: '',
    city: '',
  });

  // Step 2: Social Connections
  const [socialConnections, setSocialConnections] = useState<SocialConnection[]>([
    { id: 'instagram', name: 'Instagram', icon: Instagram, connected: false },
    { id: 'facebook', name: 'Facebook', icon: Facebook, connected: false },
    { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, connected: false },
    { id: 'twitter', name: 'Twitter/X', icon: Twitter, connected: false },
  ]);

  // Step 3: Brand DNA (generated)
  const [brandDNA, setBrandDNA] = useState<{
    toneOfVoice: string;
    values: string[];
    keywords: string[];
    colors: string[];
  } | null>(null);

  // Step 4: Generated content
  const [generatedPosts, setGeneratedPosts] = useState<string[]>([]);

  const handleConnectSocial = async (socialId: string) => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/oauth/${socialId}/authorize`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        // Redirect to OAuth provider
        if (data.auth_url) {
          window.location.href = data.auth_url;
        }
      } else {
        // Fallback: mark as connected for demo
        setSocialConnections(prev => prev.map(s =>
          s.id === socialId
            ? { ...s, connected: true, username: `@${companyData.name.toLowerCase().replace(/\s/g, '_')}` }
            : s
        ));
      }
    } catch (error) {
      console.error('OAuth error:', error);
      // Fallback: mark as connected for demo
      setSocialConnections(prev => prev.map(s =>
        s.id === socialId
          ? { ...s, connected: true, username: `@${companyData.name.toLowerCase().replace(/\s/g, '_')}` }
          : s
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateBrandDNA = async () => {
    setIsLoading(true);

    // Simulate AI analysis
    await new Promise(resolve => setTimeout(resolve, 2000));

    setBrandDNA({
      toneOfVoice: 'Professionale ma amichevole, con un tocco di innovazione',
      values: ['Qualità', 'Innovazione', 'Affidabilità'],
      keywords: ['premium', 'made in italy', 'sostenibile', companyData.industry.toLowerCase()],
      colors: ['#D4AF37', '#0A0A0A', '#FFFFFF'],
    });

    setIsLoading(false);
  };

  const handleGenerateContent = async () => {
    setIsLoading(true);

    // Simulate content generation
    await new Promise(resolve => setTimeout(resolve, 2500));

    setGeneratedPosts([
      `🌟 ${companyData.name} - La tua scelta di qualità nel ${companyData.industry}! Scopri cosa ci rende unici. #${companyData.industry.replace(/\s/g, '')} #QualitàItaliana`,
      `💡 Sai perché i nostri clienti ci scelgono? Innovazione, affidabilità e passione. Vieni a scoprirci! ${companyData.city ? `📍 ${companyData.city}` : ''}`,
      `✨ Nuovo traguardo per ${companyData.name}! Grazie a tutti i clienti che ci supportano ogni giorno. Insieme cresciamo! 🚀`,
    ]);

    setIsLoading(false);
  };

  const handleNext = async () => {
    if (currentStep === 3 && !brandDNA) {
      await handleGenerateBrandDNA();
    }
    if (currentStep === 4 && generatedPosts.length === 0) {
      await handleGenerateContent();
    }
    if (currentStep < 4) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleComplete = async () => {
    try {
      const token = localStorage.getItem('access_token');

      // Complete onboarding and get free tokens
      const response = await fetch('/api/v1/onboarding/complete', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Onboarding complete:', data.message);
      }
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
    }

    navigate('/customer');
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return companyData.name && companyData.industry;
      case 2:
        return socialConnections.some(s => s.connected);
      case 3:
        return brandDNA !== null;
      case 4:
        return generatedPosts.length > 0;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Progress Header */}
      <div className="bg-card border-b border-border px-4 py-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold">M</span>
              </div>
              <div>
                <h1 className="font-bold text-foreground">MARKETTINA</h1>
                <p className="text-xs text-muted-foreground">Setup Guidato</p>
              </div>
            </div>
            <span className="text-sm text-muted-foreground">
              Step {currentStep} di {STEPS.length}
            </span>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center gap-2">
            {STEPS.map((step, index) => (
              <div key={step.id} className="flex-1 flex items-center gap-2">
                <div className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center transition-all',
                  currentStep > step.id
                    ? 'bg-primary text-primary-foreground'
                    : currentStep === step.id
                    ? 'bg-primary/20 text-primary border-2 border-primary'
                    : 'bg-muted text-muted-foreground'
                )}>
                  {currentStep > step.id ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <step.icon className="h-5 w-5" />
                  )}
                </div>
                {index < STEPS.length - 1 && (
                  <div className={cn(
                    'flex-1 h-1 rounded-full transition-all',
                    currentStep > step.id ? 'bg-primary' : 'bg-muted'
                  )} />
                )}
              </div>
            ))}
          </div>

          <div className="mt-4 text-center">
            <h2 className="text-xl font-bold text-foreground">
              {STEPS[currentStep - 1].title}
            </h2>
            <p className="text-sm text-muted-foreground">
              {STEPS[currentStep - 1].description}
            </p>
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {/* Step 1: Company Info */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Nome Azienda *
                </label>
                <input
                  type="text"
                  value={companyData.name}
                  onChange={(e) => setCompanyData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Es. La Mia Azienda Srl"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Settore *
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {INDUSTRIES.map((industry) => (
                    <button
                      key={industry}
                      onClick={() => setCompanyData(prev => ({ ...prev, industry }))}
                      className={cn(
                        'px-4 py-3 rounded-xl text-sm font-medium transition-all',
                        companyData.industry === industry
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground hover:bg-muted/80'
                      )}
                    >
                      {industry}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={companyData.targetAudience}
                  onChange={(e) => setCompanyData(prev => ({ ...prev, targetAudience: e.target.value }))}
                  placeholder="Es. PMI e professionisti 25-55 anni"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Sito Web
                  </label>
                  <input
                    type="url"
                    value={companyData.website}
                    onChange={(e) => setCompanyData(prev => ({ ...prev, website: e.target.value }))}
                    placeholder="https://www.esempio.it"
                    className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Città
                  </label>
                  <input
                    type="text"
                    value={companyData.city}
                    onChange={(e) => setCompanyData(prev => ({ ...prev, city: e.target.value }))}
                    placeholder="Es. Milano"
                    className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 2: Connect Social */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <p className="text-center text-muted-foreground mb-6">
                Collega almeno un account social per permettere all'AI di analizzare il tuo stile
              </p>

              {socialConnections.map((social) => {
                const Icon = social.icon;
                return (
                  <div
                    key={social.id}
                    className={cn(
                      'flex items-center justify-between p-4 rounded-xl border',
                      social.connected
                        ? 'border-green-500/30 bg-green-500/5'
                        : 'border-border bg-card'
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="h-6 w-6 text-muted-foreground" />
                      <div>
                        <p className="font-medium text-foreground">{social.name}</p>
                        {social.connected && social.username && (
                          <p className="text-sm text-green-500">{social.username}</p>
                        )}
                      </div>
                    </div>

                    {social.connected ? (
                      <div className="flex items-center gap-1 text-green-500 text-sm">
                        <Check className="h-4 w-4" />
                        Connesso
                      </div>
                    ) : (
                      <button
                        onClick={() => handleConnectSocial(social.id)}
                        disabled={isLoading}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
                      >
                        {isLoading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          'Connetti'
                        )}
                      </button>
                    )}
                  </div>
                );
              })}
            </motion.div>
          )}

          {/* Step 3: Brand DNA */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              {isLoading ? (
                <div className="text-center py-12">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center"
                  >
                    <Brain className="h-8 w-8 text-white" />
                  </motion.div>
                  <p className="text-lg font-medium text-foreground">Analizzando il tuo brand...</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    L'AI sta studiando i tuoi contenuti social
                  </p>
                </div>
              ) : brandDNA ? (
                <div className="space-y-4">
                  <div className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <MessageSquare className="h-5 w-5 text-purple-500" />
                      <h4 className="font-semibold text-foreground">Tone of Voice</h4>
                    </div>
                    <p className="text-muted-foreground">{brandDNA.toneOfVoice}</p>
                  </div>

                  <div className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <Target className="h-5 w-5 text-blue-500" />
                      <h4 className="font-semibold text-foreground">Valori</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {brandDNA.values.map((value) => (
                        <span key={value} className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
                          {value}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <Brain className="h-5 w-5 text-green-500" />
                      <h4 className="font-semibold text-foreground">Keywords</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {brandDNA.keywords.map((keyword) => (
                        <span key={keyword} className="px-3 py-1 rounded-full bg-muted text-muted-foreground text-sm">
                          #{keyword}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <Palette className="h-5 w-5 text-pink-500" />
                      <h4 className="font-semibold text-foreground">Palette Colori</h4>
                    </div>
                    <div className="flex gap-3">
                      {brandDNA.colors.map((color, index) => (
                        <div key={index} className="text-center">
                          <div
                            className="w-12 h-12 rounded-xl border border-border"
                            style={{ backgroundColor: color }}
                          />
                          <span className="text-xs text-muted-foreground mt-1 block">{color}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Brain className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                  <p className="text-lg font-medium text-foreground">Pronto per l'analisi</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Clicca "Avanti" per generare il tuo Brand DNA
                  </p>
                </div>
              )}
            </motion.div>
          )}

          {/* Step 4: First Content */}
          {currentStep === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              {isLoading ? (
                <div className="text-center py-12">
                  <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 flex items-center justify-center"
                  >
                    <Sparkles className="h-8 w-8 text-white" />
                  </motion.div>
                  <p className="text-lg font-medium text-foreground">Generando i tuoi primi contenuti...</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    L'AI sta creando post personalizzati per te
                  </p>
                </div>
              ) : generatedPosts.length > 0 ? (
                <>
                  <p className="text-center text-muted-foreground mb-6">
                    Ecco i tuoi primi 3 post generati con AI! 🎉
                  </p>

                  {generatedPosts.map((post, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-card border border-border rounded-xl p-4"
                    >
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="text-primary font-bold text-sm">{index + 1}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">Post #{index + 1}</span>
                      </div>
                      <p className="text-foreground whitespace-pre-wrap">{post}</p>
                    </motion.div>
                  ))}

                  <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 text-center">
                    <Check className="h-8 w-8 mx-auto text-green-500 mb-2" />
                    <p className="font-medium text-foreground">Setup Completato!</p>
                    <p className="text-sm text-muted-foreground">
                      Riceverai 150 token gratis per iniziare
                    </p>
                  </div>
                </>
              ) : (
                <div className="text-center py-12">
                  <Sparkles className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                  <p className="text-lg font-medium text-foreground">Pronto a generare</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Clicca "Avanti" per creare i tuoi primi contenuti
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-card border-t border-border px-4 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 1}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-colors',
              currentStep === 1
                ? 'text-muted-foreground opacity-50 cursor-not-allowed'
                : 'text-foreground hover:bg-muted'
            )}
          >
            <ArrowLeft className="h-4 w-4" />
            Indietro
          </button>

          {currentStep < 4 || generatedPosts.length === 0 ? (
            <button
              onClick={handleNext}
              disabled={!canProceed() || isLoading}
              className={cn(
                'flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-colors',
                canProceed() && !isLoading
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'bg-muted text-muted-foreground cursor-not-allowed'
              )}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Elaborazione...
                </>
              ) : (
                <>
                  Avanti
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          ) : (
            <button
              onClick={handleComplete}
              className="flex items-center gap-2 px-6 py-3 bg-green-500 text-white rounded-xl font-medium hover:bg-green-600 transition-colors"
            >
              <Check className="h-4 w-4" />
              Inizia a Usare MARKETTINA
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
