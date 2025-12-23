
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Heart } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/volunteer')({
    component: VolunteerPage,
})

function VolunteerPage() {
    return (
        <DashboardLayout
            title="Volontariato"
            description="Gestione volontari e candidature"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <Heart className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>La gestione volontariato sarà disponibile a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
