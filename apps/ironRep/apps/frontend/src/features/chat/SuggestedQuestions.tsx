import { MessageCircle, Dumbbell, Heart, Apple } from "lucide-react";
import { hapticFeedback } from "../../lib/haptics";
import { cn } from "../../lib/utils";

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
  mode?: "chat" | "checkin" | "medical" | "workout" | "nutrition";
}

// ============================================================================
// DOMANDE SPECIFICHE PER OGNI AGENTE
// ============================================================================

const COACH_QUESTIONS = [
  {
    category: "Programmazione",
    questions: [
      "Qual è il mio workout di oggi?",
      "Modifica il mio programma per questa settimana",
      "Aggiungi più volume per le gambe",
    ],
  },
  {
    category: "CrossFit",
    questions: [
      "Creami un EMOM di 15 minuti",
      "WOD Hero scalato per il mio livello",
      "Come migliorare i miei double-unders?",
    ],
  },
  {
    category: "Tecnica",
    questions: [
      "Cue per lo snatch",
      "Come migliorare il clean & jerk?",
      "Progressione per muscle-up",
    ],
  },
  {
    category: "Performance",
    questions: [
      "Come superare un plateau?",
      "Strategie per competizione",
      "Deload: quando e come?",
    ],
  },
];

const MEDICAL_QUESTIONS = [
  {
    category: "Dolore",
    questions: [
      "Perché ho dolore dopo l'allenamento?",
      "Differenza tra dolore buono e cattivo",
      "Quando preoccuparmi per un dolore?",
    ],
  },
  {
    category: "Recupero",
    questions: [
      "Strategie di recupero attivo",
      "Quanto riposo tra allenamenti?",
      "Benefici del foam rolling",
    ],
  },
  {
    category: "Prevenzione",
    questions: [
      "Esercizi preventivi per la schiena",
      "Come evitare infortuni alle spalle",
      "Warm-up ottimale pre-workout",
    ],
  },
  {
    category: "Progressione",
    questions: [
      "Quando tornare ad allenarmi dopo infortunio?",
      "Come scalare gli esercizi?",
      "Posso allenarmi con dolore 3/10?",
    ],
  },
];

const NUTRITION_QUESTIONS = [
  {
    category: "Macro",
    questions: [
      "Quante proteine al giorno?",
      "Timing dei carbo pre/post workout",
      "Come calcolare il deficit calorico",
    ],
  },
  {
    category: "Pasti",
    questions: [
      "Colazione proteica veloce",
      "Pasto post-workout ideale",
      "Snack sani per la sera",
    ],
  },
  {
    category: "Performance",
    questions: [
      "Alimentazione giorno di gara",
      "Come gestire i refeed",
      "Integratori essenziali per CrossFit",
    ],
  },
  {
    category: "Obiettivi",
    questions: [
      "Dieta per mettere massa",
      "Come perdere grasso senza perdere forza",
      "Alimentazione per il recupero",
    ],
  },
];

const DEFAULT_QUESTIONS = [
  {
    category: "Recupero",
    questions: [
      "Come posso accelerare il recupero?",
      "Esercizi per prevenire infortuni",
      "È normale avere DOMS?",
    ],
  },
  {
    category: "Allenamento",
    questions: [
      "Esercizi adatti al mio livello",
      "Migliori stretch per mobilità",
      "Come migliorare la mobilità",
    ],
  },
  {
    category: "Progressione",
    questions: [
      "Quando passare alla fase successiva?",
      "Come capire se sto migliorando?",
      "Tempo di recupero stimato?",
    ],
  },
];

// ============================================================================
// COMPONENTE
// ============================================================================

export function SuggestedQuestions({ onSelect, mode = "chat" }: SuggestedQuestionsProps) {
  const getQuestions = () => {
    switch (mode) {
      case "workout":
        return COACH_QUESTIONS;
      case "medical":
      case "checkin":
        return MEDICAL_QUESTIONS;
      case "nutrition":
        return NUTRITION_QUESTIONS;
      default:
        return DEFAULT_QUESTIONS;
    }
  };

  const getIcon = () => {
    switch (mode) {
      case "workout":
        return <Dumbbell className="h-4 w-4" />;
      case "medical":
      case "checkin":
        return <Heart className="h-4 w-4" />;
      case "nutrition":
        return <Apple className="h-4 w-4" />;
      default:
        return <MessageCircle className="h-4 w-4" />;
    }
  };

  const getTitle = () => {
    switch (mode) {
      case "workout":
        return "Chiedi al Coach";
      case "medical":
      case "checkin":
        return "Chiedi al Medico";
      case "nutrition":
        return "Chiedi al Nutrizionista";
      default:
        return "Domande Frequenti";
    }
  };

  const questions = getQuestions();

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        {getIcon()}
        <span>{getTitle()}</span>
      </div>

      <div className="flex flex-col gap-3">
        {questions.map((category, idx) => (
          <div key={category.category} className={cn(idx >= 2 && "hidden md:block")}>
            <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">
              {category.category}
            </h4>
            <div className="flex gap-2 overflow-x-auto no-scrollbar md:flex-wrap md:overflow-visible">
              {category.questions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => {
                    hapticFeedback.selection();
                    onSelect(question);
                  }}
                  className="shrink-0 md:shrink px-4 py-3 text-sm bg-card border rounded-full hover:bg-accent hover:border-primary transition-colors text-left min-h-[44px] touch-manipulation"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
