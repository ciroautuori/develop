import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  FileText,
  Search,
  RefreshCw,
  ExternalLink,
  Calendar,
  Building,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Clock,
  TrendingUp,
  Filter,
  Download
} from 'lucide-react'
import { useState } from 'react'

export const Route = createFileRoute('/dashboard/admin/bandi')({
  component: BandiAdminPage,
})

interface Bando {
  id: number
  title: string
  ente: string
  scadenza: string | null
  scadenza_raw: string
  link: string
  descrizione: string
  status: string
  fonte: string
  categoria: string
  keyword_match: string
  data_trovato: string
}

interface BandiResponse {
  items: Bando[]
  total: number
  page: number
  size: number
  pages: number
}

interface BandiStats {
  totali: number
  attivi: number
  scaduti: number
  in_scadenza: number
  nuovi_settimana: number
}

// Fetch bandi from API
async function fetchBandi(page: number, search?: string): Promise<BandiResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    per_page: '20',
  })
  if (search) params.append('search', search)

  const response = await fetch(`/api/v1/bandi/?${params}`)
  if (!response.ok) throw new Error('Errore caricamento bandi')
  return response.json()
}

// Fetch bandi stats
async function fetchBandiStats(): Promise<BandiStats> {
  const response = await fetch('/api/v1/bandi/stats')
  if (!response.ok) throw new Error('Errore caricamento statistiche')
  return response.json()
}

// Trigger AI search
async function triggerAISearch(): Promise<{ message: string }> {
  const response = await fetch('/api/v1/bandi/ai-search', {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Errore avvio ricerca AI')
  return response.json()
}

function BandiAdminPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const queryClient = useQueryClient()

  // Query per bandi
  const { data: bandiData, isLoading, error, refetch } = useQuery({
    queryKey: ['admin-bandi', currentPage, searchQuery],
    queryFn: () => fetchBandi(currentPage, searchQuery),
    staleTime: 30000, // 30 secondi
  })

  // Query per stats
  const { data: stats } = useQuery({
    queryKey: ['bandi-stats'],
    queryFn: fetchBandiStats,
    staleTime: 60000, // 1 minuto
  })

  // Mutation per AI search
  const aiSearchMutation = useMutation({
    mutationFn: triggerAISearch,
    onSuccess: () => {
      // Refresh dopo 3 secondi per dare tempo all'AI di trovare bandi
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['admin-bandi'] })
        queryClient.invalidateQueries({ queryKey: ['bandi-stats'] })
      }, 3000)
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setCurrentPage(1)
    refetch()
  }

  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'attivo':
        return <Badge className="bg-green-100 text-green-800 border-green-200">Attivo</Badge>
      case 'scaduto':
        return <Badge className="bg-red-100 text-red-800 border-red-200">Scaduto</Badge>
      case 'in_valutazione':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">In valutazione</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 border-gray-200">{status}</Badge>
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Non specificata'
    try {
      return new Date(dateString).toLocaleDateString('it-IT', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      })
    } catch {
      return dateString
    }
  }

  return (
    <DashboardLayout
      title="Gestione Bandi"
      description="Monitoraggio e gestione dei bandi trovati dall'AI Agent"
      userRole="admin"
      action={
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Aggiorna
          </Button>
          <Button
            onClick={() => aiSearchMutation.mutate()}
            disabled={aiSearchMutation.isPending}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          >
            <Sparkles className={`h-4 w-4 mr-2 ${aiSearchMutation.isPending ? 'animate-pulse' : ''}`} />
            {aiSearchMutation.isPending ? 'Ricerca in corso...' : '🤖 Cerca con AI'}
          </Button>
        </div>
      }
    >
      {/* AI Search Success Message */}
      {aiSearchMutation.isSuccess && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="flex items-center gap-3 py-4">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <p className="text-green-800">
              <strong>Ricerca AI avviata!</strong> I nuovi bandi appariranno tra qualche secondo.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-blue-800">Bandi Totali</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-900">{stats?.totali || bandiData?.total || 0}</div>
            <p className="text-xs text-blue-600 flex items-center mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              Database completo
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-green-800">Bandi Attivi</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-900">{stats?.attivi || 0}</div>
            <p className="text-xs text-green-600 flex items-center mt-1">
              <CheckCircle2 className="h-3 w-3 mr-1" />
              Scadenza futura
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-yellow-800">In Scadenza</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-900">{stats?.in_scadenza || 0}</div>
            <p className="text-xs text-yellow-600 flex items-center mt-1">
              <Clock className="h-3 w-3 mr-1" />
              Prossimi 30 giorni
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-red-800">Scaduti</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-900">{stats?.scaduti || 0}</div>
            <p className="text-xs text-red-600 flex items-center mt-1">
              <AlertCircle className="h-3 w-3 mr-1" />
              Archiviati
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-purple-800">Nuovi (7gg)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-900">{stats?.nuovi_settimana || 0}</div>
            <p className="text-xs text-purple-600 flex items-center mt-1">
              <Sparkles className="h-3 w-3 mr-1" />
              Trovati dall'AI
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Cerca e Filtra
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Cerca per titolo, ente, descrizione..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button type="submit">
              <Search className="h-4 w-4 mr-2" />
              Cerca
            </Button>
            <Button type="button" variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Esporta CSV
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Bandi List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Lista Bandi ({bandiData?.total || 0})
          </CardTitle>
          <CardDescription>
            Bandi trovati automaticamente dall'AI Agent per APS della Campania
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
              <span className="ml-3 text-gray-500">Caricamento bandi...</span>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-12 text-red-500">
              <AlertCircle className="h-6 w-6 mr-2" />
              Errore nel caricamento dei bandi
            </div>
          ) : (
            <div className="space-y-4">
              {bandiData?.items?.map((bando) => (
                <div
                  key={bando.id}
                  className="flex items-start justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors border border-gray-100"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 line-clamp-2 mb-1">
                          {bando.title}
                        </h3>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mb-2">
                          <span className="flex items-center gap-1">
                            <Building className="h-3.5 w-3.5" />
                            {bando.ente}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3.5 w-3.5" />
                            {bando.scadenza_raw || formatDate(bando.scadenza)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500 line-clamp-2">
                          {bando.descrizione}
                        </p>
                        <div className="flex gap-2 mt-2">
                          {getStatusBadge(bando.status)}
                          {bando.fonte && (
                            <Badge variant="outline" className="text-xs">
                              📍 {bando.fonte}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 ml-4">
                    {bando.link && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(bando.link, '_blank')}
                      >
                        <ExternalLink className="h-3.5 w-3.5 mr-1" />
                        Apri
                      </Button>
                    )}
                    <span className="text-xs text-gray-400">
                      {formatDate(bando.data_trovato)}
                    </span>
                  </div>
                </div>
              ))}

              {bandiData?.items?.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg font-medium">Nessun bando trovato</p>
                  <p className="text-sm">Prova a modificare i filtri o avvia una ricerca AI</p>
                </div>
              )}
            </div>
          )}

          {/* Pagination */}
          {bandiData && bandiData.pages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6 pt-6 border-t">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                Precedente
              </Button>
              <span className="text-sm text-gray-600">
                Pagina {currentPage} di {bandiData.pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.min(bandiData.pages, p + 1))}
                disabled={currentPage === bandiData.pages}
              >
                Successiva
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </DashboardLayout>
  )
}
