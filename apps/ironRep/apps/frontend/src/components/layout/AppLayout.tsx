import { useState } from "react";
import { Sidebar } from "./Sidebar";
import { BottomNav } from "./BottomNav";
import { MobileDrawer } from "./MobileDrawer";
import { PWAInstallBanner } from "../ui/PWAInstallBanner";
import { OfflineIndicator } from "../ui/OfflineIndicator";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  return (
    <div className="flex h-[100dvh] min-h-[100dvh] w-full bg-background text-foreground overflow-hidden">
      {/* Desktop Sidebar (Hidden on Mobile) */}
      <Sidebar />

      <div className="flex flex-col flex-1 h-full overflow-hidden relative">
        {/* Main Content Area */}
        <main className="flex-1 min-h-0 overflow-y-auto overscroll-contain">
          <div className="w-full min-h-full max-w-full px-3 xs:px-4 sm:px-6 md:max-w-3xl lg:max-w-5xl md:mx-auto pb-[calc(5rem+env(safe-area-inset-bottom))] lg:pb-6 safe-area-left safe-area-right">
            {children}
          </div>
        </main>

        {/* Mobile Bottom Nav (Hidden on Desktop) */}
        <BottomNav />

        {/* Mobile Drawer Menu */}
        <MobileDrawer
          isOpen={isMobileDrawerOpen}
          onClose={() => setIsMobileDrawerOpen(false)}
        />

        {/* PWA Install Prompt */}
        <PWAInstallBanner />

        {/* Offline/Online Indicator */}
        <OfflineIndicator />
      </div>
    </div>
  );
}
