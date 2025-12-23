/**
 * BookingForm - Form completo per creare prenotazione
 * API REALI NO MOCK
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { Input } from '../../../shared/components/ui/input';
import { Label } from '../../../shared/components/ui/label';
import { Textarea } from '../../../shared/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../shared/components/ui/select';
import { Calendar, User, Mail, Phone, Building2, FileText } from 'lucide-react';
import { useBooking } from '../hooks/useBooking';
import type { BookingFormData, ServiceType, MeetingProvider, Booking } from '../types/booking.types';
import { SERVICE_TYPES, MEETING_PROVIDERS } from '../types/booking.types';

interface BookingFormProps {
  selectedDatetime?: string;
  selectedDuration?: number;
  onSuccess?: (booking: Booking) => void;
  onCancel?: () => void;
}

export function BookingForm({
  selectedDatetime,
  selectedDuration = 30,
  onSuccess,
  onCancel
}: BookingFormProps) {
  const { createBooking, loading, error } = useBooking();

  const [formData, setFormData] = useState<Partial<BookingFormData>>({
    service_type: 'consultation',
    duration_minutes: selectedDuration,
    timezone: 'Europe/Rome',
    meeting_provider: 'google_meet',
    scheduled_at: selectedDatetime,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.client_name || !formData.client_email || !formData.scheduled_at) {
      return;
    }

    try {
      const response = await createBooking(formData as BookingFormData);
      // Extract booking from response
      const result = response.booking;
      // Passa la booking reale dalla API
      const booking: Booking = {
        id: result.id,
        client_name: formData.client_name,
        client_email: formData.client_email,
        client_phone: formData.client_phone,
        service_type: formData.service_type || 'consultation',
        title: result.title || `Prenotazione ${formData.service_type}`,
        scheduled_at: formData.scheduled_at,
        duration_minutes: formData.duration_minutes || 30,
        timezone: formData.timezone || 'Europe/Rome',
        status: result.status || 'confirmed',
        meeting_provider: formData.meeting_provider || 'google_meet',
        meeting_url: result.meeting_url,
        reminder_sent: false,
        created_at: result.created_at || new Date().toISOString(),
        updated_at: result.updated_at || new Date().toISOString(),
      };
      onSuccess?.(booking);
    } catch (err) {
      // Error già gestito da useBooking
    }
  };

  const updateField = (field: keyof BookingFormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          Completa la prenotazione
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nome */}
          <div className="space-y-2">
            <Label htmlFor="client_name" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              Nome completo *
            </Label>
            <Input
              id="client_name"
              required
              value={formData.client_name || ''}
              onChange={(e) => updateField('client_name', e.target.value)}
              placeholder="Mario Rossi"
            />
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="client_email" className="flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Email *
            </Label>
            <Input
              id="client_email"
              type="email"
              required
              value={formData.client_email || ''}
              onChange={(e) => updateField('client_email', e.target.value)}
              placeholder="mario.rossi@example.com"
            />
          </div>

          {/* Telefono */}
          <div className="space-y-2">
            <Label htmlFor="client_phone" className="flex items-center gap-2">
              <Phone className="w-4 h-4" />
              Telefono
            </Label>
            <Input
              id="client_phone"
              type="tel"
              value={formData.client_phone || ''}
              onChange={(e) => updateField('client_phone', e.target.value)}
              placeholder="+39 123 456 7890"
            />
          </div>

          {/* Azienda */}
          <div className="space-y-2">
            <Label htmlFor="client_company" className="flex items-center gap-2">
              <Building2 className="w-4 h-4" />
              Azienda
            </Label>
            <Input
              id="client_company"
              value={formData.client_company || ''}
              onChange={(e) => updateField('client_company', e.target.value)}
              placeholder="Nome azienda"
            />
          </div>

          {/* Tipo servizio */}
          <div className="space-y-2">
            <Label htmlFor="service_type">Tipo di servizio *</Label>
            <Select
              value={formData.service_type}
              onValueChange={(value) => updateField('service_type', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(SERVICE_TYPES).map(([key, label]) => (
                  <SelectItem key={key} value={key}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Titolo */}
          <div className="space-y-2">
            <Label htmlFor="title">Oggetto *</Label>
            <Input
              id="title"
              required
              value={formData.title || ''}
              onChange={(e) => updateField('title', e.target.value)}
              placeholder="Consulenza per nuovo progetto"
            />
          </div>

          {/* Descrizione */}
          <div className="space-y-2">
            <Label htmlFor="description" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Descrizione
            </Label>
            <Textarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Descrivi brevemente di cosa vorresti parlare..."
              rows={4}
            />
          </div>

          {/* Meeting provider */}
          <div className="space-y-2">
            <Label htmlFor="meeting_provider">Piattaforma meeting *</Label>
            <Select
              value={formData.meeting_provider}
              onValueChange={(value) => updateField('meeting_provider', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(MEETING_PROVIDERS).map(([key, label]) => (
                  <SelectItem key={key} value={key}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Note cliente */}
          <div className="space-y-2">
            <Label htmlFor="client_notes">Note aggiuntive</Label>
            <Textarea
              id="client_notes"
              value={formData.client_notes || ''}
              onChange={(e) => updateField('client_notes', e.target.value)}
              placeholder="Eventuali richieste particolari..."
              rows={3}
            />
          </div>

          {/* Error message */}
          {error && (
            <div className="p-3 bg-gray-50 border border-gray-300 rounded-md text-gray-500 text-sm">
              {error.message}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Prenotazione in corso...' : 'Conferma prenotazione'}
            </Button>
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={loading}
              >
                Annulla
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
