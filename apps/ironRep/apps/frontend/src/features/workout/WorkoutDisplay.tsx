import { useState, Suspense } from "react";
import { CheckCircle2, Circle, Clock, Play, AlertCircle } from "lucide-react";
import { cn } from "../../lib/utils";
import { useNavigate } from "@tanstack/react-router";
import { useIsMobile } from "../../hooks/useMediaQuery";
import { MobileWorkoutView } from "./MobileWorkoutView";
import { WorkoutSession } from "./WorkoutSession";
import { type WorkoutCompletionSummary } from "../../lib/api";
import { hapticFeedback } from "../../lib/haptics";
import { useWorkout } from "./hooks/useWorkout";
import { WorkoutSkeleton } from "../../components/ui/Skeletons";
import { motion } from "framer-motion";

export function WorkoutDisplay() {
  return (
    <Suspense fallback={<WorkoutSkeleton />}>
      <WorkoutDisplayContent />
    </Suspense>
  );
}

function WorkoutDisplayContent() {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const { workout, toggleExercise, completeWorkout } = useWorkout();
  const [isCompleting, setIsCompleting] = useState(false);
  const [isInSession, setIsInSession] = useState(false);

  const handleToggleExercise = (exerciseName: string) => {
    hapticFeedback.selection();
    toggleExercise(exerciseName);
  };

  const handleCompleteWorkout = async () => {
    hapticFeedback.notification("success");
    setIsCompleting(true);
    try {
      await completeWorkout({ painImpact: 3, notes: "Completed via app checklist" });
      navigate({ to: "/progress" });
    } catch (err) {
      // Error handled by hook/logger
    } finally {
      setIsCompleting(false);
    }
  };

  const handleWorkoutSessionComplete = async (summary: WorkoutCompletionSummary) => {
    hapticFeedback.notification("success");
    try {
      const painImpact = summary.pain_checks.length > 0
        ? Math.round(
          summary.pain_checks.reduce((sum, check) => sum + check.pain_level, 0) /
          summary.pain_checks.length
        )
        : 3;

      await completeWorkout({
        painImpact,
        notes: summary.notes || "Completed via guided session"
      });
      navigate({ to: "/progress" });
    } catch (err) {
      // Error handled by hook
    }
  };

  // If in guided session mode, show WorkoutSession component
  if (isInSession) {
    return (
      <WorkoutSession
        workout={workout}
        onComplete={handleWorkoutSessionComplete}
        onExit={() => setIsInSession(false)}
      />
    );
  }

  // Mobile View
  if (isMobile) {
    return (
      <MobileWorkoutView
        workout={workout}
        onToggleExercise={handleToggleExercise}
        onCompleteWorkout={handleCompleteWorkout}
        onStartGuided={() => setIsInSession(true)}
        isCompleting={isCompleting}
      />
    );
  }

  // Desktop View
  const allExercises = [
    ...workout.warm_up,
    ...workout.technical_work,
    ...workout.conditioning,
    ...workout.cool_down,
  ];

  const completedCount = allExercises.filter((ex) => ex.completed).length;
  const totalCount = allExercises.length;
  const progress = Math.round((completedCount / totalCount) * 100);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6 pb-20"
    >
      <div className="flex items-center justify-between sticky top-0 bg-background/95 backdrop-blur z-10 py-3 border-b">
        <div>
          <h2 className="text-xl font-bold">Allenamento di Oggi</h2>
          <div className="text-xs text-muted-foreground">
            {completedCount}/{totalCount} completati ({progress}%)
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              hapticFeedback.impact("medium");
              setIsInSession(true);
            }}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-full font-semibold shadow-lg hover:bg-primary/90 transition-colors flex items-center gap-2 active:scale-95"
          >
            <Play size={16} />
            Inizia Guidato
          </button>
          {progress === 100 && !workout.completed && (
            <button
              onClick={handleCompleteWorkout}
              disabled={isCompleting}
              className="bg-green-600 text-white px-4 py-2 rounded-full font-semibold shadow-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {isCompleting ? "..." : "Termina"}
            </button>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3">
        {allExercises.map((exercise, index) => (
          <div
            key={index}
            onClick={() => handleToggleExercise(exercise.name)}
            className={cn(
              "bg-card border rounded-lg p-4 shadow-sm transition-all hover:shadow-md cursor-pointer active:scale-[0.98]",
              exercise.completed
                ? "border-primary/50 bg-primary/5"
                : "border-border"
            )}
          >
            <div className="flex justify-between items-start mb-4">
              <h3
                className={cn(
                  "font-semibold text-lg",
                  exercise.completed && "line-through text-muted-foreground"
                )}
              >
                {exercise.name}
              </h3>
              <div
                className={cn(
                  "text-muted-foreground transition-colors",
                  exercise.completed && "text-primary"
                )}
              >
                {exercise.completed ? (
                  <CheckCircle2 size={24} />
                ) : (
                  <Circle size={24} />
                )}
              </div>
            </div>

            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="font-medium text-foreground">Serie:</span>
                {exercise.sets}
              </div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-foreground">Ripetizioni:</span>
                {exercise.reps}
              </div>
              <div className="flex items-center gap-2">
                <Clock size={16} />
                {exercise.rest_seconds}s recupero
              </div>
              {exercise.notes && (
                <div className="bg-muted/50 p-2 rounded text-xs italic">
                  "{exercise.notes}"
                </div>
              )}
            </div>

            <div
              className="mt-4 pt-4 border-t border-border flex justify-end"
              onClick={(e) => e.stopPropagation()}
            >
              {exercise.video_url && (
                <a
                  href={exercise.video_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary text-sm font-medium flex items-center gap-1 hover:underline"
                >
                  <Play size={14} /> Guarda Video
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
