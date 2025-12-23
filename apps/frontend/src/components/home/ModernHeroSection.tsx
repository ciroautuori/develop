// Removed unused Link import
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  Heart,
  Target,
  Users,
  Shield,
  Accessibility,
  Globe,
  Clock,
  Zap
} from 'lucide-react';

interface ModernHeroSectionProps {
  stats?: {
    total_bandi?: number;
    bandi_attivi?: number;
    bandi_scaduti?: number;
    in_scadenza?: number;
    bandi_per_fonte?: Record<string, number>;
    ultimi_trovati?: number;
    media_giornaliera?: number;
  };
}

export function ModernHeroSection({ stats }: ModernHeroSectionProps) {
  // Solo statistiche reali dal database
  const totalBandi = stats?.total_bandi || 0;
  const inScadenza = stats?.in_scadenza || 0;
  const fontiMonitorate = stats?.bandi_per_fonte ? Object.keys(stats.bandi_per_fonte).length : 0;

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-iss-bordeaux-900 via-iss-bordeaux-800 to-iss-bordeaux-700">
      {/* Background Pattern */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}
      />

      {/* Floating Elements */}
      <div className="absolute top-20 left-10 w-20 h-20 bg-iss-gold-400/10 rounded-full blur-xl animate-pulse" />
      <div className="absolute top-40 right-20 w-32 h-32 bg-iss-gold-400/5 rounded-full blur-2xl animate-pulse delay-1000" />
      <div className="absolute bottom-20 left-1/4 w-16 h-16 bg-white/5 rounded-full blur-xl animate-pulse delay-2000" />

      <div className="relative container mx-auto px-3 sm:px-4 pt-20 sm:pt-24 md:pt-28 lg:pt-36 pb-12 sm:pb-16 md:pb-20 lg:pb-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Hero Content */}
          <div className="text-white space-y-8">
            <div className="space-y-6">
              {/* Badge */}
              <Badge className="bg-iss-gold-500 text-iss-bordeaux-900 hover:bg-iss-gold-400 font-semibold px-4 py-2 text-sm">
                <Heart className="w-4 h-4 mr-2" />
                100% Gratuito e Open Source
              </Badge>

              {/* Main Headline */}
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                Monitoraggio bandi
                <span className="text-iss-gold-400 block mt-2">
                  per il Terzo Settore
                </span>
                <span className="text-white block">
                  campano
                </span>
              </h1>

              {/* Subtitle */}
              <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-iss-bordeaux-100 leading-relaxed max-w-2xl">
                ISS monitora automaticamente i bandi di finanziamento per APS della Campania,
                usando l'intelligenza artificiale per trovare le migliori opportunità.
              </p>

              {/* Value Proposition */}
              <div className="flex flex-wrap gap-4 text-iss-bordeaux-200">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-iss-gold-400" />
                  <span className="text-sm font-medium">Ricerca AI-powered</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-iss-gold-400" />
                  <span className="text-sm font-medium">Aggiornato quotidianamente</span>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <Button
                variant="outline"
                size="lg"
                className="border-2 border-white/80 bg-white/10 backdrop-blur-sm text-white hover:bg-white hover:text-iss-bordeaux-900 hover:border-white px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg font-semibold transition-all duration-300 hover:scale-105 w-full sm:w-auto min-h-[44px]"
                onClick={() => window.location.href = '/bandi'}
              >
                <Target className="w-5 h-5 mr-2" />
                Esplora Bandi
              </Button>

              <Button
                size="lg"
                className="bg-iss-gold-500 hover:bg-iss-gold-400 text-iss-bordeaux-900 font-semibold px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 w-full sm:w-auto min-h-[44px]"
                onClick={() => window.location.href = '/auth/register'}
              >
                <Users className="w-5 h-5 mr-2" />
                Registrati Gratis
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-col sm:flex-row sm:flex-wrap items-start sm:items-center gap-3 sm:gap-6 pt-6 sm:pt-8 border-t border-iss-bordeaux-600">
              <div className="flex items-center gap-2 text-iss-bordeaux-200">
                <Shield className="w-4 h-4 sm:w-5 sm:h-5 text-iss-gold-400" />
                <span className="text-xs sm:text-sm font-medium">Sicuro e Certificato</span>
              </div>
              <div className="flex items-center gap-2 text-iss-bordeaux-200">
                <Accessibility className="w-4 h-4 sm:w-5 sm:h-5 text-iss-gold-400" />
                <span className="text-xs sm:text-sm font-medium">WCAG 2.1 AA</span>
              </div>
              <div className="flex items-center gap-2 text-iss-bordeaux-200">
                <Globe className="w-4 h-4 sm:w-5 sm:h-5 text-iss-gold-400" />
                <span className="text-xs sm:text-sm font-medium">Open Source</span>
              </div>
            </div>
          </div>

          {/* Hero Stats Grid - Solo dati reali */}
          <div className="grid grid-cols-2 gap-3 sm:gap-4 md:gap-6">
            <Card className="bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/15 transition-all duration-300 hover:scale-105">
              <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-iss-gold-400 mb-1 sm:mb-2">
                  {totalBandi > 0 ? totalBandi : '—'}
                </div>
                <div className="text-xs sm:text-sm text-iss-bordeaux-100 font-medium">
                  Bandi nel Database
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/15 transition-all duration-300 hover:scale-105">
              <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-orange-400 mb-1 sm:mb-2">
                  {inScadenza > 0 ? inScadenza : '—'}
                </div>
                <div className="text-xs sm:text-sm text-iss-bordeaux-100 font-medium">
                  In Scadenza (7gg)
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/15 transition-all duration-300 hover:scale-105">
              <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-iss-gold-400 mb-1 sm:mb-2">
                  {fontiMonitorate > 0 ? fontiMonitorate : '—'}
                </div>
                <div className="text-xs sm:text-sm text-iss-bordeaux-100 font-medium">
                  Fonti Monitorate
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/15 transition-all duration-300 hover:scale-105">
              <CardContent className="p-3 sm:p-4 md:p-6 text-center">
                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-iss-gold-400 mb-1 sm:mb-2">
                  24/7
                </div>
                <div className="text-xs sm:text-sm text-iss-bordeaux-100 font-medium">
                  Monitoraggio Continuo
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Wave Separator */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" className="w-full h-12 fill-white">
          <path d="M0,64L48,69.3C96,75,192,85,288,80C384,75,480,53,576,48C672,43,768,53,864,64C960,75,1056,85,1152,80C1248,75,1344,53,1392,42.7L1440,32L1440,120L1392,120C1344,120,1248,120,1152,120C1056,120,960,120,864,120C768,120,672,120,576,120C480,120,384,120,288,120C192,120,96,120,48,120L0,120Z" />
        </svg>
      </div>
    </section>
  );
}
