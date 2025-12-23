import { createLazyFileRoute } from "@tanstack/react-router";
import { useState, useEffect, useMemo } from "react";
import {
  Calendar, Activity, Dumbbell, Utensils, ChevronLeft, ChevronRight,
  MessageSquare, CheckCircle, AlertTriangle, TrendingUp, Clock
} from "lucide-react";
import { cn } from "../lib/utils";
import { logger } from "../lib/logger";
import { progressApi, type DashboardData } from "../lib/api";
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, addMonths, subMonths, isSameMonth, isToday, getWeek, getYear } from "date-fns";
import { it } from "date-fns/locale";
import { motion, AnimatePresence } from "framer-motion";
import { ProgressDashboard } from "../features/progress/ProgressDashboard";

export const Route = createLazyFileRoute("/progress")({
  component: ProgressHub,
});

type ProgressTab = "all" | "medical" | "coach" | "nutrition";

function ProgressHub() {
  const [activeTab, setActiveTab] = useState<ProgressTab>("all");
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedWeek, setSelectedWeek] = useState<{ weekNum: number; year: number } | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await progressApi.getDashboard();
      setDashboardData(data);
      setError(null);
    } catch (error) {
      logger.error("Error loading dashboard", { error });
      setError("Errore nel caricamento dei dati");
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: "all" as const, label: "Tutti", icon: Calendar, color: "text-primary" },
    { id: "medical" as const, label: "Medical", icon: Activity, color: "text-red-500" },
    { id: "coach" as const, label: "Coach", icon: Dumbbell, color: "text-blue-500" },
    { id: "nutrition" as const, label: "Nutrition", icon: Utensils, color: "text-green-500" },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden w-full max-w-5xl mx-auto gap-3 px-3 sm:px-4">
      {/* Header */}
      <div className="shrink-0 flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold mb-1">Progressi</h1>
          <p className="text-sm text-muted-foreground">
            Piani settimanali e storico
          </p>
        </div>
      </div>

      {/* Monthly Calendar with Week View */}
      <div className="block shrink-0">
        <MonthlyWeekCalendar
          currentMonth={currentMonth}
          onMonthChange={setCurrentMonth}
          selectedWeek={selectedWeek}
          onWeekSelect={setSelectedWeek}
          activeTab={activeTab}
          dashboardData={dashboardData}
        />
      </div>

      {/* Section Tabs */}
      <div className="bg-card border-b border-border shrink-0 rounded-xl overflow-hidden">
        <div className="flex gap-1 p-1.5">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-2.5 px-2 rounded-lg text-sm font-medium transition-all",
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-muted"
              )}
            >
              <tab.icon size={16} className={activeTab === tab.id ? "" : tab.color} />
              <span className="text-xs sm:text-sm">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content - Storico e Pianificato */}
      <div className="flex-1 overflow-hidden min-h-0">
        <AnimatePresence mode="wait">
          {selectedWeek ? (
            <motion.div
              key="week-detail"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              <WeekDetailView
                weekNum={selectedWeek.weekNum}
                year={selectedWeek.year}
                activeTab={activeTab}
                onClose={() => setSelectedWeek(null)}
              />
            </motion.div>
          ) : (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full flex flex-col gap-3"
            >
              {(activeTab === "all" || activeTab === "medical") && (
                <ProgressDashboard data={dashboardData} isLoading={isLoading} error={error} />
              )}

              {(activeTab === "all" || activeTab === "medical") && (
                <div className={cn(activeTab === "all" && "hidden md:block")}>
                  <MedicalProgressSection data={dashboardData} isLoading={isLoading} />
                </div>
              )}
              {(activeTab === "all" || activeTab === "coach") && (
                <div className={cn(activeTab === "all" && "hidden md:block")}>
                  <CoachProgressSection data={dashboardData} isLoading={isLoading} />
                </div>
              )}
              {(activeTab === "all" || activeTab === "nutrition") && (
                <div className={cn(activeTab === "all" && "hidden md:block")}>
                  <NutritionProgressSection data={dashboardData} isLoading={isLoading} />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ============================================================================
// MONTHLY CALENDAR WITH WEEK ROWS
// ============================================================================

interface MonthlyWeekCalendarProps {
  currentMonth: Date;
  onMonthChange: (date: Date) => void;
  selectedWeek: { weekNum: number; year: number } | null;
  onWeekSelect: (week: { weekNum: number; year: number } | null) => void;
  activeTab: ProgressTab;
  dashboardData: DashboardData | null;
}

function MonthlyWeekCalendar({
  currentMonth,
  onMonthChange,
  selectedWeek,
  onWeekSelect,
  activeTab,
  dashboardData
}: MonthlyWeekCalendarProps) {
  // Generate weeks for the month
  const weeks = useMemo(() => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 });
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });

    const weeksArray: Array<{
      weekNum: number;
      year: number;
      days: Date[];
      isCurrentWeek: boolean;
    }> = [];

    let currentDate = calendarStart;
    while (currentDate <= calendarEnd) {
      const weekStart = currentDate;
      const days: Date[] = [];
      for (let i = 0; i < 7; i++) {
        days.push(addDays(weekStart, i));
      }

      const weekNum = getWeek(weekStart, { weekStartsOn: 1 });
      const year = getYear(weekStart);
      const isCurrentWeek = days.some(d => isToday(d));

      weeksArray.push({ weekNum, year, days, isCurrentWeek });
      currentDate = addDays(currentDate, 7);
    }

    return weeksArray;
  }, [currentMonth]);

  return (
    <div className="bg-card border rounded-xl p-4 shadow-sm">
      {/* Month Navigation */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => onMonthChange(subMonths(currentMonth, 1))}
          className="p-2 rounded-lg hover:bg-secondary transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <h2 className="text-lg font-bold">
          {format(currentMonth, "MMMM yyyy", { locale: it })}
        </h2>
        <button
          onClick={() => onMonthChange(addMonths(currentMonth, 1))}
          className="p-2 rounded-lg hover:bg-secondary transition-colors"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Day Headers */}
      <div className="grid grid-cols-8 gap-1 mb-2">
        <div className="text-xs font-semibold text-muted-foreground text-center py-1">Sett</div>
        {["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"].map(day => (
          <div key={day} className="text-xs font-semibold text-muted-foreground text-center py-1">
            {day}
          </div>
        ))}
      </div>

      {/* Week Rows */}
      <div className="flex flex-col gap-1">
        {weeks.map((week) => {
          const isSelected = selectedWeek?.weekNum === week.weekNum && selectedWeek?.year === week.year;

          return (
            <button
              key={`${week.year}-${week.weekNum}`}
              onClick={() => onWeekSelect(isSelected ? null : { weekNum: week.weekNum, year: week.year })}
              className={cn(
                "w-full grid grid-cols-8 gap-1 p-1.5 rounded-lg transition-all",
                isSelected
                  ? "bg-primary/10 ring-2 ring-primary"
                  : week.isCurrentWeek
                    ? "bg-blue-500/10 hover:bg-blue-500/20"
                    : "hover:bg-secondary"
              )}
            >
              {/* Week Number */}
              <div className={cn(
                "text-xs font-bold flex items-center justify-center rounded",
                week.isCurrentWeek ? "text-blue-600" : "text-muted-foreground"
              )}>
                W{week.weekNum}
              </div>

              {/* Days */}
              {week.days.map((day, i) => {
                const inMonth = isSameMonth(day, currentMonth);
                const today = isToday(day);

                return (
                  <div
                    key={i}
                    className={cn(
                      "text-xs text-center py-1 rounded",
                      !inMonth && "text-muted-foreground/40",
                      today && "bg-primary text-primary-foreground font-bold"
                    )}
                  >
                    {format(day, "d")}
                  </div>
                );
              })}
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-3 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-blue-500" />
          <span>Settimana corrente</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-primary" />
          <span>Oggi</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// WEEK DETAIL VIEW
// ============================================================================

interface WeekDetailViewProps {
  weekNum: number;
  year: number;
  activeTab: ProgressTab;
  onClose: () => void;
}

function WeekDetailView({ weekNum, year, activeTab, onClose }: WeekDetailViewProps) {
  const weekStart = useMemo(() => {
    // Get first day of year, then add weeks
    const jan1 = new Date(year, 0, 1);
    const firstMonday = startOfWeek(jan1, { weekStartsOn: 1 });
    return addDays(firstMonday, (weekNum - 1) * 7);
  }, [weekNum, year]);

  const isCurrentWeek = isToday(weekStart) || isToday(addDays(weekStart, 6));
  const isPastWeek = addDays(weekStart, 6) < new Date();

  return (
    <div className="bg-card border rounded-xl p-4 shadow-sm flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold text-lg">
            Settimana {weekNum} - {year}
          </h3>
          <p className="text-sm text-muted-foreground">
            {format(weekStart, "d MMM", { locale: it })} - {format(addDays(weekStart, 6), "d MMM", { locale: it })}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isCurrentWeek && (
            <span className="text-xs bg-blue-500/20 text-blue-600 px-2 py-1 rounded-full font-medium">
              Corrente
            </span>
          )}
          {isPastWeek && (
            <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded-full">
              Completata
            </span>
          )}
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Week Plans by Agent */}
      <div className="flex flex-col gap-3">
        <div className="p-8 text-center border rounded-xl bg-secondary/10">
            <p className="text-muted-foreground">Dettaglio storico non ancora disponibile.</p>
        </div>
      </div>

      {/* Weekly Review Button */}
      {isCurrentWeek && (
        <button className="w-full py-3 bg-primary text-primary-foreground rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-primary/90 transition-colors">
          <MessageSquare className="w-5 h-5" />
          Review Settimanale con AI
        </button>
      )}
    </div>
  );
}

// ============================================================================
// WEEK PLAN CARD
// ============================================================================

interface WeekPlanCardProps {
  agentType: "coach" | "medical" | "nutrition";
  title: string;
  status: "planned" | "active" | "completed";
  summary: string;
  progress: number;
  completedItems: number;
  totalItems: number;
}

function WeekPlanCard({ agentType, title, status, summary, progress, completedItems, totalItems }: WeekPlanCardProps) {
  const statusColors = {
    planned: "bg-muted text-muted-foreground",
    active: "bg-blue-500/20 text-blue-600",
    completed: "bg-green-500/20 text-green-600"
  };

  const progressColors = {
    coach: "bg-blue-500",
    medical: "bg-red-500",
    nutrition: "bg-green-500"
  };

  return (
    <div className="bg-secondary/30 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold">{title}</h4>
        <span className={cn("text-xs px-2 py-1 rounded-full font-medium", statusColors[status])}>
          {status === "planned" ? "Pianificato" : status === "active" ? "In corso" : "Completato"}
        </span>
      </div>

      <p className="text-sm text-muted-foreground">{summary}</p>

      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between text-xs">
          <span>{completedItems}/{totalItems} completati</span>
          <span className="font-medium">{progress}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all", progressColors[agentType])}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// PROGRESS SECTIONS (with real data)
// ============================================================================

interface ProgressSectionProps {
  data: DashboardData | null;
  isLoading: boolean;
}

function MedicalProgressSection({ data, isLoading }: ProgressSectionProps) {
  const stats = data?.stats;

  return (
    <div className="bg-card border rounded-xl p-4 shadow-sm">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Activity className="w-5 h-5 text-red-500" />
        Progressi Medici
      </h3>

      {isLoading ? (
        <div className="animate-pulse flex flex-col gap-3">
          <div className="h-20 bg-muted rounded-xl" />
          <div className="h-20 bg-muted rounded-xl" />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            label="Dolore Medio (30gg)"
            value={stats?.avg_pain_30_days?.toFixed(1) || "N/A"}
            trend={stats?.avg_pain_30_days && stats.avg_pain_30_days < 4 ? "down" : "neutral"}
          />
          <StatCard
            label="Valutazioni"
            value={stats?.total_assessments?.toString() || "0"}
            trend="neutral"
          />
          <StatCard
            label="Mobilità Score"
            value={stats?.mobility_score?.toString() || "N/A"}
            trend="up"
          />
          <StatCard
            label="Settimane Attive"
            value={stats?.total_weeks?.toString() || "0"}
            trend="up"
          />
        </div>
      )}
    </div>
  );
}

function CoachProgressSection({ data, isLoading }: ProgressSectionProps) {
  const stats = data?.stats;
  const kpisAny = (data as unknown as { kpis?: Array<Record<string, unknown>> })?.kpis;
  const latestKpi = kpisAny && kpisAny.length > 0 ? kpisAny[kpisAny.length - 1] : undefined;
  const complianceRate = typeof latestKpi?.compliance_rate === "number" ? latestKpi.compliance_rate : null;

  const streakDays = (() => {
    const workoutsAny = (data as unknown as { recent_workouts?: Array<{ date?: string }> })?.recent_workouts;
    if (!workoutsAny || workoutsAny.length === 0) return null;

    const uniqueDays = Array.from(
      new Set(
        workoutsAny
          .map((w) => (w.date ? new Date(w.date).toDateString() : null))
          .filter((d): d is string => Boolean(d))
      )
    )
      .map((d) => new Date(d))
      .sort((a, b) => b.getTime() - a.getTime());

    if (uniqueDays.length === 0) return null;

    let streak = 1;
    for (let i = 1; i < uniqueDays.length; i++) {
      const prev = uniqueDays[i - 1]!.getTime();
      const curr = uniqueDays[i]!.getTime();
      const diffDays = Math.round((prev - curr) / (1000 * 60 * 60 * 24));
      if (diffDays === 1) streak += 1;
      else break;
    }

    return streak;
  })();

  return (
    <div className="bg-card border rounded-xl p-4 shadow-sm">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Dumbbell className="w-5 h-5 text-blue-500" />
        Progressi Workout
      </h3>

      {isLoading ? (
        <div className="animate-pulse flex flex-col gap-3">
          <div className="h-20 bg-muted rounded-xl" />
          <div className="h-20 bg-muted rounded-xl" />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            label="Workout Completati"
            value={stats?.total_completed_workouts?.toString() || "0"}
            trend="up"
          />
          <StatCard
            label="Questa Settimana"
            value={data?.recent_workouts?.length?.toString() || "0"}
            trend="neutral"
          />
          {complianceRate !== null && (
            <StatCard
              label="Compliance"
              value={`${Math.round(complianceRate)}%`}
              trend={complianceRate >= 80 ? "up" : complianceRate >= 60 ? "neutral" : "down"}
            />
          )}
          {streakDays !== null && (
            <StatCard
              label="Streak"
              value={`${streakDays} giorni`}
              trend={streakDays >= 3 ? "up" : "neutral"}
            />
          )}
        </div>
      )}
    </div>
  );
}

function NutritionProgressSection({ data, isLoading }: ProgressSectionProps) {
  return (
    <div className="bg-card border rounded-xl p-4 shadow-sm">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Utensils className="w-5 h-5 text-green-500" />
        Progressi Nutrizione
      </h3>

      {isLoading ? (
        <div className="animate-pulse flex flex-col gap-3">
          <div className="h-20 bg-muted rounded-xl" />
          <div className="h-20 bg-muted rounded-xl" />
        </div>
      ) : (
        <div className="rounded-xl border bg-muted/20 p-4 text-sm text-muted-foreground">
          Nessun dato nutrizione disponibile. Genera un piano nutrizionale o registra i pasti per vedere i progressi.
        </div>
      )}
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  trend: "up" | "down" | "neutral";
}

function StatCard({ label, value, trend }: StatCardProps) {
  const trendIcon = {
    up: "📈",
    down: "📉",
    neutral: "➡️",
  };

  const trendColor = {
    up: "text-green-600 dark:text-green-400",
    down: "text-red-600 dark:text-red-400",
    neutral: "text-muted-foreground",
  };

  const trendBg = {
    up: "bg-green-500/10",
    down: "bg-red-500/10",
    neutral: "bg-muted/50",
  };

  return (
    <div className={cn(
      "rounded-xl sm:rounded-2xl p-3 sm:p-4 transition-all duration-300 hover:shadow-md active:scale-[0.98] touch-manipulation select-none",
      trendBg[trend]
    )}>
      <p className="text-[10px] sm:text-xs text-muted-foreground mb-0.5 sm:mb-1 uppercase tracking-wider leading-tight">{label}</p>
      <p className="text-xl sm:text-2xl font-bold">{value}</p>
      <p className={cn("text-[10px] sm:text-xs mt-1 sm:mt-1.5 font-medium", trendColor[trend])}>
        {trendIcon[trend]} {trend === "up" ? "Migliora" : trend === "down" ? "In Calo" : "Stabile"}
      </p>
    </div>
  );
}
