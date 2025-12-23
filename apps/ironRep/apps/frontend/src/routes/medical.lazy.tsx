import { createLazyFileRoute, Link } from "@tanstack/react-router";
import { MessageSquare, Activity, Heart, FileText, ChevronRight, Plus, AlertTriangle, RefreshCw, Loader2, Check } from "lucide-react";
import { HubLayout } from "../features/layout/HubLayout";
import { ChatInterface } from "../features/chat/ChatInterface";
import { BodyHeatmap } from "../features/checkin/BodyHeatmap";
import { useState, useEffect, useCallback } from "react";
import { cn } from "../lib/utils";
import { progressApi } from "../lib/api";
import { plansApi, type MedicalProtocol } from "../lib/api/plans";
import { translateRestrictions } from '../lib/medical-utils';
import { logger } from "../lib/logger";
import { hapticFeedback } from "../lib/haptics";
import { toast } from "../components/ui/Toast";

/** Pain statistics from the dashboard API */
interface PainStats {
  avg_pain_30_days: number | null;
  total_assessments: number;
  mobility_score: number | null;
}

export const Route = createLazyFileRoute("/medical")({
  component: MedicalHub,
});

// ============================================================================
// PAIN CHECK-IN TAB
// ============================================================================

function PainCheckInTab() {
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [painLevel, setPainLevel] = useState<number>(0);
  const [stats, setStats] = useState<PainStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await progressApi.getDashboard();
      setStats(data.stats);
    } catch (error) {
      logger.error("Error loading stats", { error });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLocationToggle = (location: string) => {
    setSelectedLocations((prev) =>
      prev.includes(location) ? prev.filter((l) => l !== location) : [...prev, location]
    );
  };

  const handleSubmitCheckIn = async () => {
    if (painLevel === 0 && selectedLocations.length === 0) return;

    try {
      setIsSubmitting(true);
      await plansApi.submitPainCheckIn({
        painLevel,
        locations: selectedLocations,
      });
      setSubmitSuccess(true);
      setPainLevel(0);
      setSelectedLocations([]);
      await loadStats();
      setTimeout(() => setSubmitSuccess(false), 3000);
    } catch (error) {
      logger.error("Error submitting check-in", { error });
      toast.error({ title: "Errore", description: "Impossibile inviare il check-in" });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden p-3 pb-safe gap-3">
      {/* Quick Stats */}
      <div className="hidden md:block">
        {isLoading ? (
          <div className="grid grid-cols-3 gap-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-muted animate-pulse rounded-xl h-16" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-card border rounded-xl p-3 text-center shadow-sm">
              <div className="text-xl font-bold text-red-500">
                {stats?.avg_pain_30_days?.toFixed(1) || "--"}
              </div>
              <div className="text-[10px] text-muted-foreground mt-0.5">Dolore Medio</div>
            </div>
            <div className="bg-card border rounded-xl p-3 text-center shadow-sm">
              <div className="text-xl font-bold text-primary">{stats?.total_assessments || "--"}</div>
              <div className="text-[10px] text-muted-foreground mt-0.5">Check-in</div>
            </div>
            <div className="bg-card border rounded-xl p-3 text-center shadow-sm">
              <div className="text-xl font-bold text-green-500">{stats?.mobility_score || "--"}</div>
              <div className="text-[10px] text-muted-foreground mt-0.5">Mobilità</div>
            </div>
          </div>
        )}
      </div>

      {/* New Check-in Card */}
      <div className="bg-card border rounded-xl p-3 md:p-4 shadow-sm md:shadow-lg flex flex-col gap-3">
          <h3 className="font-bold text-base md:text-lg flex items-center gap-2">
            <Plus className="w-4 h-4 md:w-5 md:h-5 text-primary" />
            Nuovo Check-in
          </h3>

          {/* Pain Level Slider */}
          <div>
            <label className="text-sm font-semibold mb-2 block">
              Livello Dolore: <span className="text-primary font-bold text-base md:text-lg">{painLevel}/10</span>
            </label>
            <input
              type="range"
              min="0"
              max="10"
              value={painLevel}
              onChange={(e) => setPainLevel(parseInt(e.target.value))}
              className="w-full h-3 bg-secondary rounded-xl appearance-none cursor-pointer accent-primary touch-manipulation"
              style={{ WebkitAppearance: 'none' }}
            />
            <div className="hidden md:flex justify-between text-sm text-muted-foreground mt-2">
              <span>😊 Nessuno</span>
              <span>😐 Moderato</span>
              <span>😣 Severo</span>
            </div>
          </div>

          {/* Body Heatmap */}
          <div>
            <label className="text-base font-semibold mb-3 block">Localizzazione</label>
            <BodyHeatmap
              selectedLocations={selectedLocations}
              onLocationToggle={handleLocationToggle}
              compact
              showIntensityControls={false}
            />
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmitCheckIn}
            disabled={(painLevel === 0 && selectedLocations.length === 0) || isSubmitting}
            className={cn(
              "w-full h-12 md:h-14 rounded-xl font-bold text-base md:text-lg disabled:opacity-50 flex items-center justify-center gap-2 transition-transform active:scale-[0.98] touch-manipulation shadow-sm md:shadow-lg",
              submitSuccess ? "bg-green-600 text-white" : "bg-primary text-primary-foreground"
            )}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Invio...
              </>
            ) : submitSuccess ? (
              "✓ Check-in Salvato!"
            ) : (
              "Registra Check-in"
            )}
          </button>
        </div>

        {/* Link to Progress */}
      <Link
        to="/progress"
        className="hidden md:flex items-center justify-between p-4 bg-secondary/50 rounded-xl hover:bg-secondary/70 transition-colors"
      >
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-muted-foreground" />
          <span className="font-medium">Vedi Storico Completo</span>
        </div>
        <ChevronRight className="w-5 h-5 text-muted-foreground" />
      </Link>
    </div>
  );
}

