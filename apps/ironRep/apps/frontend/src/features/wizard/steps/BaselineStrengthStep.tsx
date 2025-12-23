/**
 * BaselineStrengthStep - Wizard Step for Baseline Strength Metrics
 *
 * Collects: baseline_deadlift_1rm, baseline_squat_1rm
 * Only shown if coach_mode enabled and sport requires strength baseline
 *
 * @production-ready Optional with skip, helpful hints, kg/lbs conversion
 */

import { useState } from "react";
import { Dumbbell, TrendingUp, Info } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

export interface BaselineStrength {
  baseline_deadlift_1rm?: number;
  baseline_squat_1rm?: number;
}

interface BaselineStrengthStepProps {
  onComplete: (data: BaselineStrength) => void;
  onSkip: () => void;
  initialData?: Partial<BaselineStrength>;
}

export function BaselineStrengthStep({ onComplete, onSkip, initialData }: BaselineStrengthStepProps) {
  const [deadlift, setDeadlift] = useState<string>(initialData?.baseline_deadlift_1rm?.toString() || "");
  const [squat, setSquat] = useState<string>(initialData?.baseline_squat_1rm?.toString() || "");
  const [showInfo, setShowInfo] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (deadlift) {
      const deadliftNum = parseFloat(deadlift);
      if (isNaN(deadliftNum) || deadliftNum < 20 || deadliftNum > 500) {
        newErrors.deadlift = "1RM Deadlift deve essere tra 20 e 500 kg";
      }
    }

    if (squat) {
      const squatNum = parseFloat(squat);
      if (isNaN(squatNum) || squatNum < 20 || squatNum > 500) {
        newErrors.squat = "1RM Squat deve essere tra 20 e 500 kg";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) {
      hapticFeedback.notification("error");
      return;
    }

    // Allow submission even if both are empty (skip equivalent)
    if (!deadlift && !squat) {
      handleSkip();
      return;
    }

    hapticFeedback.notification("success");
    onComplete({
      baseline_deadlift_1rm: deadlift ? parseFloat(deadlift) : undefined,
      baseline_squat_1rm: squat ? parseFloat(squat) : undefined,
    });
  };

  const handleSkip = () => {
    hapticFeedback.selection();
    onSkip();
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-background to-secondary/10 overflow-hidden">
      {/* Content (NO SCROLL) */}
      <div className="flex-1 overflow-hidden px-4 py-6 pb-safe">
        <div className="max-w-md mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="text-center space-y-2 pt-4">
            <div className="w-16 h-16 mx-auto bg-blue-50 dark:bg-blue-950/20 rounded-full flex items-center justify-center">
              <Dumbbell className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold">Forza Baseline</h2>
            <p className="text-muted-foreground text-sm px-4">
              Opzionale - aiuta il Coach a programmare carichi ottimali
            </p>
          </div>

          {/* Info Toggle */}
          <button
            onClick={() => setShowInfo(!showInfo)}
            className="w-full flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950/20 rounded-xl text-sm transition-all touch-manipulation"
          >
            <span className="flex items-center gap-2 text-blue-700 dark:text-blue-300 font-medium">
              <Info className="w-4 h-4" />
              Cos'è il 1RM?
            </span>
            <span className="text-blue-600">{showInfo ? "−" : "+"}</span>
          </button>

          {showInfo && (
            <div className="p-4 bg-muted/50 rounded-xl text-sm space-y-2 animate-in slide-in-from-top-2">
              <p className="font-medium">1RM = One Rep Max</p>
              <p className="text-muted-foreground">
                Il massimo peso che puoi sollevare per <strong>una singola ripetizione</strong> con tecnica corretta.
              </p>
              <p className="text-muted-foreground">
                <strong>Non sai il tuo 1RM?</strong> Puoi calcolarlo: se fai 5 reps con 100kg, il tuo stimato 1RM è circa 112-115kg.
              </p>
            </div>
          )}

          <div className="space-y-4">
            {/* Deadlift 1RM */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-muted-foreground" />
                1RM Deadlift (kg)
              </label>
              <input
                type="number"
                inputMode="decimal"
                value={deadlift}
                onChange={(e) => setDeadlift(e.target.value)}
                placeholder="es. 140"
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background text-lg",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation",
                  errors.deadlift && "border-red-500 focus:ring-red-500/20"
                )}
                min="20"
                max="500"
                step="2.5"
              />
              {errors.deadlift && (
                <p className="text-sm text-red-500">{errors.deadlift}</p>
              )}
              {deadlift && !errors.deadlift && (
                <p className="text-xs text-muted-foreground">
                  ≈ {(parseFloat(deadlift) * 2.20462).toFixed(0)} lbs
                </p>
              )}
            </div>

            {/* Squat 1RM */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-muted-foreground" />
                1RM Squat (kg)
              </label>
              <input
                type="number"
                inputMode="decimal"
                value={squat}
                onChange={(e) => setSquat(e.target.value)}
                placeholder="es. 120"
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background text-lg",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation",
                  errors.squat && "border-red-500 focus:ring-red-500/20"
                )}
                min="20"
                max="500"
                step="2.5"
              />
              {errors.squat && (
                <p className="text-sm text-red-500">{errors.squat}</p>
              )}
              {squat && !errors.squat && (
                <p className="text-xs text-muted-foreground">
                  ≈ {(parseFloat(squat) * 2.20462).toFixed(0)} lbs
                </p>
              )}
            </div>
          </div>

          {/* Strength Ratio Hint */}
          {deadlift && squat && !errors.deadlift && !errors.squat && (
            <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-xl">
              <p className="text-sm font-medium text-green-900 dark:text-green-200">
                Ratio Deadlift/Squat: {(parseFloat(deadlift) / parseFloat(squat)).toFixed(2)}
              </p>
              <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                Ideale: 1.10-1.25 (il deadlift dovrebbe essere leggermente più alto dello squat)
              </p>
            </div>
          )}

          {/* Buttons */}
          <div className="space-y-3">
            <button
              onClick={handleSubmit}
              className={cn(
                "w-full py-4 rounded-xl font-semibold text-white transition-all touch-manipulation",
                "bg-primary hover:bg-primary/90 active:scale-98"
              )}
            >
              {deadlift || squat ? "Continua" : "Salta per ora"}
            </button>

            <button
              onClick={handleSkip}
              className="w-full py-3 text-sm text-muted-foreground hover:text-foreground transition-colors touch-manipulation"
            >
              Non conosco i miei 1RM (compila dopo)
            </button>
          </div>

          {/* Note */}
          <p className="text-xs text-center text-muted-foreground pb-4">
            💡 Puoi aggiornare questi valori in qualsiasi momento dal tuo profilo
          </p>
        </div>
      </div>
    </div>
  );
}
