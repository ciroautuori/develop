import { createLazyFileRoute } from "@tanstack/react-router";
import { useState, Suspense } from "react";
import { PainTrendsChart } from "../features/progress/PainTrendsChart";
import { BodyHeatmap } from "../features/checkin/BodyHeatmap";
import { cn } from "../lib/utils";
import { TrendingUp, Heart, Calendar } from "lucide-react";
import { usePainHistory } from "../features/progress/hooks/usePainHistory";
import { motion, AnimatePresence } from "framer-motion";

interface PainHistoryEntry {
  id: string;
  date: string;
  pain_level: number;
  pain_locations?: string[];
  notes?: string;
}

export const Route = createLazyFileRoute("/pain-tracker")({
  component: PainTrackerPage,
});

type ViewMode = "chart" | "heatmap" | "calendar";

function PainTrackerPage() {
  const [view, setView] = useState<ViewMode>("chart");

  return (
    <div className="space-y-4 pb-20 overflow-x-hidden">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-0.5"
      >
        <h1 className="text-xl md:text-2xl font-bold">Tracker Dolore</h1>
        <p className="text-xs md:text-sm text-muted-foreground">
          Monitora l'andamento nel tempo
        </p>
      </motion.div>

      {/* View Switcher - Mobile Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 md:mx-0 md:px-0 no-scrollbar">
        <TabButton
          active={view === "chart"}
          onClick={() => setView("chart")}
          icon={<TrendingUp size={18} />}
        >
          Grafico
        </TabButton>
        <TabButton
          active={view === "heatmap"}
          onClick={() => setView("heatmap")}
          icon={<Heart size={18} />}
        >
          Mappa Corpo
        </TabButton>
        <TabButton
          active={view === "calendar"}
          onClick={() => setView("calendar")}
          icon={<Calendar size={18} />}
        >
          Calendario
        </TabButton>
      </div>

      {/* Views */}
      <div className="min-h-[400px]">
        <AnimatePresence mode="wait">
          {view === "chart" && (
            <motion.div
              key="chart"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              <Suspense fallback={<div className="h-64 bg-muted animate-pulse rounded-xl" />}>
                <PainTrendsChart days={30} />
              </Suspense>
            </motion.div>
          )}
          {view === "heatmap" && (
            <motion.div
              key="heatmap"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              <Suspense fallback={<div className="h-96 bg-muted animate-pulse rounded-xl" />}>
                <BodyHeatmapContainer />
              </Suspense>
            </motion.div>
          )}
          {view === "calendar" && (
            <motion.div
              key="calendar"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              <PainCalendarView />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  children: React.ReactNode;
}

function TabButton({ active, onClick, icon, children }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "relative flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm whitespace-nowrap transition-all duration-200 active:scale-95 touch-manipulation",
        active
          ? "text-primary-foreground"
          : "bg-muted text-muted-foreground hover:bg-muted/80"
      )}
    >
      {active && (
        <motion.div
          layoutId="activeTab"
          className="absolute inset-0 bg-primary rounded-xl shadow-md z-0"
          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
        />
      )}
      <span className="relative z-10 flex items-center gap-2">
        {icon}
        {children}
      </span>
    </button>
  );
}

function BodyHeatmapContainer() {
  const { data: history } = usePainHistory(7);

  // Aggregate pain locations from last 7 days
  const uniqueLocations = Array.from(new Set(
    history.flatMap((entry: PainHistoryEntry) => entry.pain_locations || [])
  )) as string[];

  return (
    <div className="bg-card border border-border rounded-xl p-4 md:p-6">
      <h3 className="font-semibold mb-4 text-lg">Zone Dolenti (7 Giorni)</h3>
      <BodyHeatmap selectedLocations={uniqueLocations} readOnly={true} />
    </div>
  );
}

function PainCalendarView() {
  const { data: history } = usePainHistory(30);

  // Create calendar grid for last 30 days
  const days = Array.from({ length: 30 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (29 - i));
    const dateStr = date.toISOString().split('T')[0];
    const entry = history.find((h: PainHistoryEntry) => h.date.startsWith(dateStr));
    return {
      date,
      dateStr,
      pain_level: entry?.pain_level ?? null,
      weekday: date.toLocaleDateString('it', { weekday: 'narrow' }),
      day: date.getDate(),
    };
  });

  const getColorClass = (level: number | null) => {
    if (level === null) return 'bg-muted/30';
    if (level <= 2) return 'bg-green-400';
    if (level <= 4) return 'bg-yellow-400';
    if (level <= 6) return 'bg-orange-400';
    if (level <= 8) return 'bg-red-400';
    return 'bg-red-600';
  };

  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
        <Calendar size={16} className="text-primary" />
        Ultimi 30 Giorni
      </h3>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1">
        {/* Weekday headers */}
        {['L', 'M', 'M', 'G', 'V', 'S', 'D'].map((d, i) => (
          <div key={i} className="text-center text-[10px] text-muted-foreground font-medium py-1">{d}</div>
        ))}

        {/* Empty cells for alignment */}
        {Array.from({ length: (days[0]?.date.getDay() + 6) % 7 }).map((_, i) => (
          <div key={`empty-${i}`} className="aspect-square" />
        ))}

        {/* Day cells */}
        {days.map((day) => (
          <div
            key={day.dateStr}
            className={cn(
              "aspect-square rounded-md flex items-center justify-center text-[10px] font-medium transition-all",
              getColorClass(day.pain_level),
              day.pain_level !== null ? "text-white shadow-sm" : "text-muted-foreground",
              "hover:scale-110 cursor-default"
            )}
            title={`${day.dateStr}: ${day.pain_level !== null ? `Dolore ${day.pain_level}/10` : 'Nessun dato'}`}
          >
            {day.day}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-2 mt-3 text-[9px] text-muted-foreground">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-green-400"/> 0-2</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-yellow-400"/> 3-4</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-orange-400"/> 5-6</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-red-400"/> 7-8</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-red-600"/> 9-10</span>
      </div>
    </div>
  );
}
