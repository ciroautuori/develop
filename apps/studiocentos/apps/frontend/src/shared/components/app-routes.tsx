import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { StudiocentosLanding } from '../../features/landing'
import { PrivacyPolicy, TermsOfService } from '../../features/landing/pages'
import { NotFound } from '../../features/landing/pages/NotFound'
import { ROUTES } from "../lib/utils"
import { getAdminToken } from "../lib/api"

// Lazy load ToolAI pages to avoid framer-motion bundling issues
const ToolAIHub = lazy(() => import('../../features/landing/pages/ToolAIHub').then(m => ({ default: m.ToolAIHub })))
const ToolAIPostDetail = lazy(() => import('../../features/landing/pages/ToolAIPostDetail').then(m => ({ default: m.ToolAIPostDetail })))

// Lazy load all admin components to avoid loading framer-motion on landing page
const DashboardLayout = lazy(() => import('../../features/dashboard/components/dashboard-layout').then(m => ({ default: m.DashboardLayout })))
const DashboardOverview = lazy(() => import('../../features/dashboard/components/dashboard-overview').then(m => ({ default: m.DashboardOverview })))
const SupportDashboard = lazy(() => import('../../features/support/pages/SupportDashboard').then(m => ({ default: m.SupportDashboard })))
const PortfolioManagement = lazy(() => import('../../features/admin/components/PortfolioManagement').then(m => ({ default: m.PortfolioManagement })))
const AdminLogin = lazy(() => import('../../features/admin/pages/AdminLogin').then(m => ({ default: m.AdminLogin })))
const AdminLayout = lazy(() => import('../../features/admin/layouts/AdminLayout').then(m => ({ default: m.AdminLayout })))
// AdminDashboard rimosso - redirect a BusinessHub
// const AdminDashboard = lazy(() => import('../../features/admin/pages/Dashboard').then(m => ({ default: m.AdminDashboard })))
// PortfolioList rimosso - integrato in PortfolioHub
// const PortfolioList = lazy(() => import('../../features/admin/pages/PortfolioList').then(m => ({ default: m.PortfolioList })))
const PortfolioHub = lazy(() => import('../../features/admin/pages/PortfolioHub').then(m => ({ default: m.PortfolioHub })))
const ProjectForm = lazy(() => import('../../features/admin/pages/ProjectForm').then(m => ({ default: m.ProjectForm })))
const ServiceForm = lazy(() => import('../../features/admin/pages/ServiceForm').then(m => ({ default: m.ServiceForm })))
// Settings.tsx deprecated - use SettingsHub instead
const CalendarView = lazy(() => import('../../features/admin/pages/CalendarView').then(m => ({ default: m.CalendarView })))
// Analytics rimosso - integrato in AIMarketing Hub
// const Analytics = lazy(() => import('../../features/admin/pages/Analytics').then(m => ({ default: m.Analytics })))
// ResponsiveFinanceDashboard deprecated - use FinanceHub directly
const UserManagement = lazy(() => import('../../features/admin/pages/UserManagement').then(m => ({ default: m.UserManagement })))
const AIMarketing = lazy(() => import('../../features/admin/pages/AIMarketing').then(m => ({ default: m.AIMarketing })))
const EditorialCalendar = lazy(() => import('../../features/admin/pages/EditorialCalendar').then(m => ({ default: m.EditorialCalendar })))
const BusinessHub = lazy(() => import('../../features/admin/pages/BusinessHub').then(m => ({ default: m.BusinessHub })))
const FinanceHub = lazy(() => import('../../features/admin/pages/FinanceHub').then(m => ({ default: m.FinanceHub })))
const SettingsHub = lazy(() => import('../../features/admin/pages/SettingsHub').then(m => ({ default: m.SettingsHub })))
// ToolAIBackoffice rimosso - integrato in PortfolioHub
// const ToolAIBackoffice = lazy(() => import('../../features/admin/pages/ToolAIBackoffice').then(m => ({ default: m.ToolAIBackoffice })))
const CustomerList = lazy(() => import('../../features/crm/components/CustomerList'))
const CustomerDetail = lazy(() => import('../../features/crm/components/CustomerDetail'))
const CustomerForm = lazy(() => import('../../features/crm/components/CustomerForm'))
const QuoteList = lazy(() => import('../../features/quotes/components/QuoteList'))
const QuoteForm = lazy(() => import('../../features/quotes/components/QuoteForm'))
const CourseForm = lazy(() => import('../../features/admin/pages/CourseForm').then(m => ({ default: m.CourseForm })))

