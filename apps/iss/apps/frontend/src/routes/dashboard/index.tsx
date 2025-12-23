import { createFileRoute, Outlet } from '@tanstack/react-router'

export const Route = createFileRoute('/dashboard')({
  component: DashboardLayout,
})

import { Navigate } from '@tanstack/react-router'

function DashboardLayout() {
  const userStr = localStorage.getItem('iss_user')
  const user = userStr ? JSON.parse(userStr) : null

  if (!user) {
    return <Navigate to="/auth/login" />
  }

  // Admin redirect
  if (user.role === 'admin') {
    return <Navigate to="/dashboard/admin" />
  }

  // APS/Others redirect
  return <Navigate to="/dashboard/user" />
}
