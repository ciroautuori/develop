import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { biometricsApi, type BiometricData } from "../../lib/api";
import { toast } from "sonner";
import { useState } from "react";
import { logger } from "../../lib/logger";
import { touchTarget } from "../../lib/touch-targets";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";

const formSchema = z.object({
  weight_kg: z.number().min(30).max(300).optional(),
  height_cm: z.number().min(100).max(250).optional(),
  body_fat_percentage: z.number().min(0).max(100).optional(),
  muscle_mass_kg: z.number().min(0).max(200).optional(),
  resting_heart_rate: z.number().min(30).max(200).optional(),
  blood_pressure_systolic: z.number().min(60).max(250).optional(),
  blood_pressure_diastolic: z.number().min(40).max(150).optional(),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

interface BiometricsFormProps {
  onSuccess?: () => void;
}

export function BiometricsForm({
  onSuccess,
}: BiometricsFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      weight_kg: undefined,
      height_cm: undefined,
      body_fat_percentage: undefined,
      muscle_mass_kg: undefined,
      resting_heart_rate: undefined,
      blood_pressure_systolic: undefined,
      blood_pressure_diastolic: undefined,
      notes: "",
    },
  });

  const onSubmit = async (values: FormData) => {
    try {
      setIsSubmitting(true);
      hapticFeedback.impact("medium");

      const data: BiometricData = {
        date: new Date().toISOString(),
        ...values,
      };

      await biometricsApi.create(data);
      hapticFeedback.notification("success");
      toast.success("Dati biometrici salvati con successo!");
      form.reset();
      onSuccess?.();
    } catch (error) {
      logger.error('Error saving biometrics', { error });
      hapticFeedback.notification("error");
      toast.error("Errore nel salvataggio dei dati");
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputClasses = cn(
    "w-full h-12 px-4 py-3 border-2 border-input rounded-xl bg-background",
    "text-base focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary",
    "transition-all duration-200"
  );

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-5">
        <div className="space-y-3">
          <label className="text-base font-semibold">Peso (kg)</label>
          <input
            type="number"
            step="0.1"
            {...form.register("weight_kg", { valueAsNumber: true })}
            className={inputClasses}
            placeholder="es. 75.5"
          />
          {form.formState.errors.weight_kg && (
            <p className="text-sm text-destructive">
              {form.formState.errors.weight_kg.message}
            </p>
          )}
        </div>

        <div className="space-y-3">
          <label className="text-base font-semibold">Altezza (cm)</label>
          <input
            type="number"
            {...form.register("height_cm", { valueAsNumber: true })}
            className={inputClasses}
            placeholder="es. 175"
          />
          {form.formState.errors.height_cm && (
            <p className="text-sm text-destructive">
              {form.formState.errors.height_cm.message}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-5">
        <div className="space-y-3">
          <label className="text-base font-semibold">Massa Grassa (%)</label>
          <input
            type="number"
            step="0.1"
            {...form.register("body_fat_percentage", { valueAsNumber: true })}
            className={inputClasses}
            placeholder="es. 18.5"
          />
        </div>

        <div className="space-y-3">
          <label className="text-base font-semibold">Massa Muscolare (kg)</label>
          <input
            type="number"
            step="0.1"
            {...form.register("muscle_mass_kg", { valueAsNumber: true })}
            className={inputClasses}
            placeholder="es. 55.2"
          />
        </div>
      </div>

      <div className="space-y-3">
        <label className="text-base font-semibold">
          Frequenza Cardiaca a Riposo (bpm)
        </label>
        <input
          type="number"
          {...form.register("resting_heart_rate", { valueAsNumber: true })}
          className={inputClasses}
          placeholder="es. 65"
        />
      </div>

      <div className="space-y-3">
        <label className="text-base font-semibold">Pressione Sanguigna</label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <input
              type="number"
              {...form.register("blood_pressure_systolic", {
                valueAsNumber: true,
              })}
              className={inputClasses}
              placeholder="Sistolica (es. 120)"
            />
          </div>
          <div>
            <input
              type="number"
              {...form.register("blood_pressure_diastolic", {
                valueAsNumber: true,
              })}
              className={inputClasses}
              placeholder="Diastolica (es. 80)"
            />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <label className="text-base font-semibold">Note (opzionale)</label>
        <textarea
          {...form.register("notes")}
          rows={4}
          className={cn(
            "w-full px-4 py-3 border-2 border-input rounded-xl bg-background",
            "text-base focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary",
            "resize-none transition-all duration-200"
          )}
          placeholder="Aggiungi eventuali note..."
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className={cn(
          "w-full bg-primary text-primary-foreground rounded-xl font-bold text-lg",
          "hover:bg-primary/90 active:scale-98 transition-all shadow-lg",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "h-14 px-6 py-4",
          touchTarget.manipulation
        )}
      >
        {isSubmitting ? "Salvataggio..." : "Salva Dati Biometrici"}
      </button>
    </form>
  );
}
