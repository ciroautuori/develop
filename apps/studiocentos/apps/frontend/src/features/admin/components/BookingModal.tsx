/**
 * Booking Modal - Modal per gestire prenotazioni
 * LIGHT MODE SUPPORT - EditorialCalendar Design System
 */
import { useState, useEffect } from 'react';
import { X, Check, XCircle, Calendar, Save, Loader2, Users, Clock, Video, Phone, MapPin } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useConfirmBooking, useCancelBooking, useRescheduleBooking, useCreateBooking, useUpdateBooking } from '../hooks/useBookings';
import { Button } from '../../../shared/components/ui/button';
import { Input } from '../../../shared/components/ui/input';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';

interface BookingModalProps {
  booking?: any;
  onClose: () => void;
  isOpen?: boolean;
  onSuccess?: () => void;
}

export function BookingModal({ booking, onClose, isOpen = true, onSuccess }: BookingModalProps) {
  if (!isOpen) return null;

  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const isEdit = !!booking;

  // Theme classes - EditorialCalendar pattern
  const modalBg = isDark
    ? 'bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a] border border-white/10'
    : 'bg-white border border-gray-200';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-500';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-300 text-gray-900';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const labelText = isDark ? 'text-gray-300' : 'text-gray-700';

  // Service-based smart defaults
  const SERVICE_DEFAULTS = {
    consultation: { duration: 60, requiresMeet: true },
    meeting: { duration: 30, requiresMeet: true },
    demo: { duration: 45, requiresMeet: true },
    support: { duration: 30, requiresMeet: false },
    training: { duration: 120, requiresMeet: true },
    interview: { duration: 60, requiresMeet: true }
  };

  const [formData, setFormData] = useState({
    client_name: '',
    client_email: '',
    client_phone: '',
    title: '',
    service_type: 'consultation',
    scheduled_at: '',
    duration_minutes: 60,
    meeting_provider: 'google_meet', // Backend field for Calendar API
    meeting_url: '', // Will be filled by backend
    admin_notes: ''
  });

  const confirmBooking = useConfirmBooking();
  const cancelBooking = useCancelBooking();
  const rescheduleBooking = useRescheduleBooking();
  const createBooking = useCreateBooking();
  const updateBooking = useUpdateBooking();

  useEffect(() => {
    if (booking) {
      // Converti scheduled_at da datetime ISO a datetime-local format
      let scheduledAtLocal = '';
      if (booking.scheduled_at) {
        const date = new Date(booking.scheduled_at);
        scheduledAtLocal = date.toISOString().slice(0, 16); // YYYY-MM-DDTHH:MM
      }

      setFormData({
        client_name: booking.client_name || '',
        client_email: booking.client_email || '',
        client_phone: booking.client_phone || '',
        title: booking.title || '',
        service_type: booking.service_type || 'consultation',
        scheduled_at: scheduledAtLocal,
        duration_minutes: booking.duration_minutes || 60,
        meeting_provider: booking.meeting_provider || 'google_meet',
        meeting_url: booking.meeting_url || '', // Google Meet link from backend
        admin_notes: booking.admin_notes || ''
      });
    }
  }, [booking]);

  // Smart pre-selection: auto-adjust duration when service_type changes
  const handleServiceTypeChange = (newServiceType: string) => {
    const defaults = SERVICE_DEFAULTS[newServiceType as keyof typeof SERVICE_DEFAULTS];
    setFormData({
      ...formData,
      service_type: newServiceType,
      duration_minutes: defaults?.duration || 60,
      meeting_provider: defaults?.requiresMeet ? 'google_meet' : 'phone'
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Trasforma scheduled_at da datetime-local a ISO datetime
      const payload = {
        ...formData,
        scheduled_at: new Date(formData.scheduled_at).toISOString(),
        // Backend creerà automaticamente Google Calendar event se meeting_provider='google_meet'
      };

      if (isEdit) {
        const result = await updateBooking.mutateAsync({ id: booking.id, data: payload });
        toast.success('✅ Prenotazione aggiornata!');
        if (result?.meeting_url) {
          toast.success(`🎥 Google Meet: ${result.meeting_url}`, { duration: 5000 });
        }
      } else {
        const result = await createBooking.mutateAsync(payload);
        toast.success('✅ Prenotazione creata!');
        if (result?.meeting_url) {
          toast.success(`🎥 Meet creato: ${result.meeting_url}`, { duration: 8000 });
        }
      }
      if (onSuccess) onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving booking:', error);
      toast.error('❌ Errore durante il salvataggio');
    }
  };

  const handleConfirm = async () => {
    try {
      await confirmBooking.mutateAsync(booking.id);
      toast.success('✅ Prenotazione confermata!');
      if (onSuccess) onSuccess();
      onClose();
    } catch (error) {
      console.error('Error confirming booking:', error);
      toast.error('❌ Errore nella conferma');
    }
  };

  const handleCancel = async () => {
    const reason = prompt('Motivo cancellazione:');
    if (!reason) return;

    try {
      await cancelBooking.mutateAsync({ id: booking.id, reason });
      toast.success('✅ Prenotazione cancellata');
      if (onSuccess) onSuccess();
      onClose();
    } catch (error) {
      console.error('Error cancelling booking:', error);
      toast.error('❌ Errore nella cancellazione');
    }
  };

  const handleReschedule = async () => {
    const newDate = prompt('Nuova data/ora (YYYY-MM-DD HH:MM):');
    if (!newDate) return;

    try {
      await rescheduleBooking.mutateAsync({
        id: booking.id,
        scheduled_at: newDate,
        duration_minutes: formData.duration_minutes,
        reason: 'Rescheduled by admin'
      });
      toast.success('✅ Prenotazione rimandata');
      if (onSuccess) onSuccess();
      onClose();
    } catch (error) {
      console.error('Error rescheduling booking:', error);
      toast.error('❌ Errore nella modifica data');
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className={cn(
            "w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl",
            modalBg
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-inherit border-b border-white/10 p-4 sm:p-6 flex items-center justify-between">
            <div>
              <h2 className={`text-xl sm:text-2xl font-bold ${textPrimary}`}>
                {isEdit ? '✏️ Gestisci Prenotazione' : '📅 Nuova Prenotazione'}
              </h2>
              <p className={`text-sm ${textSecondary} mt-1`}>
                {isEdit ? 'Modifica o conferma la prenotazione' : 'Crea una nuova prenotazione'}
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-6">
            {/* Status Badge */}
            {isEdit && (
              <div className="flex items-center gap-2">
                <span className={`text-sm ${labelText}`}>Stato:</span>
                <span
                  className={cn(
                    "px-3 py-1 rounded-full text-xs font-medium",
                    booking.status === 'confirmed' && 'bg-gold/10 text-gold',
                    booking.status === 'pending' && 'bg-gold/10 text-gold',
                    booking.status === 'cancelled' && 'bg-gray-500/10 text-gray-400',
                    booking.status === 'completed' && 'bg-gold/10 text-gold'
                  )}
                >
                  {booking.status.toUpperCase()}
                </span>
              </div>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                  <Users className="inline h-4 w-4 mr-2" />
                  Nome Cliente *
                </label>
                <input
                  type="text"
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                  className={cn("w-full px-4 py-3 rounded-lg border", inputBg)}
                  placeholder="Es: Mario Rossi"
                  required
                />
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                  Email *
                </label>
                <input
                  type="email"
                  value={formData.client_email}
                  onChange={(e) => setFormData({ ...formData, client_email: e.target.value })}
                  className={cn("w-full px-4 py-3 rounded-lg border", inputBg)}
                  placeholder="mario@example.com"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                  <Phone className="inline h-4 w-4 mr-2" />
                  Telefono
                </label>
                <input
                  type="tel"
                  value={formData.client_phone}
                  onChange={(e) => setFormData({ ...formData, client_phone: e.target.value })}
                  className={cn("w-full px-4 py-3 rounded-lg border", inputBg)}
                  placeholder="+39 333 1234567"
                />
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                  Tipo Servizio
                </label>
                <select
                  value={formData.service_type}
                  onChange={(e) => handleServiceTypeChange(e.target.value)}
                  className={cn("w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-[#D4AF37] focus:outline-none", selectBg)}
                >
                  <option value="consultation">💼 Consulenza (60 min)</option>
                  <option value="meeting">🤝 Meeting (30 min)</option>
                  <option value="demo">🎯 Demo (45 min)</option>
                  <option value="support">🛠️ Supporto (30 min)</option>
                  <option value="training">📚 Formazione (2h)</option>
                  <option value="interview">🎤 Colloquio (60 min)</option>
                </select>
                <p className={`text-xs mt-1 ${textSecondary}`}>
                  ✨ Durata e tipo meeting si adattano automaticamente
                </p>
              </div>
            </div>

            {/* Titolo */}
            <div>
              <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                Titolo Appuntamento *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className={cn("w-full px-4 py-3 rounded-lg border", inputBg)}
                placeholder="Es: Consulenza Marketing Strategico"
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                  <Calendar className="inline h-4 w-4 mr-2" />
                  Data/Ora *
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_at}
                  onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
                  className={cn("w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-[#D4AF37] focus:outline-none", inputBg)}
                  required
                />
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                  <Clock className="inline h-4 w-4 mr-2" />
                  Durata (minuti) *
                </label>
                <select
                  value={formData.duration_minutes}
                  onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                  className={cn("w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-[#D4AF37] focus:outline-none", selectBg)}
                  required
                >
                  <option value="15">⚡ 15 minuti</option>
                  <option value="30">📞 30 minuti</option>
                  <option value="60">⏱️ 1 ora</option>
                  <option value="90">🕐 1 ora e 30</option>
                  <option value="120">⏰ 2 ore</option>
                  <option value="180">📅 3 ore</option>
                  <option value="240">🗓️ Mezza giornata (4h)</option>
                  <option value="480">📆 Giornata intera (8h)</option>
                </select>
              </div>
            </div>

            {/* Meeting Provider - GOOGLE CALENDAR/MEET INTEGRATION */}
            <div>
              <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                <Video className="inline h-4 w-4 mr-2" />
                Tipo Meeting *
              </label>
              <select
                value={formData.meeting_provider}
                onChange={(e) => setFormData({ ...formData, meeting_provider: e.target.value })}
                className={cn("w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-[#D4AF37] focus:outline-none", selectBg)}
                required
              >
                <option value="google_meet">🎥 Google Meet (Calendar API)</option>
                <option value="phone">📞 Chiamata Telefonica</option>
                <option value="in_person">🏢 Di Persona</option>
                <option value="zoom">🎬 Zoom (Manuale)</option>
              </select>
              {formData.meeting_provider === 'google_meet' && (
                <p className={`text-xs mt-1 ${textSecondary}`}>
                  ✨ Google Calendar creerà automaticamente evento + Meet link + invito email
                </p>
              )}
            </div>

            {/* Google Meet Link Display (read-only, from backend) */}
            {isEdit && booking?.meeting_url && (
              <div>
                <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                  <Video className="inline h-4 w-4 mr-2" />
                  Link Google Meet
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={booking.meeting_url}
                    readOnly
                    className={cn("flex-1 px-4 py-3 rounded-lg border bg-gray-100 dark:bg-white/5 text-gray-600 dark:text-gray-400")}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      navigator.clipboard.writeText(booking.meeting_url!);
                      toast.success('📋 Link copiato!');
                    }}
                  >
                    📋
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => window.open(booking.meeting_url!, '_blank')}
                  >
                    🚀
                  </Button>
                </div>
                <p className={`text-xs mt-1 text-gold`}>
                  ✅ Google Meet creato via Calendar API
                </p>
              </div>
            )}

            <div>
              <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                Note Admin
              </label>
              <textarea
                value={formData.admin_notes}
                onChange={(e) => setFormData({ ...formData, admin_notes: e.target.value })}
                className={cn("w-full px-4 py-3 rounded-lg border", inputBg)}
                rows={4}
                placeholder="Note interne per admin..."
              />
            </div>

            {/* Actions */}
            <div className="flex flex-wrap gap-3 pt-4 border-t border-white/10">
              {isEdit && booking.status === 'pending' && (
                <>
                  <Button
                    type="button"
                    onClick={handleConfirm}
                    className="bg-gold hover:bg-gold text-white"
                  >
                    <Check className="mr-2 h-4 w-4" />
                    Conferma
                  </Button>
                  <Button
                    type="button"
                    onClick={handleCancel}
                    className="bg-gray-500 hover:bg-gray-500 text-white"
                  >
                    <XCircle className="mr-2 h-4 w-4" />
                    Cancella
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleReschedule}
                  >
                    <Calendar className="mr-2 h-4 w-4" />
                    Reschedule
                  </Button>
                </>
              )}
              <Button
                type="submit"
                disabled={createBooking.isPending || updateBooking.isPending}
                className="bg-[#D4AF37] hover:bg-[#B8963A] text-black"
              >
                {createBooking.isPending || updateBooking.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Salvataggio...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    {isEdit ? 'Aggiorna' : 'Crea'}
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
              >
                Annulla
              </Button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
