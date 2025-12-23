import { useState, useMemo, useCallback } from "react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  Dumbbell,
  Clock,
  Flame,
  CheckCircle,
  Plus,
  X,
  Target,
  Zap,
} from "lucide-react";
import { format, startOfWeek, addDays, isSameDay, isToday, addWeeks, subWeeks, parseISO } from "date-fns";
import { it } from "date-fns/locale";

// ============================================================================
// TYPES
// ============================================================================

interface ScheduledWorkout {
  id: string;
  date: string; // ISO date
  title: string;
  type: "strength" | "conditioning" | "recovery" | "skill" | "wod";
  duration: number; // minutes
  completed: boolean;
  intensity?: "low" | "medium" | "high";
  exercises?: number;
  notes?: string;
}

interface WorkoutCalendarProps {
  workouts?: ScheduledWorkout[];
  onDateSelect?: (date: Date) => void;
  onWorkoutClick?: (workout: ScheduledWorkout) => void;
  onAddWorkout?: (date: Date) => void;
  compact?: boolean;
}

// Default empty array - workouts come from API via props

// ============================================================================
// CONSTANTS
// ============================================================================

const WORKOUT_TYPES: Record<ScheduledWorkout["type"], { label: string; icon: typeof Dumbbell; color: string; bgColor: string }> = {
  strength: {
    label: "Forza",
    icon: Dumbbell,
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
  },
  conditioning: {
    label: "Conditioning",
    icon: Flame,
    color: "text-orange-600 dark:text-orange-400",
    bgColor: "bg-orange-100 dark:bg-orange-900/30",
  },
  recovery: {
    label: "Recupero",
    icon: Target,
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-900/30",
  },
  skill: {
    label: "Skill",
    icon: Zap,
    color: "text-purple-600 dark:text-purple-400",
    bgColor: "bg-purple-100 dark:bg-purple-900/30",
  },
  wod: {
    label: "WOD",
    icon: Flame,
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-100 dark:bg-red-900/30",
  },
};

const DAYS_IT = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"];

// ============================================================================
// WORKOUT CARD COMPONENT
// ============================================================================

interface WorkoutCardProps {
  workout: ScheduledWorkout;
  onClick?: () => void;
  compact?: boolean;
}

