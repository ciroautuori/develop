import { useState, useCallback, useMemo, useEffect } from "react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
import {
  Trophy,
  TrendingUp,
  Calculator,
  ChevronUp,
  ChevronDown,
  Flame,
  Star,
  Target,
  Zap,
  Award,
  X,
  Plus,
  History,
  BarChart3,
} from "lucide-react";
import confetti from "canvas-confetti";

// ============================================================================
// TYPES
// ============================================================================

interface PersonalRecord {
  id: string;
  exercise: string;
  weight: number;
  reps: number;
  date: string;
  estimated1RM: number;
  isPR: boolean;
}

interface SetLog {
  setNumber: number;
  weight: number;
  reps: number;
  rpe?: number;
  notes?: string;
  timestamp: Date;
}

interface ExerciseLog {
  exerciseId: string;
  exerciseName: string;
  sets: SetLog[];
  personalBest?: number;
}

interface WeightTrackerProps {
  exerciseId?: string;
  exerciseName?: string;
  targetSets?: number;
  targetReps?: string;
  suggestedWeight?: number;
  previousBest?: number;
  onSetComplete?: (set: SetLog) => void;
  onExerciseComplete?: (log: ExerciseLog) => void;
  compact?: boolean;
}

// ============================================================================
// 1RM CALCULATOR FORMULAS
// ============================================================================

const calculate1RM = (weight: number, reps: number, formula: "epley" | "brzycki" | "lombardi" = "epley"): number => {
  if (reps === 1) return weight;
  if (reps <= 0 || weight <= 0) return 0;

  switch (formula) {
    case "epley":
      return weight * (1 + reps / 30);
    case "brzycki":
      return weight * (36 / (37 - reps));
    case "lombardi":
      return weight * Math.pow(reps, 0.1);
    default:
      return weight * (1 + reps / 30);
  }
};

const calculateWeight = (oneRM: number, targetReps: number): number => {
  if (targetReps === 1) return oneRM;
  // Inverse Epley formula
  return oneRM / (1 + targetReps / 30);
};

// ============================================================================
// CELEBRATION UTILS
// ============================================================================

const celebratePR = () => {
  // Confetti explosion
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: ["#FFD700", "#FFA500", "#FF6347", "#32CD32", "#1E90FF"],
  });

  // Haptic feedback
  hapticFeedback.notification("success");

  // Additional burst
  setTimeout(() => {
    confetti({
      particleCount: 50,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
    });
    confetti({
      particleCount: 50,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
    });
  }, 200);
};

// ============================================================================
// RPE SCALE COMPONENT
// ============================================================================

interface RPEInputProps {
  value?: number;
  onChange: (rpe: number) => void;
}

