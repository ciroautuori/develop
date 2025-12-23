import { Zap } from "lucide-react";
import { hapticFeedback } from "../../lib/haptics";

interface QuickNotesTemplatesProps {
  onSelect: (note: string) => void;
}

const TEMPLATES = [
  {
    id: "morning",
    label: "Dolore Mattutino",
    text: "Dolore più intenso al risveglio, migliora durante la giornata.",
  },
  {
    id: "after-workout",
    label: "Post Workout",
    text: "Dolore aumentato dopo allenamento, necessario più recupero.",
  },
  {
    id: "sitting",
    label: "Da Seduto",
    text: "Dolore peggiora stando seduto a lungo, migliora in movimento.",
  },
  {
    id: "standing",
    label: "In Piedi",
    text: "Difficoltà a stare in piedi per periodi prolungati.",
  },
  {
    id: "night",
    label: "Notturno",
    text: "Dolore disturba il sonno, difficoltà a trovare posizione comoda.",
  },
  {
    id: "weather",
    label: "Meteo",
    text: "Dolore influenzato da cambiamenti meteorologici.",
  },
  {
    id: "stress",
    label: "Stress",
    text: "Dolore aumenta in periodi di stress emotivo/fisico.",
  },
  {
    id: "improving",
    label: "Miglioramento",
    text: "Noto miglioramento generale, dolore meno frequente.",
  },
];

export function QuickNotesTemplates({ onSelect }: QuickNotesTemplatesProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Zap className="h-4 w-4" />
        <span>Template Rapidi</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {TEMPLATES.map((template) => (
          <button
            key={template.id}
            onClick={() => {
              hapticFeedback.selection();
              onSelect(template.text);
            }}
            className="p-3 text-left rounded-lg border bg-card hover:bg-accent hover:border-primary transition-colors group"
          >
            <div className="text-sm font-medium mb-1 group-hover:text-primary transition-colors">
              {template.label}
            </div>
            <div className="text-xs text-muted-foreground line-clamp-2">
              {template.text}
            </div>
          </button>
        ))}
      </div>

      <div className="text-xs text-muted-foreground text-center pt-2">
        💡 Clicca su un template per aggiungerlo alle note
      </div>
    </div>
  );
}
