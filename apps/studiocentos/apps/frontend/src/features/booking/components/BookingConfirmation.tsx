/**
 * BookingConfirmation - Conferma prenotazione avvenuta
 */

import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { Calendar, Clock, Mail } from 'lucide-react';
import type { Booking } from '../types/booking.types';

interface BookingConfirmationProps {
  booking: Booking;
  onClose?: () => void;
}

export function BookingConfirmation({ booking, onClose }: BookingConfirmationProps) {
  const scheduledDate = new Date(booking.scheduled_at);

  return (
    <Card className="border-gold/20 bg-gold/10">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-gold">
          <span className="text-2xl">✅</span>
          Prenotazione confermata!
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-muted-foreground">
          La tua prenotazione è stata confermata con successo. Riceverai una email di conferma
          all'indirizzo <strong>{booking.client_email}</strong> con tutti i dettagli.
        </p>

        <div className="space-y-3 p-4 bg-white rounded-lg border">
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
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-muted-foreground mt-0.5" />
            <div>
              <div className="font-semibold">Orario</div>
              <div className="text-sm text-muted-foreground">
                {scheduledDate.toLocaleTimeString('it-IT', {
                  hour: '2-digit',
                  minute: '2-digit',
                })} ({booking.duration_minutes} minuti)
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-xl">🎥</span>
            <div>
              <div className="font-semibold">Piattaforma</div>
              <div className="text-sm text-muted-foreground">
                {booking.meeting_provider.replace('_', ' ')}
              </div>
              {booking.meeting_url && (
                <a
                  href={booking.meeting_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gold hover:underline"
                >
                  Link meeting →
                </a>
              )}
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Mail className="w-5 h-5 text-muted-foreground mt-0.5" />
            <div>
              <div className="font-semibold">Email di conferma</div>
              <div className="text-sm text-muted-foreground">
                Inviata a {booking.client_email}
              </div>
            </div>
          </div>
        </div>

        <div className="p-4 bg-gold/10 border border-gold/30 rounded-lg">
          <p className="text-sm text-foreground">
            <strong>📧 Promemoria:</strong> Riceverai un'email di promemoria 24 ore prima
            dell'appuntamento con il link per accedere al meeting.
          </p>
        </div>

        {onClose && (
          <Button onClick={onClose} className="w-full">
            Chiudi
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
