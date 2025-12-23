
# Implementation Plan - Dashboard Fixes & Settings Page

## Goal Description
Fix the "empty page" issue on dashboard routes (`/dashboard/admin`, `/dashboard/user`) and create the missing `/settings` page.

## User Review Required
None.

## Proposed Changes

### Frontend - Dashboard
#### [MODIFY] [DashboardLayout.tsx](file:///home/autcir_gmail_com/develop/apps/iss/apps/frontend/src/components/dashboard/DashboardLayout.tsx)
- Ensure it's correctly exported and imported.
- No major logic changes expected unless sidebar/header are broken.

#### [MODIFY] [admin.tsx](file:///home/autcir_gmail_com/develop/apps/iss/apps/frontend/src/routes/dashboard/admin.tsx)
- Verify `useQuery` usage and ensure it doesn't return `null` unexpectedly.

#### [MODIFY] [user.tsx](file:///home/autcir_gmail_com/develop/apps/iss/apps/frontend/src/routes/dashboard/user.tsx)
- Similar verification as admin.tsx.

### Frontend - Settings
#### [NEW] [settings.tsx](file:///home/autcir_gmail_com/develop/apps/iss/apps/frontend/src/routes/settings.tsx)
- Create a new route for `/settings`.
- Implement a basic settings page (or a placeholder "Under Construction").
- Use [DashboardLayout](file:///home/autcir_gmail_com/develop/apps/iss/apps/frontend/src/components/dashboard/DashboardLayout.tsx#16-96) if appropriate, or a simple page layout.

### Verification Plan
#### Automated Tests
- None.

#### Manual Verification
- Manual navigation to `/dashboard/admin` and `/dashboard/user` to ensure content renders.
- Manual navigation to `/settings` to ensure 404 is gone.
