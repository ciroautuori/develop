import { createLazyFileRoute, useNavigate } from "@tanstack/react-router";
import { WorkoutDisplay } from "../features/workout/WorkoutDisplay";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { plansApi } from "../lib/api/plans";
import { toast } from "../components/ui/Toast";
import { useEffect, useState } from "react";
import { cn } from "../lib/utils";

export const Route = createLazyFileRoute("/workout")({
  component: WorkoutPage,
});

function WorkoutPage() {
  const navigate = useNavigate();
  const search = Route.useSearch() as unknown as {
    coachPlanId?: unknown;
    coachSessionIndex?: unknown;
  };

  const coachPlanId = typeof search.coachPlanId === "string" ? search.coachPlanId : undefined;
  const coachSessionIndexRaw = search.coachSessionIndex;
  const coachSessionIndexNum =
    typeof coachSessionIndexRaw === "number"
      ? coachSessionIndexRaw
      : typeof coachSessionIndexRaw === "string"
        ? Number(coachSessionIndexRaw)
        : NaN;

  const coachSessionIndex =
    Number.isInteger(coachSessionIndexNum) && coachSessionIndexNum >= 0 ? coachSessionIndexNum : undefined;

  useEffect(() => {
    if (coachPlanId && typeof coachSessionIndex !== "number") {
      navigate({ to: "/coach" });
    }
  }, [coachPlanId, coachSessionIndex, navigate]);

  if (coachPlanId && typeof coachSessionIndex === "number") {
    return <CoachSessionWorkout coachPlanId={coachPlanId} coachSessionIndex={coachSessionIndex} />;
  }

  return <WorkoutDisplay />;
}

function CoachSessionWorkout({
  coachPlanId,
  coachSessionIndex,
}: {
  coachPlanId: string;
  coachSessionIndex: number;
}) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isCompleting, setIsCompleting] = useState(false);
  const [rating, setRating] = useState<number>(5);
  const [notes, setNotes] = useState<string>("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["plans", "coach", "current"],
    queryFn: () => plansApi.getCurrentCoachPlan(),
    retry: false,
  });

  const plan = data?.plan;
  const session = plan?.sessions?.[coachSessionIndex];

  if (isLoading) {
    return <div className="h-full bg-background overflow-hidden p-4" />;
  }

  const handleBackToCoach = () => {
    navigate({ to: "/coach" });
  };

  const handleRefreshAndBack = async () => {
    await queryClient.invalidateQueries({ queryKey: ["plans", "coach", "current"] });
    navigate({ to: "/coach" });
  };

  if (isError || !plan || !session || plan.id !== coachPlanId) {
    const title = !plan
      ? "Nessun piano coach attivo"
      : plan.id !== coachPlanId
        ? "Piano non più corrente"
        : !session
          ? "Sessione non disponibile"
          : "Errore";

    const description = !plan
      ? "Genera una nuova scheda dal Coach."
      : plan.id !== coachPlanId
        ? "La scheda è cambiata (o è stata rigenerata). Torna al Coach e seleziona di nuovo la sessione."
        : !session
          ? "Indice sessione non valido o sessione mancante."
          : "Impossibile caricare la sessione.";

    return (
      <div className="h-full bg-background overflow-hidden p-4">
        <div className="bg-card border rounded-xl p-4">
          <div className="font-semibold">{title}</div>
          <div className="mt-1 text-sm text-muted-foreground">{description}</div>
          <button
            className="mt-4 w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold"
            onClick={handleBackToCoach}
          >
            Torna al Coach
          </button>
          {plan && plan.id !== coachPlanId && (
            <button
              className="mt-2 w-full h-12 rounded-xl bg-secondary border font-semibold"
              onClick={handleRefreshAndBack}
            >
              Aggiorna e torna al Coach
            </button>
          )}
        </div>
      </div>
    );
  }

  const MAX_VISIBLE_EXERCISES = 6;
  const exercises = (session.exercises ?? []).slice(0, MAX_VISIBLE_EXERCISES);

  const handleComplete = async () => {
    try {
      setIsCompleting(true);
      await plansApi.completeWorkoutSession(plan.id, coachSessionIndex, {
        rating,
        notes: notes.trim() ? notes.trim() : undefined,
        exercises: [],
      });
      await queryClient.invalidateQueries({ queryKey: ["plans", "coach", "current"] });
      toast.success({ title: "Sessione completata" });
      navigate({ to: "/coach" });
    } catch {
      toast.error({ title: "Errore", description: "Impossibile completare la sessione" });
    } finally {
      setIsCompleting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden">
      <div className="shrink-0 p-4 border-b">
        <div className="font-bold text-lg truncate">{session.name}</div>
        <div className="text-sm text-muted-foreground truncate">
          {plan.focus} • {session.duration} min
        </div>
      </div>

      <div className="flex-1 overflow-hidden p-4">
        <div className="bg-card border rounded-xl p-4">
          <div className="text-sm font-semibold mb-3">Esercizi</div>
          <div className="space-y-2">
            {exercises.map((ex: any, idx: number) => (
              <div key={idx} className="p-3 rounded-lg bg-secondary/30 border">
                <div className="font-medium text-sm truncate">{ex.name ?? "Esercizio"}</div>
                <div className="text-xs text-muted-foreground truncate">
                  {ex.sets && ex.reps ? `${ex.sets}x${ex.reps}` : ex.duration ?? ""}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="shrink-0 p-4 border-t safe-area-bottom">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="text-sm font-semibold">Valutazione</div>
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => setRating(v)}
                disabled={isCompleting}
                className={cn(
                  "h-9 w-9 rounded-lg border text-sm font-bold",
                  rating >= v ? "bg-primary text-primary-foreground border-primary" : "bg-secondary/30",
                  "disabled:opacity-50"
                )}
                aria-label={`Valutazione ${v}`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
        <input
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={isCompleting}
          placeholder="Note (opzionali)"
          className="mb-3 h-11 w-full rounded-xl border bg-background px-3 text-sm disabled:opacity-50"
          maxLength={120}
        />
        <button
          className={cn(
            "w-full h-12 rounded-xl font-bold",
            "bg-primary text-primary-foreground disabled:opacity-50"
          )}
          disabled={isCompleting || session.type === "rest"}
          onClick={handleComplete}
        >
          {isCompleting ? "Salvataggio..." : "Segna completata"}
        </button>
      </div>
    </div>
  );
}
