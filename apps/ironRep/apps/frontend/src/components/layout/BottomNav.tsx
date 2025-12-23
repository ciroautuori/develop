import { useEffect, useState } from "react";
import { Link, useLocation } from "@tanstack/react-router";
import { cn } from "../../lib/utils";
import { navigationItems, type NavigationItem } from "../../lib/navigation";
import { touchTarget } from "../../lib/touch-targets";

interface BottomNavProps {}

export function BottomNav({}: BottomNavProps) {
  const location = useLocation();
  const currentPath = location.pathname;
  const [badges, setBadges] = useState<Record<string, string | null>>({});

  const bottomNavItems = navigationItems.filter((item) => item.mobileLocation === "bottom");

  useEffect(() => {
    async function loadBadges() {
      const newBadges: Record<string, string | null> = {};
      for (const item of bottomNavItems) {
        if ("getBadge" in item && item.getBadge) {
          try {
            newBadges[item.id] = await item.getBadge();
          } catch {
            newBadges[item.id] = null;
          }
        }
      }
      setBadges(newBadges);
    }
    loadBadges();
    const interval = setInterval(loadBadges, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const isActive = (item: NavigationItem) => {
    if (!item.to) return false;
    return item.to === "/" ? currentPath === "/" : currentPath.startsWith(item.to);
  };

  return (
    <nav className="fixed inset-x-0 bottom-0 w-full bg-background/98 backdrop-blur-xl border-t border-border/30 z-50 lg:hidden">
      <div className="flex w-full justify-around items-center h-16 px-2 pb-[env(safe-area-inset-bottom)]">
        {bottomNavItems.map((item) => {
          if (item.isMain && item.to) {
            return (
              <div key={item.id} className="-mt-6">
                <NavItem
                  to={item.to}
                  icon={<item.icon size={28} />}
                  label={item.label}
                  isActive={isActive(item)}
                  isMain={true}
                  badge={badges[item.id]}
                  color={item.color}
                />
              </div>
            );
          } else if (item.to) {
            return (
              <NavItem
                key={item.id}
                to={item.to}
                icon={<item.icon size={22} />}
                label={item.label}
                isActive={isActive(item)}
                badge={badges[item.id]}
                color={item.color}
              />
            );
          }
          return null;
        })}
      </div>
    </nav>
  );
}

function NavItem({
  to,
  icon,
  label,
  isActive,
  isMain = false,
  badge,
  color,
}: {
  to: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  isMain?: boolean;
  badge?: string | null;
  color?: string;
}) {
  const handleClick = () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  };

  if (isMain) {
    return (
      <Link
        to={to}
        onClick={handleClick}
        className={cn(
          "flex flex-col items-center justify-center",
          "min-h-14 min-w-14 p-3 rounded-2xl",
          touchTarget.manipulation,
          touchTarget.active,
          "transition-all duration-200",
          isActive
            ? "bg-primary text-primary-foreground shadow-lg scale-105"
            : "bg-card text-muted-foreground shadow-md hover:bg-muted",
          "relative"
        )}
      >
        <div className={cn("flex items-center justify-center", isActive && "scale-110")}>
          {icon}
        </div>
        <span className={cn(
          "text-xs font-medium mt-1 text-center leading-tight",
          isActive && "font-bold"
        )}>
          {label}
        </span>
        {badge && (
          <div className="absolute -top-1 -right-1 bg-destructive text-destructive-foreground text-xs font-bold rounded-full min-w-5 h-5 flex items-center justify-center px-1.5 shadow-md animate-pulse">
            {badge}
          </div>
        )}
      </Link>
    );
  }

  return (
    <Link
      to={to}
      onClick={handleClick}
      className={cn(
        "flex flex-col items-center justify-center gap-1",
        touchTarget.button.sm,
        touchTarget.manipulation,
        touchTarget.active,
        "rounded-xl transition-all duration-200",
        isActive
          ? cn("text-primary", color)
          : "text-muted-foreground hover:text-foreground",
        "relative"
      )}
    >
      <div className={cn(
        "flex items-center justify-center transition-transform duration-200",
        isActive && "scale-110"
      )}>
        {icon}
      </div>
      <span className={cn(
        "text-[10px] font-medium text-center leading-tight max-w-[4rem] truncate",
        isActive && "font-bold"
      )}>
        {label}
      </span>
      {badge && (
        <div className="absolute -top-0.5 -right-0.5 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full min-w-4 h-4 flex items-center justify-center px-1 shadow-md animate-pulse">
          {badge}
        </div>
      )}
    </Link>
  );
}
