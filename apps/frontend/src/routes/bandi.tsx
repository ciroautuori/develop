import { createFileRoute } from '@tanstack/react-router';
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SmartBandoCard } from '@/components/bandi/SmartBandoCard';
import { AISearchHeader } from '@/components/bandi/AISearchHeader';
import { SmartBandoFilters } from '@/components/bandi/SmartBandoFilters';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { bandoAPI } from '@/services/api';
import { BandoFilters as BandoFiltersType, Bando } from '@/types/api';
import { Search, SlidersHorizontal } from 'lucide-react';

// Validation schema per filtri (esteso con sezione)
const filtersSchema = {
  search: '',
  sezione: 'tutti', // NUOVO: sezione principale
  fonte: 'all',
  categoria: 'all',
  status: 'all',
  importo_min: 0,
  importo_max: 1000000,
  data_scadenza_da: '',
  data_scadenza_a: '',
  sort_by: 'relevance',
  sort_order: 'desc',
  per_page: 20,
  page: 1,
  subFonti: '', // NUOVO: sub-fonti specifiche per sezione
} as const;

export const Route = createFileRoute('/bandi')({
  component: BandiPage,
  validateSearch: (search: Record<string, unknown>): BandoFiltersType => {
    return {
      search: (search.search as string) || filtersSchema.search,
      fonte: (search.fonte as string) || filtersSchema.fonte,
      categoria: (search.categoria as string) || filtersSchema.categoria,
      status: (search.status as string) || filtersSchema.status,
      importo_min: Number(search.importo_min) || filtersSchema.importo_min,
      importo_max: Number(search.importo_max) || filtersSchema.importo_max,
      data_scadenza_da: (search.data_scadenza_da as string) || filtersSchema.data_scadenza_da,
      data_scadenza_a: (search.data_scadenza_a as string) || filtersSchema.data_scadenza_a,
      sort_by: (search.sort_by as string) || filtersSchema.sort_by,
      sort_order: (search.sort_order as string) || filtersSchema.sort_order,
      per_page: Number(search.per_page) || filtersSchema.per_page,
      page: Number(search.page) || filtersSchema.page,
    };
  },
});

