import { useEffect, useMemo, useState } from "react";
import { Calendar, Plus, Save, Sparkles } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import { Tabs } from "../../../../shared/components/ui/tabs";
import { Input } from "../../../../shared/components/ui/input";
import { Button } from "../../../../shared/components/ui/button";
import { FoodSearchPanel } from "../FoodSearch/FoodSearchPanel";
import { WeeklyMealCalendar } from "./WeeklyMealCalendar";
import { MacroSummary } from "./MacroSummary";
import { useMealPlannerStore } from "../../stores/mealPlannerStore";
import type { FoodItem } from "../../types/food.types";
import { toast } from "sonner";
import { cn } from "../../../../lib/utils";
import { hapticFeedback } from "../../../../lib/haptics";
import { plansApi } from "@/lib/api/plans";
import { nutritionApi } from "@/lib/api/nutrition";
import { usersApi } from "@/lib/api";
import Modal from "../../../../components/ui/Modal";

export function MealPlannerPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("planner");
  const [isTargetsModalOpen, setIsTargetsModalOpen] = useState(false);
  const {
    currentWeek,
    selectedDay,
    selectedMeal,
    addFoodToMeal,
    initWeek,
    setDailyTargetsForWeek,
    setFoodsForMeal,
  } = useMealPlannerStore();

  const [isLoading, setIsLoading] = useState(false);
  const [isSavingTargets, setIsSavingTargets] = useState(false);
  const [hasNutritionPlan, setHasNutritionPlan] = useState<boolean | null>(null);
  const [manualTargets, setManualTargets] = useState<{
    calories: string;
    protein: string;
    carbs: string;
    fat: string;
  }>({
    calories: "",
    protein: "",
    carbs: "",
    fat: "",
  });

  useEffect(() => {
    if (currentWeek.length === 0) {
      initWeek();
    }
  }, [currentWeek.length, initWeek]);

  const currentDayPlan = useMemo(() => {
    return currentWeek.find((d) => d.date === selectedDay) || currentWeek[0] || null;
  }, [currentWeek, selectedDay]);

  useEffect(() => {
    const loadTargetsAndLogs = async () => {
      if (currentWeek.length === 0) return;

      setIsLoading(true);
      try {
        const currentPlan = await plansApi.getCurrentNutritionPlan();
        if (currentPlan.plan) {
          setHasNutritionPlan(true);
          setDailyTargetsForWeek({
            calories: currentPlan.plan.dailyCalorieTarget,
            protein: currentPlan.plan.dailyProteinTarget,
            carbs: currentPlan.plan.dailyCarbsTarget,
            fat: currentPlan.plan.dailyFatTarget,
          });
        } else {
          setHasNutritionPlan(false);
          const me = await usersApi.getMe();

          const calories = me.manual_target_calories ?? null;
          const protein = me.manual_target_protein_g ?? null;
          const carbs = me.manual_target_carbs_g ?? null;
          const fat = me.manual_target_fat_g ?? null;

          setManualTargets({
            calories: calories != null ? String(calories) : "",
            protein: protein != null ? String(protein) : "",
            carbs: carbs != null ? String(carbs) : "",
            fat: fat != null ? String(fat) : "",
          });

          if (calories != null && protein != null && carbs != null && fat != null) {
            setDailyTargetsForWeek({ calories, protein, carbs, fat });
          } else {
            setDailyTargetsForWeek({ calories: 0, protein: 0, carbs: 0, fat: 0 });
          }
        }

        const normalizeMealType = (name: string) => {
          const n = name.toLowerCase();
          if (n.includes("breakfast") || n.includes("colaz")) return "breakfast";
          if (n.includes("lunch") || n.includes("pranzo")) return "lunch";
          if (n.includes("dinner") || n.includes("cena")) return "dinner";
          if (n.includes("snack")) return "snack";
          return null;
        };

        await Promise.all(
          currentWeek.map(async (day) => {
            const log = await nutritionApi.getDailyLog(day.date);
            if (!log.meals || log.meals.length === 0) return;

            const buckets: Record<"breakfast" | "lunch" | "dinner" | "snack", any[]> = {
              breakfast: [],
              lunch: [],
              dinner: [],
              snack: [],
            };

            log.meals.forEach((m, mealIndex) => {
              const mealType = normalizeMealType(m.name);
              if (!mealType) return;
              m.foods.forEach((f, foodIndex) => {
                buckets[mealType].push({
                  id: `${day.date}-${mealType}-${mealIndex}-${foodIndex}`,
                  name: f.name,
                  brand: f.brand,
                  calories: f.calories,
                  protein: f.protein,
                  carbs: f.carbs,
                  fat: f.fat,
                  type: f.brand ? "brand" : "generic",
                  quantity: f.quantity,
                });
              });
            });

            (Object.keys(buckets) as Array<"breakfast" | "lunch" | "dinner" | "snack">).forEach((mealType) => {
              if (buckets[mealType].length > 0) {
                setFoodsForMeal(day.date, mealType, buckets[mealType] as any);
              }
            });
          })
        );
      } catch (e) {
        toast.error("Errore nel caricamento del piano alimentare");
      } finally {
        setIsLoading(false);
      }
    };

    void loadTargetsAndLogs();
  }, [currentWeek, setDailyTargetsForWeek, setFoodsForMeal]);

  const saveManualTargets = async () => {
    const calories = Number(manualTargets.calories);
    const protein = Number(manualTargets.protein);
    const carbs = Number(manualTargets.carbs);
    const fat = Number(manualTargets.fat);

    if (
      !Number.isFinite(calories) ||
      !Number.isFinite(protein) ||
      !Number.isFinite(carbs) ||
      !Number.isFinite(fat) ||
      calories <= 0 ||
      protein < 0 ||
      carbs < 0 ||
      fat < 0
    ) {
      toast.error("Inserisci target validi (kcal > 0, macro >= 0)");
      return;
    }

    setIsSavingTargets(true);
    try {
      const me = await usersApi.getMe();
      await usersApi.update(me.id, {
        manual_target_calories: Math.round(calories),
        manual_target_protein_g: Math.round(protein),
        manual_target_carbs_g: Math.round(carbs),
        manual_target_fat_g: Math.round(fat),
      });

      setDailyTargetsForWeek({
        calories: Math.round(calories),
        protein: Math.round(protein),
        carbs: Math.round(carbs),
        fat: Math.round(fat),
      });
      toast.success("Target salvati");
      setIsTargetsModalOpen(false);
    } catch {
      toast.error("Errore nel salvataggio dei target");
    } finally {
      setIsSavingTargets(false);
    }
  };

  const saveDay = async (day: string) => {
    const dayPlan = currentWeek.find((d) => d.date === day);
    if (!dayPlan) return;

    const mealTypes = ["breakfast", "lunch", "dinner", "snack"] as const;
    const meals = mealTypes.map((type) => ({
      name: type,
      foods: dayPlan.meals[type].foods.map((f) => ({
        name: f.name,
        quantity: f.quantity,
        unit: "g",
        calories: Math.round(f.calories),
        protein: f.protein,
        carbs: f.carbs,
        fat: f.fat,
        brand: f.brand,
      })),
    }));

    await nutritionApi.saveDailyLog({
      date: day,
      meals,
      water_ml: 0,
      supplements: [],
      notes: "",
    });
  };

  const handleAddFood = (food: FoodItem) => {
    hapticFeedback.impact("medium");

    if (selectedDay && selectedMeal) {
      addFoodToMeal(selectedDay, selectedMeal, food);
      void saveDay(selectedDay)
        .then(() => toast.success("Alimento aggiunto e salvato"))
        .catch(() => toast.error("Alimento aggiunto, ma salvataggio fallito"));
    } else {
      hapticFeedback.notification("error");
      toast.error(
        "Seleziona un pasto nel calendario prima di aggiungere alimenti"
      );
      setActiveTab("planner");
    }
  };

  const handleGenerateAIDiet = () => {
    hapticFeedback.impact("heavy");
    navigate({ to: "/nutrition", search: { tab: "chat" } as any });
  };

  const handleSave = () => {
    hapticFeedback.notification("success");
    if (!currentDayPlan) {
      toast.error("Nessun giorno selezionato");
      return;
    }

    setIsLoading(true);
    void saveDay(currentDayPlan.date)
      .then(() => toast.success("Piano salvato"))
      .catch(() => toast.error("Errore nel salvataggio"))
      .finally(() => setIsLoading(false));
  };

  return (
    <div className="bg-background">
      <Modal open={isTargetsModalOpen} onOpenChange={setIsTargetsModalOpen}>
        <Modal.Header>
          <Modal.Title>Target giornalieri</Modal.Title>
          <Modal.Description>
            Imposta calorie e macro (modalità autogestita)
          </Modal.Description>
        </Modal.Header>
        <Modal.Body>
          <div className="space-y-4">
            <div className="space-y-1">
              <div className="text-sm font-medium">Calorie (kcal)</div>
              <Input
                inputMode="numeric"
                value={manualTargets.calories}
                onChange={(e) =>
                  setManualTargets((p) => ({ ...p, calories: e.target.value }))
                }
                placeholder="Es. 2200"
              />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <div className="text-sm font-medium">Proteine (g)</div>
                <Input
                  inputMode="numeric"
                  value={manualTargets.protein}
                  onChange={(e) =>
                    setManualTargets((p) => ({ ...p, protein: e.target.value }))
                  }
                  placeholder="Es. 160"
                />
              </div>
              <div className="space-y-1">
                <div className="text-sm font-medium">Carbo (g)</div>
                <Input
                  inputMode="numeric"
                  value={manualTargets.carbs}
                  onChange={(e) =>
                    setManualTargets((p) => ({ ...p, carbs: e.target.value }))
                  }
                  placeholder="Es. 220"
                />
              </div>
              <div className="space-y-1">
                <div className="text-sm font-medium">Grassi (g)</div>
                <Input
                  inputMode="numeric"
                  value={manualTargets.fat}
                  onChange={(e) =>
                    setManualTargets((p) => ({ ...p, fat: e.target.value }))
                  }
                  placeholder="Es. 70"
                />
              </div>
            </div>
          </div>
        </Modal.Body>
        <Modal.Footer className="justify-between">
          <Button
            variant="outline"
            onClick={() => setIsTargetsModalOpen(false)}
            disabled={isSavingTargets}
          >
            Annulla
          </Button>
          <Button onClick={saveManualTargets} disabled={isSavingTargets}>
            {isSavingTargets ? "Salvataggio..." : "Salva"}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Header - Mobile optimized */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b safe-area-top">
        <div className="px-4 py-4 space-y-4">
          <div>
            <h1 className="text-2xl font-bold">Piano Alimentare</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Pianifica i tuoi pasti della settimana
            </p>
          </div>

          {/* Action Buttons - Mobile first */}
          <div className="flex gap-3">
            <button
              onClick={handleGenerateAIDiet}
              disabled={isLoading}
              className="flex-1 h-12 flex items-center justify-center gap-2 bg-secondary text-secondary-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span className="text-sm">AI</span>
            </button>
            <button
              onClick={handleSave}
              className="flex-1 h-12 flex items-center justify-center gap-2 bg-primary text-primary-foreground rounded-xl font-semibold transition-transform active:scale-[0.98] touch-manipulation shadow-lg"
            >
              <Save className="w-4 h-4" />
              <span className="text-sm">Salva</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {hasNutritionPlan === false && (
          <div className="px-4 pt-4">
            <div className="bg-card border rounded-xl p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="font-semibold">Modalità autogestita</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Imposta i tuoi target giornalieri per tracciare i pasti.
                  </div>
                </div>
                <button
                  className="h-10 px-3 rounded-xl bg-primary text-primary-foreground font-semibold transition-transform active:scale-[0.98] touch-manipulation"
                  onClick={() => {
                    hapticFeedback.selection();
                    setIsTargetsModalOpen(true);
                  }}
                >
                  Modifica
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Macro Summary */}
        <div className="px-4 py-4">
          <MacroSummary week={currentWeek} selectedDay={selectedDay} />
        </div>

        {/* Tabs - Mobile optimized */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col">
          {/* Tab Navigation */}
          <div className="sticky top-[120px] z-10 bg-background border-b px-4">
            <div className="grid grid-cols-2 gap-1 p-1 bg-secondary/50 rounded-xl">
              <button
                onClick={() => setActiveTab("planner")}
                className={cn(
                  "flex items-center justify-center gap-2 h-11 rounded-lg font-semibold transition-all touch-manipulation",
                  activeTab === "planner"
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground active:text-foreground"
                )}
              >
                <Calendar className="w-4 h-4" />
                <span className="text-sm">Piano</span>
              </button>
              <button
                onClick={() => setActiveTab("search")}
                className={cn(
                  "flex items-center justify-center gap-2 h-11 rounded-lg font-semibold transition-all touch-manipulation",
                  activeTab === "search"
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground active:text-foreground"
                )}
              >
                <Plus className="w-4 h-4" />
                <span className="text-sm">Alimenti</span>
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div>
            {activeTab === "planner" && (
              <div className="px-4 py-4">
                <WeeklyMealCalendar
                  onChange={(day) => {
                    void saveDay(day).catch(() => {
                      toast.error("Errore nel salvataggio");
                    });
                  }}
                  onAddFood={() => {
                    setActiveTab("search");
                  }}
                />
              </div>
            )}
            {activeTab === "search" && (
              <div className="px-4 py-4">
                <FoodSearchPanel onSelectFood={handleAddFood} />
              </div>
            )}
          </div>
        </Tabs>
      </main>
    </div>
  );
}
