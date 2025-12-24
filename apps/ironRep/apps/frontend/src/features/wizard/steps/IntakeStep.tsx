/**
 * IntakeStep - Unified Wizard Intake
 * 
 * Consolidates Biometrics, Goals, and Initial Health Check into a single flow.
 * Replaces the fragmented multi-step process.
 * 
 * Sections:
 * 1. Biometrics (Age, Weight, Height, Sex)
 * 2. Training Context (Goal, Experience, Days)
 * 3. Health Check (Injury Toggle + Details if needed)
 * 
 * @production-ready
 */

import { useState } from "react";
import { User, Target, Heart, AlertCircle, ChevronRight, Check } from "lucide-react";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";

// ==========================================
// TYPES
// ==========================================

export interface IntakeData {
    // Biometrics
    age: number;
    weight: number;
    height: number;
    sex: "male" | "female" | "other";

    // Goals
    primaryGoal: string;
    experience: "beginner" | "intermediate" | "advanced" | "athlete";
    daysPerWeek: number;

    // Medical
    hasInjury: boolean;
    injuryDetails?: {
        diagnosis: string;
        painLevel: number; // 1-10
        location?: string;
    };
}

interface IntakeStepProps {
    onComplete: (data: IntakeData) => void;
    initialData?: Partial<IntakeData>;
}

// ==========================================
// CONSTANTS
// ==========================================

const GOAL_OPTIONS = [
    { value: "muscle_gain", label: "Massa Muscolare", icon: "💪" },
    { value: "fat_loss", label: "Dimagrimento", icon: "🔥" },
    { value: "strength", label: "Forza Pura", icon: "🏋️" },
    { value: "general_fitness", label: "Indeciso / Fitness", icon: "🤷" }, // Simplified
];

const EXPERIENCE_OPTIONS = [
    { value: "beginner", label: "Principiante (<1 anno)" },
    { value: "intermediate", label: "Intermedio (1-3 anni)" },
    { value: "advanced", label: "Avanzato (3+ anni)" },
];

