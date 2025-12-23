import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { issService } from '@/services/api'
import { Loader2, HeartHandshake } from 'lucide-react'

export const Route = createFileRoute('/volontariato')({
  component: VolontariatoPage,
})

function VolontariatoPage() {
  // Fetch opportunità volontariato da API - dati reali dal database
  const { data: volontariatoData, isLoading } = useQuery({
    queryKey: ['volontariato'],
    queryFn: () => issService.getVolontariato({ limit: 20 }),
    staleTime: 1000 * 60 * 10,
  })

  const opportunita = volontariatoData?.items || []

  const getTipoColor = (tipo: string) => {
    switch (tipo) {
      case 'continuativo': return 'bg-blue-100 text-blue-800'
      case 'progetto': return 'bg-purple-100 text-purple-800'
      case 'evento': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-orange-50">
      <div className="bg-gradient-to-r from-[#7a2426] to-[#a53327] text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">
            🤝 Volontariato <span className="text-[#f4af00]">Digitale</span>
          </h1>
          <p className="text-xl">Metti le tue competenze al servizio del sociale</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-iss-bordeaux-600" />
            <span className="ml-3 text-lg">Caricamento...</span>
          </div>
        ) : opportunita.length === 0 ? (
          <div className="text-center py-20">
            <HeartHandshake className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-600 mb-4">
              Sezione in costruzione
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              Le opportunità di volontariato verranno aggiunte prossimamente dall'amministratore.
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
            {opportunita.map((opp: any) => (
              <Card key={opp.id} className="p-6 bg-white/90">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold">{opp.titolo}</h3>
                  <div className="flex gap-2">
                    {opp.tipo_impegno && (
                      <Badge className={getTipoColor(opp.tipo_impegno)}>
                        {opp.tipo_impegno}
                      </Badge>
                    )}
                    {opp.match_score && opp.match_score > 80 && (
                      <Badge className="bg-green-100 text-green-800">
                        {opp.match_score}% Match
                      </Badge>
                    )}
                  </div>
                </div>

                {opp.descrizione_breve && (
                  <p className="text-gray-600 mb-4">{opp.descrizione_breve}</p>
                )}

                <div className="space-y-2 mb-4">
                  {opp.ore_settimanali && (
                    <div className="text-sm text-gray-600">
                      ⏰ {opp.ore_settimanali} ore/settimana
                    </div>
                  )}
                  {opp.luogo && (
                    <div className="text-sm text-gray-600">
                      📍 {opp.luogo}
                    </div>
                  )}
                  {opp.skills_richieste && opp.skills_richieste.length > 0 && (
                    <div className="text-sm text-gray-600">
                      🛠️ Skills: {opp.skills_richieste.join(', ')}
                    </div>
                  )}
                </div>

                <Button
                  className="w-full bg-[#7a2426] hover:bg-[#a53327]"
                  disabled={!opp.candidature_aperte}
                >
                  {opp.candidature_aperte !== false ? 'Candidati' : 'Candidature chiuse'}
                </Button>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
