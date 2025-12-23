import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Activity, Heart, Flame, RefreshCw, Smartphone } from "lucide-react";
import { format } from "date-fns";
import { it } from "date-fns/locale";

import { Card, CardContent, CardHeader, CardTitle } from "../../shared/components/ui/card";
import { Button } from "../../shared/components/ui/button";
import { toast } from "../../components/ui/Toast";
import { googleFitApi } from "../../lib/api/googleFit";
import { cn } from "../../lib/utils";

export function GoogleFitWidget() {
    const queryClient = useQueryClient();
    const [isSyncing, setIsSyncing] = useState(false);

    const { data: status } = useQuery({
        queryKey: ["google-fit-status"],
        queryFn: googleFitApi.getConnectionStatus,
    });

    const syncMutation = useMutation({
        mutationFn: () => googleFitApi.sync(7),
        onMutate: () => setIsSyncing(true),
        onSuccess: (data) => {
            toast.success("Dati aggiornati ✨", "Sincronizzazione da Google Fit completata.");
            queryClient.invalidateQueries({ queryKey: ["google-fit-status"] });
            queryClient.setQueryData(["google-fit-data"], data);
        },
        onError: () => {
            toast.error("Errore sincronizzazione", "Controlla la connessione con Google Fit.");
        },
        onSettled: () => setIsSyncing(false),
    });

    // Fetch data only if connected
    const { data: fitData } = useQuery({
        queryKey: ["google-fit-data"],
        queryFn: () => googleFitApi.sync(7), // Initial fetch on load
        enabled: !!status?.connected && !!status?.fit_sync_enabled,
        staleTime: 1000 * 60 * 15, // 15 mins
    });

    const handleConnect = () => {
        // Redirect to backend auth URL logic - usually handled by specific auth component or direct link
        // For now we assume typical flow
        window.location.href = "/api/google/auth/url"; // Simplified for now, should use API URL getter
    };

    if (!status?.connected) {
        return (
            <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100 dark:from-blue-950/20 dark:to-indigo-950/20 dark:border-blue-900/50">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                        <Activity className="h-4 w-4" /> Google Fit
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center py-6 gap-3">
                    <Smartphone className="h-10 w-10 text-muted-foreground/50" />
                    <p className="text-sm text-center text-muted-foreground">Collega Google Fit per tracciare passi, calorie e peso automaticamente.</p>
                    <Button size="sm" variant="outline" className="gap-2" asChild>
                        <a href="/api/google/auth/url" target="_blank" rel="noopener noreferrer">
                            Connetti
                        </a>
                    </Button>
                </CardContent>
            </Card>
        );
    }

    const stepsToday = fitData?.steps?.[0]?.steps ?? 0;
    const calsToday = fitData?.calories_today ?? 0;
    const weight = fitData?.weight?.[0]?.weight_kg;
    const hr = fitData?.heart_rate?.[0]?.avg_hr;

    return (
        <Card className="overflow-hidden">
            <CardHeader className="py-3 bg-muted/30 border-b flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">
                        <Activity className="h-3.5 w-3.5" />
                    </span>
                    Google Fit
                </CardTitle>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-muted-foreground"
                    onClick={() => syncMutation.mutate()}
                    disabled={isSyncing}
                >
                    <RefreshCw className={cn("h-3.5 w-3.5", isSyncing && "animate-spin")} />
                </Button>
            </CardHeader>
            <CardContent className="p-0">
                <div className="grid grid-cols-2 divide-x divide-y">
                    {/* Steps */}
                    <div className="p-3 flex flex-col items-center justify-center text-center">
                        <div className="text-xs text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Passi Oggi</div>
                        <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                            {stepsToday.toLocaleString()}
                        </div>
                    </div>

                    {/* Calories */}
                    <div className="p-3 flex flex-col items-center justify-center text-center">
                        <div className="text-xs text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Kcal</div>
                        <div className="text-xl font-bold text-orange-500">
                            <div className="flex items-center gap-1">
                                <Flame className="h-3.5 w-3.5 fill-current" />
                                {calsToday}
                            </div>
                        </div>
                    </div>

                    {/* Weight */}
                    <div className="p-3 flex flex-col items-center justify-center text-center">
                        <div className="text-xs text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Peso</div>
                        <div className="text-lg font-semibold">
                            {weight ? `${weight} kg` : "--"}
                        </div>
                        {fitData?.weight?.[0]?.date && (
                            <div className="text-[10px] text-muted-foreground mt-0.5">
                                {format(new Date(fitData.weight[0].date), "d MMM", { locale: it })}
                            </div>
                        )}
                    </div>

                    {/* Heart Rate */}
                    <div className="p-3 flex flex-col items-center justify-center text-center">
                        <div className="text-xs text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Battito Medio</div>
                        <div className="text-lg font-semibold text-rose-500">
                            <div className="flex items-center gap-1">
                                <Heart className="h-3.5 w-3.5 fill-current" />
                                {hr ? Math.round(hr) : "--"}
                            </div>
                        </div>
                        <div className="text-[10px] text-muted-foreground mt-0.5">
                            7 giorni
                        </div>
                    </div>
                </div>

                {status?.last_fit_sync_at && (
                    <div className="bg-muted/30 py-1 px-3 text-[10px] text-center text-muted-foreground border-t">
                        Ultimo sync: {format(new Date(status.last_fit_sync_at), "HH:mm")}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
