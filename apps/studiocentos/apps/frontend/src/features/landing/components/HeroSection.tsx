/**
 * Hero Section Component
 */

import { Button } from '../../../shared/components/ui/button';
import { useLanguage } from '../i18n';

export function HeroSection() {
  const { t } = useLanguage();

  return (
    <section className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 pt-20 sm:pt-24">
      <div className="max-w-4xl w-full">
        <div className="inline-block mb-4 sm:mb-6 px-3 sm:px-4 py-1.5 sm:py-2 bg-muted rounded-full text-xs sm:text-sm text-muted-foreground">
          {t.hero.greeting}
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-light mb-6 sm:mb-8 leading-tight text-foreground">
          {t.hero.title1}<br />
          <span className="text-primary font-medium">{t.hero.titleHighlight}</span><br />
          {t.hero.title2}
        </h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground mb-8 sm:mb-10 leading-relaxed">
          {t.hero.description} <span className="text-primary">{t.hero.descHighlight}</span>.
          <span className="hidden sm:inline"><br /></span>
          <span className="inline sm:hidden"> </span>
          {t.hero.descTime}
          <span className="hidden sm:inline"><br /></span>
          <span className="inline sm:hidden"> </span>
          <span className="text-foreground font-medium">{t.hero.madeIn}</span>
        </p>

        {/* Social proof immediato */}
        <div className="grid grid-cols-3 gap-3 sm:gap-6 lg:gap-8 mb-8 sm:mb-12 p-4 sm:p-6 lg:p-8 bg-card rounded-xl sm:rounded-2xl border border-border">
          <div className="text-center">
            <div className="text-xl sm:text-2xl lg:text-3xl font-light text-primary mb-0.5 sm:mb-1">850+</div>
            <div className="text-xs sm:text-sm text-muted-foreground">{t.hero.stats.files}</div>
          </div>
          <div className="text-center">
            <div className="text-xl sm:text-2xl lg:text-3xl font-light text-primary mb-0.5 sm:mb-1">45gg</div>
            <div className="text-xs sm:text-sm text-muted-foreground">{t.hero.stats.time}</div>
          </div>
          <div className="text-center">
            <div className="text-xl sm:text-2xl lg:text-3xl font-light text-primary mb-0.5 sm:mb-1">100%</div>
            <div className="text-xs sm:text-sm text-muted-foreground">{t.hero.stats.satisfaction}</div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
          <a href="#progetti" className="w-full sm:w-auto">
            <Button size="lg" className="w-full sm:w-auto font-medium">
              {t.hero.cta.projects}
            </Button>
          </a>
          <a href="#contatti" className="w-full sm:w-auto">
            <Button variant="outline" size="lg" className="w-full sm:w-auto font-medium">
              {t.hero.cta.talk}
            </Button>
          </a>
        </div>
      </div>
    </section>
  );
}
