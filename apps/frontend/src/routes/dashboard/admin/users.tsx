import { createFileRoute } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

// Types
interface User {
  id: number
  email: string
  username?: string
  full_name?: string
  role: string
  status: string
  created_at: string
  last_login?: string
  is_active: boolean
  accessibility_needs?: string
  aps_nome_organizzazione?: string
}

interface UserStats {
  total_users: number
  active_users: number
  pending_users: number
  suspended_users: number
  aps_organizations: number
  accessibility_users: number
  users_by_role: Record<string, number>
  users_by_status: Record<string, number>
}

export const Route = createFileRoute('/dashboard/admin/users')({
  component: UsersPage,
})

function UsersPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterRole, setFilterRole] = useState<string>('')
  const [filterStatus, setFilterStatus] = useState<string>('')
  const [page, setPage] = useState(0)
  const limit = 20

  // Fetch user stats
  const { data: statsData } = useQuery<UserStats>({
    queryKey: ['user-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/users/stats', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      if (!response.ok) {
        // Return default stats if not authorized
        return {
          total_users: 0,
          active_users: 0,
          pending_users: 0,
          suspended_users: 0,
          aps_organizations: 0,
          accessibility_users: 0,
          users_by_role: {},
          users_by_status: {}
        }
      }
      return response.json()
    }
  })

  // Fetch users list
  const { data: usersData, isLoading } = useQuery<User[]>({
    queryKey: ['users', searchQuery, filterRole, filterStatus, page],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String(page * limit),
        limit: String(limit),
        ...(searchQuery && { search: searchQuery }),
        ...(filterRole && { role: filterRole }),
        ...(filterStatus && { status: filterStatus })
      })

      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/v1/users/?${params}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
      if (!response.ok) return []
      return response.json()
    }
  })

  // Change user status mutation
  const changeStatusMutation = useMutation({
    mutationFn: async ({ userId, newStatus }: { userId: number, newStatus: string }) => {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/v1/users/${userId}/change-status?new_status=${newStatus}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      })
      if (!response.ok) throw new Error('Failed to change status')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      queryClient.invalidateQueries({ queryKey: ['user-stats'] })
    }
  })

  const users = usersData || []
  const stats = statsData

  const getRoleBadge = (role: string) => {
    const roleColors: Record<string, string> = {
      'super_admin': 'bg-purple-100 text-purple-800',
      'admin': 'bg-red-100 text-red-800',
      'moderator': 'bg-orange-100 text-orange-800',
      'aps_responsabile': 'bg-blue-100 text-blue-800',
      'aps_operatore': 'bg-cyan-100 text-cyan-800',
      'partner': 'bg-green-100 text-green-800',
      'user': 'bg-gray-100 text-gray-800',
      'volunteer': 'bg-yellow-100 text-yellow-800'
    }
    const roleNames: Record<string, string> = {
      'super_admin': '👑 Super Admin',
      'admin': '🔐 Admin',
      'moderator': '🛡️ Moderatore',
      'aps_responsabile': '🏛️ APS Resp.',
      'aps_operatore': '👷 APS Oper.',
      'partner': '🤝 Partner',
      'user': '👤 Utente',
      'volunteer': '🙋 Volontario'
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${roleColors[role] || 'bg-gray-100 text-gray-800'}`}>
        {roleNames[role] || role}
      </span>
    )
  }

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      'active': 'bg-green-100 text-green-800',
      'pending': 'bg-yellow-100 text-yellow-800',
      'suspended': 'bg-red-100 text-red-800',
      'inactive': 'bg-gray-100 text-gray-800'
    }
    const statusNames: Record<string, string> = {
      'active': '✅ Attivo',
      'pending': '⏳ In Attesa',
      'suspended': '🚫 Sospeso',
      'inactive': '💤 Inattivo'
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
        {statusNames[status] || status}
      </span>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">👥 Gestione Utenti</h1>
          <p className="text-gray-600 mt-1">Pannello completo per la gestione utenti della piattaforma ISS</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-iss-primary text-white rounded-lg hover:bg-iss-primary-dark transition-colors">
          <span className="mr-2">➕</span>
          Nuovo Utente
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-xl border border-blue-200">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-blue-700">Totali</h3>
            <span className="text-2xl">👥</span>
          </div>
          <p className="text-3xl font-bold text-blue-900 mt-2">{stats?.total_users ?? 0}</p>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-xl border border-green-200">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-green-700">Attivi</h3>
            <span className="text-2xl">✅</span>
          </div>
          <p className="text-3xl font-bold text-green-900 mt-2">{stats?.active_users ?? 0}</p>
        </div>
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-xl border border-yellow-200">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-yellow-700">In Attesa</h3>
            <span className="text-2xl">⏳</span>
          </div>
          <p className="text-3xl font-bold text-yellow-900 mt-2">{stats?.pending_users ?? 0}</p>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-xl border border-red-200">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-red-700">Sospesi</h3>
            <span className="text-2xl">🚫</span>
          </div>
          <p className="text-3xl font-bold text-red-900 mt-2">{stats?.suspended_users ?? 0}</p>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-xl border border-purple-200">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-purple-700">APS</h3>
            <span className="text-2xl">🏛️</span>
          </div>
          <p className="text-3xl font-bold text-purple-900 mt-2">{stats?.aps_organizations ?? 0}</p>
        </div>
        <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 p-4 rounded-xl border border-cyan-200">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-cyan-700">Accessibilità</h3>
            <span className="text-2xl">♿</span>
          </div>
          <p className="text-3xl font-bold text-cyan-900 mt-2">{stats?.accessibility_users ?? 0}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl border shadow-sm">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">🔍 Cerca</label>
            <input
              type="text"
              placeholder="Nome, email, username..."
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setPage(0); }}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-iss-primary focus:border-transparent"
            />
          </div>
          <div className="w-full md:w-48">
            <label className="block text-sm font-medium text-gray-700 mb-1">👤 Ruolo</label>
            <select
              value={filterRole}
              onChange={(e) => { setFilterRole(e.target.value); setPage(0); }}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-iss-primary focus:border-transparent"
            >
              <option value="">Tutti i ruoli</option>
              <option value="super_admin">Super Admin</option>
              <option value="admin">Admin</option>
              <option value="moderator">Moderatore</option>
              <option value="aps_responsabile">APS Responsabile</option>
              <option value="aps_operatore">APS Operatore</option>
              <option value="partner">Partner</option>
              <option value="user">Utente</option>
              <option value="volunteer">Volontario</option>
            </select>
          </div>
          <div className="w-full md:w-48">
            <label className="block text-sm font-medium text-gray-700 mb-1">📊 Stato</label>
            <select
              value={filterStatus}
              onChange={(e) => { setFilterStatus(e.target.value); setPage(0); }}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-iss-primary focus:border-transparent"
            >
              <option value="">Tutti gli stati</option>
              <option value="active">Attivo</option>
              <option value="pending">In Attesa</option>
              <option value="suspended">Sospeso</option>
              <option value="inactive">Inattivo</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="animate-spin text-4xl mb-4">⏳</div>
            <p className="text-gray-600">Caricamento utenti...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4">👤</div>
            <h3 className="text-xl font-semibold text-gray-800">Nessun utente trovato</h3>
            <p className="text-gray-600 mt-2">Prova a modificare i filtri di ricerca</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Utente</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Ruolo</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Stato</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Registrato</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Ultimo accesso</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Azioni</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-iss-primary/10 flex items-center justify-center text-iss-primary font-bold">
                          {(user.full_name || user.email)[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{user.full_name || 'N/A'}</p>
                          {user.username && <p className="text-sm text-gray-500">@{user.username}</p>}
                          {user.aps_nome_organizzazione && (
                            <p className="text-xs text-blue-600">🏛️ {user.aps_nome_organizzazione}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{user.email}</td>
                    <td className="px-4 py-3">{getRoleBadge(user.role)}</td>
                    <td className="px-4 py-3">{getStatusBadge(user.status)}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {new Date(user.created_at).toLocaleDateString('it-IT')}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {user.last_login ? new Date(user.last_login).toLocaleDateString('it-IT') : 'Mai'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Visualizza"
                        >
                          👁️
                        </button>
                        <button
                          className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                          title="Modifica"
                        >
                          ✏️
                        </button>
                        {user.status === 'pending' && (
                          <button
                            onClick={() => changeStatusMutation.mutate({ userId: user.id, newStatus: 'active' })}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Approva"
                          >
                            ✅
                          </button>
                        )}
                        {user.status === 'active' && (
                          <button
                            onClick={() => changeStatusMutation.mutate({ userId: user.id, newStatus: 'suspended' })}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Sospendi"
                          >
                            🚫
                          </button>
                        )}
                        {user.status === 'suspended' && (
                          <button
                            onClick={() => changeStatusMutation.mutate({ userId: user.id, newStatus: 'active' })}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Riattiva"
                          >
                            ♻️
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {users.length > 0 && (
          <div className="px-4 py-3 border-t bg-gray-50 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Pagina {page + 1} • {users.length} utenti mostrati
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-3 py-1 border rounded-lg hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ← Precedente
              </button>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={users.length < limit}
                className="px-3 py-1 border rounded-lg hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Successiva →
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Role Distribution */}
      {stats?.users_by_role && Object.keys(stats.users_by_role).length > 0 && (
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <h3 className="text-lg font-semibold mb-4">📊 Distribuzione per Ruolo</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.users_by_role).map(([role, count]) => (
              <div key={role} className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-iss-primary">{count}</p>
                <p className="text-sm text-gray-600 capitalize">{role.replace('_', ' ')}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
