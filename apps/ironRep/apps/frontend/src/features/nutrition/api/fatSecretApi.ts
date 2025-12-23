import { apiClient as api } from "@/lib/api";
import type { FoodItem, FoodCategory } from "../types/food.types";

export const fatSecretApi = {
  searchFoods: async (
    query: string,
    page = 0,
    limit = 20
  ): Promise<FoodItem[]> => {
    const response = await api.get("/foods/search", {
      params: { q: query, page, limit },
    });
    return response.data;
  },

  getFoodDetails: async (foodId: string): Promise<FoodItem> => {
    const response = await api.get(`/foods/details/${foodId}`);
    return response.data;
  },

  getCategories: async (): Promise<FoodCategory[]> => {
    const response = await api.get("/foods/categories");
    return response.data;
  },

  getFavorites: async (): Promise<FoodItem[]> => {
    const response = await api.get("/foods/favorites");
    return response.data;
  },

  addFavorite: async (foodId: string): Promise<{ success: boolean }> => {
    const response = await api.post(`/foods/favorites/${foodId}`);
    return response.data;
  },

  removeFavorite: async (foodId: string): Promise<{ success: boolean }> => {
    const response = await api.delete(`/foods/favorites/${foodId}`);
    return response.data;
  },
};
