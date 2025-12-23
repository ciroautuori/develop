
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Database } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/system')({
    component: SystemPage,
})

function SystemPage() {
    return (
        <DashboardLayout
            title="Sistema"
            description="Configurazione e stato del sistema"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <Database className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>La configurazione sistema sarà disponibile a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
