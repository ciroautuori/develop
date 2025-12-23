import { useState } from "react";
import {
  CheckCircle2,
  Circle,
  Clock,
  Play,
  ChevronRight,
  ChevronLeft,
  Timer,
} from "lucide-react";
import { cn } from "../../lib/utils";
import { type Workout } from "../../lib/api";
import { SwipeableCard } from "../../components/ui/mobile/SwipeableCard";
import { motion, AnimatePresence } from "framer-motion";
import { touchTarget } from "../../lib/touch-targets";
import { hapticFeedback } from "../../lib/haptics";
import { CrossFitTimer } from "./CrossFitTimer";

interface MobileWorkoutViewProps {
  workout: Workout;
  onToggleExercise: (name: string) => void;
  onCompleteWorkout: () => void;
  onStartGuided: () => void;
  isCompleting: boolean;
}

type SectionKey = "warm_up" | "technical_work" | "conditioning" | "cool_down";

const SECTIONS: { key: SectionKey; label: string }[] = [
  { key: "warm_up", label: "Riscaldamento" },
  { key: "technical_work", label: "Tecnica" },
  { key: "conditioning", label: "Metcon" },
  { key: "cool_down", label: "Defaticamento" },
];

export function MobileWorkoutView({
  workout,
  onToggleExercise,
  onCompleteWorkout,
  onStartGuided,
  isCompleting,
}: MobileWorkoutViewProps) {
  const [activeSectionIndex, setActiveSectionIndex] = useState(0);
  const [showTimer, setShowTimer] = useState(false);
  const activeSection = SECTIONS[activeSectionIndex];
  const exercises = workout[activeSection.key];

  const MAX_VISIBLE_EXERCISES = 6;
  const visibleExercises = exercises.slice(0, MAX_VISIBLE_EXERCISES);
  const isTruncated = exercises.length > MAX_VISIBLE_EXERCISES;

  const handleSectionChange = (index: number) => {
    hapticFeedback.selection();
    setActiveSectionIndex(index);
  };

  const handleToggle = (name: string) => {
    // Haptics handled by parent
    onToggleExercise(name);
  };

  const handleComplete = () => {
    hapticFeedback.notification("success");
    onCompleteWorkout();
  };

  const nextSection = () => {
    if (activeSectionIndex < SECTIONS.length - 1) {
      handleSectionChange(activeSectionIndex + 1);
    }
  };

  const prevSection = () => {
    if (activeSectionIndex > 0) {
      handleSectionChange(activeSectionIndex - 1);
    }
  };

  const progress = calculateProgress(workout);

  // Show CrossFitTimer fullscreen when active
  if (showTimer) {
    return (
      <div className="fixed inset-0 z-50 bg-background p-4 safe-area-top safe-area-bottom">
        <button
          onClick={() => setShowTimer(false)}
          className="absolute top-4 right-4 p-2 rounded-full bg-secondary z-10"
        >
          ✕
        </button>
        <CrossFitTimer
          initialMode="amrap"
          onComplete={(mode, duration, rounds) => {
            hapticFeedback.notification("success");
            setShowTimer(false);
          }}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden safe-area-bottom">
      {/* Progress Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur z-20 border-b p-4 safe-area-top shadow-sm">
        <div className="flex justify-between items-center mb-3">
          <div className="flex flex-col">
            <h2 className="font-bold text-lg">{workout.name}</h2>
            <span className="text-xs text-muted-foreground">
              {progress.completed}/{progress.total} Esercizi • {progress.percentage}%
            </span>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => {
                hapticFeedback.impact("medium");
                setShowTimer(true);
              }}
              className={cn(
                "flex items-center gap-2 bg-orange-500 text-white px-3 py-2 rounded-full text-sm font-bold shadow-md active:scale-95 transition-transform",
                touchTarget.manipulation
              )}
            >
              <Timer className="h-4 w-4" />
              Timer
            </button>
            <button
              onClick={onStartGuided}
              className={cn(
                "flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-full text-sm font-bold shadow-md active:scale-95 transition-transform",
                touchTarget.manipulation
              )}
            >
              <Play className="h-4 w-4 fill-current" />
              Avvia
            </button>
          </div>
        </div>
        <div className="h-2 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-500 ease-out"
            style={{ width: `${progress.percentage}%` }}
          />
        </div>
      </div>

      {/* Section Tabs */}
      <div className="flex overflow-x-auto py-4 px-4 gap-3 no-scrollbar scroll-snap-x">
        {SECTIONS.map((section, index) => {
          const isActive = index === activeSectionIndex;
          const count = workout[section.key].length;
          const completed = workout[section.key].filter((e) => e.completed).length;

          if (count === 0) return null;

          return (
            <button
              key={section.key}
              onClick={() => handleSectionChange(index)}
              className={cn(
                "flex-shrink-0 px-5 py-3 rounded-xl text-sm font-semibold transition-all whitespace-nowrap scroll-snap-align-start",
                touchTarget.manipulation,
                isActive
                  ? "bg-primary text-primary-foreground shadow-lg scale-105 ring-2 ring-primary/20"
                  : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
              )}
            >
              {section.label} ({completed}/{count})
            </button>
          );
        })}
      </div>

      {/* Navigation Arrows (Mobile Helper) */}
      <div className="flex justify-between px-4 mb-2">
        <button
          onClick={prevSection}
          disabled={activeSectionIndex === 0}
          className={cn(
            touchTarget.icon.sm,
            "text-muted-foreground disabled:opacity-20 transition-opacity p-2"
          )}
          aria-label="Sezione precedente"
        >
          <ChevronLeft className="h-6 w-6" />
        </button>
        <button
          onClick={nextSection}
          disabled={activeSectionIndex === SECTIONS.length - 1}
          className={cn(
            touchTarget.icon.sm,
            "text-muted-foreground disabled:opacity-20 transition-opacity p-2"
          )}
          aria-label="Sezione successiva"
        >
          <ChevronRight className="h-6 w-6" />
        </button>
      </div>

      {/* Exercises List */}
      <div className="flex-1 overflow-hidden px-4 space-y-4 pb-4">
        <AnimatePresence mode="wait">
          {exercises && exercises.length > 0 ? (
            <motion.div
              key={activeSection.key}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="space-y-4"
            >
              {isTruncated && (
                <div className="text-[11px] text-muted-foreground/70 bg-secondary/40 border border-border/40 rounded-xl px-3 py-2">
                  Sezione lunga: mostro i primi {MAX_VISIBLE_EXERCISES} esercizi (NO SCROLL attivo).
                </div>
              )}

              {visibleExercises.map((exercise, index) => (
                <ExerciseItem
                  key={`${activeSection.key}-${exercise.name}-${index}`}
                  exercise={exercise}
                  onToggle={() => handleToggle(exercise.name)}
                />
              ))}
            </motion.div>
          ) : (
            <div className="text-center py-12 text-muted-foreground text-base">
              Nessun esercizio in questa sezione
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Complete Workout Button */}
      {progress.percentage === 100 && (
        <div className="fixed bottom-20 left-0 right-0 p-4 flex justify-center pointer-events-none z-30">
          <motion.button
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={handleComplete}
            disabled={isCompleting}
            className={cn(
              "pointer-events-auto w-full max-w-md py-4 bg-green-600 text-white rounded-2xl font-bold text-lg",
              "hover:bg-green-700 active:scale-95 transition-all shadow-xl ring-4 ring-green-600/30",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "flex items-center justify-center gap-3",
              touchTarget.manipulation
            )}
          >
            <CheckCircle2 className="h-6 w-6" />
            {isCompleting ? "Completamento..." : "TERMINA WORKOUT"}
          </motion.button>
        </div>
      )}
    </div>
  );
}

function ExerciseItem({
  exercise,
  onToggle,
}: {
  exercise: Workout['warm_up'][number];
  onToggle: () => void;
}) {
  return (
    <SwipeableCard
      onSwipeRight={onToggle}
      className={cn(
        "p-4 rounded-2xl border transition-all duration-200 shadow-sm",
        touchTarget.manipulation,
        exercise.completed
          ? "bg-muted/50 border-transparent opacity-70"
          : "bg-card border-border hover:border-primary/30"
      )}
    >
      <div className="flex items-start gap-4">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggle();
          }}
          className={cn(
            touchTarget.icon.md,
            "flex-shrink-0 rounded-full transition-all active:scale-90"
          )}
          aria-label={exercise.completed ? "Segna come non completato" : "Segna come completato"}
        >
          {exercise.completed ? (
            <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400 fill-green-100 dark:fill-green-900/30" />
          ) : (
            <Circle className="h-8 w-8 text-muted-foreground hover:text-primary" />
          )}
        </button>

        <div className="flex-1 min-w-0 pt-0.5" onClick={onToggle}>
          <h3 className={cn(
            "font-bold text-base leading-snug mb-1.5",
            exercise.completed && "line-through text-muted-foreground"
          )}>
            {exercise.name}
          </h3>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
            {exercise.sets && (
              <span className="font-medium text-foreground/80">{exercise.sets} serie</span>
            )}
            {exercise.reps && (
              <span className="font-medium">{exercise.reps} reps</span>
            )}
            {exercise.rest_seconds && (
              <span className="flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" />
                {exercise.rest_seconds}s
              </span>
            )}
          </div>
        </div>
      </div>
    </SwipeableCard>
  );
}

function calculateProgress(workout: Workout) {
  const allExercises = [
    ...workout.warm_up,
    ...workout.technical_work,
    ...workout.conditioning,
    ...workout.cool_down,
  ];
  const total = allExercises.length;
  const completed = allExercises.filter((e) => e.completed).length;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  return { total, completed, percentage };
}