// Loading fallback for lazy components
const LazyFallback = () => (
  <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
    <div className="animate-spin w-8 h-8 border-4 border-gold border-t-transparent rounded-full"></div>
  </div>
)

// Protected Route Component - Admin Only with token validation
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  // Admin-only authentication with expiry check
  const adminToken = getAdminToken();
  if (adminToken) {
    return <>{children}</>
  }

  // Redirect to admin login
  return <Navigate to="/admin/login" replace />
}

export function AppRoutes() {
  return (
    <Routes>
      {/* Login routes - Redirect to Admin Login */}
      <Route
        path={ROUTES.LOGIN}
        element={<Navigate to="/admin/login" replace />}
      />

      <Route
        path={ROUTES.REGISTER}
        element={<Navigate to="/admin/login" replace />}
      />

      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardOverview />} />
        <Route path="portfolio" element={<PortfolioManagement />} />
        <Route path="bookings" element={<Navigate to="/admin/business" replace />} />
        <Route path="users" element={<Navigate to="/admin/utenti" replace />} />
        <Route path="support" element={<SupportDashboard />} />
        <Route path="settings" element={<Navigate to="/admin/settings" replace />} />
      </Route>

      {/* Legacy routes - redirect to admin equivalents */}
      <Route path={ROUTES.USERS} element={<Navigate to="/admin/utenti" replace />} />
      <Route path={ROUTES.SETTINGS} element={<Navigate to="/admin/settings" replace />} />
      <Route path={ROUTES.PROFILE} element={<Navigate to="/admin/settings" replace />} />

      {/* Admin Routes */}
      <Route path="/admin/login" element={<AdminLogin />} />

      <Route path="/admin" element={
        <ProtectedRoute>
          <AdminLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/admin/business" replace />} />
        <Route path="portfolio" element={<PortfolioHub />} />
        <Route path="portfolio/project/new" element={<ProjectForm />} />
        <Route path="portfolio/project/:id" element={<ProjectForm />} />
        <Route path="portfolio/service/new" element={<ServiceForm />} />
        <Route path="portfolio/service/:id" element={<ServiceForm />} />
        <Route path="calendario" element={<CalendarView />} />
        <Route path="analytics" element={<Navigate to="/admin/ai-marketing" replace />} />
        <Route path="finance" element={<FinanceHub />} />
        <Route path="ai-marketing" element={<AIMarketing />} />
        <Route path="calendario-editoriale" element={<EditorialCalendar />} />
        <Route path="utenti" element={<UserManagement />} />
        {/* impostazioni redirects to settings */}
        <Route path="impostazioni" element={<Navigate to="/admin/settings" replace />} />

        {/* Main Hubs */}
        <Route path="business" element={<BusinessHub />} />
        <Route path="settings" element={<SettingsHub />} />
        <Route path="toolai-backoffice" element={<Navigate to="/admin/portfolio" replace />} />

        {/* Courses - Corso Tool AI */}
        {/* Hub is now inside Portfolio */}
        <Route path="courses/new" element={<CourseForm />} />
        <Route path="courses/:id" element={<CourseForm />} />

        {/* CRM - Customers */}
        <Route path="crm/customers" element={<CustomerList />} />
        <Route path="crm/customers/new" element={<CustomerForm />} />
        <Route path="crm/customers/:id" element={<CustomerDetail />} />
        <Route path="crm/customers/:id/edit" element={<CustomerForm />} />

        {/* Quotes - Preventivi */}
        <Route path="quotes" element={<QuoteList />} />
        <Route path="quotes/new" element={<QuoteForm />} />
        <Route path="quotes/:id/edit" element={<QuoteForm />} />
      </Route>

      {/* Landing Page (Home) */}
      <Route
        path={ROUTES.HOME}
        element={<StudiocentosLanding />}
      />

      {/* Legal Pages */}
      <Route path="/privacy" element={<PrivacyPolicy />} />
      <Route path="/terms" element={<TermsOfService />} />

      {/* ToolAI Public Pages - Lazy loaded to avoid framer-motion issues */}
      <Route path="/toolai" element={<Suspense fallback={<LazyFallback />}><ToolAIHub /></Suspense>} />
      <Route path="/toolai/:slug" element={<Suspense fallback={<LazyFallback />}><ToolAIPostDetail /></Suspense>} />

      {/* Localized Landing Pages */}
      <Route path="/en/*" element={<StudiocentosLanding />} />
      <Route path="/es/*" element={<StudiocentosLanding />} />

      {/* Default redirect for unknown routes -> NotFound (Fixed SEO Redirect/Soft 404 issue) */}
      <Route
        path="*"
        element={<NotFound />}
      />
    </Routes>
  )
}
