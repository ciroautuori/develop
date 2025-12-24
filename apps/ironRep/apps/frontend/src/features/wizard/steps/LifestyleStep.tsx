/**
 * LifestyleStep - Comprehensive Lifestyle & Recovery Data Collection
 *
 * Collects: activity_level, work_type, stress_level, sleep_hours, sleep_quality,
 *           recovery_capacity, lifestyle_factors
 *
 * @production-ready Critical data for Coach agent personalization
 */

import type React from "react";
import { useState } from "react";
import { Briefcase, Moon, Activity, Heart, Battery, AlertTriangle } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

export interface LifestyleData {
  activity_level: "sedentary" | "lightly_active" | "moderately_active" | "very_active" | "extra_active";
  work_type: "desk_job" | "standing" | "physical_labor" | "mixed" | "student" | "retired";
  work_hours_per_day?: number;
  commute_active: boolean; // Walk/bike to work?
  stress_level: 1 | 2 | 3 | 4 | 5;
  stress_sources?: string[];
  sleep_hours: number;
  sleep_quality: "poor" | "fair" | "good" | "excellent";
  sleep_schedule: "consistent" | "irregular" | "shift_work";
  recovery_capacity: "low" | "normal" | "high";
  health_conditions?: string[];
  supplements_used?: string[];
}

interface LifestyleStepProps {
  onComplete: (data: LifestyleData) => void;
  onSkip?: () => void;
  initialData?: Partial<LifestyleData>;
}

const ACTIVITY_LEVELS = [
  { value: "sedentary", label: "Sedentario", description: "Lavoro d'ufficio, poco movimento", multiplier: "1.2x TDEE" },
  { value: "lightly_active", label: "Poco Attivo", description: "Camminate leggere, 1-2 allenamenti", multiplier: "1.375x TDEE" },
  { value: "moderately_active", label: "Moderatamente Attivo", description: "3-5 allenamenti/settimana", multiplier: "1.55x TDEE" },
  { value: "very_active", label: "Molto Attivo", description: "Allenamenti intensi 6-7x", multiplier: "1.725x TDEE" },
  { value: "extra_active", label: "Estremamente Attivo", description: "Atleta, lavoro fisico + sport", multiplier: "1.9x TDEE" },
];

const WORK_TYPES = [
  { value: "desk_job", label: "🖥️ Ufficio/Scrivania", description: "Seduto 6-8h" },
  { value: "standing", label: "🧍 In piedi", description: "Retail, ristorazione" },
  { value: "physical_labor", label: "🔨 Lavoro fisico", description: "Edilizia, agricoltura" },
  { value: "mixed", label: "🔄 Misto", description: "Varia durante il giorno" },
  { value: "student", label: "📚 Studente", description: "Studio e università" },
  { value: "retired", label: "🏖️ Pensionato", description: "Tempo libero" },
];

const SLEEP_QUALITY_OPTIONS = [
  { value: "poor", label: "😴 Scarsa", description: "Risvegli frequenti, stanchezza" },
  { value: "fair", label: "😐 Discreta", description: "Qualche problema occasionale" },
  { value: "good", label: "😊 Buona", description: "Riposo adeguato" },
  { value: "excellent", label: "😎 Eccellente", description: "Dormo come un bambino" },
];

const STRESS_SOURCES = [
  { value: "work", label: "Lavoro" },
  { value: "family", label: "Famiglia" },
  { value: "financial", label: "Finanze" },
  { value: "health", label: "Salute" },
  { value: "relationships", label: "Relazioni" },
  { value: "studies", label: "Studio" },
  { value: "none", label: "Nessuno particolare" },
];

const HEALTH_CONDITIONS = [
  { value: "diabetes", label: "Diabete" },
  { value: "hypertension", label: "Ipertensione" },
  { value: "heart_condition", label: "Problemi cardiaci" },
  { value: "thyroid", label: "Tiroide" },
  { value: "back_pain", label: "Mal di schiena cronico" },
  { value: "joint_pain", label: "Dolori articolari" },
  { value: "sleep_apnea", label: "Apnea notturna" },
  { value: "anxiety", label: "Ansia" },
  { value: "depression", label: "Depressione" },
  { value: "none", label: "Nessuna" },
];

const SUPPLEMENTS = [
  { value: "protein", label: "Proteine" },
  { value: "creatine", label: "Creatina" },
  { value: "caffeine", label: "Caffeina/Pre-workout" },
  { value: "omega3", label: "Omega-3" },
  { value: "vitamin_d", label: "Vitamina D" },
  { value: "multivitamin", label: "Multivitaminico" },
  { value: "bcaa", label: "BCAA/EAA" },
  { value: "melatonin", label: "Melatonina" },
  { value: "none", label: "Nessuno" },
];