export function IntakeStep({ onComplete, initialData }: IntakeStepProps) {
    const [currentSection, setCurrentSection] = useState(0);
    const TOTAL_SECTIONS = 3;

    // --- STATE ---

    // 1. Biometrics
    const [age, setAge] = useState<string>(initialData?.age?.toString() || "");
    const [weight, setWeight] = useState<string>(initialData?.weight?.toString() || "");
    const [height, setHeight] = useState<string>(initialData?.height?.toString() || "");
    const [sex, setSex] = useState<IntakeData["sex"] | "">(initialData?.sex || "");

    // 2. Goals
    const [goal, setGoal] = useState<string>(initialData?.primaryGoal || "");
    const [experience, setExperience] = useState<string>(initialData?.experience || "");
    const [days, setDays] = useState<number>(initialData?.daysPerWeek || 3);

    // 3. Health
    const [hasInjury, setHasInjury] = useState<boolean | null>(initialData?.hasInjury ?? null);
    const [injuryDiagnosis, setInjuryDiagnosis] = useState<string>(initialData?.injuryDetails?.diagnosis || "");
    const [painLevel, setPainLevel] = useState<number>(initialData?.injuryDetails?.painLevel || 5);
    const [injuryLocation, setInjuryLocation] = useState<string>(initialData?.injuryDetails?.location || "");

    const [errors, setErrors] = useState<Record<string, string>>({});

    // --- VALIDATION & HANDLERS ---

    const validateSection = (section: number): boolean => {
        const newErrors: Record<string, string> = {};

        if (section === 0) { // Biometrics
            if (!age || parseInt(age) < 13 || parseInt(age) > 100) newErrors.age = "Età valida richiesta (13-100)";
            if (!weight || parseFloat(weight) < 30 || parseFloat(weight) > 300) newErrors.weight = "Peso valido richiesto";
            if (!height || parseFloat(height) < 100 || parseFloat(height) > 250) newErrors.height = "Altezza valida richiesta";
            if (!sex) newErrors.sex = "Seleziona sesso";
        }

        if (section === 1) { // Goals
            if (!goal) newErrors.goal = "Seleziona un obiettivo";
            if (!experience) newErrors.experience = "Seleziona esperienza";
        }

        if (section === 2) { // Health
            if (hasInjury === null) newErrors.hasInjury = "Rispondi alla domanda sulla salute";
            if (hasInjury === true) {
                if (!injuryDiagnosis || injuryDiagnosis.length < 3) newErrors.injuryDiagnosis = "Descrivi brevemente l'infortunio";
                if (!injuryLocation) newErrors.injuryLocation = "Indica la zona (es. schiena, ginocchio)";
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleNext = () => {
        if (!validateSection(currentSection)) {
            hapticFeedback.notification("error");
            return;
        }

        hapticFeedback.selection();
        if (currentSection < TOTAL_SECTIONS - 1) {
            setCurrentSection(prev => prev + 1);
        } else {
            handleComplete();
        }
    };

    const handleBack = () => {
        if (currentSection > 0) {
            setCurrentSection(prev => prev - 1);
        }
    };

    const handleComplete = () => {
        onComplete({
            age: parseInt(age),
            weight: parseFloat(weight),
            height: parseFloat(height),
            sex: sex as IntakeData["sex"],
            primaryGoal: goal,
            experience: experience as IntakeData["experience"],
            daysPerWeek: days,
            hasInjury: hasInjury === true,
            injuryDetails: hasInjury ? {
                diagnosis: injuryDiagnosis,
                painLevel: painLevel,
                location: injuryLocation
            } : undefined
        });
    };

    // --- RENDER ---

    return (
        <div className="flex flex-col h-full bg-background relative overflow-hidden">

            {/* ProgressBar */}
            <div className="px-4 py-4 safe-area-top w-full z-10 bg-background/95 backdrop-blur shadow-sm">
                <div className="flex gap-2 mb-2">
                    {[...Array(TOTAL_SECTIONS)].map((_, i) => (
                        <div
                            key={i}
                            className={cn(
                                "h-1.5 flex-1 rounded-full transition-all duration-300",
                                i <= currentSection ? "bg-primary" : "bg-muted"
                            )}
                        />
                    ))}
                </div>
                <div className="flex justify-between text-xs font-medium text-muted-foreground">
                    <span>{currentSection === 0 ? "Profilo" : currentSection === 1 ? "Obiettivi" : "Salute"}</span>
                    <span>{currentSection + 1}/{TOTAL_SECTIONS}</span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-6 pb-32">
                <div className="max-w-md mx-auto animate-in fade-in slide-in-from-right-8 duration-300">

                    {/* SECTION 1: BIOMETRICS */}
                    {currentSection === 0 && (
                        <div className="space-y-6">
                            <div className="text-center space-y-2 mb-8">
                                <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
                                    <User className="w-8 h-8 text-primary" />
                                </div>
                                <h2 className="text-2xl font-bold">Chi sei?</h2>
                                <p className="text-sm text-muted-foreground">Partiamo dalle basi per calibrare il tutto.</p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Peso (kg)</label>
                                    <input
                                        type="number"
                                        value={weight}
                                        onChange={(e) => setWeight(e.target.value)}
                                        className={cn("w-full px-4 py-3 rounded-xl border bg-secondary/30 text-lg", errors.weight && "border-red-500")}
                                        placeholder="75"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Altezza (cm)</label>
                                    <input
                                        type="number"
                                        value={height}
                                        onChange={(e) => setHeight(e.target.value)}
                                        className={cn("w-full px-4 py-3 rounded-xl border bg-secondary/30 text-lg", errors.height && "border-red-500")}
                                        placeholder="175"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Età</label>
                                <input
                                    type="number"
                                    value={age}
                                    onChange={(e) => setAge(e.target.value)}
                                    className={cn("w-full px-4 py-3 rounded-xl border bg-secondary/30 text-lg", errors.age && "border-red-500")}
                                    placeholder="30"
                                />
                            </div>

                            <div className="space-y-2 pt-2">
                                <label className="text-sm font-medium">Sesso Biologico</label>
                                <div className="grid grid-cols-2 gap-3">
                                    {["male", "female"].map((s) => (
                                        <button
                                            key={s}
                                            onClick={() => setSex(s as any)}
                                            className={cn(
                                                "py-3 rounded-xl border transition-all",
                                                sex === s ? "bg-primary text-white border-primary" : "bg-card hover:bg-secondary"
                                            )}
                                        >
                                            {s === "male" ? "Uomo" : "Donna"}
                                        </button>
                                    ))}
                                </div>
                                {errors.sex && <p className="text-red-500 text-xs">{errors.sex}</p>}
                            </div>
                        </div>
                    )}

                    {/* SECTION 2: GOALS */}
                    {currentSection === 1 && (
                        <div className="space-y-6">
                            <div className="text-center space-y-2 mb-8">
                                <div className="w-16 h-16 mx-auto bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center">
                                    <Target className="w-8 h-8 text-blue-600" />
                                </div>
                                <h2 className="text-2xl font-bold">Il tuo Obiettivo</h2>
                                <p className="text-sm text-muted-foreground">Cosa vuoi ottenere con IronRep?</p>
                            </div>

                            <div className="space-y-3">
                                {GOAL_OPTIONS.map((opt) => (
                                    <button
                                        key={opt.value}
                                        onClick={() => { setGoal(opt.value); hapticFeedback.selection(); }}
                                        className={cn(
                                            "w-full p-4 rounded-xl border-2 text-left transition-all flex items-center gap-4",
                                            goal === opt.value ? "border-primary bg-primary/5" : "border-transparent bg-secondary/50"
                                        )}
                                    >
                                        <span className="text-2xl">{opt.icon}</span>
                                        <span className="font-semibold flex-1">{opt.label}</span>
                                        {goal === opt.value && <Check className="w-5 h-5 text-primary" />}
                                    </button>
                                ))}
                                {errors.goal && <p className="text-red-500 text-xs text-center">{errors.goal}</p>}
                            </div>

                            <div className="space-y-3 pt-6 border-t border-border/50">
                                <label className="text-sm font-medium">Livello Esperienza</label>
                                <select
                                    value={experience}
                                    onChange={(e) => setExperience(e.target.value)}
                                    className={cn("w-full px-4 py-3 rounded-xl border bg-secondary/30", errors.experience && "border-red-500")}
                                >
                                    <option value="">Seleziona...</option>
                                    {EXPERIENCE_OPTIONS.map((e) => (
                                        <option key={e.value} value={e.value}>{e.label}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="space-y-3 pt-4">
                                <label className="text-sm font-medium">Giorni a settimana: <span className="text-primary font-bold">{days}</span></label>
                                <input
                                    type="range"
                                    min="2" max="7" step="1"
                                    value={days}
                                    onChange={(e) => setDays(parseInt(e.target.value))}
                                    className="w-full accent-primary h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
                                />
                                <div className="flex justify-between text-xs text-muted-foreground px-1">
                                    <span>2</span><span>7</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* SECTION 3: HEALTH */}
                    {currentSection === 2 && (
                        <div className="space-y-6">
                            <div className="text-center space-y-2 mb-8">
                                <div className="w-16 h-16 mx-auto bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
                                    <Heart className="w-8 h-8 text-red-600" />
                                </div>
                                <h2 className="text-2xl font-bold">Salute & Dolori</h2>
                                <p className="text-sm text-muted-foreground">Fondamentale per la tua sicurezza.</p>
                            </div>

                            <div className="bg-secondary/30 p-6 rounded-2xl border border-border/50">
                                <h3 className="text-lg font-semibold mb-2">Hai infortuni attivi o dolori?</h3>
                                <p className="text-sm text-muted-foreground mb-4">
                                    Ernie, infiammazioni, dolori articolari che limitano i movimenti.
                                </p>

                                <div className="grid grid-cols-2 gap-3">
                                    <button
                                        onClick={() => setHasInjury(false)}
                                        className={cn(
                                            "py-4 rounded-xl font-semibold border-2 transition-all",
                                            hasInjury === false ? "border-green-500 bg-green-500/10 text-green-600" : "border-transparent bg-background"
                                        )}
                                    >
                                        No, sto bene
                                    </button>
                                    <button
                                        onClick={() => setHasInjury(true)}
                                        className={cn(
                                            "py-4 rounded-xl font-semibold border-2 transition-all",
                                            hasInjury === true ? "border-red-500 bg-red-500/10 text-red-600" : "border-transparent bg-background"
                                        )}
                                    >
                                        Sì, ho dolore
                                    </button>
                                </div>
                                {errors.hasInjury && <p className="text-red-500 text-xs mt-2 text-center">{errors.hasInjury}</p>}
                            </div>

                            {/* DYNAMIC INJURY FORM */}
                            {hasInjury === true && (
                                <div className="space-y-4 animate-in fade-in slide-in-from-top-4">
                                    <div className="p-4 bg-red-50 dark:bg-red-950/20 rounded-xl border border-red-200 dark:border-red-900 text-sm">
                                        <div className="flex gap-2 text-red-800 dark:text-red-200">
                                            <AlertCircle className="w-5 h-5 shrink-0" />
                                            <p>Il Medical Agent analizzerà questi dati per adattare il piano.</p>
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Dove fa male?</label>
                                        <input
                                            type="text"
                                            value={injuryLocation}
                                            onChange={(e) => setInjuryLocation(e.target.value)}
                                            placeholder="es. Bassa schiena, Ginocchio destro"
                                            className={cn("w-full px-4 py-3 rounded-xl border bg-background", errors.injuryLocation && "border-red-500")}
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Diagnosi o Descrizione breve</label>
                                        <input
                                            type="text"
                                            value={injuryDiagnosis}
                                            onChange={(e) => setInjuryDiagnosis(e.target.value)}
                                            placeholder="es. Ernia L5-S1, Infiammazione tendinea"
                                            className={cn("w-full px-4 py-3 rounded-xl border bg-background", errors.injuryDiagnosis && "border-red-500")}
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <label className="text-sm font-medium">Livello Dolore (1-10): <span className="text-red-600 font-bold">{painLevel}</span></label>
                                        <input
                                            type="range"
                                            min="1" max="10" step="1"
                                            value={painLevel}
                                            onChange={(e) => setPainLevel(parseInt(e.target.value))}
                                            className="w-full accent-red-600 h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
                                        />
                                        <div className="flex justify-between text-xs text-muted-foreground px-1">
                                            <span>Fastidio</span><span>Insopportabile</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                </div>
            </div>

            {/* FOOTER NAV */}
            <div className="fixed bottom-0 left-0 right-0 p-4 bg-background/80 backdrop-blur border-t safe-area-bottom z-10">
                <div className="max-w-md mx-auto flex gap-3">
                    {currentSection > 0 && (
                        <button
                            onClick={handleBack}
                            className="px-6 py-4 rounded-xl font-semibold bg-secondary hover:bg-secondary/80 text-foreground transition-all"
                        >
                            Indietro
                        </button>
                    )}
                    <button
                        onClick={handleNext}
                        className="flex-1 py-4 rounded-xl font-semibold bg-primary text-white hover:bg-primary/90 flex items-center justify-center gap-2 transition-all active:scale-98"
                    >
                        {currentSection === TOTAL_SECTIONS - 1 ? "Inizia Chat" : "Continua"}
                        {currentSection < TOTAL_SECTIONS - 1 && <ChevronRight className="w-5 h-5" />}
                    </button>
                </div>
            </div>

        </div>
    );
}
