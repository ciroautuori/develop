import { z } from "zod";
import { FoodItemSchema } from "./food.types";

export const MealFoodSchema = FoodItemSchema.extend({
  quantity: z.number(),
  selectedServingId: z.string().optional(),
});

export type MealFood = z.infer<typeof MealFoodSchema>;

export interface Meal {
  foods: MealFood[];
  totalCalories: number;
  totalProtein: number;
  totalCarbs: number;
  totalFat: number;
}

export interface DailyMealPlan {
  date: string;
  meals: {
    breakfast: Meal;
    lunch: Meal;
    dinner: Meal;
    snack: Meal;
  };
  dailyTargets: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
}
