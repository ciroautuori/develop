import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi, type UserProfile } from "../../../lib/api";
import { logger } from "../../../lib/logger";

export const PROFILE_KEYS = {
  all: ["profile"] as const,
  me: () => [...PROFILE_KEYS.all, "me"] as const,
  user: (id: string) => [...PROFILE_KEYS.all, id] as const,
};

export function useProfile(userId?: string) {
  const queryClient = useQueryClient();
  const queryKey = userId ? PROFILE_KEYS.user(userId) : PROFILE_KEYS.me();

  const { data: profile, isLoading, error } = useSuspenseQuery({
    queryKey,
    queryFn: async () => {
      if (userId) {
        return await usersApi.getById(userId);
      }
      return await usersApi.getMe();
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: async (data: Partial<UserProfile>) => {
      // If userId is provided, use it. Otherwise assume 'me' but API requires ID for update usually.
      // usersApi.update takes userId. Profile object has ID.
      if (!profile?.id) throw new Error("No profile ID found");
      return await usersApi.update(profile.id, data);
    },
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(queryKey, updatedProfile);
      queryClient.invalidateQueries({ queryKey: ["dashboard"] }); // Update dashboard too
    },
    onError: (err) => {
      logger.error("Failed to update profile", { error: err });
    },
  });

  return {
    profile,
    isLoading,
    error,
    updateProfile: updateProfileMutation.mutateAsync,
    isUpdating: updateProfileMutation.isPending,
  };
}
