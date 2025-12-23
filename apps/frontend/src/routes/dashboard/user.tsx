import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { StatCard } from '@/components/dashboard/StatCard'
import { QuickAction } from '@/components/dashboard/QuickAction'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Calendar,
  Heart,
  FileText,
  BookOpen,
  Search,
  ExternalLink,
  Clock,
  Euro
} from 'lucide-react'

interface Bando {
  id: number
  title: string
  ente: string
  fonte: string
  scadenza?: string | null
  scadenza_raw?: string
  importo?: number | null
  categoria?: string
  link?: string
}

interface BandiResponse {
  items: Bando[]
  total: number
}

export const Route = createFileRoute('/dashboard/user')({
  component: UserDashboard,
})

function UserDashboard() {
  // Fetch bandi attivi (i più recenti/in scadenza)
  const { data: bandiData, isLoading: bandiLoading } = useQuery<BandiResponse>({
    queryKey: ['user-bandi'],
    queryFn: async () => {
      const response = await fetch('/api/v1/bandi/?limit=6&status=active')
      if (!response.ok) return { items: [], total: 0 }
      return response.json()
    }
  })

  // Fetch bandi stats
  const { data: bandiStats } = useQuery({
    queryKey: ['bandi-stats'],
    queryFn: async () => {
      const response = await fetch('/api/v1/bandi/stats')
      if (!response.ok) return { totali: 0, attivi: 0, in_scadenza: 0, fonti: {} }
      return response.json()
    }
  })

  const bandi = bandiData?.items || []
  const totalBandi = bandiStats?.totali || bandiData?.total || 0

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Da definire'
    return new Date(dateStr).toLocaleDateString('it-IT', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  const formatAmount = (amount?: number) => {
    if (!amount) return '-'
    if (amount >= 1000000) return `€${(amount / 1000000).toFixed(1)}M`
    if (amount >= 1000) return `€${(amount / 1000).toFixed(0)}K`
    return `€${amount}`
  }

  const isExpiringSoon = (dateStr?: string) => {
    if (!dateStr) return false
    const days = Math.ceil((new Date(dateStr).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    return days <= 30 && days > 0
  }

  return (
    <DashboardLayout
      title="Benvenuto nella tua Dashboard"
      description="Scopri i bandi attivi e le opportunità per la tua organizzazione"
      userRole="user"
      action={
        <Link to="/bandi">
          <Button>
            <Search className="h-4 w-4 mr-2" />
            Cerca Bandi
          </Button>
        </Link>
      }
    >
      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Bandi Disponibili"
          value={totalBandi}
          change="Aggiornati ogni 6h"
          trend="up"
          icon={FileText}
        />
        <StatCard
          title="Bandi Attivi"
          value={bandiStats?.attivi ?? 0}
          change="Aperti ora"
          trend="up"
          icon={Calendar}
        />
        <StatCard
          title="In Scadenza"
          value={bandiStats?.in_scadenza ?? 0}
          change="Prossimi 30 giorni"
          trend={bandiStats?.in_scadenza > 5 ? "down" : "up"}
          icon={Clock}
        />
        <StatCard
          title="Fonti Monitorate"
          value={Object.keys(bandiStats?.fonti || {}).length}
          change="AI Agent attivo"
          trend="up"
          icon={Search}
        />
      </div>

      {/* Bandi Cards */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">📋 Bandi in Evidenza</h2>
          <Link to="/bandi" className="text-iss-primary hover:underline text-sm flex items-center gap-1">
            Vedi tutti <ExternalLink className="h-3 w-3" />
          </Link>
        </div>

        {bandiLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map(i => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                  <div className="h-3 bg-gray-100 rounded w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <div className="h-3 bg-gray-100 rounded w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : bandi.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="text-5xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold mb-2">Nessun bando trovato</h3>
              <p className="text-gray-600">L'AI Agent sta cercando nuovi bandi per te.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {bandi.map((bando) => (
              <Card key={bando.id} className="hover:shadow-lg transition-shadow group">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base line-clamp-2 group-hover:text-iss-primary transition-colors">
                      {bando.title}
                    </CardTitle>
                    {isExpiringSoon(bando.scadenza) && (
                      <Badge variant="destructive" className="shrink-0 text-xs">
                        ⏰ Scade presto
                      </Badge>
                    )}
                  </div>
                  <CardDescription className="flex items-center gap-1">
                    🏛️ {bando.ente || 'Ente non specificato'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex flex-wrap gap-2 text-xs">
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {bando.scadenza_raw || formatDate(bando.scadenza)}
                    </Badge>
                    {bando.importo && (
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Euro className="h-3 w-3" />
                        {formatAmount(bando.importo)}
                      </Badge>
                    )}
                    {bando.categoria && (
                      <Badge variant="secondary" className="text-xs">
                        {bando.categoria}
                      </Badge>
                    )}
                  </div>
                  <Badge variant="outline" className="text-xs">
                    📍 {bando.fonte}
                  </Badge>
                  {bando.link && bando.link !== 'Link non disponibile' && (
                    <a
                      href={bando.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-sm text-iss-primary hover:underline mt-2"
                    >
                      Vai al bando <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Link to="/bandi" className="block">
          <QuickAction
            title="Cerca Bandi"
            description={`${totalBandi} opportunità disponibili`}
            icon={Search}
            onClick={() => {}}
            variant="primary"
          />
        </Link>
        <QuickAction
          title="Eventi"
          description="Formazione e networking"
          icon={Calendar}
          onClick={() => {}}
          variant="secondary"
        />
        <QuickAction
          title="Volontariato"
          description="Opportunità di impegno"
          icon={Heart}
          onClick={() => {}}
          variant="default"
        />
        <QuickAction
          title="Risorse"
          description="Guide e materiali"
          icon={BookOpen}
          onClick={() => {}}
          variant="destructive"
        />
      </div>
    </DashboardLayout>
  )
}
