/**
 * InjuryDetailsStep - Wizard Step for Injury Information
 *
 * Collects: injury_date, diagnosis, injury_description
 * Only shown if medical_mode = "injury_recovery"
 *
 * @production-ready Conditional rendering, medical terminology, validation
 */

import { useState } from "react";
import { Heart, AlertCircle, FileText, Calendar } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

export interface InjuryDetails {
  injury_date: string; // ISO date string
  diagnosis: string;
  injury_description: string;
}

interface InjuryDetailsStepProps {
  onComplete: (data: InjuryDetails) => void;
  onSkip?: () => void;
  initialData?: Partial<InjuryDetails>;
}

const COMMON_INJURIES = [
  "Lower Back Strain/Sprain",
  "Knee Meniscus Tear",
  "Shoulder Rotator Cuff",
  "Ankle Sprain",
  "Hip Flexor Strain",
  "Hamstring Tear",
  "ACL/PCL Tear",
  "Tennis/Golfer Elbow",
  "Wrist Strain",
  "Altro (custom)",
];

export function InjuryDetailsStep({ onComplete, onSkip, initialData }: InjuryDetailsStepProps) {
  // Convert ISO date to YYYY-MM-DD format for HTML date input
  const formatDateForInput = (dateStr?: string): string => {
    if (!dateStr) return "";
    try {
      return new Date(dateStr).toISOString().split('T')[0];
    } catch {
      return dateStr;
    }
  };

  const [injuryDate, setInjuryDate] = useState<string>(formatDateForInput(initialData?.injury_date));
  const [diagnosis, setDiagnosis] = useState<string>(initialData?.diagnosis || "");
  const [customDiagnosis, setCustomDiagnosis] = useState<string>("");
  const [description, setDescription] = useState<string>(initialData?.injury_description || "");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!injuryDate) {
      newErrors.injuryDate = "Seleziona la data dell'infortunio";
    } else {
      const date = new Date(injuryDate);
      const now = new Date();
      const twoYearsAgo = new Date();
      twoYearsAgo.setFullYear(now.getFullYear() - 2);

      if (date > now) {
        newErrors.injuryDate = "La data non può essere nel futuro";
      } else if (date < twoYearsAgo) {
        newErrors.injuryDate = "Infortunio più vecchio di 2 anni - consulta un medico";
      }
    }

    const finalDiagnosis = diagnosis === "Altro (custom)" ? customDiagnosis : diagnosis;
    if (!finalDiagnosis || finalDiagnosis.trim().length < 5) {
      newErrors.diagnosis = "Inserisci una diagnosi (minimo 5 caratteri)";
    }

    if (description && description.length > 500) {
      newErrors.description = "Descrizione troppo lunga (max 500 caratteri)";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) {
      hapticFeedback.notification("error");
      return;
    }

    hapticFeedback.notification("success");
    const finalDiagnosis = diagnosis === "Altro (custom)" ? customDiagnosis : diagnosis;

    onComplete({
      injury_date: new Date(injuryDate).toISOString(),
      diagnosis: finalDiagnosis,
      injury_description: description || "",
    });
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-background to-secondary/10 overflow-hidden">
      {/* Content (NO SCROLL) */}
      <div className="flex-1 overflow-hidden px-4 py-6 pb-safe">
        <div className="max-w-md mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="text-center space-y-2 pt-4">
            <div className="w-16 h-16 mx-auto bg-red-50 dark:bg-red-950/20 rounded-full flex items-center justify-center">
              <Heart className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold">Dettagli Infortunio</h2>
            <p className="text-muted-foreground text-sm px-4">
              Aiutaci a capire il tuo punto di partenza per un recovery sicuro
            </p>
          </div>

          {/* Form Fields */}
          <div className="space-y-4">
            {/* Injury Date */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                Data Infortunio <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={injuryDate}
                onChange={(e) => setInjuryDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation",
                  errors.injuryDate && "border-red-500 focus:ring-red-500/20"
                )}
              />
              {errors.injuryDate && (
                <p className="text-sm text-red-500">{errors.injuryDate}</p>
              )}
            </div>

            {/* Diagnosis - Common Injuries */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-muted-foreground" />
                Diagnosi <span className="text-red-500">*</span>
              </label>
              <select
                value={diagnosis}
                onChange={(e) => {
                  setDiagnosis(e.target.value);
                  hapticFeedback.selection();
                }}
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation",
                  errors.diagnosis && "border-red-500 focus:ring-red-500/20"
                )}
              >
                <option value="">Seleziona il tipo di infortunio...</option>
                {COMMON_INJURIES.map((injury) => (
                  <option key={injury} value={injury}>
                    {injury}
                  </option>
                ))}
              </select>

              {/* Custom Diagnosis Input */}
              {diagnosis === "Altro (custom)" && (
                <input
                  type="text"
                  value={customDiagnosis}
                  onChange={(e) => setCustomDiagnosis(e.target.value)}
                  placeholder="Inserisci la diagnosi specifica..."
                  className={cn(
                    "w-full px-4 py-3 rounded-xl border bg-background",
                    "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                    "touch-manipulation mt-2"
                  )}
                />
              )}

              {errors.diagnosis && (
                <p className="text-sm text-red-500">{errors.diagnosis}</p>
              )}
            </div>

            {/* Description (optional) */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <FileText className="w-4 h-4 text-muted-foreground" />
                Descrizione (opzionale)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Aggiungi dettagli: come è successo, sintomi, trattamenti già ricevuti..."
                rows={4}
                maxLength={500}
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background resize-none",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation",
                  errors.description && "border-red-500 focus:ring-red-500/20"
                )}
              />
              <div className="flex justify-between items-center text-xs text-muted-foreground">
                <span>Aiuta il Medical Agent a personalizzare il protocollo</span>
                <span>{description.length}/500</span>
              </div>
              {errors.description && (
                <p className="text-sm text-red-500">{errors.description}</p>
              )}
            </div>
          </div>

          {/* Warning Box */}
          <div className="p-4 bg-amber-50 dark:bg-amber-950/20 rounded-xl border border-amber-200 dark:border-amber-800">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div className="text-sm text-amber-900 dark:text-amber-200">
                <p className="font-semibold">Importante</p>
                <p className="mt-1">
                  IronRep non sostituisce il parere medico. Consulta sempre un professionista sanitario per diagnosi e trattamento.
                </p>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="space-y-3">
            <button
              onClick={handleSubmit}
              className={cn(
                "w-full py-4 rounded-xl font-semibold text-white transition-all touch-manipulation",
                "bg-primary hover:bg-primary/90 active:scale-98"
              )}
            >
              Continua
            </button>

            {onSkip && (
              <button
                onClick={() => {
                  hapticFeedback.selection();
                  onSkip();
                }}
                className="w-full py-3 text-sm text-muted-foreground hover:text-foreground transition-colors touch-manipulation min-h-[44px]"
              >
                Salta (compila dopo)
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
