/**
 * Booking API Client - Centralized API calls
 */

import type {
  CalendarAvailability,
  BookingFormData,
  BookingResponse,
  Booking,
} from '../types/booking.types';

const API_BASE = '/api/v1/booking';

export class BookingApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'BookingApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new BookingApiError(
      errorData.detail || `API Error: ${response.statusText}`,
      response.status,
      errorData
    );
  }
  return response.json();
}

export const bookingApi = {
  /**
   * Get calendar availability for date range
   */
  async getAvailability(params: {
    start_date: string;
    end_date: string;
    service_type?: string;
    timezone?: string;
  }): Promise<{ availability: CalendarAvailability[] }> {
    const response = await fetch(`${API_BASE}/calendar/availability`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...params,
        timezone: params.timezone || 'Europe/Rome',
      }),
    });
    return handleResponse(response);
  },

  /**
   * Create new booking
   */
  async createBooking(data: BookingFormData): Promise<BookingResponse> {
    const response = await fetch(`${API_BASE}/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Get booking by ID
   */
  async getBooking(id: number): Promise<Booking> {
    const response = await fetch(`${API_BASE}/bookings/${id}`);
    return handleResponse(response);
  },

  /**
   * Cancel booking
   */
  async cancelBooking(id: number, reason?: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE}/bookings/${id}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cancellation_reason: reason }),
    });
    return handleResponse(response);
  },

  /**
   * Reschedule booking
   */
  async rescheduleBooking(
    id: number,
    newDatetime: string
  ): Promise<BookingResponse> {
    const response = await fetch(`${API_BASE}/bookings/${id}/reschedule`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_datetime: newDatetime }),
    });
    return handleResponse(response);
  },

  /**
   * Get my bookings (requires auth)
   */
  async getMyBookings(): Promise<{ bookings: Booking[] }> {
    const response = await fetch(`${API_BASE}/bookings/my`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    });
    return handleResponse(response);
  },
};
