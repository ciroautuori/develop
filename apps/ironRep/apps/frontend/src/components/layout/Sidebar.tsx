import type React from "react";
import { useState } from "react";
import { Link, useLocation } from "@tanstack/react-router";
import { Menu } from "lucide-react";
import { cn } from "../../lib/utils";
import { navigationItems } from "../../lib/navigation";
import { touchTarget } from "../../lib/touch-targets";

export function Sidebar() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleToggle = () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(5);
    }
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <aside
      className={cn(
        "bg-card border-r border-border transition-all duration-300 ease-in-out flex-col hidden lg:flex h-full",
        isSidebarOpen ? "w-64" : "w-16"
      )}
    >
      <div className="p-4 flex items-center justify-between border-b border-border h-16">
        {isSidebarOpen && (
          <span className="font-bold text-xl text-primary">ironRep</span>
        )}
        <button
          onClick={handleToggle}
          className={cn(
            touchTarget.icon.md,
            "rounded-lg hover:bg-accent hover:text-accent-foreground transition-colors"
          )}
          aria-label="Toggle Sidebar"
        >
          <Menu size={22} />
        </button>
      </div>

      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {navigationItems
          .filter((item) => item.desktopLocation === "sidebar")
          .map((item) => (
            <NavItem
              key={item.id}
              to={item.to!}
              icon={<item.icon size={22} />}
              label={item.label}
              isOpen={isSidebarOpen}
            />
          ))}
      </nav>
    </aside>
  );
}

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  isOpen: boolean;
}

function NavItem({ to, icon, label, isOpen }: NavItemProps) {
  const location = useLocation();
  const isActive =
    location.pathname === to ||
    (to !== "/" && location.pathname.startsWith(to));

  const handleClick = () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  };

  return (
    <Link
      to={to}
      onClick={handleClick}
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg transition-all duration-200",
        touchTarget.button.sm,
        touchTarget.manipulation,
        isActive
          ? "bg-primary/10 text-primary font-semibold shadow-sm"
          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
      )}
    >
      <div className="flex-shrink-0">{icon}</div>
      {isOpen && (
        <span className="whitespace-nowrap overflow-hidden text-ellipsis text-base">
          {label}
        </span>
      )}
    </Link>
  );
}
