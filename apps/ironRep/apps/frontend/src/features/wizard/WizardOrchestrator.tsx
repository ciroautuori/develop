/**
 * Enhanced Wizard Orchestrator (Refactored v3)
 * 
 * Simplified 2-Step Flow:
 * 1. Unified Intake (IntakeStep) -> Collects Biometrics, Goals, Injury Check
 * 2. Smart Chat (WizardChat) -> Refines plan, skips redundancy
 * 3. Completion -> Generates plans
 */

import { useState, useCallback, useEffect } from "react";
import { WizardChat } from "./WizardChat";
import { IntakeStep, type IntakeData } from "./steps/IntakeStep";
import { onboardingApi, usersApi, type UserProfile } from "../../lib/api";
import { plansApi as weeklyPlansApi } from "../../lib/api/plans";
import { logger } from "../../lib/logger";
import { useNavigate } from "@tanstack/react-router";
import { Loader2, AlertCircle } from "lucide-react";
import { toast } from "../../components/ui/Toast";

type WizardStep = "intake" | "chat" | "completing" | "error";

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
  const [chatData, setChatData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<OnboardingError | null>(null);

  // Restore Logic
  useEffect(() => {
    const restoreProgress = async () => {
      try {
        const user = await usersApi.getMe();
        if (user) {
          // Attempt to reconstruct intake data if exists
          if (user.age && user.weight_kg && user.primary_goal) {
            const restoredIntake: IntakeData = {
              age: user.age,
              weight_kg: user.weight_kg,
              height_cm: user.height_cm || 0,
              sex: (user.sex as any) || "male",
              primaryGoal: user.primary_goal,
              experience: (user.training_experience as any) || "beginner",
              daysPerWeek: user.available_days || 3,
              hasInjury: user.has_injury || false,
              injuryDetails: user.has_injury ? {
                diagnosis: user.injury_diagnosis || "",
                painLevel: 5, // Default if missing
                location: user.injury_description || "" // Mapping description to location loosely
              } : undefined
            };
            setIntakeData(restoredIntake);
            // If we have basic data, we could theoretically jump to chat, 
            // but let's keep them on intake to confirm details unless fully onboarded.
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

  // HANDLER: Intake Complete
  const handleIntakeComplete = async (data: IntakeData) => {
    logger.info("✅ Intake collected", { data });
    setIntakeData(data);

    // 1. Persist partial data immediately
    try {
      const me = await usersApi.getMe();
      await usersApi.update(me.id, {
        age: data.age,
        weight_kg: data.weight_kg,
        height_cm: data.height_cm,
        sex: data.sex,
        primary_goal: data.primaryGoal,
        training_experience: data.experience,
        available_days: data.daysPerWeek,
        has_injury: data.hasInjury,
        // Map injury details if present
        ...(data.hasInjury && data.injuryDetails ? {
          injury_diagnosis: data.injuryDetails.diagnosis,
          injury_description: `${data.injuryDetails.location} - Pain Level: ${data.injuryDetails.painLevel}`,
          // Note: Backend might need specific fields, utilizing description for extra context
        } : {})
      });
    } catch (e) {
      logger.error("Failed to persist intake data", { error: e });
      // Proceed anyway, we have it in state
    }

    setCurrentStep("chat");
  };

  // HANDLER: Chat Complete -> Finish
  const handleChatComplete = (finalData: Record<string, unknown>) => {
    logger.info("✅ Chat completed", { finalData });
    setChatData(finalData);
    if (intakeData) {
      completeOnboarding(intakeData, finalData);
    }
  };

  // FINALIZATION
  const completeOnboarding = useCallback(async (intake: IntakeData, chatResult: Record<string, unknown>) => {
    setCurrentStep("completing");
    setIsSubmitting(true);
    setError(null);

    try {
      logger.info("Finalizing onboarding...");

      // 1. Merge all data for final profile update
      const completeProfile: Partial<UserProfile> = {
        age: intake.age,
        weight_kg: intake.weight_kg,
        height_cm: intake.height_cm,
        sex: intake.sex,
        primary_goal: intake.primaryGoal,
        training_experience: intake.experience,
        available_days: intake.daysPerWeek,
        has_injury: intake.hasInjury,
        ...(intake.hasInjury && intake.injuryDetails ? {
          injury_diagnosis: intake.injuryDetails.diagnosis,
          injury_description: `${intake.injuryDetails.location} (Pain: ${intake.injuryDetails.painLevel}/10)`
        } : {}),
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
      if (intake.hasInjury && intake.injuryDetails) {
        planPromises.push(weeklyPlansApi.generateMedicalProtocol({
          target_areas: [intake.injuryDetails.location || "General"],
          current_pain_level: intake.injuryDetails.painLevel
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

  if (currentStep === "chat") {
    return (
      <WizardChat
        onComplete={handleChatComplete}
        initialBiometrics={{
          age: intakeData?.age || 0,
          weight_kg: intakeData?.weight_kg || 0,
          height_cm: intakeData?.height_cm || 0,
          sex: intakeData?.sex || "other"
        }}
        initialContext={{
          intake: intakeData, // Pass full rich object for Agent
          injury: intakeData?.hasInjury ? intakeData.injuryDetails : undefined,
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
          onClick={() => error && completeOnboarding(error.retryData.intake, error.retryData.chatResult)}
          className="px-6 py-3 bg-primary text-white rounded-xl font-semibold"
        >
          Riprova
        </button>
      </div>
    );
  }

  return null;
}

type WizardStep =
  | "biometrics"
  | "training_goals"
  | "lifestyle"
  | "nutrition_goals"
  | "chat"
  | "food_prefs"
  | "injury"
  | "strength"
  | "completing"
  | "error";

// Helper to calculate total steps based on agent config
const calculateTotalSteps = (config: Record<string, unknown>, hasNutrition: boolean): number => {
  let steps = 4; // biometrics + training_goals + lifestyle + chat always
  if (hasNutrition) steps += 2; // nutrition_goals + food_prefs
  if (config.medical_mode === "injury_recovery" || config.has_injury || config.health_conditions) steps++;
  if (config.coach_mode !== "disabled" || config.sport_type) steps++;
  return steps;
};

const getStepNumber = (step: WizardStep, config: Record<string, unknown>, hasNutrition: boolean): number => {
  const stepOrder: WizardStep[] = ["biometrics", "training_goals", "lifestyle"];
  if (hasNutrition) stepOrder.push("nutrition_goals");
  if (hasNutrition) stepOrder.push("food_prefs");
  if (config.medical_mode === "injury_recovery" || config.has_injury || config.health_conditions) stepOrder.push("injury");
  if (config.coach_mode !== "disabled" || config.sport_type) stepOrder.push("strength");
  stepOrder.push("chat");
  return stepOrder.indexOf(step) + 1;
};

interface OnboardingError {
  message: string;
  retryData: {
    biometrics: BiometricsData;
    injury: InjuryDetails | null;
    strength: BaselineStrength | null;
  } | null;
}

interface WizardOrchestratorProps {
  onComplete?: () => void;
}

export function WizardOrchestrator({ onComplete }: WizardOrchestratorProps) {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<WizardStep>("biometrics");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Collected data from wizard
  const [collectedData, setCollectedData] = useState<Record<string, unknown>>({});
  const [agentConfig, setAgentConfig] = useState<Record<string, unknown>>({});
  const [biometricsData, setBiometricsData] = useState<BiometricsData | null>(null);
  const [trainingGoalsData, setTrainingGoalsData] = useState<TrainingGoalsData | null>(null);
  const [lifestyleData, setLifestyleData] = useState<LifestyleData | null>(null);
  const [nutritionGoalsData, setNutritionGoalsData] = useState<NutritionGoalsData | null>(null);
  const [injuryData, setInjuryData] = useState<InjuryDetails | null>(null);
  const [foodPreferencesData, setFoodPreferencesData] = useState<{ liked: string[], disliked: string[] } | null>(null);
  const [error, setError] = useState<OnboardingError | null>(null);
  const [stepHistory, setStepHistory] = useState<WizardStep[]>([]);

  const hasNutritionEnabled = nutritionGoalsData !== null || trainingGoalsData?.primary_goal === "fat_loss" || trainingGoalsData?.primary_goal === "muscle_gain";
  const [isRestoring, setIsRestoring] = useState(true);
  const [googleUpdates, setGoogleUpdates] = useState<string[]>([]);

  // RESTORE STATE FROM BACKEND ON MOUNT
  useEffect(() => {
    const restoreProgress = async () => {
      try {
        // Sync with Google Fit first to get latest biometrics
        const googleSyncFields: string[] = [];
        try {
          const syncResult = await usersApi.syncGoogleFit();
          if (syncResult.success && syncResult.updates) {
            const fields = Object.keys(syncResult.updates);
            googleSyncFields.push(...fields);
            setGoogleUpdates(fields);
            logger.info("Google Fit sync completed on wizard mount", syncResult.updates);
          }
        } catch (syncErr) {
          logger.warn("Google Fit sync failed on mount (likely not linked)", syncErr);
        }

        const user = await usersApi.getMe();
        if (!user) return;

        // 1. Restore Biometrics (even if partial)
        const bio: any = {};
        if (user.age) bio.age = user.age;
        if (user.weight_kg) bio.weight_kg = user.weight_kg;
        if (user.height_cm) bio.height_cm = user.height_cm;
        if (user.sex) bio.sex = user.sex;

        if (Object.keys(bio).length > 0) {
          setBiometricsData(bio);
          setCollectedData(prev => ({ ...prev, ...bio }));
        }

        // 2. Restore Training Goals (even if partial)
        const goals: any = {};
        if (user.primary_goal) goals.primary_goal = user.primary_goal;
        if (user.secondary_goals) goals.secondary_goals = user.secondary_goals;
        if (user.training_experience) goals.training_experience = user.training_experience;
        if (user.training_years) goals.training_years = user.training_years;
        if (user.available_days) goals.available_days = user.available_days;
        if (user.session_duration_minutes) goals.session_duration = user.session_duration_minutes;
        if (user.equipment_available) goals.equipment_available = user.equipment_available;
        if (user.preferred_time) goals.preferred_time = user.preferred_time;
        if (user.intensity_preference) goals.intensity_preference = user.intensity_preference;

        if (Object.keys(goals).length > 0) {
          setTrainingGoalsData(goals);
          setCollectedData(prev => ({ ...prev, ...goals }));
        }

        // 3. Restore Lifestyle (even if partial, e.g. activity_level from Google Fit)
        const life: any = {};
        if (user.activity_level) life.activity_level = user.activity_level;
        if (user.work_type) life.work_type = user.work_type;
        if (user.work_hours_per_day) life.work_hours_per_day = user.work_hours_per_day;
        if (user.commute_active !== undefined) life.commute_active = user.commute_active;
        if (user.stress_level) life.stress_level = user.stress_level;
        if (user.stress_sources) life.stress_sources = user.stress_sources;
        if (user.sleep_hours) life.sleep_hours = user.sleep_hours;
        if (user.sleep_quality) life.sleep_quality = user.sleep_quality;
        if (user.sleep_schedule) life.sleep_schedule = user.sleep_schedule;
        if (user.recovery_capacity) life.recovery_capacity = user.recovery_capacity;
        if (user.health_conditions) life.health_conditions = user.health_conditions;
        if (user.supplements_used) life.supplements_used = user.supplements_used;

        if (Object.keys(life).length > 0) {
          setLifestyleData(life);
          setCollectedData(prev => ({ ...prev, ...life }));
        }

        // 4. Restore Nutrition Goals
        const nut: any = {};
        if (user.nutrition_goal) nut.nutrition_goal = user.nutrition_goal;
        if (user.diet_type) nut.diet_type = user.diet_type;
        if (user.calorie_preference) nut.calorie_preference = user.calorie_preference;
        if (user.custom_calories) nut.custom_calories = user.custom_calories;
        if (user.protein_priority) nut.protein_priority = user.protein_priority;
        if (user.macro_preference) nut.macro_preference = user.macro_preference;
        if (user.meal_frequency) nut.meal_frequency = user.meal_frequency;
        if (user.meal_timing) nut.meal_timing = user.meal_timing;
        if (user.intermittent_window) nut.intermittent_window = user.intermittent_window;
        if (user.allergies) nut.allergies = user.allergies;
        if (user.intolerances) nut.intolerances = user.intolerances;
        if (user.dietary_restrictions) nut.dietary_restrictions = user.dietary_restrictions;
        if (user.budget_preference) nut.budget_preference = user.budget_preference;
        if (user.cooking_skill) nut.cooking_skill = user.cooking_skill;
        if (user.meal_prep_available !== undefined) nut.meal_prep_available = user.meal_prep_available;
        if (user.supplements_interest) nut.supplements_interest = user.supplements_interest;

        if (Object.keys(nut).length > 0) {
          setNutritionGoalsData(nut);
          setCollectedData(prev => ({ ...prev, ...nut }));
        }

        // Determine CURRENT STEP based on missing data
        if (!user.age || !user.weight_kg || !user.height_cm || !user.sex) {
          setCurrentStep("biometrics");
        } else if (!user.primary_goal || !user.training_experience) {
          setCurrentStep("training_goals");
        } else if (!user.activity_level || !user.work_type || !user.sleep_quality) {
          setCurrentStep("lifestyle");
        } else {
          const nutritionRelatedGoals = ["fat_loss", "muscle_gain", "recomp", "lean_bulk"];
          const needsNutrition = nutritionRelatedGoals.includes(user.primary_goal);

          if (needsNutrition && (!user.nutrition_goal || !user.diet_type)) {
            setCurrentStep("nutrition_goals");
          } else if (user.has_injury) {
            setCurrentStep("injury");
          } else if (user.sport_type) {
            setCurrentStep("strength");
          } else {
            setCurrentStep("chat");
          }
        }
      } catch (err) {
        logger.error("Failed to restore progress", err as Record<string, unknown>);
      } finally {
        setIsRestoring(false);
      }
    };

    restoreProgress();
  }, []);
  const handleBiometricsComplete = async (data: BiometricsData) => {
    logger.info("✅ Biometrics collected - moving to training goals", { data });
    setBiometricsData(data);
    setCollectedData(prev => ({ ...prev, ...data }));

    // Persist to backend
    try {
      const me = await usersApi.getMe();
      await usersApi.update(me.id, {
        age: data.age,
        weight_kg: data.weight_kg,
        height_cm: data.height_cm,
        sex: data.sex
      });
    } catch (e) {
      logger.error("Failed to persist biometrics", { error: e });
    }

    setStepHistory(prev => [...prev, "biometrics"]);
    setCurrentStep("training_goals");
  };

  // STEP 2: Handle training goals completion → move to lifestyle
  const handleTrainingGoalsComplete = async (data: TrainingGoalsData) => {
    logger.info("✅ Training goals collected - moving to lifestyle", { data });
    setTrainingGoalsData(data);
    setCollectedData(prev => ({ ...prev, ...data }));

    // Persist to backend
    try {
      const me = await usersApi.getMe();
      await usersApi.update(me.id, {
        primary_goal: data.primary_goal,
        secondary_goals: data.secondary_goals,
        training_experience: data.training_experience,
        training_years: data.training_years,
        available_days: data.available_days,
        session_duration_minutes: data.session_duration,
        equipment_available: data.equipment_available,
        preferred_time: data.preferred_time,
        intensity_preference: data.intensity_preference
      });
    } catch (e) {
      logger.error("Failed to persist training goals", { error: e });
    }

    setStepHistory(prev => [...prev, "training_goals"]);
    setCurrentStep("lifestyle");
  };

  // STEP 3: Handle lifestyle completion → move to nutrition goals or chat
  const handleLifestyleComplete = async (data: LifestyleData) => {
    logger.info("✅ Lifestyle data collected", { data });
    setLifestyleData(data);
    setCollectedData(prev => ({ ...prev, ...data }));

    // Persist to backend
    try {
      const me = await usersApi.getMe();
      await usersApi.update(me.id, {
        activity_level: data.activity_level,
        work_type: data.work_type,
        work_hours_per_day: data.work_hours_per_day,
        commute_active: data.commute_active,
        stress_level: data.stress_level,
        stress_sources: data.stress_sources,
        sleep_hours: data.sleep_hours,
        sleep_quality: data.sleep_quality,
        sleep_schedule: data.sleep_schedule,
        recovery_capacity: data.recovery_capacity,
        health_conditions: data.health_conditions,
        supplements_used: data.supplements_used
      });
    } catch (e) {
      logger.error("Failed to persist lifestyle", { error: e });
    }

    setStepHistory(prev => [...prev, "lifestyle"]);

    // If training goal is related to nutrition, go to nutrition goals
    const nutritionRelatedGoals = ["fat_loss", "muscle_gain", "recomp", "lean_bulk"];
    if (trainingGoalsData && nutritionRelatedGoals.includes(trainingGoalsData.primary_goal)) {
      setCurrentStep("nutrition_goals");
    } else if (lifestyleData?.health_conditions || agentConfig.has_injury) {
      setCurrentStep("injury");
    } else if (trainingGoalsData?.sport_type || agentConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      setCurrentStep("chat");
    }
  };

  // STEP 4: Handle nutrition goals completion → move to chat
  const handleNutritionGoalsComplete = async (data: NutritionGoalsData) => {
    logger.info("✅ Nutrition goals collected - moving to chat", { data });
    setNutritionGoalsData(data);
    setCollectedData(prev => ({ ...prev, ...data }));

    // Persist to backend
    try {
      const me = await usersApi.getMe();
      await usersApi.update(me.id, {
        nutrition_goal: data.nutrition_goal,
        diet_type: data.diet_type,
        calorie_preference: data.calorie_preference,
        custom_calories: data.custom_calories,
        protein_priority: data.protein_priority,
        macro_preference: data.macro_preference,
        meal_frequency: data.meal_frequency,
        meal_timing: data.meal_timing,
        intermittent_window: data.intermittent_window,
        allergies: data.allergies,
        intolerances: data.intolerances,
        dietary_restrictions: data.dietary_restrictions,
        budget_preference: data.budget_preference,
        cooking_skill: data.cooking_skill,
        meal_prep_available: data.meal_prep_available,
        supplements_interest: data.supplements_interest
      });
    } catch (e) {
      logger.error("Failed to persist nutrition goals", { error: e });
    }

    setStepHistory(prev => [...prev, "nutrition_goals"]);
    setCurrentStep("food_prefs");
  };

  // Back navigation handler
  const handleBack = useCallback(() => {
    if (stepHistory.length > 0) {
      const newHistory = [...stepHistory];
      const previousStep = newHistory.pop();
      setStepHistory(newHistory);
      if (previousStep) {
        setCurrentStep(previousStep);
      }
    }
  }, [stepHistory]);

  // STEP 5: Handle chat completion -> Finish onboarding
  const handleChatComplete = (data: Record<string, unknown>) => {
    logger.info("✅ Chat wizard completed", { data });
    completeOnboarding(biometricsData!, injuryData, null);
  };

  // STEP 3: Handle food preferences completion → next step
  const handleFoodPreferencesComplete = (preferences: { liked: string[], disliked: string[] }) => {
    logger.info("✅ Food preferences collected", { preferences });
    setFoodPreferencesData(preferences);
    setCollectedData(prev => ({
      ...prev,
      favorite_foods: preferences.liked,
      disliked_foods: preferences.disliked
    }));
    setStepHistory(prev => [...prev, "food_prefs"]);

    if (lifestyleData?.health_conditions || agentConfig.has_injury) {
      setCurrentStep("injury");
    } else if (trainingGoalsData?.sport_type || agentConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      setCurrentStep("chat");
    }
  };

  const handleFoodPreferencesSkip = () => {
    logger.info("Food preferences skipped");
    handleFoodPreferencesComplete({ liked: [], disliked: [] });
  };

  // Handle injury details completion → strength or complete
  const handleInjuryComplete = (data: InjuryDetails) => {
    logger.info("Injury details collected", { data });
    setInjuryData(data);
    setCollectedData(prev => ({
      ...prev,
      injury_diagnosis: data.diagnosis,
      injury_description: data.injury_description,
      injury_date: data.injury_date
    }));
    setStepHistory(prev => [...prev, "injury"]);

    // Check if strength baseline needed
    if (trainingGoalsData?.sport_type || agentConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      setCurrentStep("chat");
    }
  };

  // Handle injury skip
  const handleInjurySkip = () => {
    logger.info("Injury details skipped");

    if (trainingGoalsData?.sport_type || agentConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      setCurrentStep("chat");
    }
  };

  // Handle strength completion or skip → complete
  const handleStrengthComplete = (data: BaselineStrength) => {
    logger.info("Strength baseline collected", { data });
    setCollectedData(prev => ({
      ...prev,
      deadlift_1rm: data.baseline_deadlift_1rm,
      squat_1rm: data.baseline_squat_1rm
    }));
    setStepHistory(prev => [...prev, "strength"]);
    setCurrentStep("chat");
  };

  const handleStrengthSkip = () => {
    logger.info("Strength baseline skipped");
    setStepHistory(prev => [...prev, "strength"]);
    setCurrentStep("chat");
  };

  // ============================================================================
  // COMPLETE ONBOARDING - Full Integration
  // ============================================================================
  const completeOnboarding = useCallback(async (
    biometrics: BiometricsData,
    injury: InjuryDetails | null,
    strength: BaselineStrength | null
  ) => {
    setCurrentStep("completing");
    setIsSubmitting(true);
    setError(null);

    try {
      logger.info("Starting complete onboarding integration...");

      // 1. Build complete user profile data with proper typing
      const completeProfileData: Partial<UserProfile> & Record<string, unknown> = {
        ...collectedData,
        // Normalize training duration field name
        ...(collectedData.session_duration_minutes === undefined && collectedData.session_duration !== undefined && {
          session_duration_minutes: collectedData.session_duration,
        }),
        // Biometrics
        age: biometrics.age,
        weight_kg: biometrics.weight_kg,
        height_cm: biometrics.height_cm,
        sex: biometrics.sex,
        // Injury (if collected)
        ...(injury && {
          injury_date: injury.injury_date,
          diagnosis: injury.diagnosis,
          injury_description: injury.injury_description,
        }),
        // Strength (if collected)
        ...(strength && {
          baseline_deadlift_1rm: strength.baseline_deadlift_1rm,
          baseline_squat_1rm: strength.baseline_squat_1rm,
        }),
      };

      // 2. Complete onboarding (sets is_onboarded = true)
      await onboardingApi.complete(completeProfileData);
      logger.info("✅ Onboarding marked as complete");

      // 3. Create initial biometrics entry (backend uses auth token for user_id)
      await biometricsApi.create({
        date: new Date().toISOString(),
        weight_kg: biometrics.weight_kg,
        height_cm: biometrics.height_cm,
      });
      logger.info("✅ Initial biometrics entry created");

      // 4. Update user profile with ALL collected data
      const currentUser = await usersApi.getMe();
      await usersApi.update(currentUser.id, completeProfileData);
      logger.info("✅ User profile updated with complete data");

      // 4.5 Save food preferences if available (BLOCKING before plan generation)
      if (foodPreferencesData && (foodPreferencesData.liked.length > 0 || foodPreferencesData.disliked.length > 0)) {
        try {
          await weeklyPlansApi.savePreferences({
            nutrition: {
              favorite_foods: foodPreferencesData.liked,
              disliked_foods: foodPreferencesData.disliked
            }
          });
          logger.info("✅ Food preferences saved to backend");
        } catch (err) {
          logger.error("Failed to save food preferences", err as Record<string, unknown>);
          // Non-fatal error, proceed
        }
      }

      // 5. Generate plans for enabled agents (parallel, non-blocking)
      const config = agentConfig;
      const planPromises: Promise<unknown>[] = [];

      if (config.sport_type && config.coach_mode !== "disabled") {
        planPromises.push(
          weeklyPlansApi.generateCoachPlan({
            focus: String(config.sport_type),
            days_available: Number(collectedData.available_days) || 4,
          })
        );
      }

      if (config.medical_mode === "injury_recovery" || config.has_injury) {
        planPromises.push(
          weeklyPlansApi.generateMedicalProtocol({
            current_pain_level: Number(collectedData.pain_level) || 5,
            target_areas: (collectedData.pain_locations as string[]) || [],
          })
        );
      }

      if (config.nutrition_mode && config.nutrition_mode !== "disabled") {
        planPromises.push(
          weeklyPlansApi.generateNutritionPlan({
            goal: config.nutrition_mode === "full_diet_plan" ? "balanced" : "recipes",
            calorie_target: Number(collectedData.calorie_target) || undefined,
          })
        );
      }

      // Non-blocking plan generation
      Promise.allSettled(planPromises).then((results) => {
        const succeeded = results.filter(r => r.status === "fulfilled").length;
        logger.info(`✅ ${succeeded}/${planPromises.length} agent plans generated`);
      });

      // 6. Success toast and navigate
      toast.success({
        title: "Profilo completato!",
        description: "I tuoi piani personalizzati sono in generazione",
      });

      logger.info("🎉 Onboarding complete - navigating to home");
      if (onComplete) {
        onComplete();
      } else {
        navigate({ to: "/" });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Errore sconosciuto";
      logger.error("❌ Error during onboarding completion", { error: err });

      // Set error state for retry UI
      setError({
        message: errorMessage,
        retryData: { biometrics, injury, strength },
      });
      setCurrentStep("error");

      toast.error({
        title: "Errore durante il completamento",
        description: "Puoi riprovare usando il pulsante qui sotto",
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [biometricsData, collectedData, agentConfig, foodPreferencesData, navigate, onComplete]);

  // Retry handler
  const handleRetry = useCallback(() => {
    if (error?.retryData) {
      const { biometrics, injury, strength } = error.retryData;
      completeOnboarding(biometrics, injury, strength);
    }
  }, [error, completeOnboarding]);

  // ============================================================================
  // RENDER
  // ============================================================================

  if (isRestoring && currentStep !== "error") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Recupero progressi...</p>
      </div>
    );
  }

  if (currentStep === "biometrics") {
    // BiometricsStep has its own internal header - no wrapper needed
    return <BiometricsStep onComplete={handleBiometricsComplete} initialData={biometricsData || undefined} />;
  }

  if (currentStep === "training_goals") {
    // TrainingGoalsStep has internal section progress - wrap with global progress
    return (
      <>
        <WizardProgressHeader
          currentStep={2}
          totalSteps={calculateTotalSteps(agentConfig, hasNutritionEnabled)}
          stepLabel="Obiettivi Allenamento"
          onBack={handleBack}
          showBack={true}
        />
        <TrainingGoalsStep
          onComplete={handleTrainingGoalsComplete}
          initialData={trainingGoalsData || undefined}
        />
      </>
    );
  }

  if (currentStep === "lifestyle") {
    return (
      <>
        <WizardProgressHeader
          currentStep={3}
          totalSteps={calculateTotalSteps(agentConfig, hasNutritionEnabled)}
          stepLabel="Stile di Vita"
          onBack={handleBack}
          showBack={true}
        />
        <LifestyleStep
          onComplete={handleLifestyleComplete}
          initialData={lifestyleData || undefined}
        />
      </>
    );
  }

  if (currentStep === "nutrition_goals") {
    return (
      <>
        <WizardProgressHeader
          currentStep={4}
          totalSteps={calculateTotalSteps(agentConfig, hasNutritionEnabled)}
          stepLabel="Obiettivi Nutrizione"
          onBack={handleBack}
          showBack={true}
        />
        <NutritionGoalsStep
          onComplete={handleNutritionGoalsComplete}
          initialData={nutritionGoalsData || undefined}
        />
      </>
    );
  }

  if (currentStep === "chat") {
    // WizardChat has its own full-screen layout
    return (
      <WizardChat
        onComplete={handleChatComplete}
        initialBiometrics={biometricsData}
        initialContext={{
          trainingGoals: trainingGoalsData,
          lifestyle: lifestyleData,
          nutritionGoals: nutritionGoalsData,
          foodPreferences: foodPreferencesData,
          injury: injuryData,
          googleSyncFields: googleUpdates,
        }}
      />
    );
  }

  if (currentStep === "food_prefs") {
    return (
      <>
        <WizardProgressHeader
          currentStep={getStepNumber("food_prefs", agentConfig, hasNutritionEnabled)}
          totalSteps={calculateTotalSteps(agentConfig, hasNutritionEnabled)}
          stepLabel="Preferenze Alimentari"
          onBack={handleBack}
          showBack={stepHistory.length > 0}
        />
        <FoodPreferencesStep
          onComplete={handleFoodPreferencesComplete}
          onSkip={handleFoodPreferencesSkip}
          initialData={{
            liked: (collectedData.favorite_foods as string[]) || [],
            disliked: (collectedData.disliked_foods as string[]) || [],
          }}
        />
      </>
    );
  }

  if (currentStep === "injury") {
    return (
      <>
        <WizardProgressHeader
          currentStep={getStepNumber("injury", agentConfig, hasNutritionEnabled)}
          totalSteps={calculateTotalSteps(agentConfig, hasNutritionEnabled)}
          stepLabel="Dettagli Infortunio"
          onBack={handleBack}
          showBack={stepHistory.length > 0}
        />
        <InjuryDetailsStep
          onComplete={handleInjuryComplete}
          onSkip={handleInjurySkip}
          initialData={{
            diagnosis: collectedData.injury_diagnosis as string,
            injury_description: collectedData.injury_description as string,
            injury_date: collectedData.injury_date as string,
          }}
        />
      </>
    );
  }

  if (currentStep === "strength") {
    return (
      <>
        <WizardProgressHeader
          currentStep={getStepNumber("strength", agentConfig, hasNutritionEnabled)}
          totalSteps={calculateTotalSteps(agentConfig, hasNutritionEnabled)}
          stepLabel="Forza Baseline"
          onBack={handleBack}
          showBack={stepHistory.length > 0}
        />
        <BaselineStrengthStep
          onComplete={handleStrengthComplete}
          onSkip={handleStrengthSkip}
          initialData={{
            baseline_deadlift_1rm: collectedData.deadlift_1rm ? Number(collectedData.deadlift_1rm) : undefined,
            baseline_squat_1rm: collectedData.squat_1rm ? Number(collectedData.squat_1rm) : undefined,
          }}
        />
      </>
    );
  }

  if (currentStep === "completing") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background px-4">
        <Loader2 className="w-12 h-12 animate-spin text-primary mb-4" />
        <h2 className="text-xl font-bold mb-2">Finalizzazione profilo...</h2>
        <p className="text-muted-foreground text-center text-sm">
          Stiamo generando i tuoi piani personalizzati
        </p>
        <div className="mt-6 space-y-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            Salvataggio dati biometrici
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-75" />
            Aggiornamento profilo
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-150" />
            Generazione piani allenamento
          </div>
        </div>
      </div>
    );
  }

  // Error state with retry UI
  if (currentStep === "error" && error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background px-4">
        <div className="w-16 h-16 bg-red-100 dark:bg-red-950/30 rounded-full flex items-center justify-center mb-4">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-xl font-bold mb-2 text-center">Ops! Qualcosa è andato storto</h2>
        <p className="text-muted-foreground text-center text-sm mb-2 max-w-sm">
          Non siamo riusciti a completare la configurazione del tuo profilo.
        </p>
        <p className="text-xs text-muted-foreground/70 mb-6 max-w-sm text-center">
          {error.message}
        </p>

        <button
          onClick={handleRetry}
          disabled={isSubmitting}
          className={cn(
            "flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white",
            "bg-primary hover:bg-primary/90 active:scale-98 transition-all",
            "touch-manipulation min-h-[44px]",
            isSubmitting && "opacity-50 cursor-not-allowed"
          )}
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <RefreshCw className="w-5 h-5" />
          )}
          {isSubmitting ? "Riprovo..." : "Riprova"}
        </button>

        <button
          onClick={() => setCurrentStep("biometrics")}
          className="mt-3 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Torna indietro e modifica i dati
        </button>
      </div>
    );
  }

  return null;
}
