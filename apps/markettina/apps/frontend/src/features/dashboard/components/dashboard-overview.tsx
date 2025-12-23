import { useQuery } from '@tanstack/react-query'
import {
  Users,
  CreditCard,
  Activity,
  DollarSign,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../shared/components/ui/card'
import { Badge } from '../../../shared/components/ui/badge'
import { Progress } from '../../../shared/components/ui/progress'
import { apiClient } from '../../../shared/lib/api'
import { formatCurrency } from '../../../shared/lib/utils'

interface DashboardStats {
  totalUsers: number
  activeUsers: number
  totalRevenue: number
  monthlyRevenue: number
  totalSubscriptions: number
  activeSubscriptions: number
  conversionRate: number
  churnRate: number
}

interface MetricCardProps {
  title: string
  value: string | number
  description: string
  icon: React.ComponentType<{ className?: string }>
  trend?: {
    value: number
    isPositive: boolean
  }
}

function MetricCard({ title, value, description, icon: Icon, trend }: MetricCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
          <span>{description}</span>
          {trend && (
            <div className={`flex items-center ${trend.isPositive ? 'text-gold' : 'text-gray-500'}`}>
              {trend.isPositive ? (
                <ArrowUpRight className="h-3 w-3" />
              ) : (
                <ArrowDownRight className="h-3 w-3" />
              )}
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export function DashboardOverview() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async (): Promise<DashboardStats> => {
      // API Reale - chiama il backend
      const token = localStorage.getItem('token') || localStorage.getItem('admin_token');
      const res = await fetch('/api/v1/dashboard/stats', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });

      if (!res.ok) {
        // Fallback a valori default se API non disponibile
        return {
          totalUsers: 0,
          activeUsers: 0,
          totalRevenue: 0,
          monthlyRevenue: 0,
          totalSubscriptions: 0,
          activeSubscriptions: 0,
          conversionRate: 0,
          churnRate: 0
        };
      }

      const data = await res.json();
      return {
        totalUsers: data.total_users || 0,
        activeUsers: data.active_users || 0,
        totalRevenue: data.total_revenue || 0,
        monthlyRevenue: data.monthly_revenue || 0,
        totalSubscriptions: data.total_subscriptions || 0,
        activeSubscriptions: data.active_subscriptions || 0,
        conversionRate: data.conversion_rate || 0,
        churnRate: data.churn_rate || 0
      };
    },
    refetchInterval: 300000, // Refresh every 5 minutes
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="animate-pulse">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </CardHeader>
              <CardContent className="animate-pulse">
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-lg text-muted-foreground">Errore nel caricamento dei dati</p>
          <p className="text-sm text-muted-foreground">Riprova più tardi</p>
        </div>
      </div>
    )
  }

  const userGrowth = ((stats.activeUsers / stats.totalUsers) * 100).toFixed(1)
  const subscriptionRate = ((stats.activeSubscriptions / stats.totalSubscriptions) * 100).toFixed(1)

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-muted-foreground">
            Benvenuto nel pannello di controllo MARKETTINA
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-gold border-gold">
            <Activity className="mr-1 h-3 w-3" />
            Sistema Operativo
          </Badge>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Utenti Totali"
          value={stats.totalUsers.toLocaleString()}
          description={`${userGrowth}% attivi`}
          icon={Users}
          trend={{ value: 12.5, isPositive: true }}
        />
        <MetricCard
          title="Fatturato Mensile"
          value={formatCurrency(stats.monthlyRevenue)}
          description="Rispetto al mese scorso"
          icon={DollarSign}
          trend={{ value: 8.2, isPositive: true }}
        />
        <MetricCard
          title="Abbonamenti Attivi"
          value={stats.activeSubscriptions}
          description={`${subscriptionRate}% del totale`}
          icon={CreditCard}
          trend={{ value: 5.1, isPositive: true }}
        />
        <MetricCard
          title="Tasso di Conversione"
          value={`${stats.conversionRate}%`}
          description="Ultimi 30 giorni"
          icon={TrendingUp}
          trend={{ value: 2.3, isPositive: true }}
        />
      </div>

      {/* Detailed Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* User Activity */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Attività Utenti
            </CardTitle>
            <CardDescription>
              Panoramica dell'attività degli utenti negli ultimi 30 giorni
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Utenti Attivi</span>
                <span className="font-medium">{stats.activeUsers}</span>
              </div>
              <Progress value={72} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Nuove Registrazioni</span>
                <span className="font-medium">245</span>
              </div>
              <Progress value={45} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Retention Rate</span>
                <span className="font-medium">89.2%</span>
              </div>
              <Progress value={89} className="h-2" />
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Statistiche Rapide
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Fatturato Totale</span>
                <span className="font-semibold">{formatCurrency(stats.totalRevenue)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Abbonamenti Totali</span>
                <span className="font-semibold">{stats.totalSubscriptions}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Tasso di Abbandono</span>
                <span className="font-semibold text-gray-500">{stats.churnRate}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Soddisfazione</span>
                <span className="font-semibold text-gold">95.8%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Attività Recente</CardTitle>
          <CardDescription>
            Ultime attività del sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { action: 'Nuovo utente registrato', user: 'mario.rossi@email.com', time: '2 minuti fa' },
              { action: 'Pagamento completato', user: 'laura.bianchi@email.com', time: '15 minuti fa' },
              { action: 'Abbonamento rinnovato', user: 'giuseppe.verdi@email.com', time: '1 ora fa' },
              { action: 'Password reset richiesto', user: 'anna.ferrari@email.com', time: '2 ore fa' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                <div>
                  <p className="text-sm font-medium">{activity.action}</p>
                  <p className="text-xs text-muted-foreground">{activity.user}</p>
                </div>
                <span className="text-xs text-muted-foreground">{activity.time}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
