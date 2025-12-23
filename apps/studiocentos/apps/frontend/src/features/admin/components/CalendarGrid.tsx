/**
 * Calendar Grid Component - Griglia calendario mensile
 * LIGHT MODE SUPPORT
 */
import { useTheme } from '../../../shared/contexts/ThemeContext';

interface CalendarDay {
  date: string;
  bookings: any[];
  is_blocked: boolean;
}

interface CalendarGridProps {
  days: CalendarDay[];
  onBookingClick: (booking: any) => void;
}

export function CalendarGrid({ days, onBookingClick }: CalendarGridProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const weekDays = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];
  const weekDaysMobile = ['L', 'M', 'M', 'G', 'V', 'S', 'D'];

  // Dynamic classes based on theme
  const gridBg = isDark ? 'bg-[#0a0a0a] border-white/10' : 'bg-white border-gray-200';
  const headerBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-100 border-gray-200';
  const headerText = isDark ? 'text-gray-400' : 'text-gray-600';
  const cellBg = isDark ? 'bg-[#0a0a0a]' : 'bg-white';
  const cellHover = isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50';
  const cellBorder = isDark ? 'border-white/10' : 'border-gray-200';
  const blockedBg = isDark ? 'bg-white/5' : 'bg-gray-100';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-gold/10 text-gold border-gold/20';
      case 'pending':
        return 'bg-gold/10 text-gold border-gold/20';
      case 'cancelled':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
      case 'completed':
        return 'bg-gold/10 text-gold border-gold/20';
      default:
        return isDark ? 'bg-gray-500/10 text-gray-400 border-gray-500/20' : 'bg-gray-200 text-gray-600 border-gray-300';
    }
  };

  return (
    <div className={`overflow-hidden rounded-lg border shadow-lg ${gridBg}`}>
      {/* Week Days Header */}
      <div className={`grid grid-cols-7 border-b ${headerBg}`}>
        {weekDays.map((day, index) => (
          <div
            key={day}
            className={`border-r p-2 sm:p-3 text-center text-xs sm:text-sm font-medium last:border-r-0 ${cellBorder} ${headerText}`}
          >
            {/* Mobile: lettere singole, Desktop: nomi completi */}
            <span className="sm:hidden">{weekDaysMobile[index]}</span>
            <span className="hidden sm:inline">{day}</span>
          </div>
        ))}
      </div>

      {/* Calendar Days Grid */}
      <div className="grid grid-cols-7">
        {days.map((day) => {
          const date = new Date(day.date);
          const dayNumber = date.getDate();
          const isToday = new Date().toDateString() === date.toDateString();

          return (
            <div
              key={day.date}
              className={`min-h-[80px] sm:min-h-[120px] border-b border-r p-1 sm:p-2 last:border-r-0 transition-colors ${cellBorder} ${
                day.is_blocked ? blockedBg : `${cellBg} ${cellHover}`
              }`}
            >
              {/* Day Number - MOBILE FIRST */}
              <div className="mb-1 sm:mb-2 flex items-center justify-between">
                <span
                  className={`flex h-5 w-5 sm:h-6 sm:w-6 items-center justify-center rounded-full text-xs sm:text-sm font-medium ${
                    isToday
                      ? 'bg-[#D4AF37] text-black shadow-sm'
                      : textPrimary
                  }`}
                >
                  {dayNumber}
                </span>
                {day.bookings.length > 0 && (
                  <span className={`text-[10px] sm:text-xs ${textSecondary}`}>
                    {day.bookings.length}
                  </span>
                )}
              </div>

              {/* Blocked Indicator */}
              {day.is_blocked && (
                <div className="mb-1 sm:mb-2 rounded-lg bg-gray-500/10 border border-gray-500/20 px-1 sm:px-2 py-0.5 sm:py-1 text-[10px] sm:text-xs text-gray-400 shadow-sm">
                  <span className="sm:hidden">🚫</span>
                  <span className="hidden sm:inline">Bloccato</span>
                </div>
              )}

              {/* Bookings - MOBILE FIRST */}
              <div className="space-y-0.5 sm:space-y-1">
                {day.bookings.slice(0, typeof window !== 'undefined' && window.innerWidth < 640 ? 1 : 3).map((booking) => (
                  <button
                    key={booking.id}
                    onClick={() => onBookingClick(booking)}
                    className={`w-full rounded-lg border px-1 sm:px-2 py-0.5 sm:py-1 text-left text-[10px] sm:text-xs transition-all hover:scale-105 active:scale-95 touch-manipulation ${getStatusColor(
                      booking.status
                    )}`}
                  >
                    <div className="truncate font-medium">{booking.client_name}</div>
                    <div className="truncate text-[8px] sm:text-[10px] hidden sm:block">
                      {new Date(booking.scheduled_at).toLocaleTimeString('it-IT', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </button>
                ))}
                {day.bookings.length > (typeof window !== 'undefined' && window.innerWidth < 640 ? 1 : 3) && (
                  <div className={`text-center text-[10px] sm:text-xs ${textSecondary}`}>
                    +{day.bookings.length - (typeof window !== 'undefined' && window.innerWidth < 640 ? 1 : 3)} altri
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
