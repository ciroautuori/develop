import { useState, useCallback, useMemo } from "react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
import { RotateCcw, User, Minus, Plus, Info, Flame, AlertTriangle, CheckCircle } from "lucide-react";

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

interface PainPoint {
  location: string;
  intensity: number; // 1-10
  side?: "left" | "right" | "center";
}

interface BodyHeatmapProps {
  selectedLocations: string[];
  painPoints?: PainPoint[];
  onLocationToggle?: (location: string) => void;
  onPainIntensityChange?: (location: string, intensity: number) => void;
  readOnly?: boolean;
  showIntensityControls?: boolean;
  compact?: boolean;
}

interface BodyPart {
  id: string;
  label: string;
  labelIt: string;
  x: number;
  y: number;
  width: number;
  zone: "head" | "upper" | "core" | "lower";
  muscleGroup?: string;
  commonInjuries?: string[];
}

type ViewMode = "front" | "back";

// ============================================================================
// BODY PARTS DATA - Comprehensive anatomical mapping
// ============================================================================

const BODY_PARTS_FRONT: BodyPart[] = [
  // Head & Neck
  { id: "neck-front", label: "Neck", labelIt: "Collo", x: 50, y: 15, width: 8, zone: "head", muscleGroup: "Cervicale", commonInjuries: ["Torcicollo", "Ernia cervicale"] },

  // Shoulders & Upper Arms
  { id: "shoulder-r", label: "Right Shoulder", labelIt: "Spalla Dx", x: 32, y: 22, width: 10, zone: "upper", muscleGroup: "Deltoide", commonInjuries: ["Lesione cuffia", "Lussazione"] },
  { id: "shoulder-l", label: "Left Shoulder", labelIt: "Spalla Sx", x: 68, y: 22, width: 10, zone: "upper", muscleGroup: "Deltoide", commonInjuries: ["Lesione cuffia", "Lussazione"] },

  // Chest
  { id: "chest-r", label: "Right Chest", labelIt: "Petto Dx", x: 42, y: 28, width: 8, zone: "upper", muscleGroup: "Pettorale", commonInjuries: ["Strappo muscolare"] },
  { id: "chest-l", label: "Left Chest", labelIt: "Petto Sx", x: 58, y: 28, width: 8, zone: "upper", muscleGroup: "Pettorale", commonInjuries: ["Strappo muscolare"] },

  // Arms
  { id: "bicep-r", label: "Right Bicep", labelIt: "Bicipite Dx", x: 28, y: 32, width: 6, zone: "upper", muscleGroup: "Bicipite", commonInjuries: ["Tendinite"] },
  { id: "bicep-l", label: "Left Bicep", labelIt: "Bicipite Sx", x: 72, y: 32, width: 6, zone: "upper", muscleGroup: "Bicipite", commonInjuries: ["Tendinite"] },
  { id: "elbow-r", label: "Right Elbow", labelIt: "Gomito Dx", x: 26, y: 40, width: 5, zone: "upper", muscleGroup: "Articolazione", commonInjuries: ["Epicondilite", "Borsite"] },
  { id: "elbow-l", label: "Left Elbow", labelIt: "Gomito Sx", x: 74, y: 40, width: 5, zone: "upper", muscleGroup: "Articolazione", commonInjuries: ["Epicondilite", "Borsite"] },
  { id: "forearm-r", label: "Right Forearm", labelIt: "Avambraccio Dx", x: 24, y: 47, width: 5, zone: "upper", muscleGroup: "Avambraccio" },
  { id: "forearm-l", label: "Left Forearm", labelIt: "Avambraccio Sx", x: 76, y: 47, width: 5, zone: "upper", muscleGroup: "Avambraccio" },
  { id: "wrist-r", label: "Right Wrist", labelIt: "Polso Dx", x: 22, y: 53, width: 4, zone: "upper", muscleGroup: "Articolazione", commonInjuries: ["Tunnel carpale", "Tendinite"] },
  { id: "wrist-l", label: "Left Wrist", labelIt: "Polso Sx", x: 78, y: 53, width: 4, zone: "upper", muscleGroup: "Articolazione", commonInjuries: ["Tunnel carpale", "Tendinite"] },

  // Core
  { id: "abs-upper", label: "Upper Abs", labelIt: "Addome Alto", x: 50, y: 36, width: 10, zone: "core", muscleGroup: "Retto addominale" },
  { id: "abs-lower", label: "Lower Abs", labelIt: "Addome Basso", x: 50, y: 44, width: 10, zone: "core", muscleGroup: "Retto addominale" },
  { id: "oblique-r", label: "Right Oblique", labelIt: "Obliquo Dx", x: 40, y: 40, width: 6, zone: "core", muscleGroup: "Obliqui" },
  { id: "oblique-l", label: "Left Oblique", labelIt: "Obliquo Sx", x: 60, y: 40, width: 6, zone: "core", muscleGroup: "Obliqui" },

  // Hip & Groin
  { id: "hip-r", label: "Right Hip", labelIt: "Anca Dx", x: 40, y: 52, width: 7, zone: "core", muscleGroup: "Flessore anca", commonInjuries: ["Borsite", "Artrosi"] },
  { id: "hip-l", label: "Left Hip", labelIt: "Anca Sx", x: 60, y: 52, width: 7, zone: "core", muscleGroup: "Flessore anca", commonInjuries: ["Borsite", "Artrosi"] },
  { id: "groin", label: "Groin", labelIt: "Inguine", x: 50, y: 54, width: 6, zone: "core", muscleGroup: "Adduttori", commonInjuries: ["Pubalgia", "Strappo"] },

  // Upper Legs
  { id: "quad-r", label: "Right Quadricep", labelIt: "Quadricipite Dx", x: 42, y: 62, width: 8, zone: "lower", muscleGroup: "Quadricipite", commonInjuries: ["Strappo", "Contrattura"] },
  { id: "quad-l", label: "Left Quadricep", labelIt: "Quadricipite Sx", x: 58, y: 62, width: 8, zone: "lower", muscleGroup: "Quadricipite", commonInjuries: ["Strappo", "Contrattura"] },

  // Knees
  { id: "knee-r", label: "Right Knee", labelIt: "Ginocchio Dx", x: 42, y: 72, width: 6, zone: "lower", muscleGroup: "Articolazione", commonInjuries: ["Menisco", "LCA", "Tendinite rotulea"] },
  { id: "knee-l", label: "Left Knee", labelIt: "Ginocchio Sx", x: 58, y: 72, width: 6, zone: "lower", muscleGroup: "Articolazione", commonInjuries: ["Menisco", "LCA", "Tendinite rotulea"] },

  // Lower Legs
  { id: "shin-r", label: "Right Shin", labelIt: "Tibia Dx", x: 42, y: 80, width: 5, zone: "lower", muscleGroup: "Tibiale anteriore", commonInjuries: ["Periostite"] },
  { id: "shin-l", label: "Left Shin", labelIt: "Tibia Sx", x: 58, y: 80, width: 5, zone: "lower", muscleGroup: "Tibiale anteriore", commonInjuries: ["Periostite"] },

  // Ankles & Feet
  { id: "ankle-r", label: "Right Ankle", labelIt: "Caviglia Dx", x: 42, y: 88, width: 4, zone: "lower", muscleGroup: "Articolazione", commonInjuries: ["Distorsione", "Tendinite achillea"] },
  { id: "ankle-l", label: "Left Ankle", labelIt: "Caviglia Sx", x: 58, y: 88, width: 4, zone: "lower", muscleGroup: "Articolazione", commonInjuries: ["Distorsione", "Tendinite achillea"] },
];

