/**
 * Enhanced Wizard Orchestrator (Visual Smart Hybrid)
 * 
 * Flow:
 * 1. IntakeStep (Unified) -> Collects Biometrics, Goals, Module Flags
 * 2. Conditional Steps (Visual):
 *    - InjuryDetailsStep (if hasInjury)
 *    - FoodPreferencesStep (if wantNutrition)
 * 3. Smart Chat (WizardChat) -> Refines plan with full context
 * 4. Completion
 */

import { useState, useCallback, useEffect } from "react";
import { WizardChat } from "./WizardChat";
import { IntakeStep, type IntakeData } from "./steps/IntakeStep";
import { InjuryDetailsStep, type InjuryDetails } from "./steps/InjuryDetailsStep";
import { FoodPreferencesStep } from "./steps/FoodPreferencesStep";
import { onboardingApi, usersApi, type UserProfile } from "../../lib/api";
import { plansApi as weeklyPlansApi } from "../../lib/api/plans";
import { logger } from "../../lib/logger";
import { useNavigate } from "@tanstack/react-router";
import { Loader2, AlertCircle } from "lucide-react";
import { toast } from "../../components/ui/Toast";

type WizardStep = "intake" | "injury-details" | "food-prefs" | "chat" | "completing" | "error";

interface OnboardingError {
  message: string;
  retryData: any;
}

