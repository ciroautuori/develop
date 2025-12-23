import { z } from "zod";

export const FoodItemSchema = z.object({
  id: z.string(),
  name: z.string(),
  brand: z.string().optional(),
  category: z.string().optional(),
  servings: z
    .array(
      z.object({
        id: z.string(),
        description: z.string(),
        metric_amount: z.number(),
        metric_unit: z.string(),
        calories: z.number(),
        protein: z.number(),
        carbs: z.number(),
        fat: z.number(),
        fiber: z.number().optional(),
        sugar: z.number().optional(),
        sodium: z.number().optional(),
      })
    )
    .optional(),
  calories: z.number(),
  protein: z.number(),
  carbs: z.number(),
  fat: z.number(),
  type: z.string().optional(),
});

export type FoodItem = z.infer<typeof FoodItemSchema>;

export const FoodCategorySchema = z.object({
  id: z.string(),
  name: z.string(),
  icon: z.string().optional(),
});

export type FoodCategory = z.infer<typeof FoodCategorySchema>;
