import { createFileRoute, Outlet } from '@tanstack/react-router'

export const Route = createFileRoute('/dashboard')({
  component: DashboardLayout,
})

import { Navigate, useLocation } from '@tanstack/react-router'

function DashboardLayout() {
  const userStr = localStorage.getItem('iss_user')
  const user = userStr ? JSON.parse(userStr) : null
  const location = useLocation()

  if (!user) {
    return <Navigate to="/auth/login" />
  }

  // Only redirect if we are exactly at /dashboard
  if (location.pathname === '/dashboard' || location.pathname === '/dashboard/') {
    // Admin redirect
    if (user.role === 'admin') {
      return <Navigate to="/dashboard/admin" />
    }

    // APS/Others redirect
    return <Navigate to="/dashboard/user" />
  }

  // Otherwise render children (nested routes like /dashboard/admin)
  return <Outlet />
}