export function WizardOrchestrator({ onComplete }: { onComplete?: () => void }) {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<WizardStep>("intake");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRestoring, setIsRestoring] = useState(true);

  // Data State
  const [intakeData, setIntakeData] = useState<IntakeData | null>(null);
  const [injuryData, setInjuryData] = useState<InjuryDetails | null>(null);
  const [foodPrefs, setFoodPrefs] = useState<{ liked: string[], disliked: string[] } | null>(null);
  const [chatData, setChatData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<OnboardingError | null>(null);

  // Restore Logic
  useEffect(() => {
    const restoreProgress = async () => {
      try {
        const user = await usersApi.getMe();
        if (user) {
          // Simplistic restore logic: if we have basic data, stay on intake or move if fully done.
          // For now, let's keep it simple: always start at Intake but pre-fill if possible.
          if (user.age && user.weight_kg) {
            const restoredIntake: IntakeData = {
              age: user.age,
              weight: user.weight_kg,
              height: user.height_cm || 0,
              sex: (user.sex as any) || "male",
              primaryGoal: user.primary_goal || "",
              experience: (user.training_experience as any) || "beginner",
              daysPerWeek: user.available_days || 3,
              hasInjury: user.has_injury || false,
              wantNutrition: false // Default to false if unknown
            };
            setIntakeData(restoredIntake);
          }
        }
      } catch (err) {
        logger.warn("Failed to restore wizard state", err);
      } finally {
        setIsRestoring(false);
      }
    };
    restoreProgress();
  }, []);

  // STEP 1: Intake Complete
  const handleIntakeComplete = async (data: IntakeData) => {
    logger.info("✅ Intake collected", { data });
    setIntakeData(data);

    // Persist immediately
    try {
      const me = await usersApi.getMe();
      await usersApi.update(me.id, {
        age: data.age,
        weight_kg: data.weight,
        height_cm: data.height,
        sex: data.sex,
        primary_goal: data.primaryGoal,
        training_experience: data.experience,
        available_days: data.daysPerWeek,
        has_injury: data.hasInjury
      });
    } catch (e) {
      logger.error("Failed to persist intake data", { error: e });
    }

    // Determine Next Step
    if (data.hasInjury) {
      setCurrentStep("injury-details");
    } else if (data.wantNutrition) {
      setCurrentStep("food-prefs");
    } else {
      setCurrentStep("chat");
    }
  };

  // STEP 2a: Injury Complete
  const handleInjuryComplete = (data: InjuryDetails) => {
    logger.info("✅ Injury collected", data);
    setInjuryData(data);

    // Next?
    if (intakeData?.wantNutrition) {
      setCurrentStep("food-prefs");
    } else {
      setCurrentStep("chat");
    }
  };

  // STEP 2b: Food Prefs Complete
  const handleFoodComplete = (prefs: { liked: string[], disliked: string[] }) => {
    logger.info("✅ Food prefs collected", prefs);
    setFoodPrefs(prefs);
    setCurrentStep("chat");
  };

  // Skip handlers to keep flow moving
  const handleSkipInjury = () => {
    // If skipped, we assume they'll discuss it in chat
    if (intakeData?.wantNutrition) setCurrentStep("food-prefs");
    else setCurrentStep("chat");
  };

  const handleSkipFood = () => setCurrentStep("chat");


  // STEP 3: Chat Complete -> Finish
  const handleChatComplete = (finalData: Record<string, unknown>) => {
    logger.info("✅ Chat completed", { finalData });
    setChatData(finalData);
    if (intakeData) {
      completeOnboarding(intakeData, injuryData, foodPrefs, finalData);
    }
  };

  // FINALIZATION
  const completeOnboarding = useCallback(async (
    intake: IntakeData,
    injury: InjuryDetails | null,
    food: { liked: string[], disliked: string[] } | null,
    chatResult: Record<string, unknown>
  ) => {
    setCurrentStep("completing");
    setIsSubmitting(true);
    setError(null);

    try {
      logger.info("Finalizing onboarding...");

      // 1. Merge all data
      const completeProfile: Partial<UserProfile> = {
        age: intake.age,
        weight_kg: intake.weight,
        height_cm: intake.height,
        sex: intake.sex,
        primary_goal: intake.primaryGoal,
        training_experience: intake.experience,
        available_days: intake.daysPerWeek,
        has_injury: intake.hasInjury,

        // Injury Details
        ...(injury ? {
          injury_diagnosis: injury.diagnosis,
          injury_date: injury.injury_date,
          injury_description: injury.injury_description
        } : {}),

        // Food Prefs are handled via specialized APIs or Agent Context usually.
        // For now, we rely on the agent having received them in context to generate the Plan.

        ...chatResult // Merge any extra fields extracted by chat
      };

      // 2. Call Complete API
      await onboardingApi.complete(completeProfile as any);

      // 3. Generate Plans (Fire and Forget)
      const planPromises: Promise<any>[] = [];

      // Coach Plan
      if (intake.primaryGoal !== "injury_recovery") {
        planPromises.push(weeklyPlansApi.generateCoachPlan({
          focus: intake.primaryGoal,
          days_available: intake.daysPerWeek
        }));
      }

      // Medical Plan (if injury)
      if (intake.hasInjury && injury) {
        planPromises.push(weeklyPlansApi.generateMedicalProtocol({
          target_areas: [injury.diagnosis], // Approximate target
          current_pain_level: 5 // Default
        }));
      }

      Promise.allSettled(planPromises);

      // 4. Navigate
      toast.success({ title: "Tutto pronto!", description: "Il tuo piano è in fase di generazione." });
      if (onComplete) onComplete();
      else navigate({ to: "/" });

    } catch (err: any) {
      logger.error("Onboarding failed", err);
      setError({ message: err.message || "Errore sconosciuto", retryData: { intake, chatResult } });
      setCurrentStep("error");
    } finally {
      setIsSubmitting(false);
    }
  }, [navigate, onComplete]);

  // RENDER

  if (isRestoring) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Caricamento...</p>
      </div>
    );
  }

  if (currentStep === "intake") {
    return <IntakeStep onComplete={handleIntakeComplete} initialData={intakeData || undefined} />;
  }

  if (currentStep === "injury-details") {
    return <InjuryDetailsStep onComplete={handleInjuryComplete} onSkip={handleSkipInjury} />;
  }

  if (currentStep === "food-prefs") {
    return <FoodPreferencesStep onComplete={handleFoodComplete} onSkip={handleSkipFood} />;
  }

  if (currentStep === "chat") {
    return (
      <WizardChat
        onComplete={handleChatComplete}
        initialBiometrics={{
          age: intakeData?.age || 0,
          weight_kg: intakeData?.weight || 0,
          height_cm: intakeData?.height || 0,
          sex: intakeData?.sex || "other"
        }}
        initialContext={{
          intake: intakeData,
          // Pass collected visual data to agent context so it knows it exists!
          injuryDetails: injuryData,
          foodPreferences: foodPrefs,
          goals: {
            primary: intakeData?.primaryGoal,
            experience: intakeData?.experience
          }
        }}
      />
    );
  }

  if (currentStep === "completing") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background">
        <Loader2 className="w-12 h-12 animate-spin text-primary mb-6" />
        <h2 className="text-xl font-bold">Creazione Profilo...</h2>
        <p className="text-muted-foreground mt-2">L'AI sta analizzando i tuoi dati.</p>
      </div>
    );
  }

  if (currentStep === "error") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background px-4 text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-xl font-bold">Qualcosa è andato storto</h2>
        <p className="text-muted-foreground mt-2 mb-6">{error?.message}</p>
        <button
          onClick={() => error && completeOnboarding(intakeData!, injuryData, foodPrefs, error.retryData.chatResult)}
          className="px-6 py-3 bg-primary text-white rounded-xl font-semibold"
        >
          Riprova
        </button>
      </div>
    );
  }

  return null;
}
