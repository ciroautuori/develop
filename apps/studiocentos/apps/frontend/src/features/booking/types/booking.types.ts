/**
 * Booking Types - TypeScript interfaces per sistema prenotazioni
 */

export interface AvailableSlot {
  datetime: string;
  duration_minutes: number;
  service_type: string;
  available: boolean;
}

export interface CalendarAvailability {
  date: string;
  slots: AvailableSlot[];
  total_available: number;
}

export interface BookingFormData {
  client_name: string;
  client_email: string;
  client_phone?: string;
  client_company?: string;
  service_type: string;
  title: string;
  description?: string;
  scheduled_at: string;
  duration_minutes: number;
  timezone: string;
  meeting_provider: string;
  client_notes?: string;
}

export interface Booking {
  id: number;
  client_name: string;
  client_email: string;
  client_phone?: string;
  client_company?: string;
  service_type: string;
  title: string;
  description?: string;
  scheduled_at: string;
  duration_minutes: number;
  timezone: string;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  meeting_provider: string;
  meeting_url?: string;
  meeting_id?: string;
  reminder_sent: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookingResponse {
  booking: Booking;
  message: string;
}

export type ServiceType = 
  | 'consultation'
  | 'demo'
  | 'technical_support'
  | 'training'
  | 'discovery_call';

export type MeetingProvider = 
  | 'google_meet'
  | 'zoom'
  | 'teams'
  | 'whereby'
  | 'jitsi';

export const SERVICE_TYPES: Record<ServiceType, string> = {
  consultation: 'Consulenza',
  demo: 'Demo Prodotto',
  technical_support: 'Supporto Tecnico',
  training: 'Formazione',
  discovery_call: 'Discovery Call',
};

export const MEETING_PROVIDERS: Record<MeetingProvider, string> = {
  google_meet: 'Google Meet',
  zoom: 'Zoom',
  teams: 'Microsoft Teams',
  whereby: 'Whereby',
  jitsi: 'Jitsi Meet',
};
