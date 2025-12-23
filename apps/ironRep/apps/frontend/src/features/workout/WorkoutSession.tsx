import { useState, useEffect, useCallback } from "react";
import { Pause, AlertCircle, ChevronRight, ChevronLeft, X, Timer } from "lucide-react";
import { ExerciseCard } from "./ExerciseCard";
import { WorkoutSummary } from "./WorkoutSummary";
import { PainCheckModal } from "./PainCheckModal";
import { hapticFeedback } from "../../lib/haptics";
import { type Workout, type WorkoutCompletionSummary, type Exercise } from "../../lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "../../lib/utils";
import { touchTarget } from "../../lib/touch-targets";
import { HighPainAlert } from "./HighPainAlert";

/** Extended exercise type with section info for workout flow */
type SessionExercise = Exercise & { section: string };

interface WorkoutSessionProps {
  workout: Workout;
  onComplete: (summary: WorkoutCompletionSummary) => void;
  onExit: () => void;
}

export function WorkoutSession({
  workout,
  onComplete,
  onExit,
}: WorkoutSessionProps) {
  // Flatten exercises for sequential flow
  // This assumes the user wants to do them in order.
  // A more advanced version would handle sections, but flattening is standard for "Play" mode.
  const [allExercises] = useState<SessionExercise[]>(() => [
    ...workout.warm_up.map(e => ({ ...e, section: 'Riscaldamento' })),
    ...workout.technical_work.map(e => ({ ...e, section: 'Tecnica' })),
    ...workout.conditioning.map(e => ({ ...e, section: 'Conditioning' })),
    ...workout.cool_down.map(e => ({ ...e, section: 'Cool Down' })),
  ]);

  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [completedExercises, setCompletedExercises] = useState<Set<number>>(new Set());
  const [isResting, setIsResting] = useState(false);
  const [restTimeLeft, setRestTimeLeft] = useState(0);
  const [startTime] = useState(Date.now());
  const [showPainCheck, setShowPainCheck] = useState(false);
  const [painChecks, setPainChecks] = useState<Array<{ pain_level: number; timestamp: string; location?: string }>>([]);
  const [showSummary, setShowSummary] = useState(false);
  const [workoutNotes, setWorkoutNotes] = useState("");
  const [showExitDialog, setShowExitDialog] = useState(false);
  const [showHighPainAlert, setShowHighPainAlert] = useState(false);

  const currentExercise = allExercises[currentExerciseIndex];
  const progress = ((currentExerciseIndex + 1) / allExercises.length) * 100;

  // Rest timer
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isResting && restTimeLeft > 0) {
      timer = setInterval(() => {
        setRestTimeLeft((prev) => {
          if (prev <= 1) {
            hapticFeedback.notification("success"); // Vibrate when done
            setIsResting(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isResting, restTimeLeft]);

  const handleExerciseComplete = useCallback(() => {
    hapticFeedback.notification("success");

    const newCompleted = new Set(completedExercises);
    newCompleted.add(currentExerciseIndex);
    setCompletedExercises(newCompleted);

    // Logic for Pain Check (every 3 exercises or 15 mins - simplified to every 3 here)
    if (newCompleted.size % 3 === 0 && newCompleted.size < allExercises.length) {
      setShowPainCheck(true);
    } else {
      proceedToNextStep();
    }
  }, [completedExercises, currentExerciseIndex, allExercises.length]);

  const proceedToNextStep = () => {
    // Check for rest
    const restTime = currentExercise.rest_seconds || 0;
    if (restTime > 0) {
      setRestTimeLeft(restTime);
      setIsResting(true);
    }

    if (currentExerciseIndex < allExercises.length - 1) {
      // Delay index change if resting? No, show next exercise immediately but with rest overlay
      if (restTime === 0) {
        setCurrentExerciseIndex(prev => prev + 1);
      }
    } else {
      handleWorkoutComplete();
    }
  };

  const handleRestComplete = () => {
    setIsResting(false);
    if (currentExerciseIndex < allExercises.length - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
    } else {
      handleWorkoutComplete();
    }
  };

  const handlePainCheckSubmit = (painLevel: number) => {
    hapticFeedback.selection();
    setPainChecks(prev => [
      ...prev,
      {
        pain_level: painLevel,
        timestamp: new Date().toISOString(),
        location: "General Check" // Could be specific
      }
    ]);
    setShowPainCheck(false);

    // Safety check
    if (painLevel >= 7) {
      hapticFeedback.notification("warning");
      setShowHighPainAlert(true);
      // Don't proceed yet
    } else {
      proceedToNextStep();
    }
  };

  const handleWorkoutComplete = () => {
    hapticFeedback.notification("success");
    setShowSummary(true);
  };

  const handleFinalSubmit = (data: { notes?: string }) => { // Data from Summary component
    const duration = Math.round((Date.now() - startTime) / 60000);
    const summary: WorkoutCompletionSummary = {
      workout_id: workout.id,
      total_duration_minutes: duration,
      exercises_completed: completedExercises.size,
      total_exercises: allExercises.length,
      pain_checks: painChecks,
      notes: workoutNotes || data.notes, // Merge notes
    };
    onComplete(summary);
  };

  if (showSummary) {
    return (
      <WorkoutSummary
        summary={{
          workout_id: workout.id,
          workout_name: workout.name,
          duration_minutes: Math.round((Date.now() - startTime) / 60000),
          exercises_completed: completedExercises.size,
          total_exercises: allExercises.length,
          pain_checks: painChecks.map(p => ({ exercise: "Check", pain_level: p.pain_level })), // Adapter
          notes: workoutNotes,
        }}
        onClose={onExit} // Or handle completion
        onConfirm={handleFinalSubmit} // Assuming WorkoutSummary has this
      />
    );
  }

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden">
      {/* Mobile Header - Touch optimized */}
      <header className="sticky top-0 z-20 px-4 py-3 flex items-center justify-between bg-background/95 backdrop-blur-sm border-b safe-area-top">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <button
            onClick={() => setShowExitDialog(true)}
            className="p-3 -ml-1 rounded-xl transition-colors touch-manipulation min-h-[44px] min-w-[44px] flex items-center justify-center active:bg-accent"
            aria-label="Esci dal workout"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex-1 min-w-0">
            <h1 className="font-bold text-lg truncate">{workout.name}</h1>
            <p className="text-sm text-muted-foreground truncate">
              {currentExercise.section} • {currentExerciseIndex + 1}/{allExercises.length}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm font-mono font-semibold bg-primary/10 text-primary px-3 py-2 rounded-xl">
          <Timer className="w-4 h-4" />
          <span className="tabular-nums">
            {Math.floor((Date.now() - startTime) / 60000)}:
            {String(Math.floor(((Date.now() - startTime) / 1000) % 60)).padStart(2, '0')}
          </span>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="h-1 bg-secondary/50">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      </div>

      {/* Main Content - Mobile optimized */}
      <main className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={currentExerciseIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="p-4 space-y-6"
          >
            <ExerciseCard
              exercise={currentExercise}
              exerciseNumber={currentExerciseIndex + 1}
              totalExercises={allExercises.length}
              isCompleted={completedExercises.has(currentExerciseIndex)}
              onComplete={handleExerciseComplete}
            />

            {/* Notes Section */}
            <div className="hidden lg:block">
              <label className="text-base font-medium mb-3 block">Note Rapide</label>
              <textarea
                value={workoutNotes}
                onChange={(e) => setWorkoutNotes(e.target.value)}
                placeholder="Sensazioni, peso usato, difficoltà..."
                className="w-full min-h-[120px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all resize-none"
              />
            </div>
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Navigation - Sticky bottom */}
      <div className="sticky bottom-0 bg-background/95 backdrop-blur-sm border-t p-4 safe-area-bottom">
        <div className="flex gap-3">
          <button
            onClick={() => {
              if (currentExerciseIndex > 0) setCurrentExerciseIndex(p => p - 1);
            }}
            disabled={currentExerciseIndex === 0}
            className="flex-1 h-12 flex items-center justify-center gap-2 bg-secondary text-secondary-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation disabled:opacity-30 disabled:pointer-events-none"
          >
            <ChevronLeft className="w-4 h-4" />
            Precedente
          </button>

          <button
            onClick={() => {
              if (currentExerciseIndex < allExercises.length - 1) setCurrentExerciseIndex(p => p + 1);
            }}
            disabled={currentExerciseIndex === allExercises.length - 1}
            className="flex-1 h-12 flex items-center justify-center gap-2 bg-secondary text-secondary-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation disabled:opacity-30 disabled:pointer-events-none"
          >
            Successivo
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Rest Overlay */}
      <AnimatePresence>
        {isResting && (
          <motion.div
            initial={{ opacity: 0, y: "100%" }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: "100%" }}
            className="absolute inset-0 z-50 bg-background/95 backdrop-blur-xl flex flex-col items-center justify-center p-8 text-center"
          >
            <h2 className="text-3xl font-bold mb-8">Riposo</h2>

            <div className="relative w-48 h-48 mb-8 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" className="stroke-secondary fill-none" strokeWidth="8" />
                <motion.circle
                  cx="50" cy="50" r="45"
                  className="stroke-primary fill-none"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray="283"
                  initial={{ strokeDashoffset: 0 }}
                  animate={{ strokeDashoffset: 283 }}
                  transition={{ duration: currentExercise.rest_seconds, ease: "linear" }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-6xl font-bold tabular-nums tracking-tight">{restTimeLeft}</span>
              </div>
            </div>

            <p className="text-muted-foreground mb-8 text-lg">
              Prossimo: <span className="text-foreground font-semibold">{allExercises[currentExerciseIndex + 1]?.name}</span>
            </p>

            <button
              onClick={handleRestComplete}
              className="w-full h-14 bg-primary text-primary-foreground rounded-2xl font-bold text-lg shadow-lg transition-transform active:scale-[0.98] touch-manipulation"
            >
              Salta Riposo
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pain Check Overlay */}
      <AnimatePresence>
        {showPainCheck && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          >
            <PainCheckModal
              onSubmit={handlePainCheckSubmit}
              onSkip={() => {
                setShowPainCheck(false);
                proceedToNextStep();
              }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Exit Dialog */}
      <AnimatePresence>
        {showExitDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-card w-full max-w-sm rounded-2xl p-6 shadow-2xl border"
            >
              <h3 className="text-xl font-bold mb-2">Uscire dal workout?</h3>
              <p className="text-base text-muted-foreground mb-6">
                I progressi correnti verranno salvati, ma il workout risulterà incompleto.
              </p>
              <div className="space-y-3">
                <button
                  onClick={() => {
                    handleWorkoutComplete();
                  }}
                  className="w-full h-12 bg-destructive text-destructive-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation"
                >
                  Esci e Salva
                </button>
                <button
                  onClick={() => setShowExitDialog(false)}
                  className="w-full h-12 bg-secondary text-secondary-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation"
                >
                  Continua Workout
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* High Pain Alert */}
      <HighPainAlert
        open={showHighPainAlert}
        onContinue={() => {
          setShowHighPainAlert(false);
          proceedToNextStep();
        }}
        onStop={() => {
          setShowHighPainAlert(false);
          handleWorkoutComplete();
        }}
      />
    </div >
  );
}