function RPEInput({ value, onChange }: RPEInputProps) {
  const rpeDescriptions: Record<number, string> = {
    6: "Molto leggero",
    7: "Leggero",
    8: "Moderato",
    9: "Difficile",
    10: "Massimale",
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground font-medium">RPE:</span>
      <div className="flex gap-1">
        {[6, 7, 8, 9, 10].map((rpe) => (
          <button
            key={rpe}
            onClick={() => {
              hapticFeedback.selection();
              onChange(rpe);
            }}
            className={cn(
              "w-8 h-8 rounded-lg text-sm font-bold transition-all",
              value === rpe
                ? rpe >= 9
                  ? "bg-red-500 text-white"
                  : rpe >= 8
                  ? "bg-orange-500 text-white"
                  : "bg-green-500 text-white"
                : "bg-secondary hover:bg-secondary/80"
            )}
            title={rpeDescriptions[rpe]}
          >
            {rpe}
          </button>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// 1RM CALCULATOR MODAL
// ============================================================================

interface OneRMCalculatorProps {
  isOpen: boolean;
  onClose: () => void;
  exerciseName?: string;
  currentPR?: number;
}

function OneRMCalculator({ isOpen, onClose, exerciseName, currentPR }: OneRMCalculatorProps) {
  const [weight, setWeight] = useState(0);
  const [reps, setReps] = useState(1);
  const [formula, setFormula] = useState<"epley" | "brzycki" | "lombardi">("epley");

  const estimated1RM = useMemo(() => calculate1RM(weight, reps, formula), [weight, reps, formula]);
  const isPotentialPR = currentPR ? estimated1RM > currentPR : false;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-card rounded-2xl shadow-2xl border max-w-md w-full overflow-hidden">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-primary/10 rounded-xl">
                <Calculator className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-bold text-lg">Calcola 1RM</h3>
                {exerciseName && (
                  <p className="text-sm text-muted-foreground">{exerciseName}</p>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-secondary transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Input Fields */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Peso (kg)</label>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setWeight(Math.max(0, weight - 2.5))}
                  className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
                >
                  <ChevronDown className="w-4 h-4" />
                </button>
                <input
                  type="number"
                  value={weight}
                  onChange={(e) => setWeight(parseFloat(e.target.value) || 0)}
                  className="w-20 text-center font-mono text-xl font-bold bg-secondary rounded-lg py-2"
                />
                <button
                  onClick={() => setWeight(weight + 2.5)}
                  className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
                >
                  <ChevronUp className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Reps</label>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setReps(Math.max(1, reps - 1))}
                  className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
                >
                  <ChevronDown className="w-4 h-4" />
                </button>
                <input
                  type="number"
                  value={reps}
                  onChange={(e) => setReps(parseInt(e.target.value) || 1)}
                  className="w-20 text-center font-mono text-xl font-bold bg-secondary rounded-lg py-2"
                />
                <button
                  onClick={() => setReps(reps + 1)}
                  className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
                >
                  <ChevronUp className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Formula Selector */}
          <div className="mb-6">
            <label className="text-sm font-medium mb-2 block">Formula</label>
            <div className="flex gap-2">
              {(["epley", "brzycki", "lombardi"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFormula(f)}
                  className={cn(
                    "flex-1 py-2 rounded-lg text-sm font-medium capitalize transition-all",
                    formula === f
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary hover:bg-secondary/80"
                  )}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Result */}
          <div className={cn(
            "p-6 rounded-xl text-center",
            isPotentialPR
              ? "bg-gradient-to-br from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 border-2 border-yellow-400"
              : "bg-secondary/50"
          )}>
            {isPotentialPR && (
              <div className="flex items-center justify-center gap-2 mb-2">
                <Trophy className="w-5 h-5 text-yellow-500" />
                <span className="text-sm font-bold text-yellow-600 dark:text-yellow-400">
                  Potenziale Nuovo Record!
                </span>
              </div>
            )}
            <div className="text-4xl font-bold font-mono mb-1">
              {estimated1RM.toFixed(1)} <span className="text-lg text-muted-foreground">kg</span>
            </div>
            <p className="text-sm text-muted-foreground">1RM Stimato</p>
            {currentPR && (
              <p className="text-xs text-muted-foreground mt-2">
                Record attuale: {currentPR} kg
                {isPotentialPR && (
                  <span className="text-green-500 font-bold ml-1">
                    (+{(estimated1RM - currentPR).toFixed(1)} kg)
                  </span>
                )}
              </p>
            )}
          </div>

          {/* Percentage Table */}
          <div className="mt-6">
            <h4 className="text-sm font-medium mb-3">Pesi suggeriti per reps</h4>
            <div className="grid grid-cols-4 gap-2 text-center text-sm">
              {[1, 3, 5, 8, 10, 12, 15, 20].map((targetReps) => (
                <div key={targetReps} className="bg-secondary/50 rounded-lg p-2">
                  <div className="font-bold">{calculateWeight(estimated1RM, targetReps).toFixed(1)}</div>
                  <div className="text-xs text-muted-foreground">{targetReps} reps</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// PR CELEBRATION MODAL
// ============================================================================

interface PRCelebrationProps {
  isOpen: boolean;
  onClose: () => void;
  exercise: string;
  newRecord: number;
  previousRecord?: number;
  reps: number;
}

function PRCelebration({ isOpen, onClose, exercise, newRecord, previousRecord, reps }: PRCelebrationProps) {
  useEffect(() => {
    if (isOpen) {
      celebratePR();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const improvement = previousRecord ? newRecord - previousRecord : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 rounded-3xl shadow-2xl p-1 max-w-sm w-full">
        <div className="bg-card rounded-[22px] p-8 text-center">
          <div className="w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center animate-bounce">
            <Trophy className="w-12 h-12 text-white" />
          </div>

          <h2 className="text-3xl font-bold mb-2">🎉 NUOVO PR! 🎉</h2>
          <p className="text-lg text-muted-foreground mb-4">{exercise}</p>

          <div className="bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 rounded-2xl p-6 mb-6">
            <div className="text-5xl font-bold font-mono text-orange-600 dark:text-orange-400">
              {newRecord} <span className="text-2xl">kg</span>
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              × {reps} reps
            </div>
            {improvement > 0 && (
              <div className="flex items-center justify-center gap-1 mt-3 text-green-600 dark:text-green-400 font-bold">
                <TrendingUp className="w-4 h-4" />
                +{improvement.toFixed(1)} kg dal precedente
              </div>
            )}
          </div>

          <button
            onClick={onClose}
            className="w-full py-4 rounded-xl font-bold text-white bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 transition-all active:scale-[0.98]"
          >
            Continua 💪
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN WEIGHT TRACKER COMPONENT
// ============================================================================

export function WeightTracker({
  exerciseId = "exercise-1",
  exerciseName = "Back Squat",
  targetSets = 5,
  targetReps = "5",
  suggestedWeight = 80,
  previousBest = 100,
  onSetComplete,
  onExerciseComplete,
  compact = false,
}: WeightTrackerProps) {
  // State
  const [sets, setSets] = useState<SetLog[]>([]);
  const [currentWeight, setCurrentWeight] = useState(suggestedWeight);
  const [currentReps, setCurrentReps] = useState(parseInt(targetReps) || 5);
  const [currentRPE, setCurrentRPE] = useState<number | undefined>();
  const [showCalculator, setShowCalculator] = useState(false);
  const [showPRCelebration, setShowPRCelebration] = useState(false);
  const [newPR, setNewPR] = useState<{ weight: number; reps: number } | null>(null);

  // Calculate current estimated 1RM
  const currentEstimated1RM = useMemo(
    () => calculate1RM(currentWeight, currentReps),
    [currentWeight, currentReps]
  );

  // Check if current set would be a PR
  const wouldBePR = currentEstimated1RM > (previousBest || 0);

  // Log set
  const logSet = useCallback(() => {
    const newSet: SetLog = {
      setNumber: sets.length + 1,
      weight: currentWeight,
      reps: currentReps,
      rpe: currentRPE,
      timestamp: new Date(),
    };

    setSets((prev) => [...prev, newSet]);
    onSetComplete?.(newSet);
    hapticFeedback.impact("medium");

    // Check for PR
    if (wouldBePR) {
      setNewPR({ weight: currentWeight, reps: currentReps });
      setShowPRCelebration(true);
    }

    // Reset RPE for next set
    setCurrentRPE(undefined);

    // Check if exercise complete
    if (sets.length + 1 >= targetSets) {
      setTimeout(() => {
        onExerciseComplete?.({
          exerciseId,
          exerciseName,
          sets: [...sets, newSet],
          personalBest: wouldBePR ? currentEstimated1RM : previousBest,
        });
      }, wouldBePR ? 3000 : 500);
    }
  }, [sets, currentWeight, currentReps, currentRPE, targetSets, wouldBePR, currentEstimated1RM, previousBest, exerciseId, exerciseName, onSetComplete, onExerciseComplete]);

  // Best set of current session
  const bestSet = useMemo(() => {
    if (sets.length === 0) return null;
    return sets.reduce((best, set) => {
      const setRM = calculate1RM(set.weight, set.reps);
      const bestRM = calculate1RM(best.weight, best.reps);
      return setRM > bestRM ? set : best;
    });
  }, [sets]);

  return (
    <div className={cn(
      "bg-gradient-to-b from-card to-card/95 rounded-2xl border shadow-sm",
      compact ? "p-4" : "p-6"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl">
            <BarChart3 className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-bold text-lg">{exerciseName}</h3>
            <p className="text-xs text-muted-foreground">
              {targetSets} × {targetReps} reps
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {previousBest && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
              <Trophy className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
              <span className="text-sm font-bold text-yellow-700 dark:text-yellow-300">
                {previousBest} kg
              </span>
            </div>
          )}
          <button
            onClick={() => setShowCalculator(true)}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
          >
            <Calculator className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="font-medium">Progresso</span>
          <span className="text-muted-foreground">
            {sets.length} / {targetSets} serie
          </span>
        </div>
        <div className="h-3 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-primary/80 transition-all duration-500"
            style={{ width: `${(sets.length / targetSets) * 100}%` }}
          />
        </div>
      </div>

      {/* Weight & Reps Input */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Weight */}
        <div className="bg-secondary/50 rounded-xl p-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Peso (kg)
          </label>
          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => setCurrentWeight(Math.max(0, currentWeight - 2.5))}
              className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
            >
              <ChevronDown className="w-5 h-5" />
            </button>
            <input
              type="number"
              value={currentWeight}
              onChange={(e) => setCurrentWeight(parseFloat(e.target.value) || 0)}
              className="w-24 text-center font-mono text-3xl font-bold bg-transparent"
              step={2.5}
            />
            <button
              onClick={() => setCurrentWeight(currentWeight + 2.5)}
              className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
            >
              <ChevronUp className="w-5 h-5" />
            </button>
          </div>
          {suggestedWeight && currentWeight !== suggestedWeight && (
            <button
              onClick={() => setCurrentWeight(suggestedWeight)}
              className="w-full text-xs text-primary hover:underline mt-2"
            >
              Suggerito: {suggestedWeight} kg
            </button>
          )}
        </div>

        {/* Reps */}
        <div className="bg-secondary/50 rounded-xl p-4">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Reps
          </label>
          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => setCurrentReps(Math.max(1, currentReps - 1))}
              className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
            >
              <ChevronDown className="w-5 h-5" />
            </button>
            <input
              type="number"
              value={currentReps}
              onChange={(e) => setCurrentReps(parseInt(e.target.value) || 1)}
              className="w-24 text-center font-mono text-3xl font-bold bg-transparent"
            />
            <button
              onClick={() => setCurrentReps(currentReps + 1)}
              className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95"
            >
              <ChevronUp className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* 1RM Preview */}
      <div className={cn(
        "p-4 rounded-xl mb-4 flex items-center justify-between",
        wouldBePR
          ? "bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 border-2 border-yellow-400"
          : "bg-secondary/50"
      )}>
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-muted-foreground" />
          <span className="text-sm font-medium">1RM Stimato:</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono font-bold text-lg">{currentEstimated1RM.toFixed(1)} kg</span>
          {wouldBePR && (
            <span className="flex items-center gap-1 text-yellow-600 dark:text-yellow-400 font-bold text-sm">
              <Flame className="w-4 h-4" />
              PR!
            </span>
          )}
        </div>
      </div>

      {/* RPE Input */}
      {!compact && (
        <div className="mb-6">
          <RPEInput value={currentRPE} onChange={setCurrentRPE} />
        </div>
      )}

      {/* Log Set Button */}
      <button
        onClick={logSet}
        disabled={sets.length >= targetSets}
        className={cn(
          "w-full py-4 rounded-xl font-bold text-lg transition-all active:scale-[0.98]",
          sets.length >= targetSets
            ? "bg-green-500 text-white"
            : wouldBePR
            ? "bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg shadow-orange-500/25"
            : "bg-primary text-primary-foreground hover:bg-primary/90"
        )}
      >
        {sets.length >= targetSets ? (
          <span className="flex items-center justify-center gap-2">
            <Award className="w-5 h-5" />
            Esercizio Completato!
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2">
            <Plus className="w-5 h-5" />
            Log Serie {sets.length + 1}
            {wouldBePR && " 🔥"}
          </span>
        )}
      </button>

      {/* Set History */}
      {sets.length > 0 && (
        <div className="mt-6 pt-6 border-t">
          <div className="flex items-center gap-2 text-sm font-semibold mb-3">
            <History className="w-4 h-4" />
            Serie Completate
          </div>
          <div className="space-y-2">
            {sets.map((set, i) => {
              const isBest = bestSet && set === bestSet;
              return (
                <div
                  key={i}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg",
                    isBest
                      ? "bg-yellow-100 dark:bg-yellow-900/30 border border-yellow-400"
                      : "bg-secondary/50"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-muted-foreground">
                      Serie {set.setNumber}
                    </span>
                    {isBest && <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />}
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="font-mono font-bold">{set.weight} kg</span>
                    <span className="text-muted-foreground">×</span>
                    <span className="font-mono font-bold">{set.reps}</span>
                    {set.rpe && (
                      <span className={cn(
                        "px-2 py-0.5 rounded text-xs font-bold",
                        set.rpe >= 9 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                        set.rpe >= 8 ? "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400" :
                        "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      )}>
                        RPE {set.rpe}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Modals */}
      <OneRMCalculator
        isOpen={showCalculator}
        onClose={() => setShowCalculator(false)}
        exerciseName={exerciseName}
        currentPR={previousBest}
      />

      {newPR && (
        <PRCelebration
          isOpen={showPRCelebration}
          onClose={() => {
            setShowPRCelebration(false);
            setNewPR(null);
          }}
          exercise={exerciseName}
          newRecord={newPR.weight}
          previousRecord={previousBest}
          reps={newPR.reps}
        />
      )}
    </div>
  );
}
