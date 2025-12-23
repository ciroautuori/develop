/**
 * BiometricsStep - Wizard Step for Collecting User Biometrics
 *
 * Collects: weight_kg, height_cm, age, sex
 * Used during onboarding wizard to build complete user profile
 *
 * @production-ready Mobile-first, validation, accessibility
 */

import { useState } from "react";
import { Scale, Ruler, Calendar, User } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

export interface BiometricsData {
  weight_kg: number;
  height_cm: number;
  age: number;
  sex: "male" | "female" | "other";
}

interface BiometricsStepProps {
  onComplete: (data: BiometricsData) => void;
  initialData?: Partial<BiometricsData>;
}

export function BiometricsStep({ onComplete, initialData }: BiometricsStepProps) {
  const [weight, setWeight] = useState<string>(initialData?.weight_kg?.toString() || "");
  const [height, setHeight] = useState<string>(initialData?.height_cm?.toString() || "");
  const [age, setAge] = useState<string>(initialData?.age?.toString() || "");
  const [sex, setSex] = useState<BiometricsData["sex"] | "">(initialData?.sex || "");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    const weightNum = parseFloat(weight);
    if (!weight || isNaN(weightNum) || weightNum < 30 || weightNum > 300) {
      newErrors.weight = "Peso deve essere tra 30 e 300 kg";
    }

    const heightNum = parseFloat(height);
    if (!height || isNaN(heightNum) || heightNum < 100 || heightNum > 250) {
      newErrors.height = "Altezza deve essere tra 100 e 250 cm";
    }

    const ageNum = parseInt(age);
    if (!age || isNaN(ageNum) || ageNum < 13 || ageNum > 100) {
      newErrors.age = "Età deve essere tra 13 e 100 anni";
    }

    if (!sex) {
      newErrors.sex = "Seleziona sesso biologico";
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
    onComplete({
      weight_kg: parseFloat(weight),
      height_cm: parseFloat(height),
      age: parseInt(age),
      sex: sex as BiometricsData["sex"],
    });
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-background to-secondary/10 overflow-hidden">
      {/* Content (NO SCROLL) */}
      <div className="flex-1 overflow-hidden px-4 py-6 pb-safe">
        <div className="max-w-md mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="text-center space-y-2 pt-4">
            <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-primary" />
            </div>
            <h2 className="text-2xl font-bold">Dati Biometrici</h2>
            <p className="text-muted-foreground text-sm px-4">
              Questi dati ci aiutano a personalizzare i tuoi piani di allenamento e nutrizione
            </p>
          </div>

          {/* Form Fields */}
          <div className="space-y-4">
            {/* Weight */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Scale className="w-4 h-4 text-muted-foreground" />
                Peso (kg) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                inputMode="decimal"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                placeholder="es. 75"
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background text-[16px]",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation min-h-[48px]",
                  errors.weight && "border-red-500 focus:ring-red-500/20"
                )}
                min="30"
                max="300"
                step="0.1"
              />
              {errors.weight && (
                <p className="text-sm text-red-500">{errors.weight}</p>
              )}
            </div>

            {/* Height */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Ruler className="w-4 h-4 text-muted-foreground" />
                Altezza (cm) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                inputMode="numeric"
                value={height}
                onChange={(e) => setHeight(e.target.value)}
                placeholder="es. 178"
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background text-[16px]",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation min-h-[48px]",
                  errors.height && "border-red-500 focus:ring-red-500/20"
                )}
                min="100"
                max="250"
                step="1"
              />
              {errors.height && (
                <p className="text-sm text-red-500">{errors.height}</p>
              )}
            </div>

            {/* Age */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                Età <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                inputMode="numeric"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="es. 32"
                className={cn(
                  "w-full px-4 py-3 rounded-xl border bg-background text-[16px]",
                  "focus:ring-2 focus:ring-primary/20 outline-none transition-all",
                  "touch-manipulation min-h-[48px]",
                  errors.age && "border-red-500 focus:ring-red-500/20"
                )}
                min="13"
                max="100"
                step="1"
              />
              {errors.age && (
                <p className="text-sm text-red-500">{errors.age}</p>
              )}
            </div>

            {/* Sex */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Sesso Biologico <span className="text-red-500">*</span>
              </label>
              <p className="text-xs text-muted-foreground">
                Necessario per calcoli TDEE e personalizzazione allenamento
              </p>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { value: "male", label: "Maschio" },
                  { value: "female", label: "Femmina" },
                  { value: "other", label: "Altro" },
                ].map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => {
                      setSex(option.value as BiometricsData["sex"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "px-3 py-3 rounded-xl border text-sm font-medium transition-all",
                      "touch-manipulation min-h-[48px] active:scale-95",
                      sex === option.value
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background hover:bg-secondary"
                    )}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              {errors.sex && (
                <p className="text-sm text-red-500">{errors.sex}</p>
              )}
            </div>
          </div>

          {/* BMI Preview (optional) */}
          {weight && height && parseFloat(weight) > 0 && parseFloat(height) > 0 && (
            <div className="p-4 bg-muted/50 rounded-xl">
              <div className="text-sm text-muted-foreground">Il tuo BMI stimato</div>
              <div className="text-2xl font-bold text-primary">
                {(parseFloat(weight) / Math.pow(parseFloat(height) / 100, 2)).toFixed(1)}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Normale: 18.5 - 24.9
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            className={cn(
              "w-full py-4 rounded-xl font-semibold text-white transition-all touch-manipulation",
              "bg-primary hover:bg-primary/90 active:scale-98",
              "flex items-center justify-center gap-2"
            )}
          >
            Continua
          </button>

          {/* Privacy note */}
          <p className="text-xs text-center text-muted-foreground pb-4">
            🔒 I tuoi dati sono criptati e utilizzati solo per personalizzare il tuo percorso
          </p>
        </div>
      </div>
    </div>
  );
}
