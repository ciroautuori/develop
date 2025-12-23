import { Progress } from "../../../../shared/components/ui/progress";
import { Card } from "../../../../shared/components/ui/card";
import type { DailyMealPlan } from "../../types/meal.types";

interface MacroSummaryProps {
  week: DailyMealPlan[];
  selectedDay?: string;
}

export function MacroSummary({ week, selectedDay }: MacroSummaryProps) {
  const currentDayStr = selectedDay || new Date().toISOString().split("T")[0];
  const currentDay = week.find((d) => d.date === currentDayStr) || week[0];

  if (!currentDay) return null;

  const { meals, dailyTargets } = currentDay;

  let totalCalories = 0;
  let totalProtein = 0;
  let totalCarbs = 0;
  let totalFat = 0;

  Object.values(meals).forEach((meal) => {
    meal.foods.forEach((food) => {
      totalCalories += food.calories;
      totalProtein += food.protein;
      totalCarbs += food.carbs;
      totalFat += food.fat;
    });
  });

  const calculatePercent = (current: number, target: number) =>
    target > 0 ? Math.min(100, (current / target) * 100) : 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
      <Card className="p-5 border-l-4 border-l-orange-500 shadow-md">
        <div className="text-sm font-semibold text-muted-foreground mb-2">
          Calorie
        </div>
        <div className="flex justify-between items-end mb-3">
          <span className="text-3xl font-bold">
            {Math.round(totalCalories)}
          </span>
          <span className="text-base text-muted-foreground">
            / {dailyTargets.calories}
          </span>
        </div>
        <Progress
          value={calculatePercent(totalCalories, dailyTargets.calories)}
          className="h-2.5 bg-orange-100"
          indicatorClassName="bg-orange-500"
        />
      </Card>

      <Card className="p-5 border-l-4 border-l-red-500 shadow-md">
        <div className="text-sm font-semibold text-muted-foreground mb-2">
          Proteine
        </div>
        <div className="flex justify-between items-end mb-3">
          <span className="text-3xl font-bold">
            {Math.round(totalProtein)}
            <span className="text-lg font-normal">g</span>
          </span>
          <span className="text-base text-muted-foreground">
            / {dailyTargets.protein}g
          </span>
        </div>
        <Progress
          value={calculatePercent(totalProtein, dailyTargets.protein)}
          className="h-2.5 bg-red-100"
          indicatorClassName="bg-red-500"
        />
      </Card>

      <Card className="p-5 border-l-4 border-l-amber-500 shadow-md">
        <div className="text-sm font-semibold text-muted-foreground mb-2">
          Carboidrati
        </div>
        <div className="flex justify-between items-end mb-3">
          <span className="text-3xl font-bold">
            {Math.round(totalCarbs)}
            <span className="text-lg font-normal">g</span>
          </span>
          <span className="text-base text-muted-foreground">
            / {dailyTargets.carbs}g
          </span>
        </div>
        <Progress
          value={calculatePercent(totalCarbs, dailyTargets.carbs)}
          className="h-2.5 bg-amber-100"
          indicatorClassName="bg-amber-500"
        />
      </Card>

      <Card className="p-5 border-l-4 border-l-blue-500 shadow-md">
        <div className="text-sm font-semibold text-muted-foreground mb-2">
          Grassi
        </div>
        <div className="flex justify-between items-end mb-3">
          <span className="text-3xl font-bold">
            {Math.round(totalFat)}
            <span className="text-lg font-normal">g</span>
          </span>
          <span className="text-base text-muted-foreground">
            / {dailyTargets.fat}g
          </span>
        </div>
        <Progress
          value={calculatePercent(totalFat, dailyTargets.fat)}
          className="h-2.5 bg-blue-100"
          indicatorClassName="bg-blue-500"
        />
      </Card>
    </div>
  );
}
