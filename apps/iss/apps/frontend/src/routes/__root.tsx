import React from 'react';
import { createRootRoute, Outlet } from '@tanstack/react-router';
import { ModernNavbar } from '@/components/layout/ModernNavbar';
import { Footer } from '@/components/layout/Footer';

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <ModernNavbar />
      <main className="flex-1 pt-14 sm:pt-16">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
