import { DashboardCardSkeleton, ListSkeleton, Skeleton } from "../../components/ui/Skeletons";

export function DashboardSkeleton() {
  return (
    <div className="space-y-6 pb-20 animate-pulse">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between py-2">
        <div className="flex items-center gap-3">
          <Skeleton className="w-12 h-12 rounded-full" />
          <div className="flex flex-col space-y-2">
            <Skeleton className="w-32 h-5" />
            <Skeleton className="w-24 h-3" />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="w-9 h-9 rounded-full" />
          <Skeleton className="w-9 h-9 rounded-full" />
        </div>
      </div>

      {/* Welcome Banner Skeleton */}
      <Skeleton className="h-16 w-full rounded-2xl" />

      {/* Critical Alerts Skeleton */}
      <Skeleton className="h-24 w-full rounded-xl" />

      {/* CTA Skeleton */}
      <Skeleton className="h-24 w-full rounded-2xl" />

      {/* Status Cards Skeleton */}
      <DashboardCardSkeleton />

      {/* KPI Grid Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
        <DashboardCardSkeleton />
        <DashboardCardSkeleton />
      </div>

      {/* Agents Skeleton */}
      <div>
        <Skeleton className="h-4 w-32 mb-3" />
        <div className="grid grid-cols-1 gap-3">
          <ListSkeleton count={3} />
        </div>
      </div>
    </div>
  );
}
