import { Check, TrendingUp, Clock, AlertCircle, Home } from "lucide-react";
import { hapticFeedback } from "../../lib/haptics";

interface WorkoutSummaryProps {
  summary: {
    workout_id: string;
    workout_name: string;
    duration_minutes: number;
    exercises_completed: number;
    total_exercises: number;
    pain_checks: Array<{ exercise: string; pain_level: number }>;
    notes: string;
  };
  onClose: () => void;
}

export function WorkoutSummary({ summary, onClose }: WorkoutSummaryProps) {
  const completionRate =
    (summary.exercises_completed / summary.total_exercises) * 100;
  const avgPainLevel =
    summary.pain_checks.length > 0
      ? summary.pain_checks.reduce((sum, check) => sum + check.pain_level, 0) /
        summary.pain_checks.length
      : 0;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="bg-card rounded-lg shadow-xl max-w-2xl w-full p-8">
        {/* Success Icon */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900/20 rounded-full mb-4">
            <Check className="h-10 w-10 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-3xl font-bold mb-2">Workout Completato!</h1>
          <p className="text-muted-foreground">
            Ottimo lavoro! Ecco il riepilogo della tua sessione.
          </p>
        </div>

        {/* Workout Info */}
        <div className="bg-secondary/50 rounded-lg p-4 mb-6">
          <h2 className="font-semibold text-lg mb-2">{summary.workout_name}</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span>{summary.duration_minutes} minuti</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <span>{Math.round(completionRate)}% completato</span>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {/* Exercises Completed */}
          <div className="bg-primary/10 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-primary mb-1">
              {summary.exercises_completed}/{summary.total_exercises}
            </div>
            <div className="text-sm text-muted-foreground">Esercizi</div>
          </div>

          {/* Average Pain */}
          <div
            className={`rounded-lg p-4 text-center ${
              avgPainLevel >= 7
                ? "bg-red-100 dark:bg-red-900/20"
                : avgPainLevel >= 5
                  ? "bg-amber-100 dark:bg-amber-900/20"
                  : "bg-green-100 dark:bg-green-900/20"
            }`}
          >
            <div
              className={`text-3xl font-bold mb-1 ${
                avgPainLevel >= 7
                  ? "text-red-600 dark:text-red-400"
                  : avgPainLevel >= 5
                    ? "text-amber-600 dark:text-amber-400"
                    : "text-green-600 dark:text-green-400"
              }`}
            >
              {avgPainLevel > 0 ? avgPainLevel.toFixed(1) : "N/A"}
            </div>
            <div className="text-sm text-muted-foreground">Dolore Medio</div>
          </div>
        </div>

        {/* Pain Checks */}
        {summary.pain_checks.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              Pain Checks Durante Workout
            </h3>
            <div className="space-y-2">
              {summary.pain_checks.map((check, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-secondary rounded-lg text-sm"
                >
                  <span className="text-muted-foreground">
                    {check.exercise}
                  </span>
                  <span
                    className={`font-semibold ${
                      check.pain_level >= 7
                        ? "text-red-600 dark:text-red-400"
                        : check.pain_level >= 5
                          ? "text-amber-600 dark:text-amber-400"
                          : "text-green-600 dark:text-green-400"
                    }`}
                  >
                    {check.pain_level}/10
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        {summary.notes && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2">Note</h3>
            <div className="p-4 bg-secondary rounded-lg text-sm text-muted-foreground">
              {summary.notes}
            </div>
          </div>
        )}

        {/* Recommendations */}
        <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
            💡 Raccomandazioni
          </h3>
          <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-200">
            {avgPainLevel >= 7 && (
              <li>
                • Dolore elevato rilevato - Consulta il medico se persiste
              </li>
            )}
            {avgPainLevel >= 5 && avgPainLevel < 7 && (
              <li>
                • Dolore moderato - Considera di ridurre intensità nel prossimo
                workout
              </li>
            )}
            {avgPainLevel < 5 && (
              <li>• Ottimo! Dolore sotto controllo - Continua così</li>
            )}
            {completionRate === 100 && (
              <li>• Workout completato al 100% - Eccellente compliance!</li>
            )}
            {completionRate < 100 && (
              <li>
                • Prova a completare tutti gli esercizi nel prossimo workout
              </li>
            )}
          </ul>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={() => {
              hapticFeedback.selection();
              onClose();
            }}
            className="flex-1 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-semibold flex items-center justify-center gap-2"
          >
            <Home className="h-5 w-5" />
            Torna alla Home
          </button>
        </div>
      </div>
    </div>
  );
}
