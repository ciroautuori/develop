import { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import { biometricsApi, type BiometricData } from "../../lib/api";
import { BiometricsForm } from "./BiometricsForm";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import { Activity, Heart, Scale, TrendingUp } from "lucide-react";
import { hapticFeedback } from "../../lib/haptics";

interface BiometricsDashboardProps {
  // No props needed - uses authenticated user
}

export function BiometricsDashboard({ }: BiometricsDashboardProps) {
  const [latest, setLatest] = useState<BiometricData | null>(null);
  const [history, setHistory] = useState<BiometricData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  // Auto-refresh when component becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadData();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [latestRes, historyRes] = await Promise.all([
        biometricsApi.getLatest(),
        biometricsApi.getHistory(),
      ]);

      if (latestRes && latestRes.success && latestRes.biometric) {
        setLatest(latestRes.biometric);
      }

      if (historyRes && historyRes.success && historyRes.biometrics) {
        setHistory(historyRes.biometrics);
      }
    } catch (error) {
      logger.error('Error loading biometrics', { error });
      hapticFeedback.notification("error");
      // Don't show toast on 404/empty data, just log
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    loadData();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Dati Biometrici</h2>
          <p className="text-xs text-muted-foreground">
            Monitora i tuoi parametri
          </p>
        </div>
        <button
          onClick={() => {
            hapticFeedback.selection();
            setShowForm(!showForm);
          }}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
        >
          {showForm ? "Annulla" : "Aggiungi Dati"}
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-card border rounded-lg p-4">
          <BiometricsForm userId={userId} onSuccess={handleFormSuccess} />
        </div>
      )}

      {/* Latest Data */}
      {latest ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {latest.weight_kg && (
            <div className="bg-card border rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Scale className="text-primary" size={18} />
                <p className="text-xs text-muted-foreground">Peso</p>
              </div>
              <p className="text-xl font-bold">{latest.weight_kg} kg</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {format(new Date(latest.date), "dd MMM yyyy", { locale: it })}
              </p>
            </div>
          )}

          {latest.body_fat_percentage && (
            <div className="bg-card border rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="text-primary" size={18} />
                <p className="text-xs text-muted-foreground">Massa Grassa</p>
              </div>
              <p className="text-xl font-bold">
                {latest.body_fat_percentage}%
              </p>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {format(new Date(latest.date), "dd MMM yyyy", { locale: it })}
              </p>
            </div>
          )}

          {latest.muscle_mass_kg && (
            <div className="bg-card border rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="text-primary" size={18} />
                <p className="text-xs text-muted-foreground">Massa Muscolare</p>
              </div>
              <p className="text-xl font-bold">{latest.muscle_mass_kg} kg</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {format(new Date(latest.date), "dd MMM yyyy", { locale: it })}
              </p>
            </div>
          )}

          {latest.resting_heart_rate && (
            <div className="bg-card border rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Heart className="text-primary" size={18} />
                <p className="text-xs text-muted-foreground">FC Riposo</p>
              </div>
              <p className="text-xl font-bold">
                {latest.resting_heart_rate} bpm
              </p>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {format(new Date(latest.date), "dd MMM yyyy", { locale: it })}
              </p>
            </div>
          )}

          {latest.blood_pressure_systolic &&
            latest.blood_pressure_diastolic && (
              <div className="bg-card border rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Heart className="text-primary" size={18} />
                  <p className="text-xs text-muted-foreground">Pressione</p>
                </div>
                <p className="text-xl font-bold">
                  {latest.blood_pressure_systolic}/
                  {latest.blood_pressure_diastolic}
                </p>
                <p className="text-[10px] text-muted-foreground mt-0.5">mmHg</p>
              </div>
            )}
        </div>
      ) : (
        <div className="text-center py-12 bg-muted/50 rounded-lg">
          <p className="text-muted-foreground mb-4">
            Nessun dato biometrico registrato
          </p>
          <button
            onClick={() => {
              hapticFeedback.selection();
              setShowForm(true);
            }}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Aggiungi Primo Dato
          </button>
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div className="bg-card border rounded-lg p-4">
          <h3 className="text-base font-semibold mb-3">
            Storico (30 giorni)
          </h3>
          <div className="space-y-2">
            {history.map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between p-2 bg-muted/50 rounded-lg"
              >
                <div>
                  <p className="font-medium text-sm">
                    {format(new Date(entry.date), "EEE dd MMM", {
                      locale: it,
                    })}
                  </p>
                  <div className="flex gap-3 mt-0.5 text-xs text-muted-foreground">
                    {entry.weight_kg && <span>Peso: {entry.weight_kg}kg</span>}
                    {entry.body_fat_percentage && (
                      <span>BF: {entry.body_fat_percentage}%</span>
                    )}
                    {entry.resting_heart_rate && (
                      <span>FC: {entry.resting_heart_rate}bpm</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
