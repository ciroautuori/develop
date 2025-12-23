/**
 * Offline Queue System
 * Queues operations when offline and syncs when back online
 */

import { useState, useEffect, useCallback } from 'react';
import type { BiometricData } from '../lib/api';

// ============================================================================
// Operation Data Types (Type-safe discriminated union)
// ============================================================================

interface WorkoutCompleteData {
  workoutId: string;
  painImpact: number;
  feedback: string;
}

interface PainAssessmentData {
  pain_level: number;
  pain_locations: string[];
  notes?: string;
}

interface ExerciseToggleData {
  sessionId: string;
  exerciseName: string;
}

type OperationDataMap = {
  'workout-complete': WorkoutCompleteData;
  'pain-assessment': PainAssessmentData;
  'biometrics': BiometricData;
  'exercise-toggle': ExerciseToggleData;
};

export type OperationType = keyof OperationDataMap;

export interface QueuedOperation<T extends OperationType = OperationType> {
  id: string;
  type: T;
  data: OperationDataMap[T];
  timestamp: number;
  retryCount: number;
}

const QUEUE_STORAGE_KEY = 'offline-queue';
const MAX_RETRIES = 3;

/**
 * Offline Queue Hook
 */
export function useOfflineQueue() {
  const [queue, setQueue] = useState<QueuedOperation[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Load queue from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(QUEUE_STORAGE_KEY);
    if (stored) {
      try {
        setQueue(JSON.parse(stored));
      } catch (error) {
        console.error('Failed to parse offline queue:', error);
        localStorage.removeItem(QUEUE_STORAGE_KEY);
      }
    }
  }, []);

  // Save queue to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
  }, [queue]);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Auto-sync when coming back online
  useEffect(() => {
    if (isOnline && queue.length > 0 && !isSyncing) {
      syncQueue();
    }
  }, [isOnline, queue.length]);

  /**
   * Add operation to queue (type-safe)
   */
  const addToQueue = useCallback(<T extends OperationType>(
    type: T,
    data: OperationDataMap[T]
  ) => {
    const operation: QueuedOperation<T> = {
      id: `${type}-${Date.now()}-${Math.random()}`,
      type,
      data,
      timestamp: Date.now(),
      retryCount: 0,
    };

    setQueue((prev) => [...prev, operation as QueuedOperation]);
    return operation.id;
  }, []);

  /**
   * Remove operation from queue
   */
  const removeFromQueue = useCallback((id: string) => {
    setQueue((prev) => prev.filter((op) => op.id !== id));
  }, []);

  /**
   * Sync queue with backend
   */
  const syncQueue = useCallback(async () => {
    if (isSyncing || queue.length === 0) return;

    setIsSyncing(true);

    const operations = [...queue];
    const failed: QueuedOperation[] = [];

    for (const operation of operations) {
      try {
        await processOperation(operation);
        removeFromQueue(operation.id);
      } catch (error) {
        console.error(`Failed to sync operation ${operation.id}:`, error);

        if (operation.retryCount < MAX_RETRIES) {
          failed.push({
            ...operation,
            retryCount: operation.retryCount + 1,
          });
        } else {
          // Max retries reached, remove from queue
          removeFromQueue(operation.id);
          console.warn(`Operation ${operation.id} failed after ${MAX_RETRIES} retries`);
        }
      }
    }

    // Update queue with failed operations (with incremented retry count)
    setQueue(failed);
    setIsSyncing(false);
  }, [queue, isSyncing, removeFromQueue]);

  /**
   * Clear all queued operations
   */
  const clearQueue = useCallback(() => {
    setQueue([]);
    localStorage.removeItem(QUEUE_STORAGE_KEY);
  }, []);

  return {
    queue,
    isOnline,
    isSyncing,
    addToQueue,
    removeFromQueue,
    syncQueue,
    clearQueue,
  };
}

/**
 * Process individual operation
 */
async function processOperation(operation: QueuedOperation): Promise<void> {
  // Import APIs dynamically to avoid circular dependencies
  const { workoutsApi, medicalApi, biometricsApi } = await import('../lib/api');

  switch (operation.type) {
    case 'workout-complete': {
      const data = operation.data as WorkoutCompleteData;
      await workoutsApi.completeWorkout(data.workoutId, data.painImpact, data.feedback);
      break;
    }

    case 'pain-assessment': {
      const data = operation.data as PainAssessmentData;
      await medicalApi.submitPainAssessment(data);
      break;
    }

    case 'biometrics': {
      const data = operation.data as BiometricData;
      await biometricsApi.create(data);
      break;
    }

    case 'exercise-toggle': {
      const data = operation.data as ExerciseToggleData;
      await workoutsApi.updateExerciseStatus(data.sessionId, data.exerciseName);
      break;
    }

    default: {
      const _exhaustive: never = operation.type;
      throw new Error(`Unknown operation type: ${_exhaustive}`);
    }
  }
}

/**
 * Hook for showing offline indicator
 */
export function useOfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showIndicator, setShowIndicator] = useState(false);

  useEffect(() => {
    let timeout: number;

    const handleOnline = () => {
      setIsOnline(true);
      setShowIndicator(true);

      // Hide indicator after 3 seconds
      timeout = setTimeout(() => setShowIndicator(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowIndicator(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearTimeout(timeout);
    };
  }, []);

  return {
    isOnline,
    showIndicator,
  };
}
