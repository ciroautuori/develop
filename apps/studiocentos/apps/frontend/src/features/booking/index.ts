/**
 * Booking Feature - Export barrel
 */

// Components
export { CalendarView } from './components/CalendarView';
export { TimeSlotPicker } from './components/TimeSlotPicker';
export { BookingForm } from './components/BookingForm';
export { BookingConfirmation } from './components/BookingConfirmation';
export { ServiceSelector } from './components/ServiceSelector';
export { BookingWizard } from './components/BookingWizard';
export { BookingSummary } from './components/BookingSummary';

// Hooks
export { useAvailability } from './hooks/useAvailability';
export { useBooking } from './hooks/useBooking';

// Types
export type {
  AvailableSlot,
  CalendarAvailability,
  BookingFormData,
  Booking,
  BookingResponse,
  ServiceType,
  MeetingProvider,
} from './types/booking.types';

export { SERVICE_TYPES, MEETING_PROVIDERS } from './types/booking.types';
