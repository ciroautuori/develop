/**
 * Calendar - API REALI NO MOCK
 * LIGHT MODE SUPPORT
 */
import { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, X } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { CalendarGrid } from '../components/CalendarGrid';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';

export function CalendarView() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedBooking, setSelectedBooking] = useState<any>(null);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Dynamic classes based on theme
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const modalBg = isDark ? 'bg-[#0a0a0a] border-white/10' : 'bg-white border-gray-200';
  const hoverBg = isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100';

  // API REALI
  const { data: bookings, isLoading } = useQuery({
    queryKey: ['calendar', currentDate.getFullYear(), currentDate.getMonth() + 1],
    queryFn: async () => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(
        `/api/v1/admin/bookings/calendar/month?year=${currentDate.getFullYear()}&month=${currentDate.getMonth() + 1}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      return res.json();
    },
  });

  const monthName = currentDate.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' });

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
            <CalendarIcon className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
              Calendario
            </h1>
            <p className="text-sm text-muted-foreground">
              Gestisci prenotazioni e disponibilità
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-4 self-start sm:self-center w-full sm:w-auto justify-between sm:justify-end">
          <button
            onClick={prevMonth}
            className={`p-2 rounded-lg transition ${hoverBg} ${textPrimary}`}
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className={`text-base sm:text-lg lg:text-xl font-semibold capitalize min-w-[140px] text-center ${textPrimary}`}>{monthName}</span>
          <button
            onClick={nextMonth}
            className={`p-2 rounded-lg transition ${hoverBg} ${textPrimary}`}
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </motion.div>

      {/* Stats - Mobile First */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-3 sm:p-4 md:p-6`}>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-1 sm:mb-2">
              <CalendarIcon className="h-4 w-4 sm:h-5 sm:w-5 text-gold" />
              <p className={`text-xs sm:text-sm ${textSecondary}`}>Prenotazioni</p>
            </div>
            <p className={`text-xl sm:text-2xl lg:text-3xl font-bold ${textPrimary}`}>{bookings?.total_bookings || 0}</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-3 sm:p-4 md:p-6`}>
            <p className={`text-xs sm:text-sm mb-1 sm:mb-2 ${textSecondary}`}>Confermate</p>
            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gold">{bookings?.confirmed || 0}</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-3 sm:p-4 md:p-6`}>
            <p className={`text-xs sm:text-sm mb-1 sm:mb-2 ${textSecondary}`}>In Attesa</p>
            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gold">{bookings?.pending || 0}</p>
          </div>
        </motion.div>
      </div>

      {/* Calendar Grid - Mobile First */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
        <h2 className={`text-lg sm:text-xl lg:text-2xl font-semibold mb-4 sm:mb-6 ${textPrimary}`}>Vista Calendario</h2>
        {isLoading ? (
          <div className="h-64 sm:h-80 lg:h-96 flex items-center justify-center">
            <div className="loading-dots"></div>
          </div>
        ) : bookings?.days?.length > 0 ? (
          <CalendarGrid
            days={bookings.days}
            onBookingClick={(booking) => setSelectedBooking(booking)}
          />
        ) : (
          <div className={`h-64 sm:h-80 lg:h-96 flex items-center justify-center text-sm sm:text-base ${textSecondary}`}>
            Nessuna prenotazione questo mese
          </div>
        )}
      </div>

      {/* Booking Detail Modal */}
      <AnimatePresence>
        {selectedBooking && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedBooking(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className={`${modalBg} border rounded-2xl p-6 max-w-md w-full shadow-xl`}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className={`text-xl font-bold ${textPrimary}`}>Dettaglio Prenotazione</h3>
                <button
                  onClick={() => setSelectedBooking(null)}
                  className={`p-2 rounded-lg transition ${hoverBg}`}
                >
                  <X className={`h-5 w-5 ${textSecondary}`} />
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <p className={`text-sm ${textSecondary}`}>Cliente</p>
                  <p className={textPrimary}>{selectedBooking.client_name || selectedBooking.user_email || 'N/A'}</p>
                </div>
                <div>
                  <p className={`text-sm ${textSecondary}`}>Servizio</p>
                  <p className={textPrimary}>{selectedBooking.service_name || selectedBooking.title || 'N/A'}</p>
                </div>
                <div>
                  <p className={`text-sm ${textSecondary}`}>Data e Ora</p>
                  <p className={textPrimary}>
                    {selectedBooking.start_time
                      ? new Date(selectedBooking.start_time).toLocaleString('it-IT')
                      : selectedBooking.date || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className={`text-sm ${textSecondary}`}>Stato</p>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm ${selectedBooking.status === 'confirmed' ? 'bg-gold/20 text-gold' :
                      selectedBooking.status === 'pending' ? 'bg-gold/20 text-gold' :
                        selectedBooking.status === 'cancelled' ? 'bg-gray-500/20 text-gray-400' :
                          isDark ? 'bg-gray-500/20 text-gray-400' : 'bg-gray-200 text-gray-600'
                    }`}>
                    {selectedBooking.status === 'confirmed' ? 'Confermato' :
                      selectedBooking.status === 'pending' ? 'In Attesa' :
                        selectedBooking.status === 'cancelled' ? 'Cancellato' :
                          selectedBooking.status || 'N/A'}
                  </span>
                </div>
                {selectedBooking.notes && (
                  <div>
                    <p className={`text-sm ${textSecondary}`}>Note</p>
                    <p className={textPrimary}>{selectedBooking.notes}</p>
                  </div>
                )}
              </div>

              <div className="flex gap-2 mt-6">
                <button
                  onClick={() => {
                    setSelectedBooking(null);
                    toast.success('Dettagli prenotazione visualizzati');
                  }}
                  className="flex-1 px-4 py-2 bg-gold text-black rounded-lg hover:bg-gold/90 transition font-medium"
                >
                  Chiudi
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
