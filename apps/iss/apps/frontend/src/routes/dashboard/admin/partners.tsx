
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Building } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/partners')({
    component: PartnersPage,
})

function PartnersPage() {
    return (
        <DashboardLayout
            title="Partner"
            description="Gestione partner e collaborazioni"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <Building className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>La gestione partner sarà disponibile a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
