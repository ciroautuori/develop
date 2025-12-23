import { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import { TrendingUp, Calendar, Award } from "lucide-react";
import { usersApi } from "../../lib/api";

export function CurrentPhaseCard() {
  const [phase, setPhase] = useState("");
  const [weeksInPhase, setWeeksInPhase] = useState(0);
  const [nextPhase, setNextPhase] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const user = await usersApi.getMe();
        if (user) {
          setPhase(user.current_phase || "Fase 1: Recupero Iniziale");
          setWeeksInPhase(user.weeks_in_current_phase || 0);

          const phaseMap: Record<string, string> = {
            "Fase 1: Recupero Iniziale": "Fase 2: Consolidamento",
            "Fase 2: Consolidamento": "Fase 3: Potenziamento",
            "Fase 3: Potenziamento": "Fase 4: Performance",
            "Fase 4: Performance": "Completato",
          };
          setNextPhase(phaseMap[user.current_phase] || "N/A");
        }
      } catch (error: unknown) {
        logger.error('Failed to load user profile', { error });
        setPhase("");
        setWeeksInPhase(0);
        setNextPhase("");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, []);

  if (isLoading) {
    return (
      <div className="bg-card rounded-xl p-3 border animate-pulse shadow-sm">
        <div className="h-4 bg-secondary rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-secondary rounded w-3/4"></div>
      </div>
    );
  }

  if (!phase) {
    return (
      <div className="bg-card rounded-xl p-3 border shadow-sm text-center">
        <p className="text-muted-foreground text-sm">
          Completa il tuo profilo per vedere la fase attuale
        </p>
      </div>
    );
  }

  const phaseNumber = phase.match(/Fase (\d)/)?.[1] || "1";
  const phaseProgress = (parseInt(phaseNumber) / 4) * 100;

  return (
    <div className="bg-card rounded-xl p-3 border shadow-sm relative overflow-hidden">
      <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-full -translate-y-12 -translate-x-6 blur-2xl pointer-events-none" />

      <div className="flex items-start justify-between mb-2 relative z-10">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-primary/80 bg-primary/10 px-2 py-0.5 rounded">
              Fase Attuale
            </span>
            <span className="text-[10px] text-muted-foreground flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              Settimana {weeksInPhase}
            </span>
          </div>
          <h2 className="text-sm font-bold text-foreground leading-tight truncate">
            {phase}
          </h2>
        </div>

        <div className="relative w-11 h-11 flex items-center justify-center shrink-0 ml-3">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="28"
              cy="28"
              r="24"
              stroke="currentColor"
              strokeWidth="5"
              fill="none"
              className="text-secondary"
            />
            <circle
              cx="28"
              cy="28"
              r="24"
              stroke="currentColor"
              strokeWidth="5"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 24}`}
              strokeDashoffset={`${2 * Math.PI * 24 * (1 - phaseProgress / 100)}`}
              className="text-primary"
              strokeLinecap="round"
            />
          </svg>
          <span className="absolute text-[10px] font-bold">
            {Math.round(phaseProgress)}%
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 bg-muted/30 p-2.5 rounded-xl border border-border/50 relative z-10">
        <div className="p-2 bg-background rounded-full shadow-sm">
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[10px] text-muted-foreground uppercase tracking-wide font-medium">
            Prossimo Step
          </div>
          <div className="text-sm font-semibold truncate mt-0.5">{nextPhase}</div>
        </div>
      </div>

      {weeksInPhase >= 2 && (
        <div className="mt-2 flex items-center gap-2 text-xs text-green-600 dark:text-green-400 font-semibold">
          <Award className="h-3.5 w-3.5" />
          <span>Pronto per la valutazione progresso!</span>
        </div>
      )}
    </div>
  );
}
