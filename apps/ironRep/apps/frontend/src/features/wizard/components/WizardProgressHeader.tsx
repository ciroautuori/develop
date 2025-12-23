/**
 * WizardProgressHeader - Progress indicator for wizard steps
 *
 * Shows current step, total steps, and back button
 */

import { ChevronLeft } from "lucide-react";
import { cn } from "../../../lib/utils";

interface WizardProgressHeaderProps {
  currentStep: number;
  totalSteps: number;
  stepLabel: string;
  onBack?: () => void;
  showBack?: boolean;
}

export function WizardProgressHeader({
  currentStep,
  totalSteps,
  stepLabel,
  onBack,
  showBack = true,
}: WizardProgressHeaderProps) {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-md border-b safe-area-top">
      <div className="px-4 py-3">
        <div className="flex items-center gap-3">
          {showBack && onBack && (
            <button
              onClick={onBack}
              className={cn(
                "p-2 -ml-2 rounded-full hover:bg-secondary transition-colors",
                "touch-manipulation min-h-[44px] min-w-[44px] flex items-center justify-center"
              )}
              aria-label="Torna indietro"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{stepLabel}</span>
              <span className="text-xs text-muted-foreground">
                {currentStep} di {totalSteps}
              </span>
            </div>
            <div className="h-1 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300 ease-out rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
