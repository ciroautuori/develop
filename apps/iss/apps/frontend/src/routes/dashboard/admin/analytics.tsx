
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { BarChart3 } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/analytics')({
    component: AnalyticsPage,
})

function AnalyticsPage() {
    return (
        <DashboardLayout
            title="Analytics"
            description="Statistiche e reportistica"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <BarChart3 className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>La sezione analytics sarà disponibile a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
