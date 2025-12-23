import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { issService } from '@/services/api'
import { Loader2, Building2 } from 'lucide-react'

export const Route = createFileRoute('/partners')({
  component: PartnersPage,
})

function PartnersPage() {
  // Fetch partners da API - dati reali dal database
  const { data: partnersData, isLoading: loadingPartners } = useQuery({
    queryKey: ['partners'],
    queryFn: issService.getPartners,
    staleTime: 1000 * 60 * 10,
  })

  // Fetch testimonials da API - dati reali dal database
  const { data: testimonialsData, isLoading: loadingTestimonials } = useQuery({
    queryKey: ['testimonials'],
    queryFn: issService.getTestimonials,
    staleTime: 1000 * 60 * 10,
  })

  const partners = partnersData?.items || []
  const testimonials = testimonialsData?.items || []
  const isLoading = loadingPartners || loadingTestimonials

  const getLivelloColor = (livello: string) => {
    switch (livello) {
      case 'strategico': return 'bg-red-100 text-red-800'
      case 'istituzionale': return 'bg-blue-100 text-blue-800'
      case 'operativo': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTipoColor = (tipo: string) => {
    switch (tipo) {
      case 'istituzione_accademica': return 'bg-purple-100 text-purple-800'
      case 'ente_pubblico': return 'bg-blue-100 text-blue-800'
      case 'azienda_privata': return 'bg-orange-100 text-orange-800'
      case 'ong': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const renderStars = (rating: number) => {
    return '⭐'.repeat(Math.min(rating, 5))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
      <div className="bg-gradient-to-r from-[#7a2426] to-[#a53327] text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold mb-4">
            🤝 Partner & <span className="text-[#f4af00]">Collaborazioni</span>
          </h1>
          <p className="text-xl">La rete che rende possibile l'innovazione sociale</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-iss-bordeaux-600" />
            <span className="ml-3 text-lg">Caricamento...</span>
          </div>
        ) : partners.length === 0 && testimonials.length === 0 ? (
          <div className="text-center py-20">
            <Building2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-600 mb-4">
              Sezione in costruzione
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              I partner e le collaborazioni verranno aggiunti prossimamente dall'amministratore.
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
            {/* Partner Strategici */}
            {partners.filter((p: any) => p.partner_strategico).length > 0 && (
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-6">🌟 Partner Strategici</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {partners.filter((p: any) => p.partner_strategico).map((partner: any) => (
                    <Card key={partner.id} className="p-6 bg-white/90 border-l-4 border-[#f4af00]">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-bold">{partner.nome_organizzazione}</h3>
                        <div className="flex gap-2">
                          {partner.livello && (
                            <Badge className={getLivelloColor(partner.livello)}>
                              {partner.livello}
                            </Badge>
                          )}
                          {partner.tipo && (
                            <Badge className={getTipoColor(partner.tipo)}>
                              {partner.tipo.replace('_', ' ')}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {partner.descrizione_breve && (
                        <p className="text-gray-600 mb-4">{partner.descrizione_breve}</p>
                      )}

                      <div className="flex justify-between items-center">
                        <div className="text-sm text-gray-500">
                          {partner.citta && `📍 ${partner.citta}`}
                          {partner.settore && ` • 🏢 ${partner.settore}`}
                        </div>
                        {partner.sito_web && (
                          <Button
                            className="bg-[#7a2426] hover:bg-[#a53327]"
                            onClick={() => window.open(partner.sito_web, '_blank')}
                          >
                            Scopri di più
                          </Button>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Altri Partner */}
            {partners.filter((p: any) => !p.partner_strategico).length > 0 && (
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-6">🤝 Altri Partner</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {partners.filter((p: any) => !p.partner_strategico).map((partner: any) => (
                    <Card key={partner.id} className="p-4 bg-white/90">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-bold text-lg">{partner.nome_organizzazione}</h4>
                        {partner.livello && (
                          <Badge className={getLivelloColor(partner.livello)}>
                            {partner.livello}
                          </Badge>
                        )}
                      </div>

                      {partner.descrizione_breve && (
                        <p className="text-gray-600 text-sm mb-3">{partner.descrizione_breve}</p>
                      )}

                      {partner.citta && (
                        <div className="text-xs text-gray-500">
                          📍 {partner.citta}
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Testimonials */}
            {testimonials.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold mb-6">💬 Cosa Dicono di Noi</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {testimonials.map((testimonial: any) => (
                    <Card key={testimonial.id} className="p-6 bg-white/90">
                      <div className="flex items-center mb-4">
                        {testimonial.rating && (
                          <div className="text-2xl mr-3">
                            {renderStars(testimonial.rating)}
                          </div>
                        )}
                        {testimonial.verificato && (
                          <Badge className="bg-green-100 text-green-800">
                            ✓ Verificato
                          </Badge>
                        )}
                      </div>

                      <blockquote className="text-gray-700 italic mb-4">
                        "{testimonial.contenuto}"
                      </blockquote>

                      <div className="border-t pt-4">
                        <div className="font-semibold">{testimonial.nome_autore}</div>
                        {testimonial.ruolo_autore && (
                          <div className="text-sm text-gray-600">{testimonial.ruolo_autore}</div>
                        )}
                        {testimonial.organizzazione && (
                          <div className="text-sm text-gray-500">{testimonial.organizzazione}</div>
                        )}
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
