import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { issService } from '@/services/api'
import { Loader2, CalendarDays } from 'lucide-react'
import type { Evento } from '@/types/api'

export const Route = createFileRoute('/eventi')({
  component: EventiPage,
})

function EventiPage() {
  // Fetch eventi da API - dati reali dal database
  const { data: eventiData, isLoading } = useQuery({
    queryKey: ['eventi'],
    queryFn: () => issService.searchEventi({ limit: 20 }),
    staleTime: 1000 * 60 * 10,
  })

  const eventi = eventiData?.items || []

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50">
      <div className="bg-gradient-to-r from-[#7a2426] to-[#a53327] text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">
            🎪 Eventi & Workshop <span className="text-[#f4af00]">GRATUITI</span>
          </h1>
          <p className="text-xl">100% accessibili per tutti</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-iss-bordeaux-600" />
            <span className="ml-3 text-lg">Caricamento...</span>
          </div>
        ) : eventi.length === 0 ? (
          <div className="text-center py-20">
            <CalendarDays className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-600 mb-4">
              Sezione in costruzione
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              Gli eventi verranno aggiunti prossimamente dall'amministratore.
              Torna a visitarci presto!
            </p>
            <Button
              className="mt-6 bg-iss-bordeaux-600 hover:bg-iss-bordeaux-700"
              onClick={() => window.location.href = '/'}
            >
              Torna alla Home
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {eventi.map((evento: Evento) => (
              <Card key={evento.id} className="p-6 bg-white/90">
                <h3 className="text-xl font-bold mb-2">{evento.titolo}</h3>
                {evento.descrizione && (
                  <p className="text-gray-600 mb-4">{evento.descrizione}</p>
                )}
                <div className="space-y-2 mb-4">
                  {evento.data_inizio && (
                    <div className="text-sm text-gray-600">
                      📅 {formatDate(evento.data_inizio)}
                    </div>
                  )}
                  {evento.luogo && (
                    <div className="text-sm text-gray-600">
                      📍 {evento.luogo}
                    </div>
                  )}
                  {evento.posti_disponibili !== undefined && (
                    <div className="text-sm text-gray-600">
                      👥 {evento.posti_disponibili} posti disponibili
                    </div>
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <Badge className="bg-green-100 text-green-800">GRATUITO</Badge>
                  <Button className="bg-[#7a2426] hover:bg-[#a53327]">
                    Partecipa
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
