import { useMemo, memo } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { AlertCircle } from 'lucide-react'
import { ProgressChartSkeleton } from '../../components/ui/Skeletons';
import type { DashboardData, PainAssessmentSummary } from '../../lib/api'

interface ProgressDashboardProps {
  data: DashboardData | null;
  isLoading: boolean;
  error?: string | null;
}

export const ProgressDashboard = memo(function ProgressDashboard({ data, isLoading, error }: ProgressDashboardProps) {
  // Transform API data for charts (memoized to prevent recalculation)
  const chartData = useMemo(() => {
    if (!data) return [];
    return data.recent_pain.map((item: PainAssessmentSummary) => ({
      name: new Date(item.date).toLocaleDateString('it-IT', { weekday: 'short' }),
      pain: item.pain_level,
      // Use real mobility_score from API - fallback to null (not displayed)
      mobility: (item as PainAssessmentSummary & { mobility_score?: number }).mobility_score ?? null
    }));
  }, [data]);

  // Check if we have any real mobility data
  const hasMobilityData = chartData.some(d => d.mobility !== null);

  // Loading state - Mobile first
  if (isLoading) {
    return (
      <div className="space-y-4 sm:grid sm:grid-cols-2 sm:gap-4 sm:space-y-0">
        <div className="bg-card border rounded-2xl p-4 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Andamento Livello Dolore</h3>
          <div className="h-[280px]">
            <ProgressChartSkeleton />
          </div>
        </div>
        <div className="bg-card border rounded-2xl p-4 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Punteggio Mobilità</h3>
          <div className="h-[280px]">
            <ProgressChartSkeleton />
          </div>
        </div>
      </div>
    )
  }

  // Error state - Mobile optimized
  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[200px] text-center p-6 border rounded-2xl bg-muted/5">
        <AlertCircle className="w-12 h-12 text-muted-foreground mb-3" />
        <h3 className="text-lg font-semibold mb-1">Dati non disponibili</h3>
        <p className="text-base text-muted-foreground">{error || "Prova a ricaricare la pagina."}</p>
      </div>
    )
  }

  // Empty state - no real points
  if (chartData.length === 0) {
    return (
      <div className="bg-card border rounded-2xl p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-2">Andamento Dolore</h3>
        <p className="text-sm text-muted-foreground">
          Nessun dato disponibile: fai almeno un check-in dolore per visualizzare i grafici.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:grid sm:grid-cols-2 sm:gap-4 sm:space-y-0">
      {/* Pain Trend Chart - Mobile optimized */}
      <div className="bg-card border rounded-2xl p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-4 text-center sm:text-left">Andamento Dolore</h3>
        <div className="h-[240px] sm:h-[280px] w-full touch-manipulation">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <defs>
                <linearGradient id="colorPain" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="name"
                className="text-xs text-muted-foreground"
                tick={{ fontSize: 11 }}
                tickMargin={8}
                axisLine={false}
              />
              <YAxis
                className="text-xs text-muted-foreground"
                tick={{ fontSize: 11 }}
                axisLine={false}
                domain={[0, 10]}
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--popover))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                itemStyle={{ color: 'hsl(var(--popover-foreground))' }}
              />
              <Area
                type="monotone"
                dataKey="pain"
                stroke="hsl(var(--destructive))"
                fillOpacity={1}
                fill="url(#colorPain)"
                animationDuration={1500}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Mobility Score Chart - Only shown when real data exists */}
      {hasMobilityData && (
        <div className="bg-card border rounded-2xl p-4 shadow-sm">
          <h3 className="text-lg font-semibold mb-4 text-center sm:text-left">Mobilità</h3>
          <div className="h-[240px] sm:h-[280px] w-full touch-manipulation">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="name"
                  className="text-xs text-muted-foreground"
                  tick={{ fontSize: 11 }}
                  tickMargin={8}
                  axisLine={false}
                />
                <YAxis
                  className="text-xs text-muted-foreground"
                  domain={[0, 10]}
                  tick={{ fontSize: 11 }}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: 'hsl(var(--popover))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                  itemStyle={{ color: 'hsl(var(--popover-foreground))' }}
                />
                <Line
                  type="monotone"
                  dataKey="mobility"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={{ r: 4, fill: 'hsl(var(--primary))' }}
                  activeDot={{ r: 6 }}
                  animationDuration={1500}
                  connectNulls
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
});

/**
 * KPICard - Mobile-first metrics card component
 */
export function KPICard({ title, value, change, subtext }: { title: string; value: string; change?: string; subtext?: string }) {
  return (
    <div className="bg-card border rounded-2xl p-4 shadow-sm transition-transform active:scale-[0.98] touch-manipulation">
      <h4 className="text-sm font-medium text-muted-foreground mb-2">{title}</h4>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl sm:text-3xl font-bold">{value}</span>
        {change && (
          <span className="text-sm font-semibold text-green-600 bg-green-100 px-2 py-0.5 rounded-md">
            {change}
          </span>
        )}
      </div>
      {subtext && (
        <p className="text-xs text-muted-foreground">{subtext}</p>
      )}
    </div>
  )
}
