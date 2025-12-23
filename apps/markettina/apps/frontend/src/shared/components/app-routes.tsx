/**
 * MARKETTINA v2.0 - App Routes
 * Routing configuration for the application
 */
import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { MarkettinaLanding } from '../../features/landing'
import { PrivacyPolicy, TermsOfService } from '../../features/landing/pages'
import { ROUTES } from "../config/routes"
import { getAdminToken } from "../utils/auth"

// Lazy load admin components
const DashboardLayout = lazy(() => import('../../features/dashboard/components/dashboard-layout').then(m => ({ default: m.DashboardLayout })))
const DashboardOverview = lazy(() => import('../../features/dashboard/components/dashboard-overview').then(m => ({ default: m.DashboardOverview })))
const SupportDashboard = lazy(() => import('../../features/support/pages/SupportDashboard').then(m => ({ default: m.SupportDashboard })))
const AdminLogin = lazy(() => import('../../features/admin/pages/AdminLogin').then(m => ({ default: m.AdminLogin })))
const UnifiedLogin = lazy(() => import('../../features/auth/pages/UnifiedLogin').then(m => ({ default: m.UnifiedLogin })))
const AdminLayout = lazy(() => import('../../features/admin/layouts/AdminLayout').then(m => ({ default: m.AdminLayout })))
const AdminDashboard = lazy(() => import('../../features/admin/pages/Dashboard').then(m => ({ default: m.AdminDashboard })))

const CalendarView = lazy(() => import('../../features/admin/pages/CalendarView').then(m => ({ default: m.CalendarView })))
const Analytics = lazy(() => import('../../features/admin/pages/Analytics').then(m => ({ default: m.Analytics })))
// ResponsiveFinanceDashboard removed - using FinanceHub instead
const UserManagement = lazy(() => import('../../features/admin/pages/UserManagement').then(m => ({ default: m.UserManagement })))
const AIMarketing = lazy(() => import('../../features/admin/pages/AIMarketing').then(m => ({ default: m.AIMarketing })))
const EditorialCalendar = lazy(() => import('../../features/admin/pages/EditorialCalendar').then(m => ({ default: m.EditorialCalendar })))
const BusinessHub = lazy(() => import('../../features/admin/pages/BusinessHub').then(m => ({ default: m.BusinessHub })))
const FinanceHub = lazy(() => import('../../features/admin/pages/FinanceHub').then(m => ({ default: m.FinanceHub })))

const SettingsHub = lazy(() => import('../../features/admin/pages/SettingsHub').then(m => ({ default: m.SettingsHub })))
const AnalyticsGA4 = lazy(() => import('../../features/admin/pages/AnalyticsGA4').then(m => ({ default: m.AnalyticsGA4 })))
const AnalyticsSEO = lazy(() => import('../../features/admin/pages/AnalyticsSEO'))
// CRM Components
const CustomerList = lazy(() => import('../../features/crm/components/CustomerList'))
const CustomerDetail = lazy(() => import('../../features/crm/components/CustomerDetail'))
const CustomerForm = lazy(() => import('../../features/crm/components/CustomerForm'))

// Customer Portal Components
const CustomerLayout = lazy(() => import('../../features/customer/layouts/CustomerLayout').then(m => ({ default: m.CustomerLayout })))
const CustomerDashboard = lazy(() => import('../../features/customer/pages/CustomerDashboard').then(m => ({ default: m.CustomerDashboard })))
const MyContent = lazy(() => import('../../features/customer/pages/MyContent').then(m => ({ default: m.MyContent })))
const MyBrandDNA = lazy(() => import('../../features/customer/pages/MyBrandDNA').then(m => ({ default: m.MyBrandDNA })))
const MySettings = lazy(() => import('../../features/customer/pages/MySettings').then(m => ({ default: m.MySettings })))
const CustomerAIMarketing = lazy(() => import('../../features/customer/pages/CustomerAIMarketing').then(m => ({ default: m.CustomerAIMarketing })))
const TokenPurchase = lazy(() => import('../../features/customer/pages/TokenPurchase').then(m => ({ default: m.TokenPurchase })))

// Onboarding Wizard
const OnboardingWizard = lazy(() => import('../../features/onboarding/OnboardingWizard').then(m => ({ default: m.OnboardingWizard })))

// Loading fallback for lazy components
const LazyFallback = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <div className="animate-spin w-8 h-8 border-4 border-gold border-t-transparent rounded-full"></div>
  </div>
)

