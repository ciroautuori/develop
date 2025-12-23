/**
 * Contact Section Component - CTA finale (PRIMA di Booking)
 */

import { Button } from '../../../shared/components/ui/button';
import { useLanguage } from '../i18n';

export function ContactSection() {
  const { t } = useLanguage();

  return (
    <section id="contatti" className="max-w-4xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32 text-center">
      <div className="bg-card backdrop-blur rounded-2xl sm:rounded-3xl p-6 sm:p-12 lg:p-16 border border-border shadow-sm">
        <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-light mb-4 sm:mb-6 text-foreground">
          {t.contact.title}
        </h2>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground mb-8 sm:mb-12">
          {t.contact.subtitle}
          <span className="hidden sm:inline"><br /></span>
          <span className="inline sm:hidden"> </span>
          {t.contact.subtitleExtra}
        </p>
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 lg:gap-6 justify-center">
          <Button asChild size="lg" className="px-6 sm:px-8 lg:px-12 py-3 sm:py-4 lg:py-5 h-auto text-sm sm:text-base lg:text-lg">
            <a href="mailto:info@studiocentos.it">
              info@studiocentos.it
            </a>
          </Button>
          <Button asChild variant="outline" size="lg" className="px-6 sm:px-8 lg:px-12 py-3 sm:py-4 lg:py-5 h-auto text-sm sm:text-base lg:text-lg">
            <a href="#prenota">
              {t.contact.cta}
            </a>
          </Button>
        </div>
        <p className="mt-6 sm:mt-8 text-xs sm:text-sm text-muted-foreground px-2">
          {t.contact.responseTime} <span className="hidden sm:inline">•</span><span className="inline sm:hidden"><br /></span> {t.contact.freeConsult} <span className="hidden sm:inline">•</span><span className="inline sm:hidden"><br /></span> Made in Italy 🇮🇹
        </p>
      </div>
    </section>
  );
}
