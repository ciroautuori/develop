/**
 * User Management - API REALI NO MOCK
 * LIGHT MODE SUPPORT
 */
import { useState } from 'react';
import { Search, UserPlus, Shield, Power, Trash2, Users } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';

export function UserManagement() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const queryClient = useQueryClient();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Dynamic classes based on theme
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const itemBg = isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-200 text-gray-900';
  const paginationBg = isDark
    ? 'bg-white/5 hover:bg-white/10 text-white'
    : 'bg-gray-100 hover:bg-gray-200 text-gray-700';

  // API REALI
  const { data, isLoading } = useQuery({
    queryKey: ['users', page, search],
    queryFn: async () => {
      const token = localStorage.getItem('admin_token');
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '20',
        ...(search && { search })
      });
      const res = await fetch(`/api/v1/admin/users?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return res.json();
    },
  });

  // Mutation per attivare/disattivare utente
  const toggleUserStatus = useMutation({
    mutationFn: async ({ id, activate }: { id: number; activate: boolean }) => {
      const token = localStorage.getItem('admin_token');
      const endpoint = activate ? 'activate' : 'deactivate';
      const res = await fetch(`/api/v1/admin/users/${id}/${endpoint}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Errore durante l\'operazione');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Stato utente aggiornato');
    },
    onError: () => toast.error('Errore durante l\'operazione')
  });

  // Mutation per eliminare utente
  const deleteUser = useMutation({
    mutationFn: async (id: number) => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/v1/admin/users/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Errore durante l\'eliminazione');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Utente eliminato');
    },
    onError: () => toast.error('Errore durante l\'eliminazione')
  });

  // Mutation per cambiare ruolo
  const changeRole = useMutation({
    mutationFn: async ({ id, role }: { id: number; role: string }) => {
      const token = localStorage.getItem('admin_token');
      const res = await fetch(`/api/v1/admin/users/${id}/change-role`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role })
      });
      if (!res.ok) throw new Error('Errore durante il cambio ruolo');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('Ruolo aggiornato');
    },
    onError: () => toast.error('Errore durante il cambio ruolo')
  });

  const handleDeleteUser = (id: number) => {
    if (confirm('Sei sicuro di voler eliminare questo utente?')) {
      deleteUser.mutate(id);
    }
  };

  const handleToggleStatus = (user: any) => {
    toggleUserStatus.mutate({ id: user.id, activate: !user.is_active });
  };

  const users = data?.items || [];
  const total = data?.total || 0;

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
            <Users className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
              Gestione Utenti
            </h1>
            <p className="text-sm text-muted-foreground">
              Totale: {total} utenti
            </p>
          </div>
        </div>

        <button
          onClick={() => toast.info('Funzionalità creazione utente in sviluppo - gli utenti si registrano autonomamente')}
          className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold/90 transition flex items-center justify-center gap-2 text-sm sm:text-base shadow-md"
        >
          <UserPlus className="h-4 w-4 sm:h-5 sm:w-5" />
          Invita Utente
        </button>
      </motion.div>

      {/* Search - Mobile First */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
        <div className="relative">
          <Search className={`absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 ${textSecondary}`} />
          <input
            type="text"
            placeholder="Cerca utente..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={`w-full pl-10 sm:pl-12 pr-4 py-2.5 sm:py-3 border rounded-lg focus:outline-none focus:border-gold transition text-sm sm:text-base ${inputBg}`}
          />
        </div>
      </div>

      {/* Users List - Mobile First */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
        <h2 className={`text-lg sm:text-xl lg:text-2xl font-semibold mb-4 sm:mb-6 ${textPrimary}`}>Lista Utenti</h2>

        {isLoading ? (
          <div className="space-y-3 sm:space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className={`h-14 sm:h-16 rounded-lg animate-pulse ${isDark ? 'bg-white/5' : 'bg-gray-200'}`}></div>
            ))}
          </div>
        ) : users.length === 0 ? (
          <div className={`text-center py-8 sm:py-12 text-sm sm:text-base ${textSecondary}`}>
            Nessun utente trovato
          </div>
        ) : (
          <div className="space-y-2 sm:space-y-3">
            {users.map((user: any, index: number) => (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`flex items-center justify-between p-3 sm:p-4 rounded-lg transition ${itemBg}`}
              >
                <div className="flex items-center gap-3 sm:gap-4 min-w-0 flex-1">
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gold/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-gold font-semibold text-sm sm:text-base">
                      {user.email?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className={`font-medium text-sm sm:text-base truncate ${textPrimary}`}>{user.email}</p>
                    <p className={`text-xs sm:text-sm ${textSecondary}`}>
                      {user.is_active ? 'Attivo' : 'Disattivato'} • {user.role || 'User'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                  {user.is_verified && (
                    <Shield className="h-4 w-4 sm:h-5 sm:w-5 text-gold" aria-label="Verificato" />
                  )}
                  {/* Toggle attivo/disattivato */}
                  <button
                    onClick={() => handleToggleStatus(user)}
                    className={`p-1.5 sm:p-2 rounded-lg transition ${isDark ? 'hover:bg-white/10' : 'hover:bg-gray-200'
                      } ${user.is_active ? 'text-gold hover:text-gray-400' : 'text-gray-400 hover:text-gold'}`}
                    title={user.is_active ? 'Disattiva utente' : 'Attiva utente'}
                  >
                    <Power className="h-4 w-4 sm:h-5 sm:w-5" />
                  </button>
                  {/* Cambia ruolo */}
                  <select
                    value={user.role || 'user'}
                    onChange={(e) => changeRole.mutate({ id: user.id, role: e.target.value })}
                    className={`px-2 py-1 border rounded text-xs sm:text-sm focus:outline-none focus:border-gold ${selectBg}`}
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                    <option value="moderator">Moderator</option>
                  </select>
                  {/* Elimina */}
                  <button
                    onClick={() => handleDeleteUser(user.id)}
                    className={`p-1.5 sm:p-2 rounded-lg transition ${isDark ? 'hover:bg-gray-500/20 text-gray-400 hover:text-gray-400' : 'hover:bg-gray-100 text-gray-400 hover:text-gray-400'
                      }`}
                    title="Elimina utente"
                  >
                    <Trash2 className="h-4 w-4 sm:h-5 sm:w-5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Pagination - Mobile First */}
        {total > 20 && (
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4 mt-4 sm:mt-6">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className={`w-full sm:w-auto px-4 py-2 disabled:opacity-50 rounded-lg transition text-sm ${paginationBg}`}
            >
              Precedente
            </button>
            <span className={`text-sm ${textSecondary}`}>
              Pagina {page} di {Math.ceil(total / 20)}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(total / 20)}
              className={`w-full sm:w-auto px-4 py-2 disabled:opacity-50 rounded-lg transition text-sm ${paginationBg}`}
            >
              Successiva
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
