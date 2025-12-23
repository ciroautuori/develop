import { useState, useEffect, useMemo } from "react";
import { logger } from "../../lib/logger";
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { progressApi, type DashboardData, type PainAssessmentSummary } from '../../lib/api'
import { AlertCircle } from 'lucide-react'

export function ProgressDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await progressApi.getDashboard()
        if (response.success) {
          setData(response)
        } else {
          setError("Errore nel caricamento dei dati.")
        }
      } catch (err) {
        logger.error('Failed to fetch dashboard data', { error: err });
        setError("Errore di connessione al server.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-80">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-80 text-center p-5">
        <AlertCircle className="h-16 w-16 text-muted-foreground mb-4" />
        <p className="text-lg font-semibold text-muted-foreground">{error || "Nessun dato disponibile."}</p>
      </div>
    )
  }

  const chartData = useMemo(() => {
    if (!data) return [];
    return data.recent_pain.map((item: PainAssessmentSummary) => ({
      name: new Date(item.date).toLocaleDateString('it-IT', { weekday: 'short' }),
      pain: item.pain_level
    }));
  }, [data]);

  return (
    <div className="grid gap-6 md:grid-cols-2 p-4 md:p-6">
      {/* Pain Trend Chart */}
      <div className="bg-card border-2 border-border rounded-xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-5">Andamento Livello Dolore</h3>
        <div className="h-[320px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorPain" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="name"
                className="text-sm text-muted-foreground"
                tick={{ fontSize: 14 }}
              />
              <YAxis
                className="text-sm text-muted-foreground"
                tick={{ fontSize: 14 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--popover))',
                  borderColor: 'hsl(var(--border))',
                  borderRadius: '12px',
                  fontSize: '14px',
                  fontWeight: 600
                }}
                itemStyle={{ color: 'hsl(var(--popover-foreground))' }}
              />
              <Area
                type="monotone"
                dataKey="pain"
                stroke="hsl(var(--destructive))"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorPain)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Workout Completion */}
      <div className="bg-card border-2 border-border rounded-xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-5">Workout Completati</h3>
        <div className="h-[320px] flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl font-bold text-primary mb-3">
              {data.recent_workouts?.length || 0}
            </div>
            <p className="text-base text-muted-foreground font-medium">
              Ultimi 30 giorni
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
