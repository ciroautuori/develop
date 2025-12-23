import { useState, useEffect, useCallback, useRef } from "react";
import { cn } from "../../lib/utils";
import { hapticFeedback } from "../../lib/haptics";
import {
  Play,
  Pause,
  RotateCcw,
  Maximize2,
  Minimize2,
  Volume2,
  VolumeX,
  Clock,
  Flame,
  Zap,
  Timer,
  Settings,
  ChevronUp,
  ChevronDown,
  Trophy,
  X,
} from "lucide-react";

// ============================================================================
// TYPES
// ============================================================================

type TimerMode = "amrap" | "emom" | "fortime" | "tabata" | "custom";

interface TimerConfig {
  mode: TimerMode;
  totalSeconds: number;
  workSeconds?: number;
  restSeconds?: number;
  rounds?: number;
  intervals?: number;
  countUp?: boolean;
}

interface TimerState {
  isRunning: boolean;
  isPaused: boolean;
  currentSeconds: number;
  currentRound: number;
  currentInterval: number;
  isWorkPhase: boolean;
  completedRounds: number;
}

// ============================================================================
// PRESETS
// ============================================================================

const TIMER_PRESETS: Record<TimerMode, { label: string; icon: typeof Clock; color: string; description: string }> = {
  amrap: {
    label: "AMRAP",
    icon: Flame,
    color: "from-orange-500 to-red-600",
    description: "As Many Rounds As Possible",
  },
  emom: {
    label: "EMOM",
    icon: Clock,
    color: "from-blue-500 to-indigo-600",
    description: "Every Minute On the Minute",
  },
  fortime: {
    label: "For Time",
    icon: Zap,
    color: "from-green-500 to-emerald-600",
    description: "Complete ASAP with cap",
  },
  tabata: {
    label: "Tabata",
    icon: Timer,
    color: "from-purple-500 to-pink-600",
    description: "20s Work / 10s Rest × 8",
  },
  custom: {
    label: "Custom",
    icon: Settings,
    color: "from-gray-500 to-slate-600",
    description: "Custom intervals",
  },
};

const DEFAULT_CONFIGS: Record<TimerMode, TimerConfig> = {
  amrap: { mode: "amrap", totalSeconds: 12 * 60, countUp: false },
  emom: { mode: "emom", totalSeconds: 10 * 60, intervals: 10 },
  fortime: { mode: "fortime", totalSeconds: 20 * 60, countUp: true },
  tabata: { mode: "tabata", totalSeconds: 4 * 60, workSeconds: 20, restSeconds: 10, rounds: 8 },
  custom: { mode: "custom", totalSeconds: 5 * 60, workSeconds: 40, restSeconds: 20, rounds: 5 },
};

// ============================================================================
// AUDIO UTILS
// ============================================================================

const playBeep = (frequency: number = 800, duration: number = 200) => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = frequency;
    oscillator.type = "sine";

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration / 1000);
  } catch (e) {
    console.warn("Audio not available");
  }
};

const playCountdown = () => {
  playBeep(600, 150);
};

const playGo = () => {
  playBeep(1000, 300);
  setTimeout(() => playBeep(1000, 300), 150);
};

const playRoundComplete = () => {
  playBeep(800, 200);
};

const playFinish = () => {
  [0, 200, 400].forEach((delay) => {
    setTimeout(() => playBeep(1200, 250), delay);
  });
};

// ============================================================================
// FORMAT UTILS
// ============================================================================