const BODY_PARTS_BACK: BodyPart[] = [
  // Neck & Upper Back
  { id: "neck-back", label: "Neck (Back)", labelIt: "Collo Post.", x: 50, y: 15, width: 8, zone: "head", muscleGroup: "Trapezio superiore" },
  { id: "trap-r", label: "Right Trapezius", labelIt: "Trapezio Dx", x: 38, y: 22, width: 8, zone: "upper", muscleGroup: "Trapezio", commonInjuries: ["Contrattura", "Trigger point"] },
  { id: "trap-l", label: "Left Trapezius", labelIt: "Trapezio Sx", x: 62, y: 22, width: 8, zone: "upper", muscleGroup: "Trapezio", commonInjuries: ["Contrattura", "Trigger point"] },

  // Back
  { id: "upper-back-r", label: "Right Upper Back", labelIt: "Dorsale Dx", x: 42, y: 30, width: 8, zone: "upper", muscleGroup: "Romboidi", commonInjuries: ["Contrattura"] },
  { id: "upper-back-l", label: "Left Upper Back", labelIt: "Dorsale Sx", x: 58, y: 30, width: 8, zone: "upper", muscleGroup: "Romboidi", commonInjuries: ["Contrattura"] },
  { id: "lat-r", label: "Right Lat", labelIt: "Gran Dorsale Dx", x: 36, y: 36, width: 8, zone: "upper", muscleGroup: "Gran dorsale" },
  { id: "lat-l", label: "Left Lat", labelIt: "Gran Dorsale Sx", x: 64, y: 36, width: 8, zone: "upper", muscleGroup: "Gran dorsale" },

  // Triceps
  { id: "tricep-r", label: "Right Tricep", labelIt: "Tricipite Dx", x: 28, y: 34, width: 6, zone: "upper", muscleGroup: "Tricipite" },
  { id: "tricep-l", label: "Left Tricep", labelIt: "Tricipite Sx", x: 72, y: 34, width: 6, zone: "upper", muscleGroup: "Tricipite" },

  // Lower Back
  { id: "lower-back", label: "Lower Back", labelIt: "Lombare", x: 50, y: 44, width: 14, zone: "core", muscleGroup: "Erettori spinali", commonInjuries: ["Ernia", "Protrusione", "Lombalgia"] },
  { id: "si-joint-r", label: "Right SI Joint", labelIt: "Sacroiliaca Dx", x: 44, y: 50, width: 5, zone: "core", muscleGroup: "Articolazione", commonInjuries: ["Disfunzione SI"] },
  { id: "si-joint-l", label: "Left SI Joint", labelIt: "Sacroiliaca Sx", x: 56, y: 50, width: 5, zone: "core", muscleGroup: "Articolazione", commonInjuries: ["Disfunzione SI"] },

  // Glutes
  { id: "glute-r", label: "Right Glute", labelIt: "Gluteo Dx", x: 42, y: 56, width: 9, zone: "core", muscleGroup: "Gluteo", commonInjuries: ["Sindrome piriforme", "Contrattura"] },
  { id: "glute-l", label: "Left Glute", labelIt: "Gluteo Sx", x: 58, y: 56, width: 9, zone: "core", muscleGroup: "Gluteo", commonInjuries: ["Sindrome piriforme", "Contrattura"] },

  // Hamstrings
  { id: "hamstring-r", label: "Right Hamstring", labelIt: "Bicipite Femorale Dx", x: 42, y: 66, width: 8, zone: "lower", muscleGroup: "Bicipite femorale", commonInjuries: ["Strappo", "Contrattura"] },
  { id: "hamstring-l", label: "Left Hamstring", labelIt: "Bicipite Femorale Sx", x: 58, y: 66, width: 8, zone: "lower", muscleGroup: "Bicipite femorale", commonInjuries: ["Strappo", "Contrattura"] },

  // Calves
  { id: "calf-r", label: "Right Calf", labelIt: "Polpaccio Dx", x: 42, y: 78, width: 6, zone: "lower", muscleGroup: "Gastrocnemio", commonInjuries: ["Strappo", "Crampi"] },
  { id: "calf-l", label: "Left Calf", labelIt: "Polpaccio Sx", x: 58, y: 78, width: 6, zone: "lower", muscleGroup: "Gastrocnemio", commonInjuries: ["Strappo", "Crampi"] },

  // Achilles
  { id: "achilles-r", label: "Right Achilles", labelIt: "Achille Dx", x: 42, y: 86, width: 4, zone: "lower", muscleGroup: "Tendine", commonInjuries: ["Tendinite", "Rottura"] },
  { id: "achilles-l", label: "Left Achilles", labelIt: "Achille Sx", x: 58, y: 86, width: 4, zone: "lower", muscleGroup: "Tendine", commonInjuries: ["Tendinite", "Rottura"] },
];

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

