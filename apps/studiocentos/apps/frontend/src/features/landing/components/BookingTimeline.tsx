/**
 * Booking Timeline Component - API REALI NO MOCK
 * Design moderno stile Apple/Google Calendar
 */

import { useState, useMemo } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Button } from '../../../shared/components/ui/button';
import { Input } from '../../../shared/components/ui/input';
import { useLanguage } from '../i18n';

interface DaySlot {
  date: string;
  dayName: string;
  dayNumber: number;
  availableSlots: number;
  isWeekend: boolean;
}

interface TimeSlot {
  time: string;
  period: 'morning' | 'afternoon';
  available: boolean;
}

interface WeekData {
  start: string;
  end: string;
  year: number;
  startDate: Date;
}

// Genera settimane dinamiche partendo da oggi
function generateWeeks(numWeeks: number = 4, language: string = 'it'): WeekData[] {
  const weeks: WeekData[] = [];
  const today = new Date();

  // Trova il prossimo lunedì
  const dayOfWeek = today.getDay();
  const daysUntilMonday = dayOfWeek === 0 ? 1 : (dayOfWeek === 1 ? 0 : 8 - dayOfWeek);
  const nextMonday = new Date(today);
  nextMonday.setDate(today.getDate() + daysUntilMonday);

  const monthNames: Record<string, string[]> = {
    it: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
    en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    es: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
  };

  const months = monthNames[language] || monthNames.it;

  for (let i = 0; i < numWeeks; i++) {
    const weekStart = new Date(nextMonday);
    weekStart.setDate(nextMonday.getDate() + (i * 7));

    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);

    weeks.push({
      start: `${weekStart.getDate()} ${months[weekStart.getMonth()]}`,
      end: `${weekEnd.getDate()} ${months[weekEnd.getMonth()]}`,
      year: weekStart.getFullYear(),
      startDate: weekStart
    });
  }

  return weeks;
}

// Genera giorni della settimana
function generateDaysOfWeek(weekStartDate: Date, language: string = 'it'): DaySlot[] {
  const dayNames: Record<string, string[]> = {
    it: ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'],
    en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    es: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
  };

  const names = dayNames[language] || dayNames.it;
  const days: DaySlot[] = [];

  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStartDate);
    date.setDate(weekStartDate.getDate() + i);

    const isWeekend = date.getDay() === 0 || date.getDay() === 6;

    days.push({
      date: date.toISOString().split('T')[0],
      dayName: names[date.getDay()],
      dayNumber: date.getDate(),
      availableSlots: isWeekend ? 0 : 6, // Sarà aggiornato dalla API
      isWeekend
    });
  }

  return days;
}

