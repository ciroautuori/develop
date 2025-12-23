/**
 * Tour Hook - Gestisce stato e persistence dei tour
 */

import { useState, useCallback, useEffect } from 'react';

export interface TourStep {
  id: string;
  targetId: string | null; // null = fullscreen welcome
  title: string;
  description: string;
  position: 'top' | 'bottom' | 'left' | 'right' | 'center';
  action?: 'click' | 'hover' | 'none';
}

interface TourState {
  isActive: boolean;
  currentStepIndex: number;
  tourId: string | null;
}

const STORAGE_KEY = 'ironrep_tours_completed';

function getCompletedTours(): string[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function markTourCompleted(tourId: string): void {
  const completed = getCompletedTours();
  if (!completed.includes(tourId)) {
    completed.push(tourId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(completed));
  }
}

function isTourCompleted(tourId: string): boolean {
  return getCompletedTours().includes(tourId);
}

export function useTour(tourId: string, steps: TourStep[]) {
  const [state, setState] = useState<TourState>({
    isActive: false,
    currentStepIndex: 0,
    tourId: null,
  });

  const currentStep = state.isActive ? steps[state.currentStepIndex] : null;
  const totalSteps = steps.length;
  const isCompleted = isTourCompleted(tourId);

  // Start tour
  const startTour = useCallback(() => {
    if (steps.length === 0) return;
    setState({
      isActive: true,
      currentStepIndex: 0,
      tourId,
    });
  }, [tourId, steps.length]);

  // Next step
  const nextStep = useCallback(() => {
    setState((prev) => {
      if (!prev.isActive) return prev;

      const nextIndex = prev.currentStepIndex + 1;
      if (nextIndex >= steps.length) {
        // Tour completed
        markTourCompleted(tourId);
        return { isActive: false, currentStepIndex: 0, tourId: null };
      }

      return { ...prev, currentStepIndex: nextIndex };
    });
  }, [tourId, steps.length]);

  // Previous step
  const prevStep = useCallback(() => {
    setState((prev) => {
      if (!prev.isActive || prev.currentStepIndex === 0) return prev;
      return { ...prev, currentStepIndex: prev.currentStepIndex - 1 };
    });
  }, []);

  // Skip tour
  const skipTour = useCallback(() => {
    markTourCompleted(tourId);
    setState({ isActive: false, currentStepIndex: 0, tourId: null });
  }, [tourId]);

  // Reset tour (for "Rivedi tour" feature)
  const resetTour = useCallback(() => {
    const completed = getCompletedTours().filter(id => id !== tourId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(completed));
  }, [tourId]);

  // Auto-start if not completed (optional, controlled by component)
  const autoStart = useCallback(() => {
    if (!isCompleted && steps.length > 0) {
      startTour();
    }
  }, [isCompleted, steps.length, startTour]);

  return {
    isActive: state.isActive,
    currentStep,
    currentStepIndex: state.currentStepIndex,
    totalSteps,
    isCompleted,
    startTour,
    nextStep,
    prevStep,
    skipTour,
    resetTour,
    autoStart,
  };
}
