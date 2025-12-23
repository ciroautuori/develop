import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { issService } from '@/services/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Loader2, Rocket } from 'lucide-react'

export const Route = createFileRoute('/progetti')({
  component: ProgettiPage,
})

function ProgettiPage() {
  // Fetch progetti da API - dati reali dal database
  const { data: progettiData, isLoading } = useQuery({
    queryKey: ['progetti'],
    queryFn: () => issService.getProgetti({ limit: 20 }),
    staleTime: 1000 * 60 * 10,
  })

  const progetti = progettiData?.items || []

  const getStatoColor = (stato: string) => {
    switch (stato) {
      case 'in_corso': return 'bg-blue-100 text-blue-800'
      case 'completato': return 'bg-green-100 text-green-800'
      case 'pianificato': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-green-50">
      <div className="bg-gradient-to-r from-[#7a2426] to-[#a53327] text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">
            🚀 Progetti <span className="text-[#f4af00]">ISS</span>
          </h1>
          <p className="text-xl">Innovazione sociale per la Campania</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-iss-bordeaux-600" />
            <span className="ml-3 text-lg">Caricamento...</span>
          </div>
        ) : progetti.length === 0 ? (
          <div className="text-center py-20">
            <Rocket className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-600 mb-4">
              Sezione in costruzione
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              I progetti verranno aggiunti prossimamente dall'amministratore.
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
            {progetti.map((progetto: any) => (
              <Card key={progetto.id} className="p-6 bg-white/90">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold">{progetto.nome}</h3>
                  {progetto.stato && (
                    <Badge className={getStatoColor(progetto.stato)}>
                      {progetto.stato.replace('_', ' ')}
                    </Badge>
                  )}
                </div>

                {progetto.descrizione_breve && (
                  <p className="text-gray-600 mb-4">{progetto.descrizione_breve}</p>
                )}

                <div className="space-y-2 mb-4">
                  {progetto.budget_totale !== undefined && (
                    <div className="text-sm text-gray-600">
                      💰 Budget: €{progetto.budget_totale.toLocaleString()}
                    </div>
                  )}
                  {progetto.team_size !== undefined && (
                    <div className="text-sm text-gray-600">
                      👥 Team: {progetto.team_size} persone
                    </div>
                  )}
                  {progetto.impatto_sociale && (
                    <div className="text-sm text-gray-600">
                      📈 {progetto.impatto_sociale}
                    </div>
                  )}
                </div>

                <Button className="w-full bg-[#7a2426] hover:bg-[#a53327]">
                  Scopri di più
                </Button>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
