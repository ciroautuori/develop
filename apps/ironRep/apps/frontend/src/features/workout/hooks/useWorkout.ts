import { useSuspenseQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workoutsApi, type Workout } from "../../../lib/api";
import { logger } from "../../../lib/logger";

export const WORKOUT_KEYS = {
  all: ["workout"] as const,
  today: () => [...WORKOUT_KEYS.all, "today"] as const,
};

export function useWorkout() {
  const queryClient = useQueryClient();

  const { data: workout, isLoading, error } = useSuspenseQuery({
    queryKey: WORKOUT_KEYS.today(),
    queryFn: async () => {
      const response = await workoutsApi.getToday();
      if (!response.success || !response.workout) {
        throw new Error(response.message || "Nessun allenamento trovato");
      }
      return response.workout as Workout;
    },
    retry: false,
  });

  const toggleExerciseMutation = useMutation({
    mutationFn: async (exerciseName: string) => {
      await workoutsApi.updateExerciseStatus(workout.id, exerciseName);
    },
    onMutate: async (exerciseName) => {
      await queryClient.cancelQueries({ queryKey: WORKOUT_KEYS.today() });
      const previousWorkout = queryClient.getQueryData<Workout>(WORKOUT_KEYS.today());

      if (previousWorkout) {
        const toggleInList = (list: Workout['warm_up']) =>
          list.map((ex) =>
            ex.name === exerciseName ? { ...ex, completed: !ex.completed } : ex
          );

        const newWorkout = {
          ...previousWorkout,
          warm_up: toggleInList(previousWorkout.warm_up),
          technical_work: toggleInList(previousWorkout.technical_work),
          conditioning: toggleInList(previousWorkout.conditioning),
          cool_down: toggleInList(previousWorkout.cool_down),
        };

        queryClient.setQueryData(WORKOUT_KEYS.today(), newWorkout);
      }

      return { previousWorkout };
    },
    onError: (err, _newTodo, context) => {
      if (context?.previousWorkout) {
        queryClient.setQueryData(WORKOUT_KEYS.today(), context.previousWorkout);
      }
      logger.error("Failed to toggle exercise", { error: err });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: WORKOUT_KEYS.today() });
    },
  });

  const completeWorkoutMutation = useMutation({
    mutationFn: async (data: { painImpact: number; notes: string }) => {
      await workoutsApi.completeWorkout(workout.id, data.painImpact, data.notes);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WORKOUT_KEYS.today() });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] }); // Refresh dashboard
    },
  });

  return {
    workout,
    isLoading,
    error,
    toggleExercise: toggleExerciseMutation.mutate,
    completeWorkout: completeWorkoutMutation.mutateAsync,
  };
}
