import { AlertTriangle } from "lucide-react";

export function HighPainAlert({
  open,
  onContinue,
  onStop,
}: {
  open: boolean;
  onContinue: () => void;
  onStop: () => void;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-card w-full max-w-sm rounded-2xl p-6 shadow-2xl border-2 border-destructive/20">
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-4">
            <AlertTriangle className="h-8 w-8 text-destructive" />
          </div>
          <h3 className="text-xl font-bold text-foreground mb-2">Livello di Dolore Elevato</h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Hai segnalato un dolore significativo (7+). Continuare l'allenamento potrebbe peggiorare la situazione.
            Consigliamo di interrompere o consultare il Medical Agent.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <button
            onClick={onStop}
            className="w-full py-3.5 bg-destructive text-destructive-foreground rounded-xl font-bold shadow-lg active:scale-95 transition-transform"
          >
            Interrompi Workout
          </button>
          <button
            onClick={onContinue}
            className="w-full py-3.5 bg-secondary text-secondary-foreground rounded-xl font-bold active:scale-95 transition-transform"
          >
            Continua con Cautela
          </button>
        </div>
      </div>
    </div>
  );
}
