import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
    Calendar,
    MapPin,
    Users,
    Plus,
    Search,
    Edit,
    Trash2,
    MoreVertical,
    Clock,
    ExternalLink,
    ChevronRight
} from 'lucide-react'
import { eventsAPI } from '@/services/api'
import { Evento } from '@/types/api'

export const Route = createFileRoute('/dashboard/admin/events')({
    component: EventsPage,
})

function EventsPage() {
    const queryClient = useQueryClient()
    const [searchQuery, setSearchQuery] = useState('')
    const [page, setPage] = useState(0)

    // Fetch events
    const { data, isLoading } = useQuery({
        queryKey: ['admin-events', searchQuery, page],
        queryFn: () => eventsAPI.list({ query: searchQuery, skip: page * 10, limit: 10 })
    })

    // Delete event mutation
    const deleteMutation = useMutation({
        mutationFn: (id: number) => eventsAPI.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-events'] })
        }
    })

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('it-IT', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return (
        <DashboardLayout
            title="Gestione Eventi"
            description="Organizza e gestisci gli eventi, workshop e hackathon della piattaforma ISS"
            userRole="admin"
            action={
                <Button className="bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800">
                    <Plus className="h-4 w-4 mr-2" />
                    Nuovo Evento
                </Button>
            }
        >
            <div className="space-y-6">
                {/* Filters and Stats */}
                <div className="grid gap-6 md:grid-cols-4">
                    <Card className="md:col-span-3">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm font-medium">Ricerca Eventi</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex gap-4">
                                <div className="relative flex-1">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                                    <Input
                                        placeholder="Cerca per titolo, luogo o tag..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="pl-10"
                                    />
                                </div>
                                <Button variant="outline">Filtri Avanzati</Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm font-medium">Statistiche Rapide</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-500">Eventi Attivi</span>
                                    <span className="font-bold">{data?.total || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-500">Iscrizioni Totali</span>
                                    <span className="font-bold">124</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Events Table/List */}
                <Card>
                    <CardHeader>
                        <CardTitle>Programma Eventi</CardTitle>
                        <CardDescription>
                            Tutti gli eventi pianificati e passati nel sistema
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="flex justify-center py-12">
                                <Clock className="h-8 w-8 animate-spin text-iss-bordeaux-900" />
                            </div>
                        ) : data?.items?.length === 0 ? (
                            <div className="text-center py-12 text-gray-500">
                                <Calendar className="h-12 w-12 mx-auto mb-4 opacity-20" />
                                <p>Nessun evento trovato</p>
                                <Button variant="link" onClick={() => setSearchQuery('')}>Pulisci ricerca</Button>
                            </div>
                        ) : (
                            <div className="divide-y border rounded-lg overflow-hidden">
                                {data?.items?.map((item: Evento) => (
                                    <div key={item.id} className="p-4 hover:bg-gray-50 transition-colors flex items-center gap-6">
                                        <div className="flex flex-col items-center justify-center w-16 h-16 bg-iss-bordeaux-50 rounded-lg text-iss-bordeaux-900">
                                            <span className="text-xs font-bold uppercase">{new Date(item.data_evento).toLocaleString('it-IT', { month: 'short' })}</span>
                                            <span className="text-xl font-black">{new Date(item.data_evento).getDate()}</span>
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <h3 className="font-bold text-gray-900 truncate">{item.titolo}</h3>
                                                <Badge variant="outline" className="capitalize">{item.tipo}</Badge>
                                                {item.iscrizioni_aperte ? (
                                                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100 border-green-200">Aperto</Badge>
                                                ) : (
                                                    <Badge variant="secondary" className="opacity-60 text-xs">Chiuso</Badge>
                                                )}
                                            </div>
                                            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-600">
                                                <span className="flex items-center gap-1">
                                                    <Clock className="h-3.5 w-3.5" />
                                                    {formatDate(item.data_evento)}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <MapPin className="h-3.5 w-3.5" />
                                                    {item.luogo}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <Users className="h-3.5 w-3.5" />
                                                    {item.partecipanti_attuali || 0} / {item.partecipanti_max}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <Button variant="ghost" size="icon">
                                                <Edit className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                                onClick={() => {
                                                    if (confirm('Sei sicuro di voler eliminare questo evento?')) {
                                                        deleteMutation.mutate(item.id)
                                                    }
                                                }}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                            <Button variant="ghost" size="icon">
                                                <ChevronRight className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </DashboardLayout>
    )
}
