import { createLazyFileRoute, Link } from "@tanstack/react-router";
import { MessageSquare, Dumbbell, BookOpen, FileText, Play, ChevronRight, RefreshCw } from "lucide-react";
import { HubLayout } from "../features/layout/HubLayout";
import { ChatInterface } from "../features/chat/ChatInterface";
import { ExercisesBrowser } from "../features/exercises/ExercisesBrowser";
import { useState, useEffect, useCallback } from "react";
import type { CoachWeeklyPlan } from "../types/plans";
import { plansApi } from "../lib/api/plans";
import { cn } from "../lib/utils";
import { logger } from "../lib/logger";
import { toast } from "../components/ui/Toast";
import { DAY_NAMES } from "../shared/utils/date-constants";

export const Route = createLazyFileRoute("/coach")({
  component: CoachHub,
});

// ============================================================================
// MY PROGRAMS TAB - Schede settimanali generate
// ============================================================================

function MyProgramsTab() {
  const [currentPlan, setCurrentPlan] = useState<CoachWeeklyPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const MAX_VISIBLE_SESSIONS = 4;

  const loadCurrentPlan = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await plansApi.getCurrentCoachPlan();
      setCurrentPlan(response.plan);
    } catch (error) {
      logger.error("Error loading coach plan", { error });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCurrentPlan();
  }, [loadCurrentPlan]);

  useEffect(() => {
    const handleFocus = () => {
      loadCurrentPlan();
    };
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        loadCurrentPlan();
      }
    };

    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [loadCurrentPlan]);

  const handleGeneratePlan = async () => {
    try {
      setIsGenerating(true);
      await plansApi.generateCoachPlan({ days_available: 4 });
      await loadCurrentPlan();
    } catch (error) {
      logger.error("Error generating plan", { error });
      toast.error({ title: "Errore", description: "Impossibile generare il piano" });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      {/* Current Week Plan */}
      <div className="bg-card border rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-lg">Piano Settimana Corrente</h3>
            <p className="text-sm text-muted-foreground">
              {currentPlan ? `Settimana ${currentPlan.weekNumber} - ${currentPlan.focus}` : "Nessun piano"}
            </p>
          </div>
          <Link
            to="/progress"
            className="text-sm text-primary font-medium flex items-center gap-1"
          >
            Storico <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {isLoading ? (
          <div className="animate-pulse space-y-2">
            {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-12 bg-muted rounded-lg" />)}
          </div>
        ) : currentPlan ? (
          <>
            {/* Progress bar */}
            <div className="mb-4">
              <div className="flex justify-between text-xs text-muted-foreground mb-1">
                <span>Progresso</span>
                <span>{currentPlan.completedSessions}/{currentPlan.totalSessions} sessioni</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all"
                  style={{
                    width: `${currentPlan.totalSessions > 0 ? (currentPlan.completedSessions / currentPlan.totalSessions) * 100 : 0}%`,
                  }}
                />
              </div>
            </div>

            <div className="space-y-2">
              {currentPlan.sessions.slice(0, MAX_VISIBLE_SESSIONS).map((session, i) => (
                <div
                  key={i}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg border",
                    session.completed ? "bg-green-500/10 border-green-500/30" : "bg-secondary/30"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-medium text-muted-foreground w-20">
                      {DAY_NAMES[session.dayOfWeek] || session.dayOfWeek}
                    </span>
                    <span className="font-medium">{session.name}</span>
                    {session.duration > 0 && (
                      <span className="text-xs text-muted-foreground">{session.duration} min</span>
                    )}
                  </div>
                  {session.type !== "rest" && (
                    session.completed ? (
                      <span className="text-xs text-green-600 font-medium">✓ Completato</span>
                    ) : (
                      <Link
                        to="/workout"
                        search={{ coachPlanId: currentPlan.id, coachSessionIndex: i }}
                        className="flex items-center gap-1 text-xs bg-primary text-primary-foreground px-3 py-1.5 rounded-lg font-medium"
                      >
                        <Play className="w-3 h-3" /> Inizia
                      </Link>
                    )
                  )}
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <Dumbbell className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
            <p className="text-muted-foreground mb-3">Nessun piano attivo</p>
            <button
              onClick={handleGeneratePlan}
              disabled={isGenerating}
              className="flex items-center gap-2 mx-auto px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50"
            >
              {isGenerating ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {isGenerating ? "Generazione..." : "Genera Piano"}
            </button>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          to="/workout"
          className="flex flex-col items-center justify-center gap-2 p-4 rounded-xl bg-primary text-primary-foreground"
        >
          <Play className="w-6 h-6" />
          <span className="font-semibold text-sm">Inizia Workout</span>
        </Link>
        <Link
          to="/progress"
          className="flex flex-col items-center justify-center gap-2 p-4 rounded-xl bg-secondary border"
        >
          <FileText className="w-6 h-6" />
          <span className="font-semibold text-sm">Vedi Storico</span>
        </Link>
      </div>
    </div>
  );
}

// ============================================================================
// EXERCISES TAB
// ============================================================================

function ExercisesTab() {
  return (
    <div className="p-4">
      <ExercisesBrowser />
    </div>
  );
}

// ============================================================================
// MAIN HUB
// ============================================================================

function CoachHub() {
  return (
    <HubLayout
      tabs={[
        {
          id: "chat",
          label: "AI Coach",
          icon: MessageSquare,
          component: () => <ChatInterface mode="workout" />,
        },
        {
          id: "programs",
          label: "Le Mie Schede",
          icon: FileText,
          component: MyProgramsTab,
        },
        {
          id: "exercises",
          label: "Esercizi",
          icon: BookOpen,
          component: ExercisesTab,
        },
      ]}
    />
  );
}
