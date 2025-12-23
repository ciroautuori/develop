
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Calendar } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/events')({
    component: EventsPage,
})

function EventsPage() {
    return (
        <DashboardLayout
            title="Gestione Eventi"
            description="Calendario e gestione eventi ISS"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <Calendar className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>La gestione eventi sarà disponibile a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
