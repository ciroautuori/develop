import { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";
import { checkinApi } from "../../lib/api";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

interface PainData {
  date: string;
  pain_level: number;
}

export function PainTrendMiniChart({ days = 7 }: { days?: number }) {
  const [painData, setPainData] = useState<PainData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [trend, setTrend] = useState<"up" | "down" | "stable">("stable");

  useEffect(() => {
    const fetchPainHistory = async () => {
      try {
        const response = await checkinApi.getHistory(days);
        if (response.success && response.assessments) {
          const data = response.assessments.map((a: { timestamp: string; pain_level: number }) => ({
            date: a.timestamp,
            pain_level: a.pain_level,
          }));
          setPainData(data);

          if (data.length >= 2) {
            const recent =
              data
                .slice(-3)
                .reduce((sum: number, d: PainData) => sum + d.pain_level, 0) /
              Math.min(3, data.length);
            const older =
              data
                .slice(0, 3)
                .reduce((sum: number, d: PainData) => sum + d.pain_level, 0) /
              Math.min(3, data.length);

            if (recent < older - 0.5) setTrend("down");
            else if (recent > older + 0.5) setTrend("up");
            else setTrend("stable");
          }
        }
      } catch (error) {
        logger.error('Failed to fetch pain history', { error });
        hapticFeedback.notification("error");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPainHistory();
  }, [days]);

  if (isLoading) {
    return (
      <div className="bg-card rounded-xl p-3 border animate-pulse shadow-sm">
        <div className="h-4 bg-secondary rounded w-1/2 mb-2"></div>
        <div className="h-20 bg-secondary rounded"></div>
      </div>
    );
  }

  const maxPain = Math.max(...painData.map((d) => d.pain_level), 10);
  const avgPain =
    painData.length > 0
      ? painData.reduce((sum, d) => sum + d.pain_level, 0) / painData.length
      : 0;

  return (
    <div className="bg-card rounded-xl p-3 border shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold text-sm">Trend Dolore ({days}g)</h3>
        <div
          className={cn(
            "flex items-center gap-1 text-xs font-semibold",
            trend === "down"
              ? "text-green-600 dark:text-green-400"
              : trend === "up"
                ? "text-red-600 dark:text-red-400"
                : "text-muted-foreground"
          )}
        >
          {trend === "down" && (
            <>
              <TrendingDown className="h-4 w-4" /> Miglioramento
            </>
          )}
          {trend === "up" && (
            <>
              <TrendingUp className="h-4 w-4" /> Peggioramento
            </>
          )}
          {trend === "stable" && (
            <>
              <Minus className="h-4 w-4" /> Stabile
            </>
          )}
        </div>
      </div>

      <div className="relative h-20 flex items-end gap-1">
        {painData.length > 0 ? (
          painData.map((data, index) => (
            <div
              key={index}
              className="flex-1 bg-primary/20 hover:bg-primary/40 transition-all duration-200 rounded-t relative group cursor-pointer"
              style={{ height: `${(data.pain_level / maxPain) * 100}%` }}
            >
              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-popover text-popover-foreground px-2 py-1 rounded-lg text-xs font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-lg">
                {data.pain_level}/10
              </div>
            </div>
          ))
        ) : (
          <div className="w-full h-full flex items-center justify-center text-sm text-muted-foreground">
            Nessun dato disponibile
          </div>
        )}
      </div>

      <div className="mt-2 pt-2 border-t flex items-center justify-between text-xs">
        <div>
          <span className="text-muted-foreground">Media: </span>
          <span className="font-bold text-sm">{avgPain.toFixed(1)}/10</span>
        </div>
        <div>
          <span className="text-muted-foreground">Valutazioni: </span>
          <span className="font-bold text-sm">{painData.length}</span>
        </div>
      </div>
    </div>
  );
}
