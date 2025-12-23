
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Shield } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/security')({
    component: SecurityPage,
})

function SecurityPage() {
    return (
        <DashboardLayout
            title="Sicurezza"
            description="Audit log e impostazioni sicurezza"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <Shield className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>La sezione sicurezza sarà disponibile a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
