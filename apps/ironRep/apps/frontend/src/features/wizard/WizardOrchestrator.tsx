/**
 * Enhanced Wizard Orchestrator with Complete Inline Data Collection
 *
 * Flow (MARKET-READY):
 * 1. BiometricsStep (sempre) - peso, altezza, età, sesso
 * 2. TrainingGoalsStep (sempre) - obiettivi, esperienza, equipment
 * 3. LifestyleStep (sempre) - attività, lavoro, sonno, stress
 * 4. NutritionGoalsStep (se nutrition) - dieta, macro, allergie
 * 5. Chat RAG (interazione AI personalizzata)
 * 6. FoodPreferencesStep (se nutrition) - cibi FatSecret API
 * 7. InjuryDetailsStep (se injury)
 * 8. BaselineStrengthStep (se coach)
 * 9. Completion
 *
 * @production-ready Complete user profiling for all agents
 */

import { useState, useCallback } from "react";
import { WizardChat } from "./WizardChat";
import {
  BiometricsStep,
  InjuryDetailsStep,
  BaselineStrengthStep,
  FoodPreferencesStep,
  type BiometricsData,
  type InjuryDetails,
  type BaselineStrength,
} from "./steps";
import { TrainingGoalsStep, type TrainingGoalsData } from "./steps/TrainingGoalsStep";
import { LifestyleStep, type LifestyleData } from "./steps/LifestyleStep";
import { NutritionGoalsStep, type NutritionGoalsData } from "./steps/NutritionGoalsStep";
import { onboardingApi, biometricsApi, usersApi, type UserProfile } from "../../lib/api";
import { plansApi as weeklyPlansApi } from "../../lib/api/plans";
import { logger } from "../../lib/logger";
import { useNavigate } from "@tanstack/react-router";
import { Loader2, RefreshCw, AlertCircle } from "lucide-react";
import { toast } from "../../components/ui/Toast";
import { cn } from "../../lib/utils";
import { WizardProgressHeader } from "./components/WizardProgressHeader";

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
  if (config.medical_mode === "injury_recovery" || config.has_injury) steps++;
  if (config.coach_mode !== "disabled" && config.sport_type) steps++;
  return steps;
};

