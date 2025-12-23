import type React from "react";
import { Link, useLocation } from "@tanstack/react-router";
import { X, ChevronRight } from "lucide-react";
import { cn } from "../../lib/utils";
import { navigationItems } from "../../lib/navigation";
import { touchTarget } from "../../lib/touch-targets";

interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileDrawer({ isOpen, onClose }: MobileDrawerProps) {
  const location = useLocation();

  const drawerItems = navigationItems.filter((item) => item.mobileLocation === "drawer");
  const MAX_DRAWER_ITEMS = 6;
  const visibleDrawerItems = drawerItems.slice(0, MAX_DRAWER_ITEMS);
  const isTruncated = drawerItems.length > MAX_DRAWER_ITEMS;

  const handleLinkClick = () => {
    if (navigator.vibrate) navigator.vibrate(15);
    onClose();
  };

  const handleClose = () => {
    if (navigator.vibrate) navigator.vibrate(10);
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className={cn(
          "fixed inset-0 bg-background/80 backdrop-blur-sm z-50 lg:hidden transition-opacity duration-300",
          isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={handleClose}
      />

      {/* Drawer */}
      <div
        className={cn(
          "fixed right-0 top-0 bottom-0 w-80 max-w-[85vw] bg-card border-l border-border z-50 lg:hidden transition-transform duration-300 ease-out shadow-2xl safe-all",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-border bg-background/50 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <span className="font-bold text-primary text-xl">iR</span>
            </div>
            <div>
              <h2 className="font-bold text-lg leading-none">Menu</h2>
              <p className="text-xs text-muted-foreground">ironRep App</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className={cn(
              touchTarget.icon.md,
              "rounded-full hover:bg-accent active:bg-accent/80 transition-colors"
            )}
            aria-label="Close menu"
          >
            <X size={24} />
          </button>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 p-4 space-y-2 overflow-hidden">
          {isTruncated && (
            <div className="text-[11px] text-muted-foreground/70 bg-secondary/40 border border-border/40 rounded-xl px-3 py-2">
              Menu lungo: mostro le prime {MAX_DRAWER_ITEMS} voci (NO SCROLL attivo).
            </div>
          )}

          {visibleDrawerItems.map((item) => (
              <DrawerNavItem
                key={item.id}
                to={item.to!}
                icon={<item.icon size={24} />}
                label={item.label}
                description={item.description || ""}
                isActive={
                  item.to === "/"
                    ? location.pathname === "/"
                    : location.pathname.startsWith(item.to!)
                }
                onClick={handleLinkClick}
              />
            ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-border bg-muted/30">
          <p className="text-xs text-center text-muted-foreground">
            ironRep v1.0 • Medical Trainer
          </p>
        </div>
      </div>
    </>
  );
}

interface DrawerNavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  description: string;
  isActive: boolean;
  onClick: () => void;
}

function DrawerNavItem({
  to,
  icon,
  label,
  description,
  isActive,
  onClick,
}: DrawerNavItemProps) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className={cn(
        "flex items-center justify-between p-4 rounded-xl transition-all duration-200",
        touchTarget.manipulation,
        touchTarget.active,
        isActive
          ? "bg-primary/10 text-primary border border-primary/20 shadow-sm"
          : "hover:bg-accent text-foreground active:bg-accent/80"
      )}
    >
      <div className="flex items-center gap-4">
        <div
          className={cn(
            "p-2.5 rounded-lg transition-colors",
            isActive ? "bg-primary/20" : "bg-muted"
          )}
        >
          {icon}
        </div>
        <div className="flex flex-col">
          <span className="font-semibold text-base leading-tight">{label}</span>
          {description && (
            <span className="text-xs text-muted-foreground mt-0.5">{description}</span>
          )}
        </div>
      </div>
      <ChevronRight
        size={20}
        className={cn(
          "transition-transform flex-shrink-0",
          isActive && "translate-x-1"
        )}
      />
    </Link>
  );
}
