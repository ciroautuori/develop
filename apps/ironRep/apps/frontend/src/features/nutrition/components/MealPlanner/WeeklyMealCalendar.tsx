import type React from "react";
import { useMealPlannerStore } from "../../stores/mealPlannerStore";
import { Card } from "../../../../shared/components/ui/card";
import { Button } from "../../../../shared/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import { cn } from "../../../../shared/utils/cn";
import type { Meal } from "../../types/meal.types";
import { touchTarget } from "../../../../lib/touch-targets";
import { hapticFeedback } from "../../../../lib/haptics";

export function WeeklyMealCalendar({
  onChange,
  onAddFood,
}: {
  onChange?: (day: string) => void;
  onAddFood?: (mealType: "breakfast" | "lunch" | "dinner" | "snack") => void;
}) {
  const {
    currentWeek,
    selectedDay,
    selectedMeal,
    setSelectedDay,
    setSelectedMeal,
    removeFoodFromMeal,
    initWeek,
  } = useMealPlannerStore();

  if (currentWeek.length === 0) {
    initWeek();
    return null;
  }

  const handleDaySelect = (date: string) => {
    hapticFeedback.selection();
    setSelectedDay(date);
  };

  const handleMealSelect = (type: string) => {
    hapticFeedback.selection();
    setSelectedMeal(type as "breakfast" | "lunch" | "dinner" | "snack");
  };

  const handleRemoveFood = (e: React.MouseEvent, type: string, foodId: string) => {
    e.stopPropagation();
    hapticFeedback.impact("medium");
    removeFoodFromMeal(selectedDay, type as "breakfast" | "lunch" | "dinner" | "snack", foodId);
    onChange?.(selectedDay);
  };

  const currentDayPlan =
    currentWeek.find((d) => d.date === selectedDay) || currentWeek[0];

  const mealTypes = ["breakfast", "lunch", "dinner", "snack"] as const;
  const mealLabels = {
    breakfast: "Colazione",
    lunch: "Pranzo",
    dinner: "Cena",
    snack: "Snack",
  };

  const MAX_FOODS_PER_MEAL = 5;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-7 gap-5 min-h-[600px]">
      {/* Day Selector */}
      <div className="lg:col-span-2 space-y-3 overflow-hidden lg:overflow-y-auto">
        {currentWeek.map((day) => {
          const date = new Date(day.date);
          const dayName = date.toLocaleDateString("it-IT", { weekday: "long" });
          const dayNum = date.getDate();
          const isSelected = day.date === selectedDay;

          const meals = Object.values(day.meals) as Meal[];

          return (
            <Card
              key={day.date}
              className={cn(
                "p-4 cursor-pointer transition-all duration-200 border-2",
                touchTarget.manipulation,
                touchTarget.active,
                isSelected && "border-primary bg-primary/5 shadow-md",
                !isSelected && "hover:bg-accent hover:border-primary/30"
              )}
              onClick={() => handleDaySelect(day.date)}
            >
              <div className="flex items-center justify-between">
                <span className="capitalize font-semibold text-base">
                  {dayName} {dayNum}
                </span>
                <div className="text-sm text-muted-foreground font-medium">
                  {Math.round(
                    meals.reduce((acc, m) => acc + m.totalCalories, 0)
                  )}{" "}
                  kcal
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Meal Details */}
      <div className="lg:col-span-5 space-y-4 overflow-hidden lg:overflow-y-auto">
        <h2 className="text-2xl font-bold capitalize">
          {new Date(currentDayPlan.date).toLocaleDateString("it-IT", {
            weekday: "long",
            day: "numeric",
            month: "long",
          })}
        </h2>

        <div className="grid gap-4">
          {mealTypes.map((type) => {
            const meal = currentDayPlan.meals[type];
            const isSelected = selectedMeal === type;

            return (
              <Card
                key={type}
                className={cn(
                  "p-5 transition-all cursor-pointer border-2",
                  touchTarget.manipulation,
                  isSelected && "ring-2 ring-primary shadow-lg",
                  !isSelected && "hover:border-primary/50"
                )}
                onClick={() => handleMealSelect(type)}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-lg">{mealLabels[type]}</h3>
                  <span className="text-base text-muted-foreground font-semibold">
                    {Math.round(meal.totalCalories)} kcal
                  </span>
                </div>

                {/* Food List */}
                <div className="space-y-2.5">
                  {meal.foods.length === 0 ? (
                    <div className="text-base text-muted-foreground italic py-3">
                      Nessun alimento aggiunto
                    </div>
                  ) : (
                    meal.foods.slice(0, MAX_FOODS_PER_MEAL).map((food) => (
                      <div
                        key={`${type}-${food.id}`}
                        className="flex items-center justify-between bg-secondary/50 p-3 rounded-lg text-sm group"
                      >
                        <div>
                          <div className="font-semibold text-base">{food.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {Math.round(food.quantity)}g •{" "}
                            {Math.round(food.calories)} kcal
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className={cn(
                            touchTarget.icon.sm,
                            "opacity-0 group-hover:opacity-100 text-destructive hover:text-destructive hover:bg-destructive/10 rounded-lg"
                          )}
                          onClick={(e) => handleRemoveFood(e, type, food.id)}
                          aria-label="Rimuovi alimento"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))
                  )}

                  {meal.foods.length > MAX_FOODS_PER_MEAL && (
                    <div className="text-xs text-muted-foreground/70">
                      Lista lunga: mostro i primi {MAX_FOODS_PER_MEAL} alimenti (NO SCROLL attivo).
                    </div>
                  )}
                </div>

                {/* Add Button */}
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "w-full mt-3 border-2 border-dashed h-11 rounded-xl font-semibold",
                    touchTarget.manipulation
                  )}
                  onClick={() => {
                    handleMealSelect(type);
                    onAddFood?.(type);
                  }}
                >
                  <Plus className="h-5 w-5 mr-2" /> Aggiungi Alimento
                </Button>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
