/**
 * NutritionGoalsStep - Comprehensive Nutrition Goals Collection
 *
 * Collects: diet_type, calorie_goal, macro_distribution, meal_frequency,
 *           dietary_restrictions, allergies, intolerances, budget_preference
 *
 * @production-ready Critical data for Nutrition Agent with FatSecret integration
 */

import type React from "react";
import { useState } from "react";
import { Utensils, DollarSign, AlertCircle, Flame, Timer, ChevronRight, Info } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

export interface NutritionGoalsData {
  nutrition_goal: "deficit" | "maintenance" | "surplus" | "aggressive_deficit" | "lean_bulk" | "custom";
  diet_type: "standard" | "vegetarian" | "vegan" | "pescatarian" | "keto" | "paleo" | "mediterranean" | "flexible";
  calorie_preference: "auto" | "custom";
  custom_calories?: number;
  protein_priority: "low" | "moderate" | "high" | "very_high";
  macro_preference: "balanced" | "high_protein" | "high_carb" | "low_carb" | "keto_macros" | "custom";
  meal_frequency: 2 | 3 | 4 | 5 | 6;
  meal_timing: "standard" | "intermittent_fasting" | "post_workout" | "flexible";
  intermittent_window?: "16_8" | "18_6" | "20_4";
  allergies: string[];
  intolerances: string[];
  dietary_restrictions: string[];
  foods_to_avoid: string[];
  budget_preference: "low" | "medium" | "high" | "no_limit";
  cooking_skill: "none" | "basic" | "intermediate" | "advanced";
  meal_prep_available: boolean;
  supplements_interest: boolean;
}

interface NutritionGoalsStepProps {
  onComplete: (data: NutritionGoalsData) => void;
  onSkip?: () => void;
  initialData?: Partial<NutritionGoalsData>;
}

const NUTRITION_GOALS = [
  { value: "aggressive_deficit", label: "🔥 Deficit Aggressivo", description: "-500/700 kcal, perdita rapida", color: "red" },
  { value: "deficit", label: "📉 Deficit Moderato", description: "-300/500 kcal, perdita sostenibile", color: "orange" },
  { value: "maintenance", label: "⚖️ Mantenimento", description: "Calorie = TDEE, stabilità", color: "green" },
  { value: "surplus", label: "📈 Surplus Moderato", description: "+200/300 kcal, lean bulk", color: "blue" },
  { value: "lean_bulk", label: "💪 Lean Bulk", description: "+300/500 kcal, crescita muscolare", color: "purple" },
  { value: "custom", label: "⚙️ Personalizzato", description: "Imposta le tue calorie", color: "gray" },
];

const DIET_TYPES = [
  { value: "standard", label: "🍽️ Standard", description: "Nessuna restrizione" },
  { value: "mediterranean", label: "🫒 Mediterranea", description: "Dieta classica italiana" },
  { value: "flexible", label: "🔄 Flexible (IIFYM)", description: "If It Fits Your Macros" },
  { value: "high_protein", label: "💪 High Protein", description: "Focus proteine" },
  { value: "vegetarian", label: "🥗 Vegetariano", description: "No carne/pesce" },
  { value: "vegan", label: "🌱 Vegano", description: "100% vegetale" },
  { value: "pescatarian", label: "🐟 Pescetariano", description: "Pesce sì, carne no" },
  { value: "keto", label: "🥓 Chetogenica", description: "Low carb, high fat" },
  { value: "paleo", label: "🦴 Paleo", description: "Dieta ancestrale" },
];

const PROTEIN_PRIORITIES = [
  { value: "low", label: "Bassa", grams: "1.2-1.4g/kg", description: "Sedentario" },
  { value: "moderate", label: "Moderata", grams: "1.6-1.8g/kg", description: "Fitness generale" },
  { value: "high", label: "Alta", grams: "2.0-2.2g/kg", description: "Ipertrofia" },
  { value: "very_high", label: "Molto Alta", grams: "2.2-2.5g/kg", description: "Deficit + muscoli" },
];

const MACRO_PREFERENCES = [
  { value: "balanced", label: "Bilanciata", macros: "30P / 40C / 30F" },
  { value: "high_protein", label: "High Protein", macros: "40P / 35C / 25F" },
  { value: "high_carb", label: "High Carb", macros: "25P / 55C / 20F" },
  { value: "low_carb", label: "Low Carb", macros: "35P / 25C / 40F" },
  { value: "keto_macros", label: "Keto", macros: "25P / 5C / 70F" },
];

