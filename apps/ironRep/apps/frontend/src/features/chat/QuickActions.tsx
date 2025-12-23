import type React from "react";
import {
  Dumbbell, Search, TrendingUp, Zap, Trophy, Target, Flame,
  Heart, Activity, AlertTriangle,
  Apple, UtensilsCrossed, Calculator, ChefHat
} from "lucide-react";
import { hapticFeedback } from "../../lib/haptics";

interface QuickAction {
  id: string;
  icon: React.ReactNode;
  label: string;
  prompt: string;
  color: string;
}

interface QuickActionsProps {
  onAction: (prompt: string) => void;
  mode?: "chat" | "checkin" | "medical" | "workout" | "nutrition";
}

// ============================================================================
// AZIONI SPECIFICHE PER OGNI AGENTE
// ============================================================================

const COACH_ACTIONS: QuickAction[] = [
  {
    id: "generate-workout",
    icon: <Dumbbell className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Genera Workout",
    prompt: "Genera un workout completo per oggi basato sui miei obiettivi",
    color: "text-blue-600 dark:text-blue-400",
  },
  {
    id: "wod-crossfit",
    icon: <Flame className="h-4 w-4 md:h-5 md:w-5" />,
    label: "WOD CrossFit",
    prompt: "Creami un WOD CrossFit scalato per il mio livello",
    color: "text-orange-600 dark:text-orange-400",
  },
  {
    id: "check-pr",
    icon: <Trophy className="h-4 w-4 md:h-5 md:w-5" />,
    label: "I Miei PR",
    prompt: "Mostrami i miei personal record e suggerisci come migliorarli",
    color: "text-amber-600 dark:text-amber-400",
  },
  {
    id: "technique",
    icon: <Target className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Fix Tecnica",
    prompt: "Ho bisogno di cue tecnici per migliorare i miei lift principali",
    color: "text-violet-600 dark:text-violet-400",
  },
];

const MEDICAL_ACTIONS: QuickAction[] = [
  {
    id: "pain-checkin",
    icon: <Activity className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Check-in Dolore",
    prompt: "Voglio registrare il mio livello di dolore attuale",
    color: "text-red-600 dark:text-red-400",
  },
  {
    id: "red-flags",
    icon: <AlertTriangle className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Red Flags",
    prompt: "Come capisco se il mio dolore è un segnale di allarme?",
    color: "text-amber-600 dark:text-amber-400",
  },
  {
    id: "recovery-tips",
    icon: <Heart className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Recupero",
    prompt: "Dammi strategie di recupero per la mia condizione attuale",
    color: "text-pink-600 dark:text-pink-400",
  },
  {
    id: "analyze-trend",
    icon: <TrendingUp className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Trend Dolore",
    prompt: "Analizza il mio trend di dolore e dimmi come sto progredendo",
    color: "text-emerald-600 dark:text-emerald-400",
  },
];

const NUTRITION_ACTIONS: QuickAction[] = [
  {
    id: "meal-plan",
    icon: <ChefHat className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Piano Pasti",
    prompt: "Genera un piano pasti settimanale basato sui miei obiettivi",
    color: "text-orange-600 dark:text-orange-400",
  },
  {
    id: "calc-macros",
    icon: <Calculator className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Calcola Macro",
    prompt: "Calcola i miei macro giornalieri in base al mio obiettivo",
    color: "text-blue-600 dark:text-blue-400",
  },
  {
    id: "quick-recipe",
    icon: <UtensilsCrossed className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Ricetta Veloce",
    prompt: "Suggerisci una ricetta veloce e proteica per oggi",
    color: "text-emerald-600 dark:text-emerald-400",
  },
  {
    id: "supplements",
    icon: <Apple className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Integratori",
    prompt: "Quali integratori dovrei prendere per i miei obiettivi?",
    color: "text-violet-600 dark:text-violet-400",
  },
];

const DEFAULT_ACTIONS: QuickAction[] = [
  {
    id: "generate-workout",
    icon: <Dumbbell className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Genera Workout",
    prompt: "Genera un workout adattato al mio livello di dolore attuale",
    color: "text-emerald-600 dark:text-emerald-400",
  },
  {
    id: "safe-exercises",
    icon: <Search className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Esercizi Sicuri",
    prompt: "Mostrami gli esercizi sicuri per la mia condizione attuale",
    color: "text-blue-600 dark:text-blue-400",
  },
  {
    id: "analyze-trend",
    icon: <TrendingUp className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Trend Dolore",
    prompt: "Analizza il mio trend di dolore degli ultimi 7 giorni",
    color: "text-violet-600 dark:text-violet-400",
  },
  {
    id: "quick-tips",
    icon: <Zap className="h-4 w-4 md:h-5 md:w-5" />,
    label: "Tips Rapidi",
    prompt: "Dammi 3 consigli rapidi per gestire il dolore oggi",
    color: "text-amber-600 dark:text-amber-400",
  },
];

// ============================================================================
// COMPONENTE
// ============================================================================

export function QuickActions({ onAction, mode = "chat" }: QuickActionsProps) {
  const getActions = () => {
    switch (mode) {
      case "workout":
        return COACH_ACTIONS;
      case "medical":
      case "checkin":
        return MEDICAL_ACTIONS;
      case "nutrition":
        return NUTRITION_ACTIONS;
      default:
        return DEFAULT_ACTIONS;
    }
  };

  const getTitle = () => {
    switch (mode) {
      case "workout":
        return "🏋️ Azioni Coach";
      case "medical":
      case "checkin":
        return "🩺 Azioni Mediche";
      case "nutrition":
        return "🍎 Azioni Nutrizione";
      default:
        return "⚡ Azioni Rapide";
    }
  };

  const actions = getActions();
  const mobileColsClass = actions.length <= 3 ? "grid-cols-3" : "grid-cols-2";

  return (
    <div className={`grid ${mobileColsClass} gap-2 md:grid-cols-2 md:gap-3`}>
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={() => {
            hapticFeedback.selection();
            onAction(action.prompt);
          }}
          className="flex items-center justify-center gap-1.5 px-2.5 py-1.5 min-h-[44px] rounded-xl border bg-card/60 hover:bg-card transition-transform active:scale-[0.98] touch-manipulation select-none shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30"
        >
          <span className={`inline-flex ${action.color}`}>{action.icon}</span>
          <span className="text-[10px] font-semibold text-center leading-tight text-foreground">
            {action.label}
          </span>
        </button>
      ))}
    </div>
  );
}