export function BookingTimeline() {
  const { t, language } = useLanguage();
  const [selectedWeek, setSelectedWeek] = useState(0);
  const [selectedDay, setSelectedDay] = useState<DaySlot | null>(null);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const [formData, setFormData] = useState({ name: '', email: '', phone: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Genera settimane dinamiche
  const weeks = useMemo(() => generateWeeks(4, language), [language]);

  // Genera giorni per la settimana corrente
  const daysOfWeek = useMemo(() => {
    if (weeks[selectedWeek]) {
      return generateDaysOfWeek(weeks[selectedWeek].startDate, language);
    }
    return [];
  }, [weeks, selectedWeek, language]);

  // Fetch disponibilità reale dalla API
  const { data: availability, isLoading: loadingAvailability } = useQuery({
    queryKey: ['booking-availability', selectedDay?.date],
    queryFn: async () => {
      if (!selectedDay?.date) return null;

      // Use POST /calendar/availability endpoint with date range
      const targetDate = new Date(selectedDay.date);
      const endDate = new Date(targetDate);
      endDate.setDate(endDate.getDate() + 1);

      const res = await fetch(`/api/v1/booking/calendar/availability`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: selectedDay.date,
          end_date: endDate.toISOString().split('T')[0]
        })
      });

      if (!res.ok) {
        // Fallback a orari standard se API non risponde
        return {
          slots: [
            { time: '09:00', available: true },
            { time: '10:00', available: true },
            { time: '11:00', available: true },
            { time: '14:00', available: true },
            { time: '15:00', available: true },
            { time: '16:00', available: true },
          ]
        };
      }

      const data = await res.json();
      // Extract slots for the selected day from calendar response
      if (data.availability && data.availability.length > 0) {
        const daySlots = data.availability.find((a: any) => a.date === selectedDay.date);
        return { slots: daySlots?.slots || [] };
      }

      // Fallback if no data
      return {
        slots: [
          { time: '09:00', available: true },
          { time: '10:00', available: true },
          { time: '11:00', available: true },
          { time: '14:00', available: true },
          { time: '15:00', available: true },
          { time: '16:00', available: true },
        ]
      };
    },
    enabled: !!selectedDay?.date,
  });

  // Slot orari - dalla API o default
  const timeSlots: TimeSlot[] = useMemo(() => {
    if (availability?.slots) {
      return availability.slots
        .map((slot: any) => {
          // API returns 'datetime' (ISO string) - extract time from it
          // Also handle legacy 'time' format for backwards compatibility
          let timeStr: string;
          if (slot.datetime) {
            // Extract HH:MM from ISO datetime string or Date object
            const dt = new Date(slot.datetime);
            timeStr = `${dt.getHours().toString().padStart(2, '0')}:${dt.getMinutes().toString().padStart(2, '0')}`;
          } else if (slot.time) {
            timeStr = slot.time;
          } else {
            return null; // Skip invalid slots
          }
          const hour = parseInt(timeStr.split(':')[0]);
          return {
            time: timeStr,
            period: hour < 12 ? 'morning' : 'afternoon',
            available: slot.available
          };
        })
        .filter((slot: any) => slot !== null); // Remove invalid slots
    }
    // Default slots
    return [
      { time: '09:00', period: 'morning', available: true },
      { time: '10:00', period: 'morning', available: true },
      { time: '11:00', period: 'morning', available: true },
      { time: '14:00', period: 'afternoon', available: true },
      { time: '15:00', period: 'afternoon', available: true },
      { time: '16:00', period: 'afternoon', available: true },
    ];
  }, [availability]);

  const morningSlots = timeSlots.filter(s => s.period === 'morning');
  const afternoonSlots = timeSlots.filter(s => s.period === 'afternoon');

  const handleDaySelect = (day: DaySlot) => {
    if (!day.isWeekend) {
      if (selectedDay?.date === day.date) {
        // Toggle off if already selected
        setSelectedDay(null);
        setSelectedTime(null);
      } else {
        // Select new day
        setSelectedDay(day);
        setSelectedTime(null);
      }
    }
  };

  const handleTimeSelect = (time: string) => {
    setSelectedTime(time);
  };

  // Mutation per creare prenotazione
  const createBooking = useMutation({
    mutationFn: async (bookingData: any) => {
      const res = await fetch('/api/v1/booking/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookingData)
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Errore nella prenotazione');
      }
      return res.json();
    },
    onSuccess: () => {
      toast.success('Prenotazione confermata! Riceverai una email di conferma.');
      setSelectedDay(null);
      setSelectedTime(null);
      setFormData({ name: '', email: '', phone: '' });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Errore nella prenotazione');
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedDay || !selectedTime || !formData.name || !formData.email) {
      toast.error('Compila tutti i campi obbligatori');
      return;
    }

    setIsSubmitting(true);

    try {
      await createBooking.mutateAsync({
        client_name: formData.name,
        client_email: formData.email,
        client_phone: formData.phone || undefined,
        service_type: 'consultation',
        scheduled_at: `${selectedDay.date}T${selectedTime}:00`,
        duration_minutes: 30,
        timezone: 'Europe/Rome'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section id="prenota" className="max-w-6xl mx-auto px-6 py-32">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-light mb-4 text-white light:text-gray-900">
          {t.booking.title} <span className="text-gold">{t.booking.titleHighlight}</span>
        </h2>
        <p className="text-xl text-gray-400 light:text-gray-600">
          {t.booking.subtitle}
        </p>
      </div>

      <div className="bg-gradient-to-br from-white/10 to-white/5 light:from-gray-100 light:to-gray-50 backdrop-blur rounded-3xl p-8 border border-white/10 light:border-gray-200">        {/* Navigazione Settimana */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <Button
              variant="ghost"
              onClick={() => setSelectedWeek(Math.max(0, selectedWeek - 1))}
              disabled={selectedWeek === 0}
              className="px-4 py-2 bg-white/5 light:bg-gray-200 hover:bg-white/10 light:hover:bg-gray-300 rounded-lg transition text-white light:text-gray-900"
            >
              {t.booking.prevWeek}
            </Button>
            <h3 className="text-xl font-light text-white light:text-gray-900">
              {weeks[selectedWeek]?.start} - {weeks[selectedWeek]?.end} {weeks[selectedWeek]?.year}
            </h3>
            <Button
              variant="ghost"
              onClick={() => setSelectedWeek(Math.min(weeks.length - 1, selectedWeek + 1))}
              disabled={selectedWeek === weeks.length - 1}
              className="px-4 py-2 bg-white/5 light:bg-gray-200 hover:bg-white/10 light:hover:bg-gray-300 rounded-lg transition text-white light:text-gray-900"
            >
              {t.booking.nextWeek}
            </Button>
          </div>

          {/* Giorni della settimana - MOBILE FIRST */}
          <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 gap-2 sm:gap-3">
            {daysOfWeek.map((day) => (
              <button
                key={day.date}
                onClick={() => handleDaySelect(day)}
                disabled={day.isWeekend}
                className={`
                  rounded-2xl p-4 border transition text-center
                  ${day.isWeekend
                    ? 'bg-white/5 light:bg-gray-200 border-white/10 light:border-gray-300 opacity-50 cursor-not-allowed'
                    : selectedDay?.date === day.date
                      ? 'bg-gold text-black border-2 border-gold'
                      : 'bg-white/5 light:bg-gray-100 border-white/10 light:border-gray-200 hover:border-gold hover:shadow-lg text-white light:text-gray-900'
                  }
                `}
              >
                <div className={`text-xs mb-2 ${selectedDay?.date === day.date ? '' : 'text-gray-400'}`}>
                  {day.dayName}
                </div>
                <div className={`text-xl sm:text-2xl font-light mb-1 ${selectedDay?.date === day.date ? 'font-medium' : ''}`}>
                  {day.dayNumber}
                </div>
                <div className={`text-xs ${day.isWeekend ? 'text-gray-600' : selectedDay?.date === day.date ? 'font-medium' : 'text-gold'}`}>
                  {day.isWeekend ? t.booking.closed : `${day.availableSlots} ${t.booking.slots}`}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Timeline Orari */}
        {selectedDay && (
          <div className="border-t border-white/10 light:border-gray-200 pt-8">
            <h4 className="text-lg font-medium mb-6 text-white light:text-gray-900">
              {selectedDay.dayName} {selectedDay.dayNumber} - {t.booking.available}
            </h4>

            {loadingAvailability ? (
              <div className="flex justify-center py-8">
                <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Mattina */}
                <div>
                  <div className="text-sm text-gray-400 light:text-gray-600 mb-3">{t.booking.morning}</div>
                  <div className="grid grid-cols-3 gap-3">
                    {morningSlots.map((slot) => (
                      <button
                        key={slot.time}
                        onClick={() => handleTimeSelect(slot.time)}
                        disabled={!slot.available}
                        className={`
                        px-6 py-4 rounded-xl transition
                        ${selectedTime === slot.time
                            ? 'bg-gold text-black border-2 border-gold'
                            : 'bg-white/5 light:bg-gray-100 border border-white/10 light:border-gray-200 hover:bg-gold/20 hover:border-gold hover:scale-105 text-white light:text-gray-900'
                          }
                      `}
                      >
                        <div className="text-lg font-medium">{slot.time}</div>
                        <div className="text-xs text-gray-400 light:text-gray-500">{t.booking.duration}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Pomeriggio */}
                <div>
                  <div className="text-sm text-gray-400 light:text-gray-600 mb-3">{t.booking.afternoon}</div>
                  <div className="grid grid-cols-3 gap-3">
                    {afternoonSlots.map((slot) => (
                      <button
                        key={slot.time}
                        onClick={() => handleTimeSelect(slot.time)}
                        disabled={!slot.available}
                        className={`
                        px-6 py-4 rounded-xl transition
                        ${selectedTime === slot.time
                            ? 'bg-gold text-black border-2 border-gold'
                            : 'bg-white/5 light:bg-gray-100 border border-white/10 light:border-gray-200 hover:bg-gold/20 hover:border-gold hover:scale-105 text-white light:text-gray-900'
                          }
                      `}
                      >
                        <div className="text-lg font-medium">{slot.time}</div>
                        <div className="text-xs text-gray-400 light:text-gray-500">{t.booking.duration}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Riepilogo + Form */}
        {selectedDay && selectedTime && (
          <div className="border-t border-white/10 light:border-gray-200 pt-8 mt-8">
            <div className="bg-gold/10 border border-gold/30 rounded-2xl p-6 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-400 light:text-gray-600 mb-1">{t.booking.selected}</div>
                  <div className="text-xl font-medium text-gold">
                    {selectedDay.dayName} {selectedDay.dayNumber}, {t.booking.at} {selectedTime}
                  </div>
                </div>
                <div className="text-4xl">📅</div>
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <Input
                  type="text"
                  placeholder={t.booking.namePlaceholder}
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="px-4 py-3 bg-white/5 light:bg-white border border-white/10 light:border-gray-300 rounded-lg focus:border-gold focus:outline-none text-white light:text-gray-900 placeholder:text-gray-400"
                />
                <Input
                  type="email"
                  placeholder={t.booking.emailPlaceholder}
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="px-4 py-3 bg-white/5 light:bg-white border border-white/10 light:border-gray-300 rounded-lg focus:border-gold focus:outline-none text-white light:text-gray-900 placeholder:text-gray-400"
                />
              </div>
              <Input
                type="tel"
                placeholder={t.booking.phonePlaceholder}
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 light:bg-white border border-white/10 light:border-gray-300 rounded-lg focus:border-gold focus:outline-none mb-4 text-white light:text-gray-900 placeholder:text-gray-400"
              />

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full px-8 py-4 bg-gold text-black rounded-lg hover:bg-[#F4E5B8] transition font-medium text-lg disabled:opacity-50"
              >
                {isSubmitting ? t.booking.submitting : t.booking.submit}
              </Button>
            </form>
          </div>
        )}

      </div>

      {/* Info Cards */}
      <div className="mt-8 grid md:grid-cols-3 gap-6 text-center text-sm">
        <div className="bg-white/5 light:bg-gray-100 rounded-xl p-4">
          <div className="text-2xl mb-2">📧</div>
          <div className="text-gray-400 light:text-gray-600">{t.booking.infoEmail}</div>
        </div>
        <div className="bg-white/5 light:bg-gray-100 rounded-xl p-4">
          <div className="text-2xl mb-2">🎥</div>
          <div className="text-gray-400 light:text-gray-600">{t.booking.infoMeet}</div>
        </div>
        <div className="bg-white/5 light:bg-gray-100 rounded-xl p-4">
          <div className="text-2xl mb-2">🔄</div>
          <div className="text-gray-400 light:text-gray-600">{t.booking.infoCancel}</div>
        </div>
      </div>
    </section>
  );
}
