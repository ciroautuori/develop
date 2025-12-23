import { TrendingDown, TrendingUp, Minus } from "lucide-react";

interface PainComparisonWidgetProps {
  currentPain: number;
  previousPain?: number;
}

export function PainComparisonWidget({
  currentPain,
  previousPain,
}: PainComparisonWidgetProps) {
  if (!previousPain) {
    return null;
  }

  const difference = currentPain - previousPain;
  const percentChange =
    previousPain > 0 ? Math.abs((difference / previousPain) * 100) : 0;

  const getTrendInfo = () => {
    if (difference < -0.5) {
      return {
        icon: <TrendingDown className="h-5 w-5" />,
        text: "Miglioramento",
        color: "text-green-600 dark:text-green-400",
        bgColor: "bg-green-50 dark:bg-green-950/20",
        borderColor: "border-green-200 dark:border-green-800",
      };
    } else if (difference > 0.5) {
      return {
        icon: <TrendingUp className="h-5 w-5" />,
        text: "Peggioramento",
        color: "text-red-600 dark:text-red-400",
        bgColor: "bg-red-50 dark:bg-red-950/20",
        borderColor: "border-red-200 dark:border-red-800",
      };
    } else {
      return {
        icon: <Minus className="h-5 w-5" />,
        text: "Stabile",
        color: "text-muted-foreground",
        bgColor: "bg-secondary",
        borderColor: "border-border",
      };
    }
  };

  const trend = getTrendInfo();

  return (
    <div
      className={`rounded-lg p-4 border ${trend.bgColor} ${trend.borderColor}`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Confronto con Ultimo Check-in</h3>
        <div className={`flex items-center gap-1 ${trend.color}`}>
          {trend.icon}
          <span className="text-sm font-medium">{trend.text}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 text-center">
        <div>
          <div className="text-xs text-muted-foreground mb-1">Precedente</div>
          <div className="text-2xl font-bold">{previousPain.toFixed(1)}</div>
        </div>

        <div>
          <div className="text-xs text-muted-foreground mb-1">Differenza</div>
          <div className={`text-2xl font-bold ${trend.color}`}>
            {difference > 0 ? "+" : ""}
            {difference.toFixed(1)}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted-foreground mb-1">Attuale</div>
          <div className="text-2xl font-bold">{currentPain.toFixed(1)}</div>
        </div>
      </div>

      {percentChange > 0 && (
        <div className="mt-3 pt-3 border-t text-xs text-center text-muted-foreground">
          Variazione: {percentChange.toFixed(0)}%
        </div>
      )}
    </div>
  );
}
