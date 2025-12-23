
import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent } from '@/components/ui/card'
import { Bell } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/notifications')({
    component: NotificationsPage,
})

function NotificationsPage() {
    return (
        <DashboardLayout
            title="Notifiche"
            description="Centro notifiche e comunicazioni"
            userRole="admin"
        >
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <Bell className="h-12 w-12 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Coming Soon</p>
                    <p>Il centro notifiche sarà disponibile a breve.</p>
                </CardContent>
            </Card>
        </DashboardLayout>
    )
}
