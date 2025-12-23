import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { ModernHeroSection } from '@/components/home/ModernHeroSection';
import { FeatureSection } from '@/components/home/FeatureSection';
import { StatsSection } from '@/components/home/StatsSection';
import { SmartBandoCard } from '@/components/bandi/SmartBandoCard';
import { Button } from '@/components/ui/button';
import { Target } from 'lucide-react';
import { bandoAPI } from '@/services/api';

export const Route = createFileRoute('/')({
  component: HomePage,
});

function HomePage() {
  // Fetch recent bandi
  const { data: recentBandi, isLoading: isLoadingBandi } = useQuery({
    queryKey: ['recent-bandi'],
    queryFn: () => bandoAPI.getRecent(3),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Fetch stats for dashboard and hero
  const { data: bandoStats, isLoading: isLoadingStats } = useQuery({
    queryKey: ['bando-stats'],
    queryFn: bandoAPI.getStats,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });

  return (
    <div className="min-h-screen -mt-16 lg:-mt-18">
      {/* Modern Hero Section */}
      <ModernHeroSection stats={bandoStats} />

      {/* Features Section */}
      <FeatureSection />

      {/* Stats Section - Solo dati reali */}
      <StatsSection stats={bandoStats} />


      {/* Recent Bandi Section - Simplified */}
      {recentBandi?.items && recentBandi.items.length > 0 && (
        <section className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-iss-bordeaux-900 mb-4">
                Bandi in Evidenza
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Ultimi bandi aggiunti al sistema, perfetti per APS campane
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-12">
              {recentBandi.items.slice(0, 3).map((bando) => (
                <SmartBandoCard
                  key={bando.id}
                  bando={bando}
                  onView={() => window.open(bando.link, '_blank', 'noopener,noreferrer')}
                />
              ))}
            </div>

            <div className="text-center">
              <Button asChild size="lg" className="bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800">
                <a href="/bandi">
                  <Target className="w-5 h-5 mr-2" />
                  Vedi tutti i bandi
                </a>
              </Button>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