function BandiPage() {
  const navigate = Route.useNavigate();
  const filters = Route.useSearch();
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [savedBandi, setSavedBandi] = useState<Set<string>>(new Set());
  const [isAISearching, setIsAISearching] = useState(false);

  // Mappatura stato filtri per la sidebar con sezioni
  const filtersState = useMemo(() => ({
    sezione: (filters as any).sezione || 'tutti',
    categorie: filters.categoria !== 'all' ? [filters.categoria] : [],
    importoMin: filters.importo_min,
    importoMax: filters.importo_max,
    soloAttivi: filters.status === 'attivo',
    scadenzaBreve: filters.status === 'in_scadenza',
    fonte: filters.fonte !== 'all' ? [filters.fonte] : [],
    subFonti: (filters as any).subFonti ? (filters as any).subFonti.split(',').filter(Boolean) : [],
  }), [filters]);

  // Query bandi con supporto AI semantica
  const {
    data: bandiResponse,
    isLoading,
    error
  } = useQuery({
    queryKey: ['bandi', filters],
    queryFn: async () => {
      // Ricerca standard con filtri
      return bandoAPI.search(filters);
    },
    staleTime: 5 * 60 * 1000,
  });

  // Query stats per conteggi reali
  const { data: statsData } = useQuery({
    queryKey: ['bando-stats'],
    queryFn: () => bandoAPI.getStats(),
    staleTime: 10 * 60 * 1000,
  });

  const bandi = bandiResponse?.items || [];
  const totalCount = bandiResponse?.total || 0;

  // Conteggio bandi per sezione da dati reali
  const bandoCountBySection = useMemo(() => {
    const perFonte = statsData?.bandi_per_fonte || {};
    return {
      tutti: statsData?.totali || totalCount,
      terzo_settore: (perFonte['fondazione_comunita'] || 0) + (perFonte['csv_salerno'] || 0),
      invitalia: perFonte['invitalia'] || 0,
      pnrr: perFonte['pnrr_italia_domani'] || 0,
      regionali: perFonte['regione_campania'] || 0,
      locali: perFonte['comune_salerno'] || 0,
    };
  }, [statsData, totalCount]);

  // Handler aggiornamento filtri dalla sidebar (con supporto sezioni)
  const handleFiltersChange = (newFilters: any) => {
    const updatedSearchParams: any = { ...filters, page: 1 };

    // NUOVO: Gestione sezione
    updatedSearchParams.sezione = newFilters.sezione || 'tutti';

    // Mapping inverso da Sidebar state a URL params
    if (newFilters.categorie.length > 0) updatedSearchParams.categoria = newFilters.categorie[0];
    else updatedSearchParams.categoria = 'all';

    // Gestione fonte basata su sezione
    if (newFilters.sezione && newFilters.sezione !== 'tutti') {
      // Mappa sezione a fonte per il backend
      const sezioneToFonte: Record<string, string> = {
        terzo_settore: 'terzo_settore',
        invitalia: 'invitalia',
        pnrr: 'pnrr',
        regionali: 'regione_campania',
        locali: 'locale',
      };
      updatedSearchParams.fonte = sezioneToFonte[newFilters.sezione] || 'all';
    } else if (newFilters.fonte.length > 0) {
      updatedSearchParams.fonte = newFilters.fonte[0];
    } else {
      updatedSearchParams.fonte = 'all';
    }

    // NUOVO: Sub-fonti specifiche
    if (newFilters.subFonti && newFilters.subFonti.length > 0) {
      updatedSearchParams.subFonti = newFilters.subFonti.join(',');
    } else {
      updatedSearchParams.subFonti = '';
    }

    updatedSearchParams.importo_min = newFilters.importoMin;
    updatedSearchParams.importo_max = newFilters.importoMax;

    if (newFilters.scadenzaBreve) updatedSearchParams.status = 'in_scadenza';
    else if (newFilters.soloAttivi) updatedSearchParams.status = 'attivo';
    else updatedSearchParams.status = 'all';

    navigate({ search: updatedSearchParams });
  };

  const handleSearch = async (query: string) => {
    setIsAISearching(true);
    try {
      // RESET FILTRI quando si fa una nuova ricerca - cerca su TUTTI i bandi
      navigate({
        search: {
          search: query,
          fonte: 'all',
          categoria: 'all',
          status: 'all',
          sezione: 'tutti',
          subFonti: '',
          importo_min: 0,
          importo_max: 1000000,
          page: 1
        }
      });
    } finally {
      setIsAISearching(false);
    }
  };

  // Salva/rimuovi bando (simulato locale + API)
  const toggleSaveBando = async (bandoId: string) => {
    try {
      if (savedBandi.has(bandoId)) {
        await bandoAPI.unsave(bandoId);
        setSavedBandi(prev => {
          const next = new Set(prev);
          next.delete(bandoId);
          return next;
        });
      } else {
        await bandoAPI.save(bandoId);
        setSavedBandi(prev => new Set(prev).add(bandoId));
      }
    } catch (error) {
      console.error('Errore salvataggio bando:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Container principale */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

        {/* AI Search Header - NON sticky, compatto */}
        <div className="mb-6">
          <AISearchHeader
            onSearch={handleSearch}
            initialQuery={filters.search}
            isSearching={isAISearching || isLoading}
          />
        </div>

        {/* Layout principale: Sidebar + Content */}
        <div className="flex gap-6">

          {/* Sidebar Filtri - Desktop only */}
          <aside className="hidden lg:block w-72 flex-shrink-0">
            <div className="sticky top-4">
              <SmartBandoFilters
                filters={filtersState}
                onChange={handleFiltersChange}
                bandoCount={bandoCountBySection}
              />
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0">

            {/* Mobile: Bottone Filtri */}
            <div className="lg:hidden mb-4">
              <Button
                variant="outline"
                className="w-full flex justify-between bg-white border-gray-200 shadow-sm"
                onClick={() => setShowMobileFilters(true)}
              >
                <span className="flex items-center gap-2 text-gray-700 font-medium">
                  <SlidersHorizontal className="w-4 h-4" /> Filtri e Sezioni
                </span>
                <span className="bg-iss-bordeaux-100 text-iss-bordeaux-700 px-2 py-0.5 rounded-full text-xs font-bold">
                  {totalCount}
                </span>
              </Button>
            </div>

            {/* Banner ricerca attiva */}
            {filters.search && (
              <div className="mb-4 p-3 bg-iss-bordeaux-50 border border-iss-bordeaux-200 rounded-lg flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-iss-bordeaux-600" />
                  <span className="text-sm text-iss-bordeaux-800">
                    Risultati per: <strong>"{filters.search}"</strong>
                  </span>
                </div>
                <Button
                  onClick={() => navigate({ search: { ...filters, search: '', fonte: 'all', categoria: 'all', page: 1 } })}
                  variant="ghost"
                  size="sm"
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  ✕ Cancella
                </Button>
              </div>
            )}

            {/* Header risultati */}
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-lg font-bold text-gray-900">
                {filters.search ? 'Risultati' : 'Tutti i Bandi'}
              </h1>
              <span className="text-sm text-gray-500 bg-white px-3 py-1 rounded-full border">
                <strong className="text-iss-bordeaux-600">{totalCount}</strong> bandi
              </span>
            </div>

            {/* Contenuto principale */}
            {error ? (
              <Card className="border-red-200 bg-red-50">
                <CardContent className="p-6 text-center">
                  <p className="text-red-600 font-medium">Errore: {error.message}</p>
                  <Button onClick={() => window.location.reload()} variant="outline" size="sm" className="mt-3">
                    Riprova
                  </Button>
                </CardContent>
              </Card>
            ) : isLoading ? (
              <div className="grid gap-4 sm:grid-cols-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-72 bg-white rounded-lg border animate-pulse" />
                ))}
              </div>
            ) : bandi.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border">
                <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Nessun bando trovato</h3>
                <p className="text-gray-500 mb-4">Prova a modificare i filtri o la ricerca.</p>
                <Button
                  onClick={() => navigate({ search: { ...filters, search: '', fonte: 'all', categoria: 'all' } })}
                  variant="outline"
                >
                  Mostra tutti i bandi
                </Button>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {bandi.map((bando: Bando) => (
                  <SmartBandoCard
                    key={bando.id}
                    bando={bando}
                    isSaved={savedBandi.has(String(bando.id))}
                    onSave={() => toggleSaveBando(String(bando.id))}
                    onView={() => window.open(bando.link, '_blank', 'noopener,noreferrer')}
                  />
                ))}
              </div>
            )}

            {/* Paginazione */}
            {totalCount > filters.per_page && (
              <div className="mt-8 flex justify-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={filters.page === 1}
                  onClick={() => navigate({ search: { ...filters, page: filters.page - 1 } })}
                >
                  ← Precedente
                </Button>
                <span className="px-3 py-2 text-sm text-gray-600">
                  Pagina {filters.page}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate({ search: { ...filters, page: filters.page + 1 } })}
                >
                  Successiva →
                </Button>
              </div>
            )}
          </main>
        </div>
      </div>

      {/* Mobile Filters Drawer */}
      {showMobileFilters && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowMobileFilters(false)} />
          <div className="absolute inset-y-0 right-0 w-full max-w-sm bg-white shadow-xl flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-bold text-lg">Filtri</h3>
              <Button variant="ghost" size="sm" onClick={() => setShowMobileFilters(false)}>
                ✕
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <SmartBandoFilters
                filters={filtersState}
                onChange={handleFiltersChange}
                bandoCount={bandoCountBySection}
              />
            </div>
            <div className="p-4 border-t">
              <Button
                className="w-full bg-iss-bordeaux-600 hover:bg-iss-bordeaux-700 text-white"
                onClick={() => setShowMobileFilters(false)}
              >
                Mostra {totalCount} risultati
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