export function LifestyleStep({ onComplete, initialData }: LifestyleStepProps) {
  const [currentSection, setCurrentSection] = useState(0);
  const [activityLevel, setActivityLevel] = useState<LifestyleData["activity_level"] | "">(initialData?.activity_level || "");
  const [workType, setWorkType] = useState<LifestyleData["work_type"] | "">(initialData?.work_type || "");
  const [workHours, setWorkHours] = useState<string>(initialData?.work_hours_per_day?.toString() || "8");
  const [commuteActive, setCommuteActive] = useState(initialData?.commute_active || false);
  const [stressLevel, setStressLevel] = useState<number>(initialData?.stress_level || 3);
  const [stressSources, setStressSources] = useState<string[]>(initialData?.stress_sources || []);
  const [sleepHours, setSleepHours] = useState<number>(initialData?.sleep_hours || 7);
  const [sleepQuality, setSleepQuality] = useState<LifestyleData["sleep_quality"] | "">(initialData?.sleep_quality || "");
  const [sleepSchedule] = useState<LifestyleData["sleep_schedule"]>(initialData?.sleep_schedule || "consistent");
  const [recoveryCapacity, setRecoveryCapacity] = useState<LifestyleData["recovery_capacity"]>(initialData?.recovery_capacity || "normal");
  const [healthConditions, setHealthConditions] = useState<string[]>(initialData?.health_conditions || []);
  const [supplements, setSupplements] = useState<string[]>(initialData?.supplements_used || []);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const totalSections = 4;

  const MAX_VISIBLE_OPTIONS = 8;

  const toggleArrayItem = (arr: string[], setter: React.Dispatch<React.SetStateAction<string[]>>, item: string) => {
    hapticFeedback.selection();
    if (arr.includes(item)) {
      setter(prev => prev.filter(i => i !== item));
    } else {
      setter(prev => [...prev, item]);
    }
  };

  const validateSection = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (currentSection === 0 && !activityLevel) {
      newErrors.activityLevel = "Seleziona il livello di attività";
    }
    if (currentSection === 1 && !workType) {
      newErrors.workType = "Seleziona il tipo di lavoro";
    }
    if (currentSection === 2 && !sleepQuality) {
      newErrors.sleepQuality = "Seleziona la qualità del sonno";
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
      activity_level: activityLevel as LifestyleData["activity_level"],
      work_type: workType as LifestyleData["work_type"],
      work_hours_per_day: parseInt(workHours) || 8,
      commute_active: commuteActive,
      stress_level: stressLevel as LifestyleData["stress_level"],
      stress_sources: stressSources.filter(s => s !== "none"),
      sleep_hours: sleepHours,
      sleep_quality: sleepQuality as LifestyleData["sleep_quality"],
      sleep_schedule: sleepSchedule,
      recovery_capacity: recoveryCapacity,
      health_conditions: healthConditions.filter(h => h !== "none"),
      supplements_used: supplements.filter(s => s !== "none"),
    });
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-background to-secondary/10 overflow-y-auto">
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

          {/* Section 0: Activity Level */}
          {currentSection === 0 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-green-100 dark:bg-green-950/20 rounded-full flex items-center justify-center">
                  <Activity className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold">Livello Attività</h2>
                <p className="text-muted-foreground text-sm">
                  Quanto sei attivo nella vita quotidiana?
                </p>
              </div>

              <div className="grid gap-3">
                {ACTIVITY_LEVELS.map((level) => (
                  <button
                    key={level.value}
                    onClick={() => {
                      setActivityLevel(level.value as LifestyleData["activity_level"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "w-full p-4 rounded-xl border-2 text-left transition-all touch-manipulation",
                      activityLevel === level.value
                        ? "border-primary bg-primary/5"
                        : "border-transparent bg-secondary/50 hover:bg-secondary"
                    )}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-semibold">{level.label}</div>
                        <div className="text-xs text-muted-foreground">{level.description}</div>
                      </div>
                      <span className="text-xs bg-background px-2 py-1 rounded text-muted-foreground">
                        {level.multiplier}
                      </span>
                    </div>
                  </button>
                ))}
              </div>

              {errors.activityLevel && (
                <p className="text-sm text-red-500 text-center">{errors.activityLevel}</p>
              )}
            </div>
          )}

          {/* Section 1: Work & Lifestyle */}
          {currentSection === 1 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-blue-100 dark:bg-blue-950/20 rounded-full flex items-center justify-center">
                  <Briefcase className="w-8 h-8 text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold">Lavoro & Routine</h2>
                <p className="text-muted-foreground text-sm">
                  Che tipo di lavoro fai?
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {WORK_TYPES.map((work) => (
                  <button
                    key={work.value}
                    onClick={() => {
                      setWorkType(work.value as LifestyleData["work_type"]);
                      hapticFeedback.selection();
                    }}
                    className={cn(
                      "p-4 rounded-xl text-left transition-all touch-manipulation",
                      workType === work.value
                        ? "bg-primary text-white"
                        : "bg-secondary hover:bg-secondary/80"
                    )}
                  >
                    <div className="text-lg">{work.label}</div>
                    <div className={cn(
                      "text-xs mt-1",
                      workType === work.value ? "text-white/70" : "text-muted-foreground"
                    )}>{work.description}</div>
                  </button>
                ))}
              </div>

              {errors.workType && (
                <p className="text-sm text-red-500 text-center">{errors.workType}</p>
              )}

              {/* Work Hours */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Ore di lavoro/giorno</label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="4"
                    max="12"
                    value={workHours}
                    onChange={(e) => setWorkHours(e.target.value)}
                    className="flex-1 h-2 bg-secondary rounded-full accent-primary"
                  />
                  <span className="w-12 text-center font-semibold">{workHours}h</span>
                </div>
              </div>

              {/* Active Commute */}
              <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-xl">
                <div>
                  <div className="font-medium">Pendolarismo attivo?</div>
                  <div className="text-xs text-muted-foreground">Vai a lavoro a piedi o in bici?</div>
                </div>
                <button
                  onClick={() => {
                    setCommuteActive(!commuteActive);
                    hapticFeedback.selection();
                  }}
                  className={cn(
                    "w-14 h-8 rounded-full transition-all relative",
                    commuteActive ? "bg-primary" : "bg-muted"
                  )}
                >
                  <div className={cn(
                    "w-6 h-6 bg-white rounded-full absolute top-1 transition-all",
                    commuteActive ? "left-7" : "left-1"
                  )} />
                </button>
              </div>
            </div>
          )}

          {/* Section 2: Sleep & Stress */}
          {currentSection === 2 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-purple-100 dark:bg-purple-950/20 rounded-full flex items-center justify-center">
                  <Moon className="w-8 h-8 text-purple-600" />
                </div>
                <h2 className="text-2xl font-bold">Sonno & Stress</h2>
                <p className="text-muted-foreground text-sm">
                  Come riposi e gestisci lo stress?
                </p>
              </div>

              {/* Sleep Hours */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Ore di sonno/notte</label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="4"
                    max="10"
                    step="0.5"
                    value={sleepHours}
                    onChange={(e) => setSleepHours(parseFloat(e.target.value))}
                    className="flex-1 h-2 bg-secondary rounded-full accent-primary"
                  />
                  <span className="w-12 text-center font-semibold">{sleepHours}h</span>
                </div>
              </div>

              {/* Sleep Quality */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Qualità del sonno</label>
                <div className="grid grid-cols-2 gap-2">
                  {SLEEP_QUALITY_OPTIONS.map((qual) => (
                    <button
                      key={qual.value}
                      onClick={() => {
                        setSleepQuality(qual.value as LifestyleData["sleep_quality"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "p-3 rounded-xl text-left transition-all touch-manipulation",
                        sleepQuality === qual.value
                          ? "bg-primary text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="font-semibold">{qual.label}</div>
                      <div className={cn(
                        "text-xs",
                        sleepQuality === qual.value ? "text-white/70" : "text-muted-foreground"
                      )}>{qual.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {errors.sleepQuality && (
                <p className="text-sm text-red-500 text-center">{errors.sleepQuality}</p>
              )}

              {/* Stress Level */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Livello di stress (1-5)
                </label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <button
                      key={level}
                      onClick={() => {
                        setStressLevel(level);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "flex-1 py-4 rounded-xl font-semibold text-lg transition-all touch-manipulation",
                        stressLevel === level
                          ? level <= 2 ? "bg-green-500 text-white" :
                            level === 3 ? "bg-yellow-500 text-white" :
                              "bg-red-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {level}
                    </button>
                  ))}
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Basso</span>
                  <span>Alto</span>
                </div>
              </div>

              {/* Stress Sources */}
              {stressLevel >= 3 && (
                <div className="space-y-3">
                  <label className="text-sm font-medium">Fonti di stress principali</label>
                  <div className="flex flex-wrap gap-2">
                    {STRESS_SOURCES.map((source) => (
                      <button
                        key={source.value}
                        onClick={() => toggleArrayItem(stressSources, setStressSources, source.value)}
                        className={cn(
                          "px-3 py-2 rounded-full text-sm transition-all touch-manipulation",
                          stressSources.includes(source.value)
                            ? "bg-primary text-white"
                            : "bg-secondary hover:bg-secondary/80"
                        )}
                      >
                        {source.label}
                      </button>
                    ))}
                  </div>


                </div>
              )}
            </div>
          )}

          {/* Section 3: Health & Supplements */}
          {currentSection === 3 && (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto bg-red-100 dark:bg-red-950/20 rounded-full flex items-center justify-center">
                  <Heart className="w-8 h-8 text-red-600" />
                </div>
                <h2 className="text-2xl font-bold">Salute & Recovery</h2>
                <p className="text-muted-foreground text-sm">
                  Informazioni importanti per personalizzare il tuo piano
                </p>
              </div>

              {/* Recovery Capacity */}
              <div className="space-y-3">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Battery className="w-4 h-4" />
                  Capacità di Recupero
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: "low", label: "🔋 Bassa", description: "Recupero lento" },
                    { value: "normal", label: "🔋🔋 Normale", description: "Media" },
                    { value: "high", label: "🔋🔋🔋 Alta", description: "Recupero rapido" },
                  ].map((rec) => (
                    <button
                      key={rec.value}
                      onClick={() => {
                        setRecoveryCapacity(rec.value as LifestyleData["recovery_capacity"]);
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "p-3 rounded-xl text-center transition-all touch-manipulation",
                        recoveryCapacity === rec.value
                          ? "bg-primary text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      <div className="text-sm font-semibold">{rec.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Health Conditions */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Condizioni di salute rilevanti (opzionale)</label>
                <p className="text-xs text-muted-foreground">
                  ⚠️ Consulta sempre un medico prima di iniziare un programma di allenamento
                </p>
                <div className="flex flex-wrap gap-2">
                  {HEALTH_CONDITIONS.map((cond) => (
                    <button
                      key={cond.value}
                      onClick={() => {
                        if (cond.value === "none") {
                          setHealthConditions(["none"]);
                        } else {
                          const newConditions = healthConditions.filter(h => h !== "none");
                          if (newConditions.includes(cond.value)) {
                            setHealthConditions(newConditions.filter(h => h !== cond.value));
                          } else {
                            setHealthConditions([...newConditions, cond.value]);
                          }
                        }
                        hapticFeedback.selection();
                      }}
                      className={cn(
                        "px-3 py-2 rounded-full text-sm transition-all touch-manipulation",
                        healthConditions.includes(cond.value)
                          ? cond.value === "none" ? "bg-green-500 text-white" : "bg-orange-500 text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {cond.label}
                    </button>
                  ))}
                </div>


              </div>

              {/* Supplements */}
              <div className="space-y-3 pt-4 border-t">
                <label className="text-sm font-medium">Integratori utilizzati (opzionale)</label>
                <div className="flex flex-wrap gap-2">
                  {SUPPLEMENTS.map((supp) => (
                    <button
                      key={supp.value}
                      onClick={() => toggleArrayItem(supplements, setSupplements, supp.value)}
                      className={cn(
                        "px-3 py-2 rounded-full text-sm transition-all touch-manipulation",
                        supplements.includes(supp.value)
                          ? "bg-primary text-white"
                          : "bg-secondary hover:bg-secondary/80"
                      )}
                    >
                      {supp.label}
                    </button>
                  ))}
                </div>


              </div>

              {/* Summary */}
              <div className="p-4 bg-muted/50 rounded-xl space-y-2 mt-6">
                <div className="text-sm font-medium">📋 Riepilogo Lifestyle:</div>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>• Attività: {ACTIVITY_LEVELS.find(a => a.value === activityLevel)?.label || '-'}</div>
                  <div>• Lavoro: {WORK_TYPES.find(w => w.value === workType)?.label || '-'}</div>
                  <div>• Sonno: {sleepHours}h, qualità {sleepQuality}</div>
                  <div>• Stress: {stressLevel}/5</div>
                  <div>• Recovery: {recoveryCapacity}</div>
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
