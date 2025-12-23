import { cn } from "../../../lib/utils";
import { Activity, TrendingUp, Calendar, Clock } from "lucide-react";
import type { ChatContextData } from "../types";

interface ContextBadgesProps {
  data: ChatContextData;
}

export function ContextBadges({ data }: ContextBadgesProps) {
  const badges = [];

  // Phase badge
  if (data.currentPhase) {
    badges.push({
      icon: TrendingUp,
      label: data.currentPhase,
      color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    });
  }

  // Pain level badge
  if (data.recentPain && data.recentPain[0]?.pain_level !== undefined) {
    const painLevel = data.recentPain[0].pain_level;
    const painColor =
      painLevel >= 7
        ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
        : painLevel >= 4
        ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300"
        : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300";

    badges.push({
      icon: Activity,
      label: `Dolore: ${painLevel}/10`,
      color: painColor,
    });
  }

  // Last workout badge
  if (data.todayWorkout?.date) {
    badges.push({
      icon: Calendar,
      label: "Workout oggi",
      color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
    });
  }

  // Days in phase badge
  if (data.weeksInPhase) {
    const days = data.weeksInPhase * 7;
    badges.push({
      icon: Clock,
      label: `${days} giorni in fase`,
      color: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
    });
  }

  if (badges.length === 0) return null;

  return (
    <div className="px-4 py-3 border-b bg-muted/30">
      <div className="flex flex-wrap gap-2">
        {badges.map((badge, index) => {
          const Icon = badge.icon;
          return (
            <div
              key={index}
              className={cn(
                "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium",
                badge.color
              )}
            >
              <Icon size={12} />
              <span>{badge.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
