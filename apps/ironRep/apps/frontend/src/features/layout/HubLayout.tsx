import { useEffect, useRef, useState } from "react";
import { TabButton } from "./TabButton";
import type { HubLayoutProps } from "./types";

/**
 * HubLayout - Mobile-first layout for hub pages
 *
 * Usage: 70% mobile, 28% tablet, 2% desktop
 * - Full height on mobile (100dvh)
 * - Sticky tabs with horizontal scroll
 * - Safe area handling for notch devices
 */
export function HubLayout({ tabs, defaultTab }: HubLayoutProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id || "");
  const lastAppliedDefaultTabRef = useRef<string | undefined>(undefined);

  useEffect(() => {
    if (!defaultTab) return;
    if (!tabs.some((t) => t.id === defaultTab)) return;
    if (lastAppliedDefaultTabRef.current === defaultTab) return;

    lastAppliedDefaultTabRef.current = defaultTab;
    setActiveTab(defaultTab);
  }, [defaultTab, tabs]);

  const ActiveComponent = tabs.find((t) => t.id === activeTab)?.component;

  return (
    <div className="flex flex-col bg-background">
      {/* Sticky Tab Navigation - always visible */}
      <div className="sticky top-0 z-20 bg-background/95 backdrop-blur-sm border-b safe-area-top">
        <nav
          className="flex overflow-x-auto no-scrollbar"
          role="tablist"
          aria-label="Sezioni"
        >
          {tabs.map((tab) => (
            <TabButton
              key={tab.id}
              active={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
              icon={tab.icon}
              label={tab.label}
            />
          ))}
        </nav>
      </div>

      <main role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
        {ActiveComponent && <ActiveComponent />}
      </main>
    </div>
  );
}
