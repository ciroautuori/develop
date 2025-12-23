import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { StatCard } from '@/components/dashboard/StatCard'
import { ChartCard } from '@/components/dashboard/ChartCard'
import { QuickAction } from '@/components/dashboard/QuickAction'
import { Button } from '@/components/ui/button'
import {
  Users,
  Activity,
  FileText,
  Calendar,
  Shield,
  Bot
} from 'lucide-react'

interface UserStats {
  total_users: number
  active_users: number
  pending_users: number
  aps_organizations: number
  users_by_role?: Record<string, number>
}

interface BandiStats {
  totali: number
  attivi: number
  in_scadenza: number
  fonti: Record<string, number>
}

export const Route = createFileRoute('/dashboard/admin')({
  component: AdminDashboard,
})

function AdminDashboard() {
  // Fetch user stats
  const { data: userStats } = useQuery<UserStats>({
    queryKey: ['admin-user-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/users/stats', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      if (!response.ok) {
        return { total_users: 0, active_users: 0, pending_users: 0, aps_organizations: 0 }
      }
      return response.json()
    }
  })

  // Fetch bandi stats
  const { data: bandiStats } = useQuery<BandiStats>({
    queryKey: ['admin-bandi-stats'],
    queryFn: async () => {
      const response = await fetch('/api/v1/bandi/stats')
      if (!response.ok) {
        return { totali: 0, attivi: 0, in_scadenza: 0, fonti: {} }
      }
      return response.json()
    }
  })

  // Prepare chart data from real stats
  const userRolesData = userStats?.users_by_role
    ? Object.entries(userStats.users_by_role).map(([name, value]) => ({
        name: name.replace('_', ' ').charAt(0).toUpperCase() + name.replace('_', ' ').slice(1),
        value
      }))
    : [{ name: 'Utenti', value: userStats?.total_users || 0 }]

  const bandiBySourceData = bandiStats?.fonti
    ? Object.entries(bandiStats.fonti).map(([name, value]) => ({ name, value }))
    : [{ name: 'Bandi', value: bandiStats?.totali || 0 }]

  return (
    <DashboardLayout
      title="Dashboard Admin"
      description="Pannello di controllo amministrativo"
      userRole="admin"
      action={
        <Link to="/dashboard/admin/bandi" className="w-full sm:w-auto">
          <Button className="w-full sm:w-auto text-sm">
            <Bot className="h-4 w-4 mr-2" />
            <span className="hidden xs:inline">AI Bandi</span>
            <span className="xs:hidden">AI</span>
          </Button>
        </Link>
      }
    >
      {/* Real-time Statistics Cards - Mobile First Grid */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        <StatCard
          title="Utenti"
          value={(userStats?.total_users ?? 0).toLocaleString()}
          change={`${userStats?.pending_users ?? 0} pending`}
          trend="up"
          icon={Users}
        />
        <StatCard
          title="Attivi"
          value={(userStats?.active_users ?? 0).toLocaleString()}
          change={`${userStats?.aps_organizations ?? 0} APS`}
          trend="up"
          icon={Activity}
        />
        <StatCard
          title="Bandi"
          value={(bandiStats?.totali ?? 0).toLocaleString()}
          change={`${bandiStats?.attivi ?? 0} attivi`}
          trend="up"
          icon={FileText}
        />
        <StatCard
          title="Scadenza"
          value={bandiStats?.in_scadenza ?? 0}
          change="30 giorni"
          trend={bandiStats?.in_scadenza && bandiStats.in_scadenza > 5 ? "down" : "up"}
          icon={Calendar}
        />
      </div>

      {/* Charts - Stack on mobile */}
      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard
          title="Utenti per Ruolo"
          description="Distribuzione ruoli"
          data={userRolesData}
          type="pie"
        />
        <ChartCard
          title="Bandi per Fonte"
          description="Distribuzione fonti"
          data={bandiBySourceData}
          type="pie"
        />
      </div>

      {/* Platform Status - Responsive */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 sm:p-6">
        <div className="flex items-center gap-2 mb-3 sm:mb-4">
          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 bg-green-500 rounded-full animate-pulse" />
          <h3 className="text-base sm:text-lg font-semibold text-green-800">Sistema Operativo</h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 text-xs sm:text-sm">
          <div>
            <p className="text-green-700 font-medium">Backend</p>
            <p className="text-green-600">✅ Online</p>
          </div>
          <div>
            <p className="text-green-700 font-medium">Database</p>
            <p className="text-green-600">✅ PostgreSQL</p>
          </div>
          <div>
            <p className="text-green-700 font-medium">AI Agent</p>
            <p className="text-green-600">✅ Gemini</p>
          </div>
          <div>
            <p className="text-green-700 font-medium">SSL</p>
            <p className="text-green-600">✅ Attivo</p>
          </div>
        </div>
      </div>

      {/* Quick Actions - 2 columns on mobile */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        <Link to="/dashboard/admin/users" className="block">
          <QuickAction
            title="Utenti"
            description={`${userStats?.total_users ?? 0} registrati`}
            icon={Users}
            onClick={() => {}}
            variant="primary"
          />
        </Link>
        <Link to="/dashboard/admin/bandi" className="block">
          <QuickAction
            title="Bandi"
            description={`${bandiStats?.totali ?? 0} trovati`}
            icon={FileText}
            onClick={() => {}}
            variant="secondary"
          />
        </Link>
        <QuickAction
          title="AI Agent"
          description="Cerca nuovi bandi"
          icon={Bot}
          onClick={() => {
            fetch('/api/v1/bandi/ai-search', { method: 'POST' })
          }}
          variant="default"
        />
        <QuickAction
          title="Sicurezza"
          description="Log e audit"
          icon={Shield}
          onClick={() => {}}
          variant="destructive"
        />
      </div>
    </DashboardLayout>
  )
}