// Admin Protected Route - Checks admin token
function AdminProtectedRoute({ children }: { children: React.ReactNode }) {
  const adminToken = getAdminToken();
  if (adminToken) {
    return <>{children}</>
  }
  return <Navigate to="/login" replace />
}

// Customer Protected Route - Checks access_token
function CustomerProtectedRoute({ children }: { children: React.ReactNode }) {
  const customerToken = localStorage.getItem('access_token');
  if (customerToken) {
    return <>{children}</>
  }
  return <Navigate to="/login" replace />
}

// Legacy ProtectedRoute - checks both tokens for backward compatibility
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const adminToken = getAdminToken();
  const customerToken = localStorage.getItem('access_token');
  if (adminToken || customerToken) {
    return <>{children}</>
  }
  return <Navigate to="/login" replace />
}

export function AppRoutes() {
  return (
    <Routes>
      {/* Unified Login - Single login page with role-based redirect */}
      <Route
        path={ROUTES.LOGIN}
        element={<UnifiedLogin />}
      />

      <Route
        path={ROUTES.REGISTER}
        element={<UnifiedLogin />}
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
        <Route path="support" element={<SupportDashboard />} />
      </Route>

      <Route
        path={ROUTES.USERS}
        element={
          <AdminProtectedRoute>
            <AdminLayout>
              <UserManagement />
            </AdminLayout>
          </AdminProtectedRoute>
        }
      />

      <Route
        path={ROUTES.SETTINGS}
        element={
          <AdminProtectedRoute>
            <AdminLayout>
              <SettingsHub />
            </AdminLayout>
          </AdminProtectedRoute>
        }
      />

      <Route
        path={ROUTES.PROFILE}
        element={
          <AdminProtectedRoute>
            <AdminLayout>
              <SettingsHub />
            </AdminLayout>
          </AdminProtectedRoute>
        }
      />

      {/* Admin Routes - Redirect old admin login to unified login */}
      <Route path="/admin/login" element={<Navigate to="/login" replace />} />

      <Route path="/admin" element={
        <AdminProtectedRoute>
          <AdminLayout />
        </AdminProtectedRoute>
      }>
        <Route index element={<AdminDashboard />} />
        <Route path="calendario" element={<CalendarView />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="finance" element={<FinanceHub />} />
        <Route path="ai-marketing" element={<AIMarketing />} />
        <Route path="calendario-editoriale" element={<EditorialCalendar />} />
        <Route path="utenti" element={<UserManagement />} />
        {/* Settings redirected to SettingsHub */}
        <Route path="impostazioni" element={<SettingsHub />} />

        {/* Hubs */}
        <Route path="business" element={<BusinessHub />} />
        <Route path="finance-hub" element={<FinanceHub />} />
        <Route path="settings" element={<SettingsHub />} />
        <Route path="analytics/ga4" element={<AnalyticsGA4 />} />
        <Route path="analytics/seo" element={<AnalyticsSEO />} />

        {/* CRM - Customers */}
        <Route path="crm/customers" element={<CustomerList />} />
        <Route path="crm/customers/new" element={<CustomerForm />} />
        <Route path="crm/customers/:id" element={<CustomerDetail />} />
        <Route path="crm/customers/:id/edit" element={<CustomerForm />} />
      </Route>

      {/* === CUSTOMER PORTAL ROUTES === */}
      <Route path="/customer" element={
        <CustomerProtectedRoute>
          <CustomerLayout />
        </CustomerProtectedRoute>
      }>
        <Route index element={<CustomerDashboard />} />
        <Route path="ai-marketing" element={<CustomerAIMarketing />} />
        <Route path="content" element={<MyContent />} />
        <Route path="brand" element={<MyBrandDNA />} />
        <Route path="settings" element={<MySettings />} />
        <Route path="tokens" element={<TokenPurchase />} />
      </Route>

      {/* === ONBOARDING WIZARD === */}
      <Route path="/onboarding" element={
        <CustomerProtectedRoute>
          <OnboardingWizard />
        </CustomerProtectedRoute>
      } />

      {/* Landing Page (Home) */}
      <Route
        path={ROUTES.HOME}
        element={<MarkettinaLanding />}
      />

      {/* Legal Pages */}
      <Route path="/privacy" element={<PrivacyPolicy />} />
      <Route path="/terms" element={<TermsOfService />} />

      {/* Default redirect for unknown routes */}
      <Route
        path="*"
        element={<Navigate to={ROUTES.HOME} replace />}
      />
    </Routes>
  )
}
