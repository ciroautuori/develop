/**
 * StudiocentOS Landing Page
 * AI-Powered Development Made in Italy
 * Supporta traduzioni multilingua (it, en, es)
 * Con animazioni CSS native per performance ottimali
 */

import '../../app/assets/styles/landing.css';
import { useEffect } from 'react';
import { LanguageProvider, useLanguage } from './i18n';
import { LandingHeader } from './components/LandingHeader';
import { HeroSection } from './components/HeroSection';
import { StorySection } from './components/StorySection';
import { ProcessSection } from './components/ProcessSection';
import { ServicesSection } from './components/ServicesSection';
import { CoursesSection } from './components/CoursesSection';
import { CaseStudiesSection } from './components/CaseStudiesSection';
import { ToolAISection } from './components/ToolAISection';
import { BookingTimeline } from './components/BookingTimeline';
import { ContactSection } from './components/ContactSection';
import { LandingFooter } from './components/LandingFooter';
import { CookieBanner } from './components/CookieBanner';
import { ChatWidget } from '../support/components/ChatWidget';
import { usePortfolio } from './hooks/usePortfolio';
import { translations } from './i18n/translations';
import { RevealOnScroll } from '../../shared/components/ui/reveal-on-scroll';
import { Button } from '../../shared/components/ui/button';

// Get translations for loading/error screens (before context is available)
function getLoadingTranslations() {
  const saved = localStorage.getItem('studiocentos-language') as 'it' | 'en' | 'es';
  const lang = saved && ['it', 'en', 'es'].includes(saved) ? saved : 'it';
  return translations[lang].loading;
}

function LoadingScreen() {
  const t = getLoadingTranslations();
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <div className="text-primary text-xl">{t.text}</div>
      </div>
    </div>
  );
}

function ErrorScreen({ error }: { error: Error }) {
  const t = getLoadingTranslations();
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="text-muted-foreground text-5xl mb-4">⚠️</div>
        <h2 className="text-2xl font-light text-foreground mb-4">{t.errorTitle}</h2>
        <p className="text-muted-foreground mb-6">{error.message}</p>
        <Button
          onClick={() => window.location.reload()}
          size="lg"
          className="w-full sm:w-auto"
        >
          {t.retry}
        </Button>
      </div>
    </div>
  );
}

// Inner component che ha accesso al LanguageContext
function LandingContent() {
  const { language } = useLanguage();

  const {
    data,
    loading: projectsLoading,
    error: projectsError
  } = usePortfolio(language);

  // 📊 Track landing page view
  useEffect(() => {
    // trackPageView('/', 'StudioCentOS - Software House Salerno');
  }, []);

  if (projectsLoading) {
    return <LoadingScreen />;
  }

  if (projectsError) {
    return <ErrorScreen error={projectsError} />;
  }

  if (!data) {
    const t = getLoadingTranslations();
    return <ErrorScreen error={new Error(t.noData)} />;
  }

  return (
    <div className="min-h-screen bg-background text-foreground antialiased transition-colors duration-300">
      <LandingHeader />

      {/* 1. HERO - Above the fold */}
      <RevealOnScroll animation="fade-in-scale">
        <HeroSection />
      </RevealOnScroll>

      {/* 2. STORY - Chi sono + Trust */}
      <RevealOnScroll id="chi-siamo" animation="fade-in-left">
        <StorySection />
      </RevealOnScroll>

      {/* 3. PROCESS - Come lavoro */}
      <RevealOnScroll animation="fade-in-up">
        <ProcessSection />
      </RevealOnScroll>

      {/* 4. SERVICES - Servizi (dal database con traduzioni) */}
      <RevealOnScroll id="servizi" animation="fade-in-up">
        <ServicesSection services={data.services} />
      </RevealOnScroll>

      {/* 6. PROJECTS - Progetti realizzati (dal database con traduzioni) */}
      <RevealOnScroll id="progetti" animation="fade-in-up">
        <CaseStudiesSection projects={data.projects} />
      </RevealOnScroll>

      {/* 5. COURSES - Academy (dal database con traduzioni) */}
      <RevealOnScroll id="corsi" animation="fade-in-up">
        <CoursesSection courses={data.courses || []} />
      </RevealOnScroll>

      {/* 7. TOOLAI - AI Tools del Giorno */}
      <RevealOnScroll id="toolai" animation="fade-in-up">
        <ToolAISection />
      </RevealOnScroll>

      {/* 8. CONTACT - CTA forte */}
      <RevealOnScroll id="contatti" animation="fade-in-up">
        <ContactSection />
      </RevealOnScroll>

      {/* 9. BOOKING TIMELINE - Urgency */}
      <RevealOnScroll animation="fade-in-up">
        <BookingTimeline />
      </RevealOnScroll>

      {/* <div className="h-[20vh] flex items-center justify-center">
        <p className="text-xl">Debug Mode: Half Sections Active</p>
      </div> */}

      <LandingFooter />

      {/* 9. CHAT WIDGET - AI Support (bottom right) */}
      <ChatWidget />

      {/* 10. COOKIE BANNER - GDPR Compliant */}
      <CookieBanner />
    </div>
  );
}

export function StudiocentosLanding() {
  return (
    <LanguageProvider>
      <LandingContent />
    </LanguageProvider>
  );
}

export default StudiocentosLanding;
