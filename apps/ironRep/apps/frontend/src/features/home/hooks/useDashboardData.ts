import { useSuspenseQuery } from "@tanstack/react-query";
import { usersApi, progressApi, type UserProfile, type DashboardData } from "../../../lib/api";

export const DASHBOARD_KEYS = {
  all: ["dashboard"] as const,
  profile: () => [...DASHBOARD_KEYS.all, "profile"] as const,
  stats: () => [...DASHBOARD_KEYS.all, "stats"] as const,
};

export function useDashboardData() {
  const profileQuery = useSuspenseQuery({
    queryKey: DASHBOARD_KEYS.profile(),
    queryFn: async () => {
      try {
        return await usersApi.getMe();
      } catch (error) {
        // Fallback for development/unauthenticated
        return null;
      }
    },
  });

  const statsQuery = useSuspenseQuery({
    queryKey: DASHBOARD_KEYS.stats(),
    queryFn: async () => {
      try {
        return await progressApi.getDashboard();
      } catch (error) {
        // Return empty structure if fails
        return {
          stats: {
            total_assessments: 0,
            avg_pain_30_days: 0,
            total_completed_workouts: 0,
            total_weeks: 0,
          },
          recent_pain: [],
          kpis: [],
          recent_workouts: [],
        } as DashboardData;
      }
    },
  });

  return {
    userProfile: profileQuery.data,
    dashboardStats: statsQuery.data,
    isLoading: profileQuery.isLoading || statsQuery.isLoading,
    isError: profileQuery.isError || statsQuery.isError,
    refetch: () => {
      profileQuery.refetch();
      statsQuery.refetch();
    },
  };
}
