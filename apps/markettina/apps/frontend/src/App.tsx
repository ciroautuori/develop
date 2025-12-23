import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'sonner'
import { HelmetProvider } from 'react-helmet-async'
import { ThemeProvider } from './shared/contexts/ThemeContext'
import { LanguageProvider } from './shared/i18n'
import { AppRoutes } from './shared/components/app-routes'
import { Suspense } from 'react'
import './app/assets/styles/globals.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

// Loading fallback per prevenire FOUC
const LoadingFallback = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <div className="animate-spin w-8 h-8 border-4 border-gold border-t-transparent rounded-full"></div>
  </div>
)

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <LanguageProvider>
          <ThemeProvider>
            <BrowserRouter>
              <div className="min-h-screen bg-background font-sans antialiased">
                <Suspense fallback={<LoadingFallback />}>
                  <AppRoutes />
                </Suspense>
                <Toaster position="top-right" richColors />
              </div>
            </BrowserRouter>
          </ThemeProvider>
        </LanguageProvider>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </HelmetProvider>
  )
}

export default App
