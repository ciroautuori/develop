import { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import { CheckCircle2, XCircle, Calendar, TrendingUp } from "lucide-react";
import { progressApi, type WorkoutHistoryItem } from "../../lib/api";
import { toast } from "sonner";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import { hapticFeedback } from "../../lib/haptics";

interface WorkoutHistoryProps {
  limit?: number;
}

export function WorkoutHistory({
  limit = 10,
}: WorkoutHistoryProps) {
  const [workouts, setWorkouts] = useState<WorkoutHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, [limit]);

  const loadHistory = async () => {
    try {
      setIsLoading(true);
      const response = await progressApi.getWorkoutHistory(limit);
      setWorkouts(response.workouts);
    } catch (error) {
      logger.error('Error loading workout history', { error });
      hapticFeedback.notification("error");
      toast.error("Errore nel caricamento dello storico");
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

  if (workouts.length === 0) {
    return (
      <div className="text-center py-12 bg-muted/50 rounded-lg">
        <p className="text-muted-foreground">
          Nessun workout completato ancora
        </p>
      </div>
    );
  }

  // Calculate statistics
  const completedCount = workouts.filter((w) => w.completed).length;
  const completionRate = (completedCount / workouts.length) * 100;
  const avgPainImpact =
    workouts
      .filter((w) => w.completed)
      .reduce((sum, w) => sum + w.pain_impact, 0) / completedCount || 0;

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-card border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="text-green-600" size={20} />
            <p className="text-sm text-muted-foreground">Completati</p>
          </div>
          <p className="text-2xl font-bold">
            {completedCount}/{workouts.length}
          </p>
        </div>

        <div className="bg-card border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="text-primary" size={20} />
            <p className="text-sm text-muted-foreground">Tasso Completamento</p>
          </div>
          <p className="text-2xl font-bold">{completionRate.toFixed(0)}%</p>
        </div>

        <div className="bg-card border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="text-muted-foreground" size={20} />
            <p className="text-sm text-muted-foreground">
              Impatto Dolore Medio
            </p>
          </div>
          <p className="text-2xl font-bold">{avgPainImpact.toFixed(1)}/10</p>
        </div>
      </div>

      {/* Workout List */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold">Storico Workout</h3>
        {workouts.map((workout) => (
          <div
            key={workout.id}
            className="bg-card border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  {workout.completed ? (
                    <CheckCircle2 className="text-green-600" size={20} />
                  ) : (
                    <XCircle className="text-muted-foreground" size={20} />
                  )}
                  <h4 className="font-semibold">
                    {format(new Date(workout.date), "EEEE, dd MMMM yyyy", {
                      locale: it,
                    })}
                  </h4>
                </div>

                <div className="flex flex-wrap gap-2 mb-2">
                  <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">
                    {workout.phase.toUpperCase()}
                  </span>
                  <span className="text-xs px-2 py-1 bg-muted rounded-full">
                    {workout.completed_exercises}/{workout.total_exercises}{" "}
                    esercizi
                  </span>
                  {workout.completed && (
                    <span className="text-xs px-2 py-1 bg-muted rounded-full">
                      Dolore: {workout.pain_impact}/10
                    </span>
                  )}
                </div>

                {workout.feedback && (
                  <p className="text-sm text-muted-foreground italic mt-2">
                    "{workout.feedback}"
                  </p>
                )}
              </div>

              {/* Progress Bar */}
              <div className="ml-4">
                <div className="w-16 h-16 relative">
                  <svg className="w-full h-full" viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="hsl(var(--muted))"
                      strokeWidth="3"
                    />
                    <path
                      d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="hsl(var(--primary))"
                      strokeWidth="3"
                      strokeDasharray={`${(workout.completed_exercises /
                          (workout.total_exercises || 1)) *
                        100
                        }, 100`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-semibold">
                      {Math.round(
                        (workout.completed_exercises /
                          (workout.total_exercises || 1)) *
                        100
                      )}
                      %
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
