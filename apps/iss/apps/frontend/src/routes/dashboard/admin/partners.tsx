import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
    Building,
    Search,
    Plus,
    Edit,
    Trash2,
    Globe,
    Mail,
    Phone,
    Shield,
    Star,
    ExternalLink,
    Filter,
    MoreVertical
} from 'lucide-react'
import { partnerAPI } from '@/services/api'

export const Route = createFileRoute('/dashboard/admin/partners')({
    component: PartnersPage,
})

function PartnersPage() {
    const queryClient = useQueryClient()
    const [searchQuery, setSearchQuery] = useState('')

    // Fetch partners
    const { data, isLoading } = useQuery({
        queryKey: ['admin-partners', searchQuery],
        queryFn: () => partnerAPI.list({ query: searchQuery })
    })

    // Delete partner mutation
    const deleteMutation = useMutation({
        mutationFn: (id: number) => partnerAPI.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-partners'] })
        }
    })

    const getLevelBadge = (level: string) => {
        switch (level) {
            case 'platinum':
                return <Badge className="bg-purple-100 text-purple-800 border-purple-200">Platinum</Badge>
            case 'gold':
                return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Gold</Badge>
            case 'silver':
                return <Badge className="bg-gray-100 text-gray-800 border-gray-200">Silver</Badge>
            default:
                return <Badge variant="outline">{level}</Badge>
        }
    }

    const getStatusBadge = (status: string) => {
        return status === 'attiva' ? (
            <Badge className="bg-green-100 text-green-800 border-green-200">Attiva</Badge>
        ) : (
            <Badge variant="secondary">{status}</Badge>
        )
    }

    return (
        <DashboardLayout
            title="Rete Partner"
            description="Gestisci le collaborazioni strategiche, gli sponsor e i network istituzionali di ISS"
            userRole="admin"
            action={
                <Button className="bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800">
                    <Plus className="h-4 w-4 mr-2" />
                    Aggiungi Partner
                </Button>
            }
        >
            <div className="space-y-6">
                {/* Stats Grid */}
                <div className="grid gap-4 md:grid-cols-4">
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-500">Partner Totali</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{data?.total || 0}</div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-500">Strategici</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-iss-bordeaux-900">
                                {data?.partners?.filter((p: any) => p.partner_strategico).length || 0}
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-500">In Evidenza</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-iss-gold-600">
                                {data?.partners?.filter((p: any) => p.in_evidenza).length || 0}
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-500">Nuove Proposte</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-blue-600">2</div>
                        </CardContent>
                    </Card>
                </div>

                {/* Filters */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex gap-4">
                            <div className="relative flex-1">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                                <Input
                                    placeholder="Cerca partner per nome, tipo o settore..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-10"
                                />
                            </div>
                            <Button variant="outline">
                                <Filter className="h-4 w-4 mr-2" />
                                Tipo
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Partners List */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {isLoading ? (
                        <div className="col-span-full flex justify-center py-12">
                            <Building className="h-8 w-8 animate-spin text-gray-300" />
                        </div>
                    ) : data?.partners?.length === 0 ? (
                        <div className="col-span-full text-center py-12 text-gray-500 bg-white rounded-xl border border-dashed">
                            <Building className="h-12 w-12 mx-auto mb-4 opacity-10" />
                            <p>Nessun partner trovato</p>
                        </div>
                    ) : (
                        data?.partners?.map((partner: any) => (
                            <Card key={partner.id} className="group overflow-hidden hover:shadow-md transition-shadow">
                                <CardHeader className="pb-3 border-b bg-gray-50/50">
                                    <div className="flex justify-between items-start">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 rounded bg-white border flex items-center justify-center p-1 overflow-hidden">
                                                {partner.logo_url ? (
                                                    <img src={partner.logo_url} alt={partner.nome_organizzazione} className="max-h-full max-w-full object-contain" />
                                                ) : (
                                                    <Building className="h-5 w-5 text-gray-400" />
                                                )}
                                            </div>
                                            <div>
                                                <CardTitle className="text-base line-clamp-1">{partner.nome_organizzazione}</CardTitle>
                                                <CardDescription className="text-xs">{partner.tipo}</CardDescription>
                                            </div>
                                        </div>
                                        {partner.partner_strategico && (
                                            <Star className="h-4 w-4 text-iss-gold-500 fill-iss-gold-500" />
                                        )}
                                    </div>
                                </CardHeader>
                                <CardContent className="pt-4 space-y-3">
                                    <div className="flex flex-wrap gap-2">
                                        {getLevelBadge(partner.livello)}
                                        {getStatusBadge(partner.stato)}
                                        <Badge variant="outline" className="text-[10px] uppercase">{partner.settore}</Badge>
                                    </div>

                                    <p className="text-sm text-gray-600 line-clamp-2">
                                        {partner.descrizione_breve || 'Nessuna descrizione fornita.'}
                                    </p>

                                    <div className="pt-2 flex items-center justify-between border-t text-xs text-gray-500">
                                        <div className="flex gap-3">
                                            {partner.sito_web && (
                                                <a href={partner.sito_web} target="_blank" rel="noopener noreferrer" className="hover:text-iss-bordeaux-900 transition-colors">
                                                    <Globe className="h-3.5 w-3.5" />
                                                </a>
                                            )}
                                            {partner.email_contatto && (
                                                <a href={`mailto:${partner.email_contatto}`} className="hover:text-iss-bordeaux-900 transition-colors">
                                                    <Mail className="h-3.5 w-3.5" />
                                                </a>
                                            )}
                                        </div>
                                        <div className="flex gap-1">
                                            <Button variant="ghost" size="icon" className="h-7 w-7">
                                                <Edit className="h-3.5 w-3.5" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-7 w-7 text-red-600 hover:text-red-700 hover:bg-red-50"
                                                onClick={() => {
                                                    if (confirm('Sei sicuro di voler archiviare questo partner?')) {
                                                        deleteMutation.mutate(partner.id)
                                                    }
                                                }}
                                            >
                                                <Trash2 className="h-3.5 w-3.5" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            </div>
        </DashboardLayout>
    )
}
