import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { issService } from '@/services/api'
import { Loader2, GraduationCap } from 'lucide-react'
import type { Corso } from '@/types/api'

export const Route = createFileRoute('/corsi')({
  component: CorsiPage,
})

function CorsiPage() {
  // Fetch corsi da API - dati reali dal database
  const { data: corsiData, isLoading } = useQuery({
    queryKey: ['corsi'],
    queryFn: () => issService.searchCorsi({ limit: 20 }),
    staleTime: 1000 * 60 * 10,
  })

  const corsi = corsiData?.items || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="bg-gradient-to-r from-[#7a2426] to-[#a53327] text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">
            🎓 Formazione Digitale <span className="text-[#f4af00]">GRATUITA</span>
          </h1>
          <p className="text-xl">Corsi professionali per tutti</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-iss-bordeaux-600" />
            <span className="ml-3 text-lg">Caricamento...</span>
          </div>
        ) : corsi.length === 0 ? (
          <div className="text-center py-20">
            <GraduationCap className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-600 mb-4">
              Sezione in costruzione
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              I corsi di formazione verranno aggiunti prossimamente dall'amministratore.
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {corsi.map((corso: Corso) => (
              <Card key={corso.id} className="p-6 bg-white/90">
                <h3 className="text-xl font-bold mb-2">{corso.titolo}</h3>
                {corso.descrizione && (
                  <p className="text-gray-600 mb-4">{corso.descrizione}</p>
                )}
                <div className="flex justify-between items-center">
                  <Badge className="bg-green-100 text-green-800">GRATUITO</Badge>
                  <Button className="bg-[#7a2426] hover:bg-[#a53327]">
                    Iscriviti
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