const getIntensityColor = (intensity: number): string => {
  if (intensity <= 0) return "bg-primary/30";
  if (intensity <= 2) return "bg-yellow-400";
  if (intensity <= 4) return "bg-orange-400";
  if (intensity <= 6) return "bg-orange-500";
  if (intensity <= 8) return "bg-red-500";
  return "bg-red-600";
};

const getIntensityRingColor = (intensity: number): string => {
  if (intensity <= 0) return "";
  if (intensity <= 2) return "ring-yellow-400/40";
  if (intensity <= 4) return "ring-orange-400/40";
  if (intensity <= 6) return "ring-orange-500/50";
  if (intensity <= 8) return "ring-red-500/50";
  return "ring-red-600/60";
};

const getIntensityLabel = (intensity: number): string => {
  if (intensity <= 0) return "Nessun dolore";
  if (intensity <= 2) return "Lieve";
  if (intensity <= 4) return "Moderato";
  if (intensity <= 6) return "Significativo";
  if (intensity <= 8) return "Severo";
  return "Estremo";
};

const getIntensityEmoji = (intensity: number): string => {
  if (intensity <= 0) return "😊";
  if (intensity <= 2) return "😐";
  if (intensity <= 4) return "😕";
  if (intensity <= 6) return "😣";
  if (intensity <= 8) return "😫";
  return "🔥";
};

