import { createLazyFileRoute } from "@tanstack/react-router";
import { BiometricsDashboard } from "../features/biometrics/BiometricsDashboard";
import { Suspense } from "react";
import { BiometricsFormSkeleton } from "../components/ui/Skeletons";

export const Route = createLazyFileRoute("/biometrics")({
  component: BiometricsPage,
});

function BiometricsPage() {
  return (
    <div className="container mx-auto py-6 px-4">
      <Suspense fallback={<BiometricsFormSkeleton />}>
        <BiometricsDashboard />
      </Suspense>
    </div>
  );
}
