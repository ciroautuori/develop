import { Activity, TrendingDown, Award, Calendar } from "lucide-react";

interface ContextData {
  currentPain?: number;
  phase?: string;
  lastWorkout?: string;
  daysInPhase?: number;
}

interface ContextPillsProps {
  data: ContextData;
  compact?: boolean;
}

export function ContextPills({ data, compact = false }: ContextPillsProps) {
  const pills = [
    {
      icon: <Activity className="h-3 w-3" />,
      label: "Dolore",
      value: data.currentPain ? `${data.currentPain}/10` : "N/A",
      color:
        data.currentPain && data.currentPain >= 7
          ? "bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300"
          : data.currentPain && data.currentPain >= 5
            ? "bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300"
            : "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300",
    },
    {
      icon: <Award className="h-3 w-3" />,
      label: "Fase",
      value: data.phase ? data.phase.split(":")[0] : "N/A",
      color: "bg-primary/10 text-primary",
    },
  ];

  if (!compact) {
    pills.push(
      {
        icon: <TrendingDown className="h-3 w-3" />,
        label: "Ultimo",
        value: data.lastWorkout || "N/A",
        color: "bg-secondary text-foreground",
      },
      {
        icon: <Calendar className="h-3 w-3" />,
        label: "Giorni",
        value: data.daysInPhase ? `${data.daysInPhase}g` : "N/A",
        color:
          "bg-violet-100 dark:bg-violet-900/20 text-violet-700 dark:text-violet-300",
      }
    );
  }

  return (
    <div className={compact ? "flex gap-1.5" : "flex flex-col gap-1.5"}>
      {!compact && (
        <div className="text-[10px] md:text-xs font-medium text-muted-foreground px-1">
          📊 Il Coach conosce:
        </div>
      )}
      <div
        className={`flex gap-1.5 md:gap-2 ${!compact && "overflow-x-auto pb-1 scrollbar-hide"}`}
      >
        {pills.map((pill, index) => (
          <div
            key={index}
            className={`flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-medium whitespace-nowrap transition-all ${pill.color}`}
          >
            {pill.icon}
            {!compact && (
              <span className="font-normal opacity-75 hidden sm:inline">
                {pill.label}:
              </span>
            )}
            <span className="font-semibold">{pill.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
