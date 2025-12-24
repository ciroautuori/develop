import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
    Heart,
    Search,
    CheckCircle,
    XCircle,
    Clock,
    Mail,
    User,
    Briefcase,
    FileText,
    Filter,
    Download
} from 'lucide-react'
import { volunteerAPI } from '@/services/api'

export const Route = createFileRoute('/dashboard/admin/volunteer')({
    component: VolunteerPage,
})

function VolunteerPage() {
    const queryClient = useQueryClient()
    const [searchQuery, setSearchQuery] = useState('')

    // Fetch applications
    const { data: applications, isLoading } = useQuery({
        queryKey: ['admin-volunteers', searchQuery],
        queryFn: () => volunteerAPI.list({ query: searchQuery })
    })

    // Update application status
    const updateStatusMutation = useMutation({
        mutationFn: ({ id, status }: { id: number, status: string }) =>
            volunteerAPI.update(id, { status }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-volunteers'] })
        }
    })

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'approved':
                return <Badge className="bg-green-100 text-green-800 border-green-200">Approvata</Badge>
            case 'rejected':
                return <Badge className="bg-red-100 text-red-800 border-red-200">Rifiutata</Badge>
            case 'pending':
                return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200 text-[10px] uppercase font-bold">In Attesa</Badge>
            default:
                return <Badge variant="outline">{status}</Badge>
        }
    }

    return (
        <DashboardLayout
            title="Candidature Volontariato"
            description="Gestisci le richieste di cittadini che vogliono contribuire ai progetti ISS"
            userRole="admin"
            action={
                <Button variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Esporta Lista
                </Button>
            }
        >
            <div className="space-y-6">
                {/* Stats and Filter */}
                <div className="grid gap-6 md:grid-cols-4">
                    <Card className="md:col-span-3">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm font-medium">Filtra Candidature</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex gap-4">
                                <div className="relative flex-1">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                                    <Input
                                        placeholder="Cerca per nome, email o competenza..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="pl-10"
                                    />
                                </div>
                                <Button variant="outline">
                                    <Filter className="h-4 w-4 mr-2" />
                                    Stato
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-iss-bordeaux-900 text-white">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm font-medium opacity-80">Nuove Richieste</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold">12</div>
                            <p className="text-xs opacity-70 mt-1">Negli ultimi 7 giorni</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Applications List */}
                <Card>
                    <CardHeader>
                        <CardTitle>Candidature Recenti</CardTitle>
                        <CardDescription>
                            Elenco delle persone che hanno manifestato interesse per il volontariato
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="flex justify-center py-12">
                                <Clock className="h-8 w-8 animate-spin text-iss-bordeaux-900" />
                            </div>
                        ) : !applications || (Array.isArray(applications) && applications.length === 0) ? (
                            <div className="text-center py-12 text-gray-500">
                                <Heart className="h-12 w-12 mx-auto mb-4 opacity-20" />
                                <p>Nessuna candidatura trovata</p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b text-gray-500">
                                            <th className="text-left py-3 px-4 font-medium">Volontario</th>
                                            <th className="text-left py-3 px-4 font-medium">Area d'Interesse</th>
                                            <th className="text-left py-3 px-4 font-medium">Data Invio</th>
                                            <th className="text-left py-3 px-4 font-medium">Stato</th>
                                            <th className="text-right py-3 px-4 font-medium">Azioni</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y">
                                        {(Array.isArray(applications) ? applications : []).map((app: any) => (
                                            <tr key={app.id} className="hover:bg-gray-50 transition-colors">
                                                <td className="py-4 px-4">
                                                    <div className="flex items-center gap-3">
                                                        <div className="h-8 w-8 rounded-full bg-iss-bordeaux-100 text-iss-bordeaux-900 flex items-center justify-center font-bold">
                                                            {app.full_name?.[0] || 'V'}
                                                        </div>
                                                        <div>
                                                            <p className="font-semibold text-gray-900">{app.full_name}</p>
                                                            <p className="text-xs text-gray-500">{app.email}</p>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="py-4 px-4">
                                                    <div className="flex flex-wrap gap-1">
                                                        {app.interests?.map((interest: string) => (
                                                            <Badge key={interest} variant="secondary" className="text-[10px]">
                                                                {interest}
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                </td>
                                                <td className="py-4 px-4 text-gray-600">
                                                    {new Date(app.submitted_at).toLocaleDateString('it-IT')}
                                                </td>
                                                <td className="py-4 px-4">
                                                    {getStatusBadge(app.status)}
                                                </td>
                                                <td className="py-4 px-4 text-right">
                                                    <div className="flex justify-end gap-2">
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            className="text-green-600 hover:text-green-700 hover:bg-green-50"
                                                            onClick={() => updateStatusMutation.mutate({ id: app.id, status: 'approved' })}
                                                        >
                                                            <CheckCircle className="h-4 w-4" />
                                                        </Button>
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                                            onClick={() => updateStatusMutation.mutate({ id: app.id, status: 'rejected' })}
                                                        >
                                                            <XCircle className="h-4 w-4" />
                                                        </Button>
                                                        <Button variant="ghost" size="sm">
                                                            <FileText className="h-4 w-4" />
                                                        </Button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </DashboardLayout>
    )
}