// ============================================================================
// BODY SVG COMPONENTS
// ============================================================================

function BodySilhouetteFront({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 100" className={cn("w-full h-full", className)}>
      <defs>
        <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="currentColor" stopOpacity="0.15" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="0.25" />
        </linearGradient>
      </defs>

      {/* Head */}
      <ellipse cx="50" cy="8" rx="7" ry="8" fill="url(#bodyGradient)" className="text-muted-foreground" />

      {/* Neck */}
      <rect x="47" y="16" width="6" height="5" rx="2" fill="url(#bodyGradient)" className="text-muted-foreground" />

      {/* Shoulders & Torso */}
      <path d="M 30 22 Q 50 18 70 22 L 68 45 Q 50 48 32 45 Z" fill="url(#bodyGradient)" className="text-muted-foreground" />

      {/* Arms */}
      <path d="M 30 22 Q 22 28 20 40 Q 18 50 20 55 L 24 55 Q 26 48 28 38 Q 30 30 32 24 Z" fill="url(#bodyGradient)" className="text-muted-foreground" />
      <path d="M 70 22 Q 78 28 80 40 Q 82 50 80 55 L 76 55 Q 74 48 72 38 Q 70 30 68 24 Z" fill="url(#bodyGradient)" className="text-muted-foreground" />

      {/* Hands */}
      <ellipse cx="22" cy="57" rx="3" ry="4" fill="url(#bodyGradient)" className="text-muted-foreground" />
      <ellipse cx="78" cy="57" rx="3" ry="4" fill="url(#bodyGradient)" className="text-muted-foreground" />

      {/* Hips & Pelvis */}
      <path d="M 34 45 Q 50 48 66 45 L 64 58 Q 50 62 36 58 Z" fill="url(#bodyGradient)" className="text-muted-foreground" />

      {/* Legs */}
      <path d="M 38 58 Q 40 70 42 80 Q 43 88 42 92 L 48 92 Q 48 85 46 75 Q 45 65 48 58 Z" fill="url(#bodyGradient)" className="text-muted-foreground" />
      <path d="M 62 58 Q 60 70 58 80 Q 57 88 58 92 L 52 92 Q 52 85 54 75 Q 55 65 52 58 Z" fill="url(#bodyGradient)" className="text-muted-foreground" />

      {/* Feet */}
      <ellipse cx="45" cy="94" rx="4" ry="2" fill="url(#bodyGradient)" className="text-muted-foreground" />
      <ellipse cx="55" cy="94" rx="4" ry="2" fill="url(#bodyGradient)" className="text-muted-foreground" />
    </svg>
  );
}

