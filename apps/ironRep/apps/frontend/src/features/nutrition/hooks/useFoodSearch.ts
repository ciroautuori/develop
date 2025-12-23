import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fatSecretApi } from "../api/fatSecretApi";
import { useDebounce } from "../../../shared/hooks/useDebounce";

export function useFoodSearch(query: string) {
  const debouncedQuery = useDebounce(query, 500);

  return useQuery({
    queryKey: ["foods", "search", debouncedQuery],
    queryFn: () => fatSecretApi.searchFoods(debouncedQuery),
    enabled: debouncedQuery.length >= 3,
    staleTime: 0,
  });
}

export function useFoodCategories() {
  return useQuery({
    queryKey: ["foods", "categories"],
    queryFn: () => fatSecretApi.getCategories(),
    staleTime: Infinity, // Never refetch
  });
}

export function useFoodDetails(foodId: string | null) {
  return useQuery({
    queryKey: ["foods", "details", foodId],
    queryFn: () => fatSecretApi.getFoodDetails(foodId!),
    enabled: !!foodId,
  });
}

export function useFoodFavorites(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["foods", "favorites"],
    queryFn: () => fatSecretApi.getFavorites(),
    staleTime: 60 * 1000,
    retry: false,
    enabled: options?.enabled ?? true,
  });
}

export function useToggleFoodFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      foodId,
      isFavorite,
    }: {
      foodId: string;
      isFavorite: boolean;
    }) => {
      if (isFavorite) {
        return fatSecretApi.removeFavorite(foodId);
      }
      return fatSecretApi.addFavorite(foodId);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["foods", "favorites"] });
    },
  });
}