// ============================================================================
// PROTOCOL TAB - Piano settimanale medico
// ============================================================================

function ProtocolTab() {
  const [currentProtocol, setCurrentProtocol] = useState<MedicalProtocol | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [completedExercises, setCompletedExercises] = useState<Set<number>>(new Set());

  const MAX_VISIBLE_EXERCISES = 4;
  const MAX_VISIBLE_RESTRICTIONS = 4;

  useEffect(() => {
    loadProtocol();
  }, []);

  const loadProtocol = async () => {
    try {
      setIsLoading(true);
      const response = await plansApi.getCurrentMedicalProtocol();
      setCurrentProtocol(response.plan);
    } catch (error) {
      logger.error("Error loading protocol", { error });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateProtocol = async () => {
    try {
      setIsGenerating(true);
      await plansApi.generateMedicalProtocol({ current_pain_level: 5 });
      await loadProtocol();
    } catch (error) {
      logger.error("Error generating protocol", { error });
      toast.error({ title: "Errore", description: "Impossibile generare il protocollo" });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExerciseComplete = useCallback((exerciseIndex: number) => {
    hapticFeedback.impact("medium");
    setCompletedExercises(prev => {
      const next = new Set(prev);
      if (next.has(exerciseIndex)) {
        next.delete(exerciseIndex);
      } else {
        next.add(exerciseIndex);
      }
      return next;
    });
    toast.success({ title: "Esercizio completato!", description: "Ottimo lavoro 💪" });
  }, []);

  return (
    <div className="flex flex-col h-full overflow-hidden p-4 gap-3">
      {/* Current Protocol */}
      <div className="bg-card border rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-lg">{currentProtocol?.phase || "Nessun protocollo"}</h3>
            <p className="text-sm text-muted-foreground">
              {currentProtocol ? `Settimana ${currentProtocol.week_number}` : "--"}
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
          <div className="animate-pulse flex flex-col gap-2">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-12 bg-muted rounded-lg" />)}
          </div>
        ) : currentProtocol ? (
          <>
            {/* Check-in progress */}
            <div className="mb-4">
              <div className="flex justify-between text-xs text-muted-foreground mb-1">
                <span>Check-in completati</span>
                <span>{currentProtocol.checkins_completed}/{currentProtocol.checkins_required}</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full transition-all"
                  style={{ width: `${(currentProtocol.checkins_completed / currentProtocol.checkins_required) * 100}%` }}
                />
              </div>
            </div>

            {/* Exercises */}
            <div className="flex flex-col gap-2 mb-4">
              {currentProtocol.daily_exercises.slice(0, MAX_VISIBLE_EXERCISES).map((ex, i) => {
                const isCompleted = completedExercises.has(i);
                return (
                  <div
                    key={i}
                    className={cn(
                      "flex items-center justify-between p-3 rounded-lg border transition-all",
                      isCompleted ? "bg-green-500/10 border-green-500/30" : "bg-secondary/30"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      {isCompleted && <Check className="w-4 h-4 text-green-600" />}
                      <span className={cn("font-medium", isCompleted && "text-green-600")}>{ex.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {ex.sets && ex.reps ? `${ex.sets}x${ex.reps}` : ex.duration}
                      </span>
                    </div>
                    <button
                      onClick={() => handleExerciseComplete(i)}
                      className={cn(
                        "text-xs px-3 py-1.5 rounded-lg font-medium transition-all touch-manipulation min-h-[36px]",
                        isCompleted
                          ? "bg-green-600 text-white"
                          : "bg-primary text-primary-foreground hover:bg-primary/90"
                      )}
                    >
                      {isCompleted ? "✓ Fatto" : "Segna Fatto"}
                    </button>
                  </div>
                );
              })}
            </div>

            {/* Restrictions */}
            {currentProtocol.restrictions?.length > 0 && (
              <div className="hidden md:block bg-red-500/10 border border-red-500/30 rounded-xl p-3">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-medium text-red-600">Restrizioni</span>
                </div>
                <ul className="text-xs text-red-600 flex flex-col gap-1">
                  {translateRestrictions(currentProtocol.restrictions).slice(0, MAX_VISIBLE_RESTRICTIONS).map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
            <p className="text-muted-foreground mb-3">Nessun protocollo attivo</p>
            <button
              onClick={handleGenerateProtocol}
              disabled={isGenerating}
              className="flex items-center gap-2 mx-auto px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50"
            >
              {isGenerating ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              {isGenerating ? "Generazione..." : "Genera Protocollo"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// BIOMETRICS TAB
// ============================================================================

function BiometricsTab() {
  return (
    <div className="flex flex-col h-full overflow-hidden p-4 gap-3">
      <div className="bg-card border rounded-xl p-4">
        <div className="font-bold text-lg">Biometriche</div>
        <div className="mt-1 text-sm text-muted-foreground">
          Visualizza il dashboard biometrico nella pagina dedicata.
        </div>
        <Link
          to="/biometrics"
          className="mt-4 w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold flex items-center justify-center"
        >
          Apri Biometriche
        </Link>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN HUB
// ============================================================================

function MedicalHub() {
  return (
    <HubLayout
      tabs={[
        {
          id: "chat",
          label: "AI Doctor",
          icon: MessageSquare,
          component: () => <ChatInterface mode="medical" />,
        },
        {
          id: "checkin",
          label: "Check-in",
          icon: Activity,
          component: PainCheckInTab,
        },
        {
          id: "protocol",
          label: "Protocollo",
          icon: FileText,
          component: ProtocolTab,
        },
        {
          id: "biometrics",
          label: "Biometrics",
          icon: Heart,
          component: BiometricsTab,
        },
      ]}
    />
  );
}
