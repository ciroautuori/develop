/**
 * Weekly Plans - Tipi per piani settimanali degli agenti
 */

// ============================================================================
// ENUMS
// ============================================================================

export type AgentType = 'coach' | 'medical' | 'nutrition';
export type PlanStatus = 'draft' | 'active' | 'completed' | 'skipped';
export type DayOfWeek = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';

// ============================================================================
// BASE TYPES
// ============================================================================

export interface WeeklyPlanBase {
  id: string;
  userId: string;
  weekNumber: number; // 1-52
  year: number;
  startDate: string; // ISO date (Monday)
  endDate: string; // ISO date (Sunday)
  status: PlanStatus;
  createdAt: string;
  updatedAt: string;
  notes?: string;
}

// ============================================================================
// COACH - Workout Plans
// ============================================================================

export interface WorkoutExercise {
  id: string;
  name: string;
  sets: number;
  reps: string; // "8-10" or "5" or "AMRAP"
  weight?: number;
  rest?: number; // seconds
  tempo?: string; // "3-1-2-0"
  notes?: string;
  completed?: boolean;
  actualSets?: number;
  actualReps?: string;
  actualWeight?: number;
}

export interface WorkoutSession {
  id: string;
  dayOfWeek: DayOfWeek;
  name: string;
  type: 'strength' | 'conditioning' | 'recovery' | 'skill' | 'wod' | 'rest';
  duration: number; // minutes
  exercises: WorkoutExercise[];
  completed: boolean;
  completedAt?: string;
  rating?: number; // 1-5
  notes?: string;
}

export interface CoachWeeklyPlan extends WeeklyPlanBase {
  agentType: 'coach';
  sessions: WorkoutSession[];
  goals: string[];
  focus: string; // "Upper body focus" | "Deload week" | etc
  totalSessions: number;
  completedSessions: number;
  weeklyVolume?: number; // total sets
}

// ============================================================================
// MEDICAL - Recovery Plans
// ============================================================================

export interface MobilityExercise {
  id: string;
  name: string;
  duration: number; // seconds
  sets: number;
  targetArea: string;
  videoUrl?: string;
  completed?: boolean;
}

export interface PainCheckIn {
  id: string;
  date: string;
  painLevel: number; // 0-10
  locations: string[];
  redFlags?: string[];
  notes?: string;
  mobility?: number; // 0-10
}

export interface MedicalDailyProtocol {
  dayOfWeek: DayOfWeek;
  exercises: MobilityExercise[];
  checkInRequired: boolean;
  checkIn?: PainCheckIn;
}

export interface MedicalWeeklyPlan extends WeeklyPlanBase {
  agentType: 'medical';
  phase: string; // "Fase 1 - Riduzione dolore" | "Fase 2 - Mobilità" | etc
  protocols: MedicalDailyProtocol[];
  targetPainReduction: number; // target pain level to reach
  currentAvgPain: number;
  previousAvgPain: number;
  checkInsCompleted: number;
  checkInsRequired: number;
  restrictions: string[]; // "Evitare flessione lombare > 30°"
  progressNotes?: string;
}

// ============================================================================
// NUTRITION - Meal Plans
// ============================================================================

export interface Meal {
  id: string;
  name: string; // "Colazione" | "Pranzo" | "Cena" | "Snack"
  time: string; // "07:30"
  foods: {
    name: string;
    portion: string;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  }[];
  totalCalories: number;
  totalProtein: number;
  totalCarbs: number;
  totalFat: number;
  logged?: boolean;
  loggedAt?: string;
}

export interface NutritionDailyPlan {
  dayOfWeek: DayOfWeek;
  date: string;
  meals: Meal[];
  targetCalories: number;
  targetProtein: number;
  targetCarbs: number;
  targetFat: number;
  actualCalories?: number;
  actualProtein?: number;
  actualCarbs?: number;
  actualFat?: number;
  water: number; // liters
  waterTarget: number;
  compliance?: number; // 0-100%
}

export interface NutritionWeeklyPlan extends WeeklyPlanBase {
  agentType: 'nutrition';
  goal: 'deficit' | 'maintenance' | 'surplus' | 'recomp';
  dailyCalorieTarget: number;
  dailyProteinTarget: number;
  dailyCarbsTarget: number;
  dailyFatTarget: number;
  days: NutritionDailyPlan[];
  weeklyCompliance: number; // 0-100%
  avgCalories: number;
  avgProtein: number;
  notes?: string;
}

// ============================================================================
// UNIFIED TYPES
// ============================================================================

export type WeeklyPlan = CoachWeeklyPlan | MedicalWeeklyPlan | NutritionWeeklyPlan;

export interface WeekSummary {
  weekNumber: number;
  year: number;
  startDate: string;
  endDate: string;
  coach?: {
    status: PlanStatus;
    focus: string;
    progress: number; // 0-100
  };
  medical?: {
    status: PlanStatus;
    phase: string;
    avgPain: number;
    progress: number;
  };
  nutrition?: {
    status: PlanStatus;
    goal: string;
    compliance: number;
  };
}

export interface MonthCalendarData {
  year: number;
  month: number; // 1-12
  weeks: WeekSummary[];
}

// ============================================================================
// WEEKLY REVIEW
// ============================================================================

export interface WeeklyReviewRequest {
  agentType: AgentType;
  weekNumber: number;
  year: number;
  userFeedback?: string;
}

export interface WeeklyReviewResponse {
  agentType: AgentType;
  summary: string;
  achievements: string[];
  improvements: string[];
  nextWeekSuggestions: string[];
  newPlanGenerated: boolean;
  newPlanId?: string;
}
