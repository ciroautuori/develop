import { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { progressApi, type PainTrendData } from "../../lib/api";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import { hapticFeedback } from "../../lib/haptics";

interface PainTrendsChartProps {
  days?: number;
}

export function PainTrendsChart({
  days = 30,
}: PainTrendsChartProps) {
  const [trends, setTrends] = useState<PainTrendData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadTrends();
  }, [days]);

  const loadTrends = async () => {
    try {
      setIsLoading(true);
      const response = await progressApi.getPainTrends(days);
      setTrends(response?.data || []);
    } catch (error) {
      logger.error('Error loading pain trends', { error });
      hapticFeedback.notification("error");
      setTrends([]);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!trends || trends.length === 0) {
    return (
      <div className="text-center py-12 bg-muted/50 rounded-lg">
        <p className="text-muted-foreground">
          Nessun dato disponibile per il periodo selezionato
        </p>
      </div>
    );
  }

  // Prepare data for chart
  const chartData = (trends || []).map((trend) => ({
    date: format(new Date(trend.date), "dd MMM", { locale: it }),
    painLevel: trend.pain_level,
    fullDate: trend.date,
  }));

  // Calculate statistics
  const avgPain =
    trends && trends.length > 0
      ? trends.reduce((sum, t) => sum + t.pain_level, 0) / trends.length
      : 0;
  const maxPain = trends && trends.length > 0 ? Math.max(...trends.map((t) => t.pain_level)) : 0;
  const minPain = trends && trends.length > 0 ? Math.min(...trends.map((t) => t.pain_level)) : 0;
  const latestPain = trends && trends.length > 0 ? trends[trends.length - 1]?.pain_level || 0 : 0;

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div className="bg-card border rounded-lg p-4">
          <p className="text-sm text-muted-foreground mb-1">Attuale</p>
          <p className="text-2xl font-bold">{latestPain.toFixed(1)}</p>
        </div>
        <div className="bg-card border rounded-lg p-4">
          <p className="text-sm text-muted-foreground mb-1">Media</p>
          <p className="text-2xl font-bold">{avgPain.toFixed(1)}</p>
        </div>
        <div className="bg-card border rounded-lg p-4">
          <p className="text-sm text-muted-foreground mb-1">Massimo</p>
          <p className="text-2xl font-bold text-destructive">{maxPain}</p>
        </div>
        <div className="bg-card border rounded-lg p-4">
          <p className="text-sm text-muted-foreground mb-1">Minimo</p>
          <p className="text-2xl font-bold text-green-600">{minPain}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">
          Andamento Dolore (ultimi {days} giorni)
        </h3>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--background))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="painLevel"
                name="Livello Dolore"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Trend Analysis */}
      <div className="bg-card border rounded-lg p-4">
        <h4 className="font-semibold mb-2">Analisi Trend</h4>
        {latestPain < avgPain ? (
          <p className="text-green-600">
            ✅ Il dolore è sotto la media. Continua così!
          </p>
        ) : latestPain > avgPain ? (
          <p className="text-destructive">
            ⚠️ Il dolore è sopra la media. Considera di ridurre l'intensità.
          </p>
        ) : (
          <p className="text-muted-foreground">
            ℹ️ Il dolore è in linea con la media.
          </p>
        )}
      </div>
    </div>
  );
}
