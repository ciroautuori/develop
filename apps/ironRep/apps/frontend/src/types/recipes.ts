export interface RecipeIngredient {
    food_id: string;
    name: string;
    brand?: string;
    grams: number;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
}

export interface Recipe {
    id: string;
    user_id: string;
    name: string;
    description?: string;
    ingredients: RecipeIngredient[];

    // Totals
    total_calories: number;
    total_protein: number;
    total_carbs: number;
    total_fat: number;

    servings: number;
    prep_time_minutes?: number;
    instructions?: string;

    created_at: string;
    updated_at: string;
}

export interface CreateRecipePayload {
    name: string;
    description?: string;
    ingredients: RecipeIngredient[];
    servings: number;
    prep_time_minutes?: number;
    instructions?: string;
}

export interface UpdateRecipePayload {
    name?: string;
    description?: string;
    ingredients?: RecipeIngredient[];
    servings?: number;
    prep_time_minutes?: number;
    instructions?: string;
}