const MEAL_TIMING_OPTIONS = [
  { value: "standard", label: "🕐 Standard", description: "Colazione-Pranzo-Cena" },
  { value: "intermittent_fasting", label: "⏰ Digiuno Intermittente", description: "Finestra alimentare" },
  { value: "post_workout", label: "🏋️ Post-Workout Focus", description: "Pasto principale post-allenamento" },
  { value: "flexible", label: "🔄 Flessibile", description: "Quando capita" },
];

const COMMON_ALLERGIES = [
  { value: "nuts", label: "🥜 Frutta secca" },
  { value: "peanuts", label: "🥜 Arachidi" },
  { value: "shellfish", label: "🦐 Crostacei" },
  { value: "fish", label: "🐟 Pesce" },
  { value: "eggs", label: "🥚 Uova" },
  { value: "milk", label: "🥛 Latte" },
  { value: "soy", label: "🫘 Soia" },
  { value: "wheat", label: "🌾 Grano" },
  { value: "sesame", label: "🌰 Sesamo" },
];

const COMMON_INTOLERANCES = [
  { value: "lactose", label: "🥛 Lattosio" },
  { value: "gluten", label: "🌾 Glutine" },
  { value: "fructose", label: "🍎 Fruttosio" },
  { value: "histamine", label: "🧪 Istamina" },
  { value: "fodmap", label: "🫘 FODMAP" },
  { value: "caffeine", label: "☕ Caffeina" },
];

const DIETARY_RESTRICTIONS = [
  { value: "halal", label: "☪️ Halal" },
  { value: "kosher", label: "✡️ Kosher" },
  { value: "no_pork", label: "🐷 No maiale" },
  { value: "no_beef", label: "🐄 No manzo" },
  { value: "no_alcohol", label: "🍷 No alcol" },
  { value: "organic_only", label: "🌿 Solo bio" },
  { value: "no_processed", label: "🏭 No processati" },
];

