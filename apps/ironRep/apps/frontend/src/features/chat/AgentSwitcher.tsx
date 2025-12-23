/**
 * AgentSwitcher - Swipeable Tabs Component
 *
 * iOS-inspired segmented control for switching between AI agents.
 * Features:
 * - Swipeable horizontal scroll with snap points
 * - Animated indicator slide
 * - Haptic feedback on switch
 * - Active state visual feedback
 * - Keyboard accessible
 *
 * @example
 * ```tsx
 * <AgentSwitcher
 *   agents={agents}
 *   activeAgent={currentAgent}
 *   onSwitch={(agent) => setCurrentAgent(agent)}
 * />
 * ```
 */

import * as React from "react";
import { motion } from "framer-motion";
import { cn } from "../../../lib/utils";
import { hapticFeedback } from "../../../lib/haptics";
import type { AgentInfo, ChatMode } from "../types";

export interface AgentSwitcherProps {
  agents: AgentInfo[];
  activeAgent: ChatMode;
  onSwitch: (agent: ChatMode) => void;
  className?: string;
}

export function AgentSwitcher({
  agents,
  activeAgent,
  onSwitch,
  className,
}: AgentSwitcherProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const activeIndex = agents.findIndex((a) => a.id === activeAgent);

  const handleSwitch = (agentId: ChatMode) => {
    if (agentId === activeAgent) return;

    hapticFeedback.impact('medium');
    onSwitch(agentId);

    // Scroll active tab into view
    const container = containerRef.current;
    if (!container) return;

    const activeTab = container.querySelector<HTMLButtonElement>(
      `[data-agent="${agentId}"]`
    );
    if (activeTab) {
      const left =
        activeTab.offsetLeft - (container.clientWidth - activeTab.clientWidth) / 2;
      container.scrollTo({ left, behavior: "smooth" });
    }
  };

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative flex items-center gap-1 bg-secondary/50 p-1 rounded-xl overflow-x-auto no-scrollbar snap-x snap-mandatory",
        className
      )}
      role="tablist"
      aria-label="Seleziona agente AI"
    >
      {/* Active indicator background */}
      <motion.div
        className="absolute h-[calc(100%-8px)] bg-background rounded-lg shadow-sm border border-border/50"
        initial={false}
        animate={{
          x: `calc(${activeIndex * 100}% + ${activeIndex * 4}px + 4px)`,
          width: `calc(${100 / agents.length}% - 8px)`,
        }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        aria-hidden="true"
      />

      {/* Agent tabs */}
      {agents.map((agent) => {
        const isActive = agent.id === activeAgent;

        return (
          <button
            key={agent.id}
            data-agent={agent.id}
            onClick={() => handleSwitch(agent.id)}
            className={cn(
              "relative z-10 flex-1 min-w-[100px] px-4 py-2.5 rounded-lg text-sm font-medium transition-colors snap-center touch-manipulation",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
              isActive
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground"
            )}
            role="tab"
            aria-selected={isActive}
            aria-controls={`agent-panel-${agent.id}`}
            tabIndex={isActive ? 0 : -1}
          >
            <span className="flex items-center justify-center gap-2">
              <span
                className={cn(
                  "transition-transform",
                  isActive && "scale-110"
                )}
                aria-hidden="true"
              >
                {agent.icon}
              </span>
              <span className="truncate">{agent.name}</span>
            </span>
          </button>
        );
      })}
    </div>
  );
}

export default AgentSwitcher;
