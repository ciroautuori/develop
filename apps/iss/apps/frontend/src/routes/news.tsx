import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { issService } from '@/services/api'
import { Loader2, Newspaper } from 'lucide-react'

export const Route = createFileRoute('/news')({
  component: NewsPage,
})

function NewsPage() {
  // Fetch news da API - dati reali dal database
  const { data: newsData, isLoading } = useQuery({
    queryKey: ['news'],
    queryFn: issService.getNews,
    staleTime: 1000 * 60 * 10,
  })

  const articoli = newsData?.items || []

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  const getCategoriaColor = (categoria: string) => {
    switch (categoria) {
      case 'formazione': return 'bg-blue-100 text-blue-800'
      case 'partnership': return 'bg-purple-100 text-purple-800'
      case 'eventi': return 'bg-green-100 text-green-800'
      case 'progetti': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-cyan-50">
      <div className="bg-gradient-to-r from-[#7a2426] to-[#a53327] text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">
            📰 News & <span className="text-[#f4af00]">Blog</span>
          </h1>
          <p className="text-xl">Tutte le novità dal mondo ISS</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-iss-bordeaux-600" />
            <span className="ml-3 text-lg">Caricamento...</span>
          </div>
        ) : articoli.length === 0 ? (
          <div className="text-center py-20">
            <Newspaper className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-600 mb-4">
              Sezione in costruzione
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              Le news verranno pubblicate prossimamente dall'amministratore.
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
          <>
            {/* Articoli in evidenza */}
            {articoli.filter((art: any) => art.in_evidenza).length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold mb-6">📌 In Evidenza</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {articoli.filter((art: any) => art.in_evidenza).map((articolo: any) => (
                    <Card key={articolo.id} className="p-6 bg-white/90 border-l-4 border-[#f4af00]">
                      <div className="flex justify-between items-start mb-4">
                        {articolo.categoria && (
                          <Badge className={getCategoriaColor(articolo.categoria)}>
                            {articolo.categoria}
                          </Badge>
                        )}
                        {articolo.data_pubblicazione && (
                          <span className="text-sm text-gray-500">
                            {formatDate(articolo.data_pubblicazione)}
                          </span>
                        )}
                      </div>

                      <h3 className="text-xl font-bold mb-3">{articolo.titolo}</h3>
                      {articolo.contenuto_breve && (
                        <p className="text-gray-600 mb-4">{articolo.contenuto_breve}</p>
                      )}

                      <div className="flex justify-between items-center">
                        <div className="flex gap-4 text-sm text-gray-500">
                          {articolo.likes !== undefined && <span>❤️ {articolo.likes}</span>}
                          {articolo.commenti !== undefined && <span>💬 {articolo.commenti}</span>}
                          {articolo.autore && <span>✍️ {articolo.autore}</span>}
                        </div>
                        <Button className="bg-[#7a2426] hover:bg-[#a53327]">
                          Leggi tutto
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Altri articoli */}
            {articoli.filter((art: any) => !art.in_evidenza).length > 0 && (
              <div>
                <h2 className="text-2xl font-bold mb-6">📚 {articoli.filter((art: any) => art.in_evidenza).length > 0 ? 'Altri Articoli' : 'Articoli'}</h2>
                <div className="space-y-4">
                  {articoli.filter((art: any) => !art.in_evidenza).map((articolo: any) => (
                    <Card key={articolo.id} className="p-6 bg-white/90">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-4 mb-2">
                            {articolo.categoria && (
                              <Badge className={getCategoriaColor(articolo.categoria)}>
                                {articolo.categoria}
                              </Badge>
                            )}
                            {articolo.data_pubblicazione && (
                              <span className="text-sm text-gray-500">
                                {formatDate(articolo.data_pubblicazione)}
                              </span>
                            )}
                          </div>

                          <h3 className="text-lg font-bold mb-2">{articolo.titolo}</h3>
                          {articolo.contenuto_breve && (
                            <p className="text-gray-600 mb-3">{articolo.contenuto_breve}</p>
                          )}

                          <div className="flex gap-4 text-sm text-gray-500">
                            {articolo.likes !== undefined && <span>❤️ {articolo.likes}</span>}
                            {articolo.commenti !== undefined && <span>💬 {articolo.commenti}</span>}
                            {articolo.autore && <span>✍️ {articolo.autore}</span>}
                          </div>
                        </div>

                        <Button className="ml-4 bg-[#7a2426] hover:bg-[#a53327]">
                          Leggi
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
