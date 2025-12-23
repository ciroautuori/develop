import { createLazyFileRoute } from "@tanstack/react-router";
import { ExercisesBrowser } from "../features/exercises/ExercisesBrowser";
import { Suspense } from "react";
import { ListSkeleton } from "../components/ui/Skeletons";

export const Route = createLazyFileRoute("/exercises")({
  component: ExercisesPage,
});

function ExercisesPage() {
  return (
    <div className="container mx-auto py-4 sm:py-6 px-3 sm:px-4 pb-24">
      <Suspense fallback={<ListSkeleton count={8} />}>
        <ExercisesBrowser />
      </Suspense>
    </div>
  );
}
