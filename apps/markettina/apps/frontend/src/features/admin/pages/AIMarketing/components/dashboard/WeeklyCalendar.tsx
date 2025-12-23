/**
 * WeeklyCalendar - MARKET READY
 * Mini calendario 7 giorni con post schedulati
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronLeft, ChevronRight, Clock, Share2, Mail,
  Video, Loader2, Plus
} from 'lucide-react';
import { cn } from '../../../../../../shared/lib/utils';
import { useTheme } from '../../../../../../shared/contexts/ThemeContext';

// ============================================================================
// TYPES
// ============================================================================

interface ScheduledItem {
  id: string;
  title: string;
  type: 'post' | 'email' | 'video';
  time: string;
  platforms?: string[];
  scheduled_date?: string;
  scheduledDate?: string;
}

interface DayData {
  date: Date;
  isToday: boolean;
  items: ScheduledItem[];
}

interface WeeklyCalendarProps {
  className?: string;
  onAddItem?: (date: Date) => void;
  onItemClick?: (item: ScheduledItem) => void;
}

// ============================================================================
// HELPERS
// ============================================================================

const DAYS_IT = ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'];
const MONTHS_IT = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'];

function getWeekDays(startDate: Date): DayData[] {
  const days: DayData[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  for (let i = 0; i < 7; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    date.setHours(0, 0, 0, 0);

    days.push({
      date,
      isToday: date.getTime() === today.getTime(),
      items: [],
    });
  }

  return days;
}

function formatDateRange(start: Date, end: Date): string {
  const startMonth = MONTHS_IT[start.getMonth()];
  const endMonth = MONTHS_IT[end.getMonth()];

  if (startMonth === endMonth) {
    return `${start.getDate()} - ${end.getDate()} ${startMonth}`;
  }
  return `${start.getDate()} ${startMonth} - ${end.getDate()} ${endMonth}`;
}

const typeIcons: Record<string, React.ElementType> = {
  post: Share2,
  email: Mail,
  video: Video,
};

const typeColors: Record<string, string> = {
  post: 'bg-gold',
  email: 'bg-gold',
  video: 'bg-gold',
};

// ============================================================================
// API
// ============================================================================

const CalendarAPI = {
  async getScheduledItems(start: Date, end: Date): Promise<ScheduledItem[]> {
    try {
      const startStr = start.toISOString().split('T')[0];
      const endStr = end.toISOString().split('T')[0];

      const response = await fetch(
        `/api/v1/marketing/scheduler/week?start=${startStr}&end=${endStr}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('admin_token')}` },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch scheduled items');
      }

      return await response.json();
    } catch (error) {
      console.warn('Calendar fetch error, using empty state:', error);
      return []; // Return empty array instead of throwing to prevent UI crash
    }
  },
};

// ============================================================================
// COMPONENT
// ============================================================================

export function WeeklyCalendar({ className, onAddItem, onItemClick }: WeeklyCalendarProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [weekStart, setWeekStart] = useState(() => {
    const today = new Date();
    const day = today.getDay();
    const diff = today.getDate() - day + (day === 0 ? -6 : 1); // Start from Monday
    return new Date(today.setDate(diff));
  });

  const [days, setDays] = useState<DayData[]>([]);
  const [items, setItems] = useState<ScheduledItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const cardBg = isDark ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const cellBg = isDark ? 'bg-white/5' : 'bg-gray-50';
  const todayBg = isDark ? 'bg-gold/20 border-gold' : 'bg-gold/10 border-gold';

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);

        const scheduledItems = await CalendarAPI.getScheduledItems(weekStart, weekEnd);
        setItems(scheduledItems);

        // Distribute items across week days based on their scheduled date
        const weekDays = getWeekDays(weekStart);

        // Assign items to corresponding days
        scheduledItems.forEach((item) => {
          if (!item.scheduled_date && !item.scheduledDate) return;

          const itemDate = new Date(item.scheduled_date || item.scheduledDate);
          // Calculate day index carefully considering timezones
          const start = new Date(weekStart);
          start.setHours(0, 0, 0, 0);
          const current = new Date(itemDate);
          current.setHours(0, 0, 0, 0);

          const diffTime = Math.abs(current.getTime() - start.getTime());
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

          if (diffDays >= 0 && diffDays < 7) {
            weekDays[diffDays].items.push(item);
          }
        });

        setDays(weekDays);
      } catch (e) {
        console.error("WeeklyCalendar load error", e);
        // Ensure we still show the grid even if data fetch fails
        setDays(getWeekDays(weekStart));
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [weekStart]);

  const handlePrevWeek = () => {
    const newStart = new Date(weekStart);
    newStart.setDate(weekStart.getDate() - 7);
    setWeekStart(newStart);
  };

  const handleNextWeek = () => {
    const newStart = new Date(weekStart);
    newStart.setDate(weekStart.getDate() + 7);
    setWeekStart(newStart);
  };

  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekStart.getDate() + 6);

  return (
    <div className={cn('rounded-xl border p-4 sm:p-6', cardBg, className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className={cn('text-lg font-semibold', textPrimary)}>
          Calendario Settimanale
        </h3>

        <div className="flex items-center gap-2">
          <span className={cn('text-sm', textSecondary)}>
            {formatDateRange(weekStart, weekEnd)}
          </span>

          <div className="flex">
            <button
              onClick={handlePrevWeek}
              className={cn(
                'p-1.5 rounded-l-lg border transition-colors',
                isDark
                  ? 'border-white/10 hover:bg-white/10'
                  : 'border-gray-200 hover:bg-gray-100'
              )}
            >
              <ChevronLeft className={cn('w-4 h-4', textSecondary)} />
            </button>
            <button
              onClick={handleNextWeek}
              className={cn(
                'p-1.5 rounded-r-lg border-t border-r border-b transition-colors',
                isDark
                  ? 'border-white/10 hover:bg-white/10'
                  : 'border-gray-200 hover:bg-gray-100'
              )}
            >
              <ChevronRight className={cn('w-4 h-4', textSecondary)} />
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-gold" />
        </div>
      ) : (
        <div className="grid grid-cols-7 gap-2">
          {/* Day Headers */}
          {days.map((day) => (
            <div
              key={`header-${day.date.toISOString()}`}
              className="text-center pb-2"
            >
              <span className={cn('text-xs font-medium', textSecondary)}>
                {DAYS_IT[day.date.getDay()]}
              </span>
              <span
                className={cn(
                  'block text-sm font-semibold mt-1',
                  day.isToday ? 'text-gold' : textPrimary
                )}
              >
                {day.date.getDate()}
              </span>
            </div>
          ))}

          {/* Day Cells */}
          {days.map((day) => (
            <motion.div
              key={`cell-${day.date.toISOString()}`}
              className={cn(
                'min-h-[100px] sm:min-h-[120px] rounded-lg p-2 border relative group cursor-pointer transition-all',
                day.isToday ? todayBg : cellBg,
                isDark ? 'border-white/5 hover:border-white/20' : 'border-gray-100 hover:border-gray-300'
              )}
              onClick={() => onAddItem?.(day.date)}
              whileHover={{ scale: 1.02 }}
            >
              {/* Add button on hover */}
              <button
                className={cn(
                  'absolute top-1 right-1 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity',
                  isDark ? 'bg-white/10 hover:bg-white/20' : 'bg-gray-200 hover:bg-gray-300'
                )}
                onClick={(e) => {
                  e.stopPropagation();
                  onAddItem?.(day.date);
                }}
              >
                <Plus className={cn('w-3 h-3', textSecondary)} />
              </button>

              {/* Items */}
              <div className="space-y-1 mt-1">
                {day.items.slice(0, 3).map((item) => {
                  const Icon = typeIcons[item.type];
                  return (
                    <motion.div
                      key={item.id}
                      className={cn(
                        'flex items-center gap-1.5 p-1.5 rounded text-xs cursor-pointer',
                        isDark ? 'bg-white/10 hover:bg-white/20' : 'bg-white hover:bg-gray-50 shadow-sm'
                      )}
                      onClick={(e) => {
                        e.stopPropagation();
                        onItemClick?.(item);
                      }}
                      whileHover={{ x: 2 }}
                    >
                      <div className={cn('w-5 h-5 rounded flex items-center justify-center flex-shrink-0', typeColors[item.type])}>
                        <Icon className="w-3 h-3 text-white" />
                      </div>
                      <span className={cn('truncate flex-1', textPrimary)}>
                        {item.title.length > 12 ? `${item.title.substring(0, 12)}...` : item.title}
                      </span>
                      <span className={cn('text-[10px]', textSecondary)}>{item.time}</span>
                    </motion.div>
                  );
                })}

                {day.items.length > 3 && (
                  <p className={cn('text-[10px] text-center pt-1', textSecondary)}>
                    +{day.items.length - 3} altri
                  </p>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-white/5">
        {Object.entries(typeIcons).map(([type, Icon]) => (
          <div key={type} className="flex items-center gap-1.5">
            <div className={cn('w-4 h-4 rounded flex items-center justify-center', typeColors[type])}>
              <Icon className="w-2.5 h-2.5 text-white" />
            </div>
            <span className={cn('text-xs capitalize', textSecondary)}>{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