function WorkoutCard({ workout, onClick, compact = false }: WorkoutCardProps) {
  const type = WORKOUT_TYPES[workout.type];
  const Icon = type.icon;

  return (
    <button
      onClick={() => {
        hapticFeedback.selection();
        onClick?.();
      }}
      className={cn(
        "w-full text-left rounded-lg border transition-all",
        "hover:shadow-md hover:scale-[1.02] active:scale-[0.98]",
        workout.completed
          ? "bg-muted/50 border-muted"
          : cn(type.bgColor, "border-transparent"),
        compact ? "p-2" : "p-3"
      )}
    >
      <div className="flex items-start gap-2">
        <div className={cn(
          "p-1.5 rounded-lg",
          workout.completed ? "bg-green-100 dark:bg-green-900/30" : type.bgColor
        )}>
          {workout.completed ? (
            <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
          ) : (
            <Icon className={cn("w-4 h-4", type.color)} />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h4 className={cn(
            "font-semibold text-sm truncate",
            workout.completed && "line-through text-muted-foreground"
          )}>
            {workout.title}
          </h4>
          {!compact && (
            <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
              <Clock className="w-3 h-3" />
              <span>{workout.duration} min</span>
              {workout.exercises && (
                <>
                  <span>•</span>
                  <span>{workout.exercises} esercizi</span>
                </>
              )}
            </div>
          )}
        </div>
        {workout.intensity && !compact && (
          <div className={cn(
            "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase",
            workout.intensity === "high"
              ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
              : workout.intensity === "medium"
                ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
          )}>
            {workout.intensity === "high" ? "Alta" : workout.intensity === "medium" ? "Media" : "Bassa"}
          </div>
        )}
      </div>
    </button>
  );
}

// ============================================================================
// WORKOUT DETAIL MODAL
// ============================================================================

interface WorkoutDetailModalProps {
  workout: ScheduledWorkout;
  onClose: () => void;
  onStart?: () => void;
}

function WorkoutDetailModal({ workout, onClose, onStart }: WorkoutDetailModalProps) {
  const type = WORKOUT_TYPES[workout.type];
  const Icon = type.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-card rounded-2xl shadow-2xl border max-w-md w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className={cn("p-6 pb-4", type.bgColor)}>
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full hover:bg-black/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3 mb-3">
            <div className={cn("p-3 rounded-xl bg-white/50 dark:bg-black/20")}>
              <Icon className={cn("w-6 h-6", type.color)} />
            </div>
            <div>
              <span className={cn("text-xs font-bold uppercase tracking-wider", type.color)}>
                {type.label}
              </span>
              <h2 className="text-xl font-bold">{workout.title}</h2>
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1.5">
              <CalendarIcon className="w-4 h-4" />
              <span>{format(parseISO(workout.date), "EEEE d MMMM", { locale: it })}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              <span>{workout.duration} min</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-secondary/50 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-primary">{workout.exercises || 0}</div>
              <div className="text-xs text-muted-foreground">Esercizi</div>
            </div>
            <div className="bg-secondary/50 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-primary">{workout.duration}</div>
              <div className="text-xs text-muted-foreground">Minuti</div>
            </div>
            <div className="bg-secondary/50 rounded-xl p-3 text-center">
              <div className={cn(
                "text-2xl font-bold",
                workout.intensity === "high" ? "text-red-500" :
                  workout.intensity === "medium" ? "text-yellow-500" : "text-green-500"
              )}>
                {workout.intensity === "high" ? "🔥" : workout.intensity === "medium" ? "💪" : "🧘"}
              </div>
              <div className="text-xs text-muted-foreground">Intensità</div>
            </div>
          </div>

          {workout.notes && (
            <div className="bg-muted/50 rounded-xl p-4">
              <p className="text-sm text-muted-foreground">{workout.notes}</p>
            </div>
          )}

          {workout.completed ? (
            <div className="flex items-center justify-center gap-2 p-4 bg-green-100 dark:bg-green-900/20 rounded-xl text-green-700 dark:text-green-400">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">Workout Completato!</span>
            </div>
          ) : (
            <button
              onClick={() => {
                hapticFeedback.notification("success");
                onStart?.();
              }}
              className={cn(
                "w-full py-4 rounded-xl font-bold text-white transition-all",
                "bg-gradient-to-r shadow-lg active:scale-[0.98]",
                workout.type === "strength" ? "from-blue-500 to-indigo-600" :
                  workout.type === "wod" ? "from-red-500 to-orange-600" :
                    workout.type === "recovery" ? "from-green-500 to-emerald-600" :
                      "from-purple-500 to-pink-600"
              )}
            >
              Inizia Workout
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function WorkoutCalendar({
  workouts = [],
  onDateSelect,
  onWorkoutClick,
  onAddWorkout,
  compact = false,
}: WorkoutCalendarProps) {
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedWorkout, setSelectedWorkout] = useState<ScheduledWorkout | null>(null);

  // Get week days
  const weekDays = useMemo(() => {
    const start = startOfWeek(currentWeek, { weekStartsOn: 1 }); // Monday
    return Array.from({ length: 7 }, (_, i) => addDays(start, i));
  }, [currentWeek]);

  // Get workouts for each day
  const getWorkoutsForDay = useCallback((date: Date) => {
    return workouts.filter((w) => isSameDay(parseISO(w.date), date));
  }, [workouts]);

  // Navigation
  const goToPreviousWeek = () => {
    hapticFeedback.selection();
    setCurrentWeek(subWeeks(currentWeek, 1));
  };

  const goToNextWeek = () => {
    hapticFeedback.selection();
    setCurrentWeek(addWeeks(currentWeek, 1));
  };

  const goToToday = () => {
    hapticFeedback.impact("light");
    setCurrentWeek(new Date());
  };

  // Handle date click
  const handleDateClick = (date: Date) => {
    hapticFeedback.selection();
    setSelectedDate(date);
    onDateSelect?.(date);
  };

  // Stats
  const weekStats = useMemo(() => {
    const weekWorkouts = weekDays.flatMap(getWorkoutsForDay);
    return {
      total: weekWorkouts.length,
      completed: weekWorkouts.filter((w) => w.completed).length,
      totalMinutes: weekWorkouts.reduce((sum, w) => sum + w.duration, 0),
    };
  }, [weekDays, getWorkoutsForDay]);

  return (
    <div className={cn(
      "bg-gradient-to-b from-card to-card/95 rounded-2xl border shadow-sm",
      compact ? "p-4" : "p-6"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl">
            <CalendarIcon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Programma Settimanale</h3>
            <p className="text-xs text-muted-foreground">
              {format(weekDays[0], "d MMM", { locale: it })} - {format(weekDays[6], "d MMM yyyy", { locale: it })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={goToPreviousWeek}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={goToToday}
            className="px-3 py-1.5 text-sm font-medium rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
          >
            Oggi
          </button>
          <button
            onClick={goToNextWeek}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Week Stats */}
      {!compact && (
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-secondary/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-bold text-primary">{weekStats.total}</div>
            <div className="text-xs text-muted-foreground">Workout</div>
          </div>
          <div className="bg-secondary/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-bold text-green-500">{weekStats.completed}</div>
            <div className="text-xs text-muted-foreground">Completati</div>
          </div>
          <div className="bg-secondary/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-bold text-orange-500">{weekStats.totalMinutes}</div>
            <div className="text-xs text-muted-foreground">Minuti</div>
          </div>
        </div>
      )}

      {/* Week View */}
      <div className="grid grid-cols-7 gap-2">
        {/* Day Headers */}
        {DAYS_IT.map((day, i) => (
          <div key={day} className="text-center text-xs font-semibold text-muted-foreground py-2">
            {day}
          </div>
        ))}

        {/* Day Cells */}
        {weekDays.map((date) => {
          const dayWorkouts = getWorkoutsForDay(date);
          const isSelected = selectedDate && isSameDay(date, selectedDate);
          const today = isToday(date);

          return (
            <div
              key={date.toISOString()}
              onClick={() => handleDateClick(date)}
              className={cn(
                "min-h-[100px] rounded-xl border transition-all cursor-pointer",
                "hover:border-primary/50 hover:shadow-sm",
                isSelected && "ring-2 ring-primary border-primary",
                today && "bg-primary/5 border-primary/30"
              )}
            >
              {/* Date Number */}
              <div className={cn(
                "text-center py-2 border-b",
                today && "bg-primary text-primary-foreground rounded-t-xl"
              )}>
                <span className={cn(
                  "text-sm font-bold",
                  today ? "text-primary-foreground" : "text-foreground"
                )}>
                  {format(date, "d")}
                </span>
              </div>

              {/* Workouts */}
              <div className="p-1.5 space-y-1.5">
                {dayWorkouts.slice(0, 2).map((workout) => (
                  <WorkoutCard
                    key={workout.id}
                    workout={workout}
                    onClick={() => {
                      setSelectedWorkout(workout);
                      onWorkoutClick?.(workout);
                    }}
                    compact
                  />
                ))}
                {dayWorkouts.length > 2 && (
                  <div className="text-xs text-center text-muted-foreground font-medium">
                    +{dayWorkouts.length - 2} altri
                  </div>
                )}
                {dayWorkouts.length === 0 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      hapticFeedback.selection();
                      onAddWorkout?.(date);
                    }}
                    className="w-full p-2 rounded-lg border-2 border-dashed border-muted-foreground/30 hover:border-primary/50 transition-colors"
                  >
                    <Plus className="w-4 h-4 mx-auto text-muted-foreground" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Day Detail */}
      {selectedDate && !compact && (
        <div className="mt-6 pt-6 border-t">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold">
              {format(selectedDate, "EEEE d MMMM", { locale: it })}
            </h4>
            <button
              onClick={() => {
                hapticFeedback.selection();
                onAddWorkout?.(selectedDate);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Aggiungi
            </button>
          </div>

          <div className="space-y-2">
            {getWorkoutsForDay(selectedDate).map((workout) => (
              <WorkoutCard
                key={workout.id}
                workout={workout}
                onClick={() => setSelectedWorkout(workout)}
              />
            ))}
            {getWorkoutsForDay(selectedDate).length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <CalendarIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Nessun workout programmato</p>
                <p className="text-sm">Clicca "Aggiungi" per crearne uno</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Workout Detail Modal */}
      {selectedWorkout && (
        <WorkoutDetailModal
          workout={selectedWorkout}
          onClose={() => setSelectedWorkout(null)}
          onStart={() => {
            // Navigate to workout session
            setSelectedWorkout(null);
          }}
        />
      )}
    </div>
  );
}