const getStepNumber = (step: WizardStep, config: Record<string, unknown>, hasNutrition: boolean): number => {
  const stepOrder: WizardStep[] = ["biometrics", "training_goals", "lifestyle"];
  if (hasNutrition) stepOrder.push("nutrition_goals");
  stepOrder.push("chat");
  if (hasNutrition) stepOrder.push("food_prefs");
  if (config.medical_mode === "injury_recovery" || config.has_injury) stepOrder.push("injury");
  if (config.coach_mode !== "disabled" && config.sport_type) stepOrder.push("strength");
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

  // RESTORE STATE FROM BACKEND ON MOUNT
  useEffect(() => {
    const restoreProgress = async () => {
      try {
        const user = await usersApi.getMe();
        if (!user) return;

        // Restore Biometrics
        if (user.age && user.weight_kg && user.height_cm && user.sex) {
          const bio: BiometricsData = {
            age: user.age,
            weight_kg: user.weight_kg,
            height_cm: user.height_cm,
            sex: user.sex,
          };
          setBiometricsData(bio);
          setCollectedData(prev => ({ ...prev, ...bio }));

          // Restore Training Goals
          if (user.primary_goal && user.training_experience) {
            const goals: TrainingGoalsData = {
              primary_goal: user.primary_goal as any,
              secondary_goals: user.secondary_goals || [],
              training_experience: user.training_experience as any,
              training_years: user.training_years || 0,
              available_days: user.available_days || 3,
              session_duration: user.session_duration_minutes || 60,
              equipment_available: user.equipment_available || [],
              preferred_time: user.preferred_time || "any",
              intensity_preference: user.intensity_preference || "medium",
            };
            setTrainingGoalsData(goals);
            setCollectedData(prev => ({ ...prev, ...goals }));

            // Restore Lifestyle
            if (user.activity_level && user.work_type) {
              const life: LifestyleData = {
                activity_level: user.activity_level as any,
                work_type: user.work_type as any,
                work_hours_per_day: user.work_hours_per_day || 8,
                commute_active: user.commute_active || false,
                stress_level: user.stress_level || 5,
                stress_sources: user.stress_sources || [],
                sleep_hours: user.sleep_hours || 7,
                sleep_quality: (user.sleep_quality as any) || "average",
                sleep_schedule: (user.sleep_schedule as any) || "variable",
                recovery_capacity: (user.recovery_capacity as any) || "average",
                health_conditions: user.health_conditions || [],
                supplements_used: user.supplements_used || [],
              };
              setLifestyleData(life);
              setCollectedData(prev => ({ ...prev, ...life }));

              // Determine next step
              const nutritionRelatedGoals = ["fat_loss", "muscle_gain", "recomp", "lean_bulk"];
              const needsNutrition = nutritionRelatedGoals.includes(goals.primary_goal);

              if (needsNutrition) {
                if (user.nutrition_goal && user.diet_type) {
                  const nut: NutritionGoalsData = {
                    nutrition_goal: user.nutrition_goal,
                    diet_type: user.diet_type,
                    calorie_preference: user.calorie_preference || "auto",
                    custom_calories: user.custom_calories,
                    protein_priority: user.protein_priority || "balanced",
                    macro_preference: user.macro_preference || "balanced",
                    meal_frequency: user.meal_frequency || 3,
                    meal_timing: user.meal_timing || "regular",
                    intermittent_window: user.intermittent_window,
                    allergies: user.allergies || [],
                    intolerances: user.intolerances || [],
                    dietary_restrictions: user.dietary_restrictions || [],
                    budget_preference: user.budget_preference || "medium",
                    cooking_skill: user.cooking_skill || "basic",
                    meal_prep_available: user.meal_prep_available || false,
                    supplements_interest: user.supplements_interest || [],
                  };
                  setNutritionGoalsData(nut);
                  setCollectedData(prev => ({ ...prev, ...nut }));
                  setCurrentStep("chat"); // Assuming chat hasn't happened yet, or we restart chat.
                } else {
                  setCurrentStep("nutrition_goals");
                }
              } else {
                setCurrentStep("chat");
              }
            } else {
              setCurrentStep("lifestyle");
            }
          } else {
            setCurrentStep("training_goals");
          }
        } else {
          setCurrentStep("biometrics");
        }
      } catch (e) {
        logger.error("Failed to restore progress", { error: e });
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
    } else {
      // Skip nutrition, go directly to chat
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
    setCurrentStep("chat");
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

  // STEP 5: Handle chat completion → conditional food preferences or next step
  const handleChatComplete = (data: Record<string, unknown>) => {
    logger.info("✅ Chat wizard completed with RAG intelligence", { data });

    // Merge chat data with all previously collected inline data
    const mergedData = {
      ...data,
      // Training Goals
      ...(trainingGoalsData && {
        primary_goal: trainingGoalsData.primary_goal,
        secondary_goals: trainingGoalsData.secondary_goals,
        training_experience: trainingGoalsData.training_experience,
        training_years: trainingGoalsData.training_years,
        available_days: trainingGoalsData.available_days,
        session_duration_minutes: trainingGoalsData.session_duration,
        equipment_available: trainingGoalsData.equipment_available,
        preferred_time: trainingGoalsData.preferred_time,
        intensity_preference: trainingGoalsData.intensity_preference,
      }),
      // Lifestyle
      ...(lifestyleData && {
        activity_level: lifestyleData.activity_level,
        work_type: lifestyleData.work_type,
        work_hours_per_day: lifestyleData.work_hours_per_day,
        commute_active: lifestyleData.commute_active,
        stress_level: lifestyleData.stress_level,
        stress_sources: lifestyleData.stress_sources,
        sleep_hours: lifestyleData.sleep_hours,
        sleep_quality: lifestyleData.sleep_quality,
        sleep_schedule: lifestyleData.sleep_schedule,
        recovery_capacity: lifestyleData.recovery_capacity,
        health_conditions: lifestyleData.health_conditions,
        supplements_used: lifestyleData.supplements_used,
      }),
      // Nutrition Goals
      ...(nutritionGoalsData && {
        nutrition_goal: nutritionGoalsData.nutrition_goal,
        diet_type: nutritionGoalsData.diet_type,
        calorie_preference: nutritionGoalsData.calorie_preference,
        custom_calories: nutritionGoalsData.custom_calories,
        protein_priority: nutritionGoalsData.protein_priority,
        macro_preference: nutritionGoalsData.macro_preference,
        meal_frequency: nutritionGoalsData.meal_frequency,
        meal_timing: nutritionGoalsData.meal_timing,
        intermittent_window: nutritionGoalsData.intermittent_window,
        allergies: nutritionGoalsData.allergies,
        intolerances: nutritionGoalsData.intolerances,
        dietary_restrictions: nutritionGoalsData.dietary_restrictions,
        budget_preference: nutritionGoalsData.budget_preference,
        cooking_skill: nutritionGoalsData.cooking_skill,
        meal_prep_available: nutritionGoalsData.meal_prep_available,
        supplements_interest: nutritionGoalsData.supplements_interest,
      }),
    };

    setCollectedData(mergedData);
    setStepHistory(prev => [...prev, "chat"]);

    // Extract agent config from RAG analysis
    const config = (data.agent_config || {}) as Record<string, unknown>;

    // Enhance config with inline data
    const enhancedConfig = {
      ...config,
      // Force nutrition_mode if we collected nutrition goals
      nutrition_mode: nutritionGoalsData ? "full_diet_plan" : config.nutrition_mode,
      // Force coach_mode if we have training goals with equipment
      coach_mode: trainingGoalsData?.equipment_available?.length ? "personalized" : config.coach_mode,
      // Keep sport_type from agent analysis (do not overwrite with goal)
      sport_type: config.sport_type,
    };
    setAgentConfig(enhancedConfig);

    // If nutrition goals collected, go to food preferences
    if (nutritionGoalsData) {
      setCurrentStep("food_prefs");
    } else if (
      enhancedConfig.medical_mode === "injury_recovery" ||
      enhancedConfig.has_injury === true
    ) {
      setCurrentStep("injury");
    } else if (enhancedConfig.coach_mode !== "disabled" && enhancedConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      completeOnboarding(biometricsData!, null, null);
    }
  };

  // STEP 3: Handle food preferences completion → next step
  const handleFoodPreferencesComplete = (preferences: { liked: string[], disliked: string[] }) => {
    logger.info("✅ Food preferences collected", { preferences });
    setFoodPreferencesData(preferences);
    setStepHistory(prev => [...prev, "food_prefs"]);

    if (
      agentConfig.medical_mode === "injury_recovery" ||
      agentConfig.has_injury === true
    ) {
      setCurrentStep("injury");
    } else if (agentConfig.coach_mode !== "disabled" && agentConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      completeOnboarding(biometricsData!, null, null);
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
    setStepHistory(prev => [...prev, "injury"]);

    // Check if strength baseline needed
    if (agentConfig.coach_mode !== "disabled" && agentConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      completeOnboarding(biometricsData!, data, null);
    }
  };

  // Handle injury skip
  const handleInjurySkip = () => {
    logger.info("Injury details skipped");

    if (agentConfig.coach_mode !== "disabled" && agentConfig.sport_type) {
      setCurrentStep("strength");
    } else {
      completeOnboarding(biometricsData!, null, null);
    }
  };

  // Handle strength completion or skip → complete
  const handleStrengthComplete = (data: BaselineStrength) => {
    logger.info("Strength baseline collected", { data });
    completeOnboarding(biometricsData!, injuryData, data);
  };

  const handleStrengthSkip = () => {
    logger.info("Strength baseline skipped");
    completeOnboarding(biometricsData!, injuryData, null);
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
  }, [collectedData, agentConfig, foodPreferencesData, navigate, onComplete]);

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
    return <BiometricsStep onComplete={handleBiometricsComplete} />;
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
