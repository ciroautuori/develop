/**
 * Contact Section Component - CTA finale (PRIMA di Booking)
 */

import { Button } from '../../../shared/components/ui/button';
import { useLanguage } from '../i18n';

export function ContactSection() {
  const { t } = useLanguage();

  return (
    <section id="contatti" className="max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-24 lg:py-32">
      <div className="bg-card backdrop-blur rounded-3xl p-8 sm:p-12 border border-border shadow-sm">

        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* LEFT: Standard Contact */}
          <div className="text-center lg:text-left space-y-6">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-light text-foreground">
              {t.contact.title}
            </h2>
            <p className="text-lg text-muted-foreground max-w-lg mx-auto lg:mx-0">
              {t.contact.subtitle} {t.contact.subtitleExtra}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start pt-4">
              <Button asChild size="lg" className="h-12 px-8 text-base">
                <a href="mailto:info@studiocentos.it">info@studiocentos.it</a>
              </Button>
              <Button asChild variant="outline" size="lg" className="h-12 px-8 text-base">
                <a href="#prenota">{t.contact.cta}</a>
              </Button>
            </div>

            <p className="text-sm text-muted-foreground pt-4">
              {t.contact.responseTime} • {t.contact.freeConsult}
            </p>
          </div>

          {/* RIGHT: AI Office Service (New) */}
          <div className="relative">
            {/* Decorative gradient border effect */}
            <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-br from-primary via-transparent to-primary opacity-30 blur-sm pointer-events-none" />

            <div className="relative bg-background/50 rounded-2xl p-8 border border-primary/20 hover:border-primary/50 transition-colors duration-300">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-6">
                ✨ New Service
              </div>

              <h3 className="text-2xl font-light mb-2 text-foreground">
                {t.contact.officeAI.title}
              </h3>
              <p className="text-primary font-medium mb-4">
                {t.contact.officeAI.subtitle}
              </p>

              <p className="text-muted-foreground mb-8 leading-relaxed text-sm">
                {t.contact.officeAI.description}
              </p>

              <Button asChild size="lg" variant="secondary" className="w-full sm:w-auto h-12 px-8">
                <a href="mailto:consulting@studiocentos.it?subject=Richiesta%20Office%20AI%20Consulting">
                  {t.contact.officeAI.cta}
                </a>
              </Button>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