function BodySilhouetteBack({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 100" className={cn("w-full h-full", className)}>
      <defs>
        <linearGradient id="bodyGradientBack" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="currentColor" stopOpacity="0.18" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="0.28" />
        </linearGradient>
      </defs>

      {/* Head */}
      <ellipse cx="50" cy="8" rx="7" ry="8" fill="url(#bodyGradientBack)" className="text-muted-foreground" />

      {/* Neck */}
      <rect x="47" y="16" width="6" height="5" rx="2" fill="url(#bodyGradientBack)" className="text-muted-foreground" />

      {/* Back & Shoulders */}
      <path d="M 30 22 Q 50 18 70 22 L 68 45 Q 50 48 32 45 Z" fill="url(#bodyGradientBack)" className="text-muted-foreground" />

      {/* Spine line (subtle) */}
      <line x1="50" y1="20" x2="50" y2="52" stroke="currentColor" strokeWidth="1" strokeOpacity="0.1" className="text-muted-foreground" />

      {/* Arms */}
      <path d="M 30 22 Q 22 28 20 40 Q 18 50 20 55 L 24 55 Q 26 48 28 38 Q 30 30 32 24 Z" fill="url(#bodyGradientBack)" className="text-muted-foreground" />
      <path d="M 70 22 Q 78 28 80 40 Q 82 50 80 55 L 76 55 Q 74 48 72 38 Q 70 30 68 24 Z" fill="url(#bodyGradientBack)" className="text-muted-foreground" />

      {/* Hands */}
      <ellipse cx="22" cy="57" rx="3" ry="4" fill="url(#bodyGradientBack)" className="text-muted-foreground" />
      <ellipse cx="78" cy="57" rx="3" ry="4" fill="url(#bodyGradientBack)" className="text-muted-foreground" />

      {/* Lower back & Glutes */}
      <path d="M 34 45 Q 50 48 66 45 L 64 60 Q 50 64 36 60 Z" fill="url(#bodyGradientBack)" className="text-muted-foreground" />

      {/* Legs */}
      <path d="M 38 60 Q 40 72 42 82 Q 43 90 42 94 L 48 94 Q 48 87 46 77 Q 45 67 48 60 Z" fill="url(#bodyGradientBack)" className="text-muted-foreground" />
      <path d="M 62 60 Q 60 72 58 82 Q 57 90 58 94 L 52 94 Q 52 87 54 77 Q 55 67 52 60 Z" fill="url(#bodyGradientBack)" className="text-muted-foreground" />

      {/* Heels */}
      <ellipse cx="45" cy="96" rx="3" ry="2" fill="url(#bodyGradientBack)" className="text-muted-foreground" />
      <ellipse cx="55" cy="96" rx="3" ry="2" fill="url(#bodyGradientBack)" className="text-muted-foreground" />
    </svg>
  );
}

// ============================================================================
// PAIN POINT COMPONENT
// ============================================================================

interface PainPointButtonProps {
  part: BodyPart;
  isSelected: boolean;
  intensity: number;
  onClick: () => void;
  onIntensityChange?: (delta: number) => void;
  readOnly: boolean;
  showIntensityControls: boolean;
}

