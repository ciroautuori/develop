import { createFileRoute } from '@tanstack/react-router'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Building,
  Users,
  FileText,
  Target,
  Handshake,
  Mail,
  FolderOpen,
  Settings,
  Clock
} from 'lucide-react'

export const Route = createFileRoute('/dashboard/partner')({
  component: PartnerDashboard,
})

function PartnerDashboard() {
  return (
    <DashboardLayout
      title="Area Partner"
      description="Gestisci la tua collaborazione con ISS"
      userRole="partner"
    >
      {/* Welcome Card */}
      <Card className="bg-gradient-to-r from-purple-50 to-purple-100 border-purple-200">
        <CardContent className="py-8 text-center">
          <div className="text-5xl mb-4">🤝</div>
          <h2 className="text-2xl font-bold text-purple-900 mb-2">
            Benvenuto nell'Area Partner
          </h2>
          <p className="text-purple-700 max-w-xl mx-auto">
            Quest'area è riservata ai partner ufficiali di ISS.
            Qui potrai gestire progetti, visualizzare statistiche e collaborare con le APS.
          </p>
        </CardContent>
      </Card>

      {/* Feature Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Target className="h-6 w-6 text-purple-600" />
            </div>
            <CardTitle className="text-lg">I Miei Progetti</CardTitle>
            <CardDescription>
              Visualizza e gestisci i progetti attivi con ISS
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              <Clock className="h-4 w-4 mr-2" />
              Prossimamente
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <CardTitle className="text-lg">APS Collegate</CardTitle>
            <CardDescription>
              Visualizza le APS con cui stai collaborando
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              <Clock className="h-4 w-4 mr-2" />
              Prossimamente
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
            <CardTitle className="text-lg">Documentazione</CardTitle>
            <CardDescription>
              Accedi a contratti e documenti della partnership
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              <Clock className="h-4 w-4 mr-2" />
              Prossimamente
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
              <Handshake className="h-6 w-6 text-yellow-600" />
            </div>
            <CardTitle className="text-lg">Nuove Opportunità</CardTitle>
            <CardDescription>
              Scopri nuove collaborazioni disponibili
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              <Clock className="h-4 w-4 mr-2" />
              Prossimamente
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
              <Mail className="h-6 w-6 text-red-600" />
            </div>
            <CardTitle className="text-lg">Messaggi</CardTitle>
            <CardDescription>
              Comunica con il team ISS e le APS partner
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              <Clock className="h-4 w-4 mr-2" />
              Prossimamente
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mb-4">
              <Settings className="h-6 w-6 text-gray-600" />
            </div>
            <CardTitle className="text-lg">Impostazioni</CardTitle>
            <CardDescription>
              Gestisci il profilo della tua organizzazione
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              <Clock className="h-4 w-4 mr-2" />
              Prossimamente
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Info Box */}
      <Card className="border-dashed border-2">
        <CardContent className="py-6 text-center text-gray-600">
          <Building className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <h3 className="font-semibold text-gray-800 mb-2">Area in sviluppo</h3>
          <p className="text-sm max-w-md mx-auto">
            Stiamo lavorando per offrirti un'esperienza completa.
            Nel frattempo, contatta il team ISS per qualsiasi necessità.
          </p>
        </CardContent>
      </Card>
    </DashboardLayout>
  )
}
