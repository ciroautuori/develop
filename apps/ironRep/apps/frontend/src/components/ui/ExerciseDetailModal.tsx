import { X, Play, AlertTriangle, Target, Dumbbell } from "lucide-react";
import type { ExerciseDetail } from "../../lib/api";
import { hapticFeedback } from "../../lib/haptics";

interface ExerciseDetailModalProps {
  exercise: ExerciseDetail | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ExerciseDetailModal({
  exercise,
  isOpen,
  onClose,
}: ExerciseDetailModalProps) {
  if (!isOpen || !exercise) return null;

  const MAX_ITEMS = 5;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-background rounded-lg shadow-xl max-w-2xl w-full overflow-hidden">
        {/* Header */}
        <div className="sticky top-0 bg-background border-b p-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold">{exercise.name}</h2>
          <button
            onClick={() => {
              hapticFeedback.selection();
              onClose();
            }}
            className="p-2 hover:bg-muted rounded-lg transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-hidden">
          {/* Video */}
          {exercise.video_url && (
            <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
              <Play size={48} className="text-muted-foreground" />
              <p className="ml-2 text-sm text-muted-foreground">
                Video: {exercise.video_url}
              </p>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Categoria</p>
              <p className="font-medium">{exercise.category}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Fase</p>
              <p className="font-medium capitalize">{exercise.phase}</p>
            </div>
            {exercise.difficulty_level && (
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Difficoltà</p>
                <p className="font-medium capitalize">
                  {exercise.difficulty_level}
                </p>
              </div>
            )}
            {exercise.estimated_duration_minutes && (
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Durata</p>
                <p className="font-medium">
                  {exercise.estimated_duration_minutes} min
                </p>
              </div>
            )}
          </div>

          {/* Description */}
          {exercise.description && (
            <div className="space-y-2">
              <h3 className="font-semibold text-lg">Descrizione</h3>
              <p className="text-muted-foreground">{exercise.description}</p>
            </div>
          )}

          {/* Equipment */}
          {exercise.equipment && exercise.equipment.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Dumbbell size={20} />
                <h3 className="font-semibold text-lg">Attrezzatura</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {exercise.equipment.map((item, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-muted rounded-full text-sm"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Target Muscles */}
          {exercise.target_muscles && exercise.target_muscles.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Target size={20} />
                <h3 className="font-semibold text-lg">Muscoli Target</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {exercise.target_muscles.map((muscle, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium"
                  >
                    {muscle}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Instructions */}
          {exercise.instructions && exercise.instructions.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold text-lg">Istruzioni</h3>
              <ol className="list-decimal list-inside space-y-2">
                {exercise.instructions.slice(0, MAX_ITEMS).map((instruction, i) => (
                  <li key={i} className="text-muted-foreground">
                    {instruction}
                  </li>
                ))}
              </ol>
              {exercise.instructions.length > MAX_ITEMS && (
                <p className="text-xs text-muted-foreground/70">
                  Lista lunga: mostro i primi {MAX_ITEMS} elementi (NO SCROLL attivo).
                </p>
              )}
            </div>
          )}

          {/* Coaching Cues */}
          {exercise.coaching_cues && exercise.coaching_cues.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold text-lg">Coaching Cues</h3>
              <ul className="space-y-2">
                {exercise.coaching_cues.slice(0, MAX_ITEMS).map((cue, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-muted-foreground"
                  >
                    <span className="text-primary mt-1">•</span>
                    <span>{cue}</span>
                  </li>
                ))}
              </ul>
              {exercise.coaching_cues.length > MAX_ITEMS && (
                <p className="text-xs text-muted-foreground/70">
                  Lista lunga: mostro i primi {MAX_ITEMS} elementi (NO SCROLL attivo).
                </p>
              )}
            </div>
          )}

          {/* Contraindications */}
          {exercise.contraindications &&
            exercise.contraindications.length > 0 && (
              <div className="space-y-2 bg-destructive/10 border border-destructive/20 rounded-lg p-4">
                <div className="flex items-center gap-2 text-destructive">
                  <AlertTriangle size={20} />
                  <h3 className="font-semibold text-lg">Controindicazioni</h3>
                </div>
                <ul className="space-y-1">
                  {exercise.contraindications.map((contra, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-destructive"
                    >
                      <span className="mt-1">⚠️</span>
                      <span className="text-sm">{contra}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-background border-t p-4">
          <button
            onClick={() => {
              hapticFeedback.selection();
              onClose();
            }}
            className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-semibold hover:bg-primary/90 transition-colors"
          >
            Chiudi
          </button>
        </div>
      </div>
    </div>
  );
}