function PainPointButton({
  part,
  isSelected,
  intensity,
  onClick,
  onIntensityChange,
  readOnly,
  showIntensityControls
}: PainPointButtonProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div
      className="absolute"
      style={{
        left: `${part.x}%`,
        top: `${part.y}%`,
        transform: "translate(-50%, -50%)",
      }}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Main Button */}
      <button
        onClick={() => {
          if (!readOnly) {
            hapticFeedback.impact("medium");
            onClick();
          }
        }}
        disabled={readOnly}
        className={cn(
          "relative rounded-full transition-all duration-300 ease-out",
          "flex items-center justify-center",
          "shadow-sm hover:shadow-md",
          isSelected
            ? cn(
              getIntensityColor(intensity),
              "ring-4",
              getIntensityRingColor(intensity),
              "scale-125",
              "animate-pulse",
              "shadow-lg"
            )
            : "bg-primary/30 hover:bg-primary/50 hover:scale-110 border-2 border-primary/40",
          readOnly ? "cursor-default" : "cursor-pointer active:scale-95",
        )}
        style={{
          width: `${part.width * 2}px`,
          height: `${part.width * 2}px`,
          minWidth: "32px",
          minHeight: "32px",
        }}
        aria-label={`${part.labelIt} - ${isSelected ? `Intensità ${intensity}` : 'Nessun dolore'}`}
      >
        {isSelected && intensity > 0 && (
          <span className="text-white text-sm font-bold drop-shadow-md">
            {intensity}
          </span>
        )}
      </button>

      {/* Intensity Controls (on hover/tap) */}
      {isSelected && showIntensityControls && !readOnly && (
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-card shadow-lg rounded-full px-1 py-0.5 border z-20">
          <button
            onClick={(e) => {
              e.stopPropagation();
              hapticFeedback.selection();
              onIntensityChange?.(-1);
            }}
            className="p-1 hover:bg-muted rounded-full transition-colors"
            disabled={intensity <= 1}
          >
            <Minus className="w-3 h-3" />
          </button>
          <span className="text-xs font-bold w-4 text-center">{intensity}</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              hapticFeedback.selection();
              onIntensityChange?.(1);
            }}
            className="p-1 hover:bg-muted rounded-full transition-colors"
            disabled={intensity >= 10}
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-30 pointer-events-none">
          <div className="bg-popover text-popover-foreground shadow-xl rounded-lg px-3 py-2 text-xs whitespace-nowrap border">
            <div className="font-bold text-sm">{part.labelIt}</div>
            <div className="text-muted-foreground">{part.muscleGroup}</div>
            {isSelected && (
              <div className={cn("font-semibold mt-1", intensity > 6 ? "text-red-500" : "text-orange-500")}>
                {getIntensityEmoji(intensity)} {getIntensityLabel(intensity)} ({intensity}/10)
              </div>
            )}
            {part.commonInjuries && part.commonInjuries.length > 0 && (
              <div className="text-muted-foreground mt-1 text-[10px]">
                Comuni: {part.commonInjuries.slice(0, 2).join(", ")}
              </div>
            )}
          </div>
          {/* Tooltip arrow */}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-popover" />
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function BodyHeatmap({
  selectedLocations,
  painPoints = [],
  onLocationToggle,
  onPainIntensityChange,
  readOnly = false,
  showIntensityControls = true,
  compact = false,
}: BodyHeatmapProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("front");
  const [activeZoneFilter, setActiveZoneFilter] = useState<string | null>(null);

  const bodyParts = viewMode === "front" ? BODY_PARTS_FRONT : BODY_PARTS_BACK;

  const normalizeKey = useCallback((value: string) => {
    return value
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[^a-z0-9]+/g, "")
      .trim();
  }, []);

  const isSelected = useCallback((locationKey: string) => {
    const key = normalizeKey(locationKey);
    return selectedLocations.some((loc) => normalizeKey(loc) === key);
  }, [normalizeKey, selectedLocations]);

  const getIntensity = useCallback((locationKey: string): number => {
    const key = normalizeKey(locationKey);
    const point = painPoints.find((p) => normalizeKey(p.location) === key);
    return point?.intensity || (isSelected(locationKey) ? 5 : 0);
  }, [isSelected, normalizeKey, painPoints]);

  const handleIntensityChange = useCallback((locationKey: string, delta: number) => {
    const currentIntensity = getIntensity(locationKey);
    const newIntensity = Math.max(1, Math.min(10, currentIntensity + delta));
    onPainIntensityChange?.(locationKey, newIntensity);
  }, [getIntensity, onPainIntensityChange]);

  // Statistics
  const stats = useMemo(() => {
    const selected = selectedLocations.length;
    const avgIntensity = painPoints.length > 0
      ? painPoints.reduce((sum, p) => sum + p.intensity, 0) / painPoints.length
      : 0;
    const maxIntensity = painPoints.length > 0
      ? Math.max(...painPoints.map(p => p.intensity))
      : 0;
    const severeCount = painPoints.filter(p => p.intensity > 6).length;

    return { selected, avgIntensity, maxIntensity, severeCount };
  }, [selectedLocations, painPoints]);

  const filteredParts = activeZoneFilter
    ? bodyParts.filter(p => p.zone === activeZoneFilter)
    : bodyParts;

  return (
    <div className={cn(
      "bg-gradient-to-b from-card to-card/95 rounded-2xl border shadow-sm select-none touch-manipulation",
      compact ? "p-3" : "p-4 sm:p-6"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary/10 rounded-lg">
            <User className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-bold text-base">Mappa Anatomica</h3>
            <p className="text-xs text-muted-foreground">
              {viewMode === "front" ? "Vista Anteriore" : "Vista Posteriore"}
            </p>
          </div>
        </div>

        {/* View Toggle */}
        <button
          onClick={() => {
            hapticFeedback.impact("light");
            setViewMode(v => v === "front" ? "back" : "front");
          }}
          className={cn(
            "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium",
            "bg-secondary hover:bg-secondary/80 transition-all",
            "active:scale-95"
          )}
        >
          <RotateCcw className="w-4 h-4" />
          <span className="hidden sm:inline">Ruota</span>
        </button>
      </div>

      {/* Zone Filters */}
      {!compact && (
        <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
          {[
            { id: null, label: "Tutto", icon: User },
            { id: "head", label: "Testa", icon: null },
            { id: "upper", label: "Superiore", icon: null },
            { id: "core", label: "Core", icon: null },
            { id: "lower", label: "Inferiore", icon: null },
          ].map(zone => (
            <button
              key={zone.id || "all"}
              onClick={() => {
                hapticFeedback.selection();
                setActiveZoneFilter(zone.id);
              }}
              className={cn(
                "px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all",
                activeZoneFilter === zone.id
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary hover:bg-secondary/80"
              )}
            >
              {zone.label}
            </button>
          ))}
        </div>
      )}

      {/* Body Map Container */}
      <div className={cn(
        "relative mx-auto",
        compact ? "w-48 aspect-[1/1.5]" : "w-48 sm:w-64 md:w-72 aspect-[1/1.5]"
      )}>
        {/* Body Silhouette */}
        {viewMode === "front" ? (
          <BodySilhouetteFront className="absolute inset-0" />
        ) : (
          <BodySilhouetteBack className="absolute inset-0" />
        )}

        {/* Pain Points */}
        {filteredParts.map(part => (
          <PainPointButton
            key={part.id}
            part={part}
            isSelected={isSelected(part.labelIt)}
            intensity={getIntensity(part.labelIt)}
            onClick={() => onLocationToggle?.(part.labelIt)}
            onIntensityChange={(delta) => handleIntensityChange(part.labelIt, delta)}
            readOnly={readOnly}
            showIntensityControls={showIntensityControls}
          />
        ))}
      </div>

      {/* Pain Scale Legend */}
      <div className="mt-4 sm:mt-6 space-y-2">
        <div className="flex items-center justify-center gap-0.5 sm:gap-1">
          {[0, 2, 4, 6, 8, 10].map((level) => (
            <div key={level} className="flex flex-col items-center">
              <div
                className={cn(
                  "w-6 h-2 rounded-sm",
                  level === 0 ? "bg-primary/20" :
                    level <= 2 ? "bg-yellow-400" :
                      level <= 4 ? "bg-orange-400" :
                        level <= 6 ? "bg-orange-500" :
                          level <= 8 ? "bg-red-500" : "bg-red-600"
                )}
              />
              <span className="text-[9px] text-muted-foreground mt-0.5">{level}</span>
            </div>
          ))}
        </div>
        <div className="flex justify-center gap-4 text-[10px] text-muted-foreground">
          <span>😊 Nessuno</span>
          <span>😐 Lieve</span>
          <span>😣 Moderato</span>
          <span>🔥 Severo</span>
        </div>
      </div>

      {/* Statistics Panel */}
      {!compact && selectedLocations.length > 0 && (
        <div className="mt-4 p-4 bg-muted/50 rounded-xl space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Info className="w-4 h-4 text-primary" />
            Riepilogo Dolore
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-card rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-primary">{stats.selected}</div>
              <div className="text-xs text-muted-foreground">Zone Attive</div>
            </div>
            <div className="bg-card rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-orange-500">{stats.avgIntensity.toFixed(1)}</div>
              <div className="text-xs text-muted-foreground">Intensità Media</div>
            </div>
          </div>

          {stats.severeCount > 0 && (
            <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-950/20 rounded-lg border border-red-200 dark:border-red-800">
              <AlertTriangle className="w-4 h-4 text-red-500" />
              <span className="text-sm text-red-700 dark:text-red-300">
                {stats.severeCount} {stats.severeCount === 1 ? 'zona con dolore severo' : 'zone con dolore severo'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Selected Locations Tags */}
      {selectedLocations.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground mb-2">
            <Flame className="w-3.5 h-3.5" />
            Zone Selezionate ({selectedLocations.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedLocations.map((location, index) => {
              const intensity = painPoints.find(p => p.location === location)?.intensity || 5;
              return (
                <span
                  key={index}
                  className={cn(
                    "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-all",
                    intensity > 6
                      ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800"
                      : "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border border-orange-200 dark:border-orange-800"
                  )}
                >
                  <span className="text-[10px]">{getIntensityEmoji(intensity)}</span>
                  {location}
                  {!readOnly && onLocationToggle && (
                    <button
                      onClick={() => {
                        hapticFeedback.selection();
                        onLocationToggle(location);
                      }}
                      className="ml-0.5 hover:text-red-500 transition-colors"
                    >
                      ×
                    </button>
                  )}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty State */}
      {selectedLocations.length === 0 && !readOnly && (
        <div className="mt-4 p-4 bg-muted/30 rounded-xl text-center">
          <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
          <p className="text-sm font-medium text-muted-foreground">
            Nessun dolore segnalato
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Tocca le zone del corpo per segnalare eventuali fastidi
          </p>
        </div>
      )}
    </div>
  );
}
