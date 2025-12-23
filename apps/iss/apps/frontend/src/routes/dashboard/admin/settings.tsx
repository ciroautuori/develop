
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Settings } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/settings')({
    component: SettingsPage,
})

function SettingsPage() {
    return (
        <DashboardLayout
            title="Impostazioni"
            description="Preferenze generali e account"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <Settings className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>Le impostazioni saranno disponibili a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
