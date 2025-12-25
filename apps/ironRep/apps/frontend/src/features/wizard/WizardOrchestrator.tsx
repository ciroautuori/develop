/**
 * Enhanced Wizard Orchestrator (Visual Smart Hybrid - UX POLISHED)
 * 
 * Flow:
 * 1. IntakeStep (Unified) -> Collects Biometrics, Goals, Module Flags
 * 2. Conditional Steps (Visual):
 *    - InjuryDetailsStep (if hasInjury)
 *    - FoodPreferencesStep (if wantNutrition)
 * 3. Silent Completion -> Background AI Profile Build -> Plans
 */

import { useState, useCallback, useEffect } from "react";
// WizardChat REMOVED - Silent Flow
import { IntakeStep, type IntakeData } from "./steps/IntakeStep";
import { InjuryDetailsStep, type InjuryDetails } from "./steps/InjuryDetailsStep";
import { FoodPreferencesStep } from "./steps/FoodPreferencesStep";
import { onboardingApi, usersApi, wizardApi, type UserProfile } from "../../lib/api";
import { plansApi as weeklyPlansApi } from "../../lib/api/plans";
import { logger } from "../../lib/logger";
import { useNavigate } from "@tanstack/react-router";
import { Loader2, AlertCircle } from "lucide-react";
import { toast } from "../../components/ui/Toast";
// UX Polish Imports
import { useWizardDraft, type WizardDraft } from "./hooks/useWizardDraft";
import { SmartLoader } from "./components/SmartLoader";

type WizardStep = "intake" | "injury-details" | "food-prefs" | "completing-silent" | "completing" | "error";

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
  const [error, setError] = useState<OnboardingError | null>(null);

  // UX Hooks
  const { draft, hasLoaded, saveDraft, clearDraft } = useWizardDraft();

  // Restore Logic (Draft > Server User Data)
  useEffect(() => {
    if (!hasLoaded) return; // Wait for hooks

    const restoreProgress = async () => {
      try {
        // Priority 1: Local Draft (if valid and recent)
        if (draft && draft.intakeData) {
          logger.info("Found local draft, restoring...", draft);
          setIntakeData(draft.intakeData);
          if (draft.injuryData) setInjuryData(draft.injuryData);
          if (draft.foodPrefs) setFoodPrefs(draft.foodPrefs);

          // Only restore step if valid
          if (draft.step && ["intake", "injury-details", "food-prefs"].includes(draft.step)) {
            setCurrentStep(draft.step as WizardStep);
          }

          toast.success({ title: "Bentornato!", description: "Abbiamo recuperato i tuoi progressi." });
          setIsRestoring(false);
          return;
        }

        // Priority 2: Server User Data
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
  }, [hasLoaded]); // Run once when hook is ready

  // Auto-Save Effect
  useEffect(() => {
    if (!isRestoring && !isSubmitting && currentStep !== "completing" && currentStep !== "completing-silent") {
      saveDraft(currentStep, intakeData, injuryData, foodPrefs);
    }
  }, [currentStep, intakeData, injuryData, foodPrefs, saveDraft, isRestoring, isSubmitting]);

  // STEP 1: Intake Complete
  const handleIntakeComplete = async (data: IntakeData) => {
    logger.info("✅ Intake collected", { data });
    setIntakeData(data);

    // Determine Next Step
    if (data.hasInjury) {
      setCurrentStep("injury-details");
    } else if (data.wantNutrition) {
      setCurrentStep("food-prefs");
    } else {
      // Direct finish
      triggerSilentCompletion(data, null, null);
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
      triggerSilentCompletion(intakeData!, data, null);
    }
  };

  // STEP 2b: Food Prefs Complete
  const handleFoodComplete = (prefs: { liked: string[], disliked: string[] }) => {
    logger.info("✅ Food prefs collected", prefs);
    setFoodPrefs(prefs);
    triggerSilentCompletion(intakeData!, injuryData, prefs);
  };

  // Skip handlers to keep flow moving
  const handleSkipInjury = () => {
    // If skipped, move on
    if (intakeData?.wantNutrition) setCurrentStep("food-prefs");
    else triggerSilentCompletion(intakeData!, null, null);
  };

  const handleSkipFood = () => triggerSilentCompletion(intakeData!, injuryData, null);


  // TRIGGER SILENT COMPLETION
  const triggerSilentCompletion = useCallback(async (
    intake: IntakeData,
    injury: InjuryDetails | null,
    food: { liked: string[], disliked: string[] } | null
  ) => {
    setCurrentStep("completing-silent");
    setIsSubmitting(true);

    try {
      // 1. Wizard Agent Silent Build (Context, RAG, Agent Config)
      await wizardApi.completeSilent({
        intake,
        injuryDetails: injury,
        foodPreferences: food
      });

      // 2. Standard Finalization (Plans generation)
      await completeOnboarding(intake, injury, food);

    } catch (err: any) {
      logger.error("Silent completion failed", err);
      setError({ message: err.message || "Errore durante la creazione del profilo AI", retryData: { intake, injury, food } });
      setCurrentStep("error");
    }
  }, []);

  // FINALIZATION (Plans)
  const completeOnboarding = useCallback(async (
    intake: IntakeData,
    injury: InjuryDetails | null,
    food: { liked: string[], disliked: string[] } | null
  ) => {
    setCurrentStep("completing"); // Just visual change
    setIsSubmitting(true);
    setError(null);

    try {
      logger.info("Finalizing onboarding...");

      // 1. Merge all data for User Profile
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
          injury_date: injury?.injury_date, // Allow undefined
          injury_description: injury.injury_description
        } : {}),
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

      // CLEAR DRAFT ON SUCCESS
      clearDraft();

      // 4. Navigate
      toast.success({ title: "Profilo creato!", description: "Generazione piano in corso..." });

      // Delay slightly for UX
      setTimeout(() => {
        if (onComplete) onComplete();
        else navigate({ to: "/" });
      }, 1500);

    } catch (err: any) {
      logger.error("Onboarding failed", err);
      setError({ message: err.message || "Errore sconosciuto", retryData: { intake, injury, food } });
      setCurrentStep("error");
    } finally {
      setIsSubmitting(false);
    }
  }, [navigate, onComplete, clearDraft]); // Added clearDraft dependency

  // RENDER

  if (isRestoring || currentStep === "completing-silent" || currentStep === "completing") {
    // USE SMART LOADER HERE
    if (currentStep === "completing-silent" || currentStep === "completing") {
      return <SmartLoader />;
    }

    // Initial Restore Loader
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background text-center px-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <h2 className="text-xl font-bold">
          Caricamento...
        </h2>
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

  if (currentStep === "error") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background px-4 text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-xl font-bold">Qualcosa è andato storto</h2>
        <p className="text-muted-foreground mt-2 mb-6">{error?.message}</p>
        <button
          onClick={() => error && triggerSilentCompletion(intakeData!, injuryData, foodPrefs)}
          className="px-6 py-3 bg-primary text-white rounded-xl font-semibold hover:bg-primary/90 transition-colors"
        >
          Riprova
        </button>
      </div>
    );
  }

  return null;
}
