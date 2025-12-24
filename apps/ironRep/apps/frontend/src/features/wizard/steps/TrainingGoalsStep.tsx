/**
 * TrainingGoalsStep - Comprehensive Training Goals Collection
 *
 * Collects: primary_goal, secondary_goals, training_experience, available_days,
 *           session_duration, equipment_available, preferred_time
 *
 * @production-ready Inline component for detailed training data
 */

import { useState } from "react";
import { Target, Clock, Calendar, Dumbbell, Zap, Trophy, ChevronRight } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

export interface TrainingGoalsData {
  primary_goal:
  | "muscle_gain"
  | "fat_loss"
  | "strength"
  | "endurance"
  | "recomp"
  | "athletic_performance"
  | "general_fitness"
  | "injury_recovery";
  secondary_goals: string[];
  training_experience: "beginner" | "intermediate" | "advanced" | "athlete";
  training_years?: number;
  available_days: number;
  session_duration: 30 | 45 | 60 | 75 | 90 | 120;
  equipment_available: string[];
  preferred_time: "morning" | "afternoon" | "evening" | "flexible";
  intensity_preference: "low" | "moderate" | "high" | "max";
}

interface TrainingGoalsStepProps {
  onComplete: (data: TrainingGoalsData) => void;
  onSkip?: () => void;
  initialData?: Partial<TrainingGoalsData>;
}

const PRIMARY_GOALS = [
  { value: "muscle_gain", label: "Massa Muscolare", icon: "💪", description: "Costruire muscoli e ipertrofia" },
  { value: "fat_loss", label: "Perdita Grasso", icon: "🔥", description: "Definizione e dimagrimento" },
  { value: "strength", label: "Forza Massima", icon: "🏋️", description: "Powerlifting, massimali" },
  { value: "recomp", label: "Ricomposizione", icon: "⚡", description: "Muscoli su, grasso giù" },
  { value: "endurance", label: "Resistenza", icon: "🏃", description: "Cardio, endurance, stamina" },
  { value: "athletic_performance", label: "Performance Sport", icon: "🏆", description: "Per uno sport specifico" },
  { value: "general_fitness", label: "Fitness Generale", icon: "❤️", description: "Salute e benessere" },
  { value: "injury_recovery", label: "Recovery Infortunio", icon: "🩹", description: "Ritorno post-infortunio" },
];

const SECONDARY_GOALS = [
  { value: "flexibility", label: "Flessibilità" },
  { value: "posture", label: "Postura" },
  { value: "core_strength", label: "Core Strong" },
  { value: "explosiveness", label: "Esplosività" },
  { value: "grip_strength", label: "Forza Presa" },
  { value: "mobility", label: "Mobilità Articolare" },
  { value: "mental_focus", label: "Focus Mentale" },
  { value: "stress_relief", label: "Gestione Stress" },
];

const EXPERIENCE_LEVELS = [
  { value: "beginner", label: "Principiante", years: "0-1 anno", description: "Mai o poco allenato" },
  { value: "intermediate", label: "Intermedio", years: "1-3 anni", description: "Conosco gli esercizi base" },
  { value: "advanced", label: "Avanzato", years: "3-5+ anni", description: "Esperienza solida" },
  { value: "athlete", label: "Atleta", years: "5+ anni sport", description: "Competizioni/professionista" },
];

const EQUIPMENT_OPTIONS = [
  { value: "full_gym", label: "Palestra completa", icon: "🏢" },
  { value: "home_gym", label: "Home gym", icon: "🏠" },
  { value: "barbell_rack", label: "Bilanciere + Rack", icon: "🏋️" },
  { value: "dumbbells", label: "Manubri", icon: "💪" },
  { value: "kettlebells", label: "Kettlebell", icon: "🔔" },
  { value: "machines", label: "Macchine", icon: "⚙️" },
  { value: "cables", label: "Cavi", icon: "📏" },
  { value: "bodyweight", label: "Solo corpo libero", icon: "🧘" },
  { value: "bands", label: "Elastici", icon: "🎗️" },
  { value: "cardio_equipment", label: "Cardio (tapis, bike)", icon: "🚴" },
];

const DURATION_OPTIONS = [
  { value: 30, label: "30 min", subtext: "Express" },
  { value: 45, label: "45 min", subtext: "Quick" },
  { value: 60, label: "60 min", subtext: "Standard" },
  { value: 75, label: "75 min", subtext: "Full" },
  { value: 90, label: "90 min", subtext: "Extended" },
  { value: 120, label: "120 min", subtext: "Intensivo" },
];

