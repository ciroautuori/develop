/**
 * BookingSummary - Riepilogo prenotazione prima della conferma
 */

import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Calendar, Clock, User, Mail } from 'lucide-react';
import type { BookingFormData } from '../types/booking.types';
import { SERVICE_TYPES, MEETING_PROVIDERS } from '../types/booking.types';

interface BookingSummaryProps {
  bookingData: Partial<BookingFormData>;
}

export function BookingSummary({ bookingData }: BookingSummaryProps) {
  if (!bookingData.scheduled_at) {
    return null;
  }

  const scheduledDate = new Date(bookingData.scheduled_at);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Riepilogo prenotazione</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <Calendar className="w-5 h-5 text-muted-foreground mt-0.5" />
            <div>
              <div className="font-semibold">Data e ora</div>
              <div className="text-sm text-muted-foreground">
                {scheduledDate.toLocaleDateString('it-IT', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                })}
                {' alle '}
                {scheduledDate.toLocaleTimeString('it-IT', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-muted-foreground mt-0.5" />
            <div>
              <div className="font-semibold">Durata</div>
              <div className="text-sm text-muted-foreground">
                {bookingData.duration_minutes} minuti
              </div>
            </div>
          </div>

          {bookingData.service_type && (
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 mt-0.5">📋</div>
              <div>
                <div className="font-semibold">Tipo di servizio</div>
                <div className="text-sm text-muted-foreground">
                  {SERVICE_TYPES[bookingData.service_type as keyof typeof SERVICE_TYPES]}
                </div>
              </div>
            </div>
          )}

          {bookingData.client_name && (
            <div className="flex items-start gap-3">
              <User className="w-5 h-5 text-muted-foreground mt-0.5" />
              <div>
                <div className="font-semibold">Nome</div>
                <div className="text-sm text-muted-foreground">
                  {bookingData.client_name}
                </div>
              </div>
            </div>
          )}

          {bookingData.client_email && (
            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-muted-foreground mt-0.5" />
              <div>
                <div className="font-semibold">Email</div>
                <div className="text-sm text-muted-foreground">
                  {bookingData.client_email}
                </div>
              </div>
            </div>
          )}

          {bookingData.meeting_provider && (
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 mt-0.5">🎥</div>
              <div>
                <div className="font-semibold">Piattaforma meeting</div>
                <div className="text-sm text-muted-foreground">
                  {MEETING_PROVIDERS[bookingData.meeting_provider as keyof typeof MEETING_PROVIDERS]}
                </div>
              </div>
            </div>
          )}

          {bookingData.description && (
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 mt-0.5">📝</div>
              <div>
                <div className="font-semibold">Descrizione</div>
                <div className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {bookingData.description}
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
