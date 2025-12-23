import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { ThemeProvider } from 'next-themes';

import { routeTree } from './routeTree.gen';
import { AuthProvider } from '@/contexts/AuthContext';
import { DashboardProvider } from '@/contexts/DashboardContext';
import { ErrorBoundary } from '@/components/ErrorBoundary';

import './globals.css';

// Gestione globale errori non catturati per prevenire [ERROR] {}
window.addEventListener('error', (event) => {
  console.debug('Global error caught:', event.error);
  event.preventDefault(); // Previeni la propagazione alla console
});

window.addEventListener('unhandledrejection', (event) => {
  console.debug('Unhandled promise rejection caught:', event.reason);
  event.preventDefault(); // Previeni la propagazione alla console
});

// Create router instance
const router = createRouter({ routeTree });

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

// Create a client with better error handling
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: false, // Disable retries to prevent console errors
      refetchOnWindowFocus: false,
    },
  },
});

const rootElement = document.getElementById('root');
if (!rootElement?.innerHTML) {
  const root = createRoot(rootElement!);
  
  root.render(
    <StrictMode>
      <ErrorBoundary>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <QueryClientProvider client={queryClient}>
            <AuthProvider>
              <DashboardProvider>
                <RouterProvider router={router} />
{/* <ReactQueryDevtools initialIsOpen={false} /> */}
              </DashboardProvider>
            </AuthProvider>
          </QueryClientProvider>
        </ThemeProvider>
      </ErrorBoundary>
    </StrictMode>
  );
}
