import { createFileRoute, Link } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Users, Shield, Building } from 'lucide-react'

export const Route = createFileRoute('/dashboard/select')({
  component: DashboardOverview,
})

function DashboardOverview() {
  const dashboardTypes = [
    {
      title: "Dashboard Admin",
      description: "Pannello di controllo amministrativo completo",
      href: "/dashboard/admin",
      icon: Shield,
      color: "bg-red-50 border-red-200 hover:bg-red-100",
      iconColor: "text-red-600"
    },
    {
      title: "Dashboard Utente",
      description: "Area personale per utenti registrati",
      href: "/dashboard/user",
      icon: Users,
      color: "bg-green-50 border-green-200 hover:bg-green-100",
      iconColor: "text-green-600"
    },
    {
      title: "Dashboard Partner",
      description: "Area riservata ai partner ISS",
      href: "/dashboard/partner",
      icon: Building,
      color: "bg-purple-50 border-purple-200 hover:bg-purple-100",
      iconColor: "text-purple-600"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Dashboard ISS Professionali</h1>
          <p className="text-gray-600 text-lg">Seleziona la dashboard con sidebar navigabile</p>
        </div>
        
        {/* Dashboard Types */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {dashboardTypes.map((dashboard, index) => (
            <Link key={index} to={dashboard.href}>
              <Card className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${dashboard.color} h-full`}>
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-white flex items-center justify-center mb-4 shadow-sm">
                    <dashboard.icon className={`h-8 w-8 ${dashboard.iconColor}`} />
                  </div>
                  <CardTitle className="text-xl font-bold">{dashboard.title}</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <p className="text-gray-600 mb-4">{dashboard.description}</p>
                  <Button className={`w-full ${dashboard.iconColor.replace('text-', 'bg-').replace('-600', '-600')} hover:opacity-90`}>
                    Accedi alla Dashboard →
                  </Button>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Quick Access */}
        <div className="mt-12 text-center">
          <h2 className="text-2xl font-bold mb-6">Accesso Rapido Admin</h2>
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/dashboard/admin">
              <Button className="bg-red-600 hover:bg-red-700">
                <Shield className="h-4 w-4 mr-2" />
                Dashboard Admin
              </Button>
            </Link>
            <Link to="/dashboard/admin/users">
              <Button variant="outline">
                <Users className="h-4 w-4 mr-2" />
                Gestione Utenti
              </Button>
            </Link>
            <Link to="/dashboard/admin/bandi">
              <Button variant="outline">
                Gestione Bandi
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
