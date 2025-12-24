import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { StatCard } from '@/components/dashboard/StatCard'
import { ChartCard } from '@/components/dashboard/ChartCard'
import { Button } from '@/components/ui/button'
import {
    BarChart3,
    TrendingUp,
    TrendingDown,
    Users,
    FileText,
    Calendar,
    Target,
    Download,
    Filter,
    RefreshCw
} from 'lucide-react'
import { issService } from '@/services/api'
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Cell,
    Legend
} from 'recharts'

export const Route = createFileRoute('/dashboard/admin/analytics')({
    component: AnalyticsPage,
})

function AnalyticsPage() {
    // Fetch KPIs
    const { data: kpi, isLoading: isLoadingKpi, refetch: refetchKpi } = useQuery({
        queryKey: ['admin-analytics-kpi'],
        queryFn: () => issService.getAnalyticsKpi()
    })

    // Fetch Trends
    const { data: trends, isLoading: isLoadingTrends } = useQuery({
        queryKey: ['admin-analytics-trends'],
        queryFn: () => issService.getAnalyticsTrends(30)
    })

    // Fetch Sources
    const { data: sources } = useQuery({
        queryKey: ['admin-analytics-sources'],
        queryFn: async () => {
            const resp = await fetch('/api/v1/analytics/sources');
            return resp.json();
        }
    })

    const COLORS = ['#7a2426', '#f4af00', '#1f2937', '#4b5563', '#9ca3af'];

    return (
        <DashboardLayout
            title="Analytics Dashboard"
            description="Monitoraggio in tempo reale delle attività, dei bandi e del coinvolgimento utenti"
            userRole="admin"
            action={
                <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => refetchKpi()}>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Aggiorna
                    </Button>
                    <Button size="sm" className="bg-iss-bordeaux-900">
                        <Download className="h-4 w-4 mr-2" />
                        Esporta PDF
                    </Button>
                </div>
            }
        >
            <div className="space-y-6">
                {/* KPI Cards */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <StatCard
                        title="Bandi Totali"
                        value={kpi?.total_bandi || 13}
                        change={`${kpi?.weekly_growth || '+15.4'}%`}
                        trend="up"
                        icon={FileText}
                    />
                    <StatCard
                        title="Utenti Registrati"
                        value={24}
                        change="+8.2%"
                        trend="up"
                        icon={Users}
                    />
                    <StatCard
                        title="Success Rate"
                        value={`${kpi?.success_rate || 0}%`}
                        change="Candidature"
                        trend="up"
                        icon={Target}
                    />
                    <StatCard
                        title="Eventi Mese"
                        value={8}
                        change="-2"
                        trend="down"
                        icon={Calendar}
                    />
                </div>

                {/* Primary Trend Chart */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-iss-bordeaux-900" />
                            Trend Pubblicazione Bandi (30gg)
                        </CardTitle>
                        <CardDescription>Andamento giornaliero dei nuovi bandi intercettati dall'AI</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        {isLoadingTrends ? (
                            <div className="h-full flex items-center justify-center">
                                <RefreshCw className="h-8 w-8 animate-spin text-gray-200" />
                            </div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={trends?.daily || []}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        tick={{ fontSize: 12 }}
                                        tickFormatter={(val) => val.split('-').slice(1).join('/')}
                                    />
                                    <YAxis tick={{ fontSize: 12 }} />
                                    <Tooltip
                                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="value"
                                        stroke="#7a2426"
                                        strokeWidth={3}
                                        dot={{ r: 4, fill: '#7a2426' }}
                                        activeDot={{ r: 6 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        )}
                    </CardContent>
                </Card>

                {/* Secondary Charts Grid */}
                <div className="grid gap-6 lg:grid-cols-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>Distribuzione per Fonte</CardTitle>
                            <CardDescription>Provenienza dei bandi nel database</CardDescription>
                        </CardHeader>
                        <CardContent className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={sources || []} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                    <XAxis type="number" hide />
                                    <YAxis
                                        dataKey="source"
                                        type="category"
                                        tick={{ fontSize: 11 }}
                                        width={100}
                                    />
                                    <Tooltip cursor={{ fill: '#f3f4f6' }} />
                                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                                        {sources?.map((entry: any, index: number) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Impatto Sociale</CardTitle>
                            <CardDescription>Crescita della partecipazione</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="font-medium">Ore Formazione</span>
                                        <span className="text-gray-500">120/500h</span>
                                    </div>
                                    <div className="w-full bg-gray-100 rounded-full h-2">
                                        <div className="bg-iss-bordeaux-900 h-2 rounded-full" style={{ width: '24%' }} />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="font-medium">Nuove APS</span>
                                        <span className="text-gray-500">8/10</span>
                                    </div>
                                    <div className="w-full bg-gray-100 rounded-full h-2">
                                        <div className="bg-iss-gold-500 h-2 rounded-full" style={{ width: '80%' }} />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="font-medium">Candidature Approvate</span>
                                        <span className="text-gray-500">15/45</span>
                                    </div>
                                    <div className="w-full bg-gray-100 rounded-full h-2">
                                        <div className="bg-green-600 h-2 rounded-full" style={{ width: '33.3%' }} />
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </DashboardLayout>
    )
}
