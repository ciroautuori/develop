import { useState } from "react";
import { AlertCircle, X } from "lucide-react";
import { hapticFeedback } from "../../lib/haptics";

interface PainCheckModalProps {
  onSubmit: (painLevel: number) => void;
  onSkip: () => void;
}

export function PainCheckModal({ onSubmit, onSkip }: PainCheckModalProps) {
  const [painLevel, setPainLevel] = useState(5);

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-card rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 dark:bg-amber-900/20 rounded-full">
              <AlertCircle className="h-6 w-6 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Pain Check</h2>
              <p className="text-sm text-muted-foreground">
                Come ti senti ora?
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              hapticFeedback.selection();
              onSkip();
            }}
            className="p-1 hover:bg-accent rounded-md"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Pain Level Slider */}
          <div>
            <label className="block text-sm font-medium mb-3">
              Livello Dolore Attuale
            </label>
            <div className="space-y-3">
              <input
                type="range"
                min="0"
                max="10"
                value={painLevel}
                onChange={(e) => {
                  setPainLevel(Number(e.target.value));
                  hapticFeedback.selection();
                }}
                className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>0 - Nessun dolore</span>
                <span className="text-2xl font-bold text-primary">
                  {painLevel}
                </span>
                <span>10 - Massimo</span>
              </div>
            </div>
          </div>

          {/* Pain Level Indicator */}
          <div
            className={`p-4 rounded-lg ${
              painLevel >= 7
                ? "bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800"
                : painLevel >= 5
                  ? "bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800"
                  : "bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800"
            }`}
          >
            <p
              className={`text-sm font-medium ${
                painLevel >= 7
                  ? "text-red-900 dark:text-red-100"
                  : painLevel >= 5
                    ? "text-amber-900 dark:text-amber-100"
                    : "text-green-900 dark:text-green-100"
              }`}
            >
              {painLevel >= 7 && "⚠️ Dolore elevato - Considera di fermarti"}
              {painLevel >= 5 &&
                painLevel < 7 &&
                "⚡ Dolore moderato - Procedi con cautela"}
              {painLevel < 5 && "✅ Dolore gestibile - Puoi continuare"}
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={() => {
                hapticFeedback.selection();
                onSkip();
              }}
              className="flex-1 px-4 py-3 border rounded-lg hover:bg-accent transition-colors"
            >
              Salta
            </button>
            <button
              onClick={() => {
                hapticFeedback.impact("medium");
                onSubmit(painLevel);
              }}
              className="flex-1 px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-semibold"
            >
              Continua
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
