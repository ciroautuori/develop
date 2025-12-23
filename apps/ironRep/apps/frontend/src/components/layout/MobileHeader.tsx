import { Bell, User } from "lucide-react";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import { Link } from "@tanstack/react-router";
import { touchTarget } from "../../lib/touch-targets";
import { cn } from "../../lib/utils";

export function MobileHeader() {
  const today = new Date();

  const handleNotificationClick = () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  };

  return (
    <header className="lg:hidden h-16 flex items-center justify-between px-4 bg-background/95 backdrop-blur-md sticky top-0 z-40 safe-area-top shadow-sm transition-all duration-200">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
          <span className="font-bold text-primary text-xl">iR</span>
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-base leading-tight">ironRep</span>
          <span className="text-xs text-muted-foreground capitalize">
            {format(today, "EEEE d MMMM", { locale: it })}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={handleNotificationClick}
          className={cn(
            touchTarget.icon.md,
            "rounded-full hover:bg-accent active:bg-accent/80 transition-colors relative"
          )}
          aria-label="Notifiche"
        >
          <Bell size={22} strokeWidth={2} />
          {/* Notification dot */}
          <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-background animate-pulse"></span>
        </button>

        <Link
          to="/profile"
          className={cn(
            touchTarget.icon.md,
            "bg-secondary rounded-full flex items-center justify-center overflow-hidden border border-border hover:bg-accent transition-colors"
          )}
          aria-label="Profilo"
        >
          <User size={20} className="text-muted-foreground" />
        </Link>
      </div>
    </header>
  );
}
