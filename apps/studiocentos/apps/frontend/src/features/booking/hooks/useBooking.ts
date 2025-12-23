/**
 * useBooking Hook - Create and manage bookings
 */

import { useState } from 'react';
import type { BookingFormData, BookingResponse } from '../types/booking.types';

interface UseBookingReturn {
  createBooking: (data: BookingFormData) => Promise<BookingResponse>;
  loading: boolean;
  error: Error | null;
  success: boolean;
}

export function useBooking(): UseBookingReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [success, setSuccess] = useState(false);

  const createBooking = async (data: BookingFormData): Promise<BookingResponse> => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);

      const { bookingApi } = await import('../api/bookingApi');
      const result = await bookingApi.createBooking(data);
      
      setSuccess(true);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    createBooking,
    loading,
    error,
    success,
  };
}
