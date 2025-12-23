/**
 * Bookings Admin Hooks - React Query hooks for calendar management
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { API_ENDPOINTS, STORAGE_KEYS } from '../../../shared/config/constants';

const API_URL = API_ENDPOINTS.admin.bookings;

const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem(STORAGE_KEYS.adminToken)}`
});

// ============================================================================
// BOOKINGS HOOKS
// ============================================================================

export function useBookings(filters = {}) {
  return useQuery({
    queryKey: ['admin-bookings', filters],
    queryFn: async () => {
      const { data } = await axios.get(API_URL, {
        params: filters,
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useBooking(id: number) {
  return useQuery({
    queryKey: ['admin-booking', id],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/${id}`, {
        headers: getAuthHeaders()
      });
      return data;
    },
    enabled: !!id
  });
}

export function useCreateBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (bookingData: any) => {
      const { data } = await axios.post(API_URL, bookingData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['admin-calendar-month'] });
    }
  });
}

export function useUpdateBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data: bookingData }: { id: number; data: any }) => {
      const { data } = await axios.put(`${API_URL}/${id}`, bookingData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['admin-calendar-month'] });
    }
  });
}

export function useDeleteBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`${API_URL}/${id}`, {
        headers: getAuthHeaders()
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['admin-calendar-month'] });
    }
  });
}

export function useConfirmBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await axios.post(`${API_URL}/${id}/confirm`, {}, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['admin-calendar-month'] });
    }
  });
}

export function useCancelBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, reason }: { id: number; reason: string }) => {
      const { data } = await axios.post(`${API_URL}/${id}/cancel`, { reason }, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['admin-calendar-month'] });
    }
  });
}

export function useRescheduleBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, scheduled_at, duration_minutes, reason }: any) => {
      const { data } = await axios.post(`${API_URL}/${id}/reschedule`, {
        scheduled_at,
        duration_minutes,
        reason
      }, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['admin-calendar-month'] });
    }
  });
}

// ============================================================================
// CALENDAR VIEWS
// ============================================================================

export function useCalendarDay(date: string) {
  return useQuery({
    queryKey: ['admin-calendar-day', date],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/calendar/day`, {
        params: { target_date: date },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useCalendarWeek(date: string) {
  return useQuery({
    queryKey: ['admin-calendar-week', date],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/calendar/week`, {
        params: { target_date: date },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useCalendarMonth(year: number, month: number) {
  return useQuery({
    queryKey: ['admin-calendar-month', year, month],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/calendar/month`, {
        params: { year, month },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

// ============================================================================
// STATISTICS
// ============================================================================

export function useBookingStats(from_date?: string, to_date?: string) {
  return useQuery({
    queryKey: ['admin-booking-stats', from_date, to_date],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/stats`, {
        params: { from_date, to_date },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

// ============================================================================
// AVAILABILITY SLOTS
// ============================================================================

export function useAvailabilitySlots() {
  return useQuery({
    queryKey: ['admin-availability-slots'],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/availability/slots`, {
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useCreateAvailabilitySlot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (slotData: any) => {
      const { data } = await axios.post(`${API_URL}/availability/slots`, slotData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-availability-slots'] });
    }
  });
}

// ============================================================================
// BLOCKED DATES
// ============================================================================

export function useBlockedDates(from_date?: string, to_date?: string) {
  return useQuery({
    queryKey: ['admin-blocked-dates', from_date, to_date],
    queryFn: async () => {
      const { data } = await axios.get(`${API_URL}/blocked-dates`, {
        params: { from_date, to_date },
        headers: getAuthHeaders()
      });
      return data;
    }
  });
}

export function useCreateBlockedDate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (blockedData: any) => {
      const { data } = await axios.post(`${API_URL}/blocked-dates`, blockedData, {
        headers: getAuthHeaders()
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-blocked-dates'] });
      queryClient.invalidateQueries({ queryKey: ['admin-calendar-month'] });
    }
  });
}
