import { createLazyFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { MessageSquare, Apple, Flame, Droplets, Egg, Wheat, Plus, ChevronRight, FileText, RefreshCw } from "lucide-react";
import { HubLayout } from "../features/layout/HubLayout";
import { ChatInterface } from "../features/chat/ChatInterface";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { plansApi, type NutritionWeeklyPlan } from "../lib/api";
import { nutritionApi, type DailyNutritionLog } from "../lib/api/nutrition";
import { MealPlannerPage } from "../features/nutrition/components/MealPlanner/MealPlannerPage";
import { useState, useEffect } from "react";
import { cn } from "../lib/utils";
import { logger } from "../lib/logger";
import { toast } from "../components/ui/Toast";
import { hapticFeedback } from "../lib/haptics";

export const Route = createLazyFileRoute("/nutrition")({
  component: NutritionHub,
});

// ============================================================================
// TODAY'S MACROS TAB
// ============================================================================

function TodayMacrosTab() {
  const [nutritionPlan, setNutritionPlan] = useState<NutritionWeeklyPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [waterGlasses, setWaterGlasses] = useState(0);
  const [dailyLog, setDailyLog] = useState<DailyNutritionLog | null>(null);

  // Today's logged data - computed from dailyLog
  const todayLogged = dailyLog?.daily_total || {
    calories_kcal: 0,
    protein_g: 0,
    carbs_g: 0,
    fat_g: 0,
  };

  useEffect(() => {
    loadNutritionPlan();
    loadDailyLog();
  }, []);

  const loadNutritionPlan = async () => {
    try {
      setIsLoading(true);
      const response = await plansApi.getCurrentNutritionPlan();
      setNutritionPlan(response.plan);
    } catch (error) {
      logger.error("Error loading nutrition plan", { error });
    } finally {
      setIsLoading(false);
    }
  };

  const loadDailyLog = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const log = await nutritionApi.getDailyLog(today);
      setDailyLog(log);
      setWaterGlasses(Math.floor(log.water_ml / 250)); // 250ml = 1 glass
    } catch (error) {
      logger.error("Error loading daily log", { error });
      // Initialize empty log if not found
      setDailyLog({
        date: new Date().toISOString().split('T')[0],
        meals: [],
        water_ml: 0,
        supplements: [],
        notes: '',
      });
    }
  };

  const handleGeneratePlan = async () => {
    try {
      setIsGenerating(true);
      await plansApi.generateNutritionPlan({ goal: "maintenance" });
      await loadNutritionPlan();
    } catch (error) {
      logger.error("Error generating plan", { error });
      toast.error({ title: "Errore", description: "Impossibile generare il piano nutrizionale" });
    } finally {
      setIsGenerating(false);
    }
  };

  // Use real plan targets or defaults
  const targets = nutritionPlan ? {
    calories: nutritionPlan.daily_calories,
    protein: nutritionPlan.daily_protein,
    carbs: nutritionPlan.daily_carbs,
    fat: nutritionPlan.daily_fat,
  } : {
    calories: 2200,
    protein: 165,
    carbs: 220,
    fat: 73,
  };

  const macros = [
    { name: "Calorie", icon: Flame, color: "text-orange-500", bgColor: "bg-orange-500", current: todayLogged.calories_kcal, target: targets.calories, unit: "kcal" },
    { name: "Proteine", icon: Egg, color: "text-red-500", bgColor: "bg-red-500", current: todayLogged.protein_g, target: targets.protein, unit: "g" },
    { name: "Carbs", icon: Wheat, color: "text-amber-500", bgColor: "bg-amber-500", current: todayLogged.carbs_g, target: targets.carbs, unit: "g" },
    { name: "Grassi", icon: Apple, color: "text-green-500", bgColor: "bg-green-500", current: todayLogged.fat_g, target: targets.fat, unit: "g" },
  ];

  // Transform API meals to UI format
  const meals = dailyLog?.meals.map((meal, index) => ({
    id: index + 1,
    time: meal.time || "00:00",
    name: meal.name,
    logged: meal.foods.length > 0,
    calories: meal.total_macros?.calories_kcal || 0,
  })) || [];

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        <div className="animate-pulse grid grid-cols-2 gap-3">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-24 bg-muted rounded-xl" />)}
        </div>
      </div>
    );
  }

  if (!nutritionPlan) {
    return (
      <div className="p-4">
        <div className="text-center py-12 bg-card border rounded-xl">
          <Apple className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
          <p className="text-muted-foreground mb-3">Nessun piano nutrizionale attivo</p>
          <button
            onClick={handleGeneratePlan}
            disabled={isGenerating}
            className="flex items-center gap-2 mx-auto px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50"
          >
            {isGenerating ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            {isGenerating ? "Generazione..." : "Genera Piano"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {/* Goal badge */}
      <div className="flex items-center gap-2">
        <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full font-medium">
          Obiettivo: {nutritionPlan.goal === 'deficit' ? '📉 Deficit' : nutritionPlan.goal === 'surplus' ? '📈 Surplus' : '⚖️ Mantenimento'}
        </span>
        <span className="text-xs text-muted-foreground">Settimana {nutritionPlan.week_number}</span>
      </div>

      {/* Macros Grid */}
      <div className="grid grid-cols-2 gap-3">
        {macros.map((macro) => {
          const Icon = macro.icon;
          const progress = Math.min((macro.current / macro.target) * 100, 100);

          return (
            <div key={macro.name} className="bg-card border rounded-xl p-3">
              <div className="flex items-center gap-2 mb-2">
                <Icon className={cn("w-4 h-4", macro.color)} />
                <span className="text-sm font-medium">{macro.name}</span>
              </div>
              <div className="text-xl font-bold">
                {macro.current}<span className="text-sm text-muted-foreground">/{macro.target} {macro.unit}</span>
              </div>
              <div className="h-2 bg-muted rounded-full mt-2 overflow-hidden">
                <div
                  className={cn("h-full rounded-full", macro.bgColor)}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Water */}
      <div className="bg-card border rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Droplets className="w-5 h-5 text-blue-500" />
            <span className="font-medium">Acqua</span>
          </div>
          <span className="text-lg font-bold">{waterGlasses}/10 bicchieri</span>
        </div>
        <div className="flex gap-1">
          {Array.from({ length: 10 }).map((_, i) => (
            <button
              key={i}
              onClick={() => {
                hapticFeedback.impact("light");
                setWaterGlasses(i + 1);
              }}
              className={cn(
                "flex-1 h-8 rounded-lg transition-all",
                i < waterGlasses ? "bg-blue-500" : "bg-muted hover:bg-blue-200"
              )}
            />
          ))}
        </div>
      </div>

      {/* Today's Meals */}
      <div className="bg-card border rounded-xl p-4">
        <h3 className="font-bold text-lg mb-3">Pasti di Oggi</h3>
        <div className="space-y-2">
          {meals.map((meal) => (
            <div
              key={meal.id}
              className={cn(
                "flex items-center justify-between p-3 rounded-lg border",
                meal.logged ? "bg-green-500/10 border-green-500/30" : "bg-secondary/30"
              )}
            >
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">{meal.time}</span>
                <span className="font-medium">{meal.name}</span>
              </div>
              {meal.logged ? (
                <span className="text-sm font-medium text-orange-600">{meal.calories} kcal</span>
              ) : (
                <button className="flex items-center gap-1 text-xs bg-primary text-primary-foreground px-3 py-1.5 rounded-lg">
                  <Plus className="w-3 h-3" /> Log
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Link to Progress */}
      <Link
        to="/progress"
        className="flex items-center justify-between p-4 bg-secondary/50 rounded-xl"
      >
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-muted-foreground" />
          <span className="font-medium">Vedi Storico Completo</span>
        </div>
        <ChevronRight className="w-5 h-5 text-muted-foreground" />
      </Link>
    </div>
  );
}

// ============================================================================
// MEAL PLAN TAB
// ============================================================================

function MealPlanTab() {
  return <MealPlannerPage />;
}

// ============================================================================
// NUTRITION HUB
// ============================================================================

function NutritionHub() {
  const navigate = useNavigate();
  const search = Route.useSearch() as unknown as { tab?: unknown };
  const defaultTab = typeof search.tab === "string" ? search.tab : undefined;

  useEffect(() => {
    if (typeof search.tab !== "string") return;
    navigate({ to: "/nutrition", search: {} as any } as any);
  }, [navigate, search.tab]);

  return (
    <HubLayout
      tabs={[
        {
          id: "chat",
          label: "Nutrizionista",
          icon: MessageSquare,
          component: () => (
            <ErrorBoundary>
              <ChatInterface mode="nutrition" />
            </ErrorBoundary>
          ),
        },
        {
          id: "today",
          label: "Oggi",
          icon: Flame,
          component: TodayMacrosTab,
        },
        {
          id: "plan",
          label: "Piano",
          icon: FileText,
          component: MealPlanTab,
        },
      ]}
      defaultTab={defaultTab}
    />
  );
}