export function TrainingGoalsStep({ onComplete, initialData }: TrainingGoalsStepProps) {
  const [currentSection, setCurrentSection] = useState(0);
  const [primaryGoal, setPrimaryGoal] = useState<TrainingGoalsData["primary_goal"] | "">(initialData?.primary_goal || "");
  const [secondaryGoals, setSecondaryGoals] = useState<string[]>(initialData?.secondary_goals || []);
  const [experience, setExperience] = useState<TrainingGoalsData["training_experience"] | "">(initialData?.training_experience || "");
  const [trainingYears, setTrainingYears] = useState<string>(initialData?.training_years?.toString() || "");
  const [availableDays, setAvailableDays] = useState<number>(initialData?.available_days || 4);
  const [sessionDuration, setSessionDuration] = useState<TrainingGoalsData["session_duration"]>(initialData?.session_duration || 60);
  const [equipment, setEquipment] = useState<string[]>(initialData?.equipment_available || []);
  const [preferredTime, setPreferredTime] = useState<TrainingGoalsData["preferred_time"]>(initialData?.preferred_time || "flexible");
  const [intensity, setIntensity] = useState<TrainingGoalsData["intensity_preference"]>(initialData?.intensity_preference || "moderate");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const totalSections = 5;

  const MAX_VISIBLE_OPTIONS = 8;

  const toggleSecondaryGoal = (goal: string) => {
    hapticFeedback.selection();
    if (secondaryGoals.includes(goal)) {
      setSecondaryGoals(prev => prev.filter(g => g !== goal));
    } else if (secondaryGoals.length < 3) {
      setSecondaryGoals(prev => [...prev, goal]);
    }
  };

  const toggleEquipment = (eq: string) => {
    hapticFeedback.selection();
    if (equipment.includes(eq)) {
      setEquipment(prev => prev.filter(e => e !== eq));
    } else {
      setEquipment(prev => [...prev, eq]);
    }
  };

  const validateSection = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (currentSection === 0 && !primaryGoal) {
      newErrors.primaryGoal = "Seleziona un obiettivo principale";
    }
    if (currentSection === 1 && !experience) {
      newErrors.experience = "Seleziona il tuo livello";
    }
    if (currentSection === 3 && equipment.length === 0) {
      newErrors.equipment = "Seleziona almeno un'attrezzatura";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (!validateSection()) {
      hapticFeedback.notification("error");
      return;
    }

    hapticFeedback.selection();
    if (currentSection < totalSections - 1) {
      setCurrentSection(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    hapticFeedback.selection();
    if (currentSection > 0) {
      setCurrentSection(prev => prev - 1);
    }
  };

  const handleSubmit = () => {
    hapticFeedback.notification("success");
    onComplete({
      primary_goal: primaryGoal as TrainingGoalsData["primary_goal"],
      secondary_goals: secondaryGoals,
      training_experience: experience as TrainingGoalsData["training_experience"],
      training_years: trainingYears ? parseInt(trainingYears) : undefined,
      available_days: availableDays,
      session_duration: sessionDuration,
      equipment_available: equipment,
      preferred_time: preferredTime,
      intensity_preference: intensity,
    });
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-background to-secondary/10 overflow-hidden">
      {/* Progress Bar */}
      <div className="px-4 pt-4 safe-area-top">
        <div className="flex gap-1 mb-2">
          {[...Array(totalSections)].map((_, i) => (
            <div
              key={i}
              className={cn(
                "h-1.5 flex-1 rounded-full transition-all duration-300",
                i <= currentSection ? "bg-primary" : "bg-muted"
              )}
            />
          ))}
        </div>
        <p className="text-xs text-muted-foreground text-right">
          {currentSection + 1} / {totalSections}
        </p>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-4 py-6 pb-32">
        <div className="max-w-md mx-auto animate-in fade-in slide-in-from-right-4 duration-300">

          {/* Section 0: Primary Goal */}
          {currentSection === 0 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
                  <Target className="w-8 h-8 text-primary" />
                </div>
                <h2 className="text-2xl font-bold">Obiettivo Principale</h2>
                <p className="text-muted-foreground text-sm">
                  Qual è il tuo focus numero uno?
                </p>
              </div>

              <div className="grid gap-3">
                {PRIMARY_GOALS.map((goal) => (
                  <button
                    key={goal.value}
                    onClick={() => {
                      setPrimaryGoal(goal.value as TrainingGoalsData["primary_goal"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "w-full p-4 rounded-xl border-2 text-left transition-all touch-manipulation",
                      primaryGoal === goal.value
                        ? "border-primary bg-primary/5"
                        : "border-transparent bg-secondary/50 hover:bg-secondary"
                    )}
                  >
                    <div className="flex items-center gap-4">
                      <span className="text-2xl">{goal.icon}</span>
                      <div className="flex-1">
                        <div className="font-semibold">{goal.label}</div>
                        <div className="text-xs text-muted-foreground">{goal.description}</div>
                      </div>
                      {primaryGoal === goal.value && (
                        <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                          <ChevronRight className="w-4 h-4 text-white" />
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>

              {errors.primaryGoal && (
                <p className="text-sm text-red-500 text-center">{errors.primaryGoal}</p>
              )}

              {/* Secondary Goals */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">
                  Obiettivi Secondari (opzionale, max 3)
                </label>
                <div className="flex flex-wrap gap-2">
                  {SECONDARY_GOALS.slice(0, MAX_VISIBLE_OPTIONS).map((goal) => (
                    <button
                      key={goal.value}
                      onClick={() => toggleSecondaryGoal(goal.value)}
                      className={cn(
                        "px-3 py-2 rounded-full text-sm transition-all touch-manipulation",
                        secondaryGoals.includes(goal.value)
                          ? "bg-primary text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {goal.label}
                    </button>
                  ))}
                </div>

                {SECONDARY_GOALS.length > MAX_VISIBLE_OPTIONS && (
                  <p className="text-xs text-muted-foreground/70">
                    Lista lunga: mostro le prime {MAX_VISIBLE_OPTIONS} opzioni (NO SCROLL attivo).
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Section 1: Experience Level */}
          {currentSection === 1 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-blue-100 dark:bg-blue-950/20 rounded-full flex items-center justify-center">
                  <Trophy className="w-8 h-8 text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold">Esperienza Allenamento</h2>
                <p className="text-muted-foreground text-sm">
                  Da quanto tempo ti alleni?
                </p>
              </div>

              <div className="grid gap-3">
                {EXPERIENCE_LEVELS.map((level) => (
                  <button
                    key={level.value}
                    onClick={() => {
                      setExperience(level.value as TrainingGoalsData["training_experience"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "w-full p-4 rounded-xl border-2 text-left transition-all touch-manipulation",
                      experience === level.value
                        ? "border-primary bg-primary/5"
                        : "border-transparent bg-secondary/50 hover:bg-secondary"
                    )}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-semibold">{level.label}</div>
                        <div className="text-xs text-muted-foreground">{level.description}</div>
                      </div>
                      <span className="text-xs text-muted-foreground bg-background px-2 py-1 rounded">
                        {level.years}
                      </span>
                    </div>
                  </button>
                ))}
              </div>

              {errors.experience && (
                <p className="text-sm text-red-500 text-center">{errors.experience}</p>
              )}

              {/* Exact years input */}
              <div className="space-y-2 pt-4 border-t">
                <label className="text-sm font-medium">
                  Anni esatti di allenamento (opzionale)
                </label>
                <input
                  type="number"
                  inputMode="numeric"
                  value={trainingYears}
                  onChange={(e) => setTrainingYears(e.target.value)}
                  placeholder="es. 3"
                  className="w-full px-4 py-3 rounded-xl border bg-background text-[16px] focus:ring-2 focus:ring-primary/20 outline-none"
                  min="0"
                  max="50"
                />
              </div>
            </div>
          )}

          {/* Section 2: Schedule */}
          {currentSection === 2 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-green-100 dark:bg-green-950/20 rounded-full flex items-center justify-center">
                  <Calendar className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold">Disponibilità</h2>
                <p className="text-muted-foreground text-sm">
                  Quanti giorni puoi allenarti?
                </p>
              </div>

              {/* Days per week */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Giorni a settimana</label>
                <div className="flex gap-2">
                  {[2, 3, 4, 5, 6, 7].map((days) => (
                    <button
                      key={days}
                      onClick={() => {
                        setAvailableDays(days);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "flex-1 py-4 rounded-xl font-semibold text-lg transition-all touch-manipulation",
                        availableDays === days
                          ? "bg-primary text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {days}
                    </button>
                  ))}
                </div>
              </div>

              {/* Session Duration */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Durata sessione
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {DURATION_OPTIONS.map((duration) => (
                    <button
                      key={duration.value}
                      onClick={() => {
                        setSessionDuration(duration.value as TrainingGoalsData["session_duration"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "py-3 rounded-xl text-center transition-all touch-manipulation",
                        sessionDuration === duration.value
                          ? "bg-primary text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="font-semibold">{duration.label}</div>
                      <div className="text-xs opacity-70">{duration.subtext}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Preferred Time */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Orario preferito</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: "morning", label: "🌅 Mattina", subtext: "6-12" },
                    { value: "afternoon", label: "☀️ Pomeriggio", subtext: "12-18" },
                    { value: "evening", label: "🌙 Sera", subtext: "18-22" },
                    { value: "flexible", label: "🔄 Flessibile", subtext: "Qualsiasi" },
                  ].map((time) => (
                    <button
                      key={time.value}
                      onClick={() => {
                        setPreferredTime(time.value as TrainingGoalsData["preferred_time"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "py-3 px-4 rounded-xl text-left transition-all touch-manipulation",
                        preferredTime === time.value
                          ? "bg-primary text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="font-semibold">{time.label}</div>
                      <div className="text-xs opacity-70">{time.subtext}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Section 3: Equipment */}
          {currentSection === 3 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-orange-100 dark:bg-orange-950/20 rounded-full flex items-center justify-center">
                  <Dumbbell className="w-8 h-8 text-orange-600" />
                </div>
                <h2 className="text-2xl font-bold">Attrezzatura</h2>
                <p className="text-muted-foreground text-sm">
                  Cosa hai a disposizione?
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {EQUIPMENT_OPTIONS.slice(0, MAX_VISIBLE_OPTIONS).map((eq) => (
                  <button
                    key={eq.value}
                    onClick={() => toggleEquipment(eq.value)}
                    className={cn(
                      "py-4 px-3 rounded-xl text-center transition-all touch-manipulation",
                      equipment.includes(eq.value)
                        ? "bg-primary text-white"
                        : "bg-secondary hover:bg-secondary/80"
                    )}
                  >
                    <span className="text-xl">{eq.icon}</span>
                    <div className="text-sm font-medium mt-1">{eq.label}</div>
                  </button>
                ))}
              </div>

              {EQUIPMENT_OPTIONS.length > MAX_VISIBLE_OPTIONS && (
                <p className="text-xs text-muted-foreground/70">
                  Lista lunga: mostro le prime {MAX_VISIBLE_OPTIONS} opzioni (NO SCROLL attivo).
                </p>
              )}

              {errors.equipment && (
                <p className="text-sm text-red-500 text-center">{errors.equipment}</p>
              )}
            </div>
          )}

          {/* Section 4: Intensity Preference */}
          {currentSection === 4 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-purple-100 dark:bg-purple-950/20 rounded-full flex items-center justify-center">
                  <Zap className="w-8 h-8 text-purple-600" />
                </div>
                <h2 className="text-2xl font-bold">Intensità Preferita</h2>
                <p className="text-muted-foreground text-sm">
                  Quanto duro vuoi allenarti?
                </p>
              </div>

              <div className="grid gap-3">
                {[
                  { value: "low", label: "🧘 Leggera", description: "Focus su tecnica e mobilità, RPE 5-6" },
                  { value: "moderate", label: "🏃 Moderata", description: "Bilanciato, progressione costante, RPE 6-7" },
                  { value: "high", label: "💪 Alta", description: "Push hard, supersets, drop sets, RPE 7-8" },
                  { value: "max", label: "🔥 Massima", description: "Beast mode, limite assoluto, RPE 8-10" },
                ].map((int) => (
                  <button
                    key={int.value}
                    onClick={() => {
                      setIntensity(int.value as TrainingGoalsData["intensity_preference"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "w-full p-4 rounded-xl border-2 text-left transition-all touch-manipulation",
                      intensity === int.value
                        ? "border-primary bg-primary/5"
                        : "border-transparent bg-secondary/50 hover:bg-secondary"
                    )}
                  >
                    <div className="font-semibold">{int.label}</div>
                    <div className="text-xs text-muted-foreground">{int.description}</div>
                  </button>
                ))}
              </div>

              {/* Summary Preview */}
              <div className="p-4 bg-muted/50 rounded-xl space-y-2 mt-6">
                <div className="text-sm font-medium">📋 Riepilogo Obiettivi:</div>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>• Goal: {PRIMARY_GOALS.find(g => g.value === primaryGoal)?.label || '-'}</div>
                  <div>• Livello: {EXPERIENCE_LEVELS.find(l => l.value === experience)?.label || '-'}</div>
                  <div>• Schedule: {availableDays}x/settimana, {sessionDuration} min</div>
                  <div>• Attrezzatura: {equipment.length} tipo(i)</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/80 backdrop-blur-lg border-t safe-area-bottom">
        <div className="max-w-md mx-auto flex gap-3">
          {currentSection > 0 && (
            <button
              onClick={handleBack}
              className="px-6 py-4 rounded-xl font-semibold bg-secondary hover:bg-secondary/80 transition-all touch-manipulation"
            >
              Indietro
            </button>
          )}
          <button
            onClick={handleNext}
            className={cn(
              "flex-1 py-4 rounded-xl font-semibold text-white transition-all touch-manipulation",
              "bg-primary hover:bg-primary/90 active:scale-98"
            )}
          >
            {currentSection === totalSections - 1 ? "Conferma" : "Continua"}
          </button>
        </div>
      </div>
    </div>
  );
}
