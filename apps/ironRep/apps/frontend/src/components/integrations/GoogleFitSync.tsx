/**
 * GoogleFitSync - Sync and display Google Fit biometric data
 */
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Heart, Footprints, Flame, RefreshCw, Loader2, Check } from "lucide-react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
 import { authToken } from "../../lib/authToken";
import { getApiUrl } from "../../config/api.config";

async function checkGoogleStatus(): Promise<{ connected: boolean; fit_sync_enabled?: boolean; last_fit_sync_at?: string }> {
  const token = authToken.get();
  const response = await fetch(getApiUrl("/google/auth/status"), { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) return { connected: false };
  return response.json();
}

interface FitData {
  success: boolean;
  weight: Array<{ date: string; weight_kg: number }>;
  steps: Array<{ date: string; steps: number }>;
  heart_rate: Array<{ date: string; avg_hr: number; min_hr: number; max_hr: number }>;
  calories_today: number;
  synced_at: string;
}

async function syncFitData(days: number = 7): Promise<FitData> {
  const token = authToken.get();
  const response = await fetch(getApiUrl(`/google/fit/sync?days=${days}`), {
    method: "POST", headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Sync failed");
  return response.json();
}

interface Props { className?: string; showFullData?: boolean; }

export function GoogleFitSync({ className, showFullData = false }: Props) {
  const queryClient = useQueryClient();
  const [lastSync, setLastSync] = useState<FitData | null>(null);
  const { data: status, isLoading: statusLoading } = useQuery({ queryKey: ["google-status"], queryFn: checkGoogleStatus, staleTime: 60_000 });

  const mutation = useMutation({
    mutationFn: () => syncFitData(7),
    onSuccess: (data) => { setLastSync(data); queryClient.invalidateQueries({ queryKey: ["google-status"] }); hapticFeedback.notification("success"); },
    onError: () => hapticFeedback.notification("error"),
  });

  if (statusLoading) return <div className="animate-pulse h-24 bg-muted/50 rounded-xl" />;
  if (!status?.connected || !status?.fit_sync_enabled) return null;

  const todaySteps = lastSync?.steps?.[0]?.steps || 0;
  const todayHr = lastSync?.heart_rate?.[0];
  const latestWeight = lastSync?.weight?.[0]?.weight_kg;

  return (
    <div className={cn("p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-xl border border-green-200 dark:border-green-800", className)}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2"><Activity className="w-5 h-5 text-green-600" /><span className="font-semibold text-green-900 dark:text-green-100">Google Fit</span></div>
        <button onClick={() => mutation.mutate()} disabled={mutation.isPending} className={cn("flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 hover:bg-green-200 active:scale-95 touch-manipulation min-h-[36px]", mutation.isPending && "opacity-50")}>
          {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : lastSync ? <Check className="w-4 h-4" /> : <RefreshCw className="w-4 h-4" />}
          <span>{mutation.isPending ? "Sincronizzando..." : lastSync ? "Sincronizzato" : "Sincronizza"}</span>
        </button>
      </div>

      {lastSync && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-white/60 dark:bg-white/5 rounded-lg">
            <div className="flex items-center gap-2 mb-1"><Footprints className="w-4 h-4 text-blue-600" /><span className="text-xs text-muted-foreground">Passi Oggi</span></div>
            <div className="text-lg font-bold text-blue-700 dark:text-blue-300">{todaySteps.toLocaleString()}</div>
          </div>
          <div className="p-3 bg-white/60 dark:bg-white/5 rounded-lg">
            <div className="flex items-center gap-2 mb-1"><Flame className="w-4 h-4 text-orange-600" /><span className="text-xs text-muted-foreground">Calorie</span></div>
            <div className="text-lg font-bold text-orange-700 dark:text-orange-300">{(lastSync.calories_today || 0).toLocaleString()}</div>
          </div>
          {todayHr && (
            <div className="p-3 bg-white/60 dark:bg-white/5 rounded-lg">
              <div className="flex items-center gap-2 mb-1"><Heart className="w-4 h-4 text-red-600" /><span className="text-xs text-muted-foreground">Battito</span></div>
              <div className="text-lg font-bold text-red-700 dark:text-red-300">{todayHr.avg_hr} <span className="text-xs font-normal">bpm</span></div>
            </div>
          )}
          {latestWeight && (
            <div className="p-3 bg-white/60 dark:bg-white/5 rounded-lg">
              <div className="flex items-center gap-2 mb-1"><Activity className="w-4 h-4 text-purple-600" /><span className="text-xs text-muted-foreground">Peso</span></div>
              <div className="text-lg font-bold text-purple-700 dark:text-purple-300">{latestWeight} <span className="text-xs font-normal">kg</span></div>
            </div>
          )}
        </div>
      )}

      {showFullData && lastSync?.steps && lastSync.steps.length > 1 && (
        <div className="mt-4 pt-4 border-t border-green-200 dark:border-green-800">
          <div className="text-sm font-medium text-green-900 dark:text-green-100 mb-2">Ultimi 7 giorni</div>
          <div className="grid grid-cols-7 gap-1">{lastSync.steps.slice(0, 7).reverse().map((day, i) => (
            <div key={i} className="text-center"><div className="h-16 w-full bg-green-200 dark:bg-green-800 rounded flex items-end justify-center" style={{ height: `${Math.min(100, (day.steps / 10000) * 100)}%` }} />
              <div className="text-xs text-muted-foreground mt-1">{new Date(day.date).toLocaleDateString('it', { weekday: 'narrow' })}</div>
            </div>
          ))}</div>
        </div>
      )}

      {status.last_fit_sync_at && <div className="mt-3 text-xs text-muted-foreground">Ultimo sync: {new Date(status.last_fit_sync_at).toLocaleString('it')}</div>}
    </div>
  );
}

export default GoogleFitSync;
