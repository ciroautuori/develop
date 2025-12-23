/**
 * DashboardTour - Componente completo per il tour della dashboard
 * Combina spotlight e tooltip per esperienza stile Google
 */

import { useEffect } from 'react';
import { TourSpotlight } from './components/TourSpotlight';
import { TourTooltip } from './components/TourTooltip';
import { useTour } from './hooks/useTour';
import { dashboardTourSteps, DASHBOARD_TOUR_ID } from './tours/dashboardTour';

interface DashboardTourProps {
  /** Auto-start tour for new users */
  autoStart?: boolean;
  /** Callback when tour completes */
  onComplete?: () => void;
}

export function DashboardTour({ autoStart = false, onComplete }: DashboardTourProps) {
  const {
    isActive,
    currentStep,
    currentStepIndex,
    totalSteps,
    isCompleted,
    startTour,
    nextStep,
    prevStep,
    skipTour,
  } = useTour(DASHBOARD_TOUR_ID, dashboardTourSteps);

  // Auto-start on mount if not completed
  useEffect(() => {
    if (autoStart && !isCompleted) {
      // Small delay to let dashboard render first
      const timer = setTimeout(() => {
        startTour();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [autoStart, isCompleted, startTour]);

  // Handle tour completion
  const handleNext = () => {
    if (currentStepIndex === totalSteps - 1) {
      skipTour();
      onComplete?.();
    } else {
      nextStep();
    }
  };

  const handleSkip = () => {
    skipTour();
    onComplete?.();
  };

  if (!isActive || !currentStep) return null;

  return (
    <TourSpotlight
      targetId={currentStep.targetId}
      isActive={isActive}
      padding={12}
      borderRadius={16}
    >
      <TourTooltip
        step={currentStep}
        currentIndex={currentStepIndex}
        totalSteps={totalSteps}
        onNext={handleNext}
        onPrev={prevStep}
        onSkip={handleSkip}
      />
    </TourSpotlight>
  );
}

// Export hook for external control (e.g., "Rivedi tour" button)
export { useTour } from './hooks/useTour';
export { DASHBOARD_TOUR_ID } from './tours/dashboardTour';
