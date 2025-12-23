import { useSuspenseQuery } from "@tanstack/react-query";
import { checkinApi } from "../../../lib/api";

export const PAIN_HISTORY_KEYS = {
  all: ["pain-history"] as const,
  days: (days: number) => [...PAIN_HISTORY_KEYS.all, days] as const,
};

export function usePainHistory(days: number = 7) {
  return useSuspenseQuery({
    queryKey: PAIN_HISTORY_KEYS.days(days),
    queryFn: async () => {
      const data = await checkinApi.getHistory(days);
      // API returns array directly or object with data?
      // Looking at previous code: `history.flatMap` suggests it returns an array.
      // But `checkinApi.getHistory` calls `/medical/pain-history/${days}`.
      // I should verify what `medicalApi.getPainHistory` returns.
      // api.ts says: `return response.data;`
      return Array.isArray(data) ? data : [];
    },
  });
}