const formatTime = (seconds: number): string => {
  const mins = Math.floor(Math.abs(seconds) / 60);
  const secs = Math.abs(seconds) % 60;
  const sign = seconds < 0 ? "-" : "";
  return `${sign}${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
};

const formatTimeWithMs = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
};

// ============================================================================
// NUMBER INPUT COMPONENT
// ============================================================================

interface NumberInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  label: string;
  unit?: string;
}

function NumberInput({ value, onChange, min = 0, max = 999, step = 1, label, unit }: NumberInputProps) {
  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-xs text-muted-foreground font-medium">{label}</span>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onChange(Math.max(min, value - step))}
          className="p-1.5 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95 transition-all"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
        <div className="w-16 text-center font-mono text-xl font-bold">
          {value}
          {unit && <span className="text-xs text-muted-foreground ml-0.5">{unit}</span>}
        </div>
        <button
          onClick={() => onChange(Math.min(max, value + step))}
          className="p-1.5 rounded-lg bg-secondary hover:bg-secondary/80 active:scale-95 transition-all"
        >
          <ChevronUp className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

interface CrossFitTimerProps {
  onComplete?: (mode: TimerMode, duration: number, rounds: number) => void;
  initialMode?: TimerMode;
  compact?: boolean;
}

export function CrossFitTimer({ onComplete, initialMode = "amrap", compact = false }: CrossFitTimerProps) {
  // Config state
  const [mode, setMode] = useState<TimerMode>(initialMode);
  const [config, setConfig] = useState<TimerConfig>(DEFAULT_CONFIGS[initialMode]);
  const [showSettings, setShowSettings] = useState(true);

  // Timer state
  const [state, setState] = useState<TimerState>({
    isRunning: false,
    isPaused: false,
    currentSeconds: 0,
    currentRound: 1,
    currentInterval: 1,
    isWorkPhase: true,
    completedRounds: 0,
  });

  // UI state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showCompleteModal, setShowCompleteModal] = useState(false);

  // Refs
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const startTimeRef = useRef<number>(0);

  // ============================================================================
  // TIMER LOGIC
  // ============================================================================

  const resetTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setState({
      isRunning: false,
      isPaused: false,
      currentSeconds: config.countUp ? 0 : config.totalSeconds,
      currentRound: 1,
      currentInterval: 1,
      isWorkPhase: true,
      completedRounds: 0,
    });
    setShowSettings(true);
    hapticFeedback.impact("medium");
  }, [config]);

  const startTimer = useCallback(() => {
    if (state.isRunning && !state.isPaused) return;

    setShowSettings(false);
    startTimeRef.current = Date.now();

    if (soundEnabled) {
      // Countdown 3-2-1-GO
      playCountdown();
      setTimeout(playCountdown, 1000);
      setTimeout(playCountdown, 2000);
      setTimeout(playGo, 3000);
    }

    // Start after countdown
    setTimeout(() => {
      setState((prev) => ({ ...prev, isRunning: true, isPaused: false }));
      hapticFeedback.notification("success");
    }, 3000);
  }, [state.isRunning, state.isPaused, soundEnabled]);

  const pauseTimer = useCallback(() => {
    setState((prev) => ({ ...prev, isPaused: true }));
    hapticFeedback.impact("light");
  }, []);

  const resumeTimer = useCallback(() => {
    setState((prev) => ({ ...prev, isPaused: false }));
    hapticFeedback.impact("light");
  }, []);

  const completeRound = useCallback(() => {
    setState((prev) => ({
      ...prev,
      completedRounds: prev.completedRounds + 1,
      currentRound: prev.currentRound + 1,
    }));
    if (soundEnabled) playRoundComplete();
    hapticFeedback.notification("success");
  }, [soundEnabled]);

  const finishTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setState((prev) => ({ ...prev, isRunning: false, isPaused: false }));

    if (soundEnabled) playFinish();
    hapticFeedback.notification("success");
    setShowCompleteModal(true);

    const duration = Math.floor((Date.now() - startTimeRef.current) / 1000);
    onComplete?.(mode, duration, state.completedRounds);
  }, [soundEnabled, mode, state.completedRounds, onComplete]);

  // Main timer effect
  useEffect(() => {
    if (!state.isRunning || state.isPaused) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = setInterval(() => {
      setState((prev) => {
        let newSeconds = prev.currentSeconds;
        let newRound = prev.currentRound;
        let newInterval = prev.currentInterval;
        let newIsWork = prev.isWorkPhase;
        let finished = false;

        // Update seconds based on mode
        if (config.countUp) {
          newSeconds = prev.currentSeconds + 1;
          if (newSeconds >= config.totalSeconds) {
            finished = true;
          }
        } else {
          newSeconds = prev.currentSeconds - 1;
          if (newSeconds <= 0) {
            finished = true;
          }
        }

        // Handle interval-based modes (EMOM, Tabata, Custom)
        if (mode === "emom") {
          const intervalDuration = 60; // 1 minute per interval
          const elapsed = config.countUp ? newSeconds : config.totalSeconds - newSeconds;
          newInterval = Math.floor(elapsed / intervalDuration) + 1;

          if (newInterval !== prev.currentInterval && soundEnabled) {
            playRoundComplete();
            hapticFeedback.impact("medium");
          }
        }

        if (mode === "tabata" || mode === "custom") {
          const workTime = config.workSeconds || 20;
          const restTime = config.restSeconds || 10;
          const cycleTime = workTime + restTime;
          const elapsed = config.countUp ? newSeconds : config.totalSeconds - newSeconds;
          const currentCycleTime = elapsed % cycleTime;

          newIsWork = currentCycleTime < workTime;
          newRound = Math.floor(elapsed / cycleTime) + 1;

          // Beep on phase change
          if (newIsWork !== prev.isWorkPhase && soundEnabled) {
            if (newIsWork) playGo();
            else playRoundComplete();
            hapticFeedback.impact("medium");
          }
        }

        // Countdown beeps in last 3 seconds
        if (!config.countUp && newSeconds <= 3 && newSeconds > 0 && soundEnabled) {
          playCountdown();
        }

        if (finished) {
          return prev; // Will be handled by finishTimer
        }

        return {
          ...prev,
          currentSeconds: newSeconds,
          currentRound: newRound,
          currentInterval: newInterval,
          isWorkPhase: newIsWork,
        };
      });
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [state.isRunning, state.isPaused, config, mode, soundEnabled]);

  // Check for finish
  useEffect(() => {
    if (!state.isRunning) return;

    const isFinished = config.countUp
      ? state.currentSeconds >= config.totalSeconds
      : state.currentSeconds <= 0;

    if (isFinished) {
      finishTimer();
    }
  }, [state.currentSeconds, state.isRunning, config, finishTimer]);

  // Fullscreen handler
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
    hapticFeedback.selection();
  }, []);

  // Mode change handler
  const handleModeChange = (newMode: TimerMode) => {
    setMode(newMode);
    setConfig(DEFAULT_CONFIGS[newMode]);
    resetTimer();
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  const preset = TIMER_PRESETS[mode];
  const PresetIcon = preset.icon;

  const progress = config.countUp
    ? (state.currentSeconds / config.totalSeconds) * 100
    : ((config.totalSeconds - state.currentSeconds) / config.totalSeconds) * 100;

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative overflow-hidden rounded-2xl transition-all duration-300",
        isFullscreen
          ? "fixed inset-0 z-50 rounded-none bg-black"
          : "bg-gradient-to-br from-card to-card/95 border shadow-xl",
        compact ? "p-4" : "p-6"
      )}
    >
      {/* Background Gradient */}
      <div
        className={cn(
          "absolute inset-0 opacity-10 bg-gradient-to-br",
          preset.color
        )}
      />

      {/* Header */}
      <div className="relative flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn("p-2.5 rounded-xl bg-gradient-to-br", preset.color)}>
            <PresetIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-lg">{preset.label}</h3>
            <p className="text-xs text-muted-foreground">{preset.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
          >
            {soundEnabled ? (
              <Volume2 className="w-5 h-5" />
            ) : (
              <VolumeX className="w-5 h-5 text-muted-foreground" />
            )}
          </button>
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
          >
            {isFullscreen ? (
              <Minimize2 className="w-5 h-5" />
            ) : (
              <Maximize2 className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Mode Selector */}
      {showSettings && (
        <div className="relative flex gap-2 mb-6 overflow-x-auto pb-2">
          {(Object.keys(TIMER_PRESETS) as TimerMode[]).map((m) => {
            const p = TIMER_PRESETS[m];
            const Icon = p.icon;
            return (
              <button
                key={m}
                onClick={() => handleModeChange(m)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all",
                  mode === m
                    ? cn("bg-gradient-to-r text-white", p.color)
                    : "bg-secondary hover:bg-secondary/80"
                )}
              >
                <Icon className="w-4 h-4" />
                {p.label}
              </button>
            );
          })}
        </div>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <div className="relative bg-secondary/50 rounded-xl p-4 mb-6">
          <div className="flex flex-wrap justify-center gap-6">
            <NumberInput
              label="Minuti"
              value={Math.floor(config.totalSeconds / 60)}
              onChange={(v) => setConfig((c) => ({ ...c, totalSeconds: v * 60 + (c.totalSeconds % 60) }))}
              min={1}
              max={60}
            />

            {(mode === "tabata" || mode === "custom") && (
              <>
                <NumberInput
                  label="Work"
                  value={config.workSeconds || 20}
                  onChange={(v) => setConfig((c) => ({ ...c, workSeconds: v }))}
                  min={5}
                  max={120}
                  unit="s"
                />
                <NumberInput
                  label="Rest"
                  value={config.restSeconds || 10}
                  onChange={(v) => setConfig((c) => ({ ...c, restSeconds: v }))}
                  min={5}
                  max={120}
                  unit="s"
                />
              </>
            )}

            {mode === "emom" && (
              <NumberInput
                label="Intervals"
                value={config.intervals || 10}
                onChange={(v) => setConfig((c) => ({ ...c, intervals: v, totalSeconds: v * 60 }))}
                min={1}
                max={30}
              />
            )}
          </div>
        </div>
      )}

      {/* Timer Display */}
      <div className="relative text-center py-8">
        {/* Progress Ring */}
        <div className="relative w-64 h-64 mx-auto mb-6">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="128"
              cy="128"
              r="120"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-secondary"
            />
            <circle
              cx="128"
              cy="128"
              r="120"
              stroke="url(#timerGradient)"
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={2 * Math.PI * 120}
              strokeDashoffset={2 * Math.PI * 120 * (1 - progress / 100)}
              className="transition-all duration-200"
            />
            <defs>
              <linearGradient id="timerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={mode === "amrap" ? "#f97316" : mode === "emom" ? "#3b82f6" : mode === "fortime" ? "#22c55e" : mode === "tabata" ? "#a855f7" : "#6b7280"} />
                <stop offset="100%" stopColor={mode === "amrap" ? "#dc2626" : mode === "emom" ? "#4f46e5" : mode === "fortime" ? "#10b981" : mode === "tabata" ? "#ec4899" : "#475569"} />
              </linearGradient>
            </defs>
          </svg>

          {/* Center Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={cn(
              "font-mono font-bold transition-all",
              isFullscreen ? "text-8xl" : "text-6xl",
              !state.isWorkPhase && (mode === "tabata" || mode === "custom") && "text-green-500"
            )}>
              {formatTime(state.currentSeconds)}
            </div>

            {(mode === "tabata" || mode === "custom") && state.isRunning && (
              <div className={cn(
                "text-2xl font-bold mt-2 uppercase tracking-wider",
                state.isWorkPhase ? "text-red-500" : "text-green-500"
              )}>
                {state.isWorkPhase ? "WORK" : "REST"}
              </div>
            )}

            {mode === "emom" && state.isRunning && (
              <div className="text-xl font-bold mt-2 text-blue-500">
                Interval {state.currentInterval} / {config.intervals || 10}
              </div>
            )}
          </div>
        </div>

        {/* Rounds Counter (AMRAP) */}
        {mode === "amrap" && (
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="bg-secondary/50 rounded-xl px-6 py-3">
              <div className="text-3xl font-bold text-orange-500">{state.completedRounds}</div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider">Rounds</div>
            </div>
            {state.isRunning && !state.isPaused && (
              <button
                onClick={completeRound}
                className={cn(
                  "px-6 py-4 rounded-xl font-bold text-white transition-all active:scale-95",
                  "bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700",
                  "shadow-lg shadow-orange-500/25"
                )}
              >
                <Trophy className="w-5 h-5 inline mr-2" />
                +1 Round
              </button>
            )}
          </div>
        )}

        {/* For Time Display */}
        {mode === "fortime" && state.isRunning && (
          <div className="text-lg text-muted-foreground mb-4">
            Cap: {formatTimeWithMs(config.totalSeconds)}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="relative flex items-center justify-center gap-4">
        {!state.isRunning ? (
          <button
            onClick={startTimer}
            className={cn(
              "flex items-center gap-3 px-8 py-4 rounded-2xl font-bold text-lg text-white transition-all active:scale-95",
              "bg-gradient-to-r shadow-xl",
              preset.color,
              "hover:shadow-2xl hover:scale-105"
            )}
          >
            <Play className="w-6 h-6 fill-current" />
            START
          </button>
        ) : (
          <>
            {state.isPaused ? (
              <button
                onClick={resumeTimer}
                className="flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-white bg-green-500 hover:bg-green-600 transition-all active:scale-95"
              >
                <Play className="w-5 h-5 fill-current" />
                Resume
              </button>
            ) : (
              <button
                onClick={pauseTimer}
                className="flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-white bg-yellow-500 hover:bg-yellow-600 transition-all active:scale-95"
              >
                <Pause className="w-5 h-5" />
                Pause
              </button>
            )}
            <button
              onClick={resetTimer}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-bold bg-secondary hover:bg-secondary/80 transition-all active:scale-95"
            >
              <RotateCcw className="w-5 h-5" />
              Reset
            </button>
          </>
        )}
      </div>

      {/* Complete Modal */}
      {showCompleteModal && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm z-50">
          <div className="bg-card rounded-2xl p-8 max-w-sm mx-4 text-center shadow-2xl border">
            <div className={cn("w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center bg-gradient-to-br", preset.color)}>
              <Trophy className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold mb-2">Workout Complete! 🎉</h3>
            <p className="text-muted-foreground mb-4">
              {mode === "amrap" && `${state.completedRounds} rounds completed`}
              {mode === "emom" && `${config.intervals} intervals completed`}
              {mode === "fortime" && `Finished in ${formatTime(state.currentSeconds)}`}
              {(mode === "tabata" || mode === "custom") && `${config.rounds} rounds completed`}
            </p>
            <button
              onClick={() => {
                setShowCompleteModal(false);
                resetTimer();
              }}
              className="w-full py-3 rounded-xl font-bold bg-primary text-primary-foreground hover:bg-primary/90 transition-all"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
