import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { ModernHeroSection } from '@/components/home/ModernHeroSection';
import { FeatureSection } from '@/components/home/FeatureSection';
import { StatsSection } from '@/components/home/StatsSection';
import { SmartBandoCard } from '@/components/bandi/SmartBandoCard';
import { Button } from '@/components/ui/button';
import { Target, Calendar, MapPin, ArrowRight, Building, Star } from 'lucide-react';
import { bandoAPI, eventsAPI, partnerAPI } from '@/services/api';
import { Badge } from '@/components/ui/badge';

export const Route = createFileRoute('/')({
  component: HomePage,
});

function HomePage() {
  // Fetch recent bandi
  const { data: recentBandi } = useQuery({
    queryKey: ['recent-bandi'],
    queryFn: () => bandoAPI.getRecent(3),
    staleTime: 1000 * 60 * 5,
  });

  // Fetch upcoming events
  const { data: events } = useQuery({
    queryKey: ['upcoming-events'],
    queryFn: () => eventsAPI.list({ limit: 4 }),
  });

  // Fetch featured partners
  const { data: partnersData } = useQuery({
    queryKey: ['featured-partners'],
    queryFn: () => partnerAPI.list({ limit: 6 }),
  });

  // Fetch stats
  const { data: bandoStats } = useQuery({
    queryKey: ['bando-stats'],
    queryFn: bandoAPI.getStats,
  });

  return (
    <div className="min-h-screen -mt-16 lg:-mt-18">
      <ModernHeroSection stats={bandoStats} />

      <FeatureSection />

      {/* Stats Real-Time */}
      <StatsSection stats={bandoStats} />

      {/* Upcoming Events Section */}
      <section className="py-24 bg-gray-50/50">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-4">
            <div className="max-w-xl">
              <Badge className="mb-4 bg-iss-gold-500 text-iss-bordeaux-900 border-none px-4 py-1">Community Hub</Badge>
              <h2 className="text-4xl font-bold text-iss-bordeaux-900 tracking-tight">Prossimi Eventi</h2>
              <p className="text-gray-600 mt-2">Unisciti ai nostri workshop, hackathon e momenti di formazione per innovare insieme il terzo settore.</p>
            </div>
            <Button variant="ghost" className="text-iss-bordeaux-900 font-bold group">
              Vedi Calendario Completo
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {events?.items?.map((event: any) => (
              <div key={event.id} className="bg-white rounded-2xl p-6 border group hover:border-iss-gold-500 transition-colors shadow-sm">
                <div className="flex justify-between items-start mb-4">
                  <div className="bg-iss-bordeaux-50 text-iss-bordeaux-900 p-3 rounded-xl font-bold text-center">
                    <div className="text-xs uppercase">{new Date(event.data_evento).toLocaleString('it-IT', { month: 'short' })}</div>
                    <div className="text-xl">{new Date(event.data_evento).getDate()}</div>
                  </div>
                  <Badge variant="outline" className="capitalize text-[10px]">{event.tipo}</Badge>
                </div>
                <h3 className="font-bold text-lg mb-4 line-clamp-2 min-h-[3.5rem]">{event.titolo}</h3>
                <div className="space-y-2 text-sm text-gray-500 mb-6">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    {new Date(event.data_evento).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <span className="truncate">{event.luogo}</span>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="w-full border-iss-bordeaux-200 text-iss-bordeaux-900 hover:bg-iss-bordeaux-50">
                  Scopri di più
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Bandi */}
      {recentBandi?.items && recentBandi.items.length > 0 && (
        <section className="py-24 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-iss-bordeaux-900 tracking-tight mb-4">Bandi in Evidenza</h2>
              <p className="text-gray-600 max-w-2xl mx-auto italic">Algoritmi AI potenziati per trovare le migliori opportunità di finanziamento.</p>
            </div>
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 mb-12">
              {recentBandi.items.slice(0, 3).map((bando) => (
                <SmartBandoCard key={bando.id} bando={bando} onView={() => window.open(bando.link, '_blank', 'noopener,noreferrer')} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Partners Section */}
      <section className="py-24 bg-iss-bordeaux-900 text-white overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-iss-gold-500/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl" />
        <div className="container mx-auto px-4 relative">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4 tracking-tight">Rete dei Partner</h2>
            <p className="text-iss-gold-400 font-medium">Insieme ad oltre 50 istituzioni e aziende per il territorio</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
            {partnersData?.partners?.map((partner: any) => (
              <div key={partner.id} className="flex flex-col items-center justify-center grayscale hover:grayscale-0 transition-all opacity-70 hover:opacity-100">
                <div className="h-20 w-32 bg-white/5 backdrop-blur-sm rounded-xl flex items-center justify-center p-4 border border-white/10">
                  {partner.logo_url ? (
                    <img src={partner.logo_url} alt={partner.nome_organizzazione} className="max-h-full max-w-full object-contain" />
                  ) : (
                    <Building className="h-8 w-8 text-white/20" />
                  )}
                </div>
                <span className="text-[10px] mt-2 font-semibold uppercase tracking-wider text-white/40">{partner.tipo}</span>
              </div>
            ))}
          </div>

          <div className="mt-20 text-center">
            <div className="inline-flex items-center bg-white/5 border border-white/10 rounded-full px-6 py-2 backdrop-blur-md">
              <Star className="h-4 w-4 text-iss-gold-500 mr-2" />
              <span className="text-sm">Vuoi diventare partner di ISS? <a href="#" className="font-bold underline decoration-iss-gold-500 underline-offset-4">Collabora con noi</a></span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
