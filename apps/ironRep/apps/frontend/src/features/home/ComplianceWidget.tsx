import { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import { CheckCircle, Target } from "lucide-react";
import { progressApi } from "../../lib/api";
import { cn } from "../../lib/utils";

export function ComplianceWidget() {
  const [compliance, setCompliance] = useState(0);
  const [workoutsCompleted, setWorkoutsCompleted] = useState(0);
  const [workoutsTotal, setWorkoutsTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCompliance = async () => {
      try {
        const response = await progressApi.getKPIs(14);
        if (response.success && response.kpis && response.kpis.length > 0) {
          const latestKPI = response.kpis[response.kpis.length - 1];
          setCompliance(latestKPI.compliance_rate || 0);
          setWorkoutsCompleted(latestKPI.workouts_completed || 0);
          setWorkoutsTotal(latestKPI.workouts_scheduled || 0);
        }
      } catch (error: unknown) {
        logger.error('Failed to fetch compliance data', { error });
        setCompliance(0);
        setWorkoutsCompleted(0);
        setWorkoutsTotal(0);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompliance();
  }, []);

  if (isLoading) {
    return (
      <div className="bg-card rounded-xl p-3 border animate-pulse shadow-sm">
        <div className="h-4 bg-secondary rounded w-1/2 mb-2"></div>
        <div className="h-16 bg-secondary rounded"></div>
      </div>
    );
  }

  if (workoutsTotal === 0) {
    return (
      <div className="bg-card rounded-xl p-3 border shadow-sm text-center">
        <p className="text-muted-foreground text-sm">
          Inizia il tuo primo workout per vedere la compliance
        </p>
      </div>
    );
  }

  const complianceColor =
    compliance >= 80
      ? "text-green-600 dark:text-green-400"
      : compliance >= 60
        ? "text-amber-600 dark:text-amber-400"
        : "text-red-600 dark:text-red-400";

  return (
    <div className="bg-card rounded-xl p-3 border shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold text-sm flex items-center gap-1.5">
          <Target className="h-4 w-4 text-primary" />
          Compliance
        </h3>
        <span className={cn("text-base font-bold", complianceColor)}>
          {Math.round(compliance)}%
        </span>
      </div>

      <div className="h-2.5 w-full bg-secondary rounded-full overflow-hidden mb-2.5">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500",
            compliance >= 80
              ? "bg-green-500"
              : compliance >= 60
                ? "bg-amber-500"
                : "bg-red-500"
          )}
          style={{ width: `${compliance}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground flex items-center gap-1.5">
          <CheckCircle className="h-3.5 w-3.5" />
          Workout:{" "}
          <span className="font-semibold text-foreground">
            {workoutsCompleted}/{workoutsTotal}
          </span>
        </span>

        {compliance >= 80 ? (
          <span className="text-green-600 dark:text-green-400 font-semibold">
            Ottimo!
          </span>
        ) : compliance >= 60 ? (
          <span className="text-amber-600 dark:text-amber-400 font-semibold">
            Migliorabile
          </span>
        ) : (
          <span className="text-red-600 dark:text-red-400 font-semibold">
            Attenzione
          </span>
        )}
      </div>
    </div>
  );
}
