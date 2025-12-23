import React, { Suspense, useCallback, useEffect, useState } from "react";
import { createRootRoute, Outlet, useLocation, Navigate } from "@tanstack/react-router";
import { AppLayout } from "../components/layout/AppLayout";
import { usersApi } from "../lib/api";

const TanStackRouterDevtools =
  import.meta.env.PROD
    ? () => null // Render nothing in production
    : React.lazy(() =>
      // Lazy load in development
      import("@tanstack/router-devtools").then((res) => ({
        default: res.TanStackRouterDevtools,
        // For Embedded Mode
        // default: res.TanStackRouterDevtoolsPanel
      }))
    );

import { AuthProvider, useAuth } from "../features/auth/AuthContext";

import { Toaster } from "../components/ui/Toast";

function RootComponent() {
  const location = useLocation();
  const pathname = location.pathname;
  const { isAuthenticated, isLoading } = useAuth();
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(true);
  const [isOnboarded, setIsOnboarded] = useState<boolean | null>(null);
  const [onboardingError, setOnboardingError] = useState<string | null>(null);

  // Strict check for auth pages to hide AppLayout (which contains BottomNav)
  const isAuthPage =
    pathname === '/login' ||
    pathname === '/login/' ||
    pathname === '/register' ||
    pathname === '/register/';

  const isWizardPage = pathname === '/wizard' || pathname === '/wizard/';

  // Check onboarding status after auth
  const checkOnboarding = useCallback(async () => {
    if (!isAuthenticated || isAuthPage || isWizardPage) {
      setOnboardingError(null);
      setIsCheckingOnboarding(false);
      return;
    }

    try {
      setIsCheckingOnboarding(true);
      setOnboardingError(null);
      const profile = await usersApi.getMe();
      setIsOnboarded(profile?.is_onboarded ?? false);
    } catch {
      setIsOnboarded(null);
      setOnboardingError("Impossibile verificare lo stato onboarding");
    } finally {
      setIsCheckingOnboarding(false);
    }
  }, [isAuthenticated, isAuthPage, isWizardPage]);

  useEffect(() => {
    if (!isLoading) {
      checkOnboarding();
    }
  }, [isLoading, checkOnboarding]);

  if (isLoading || isCheckingOnboarding) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="text-muted-foreground text-sm">Caricamento...</p>
        </div>
      </div>
    );
  }

  if (onboardingError && isAuthenticated && !isAuthPage && !isWizardPage) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="w-full max-w-sm px-4">
          <div className="bg-card border rounded-xl p-4">
            <div className="font-semibold">Errore</div>
            <div className="mt-1 text-sm text-muted-foreground">{onboardingError}</div>
            <button
              className="mt-4 w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold"
              onClick={checkOnboarding}
            >
              Riprova
            </button>
          </div>
          <Toaster />
        </div>
      </div>
    );
  }

  if (!isAuthenticated && !isAuthPage) {
    return <Navigate to="/login" />;
  }

  if (isAuthenticated && isAuthPage) {
    return <Navigate to="/" />;
  }

  if (isAuthPage) {
    return (
      <>
        <Outlet />
        <Toaster />
      </>
    );
  }

  // Redirect to wizard if not onboarded (and not already on wizard)
  if (isAuthenticated && isOnboarded === false && !isWizardPage) {
    return <Navigate to="/wizard" />;
  }

  // Wizard page without AppLayout
  if (isWizardPage) {
    return (
      <>
        <Outlet />
        <Toaster />
      </>
    );
  }

  return (
    <AppLayout>
      <Outlet />
      <Toaster />
    </AppLayout>
  );
}

export const Route = createRootRoute({
  component: () => (
    <AuthProvider>
      <RootComponent />
      <Suspense>
        <TanStackRouterDevtools />
      </Suspense>
    </AuthProvider>
  ),
});
