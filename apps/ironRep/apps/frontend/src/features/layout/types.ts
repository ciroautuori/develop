import type React from "react";

export interface TabConfig {
  id: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  component: React.ComponentType;
}

export interface HubLayoutProps {
  tabs: TabConfig[];
  defaultTab?: string;
  headerConfig?: {
    title?: string;
    subtitle?: string;
    actions?: React.ReactNode;
  };
}

export interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
}
