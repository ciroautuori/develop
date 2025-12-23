import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Button } from '@/components/ui/button'
import { ChevronLeft } from 'lucide-react'

export const Route = createFileRoute('/settings')({
    component: SettingsPage,
})

function SettingsPage() {
    const navigate = useNavigate()
    const userStr = localStorage.getItem('iss_user')
    const user = userStr ? JSON.parse(userStr) : { role: 'user' }

    return (
        <DashboardLayout
            title="Impostazioni"
            description="Gestisci le tue preferenze"
            userRole={user.role}
        >
            <div className="space-y-6">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="sm" onClick={() => navigate({ to: '..' })}>
                        <ChevronLeft className="h-4 w-4 mr-2" />
                        Indietro
                    </Button>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h3 className="text-lg font-medium mb-4">Profilo Utente</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Email</label>
                            <div className="mt-1 text-gray-900">{user.email || 'Non disponibile'}</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Ruolo</label>
                            <div className="mt-1 text-gray-900 capitalize">{user.role}</div>
                        </div>
                    </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <h4 className="text-amber-800 font-medium mb-2">🚧 In Lavorazione</h4>
                    <p className="text-amber-700 text-sm">
                        La pagina delle impostazioni complete è in fase di sviluppo.
                        Presto potrai modificare la password, le preferenze di notifica e altro ancora.
                    </p>
                </div>
            </div>
        </DashboardLayout>
    )
}
