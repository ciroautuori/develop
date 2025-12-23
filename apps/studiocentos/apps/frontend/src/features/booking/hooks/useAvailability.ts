/**
 * useAvailability Hook - Fetch calendar availability
 */

import { useState, useEffect } from 'react';
import type { CalendarAvailability, ServiceType } from '../types/booking.types';

interface UseAvailabilityParams {
  startDate: Date;
  endDate: Date;
  serviceType?: ServiceType;
}

interface UseAvailabilityReturn {
  availability: CalendarAvailability[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useAvailability({
  startDate,
  endDate,
  serviceType,
}: UseAvailabilityParams): UseAvailabilityReturn {
  const [availability, setAvailability] = useState<CalendarAvailability[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchAvailability = async () => {
    try {
      setLoading(true);
      setError(null);

      const { bookingApi } = await import('../api/bookingApi');
      const data = await bookingApi.getAvailability({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        service_type: serviceType,
        timezone: 'Europe/Rome',
      });

      setAvailability(data.availability || []);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      console.error('Error fetching availability:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAvailability();
  }, [startDate, endDate, serviceType]);

  return {
    availability,
    loading,
    error,
    refetch: fetchAvailability,
  };
}
