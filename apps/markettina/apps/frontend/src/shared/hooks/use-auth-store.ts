import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '../lib/api'
import { STORAGE_KEYS } from '../config/constants'

export interface User {
  id: number
  email: string
  username: string
  first_name?: string
  last_name?: string
  role: string
  is_active: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  clearError: () => void
  refreshUser: () => Promise<void>
}

interface RegisterData {
  email: string
  username: string
  password: string
  first_name: string
  last_name: string
}

type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })

        try {
          const response = await apiClient.post('/auth/login', { email, password })

          const { access_token, user } = response.data

          // Set token in localStorage for client interceptor
          localStorage.setItem(STORAGE_KEYS.adminToken, access_token)

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Login failed'
          set({
            error: message,
            isLoading: false,
          })
          throw error
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true, error: null })

        try {
          const response = await apiClient.post('/auth/register', userData)

          const { access_token, user } = response.data

          // Set token in localStorage for client interceptor
          localStorage.setItem(STORAGE_KEYS.adminToken, access_token)

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Registration failed'
          set({
            error: message,
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        // Clear tokens from localStorage
        localStorage.removeItem(STORAGE_KEYS.adminToken)
        localStorage.removeItem(STORAGE_KEYS.adminRefreshToken)

        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        })
      },

      clearError: () => {
        set({ error: null })
      },

      refreshUser: async () => {
        const { token, isAuthenticated } = get()

        if (!token || !isAuthenticated) return

        try {
          const response = await apiClient.get('/users/me')
          set({ user: response.data })
        } catch {
          // If refresh fails, logout
          get().logout()
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Ensure token is in localStorage after rehydration
        if (state?.token) {
          localStorage.setItem(STORAGE_KEYS.adminToken, state.token)
        }
      },
    }
  )
)
