import { Card, CardContent } from '@/components/ui/card';
import {
  TrendingUp,
  Target,
  Clock,
  MapPin,
  Zap,
  Database,
  Search,
  Bell
} from 'lucide-react';

interface StatsSectionProps {
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

export function StatsSection({ stats }: StatsSectionProps) {
  // Solo statistiche REALI dal database
  const bandiAttivi = stats?.bandi_attivi || 0;
  const inScadenza = stats?.in_scadenza || 0;
  const bandiScaduti = stats?.bandi_scaduti || 0;
  const fonti = stats?.bandi_per_fonte ? Object.keys(stats.bandi_per_fonte).length : 0;

  // Statistiche principali - solo dati reali
  const mainStats = [
    {
      icon: Target,
      value: bandiAttivi > 0 ? bandiAttivi.toLocaleString() : '—',
      label: 'Bandi Attivi',
      description: 'Ancora candidabili',
      color: 'from-green-500 to-green-600',
      iconColor: 'text-green-600'
    },
    {
      icon: Clock,
      value: inScadenza > 0 ? inScadenza.toLocaleString() : '—',
      label: 'In Scadenza',
      description: 'Prossimi 7 giorni',
      color: 'from-orange-500 to-orange-600',
      iconColor: 'text-orange-600'
    },
    {
      icon: Database,
      value: bandiScaduti > 0 ? bandiScaduti.toLocaleString() : '—',
      label: 'Bandi Scaduti',
      description: 'Archiviati per storico',
      color: 'from-gray-400 to-gray-500',
      iconColor: 'text-gray-500'
    },
    {
      icon: MapPin,
      value: fonti > 0 ? fonti.toString() : '—',
      label: 'Fonti Monitorate',
      description: 'Enti e istituzioni',
      color: 'from-iss-bordeaux-500 to-iss-bordeaux-600',
      iconColor: 'text-iss-bordeaux-600'
    }
  ];

  // Features del sistema
  const features = [
    {
      icon: Zap,
      title: 'Ricerca AI',
      description: 'Intelligenza artificiale per trovare bandi rilevanti'
    },
    {
      icon: Bell,
      title: 'Notifiche',
      description: 'Alert automatici per nuovi bandi e scadenze'
    },
    {
      icon: Search,
      title: 'Filtri Avanzati',
      description: 'Cerca per fonte, categoria, importo'
    },
    {
      icon: TrendingUp,
      title: 'Monitoraggio 24/7',
      description: 'Sistema sempre attivo che cerca nuovi bandi'
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-iss-bordeaux-900 via-iss-bordeaux-800 to-iss-bordeaux-700 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute top-0 left-0 w-full h-full"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpolygon points='50 0 60 40 100 50 60 60 50 100 40 60 0 50 40 40'/%3E%3C/g%3E%3C/svg%3E")`
          }}
        />
      </div>

      <div className="container mx-auto px-3 sm:px-4 relative">
        {/* Section Header */}
        <div className="text-center mb-12 sm:mb-16">
          <div className="inline-flex items-center gap-2 bg-iss-gold-500 text-iss-bordeaux-900 px-3 sm:px-4 py-2 rounded-full text-xs sm:text-sm font-semibold mb-3 sm:mb-4">
            <Database className="w-3 h-3 sm:w-4 sm:h-4" />
            Dati in Tempo Reale
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 sm:mb-6">
            Il nostro database
            <span className="text-iss-gold-400 block">
              bandi
            </span>
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-iss-bordeaux-100 max-w-3xl mx-auto leading-relaxed">
            Monitoriamo automaticamente i principali enti erogatori di fondi
            per il Terzo Settore in Campania.
          </p>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 lg:gap-8 mb-12 sm:mb-16">
          {mainStats.map((stat, index) => (
            <Card
              key={index}
              className="bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/15 transition-all duration-300 hover:scale-105 group"
            >
              <CardContent className="p-3 sm:p-4 md:p-6 lg:p-8 text-center">
                <div className={`w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 bg-gradient-to-br ${stat.color} rounded-xl sm:rounded-2xl flex items-center justify-center mx-auto mb-3 sm:mb-4 lg:mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <stat.icon className="w-5 h-5 sm:w-6 sm:h-6 lg:w-8 lg:h-8 text-white" />
                </div>
                <div className="text-xl sm:text-2xl md:text-3xl lg:text-5xl font-bold text-white mb-1 sm:mb-2">
                  {stat.value}
                </div>
                <div className="text-xs sm:text-sm md:text-base lg:text-lg font-semibold text-iss-gold-300 mb-1 lg:mb-3">
                  {stat.label}
                </div>
                <div className="text-xs lg:text-sm text-iss-bordeaux-100 leading-relaxed">
                  {stat.description}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-8 lg:p-12 border border-white/10">
          <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-white text-center mb-6 sm:mb-8">
            Funzionalità della piattaforma
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center group">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-iss-gold-500 rounded-lg sm:rounded-xl flex items-center justify-center mx-auto mb-3 sm:mb-4 group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className="w-5 h-5 sm:w-6 sm:h-6 text-iss-bordeaux-900" />
                </div>
                <div className="text-sm sm:text-base lg:text-lg font-semibold text-white mb-1 sm:mb-2">
                  {feature.title}
                </div>
                <div className="text-xs lg:text-sm text-iss-bordeaux-200">
                  {feature.description}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-8 sm:mt-12">
          <div className="bg-gradient-to-r from-iss-gold-500 to-iss-gold-400 rounded-xl sm:rounded-2xl p-4 sm:p-6 md:p-8 lg:p-12 text-iss-bordeaux-900">
            <h3 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold mb-3 sm:mb-4">
              🎯 Inizia subito a esplorare i bandi
            </h3>
            <p className="text-sm sm:text-base lg:text-xl leading-relaxed max-w-4xl mx-auto mb-4 sm:mb-6">
              Accedi gratuitamente alla nostra piattaforma e trova le opportunità di finanziamento
              più adatte alla tua APS.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
              <button
                onClick={() => window.location.href = '/bandi'}
                className="bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-lg font-semibold transition-all duration-300 hover:scale-105 shadow-lg w-full sm:w-auto min-h-[44px]"
              >
                Esplora i Bandi
              </button>
              <button
                onClick={() => window.location.href = '/auth/register'}
                className="border-2 border-iss-bordeaux-900 text-iss-bordeaux-900 hover:bg-iss-bordeaux-900 hover:text-white px-6 sm:px-8 py-3 sm:py-4 rounded-lg font-semibold transition-all duration-300 hover:scale-105 w-full sm:w-auto min-h-[44px]"
              >
                Registrati Gratis
              </button>
            </div>
          </div>
        </div>

        {/* Real-time Indicator */}
        <div className="flex items-center justify-center mt-8 gap-3 text-iss-bordeaux-200">
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium">
            Sistema attivo • Dati aggiornati
          </span>
        </div>
      </div>
    </section>
  );
}
