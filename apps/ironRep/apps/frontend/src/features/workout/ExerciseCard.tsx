import { Check, AlertTriangle, Play, Info } from "lucide-react";
import { useState } from "react";
import { OptimizedImage } from "../../components/ui/OptimizedImage";
import { touchTarget } from "../../lib/touch-targets";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

interface Exercise {
  id: string;
  name: string;
  category: string;
  sets: number;
  reps: string;
  rest_seconds: number;
  tempo: string;
  coaching_cues: string[];
  injury_modifications?: string;
  video_url?: string;
  image_url?: string;
}

interface ExerciseCardProps {
  exercise: Exercise;
  exerciseNumber: number;
  totalExercises: number;
  isCompleted: boolean;
  onComplete: () => void;
}

export function ExerciseCard({
  exercise,
  exerciseNumber,
  totalExercises,
  isCompleted,
  onComplete,
}: ExerciseCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [currentSet, setCurrentSet] = useState(1);

  const handleSetComplete = () => {
    hapticFeedback.impact("medium");

    if (currentSet < exercise.sets) {
      setCurrentSet(currentSet + 1);
    } else {
      onComplete();
    }
  };

  const handleDetailsToggle = () => {
    hapticFeedback.selection();
    setShowDetails(!showDetails);
  };

  return (
    <div className="bg-card rounded-xl shadow-lg overflow-hidden border border-border">
      {/* Exercise Header */}
      <div className="bg-primary/10 p-5 border-b">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-muted-foreground">
                Esercizio {exerciseNumber}/{totalExercises}
              </span>
              {isCompleted && (
                <span className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400 font-medium">
                  <Check className="h-4 w-4" />
                  Completato
                </span>
              )}
            </div>
            <h2 className="text-2xl md:text-3xl font-bold mb-1 leading-tight">{exercise.name}</h2>
            <p className="text-base text-muted-foreground">{exercise.category}</p>
          </div>
        </div>
      </div>

      {/* Exercise Media */}
      {exercise.video_url || exercise.image_url ? (
        <div className="relative aspect-video bg-secondary">
          {exercise.video_url ? (
            <video
              src={exercise.video_url}
              controls
              className="w-full h-full object-cover"
              poster={exercise.image_url}
              playsInline
            >
              Il tuo browser non supporta i video.
            </video>
          ) : exercise.image_url ? (
            <OptimizedImage
              src={exercise.image_url}
              alt={exercise.name}
              aspectRatio="16/9"
              placeholder="blur"
              sizes="(max-width: 768px) 100vw, 50vw"
            />
          ) : null}
          <div className="absolute bottom-3 right-3">
            <button
              className={cn(
                touchTarget.icon.md,
                "bg-background/90 backdrop-blur rounded-full hover:bg-background shadow-lg"
              )}
              aria-label="Play video"
            >
              <Play className="h-5 w-5" />
            </button>
          </div>
        </div>
      ) : (
        <div className="aspect-video bg-secondary flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <Play className="h-16 w-16 mx-auto mb-3 opacity-50" />
            <p className="text-base">Video non disponibile</p>
          </div>
        </div>
      )}

      {/* Exercise Details */}
      <div className="p-6 space-y-6">
        {/* Sets/Reps/Tempo */}
        <div className="grid grid-cols-3 gap-3 md:gap-4">
          <div className="text-center p-4 md:p-5 bg-secondary/50 rounded-xl">
            <div className="text-4xl md:text-5xl font-bold text-primary mb-1">
              {exercise.sets}
            </div>
            <div className="text-sm md:text-base text-muted-foreground font-medium">Serie</div>
          </div>
          <div className="text-center p-4 md:p-5 bg-secondary/50 rounded-xl">
            <div className="text-4xl md:text-5xl font-bold text-primary mb-1">
              {exercise.reps}
            </div>
            <div className="text-sm md:text-base text-muted-foreground font-medium">Reps</div>
          </div>
          <div className="text-center p-4 md:p-5 bg-secondary/50 rounded-xl">
            <div className="text-4xl md:text-5xl font-bold text-primary mb-1">
              {exercise.tempo}
            </div>
            <div className="text-sm md:text-base text-muted-foreground font-medium">Tempo</div>
          </div>
        </div>

        {/* Current Set Progress */}
        {!isCompleted && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-base">
              <span className="font-semibold">Serie Corrente</span>
              <span className="text-muted-foreground font-medium">
                {currentSet} / {exercise.sets}
              </span>
            </div>
            <div className="h-3 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-500 ease-out"
                style={{ width: `${(currentSet / exercise.sets) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Injury Modifications */}
        {exercise.injury_modifications && (
          <div className="p-4 md:p-5 bg-amber-50 dark:bg-amber-950/20 border-2 border-amber-200 dark:border-amber-800 rounded-xl">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-6 w-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-base text-amber-900 dark:text-amber-100 mb-2">
                  Modifiche per Infortunio
                </h3>
                <p className="text-sm md:text-base text-amber-800 dark:text-amber-200 leading-relaxed">
                  {exercise.injury_modifications}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Coaching Cues */}
        <div>
          <button
            onClick={handleDetailsToggle}
            className={cn(
              touchTarget.button.sm,
              "flex items-center gap-2 text-base font-semibold mb-3 hover:text-primary transition-colors rounded-lg"
            )}
          >
            <Info className="h-5 w-5" />
            Coaching Cues
          </button>
          {showDetails &&
            exercise.coaching_cues &&
            exercise.coaching_cues.length > 0 && (
              <ul className="space-y-3 pl-6">
                {exercise.coaching_cues.map((cue, index) => (
                  <li
                    key={index}
                    className="text-base text-muted-foreground list-disc leading-relaxed"
                  >
                    {cue}
                  </li>
                ))}
              </ul>
            )}
        </div>

        {/* Rest Time Info */}
        {exercise.rest_seconds > 0 && (
          <div className="text-base text-center p-4 bg-secondary/50 rounded-xl font-medium">
            Riposo tra le serie:{" "}
            <span className="font-bold text-primary text-lg">{exercise.rest_seconds}s</span>
          </div>
        )}

        {/* Complete Button */}
        {!isCompleted && (
          <button
            onClick={handleSetComplete}
            className={cn(
              "w-full py-5 bg-primary text-primary-foreground rounded-xl font-bold text-lg hover:bg-primary/90 active:scale-98 transition-all shadow-lg flex items-center justify-center gap-3",
              touchTarget.manipulation
            )}
          >
            {currentSet < exercise.sets ? (
              <>
                <Check className="h-6 w-6" />
                Completa Serie {currentSet}
              </>
            ) : (
              <>
                <Check className="h-6 w-6" />
                Completa Esercizio
              </>
            )}
          </button>
        )}

        {isCompleted && (
          <div className="w-full py-5 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-xl font-bold text-lg text-center flex items-center justify-center gap-3 shadow-md">
            <Check className="h-6 w-6" />
            Esercizio Completato
          </div>
        )}
      </div>
    </div>
  );
}