export function NutritionGoalsStep({ onComplete, initialData }: NutritionGoalsStepProps) {
  const [currentSection, setCurrentSection] = useState(0);
  const [nutritionGoal, setNutritionGoal] = useState<NutritionGoalsData["nutrition_goal"] | "">(initialData?.nutrition_goal || "");
  const [dietType, setDietType] = useState<NutritionGoalsData["diet_type"]>(initialData?.diet_type || "standard");
  const [caloriePreference] = useState<NutritionGoalsData["calorie_preference"]>(initialData?.calorie_preference || "auto");
  const [customCalories, setCustomCalories] = useState<string>(initialData?.custom_calories?.toString() || "");
  const [proteinPriority, setProteinPriority] = useState<NutritionGoalsData["protein_priority"]>(initialData?.protein_priority || "moderate");
  const [macroPreference, setMacroPreference] = useState<NutritionGoalsData["macro_preference"]>(initialData?.macro_preference || "balanced");
  const [mealFrequency, setMealFrequency] = useState<number>(initialData?.meal_frequency || 4);
  const [mealTiming, setMealTiming] = useState<NutritionGoalsData["meal_timing"]>(initialData?.meal_timing || "standard");
  const [intermittentWindow, setIntermittentWindow] = useState<NutritionGoalsData["intermittent_window"]>(initialData?.intermittent_window || "16_8");
  const [allergies, setAllergies] = useState<string[]>(initialData?.allergies || []);
  const [intolerances, setIntolerances] = useState<string[]>(initialData?.intolerances || []);
  const [dietaryRestrictions, setDietaryRestrictions] = useState<string[]>(initialData?.dietary_restrictions || []);
  const [budgetPreference, setBudgetPreference] = useState<NutritionGoalsData["budget_preference"]>(initialData?.budget_preference || "medium");
  const [cookingSkill, setCookingSkill] = useState<NutritionGoalsData["cooking_skill"]>(initialData?.cooking_skill || "basic");
  const [mealPrepAvailable, setMealPrepAvailable] = useState(initialData?.meal_prep_available || false);
  const [supplementsInterest, setSupplementsInterest] = useState(initialData?.supplements_interest || false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const totalSections = 5;

  const MAX_VISIBLE_OPTIONS = 6;

  const toggleArrayItem = (arr: string[], setter: React.Dispatch<React.SetStateAction<string[]>>, item: string) => {
    hapticFeedback.selection();
    if (arr.includes(item)) {
      setter(prev => prev.filter(i => i !== item));
    } else {
      setter(prev => [...prev, item]);
    }
  };

  const validateSection = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (currentSection === 0 && !nutritionGoal) {
      newErrors.nutritionGoal = "Seleziona un obiettivo nutrizionale";
    }
    if (currentSection === 0 && nutritionGoal === "custom" && !customCalories) {
      newErrors.customCalories = "Inserisci le calorie personalizzate";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (!validateSection()) {
      hapticFeedback.notification("error");
      return;
    }

    hapticFeedback.selection();
    if (currentSection < totalSections - 1) {
      setCurrentSection(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    hapticFeedback.selection();
    if (currentSection > 0) {
      setCurrentSection(prev => prev - 1);
    }
  };

  const handleSubmit = () => {
    hapticFeedback.notification("success");
    onComplete({
      nutrition_goal: nutritionGoal as NutritionGoalsData["nutrition_goal"],
      diet_type: dietType,
      calorie_preference: caloriePreference,
      custom_calories: customCalories ? parseInt(customCalories) : undefined,
      protein_priority: proteinPriority,
      macro_preference: macroPreference,
      meal_frequency: mealFrequency as NutritionGoalsData["meal_frequency"],
      meal_timing: mealTiming,
      intermittent_window: mealTiming === "intermittent_fasting" ? intermittentWindow : undefined,
      allergies,
      intolerances,
      dietary_restrictions: dietaryRestrictions,
      foods_to_avoid: [], // Will be filled via FoodPreferencesStep
      budget_preference: budgetPreference,
      cooking_skill: cookingSkill,
      meal_prep_available: mealPrepAvailable,
      supplements_interest: supplementsInterest,
    });
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-background to-secondary/10 overflow-y-auto">
      {/* Progress Bar */}
      <div className="px-4 pt-4 safe-area-top">
        <div className="flex gap-1 mb-2">
          {[...Array(totalSections)].map((_, i) => (
            <div
              key={i}
              className={cn(
                "h-1.5 flex-1 rounded-full transition-all duration-300",
                i <= currentSection ? "bg-green-500" : "bg-muted"
              )}
            />
          ))}
        </div>
        <p className="text-xs text-muted-foreground text-right">
          {currentSection + 1} / {totalSections}
        </p>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-4 py-6 pb-32">
        <div className="max-w-md mx-auto animate-in fade-in slide-in-from-right-4 duration-300">

          {/* Section 0: Nutrition Goal */}
          {currentSection === 0 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-green-100 dark:bg-green-950/20 rounded-full flex items-center justify-center">
                  <Flame className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold">Obiettivo Calorico</h2>
                <p className="text-muted-foreground text-sm">
                  Cosa vuoi ottenere con la nutrizione?
                </p>
              </div>

              <div className="grid gap-3">
                {NUTRITION_GOALS.map((goal) => (
                  <button
                    key={goal.value}
                    onClick={() => {
                      setNutritionGoal(goal.value as NutritionGoalsData["nutrition_goal"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "w-full p-4 rounded-xl border-2 text-left transition-all touch-manipulation",
                      nutritionGoal === goal.value
                        ? "border-green-500 bg-green-500/5"
                        : "border-transparent bg-secondary/50 hover:bg-secondary"
                    )}
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <div className="font-semibold">{goal.label}</div>
                        <div className="text-xs text-muted-foreground">{goal.description}</div>
                      </div>
                      {nutritionGoal === goal.value && (
                        <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                          <ChevronRight className="w-4 h-4 text-white" />
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>



              {errors.nutritionGoal && (
                <p className="text-sm text-red-500 text-center">{errors.nutritionGoal}</p>
              )}

              {/* Custom Calories Input */}
              {nutritionGoal === "custom" && (
                <div className="space-y-2 p-4 bg-muted/50 rounded-xl">
                  <label className="text-sm font-medium">Calorie giornaliere target</label>
                  <input
                    type="number"
                    inputMode="numeric"
                    value={customCalories}
                    onChange={(e) => setCustomCalories(e.target.value)}
                    placeholder="es. 2500"
                    className="w-full px-4 py-3 rounded-xl border bg-background text-[16px] focus:ring-2 focus:ring-green-500/20 outline-none"
                    min="1200"
                    max="6000"
                  />
                  {errors.customCalories && (
                    <p className="text-sm text-red-500">{errors.customCalories}</p>
                  )}
                </div>
              )}

              {/* Info box */}
              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-xl flex gap-3">
                <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                <p className="text-xs text-blue-700 dark:text-blue-300">
                  Le calorie esatte verranno calcolate automaticamente in base ai tuoi dati biometrici e livello di attività.
                </p>
              </div>
            </div>
          )}

          {/* Section 1: Diet Type & Macros */}
          {currentSection === 1 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-orange-100 dark:bg-orange-950/20 rounded-full flex items-center justify-center">
                  <Utensils className="w-8 h-8 text-orange-600" />
                </div>
                <h2 className="text-2xl font-bold">Tipo di Dieta</h2>
                <p className="text-muted-foreground text-sm">
                  Che stile alimentare preferisci?
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2">
                {DIET_TYPES.slice(0, MAX_VISIBLE_OPTIONS).map((diet) => (
                  <button
                    key={diet.value}
                    onClick={() => {
                      setDietType(diet.value as NutritionGoalsData["diet_type"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "p-3 rounded-xl text-center transition-all touch-manipulation",
                      dietType === diet.value
                        ? "bg-green-500 text-white"
                        : "bg-secondary hover:bg-secondary/80"
                    )}
                  >
                    <div className="text-sm font-semibold">{diet.label}</div>
                  </button>
                ))}
              </div>

              {/* Protein Priority */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Priorità Proteine</label>
                <div className="grid grid-cols-2 gap-2">
                  {PROTEIN_PRIORITIES.map((prot) => (
                    <button
                      key={prot.value}
                      onClick={() => {
                        setProteinPriority(prot.value as NutritionGoalsData["protein_priority"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "p-3 rounded-xl text-left transition-all touch-manipulation",
                        proteinPriority === prot.value
                          ? "bg-green-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="font-semibold text-sm">{prot.label}</div>
                      <div className={cn(
                        "text-xs",
                        proteinPriority === prot.value ? "text-white/70" : "text-muted-foreground"
                      )}>{prot.grams}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Macro Preference */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Distribuzione Macro</label>
                <div className="grid gap-2">
                  {MACRO_PREFERENCES.map((macro) => (
                    <button
                      key={macro.value}
                      onClick={() => {
                        setMacroPreference(macro.value as NutritionGoalsData["macro_preference"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "p-3 rounded-xl flex justify-between items-center transition-all touch-manipulation",
                        macroPreference === macro.value
                          ? "bg-green-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <span className="font-semibold text-sm">{macro.label}</span>
                      <span className={cn(
                        "text-xs font-mono",
                        macroPreference === macro.value ? "text-white/70" : "text-muted-foreground"
                      )}>{macro.macros}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Section 2: Meal Timing */}
          {currentSection === 2 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-purple-100 dark:bg-purple-950/20 rounded-full flex items-center justify-center">
                  <Timer className="w-8 h-8 text-purple-600" />
                </div>
                <h2 className="text-2xl font-bold">Pasti & Timing</h2>
                <p className="text-muted-foreground text-sm">
                  Quanti pasti e quando?
                </p>
              </div>

              {/* Meal Frequency */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Numero pasti al giorno</label>
                <div className="flex gap-2">
                  {[2, 3, 4, 5, 6].map((num) => (
                    <button
                      key={num}
                      onClick={() => {
                        setMealFrequency(num);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "flex-1 py-4 rounded-xl font-semibold text-lg transition-all touch-manipulation",
                        mealFrequency === num
                          ? "bg-green-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div>

              {/* Meal Timing */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Strategia Timing</label>
                <div className="grid gap-2">
                  {MEAL_TIMING_OPTIONS.map((timing) => (
                    <button
                      key={timing.value}
                      onClick={() => {
                        setMealTiming(timing.value as NutritionGoalsData["meal_timing"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "p-4 rounded-xl text-left transition-all touch-manipulation",
                        mealTiming === timing.value
                          ? "bg-green-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="font-semibold">{timing.label}</div>
                      <div className={cn(
                        "text-xs",
                        mealTiming === timing.value ? "text-white/70" : "text-muted-foreground"
                      )}>{timing.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* IF Window */}
              {mealTiming === "intermittent_fasting" && (
                <div className="space-y-3 p-4 bg-purple-50 dark:bg-purple-950/20 rounded-xl">
                  <label className="text-sm font-medium">Finestra Digiuno</label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { value: "16_8", label: "16:8", description: "8h cibo" },
                      { value: "18_6", label: "18:6", description: "6h cibo" },
                      { value: "20_4", label: "20:4", description: "4h cibo" },
                    ].map((window) => (
                      <button
                        key={window.value}
                        onClick={() => {
                          setIntermittentWindow(window.value as NutritionGoalsData["intermittent_window"]);
                          hapticFeedback.selection();
                        }}
                        className={cn(
                          "p-3 rounded-xl text-center transition-all touch-manipulation",
                          intermittentWindow === window.value
                            ? "bg-purple-500 text-white"
                            : "bg-background hover:bg-secondary"
                        )}
                      >
                        <div className="font-bold">{window.label}</div>
                        <div className="text-xs opacity-70">{window.description}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Section 3: Allergies & Restrictions */}
          {currentSection === 3 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-red-100 dark:bg-red-950/20 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-8 h-8 text-red-600" />
                </div>
                <h2 className="text-2xl font-bold">Allergie & Restrizioni</h2>
                <p className="text-muted-foreground text-sm">
                  ⚠️ Importante per la tua sicurezza
                </p>
              </div>

              {/* Allergies */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Allergie alimentari</label>
                <div className="flex flex-wrap gap-2">
                  {COMMON_ALLERGIES.map((allergy) => (
                    <button
                      key={allergy.value}
                      onClick={() => toggleArrayItem(allergies, setAllergies, allergy.value)}
                      className={cn(
                        "px-3 py-2 rounded-full text-sm transition-all touch-manipulation",
                        allergies.includes(allergy.value)
                          ? "bg-red-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {allergy.label}
                    </button>
                  ))}
                </div>


              </div>

              {/* Intolerances */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Intolleranze</label>
                <div className="flex flex-wrap gap-2">
                  {COMMON_INTOLERANCES.map((intol) => (
                    <button
                      key={intol.value}
                      onClick={() => toggleArrayItem(intolerances, setIntolerances, intol.value)}
                      className={cn(
                        "px-3 py-2 rounded-full text-sm transition-all touch-manipulation",
                        intolerances.includes(intol.value)
                          ? "bg-orange-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {intol.label}
                    </button>
                  ))}
                </div>


              </div>

              {/* Dietary Restrictions */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Restrizioni alimentari</label>
                <div className="flex flex-wrap gap-2">
                  {DIETARY_RESTRICTIONS.map((restr) => (
                    <button
                      key={restr.value}
                      onClick={() => toggleArrayItem(dietaryRestrictions, setDietaryRestrictions, restr.value)}
                      className={cn(
                        "px-3 py-2 rounded-full text-sm transition-all touch-manipulation",
                        dietaryRestrictions.includes(restr.value)
                          ? "bg-blue-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {restr.label}
                    </button>
                  ))}
                </div>


              </div>

              {/* None selected notice */}
              {allergies.length === 0 && intolerances.length === 0 && dietaryRestrictions.length === 0 && (
                <div className="p-3 bg-green-50 dark:bg-green-950/20 rounded-xl text-center">
                  <p className="text-sm text-green-700 dark:text-green-300">
                    ✅ Nessuna restrizione selezionata - ottimo!
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Section 4: Budget & Cooking */}
          {currentSection === 4 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-yellow-100 dark:bg-yellow-950/20 rounded-full flex items-center justify-center">
                  <DollarSign className="w-8 h-8 text-yellow-600" />
                </div>
                <h2 className="text-2xl font-bold">Budget & Cucina</h2>
                <p className="text-muted-foreground text-sm">
                  Per ricette e pasti su misura
                </p>
              </div>

              {/* Budget */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Budget settimanale spesa</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: "low", label: "💰 Economico", description: "< €50/sett" },
                    { value: "medium", label: "💰💰 Medio", description: "€50-100/sett" },
                    { value: "high", label: "💰💰💰 Alto", description: "€100-150/sett" },
                    { value: "no_limit", label: "💎 Illimitato", description: "Qualità top" },
                  ].map((budget) => (
                    <button
                      key={budget.value}
                      onClick={() => {
                        setBudgetPreference(budget.value as NutritionGoalsData["budget_preference"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "p-3 rounded-xl text-left transition-all touch-manipulation",
                        budgetPreference === budget.value
                          ? "bg-green-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="font-semibold text-sm">{budget.label}</div>
                      <div className={cn(
                        "text-xs",
                        budgetPreference === budget.value ? "text-white/70" : "text-muted-foreground"
                      )}>{budget.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Cooking Skill */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Abilità in cucina</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: "none", label: "🔥 Zero", description: "Solo microonde" },
                    { value: "basic", label: "🍳 Base", description: "Piatti semplici" },
                    { value: "intermediate", label: "👨‍🍳 Intermedio", description: "So cucinare" },
                    { value: "advanced", label: "🎖️ Avanzato", description: "Chef casalingo" },
                  ].map((skill) => (
                    <button
                      key={skill.value}
                      onClick={() => {
                        setCookingSkill(skill.value as NutritionGoalsData["cooking_skill"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "p-3 rounded-xl text-left transition-all touch-manipulation",
                        cookingSkill === skill.value
                          ? "bg-green-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="font-semibold text-sm">{skill.label}</div>
                      <div className={cn(
                        "text-xs",
                        cookingSkill === skill.value ? "text-white/70" : "text-muted-foreground"
                      )}>{skill.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Toggle options */}
              <div className="space-y-3 pt-4 border-t">
                {/* Meal Prep */}
                <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-xl">
                  <div>
                    <div className="font-medium">Meal Prep disponibile?</div>
                    <div className="text-xs text-muted-foreground">Puoi preparare pasti in anticipo?</div>
                  </div>
                  <button
                    onClick={() => {
                      setMealPrepAvailable(!mealPrepAvailable);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "w-14 h-8 rounded-full transition-all relative",
                      mealPrepAvailable ? "bg-green-500" : "bg-muted"
                    )}
                  >
                    <div className={cn(
                      "w-6 h-6 bg-white rounded-full absolute top-1 transition-all",
                      mealPrepAvailable ? "left-7" : "left-1"
                    )} />
                  </button>
                </div>

                {/* Supplements Interest */}
                <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-xl">
                  <div>
                    <div className="font-medium">Interesse integratori?</div>
                    <div className="text-xs text-muted-foreground">Vuoi suggerimenti integratori?</div>
                  </div>
                  <button
                    onClick={() => {
                      setSupplementsInterest(!supplementsInterest);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "w-14 h-8 rounded-full transition-all relative",
                      supplementsInterest ? "bg-green-500" : "bg-muted"
                    )}
                  >
                    <div className={cn(
                      "w-6 h-6 bg-white rounded-full absolute top-1 transition-all",
                      supplementsInterest ? "left-7" : "left-1"
                    )} />
                  </button>
                </div>
              </div>

              {/* Summary */}
              <div className="p-4 bg-muted/50 rounded-xl space-y-2 mt-6">
                <div className="text-sm font-medium">📋 Riepilogo Nutrizione:</div>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>• Obiettivo: {NUTRITION_GOALS.find(g => g.value === nutritionGoal)?.label || '-'}</div>
                  <div>• Dieta: {DIET_TYPES.find(d => d.value === dietType)?.label || '-'}</div>
                  <div>• Pasti: {mealFrequency}x/giorno, timing {mealTiming}</div>
                  <div>• Allergie: {allergies.length || 'nessuna'}</div>
                  <div>• Budget: {budgetPreference}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/80 backdrop-blur-lg border-t safe-area-bottom">
        <div className="max-w-md mx-auto flex gap-3">
          {currentSection > 0 && (
            <button
              onClick={handleBack}
              className="px-6 py-4 rounded-xl font-semibold bg-secondary hover:bg-secondary/80 transition-all touch-manipulation"
            >
              Indietro
            </button>
          )}
          <button
            onClick={handleNext}
            className={cn(
              "flex-1 py-4 rounded-xl font-semibold text-white transition-all touch-manipulation",
              "bg-green-500 hover:bg-green-600 active:scale-98"
            )}
          >
            {currentSection === totalSections - 1 ? "Conferma" : "Continua"}
          </button>
        </div>
      </div>
    </div>
  );
}
