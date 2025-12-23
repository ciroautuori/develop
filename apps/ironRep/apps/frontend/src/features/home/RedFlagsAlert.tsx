import { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import { AlertTriangle, X } from "lucide-react";
import { checkinApi } from "../../lib/api";
import { touchTarget } from "../../lib/touch-targets";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

export function RedFlagsAlert() {
  const [redFlags, setRedFlags] = useState<string[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const checkForRedFlags = async () => {
      try {
        const response = await checkinApi.getHistory(1);
        if (
          response.success &&
          response.assessments &&
          response.assessments.length > 0
        ) {
          const lastCheckIn = response.assessments[0];
          if (lastCheckIn.red_flags && lastCheckIn.red_flags.length > 0) {
            setRedFlags(lastCheckIn.red_flags);
            setIsVisible(true);
          }
        }
      } catch (error) {
        logger.error('Failed to check for red flags', { error });
      }
    };

    checkForRedFlags();
  }, []);

  const handleDismiss = () => {
    hapticFeedback.selection();
    setIsVisible(false);
  };

  if (!isVisible || redFlags.length === 0) {
    return null;
  }

  return (
    <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-xl p-3 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full flex-shrink-0">
          <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-bold text-sm text-red-900 dark:text-red-100">
              ⚠️ Red Flags Rilevati
            </h3>
            <button
              onClick={handleDismiss}
              className={cn(
                touchTarget.icon.sm,
                "hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors"
              )}
              aria-label="Chiudi alert"
            >
              <X className="h-4 w-4 text-red-600 dark:text-red-400" />
            </button>
          </div>

          <ul className="space-y-1.5 text-sm text-red-800 dark:text-red-200 mb-2.5">
            {redFlags.map((flag, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-red-600 dark:text-red-400 font-bold leading-none">•</span>
                <span className="leading-relaxed">{flag}</span>
              </li>
            ))}
          </ul>

          <div className="bg-red-100 dark:bg-red-900/30 rounded-xl p-2.5 text-sm text-red-900 dark:text-red-100">
            <p className="font-bold mb-1">Azione Raccomandata:</p>
            <p className="leading-relaxed">
              Consulta un medico il prima possibile. Questi sintomi richiedono
              attenzione professionale.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
