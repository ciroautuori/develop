import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { DailyMealPlan, MealFood } from "../types/meal.types";
import type { FoodItem } from "../types/food.types";

interface MealPlannerState {
  currentWeek: DailyMealPlan[];
  selectedDay: string;
  selectedMeal: "breakfast" | "lunch" | "dinner" | "snack" | null;

  // Actions
  addFoodToMeal: (
    day: string,
    mealType: "breakfast" | "lunch" | "dinner" | "snack",
    food: FoodItem
  ) => void;
  removeFoodFromMeal: (
    day: string,
    mealType: "breakfast" | "lunch" | "dinner" | "snack",
    foodId: string
  ) => void;
  setSelectedDay: (day: string) => void;
  setSelectedMeal: (
    meal: "breakfast" | "lunch" | "dinner" | "snack" | null
  ) => void;
  initWeek: () => void;
  setDailyTargetsForWeek: (targets: { calories: number; protein: number; carbs: number; fat: number }) => void;
  setFoodsForMeal: (
    day: string,
    mealType: "breakfast" | "lunch" | "dinner" | "snack",
    foods: MealFood[]
  ) => void;
}

const createEmptyDay = (date: string): DailyMealPlan => ({
  date,
  meals: {
    breakfast: {
      foods: [],
      totalCalories: 0,
      totalProtein: 0,
      totalCarbs: 0,
      totalFat: 0,
    },
    lunch: {
      foods: [],
      totalCalories: 0,
      totalProtein: 0,
      totalCarbs: 0,
      totalFat: 0,
    },
    dinner: {
      foods: [],
      totalCalories: 0,
      totalProtein: 0,
      totalCarbs: 0,
      totalFat: 0,
    },
    snack: {
      foods: [],
      totalCalories: 0,
      totalProtein: 0,
      totalCarbs: 0,
      totalFat: 0,
    },
  },
  dailyTargets: { calories: 0, protein: 0, carbs: 0, fat: 0 },
});

export const useMealPlannerStore = create<MealPlannerState>()(
  persist(
    (set) => ({
      currentWeek: [],
      selectedDay: new Date().toISOString().split("T")[0],
      selectedMeal: null,

      initWeek: () => {
        const today = new Date();
        // Start from Monday
        const day = today.getDay();
        const diff = today.getDate() - day + (day === 0 ? -6 : 1); // adjust when day is sunday
        const monday = new Date(today.setDate(diff));

        const week: DailyMealPlan[] = [];
        for (let i = 0; i < 7; i++) {
          const date = new Date(monday);
          date.setDate(monday.getDate() + i);
          week.push(createEmptyDay(date.toISOString().split("T")[0]));
        }
        set({ currentWeek: week });
      },

      addFoodToMeal: (day, mealType, food) =>
        set((state) => {
          const dayIndex = state.currentWeek.findIndex((d) => d.date === day);
          if (dayIndex === -1) return state;

          const mealFood: MealFood = { ...food, quantity: 100 };
          const oldMeal = state.currentWeek[dayIndex].meals[mealType];

          // Immutable update: spread everything
          const newMeal = {
            ...oldMeal,
            foods: [...oldMeal.foods, mealFood],
            totalCalories: oldMeal.totalCalories + food.calories,
            totalProtein: oldMeal.totalProtein + food.protein,
            totalCarbs: oldMeal.totalCarbs + food.carbs,
            totalFat: oldMeal.totalFat + food.fat,
          };

          const newWeek = [...state.currentWeek];
          newWeek[dayIndex] = {
            ...newWeek[dayIndex],
            meals: {
              ...newWeek[dayIndex].meals,
              [mealType]: newMeal,
            },
          };

          return { currentWeek: newWeek };
        }),

      removeFoodFromMeal: (day, mealType, foodId) =>
        set((state) => {
          const dayIndex = state.currentWeek.findIndex((d) => d.date === day);
          if (dayIndex === -1) return state;

          const oldMeal = state.currentWeek[dayIndex].meals[mealType];
          const foodToRemove = oldMeal.foods.find((f) => f.id === foodId);
          if (!foodToRemove) return state;

          // Immutable update: filter foods and update totals
          const newMeal = {
            ...oldMeal,
            foods: oldMeal.foods.filter((f) => f.id !== foodId),
            totalCalories: oldMeal.totalCalories - foodToRemove.calories,
            totalProtein: oldMeal.totalProtein - foodToRemove.protein,
            totalCarbs: oldMeal.totalCarbs - foodToRemove.carbs,
            totalFat: oldMeal.totalFat - foodToRemove.fat,
          };

          const newWeek = [...state.currentWeek];
          newWeek[dayIndex] = {
            ...newWeek[dayIndex],
            meals: {
              ...newWeek[dayIndex].meals,
              [mealType]: newMeal,
            },
          };

          return { currentWeek: newWeek };
        }),

      setSelectedDay: (day: string) => set({ selectedDay: day }),
      setSelectedMeal: (
        meal: "breakfast" | "lunch" | "dinner" | "snack" | null
      ) => set({ selectedMeal: meal }),

      setDailyTargetsForWeek: (targets) =>
        set((state) => {
          if (state.currentWeek.length === 0) return state;
          return {
            currentWeek: state.currentWeek.map((d) => ({
              ...d,
              dailyTargets: {
                calories: targets.calories,
                protein: targets.protein,
                carbs: targets.carbs,
                fat: targets.fat,
              },
            })),
          };
        }),

      setFoodsForMeal: (day, mealType, foods) =>
        set((state) => {
          const dayIndex = state.currentWeek.findIndex((d) => d.date === day);
          if (dayIndex === -1) return state;

          const totalCalories = foods.reduce((acc, f) => acc + f.calories, 0);
          const totalProtein = foods.reduce((acc, f) => acc + f.protein, 0);
          const totalCarbs = foods.reduce((acc, f) => acc + f.carbs, 0);
          const totalFat = foods.reduce((acc, f) => acc + f.fat, 0);

          const oldDay = state.currentWeek[dayIndex];
          const newWeek = [...state.currentWeek];
          newWeek[dayIndex] = {
            ...oldDay,
            meals: {
              ...oldDay.meals,
              [mealType]: {
                ...oldDay.meals[mealType],
                foods,
                totalCalories,
                totalProtein,
                totalCarbs,
                totalFat,
              },
            },
          };

          return { currentWeek: newWeek };
        }),
    }),
    {
      name: "meal-planner-storage",
    }
  )
);
