import { Stethoscope, Dumbbell, Utensils } from "lucide-react";
import { medicalApi, workoutsApi, usersApi, workoutCoachApi, nutritionApi } from "../../../lib/api";
import type { ChatConfig } from "../types";
import { getApiUrl } from "../../../config/api.config";

export const CHAT_CONFIGS: Record<string, ChatConfig> = {
  medical: {
    type: "medical",
    meta: {
      title: "Medical Coach",
      subtitle: "Analisi dolore, recupero, prevenzione infortuni",
      gradient: "from-red-500 to-red-600",
      icon: Stethoscope,
      color: "red-500",
    },
    input: {
      placeholder: "Descrivi il tuo stato di salute...",
      maxLength: 500,
    },
    suggestions: [
      "Come sta andando il mio recupero?",
      "Il dolore che sento è normale?",
      "Devo preoccuparmi dei sintomi attuali?",
      "Quando posso aumentare il carico di lavoro?",
    ],
    api: {
      endpoint: async (message: string, sessionId?: string) => {
        return await medicalApi.ask(message, sessionId);
      },
      contextLoader: async () => {
        try {
          const apiUrl = getApiUrl('/medical/pain-history/7');
          const [profile, painHistory] = await Promise.all([
            usersApi.getMe(),
            fetch(`${apiUrl}/medical/pain-history/7`).then((r) => r.json()),
          ]);
          return {
            user: profile,
            recentPain: Array.isArray(painHistory) ? painHistory.slice(0, 3) : [],
            currentPhase: profile?.current_phase,
          };
        } catch (error) {
          console.error("Failed to load medical context:", error);
          return {};
        }
      },
    },
  },

  workout: {
    type: "workout",
    meta: {
      title: "Workout Coach",
      subtitle: "Programmazione, tecnica, progressione e periodizzazione",
      gradient: "from-blue-500 to-blue-600",
      icon: Dumbbell,
      color: "blue-500",
    },
    input: {
      placeholder: "Chiedi consigli sul tuo allenamento...",
      maxLength: 500,
    },
    suggestions: [
      "Come posso migliorare la tecnica?",
      "Quando posso aumentare il carico?",
      "Quale progressione devo seguire?",
      "Come modifico il workout per il dolore?",
    ],
    api: {
      endpoint: async (message: string, sessionId?: string) => {
        return await workoutCoachApi.ask(message, sessionId);
      },
      contextLoader: async () => {
        try {
          const [todayWorkout, profile] = await Promise.all([
            workoutsApi.getToday(),
            usersApi.getMe(),
          ]);
          return {
            todayWorkout,
            currentPhase: profile?.current_phase,
            weeksInPhase: profile?.weeks_in_current_phase,
          };
        } catch (error) {
          return {};
        }
      },
    },
  },

  nutrition: {
    type: "nutrition",
    meta: {
      title: "Nutrition Coach",
      subtitle: "Piano alimentare, macro, integrazione per recupero",
      gradient: "from-green-500 to-green-600",
      icon: Utensils,
      color: "green-500",
    },
    input: {
      placeholder: "Chiedi consigli nutrizionali...",
      maxLength: 500,
    },
    suggestions: [
      "Come ottimizzare le proteine per il recupero?",
      "Cosa mangiare pre-workout?",
      "Quali integratori sono utili?",
      "Come gestire le calorie?",
    ],
    api: {
      endpoint: async (message: string, sessionId?: string) => {
        return await nutritionApi.ask(message, sessionId);
      },
      contextLoader: async () => {
        try {
          const profile = await usersApi.getMe();
          return {
            currentPhase: profile?.current_phase,
            weeksInPhase: profile?.weeks_in_current_phase,
          };
        } catch (error) {
          console.error("Failed to load nutrition context:", error);
          return {};
        }
      },
    },
  },
};
