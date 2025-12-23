/**
 * User Table Component - Tabella utenti con actions
 */
import { Edit, Trash2, CheckCircle, XCircle, Key } from 'lucide-react';
import { useActivateUser, useDeactivateUser, useDeleteUser, useChangeUserRole } from '../hooks/useUsers';
import { Button } from '../../../shared/components/ui/button';

interface UserTableProps {
  users: any[];
}

export function UserTable({ users }: UserTableProps) {
  const activateUser = useActivateUser();
  const deactivateUser = useDeactivateUser();
  const deleteUser = useDeleteUser();
  const changeRole = useChangeUserRole();

  const handleActivate = (id: number) => {
    activateUser.mutate(id);
  };

  const handleDeactivate = (id: number) => {
    deactivateUser.mutate(id);
  };

  const handleDelete = (id: number, email: string) => {
    if (confirm(`Sei sicuro di voler eliminare l'utente ${email}?`)) {
      deleteUser.mutate(id);
    }
  };

  const handleChangeRole = (id: number, currentRole: string) => {
    const newRole = prompt(`Nuovo ruolo (user/premium/admin):`, currentRole);
    if (newRole && ['user', 'premium', 'admin'].includes(newRole)) {
      changeRole.mutate({ id, role: newRole });
    }
  };

  const getRoleBadge = (role: string) => {
    const colors = {
      admin: 'bg-gray-100 text-gray-500 dark:bg-white/10/20 dark:text-gray-400',
      premium: 'bg-gold/10 text-gold dark:bg-gold/20/20 dark:text-gold',
      user: 'bg-gray-100 text-gray-700 dark:bg-[#0A0A0A]/20 dark:text-gray-400'
    };
    return colors[role as keyof typeof colors] || colors.user;
  };

  if (!users || users.length === 0) {
    return (
      <div className="py-12 text-center text-neutral-500">
        Nessun utente trovato
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="border-b border-neutral-200 dark:border-neutral-800">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-medium text-neutral-600 dark:text-neutral-400">
              Utente
            </th>
            <th className="px-6 py-3 text-left text-sm font-medium text-neutral-600 dark:text-neutral-400">
              Email
            </th>
            <th className="px-6 py-3 text-left text-sm font-medium text-neutral-600 dark:text-neutral-400">
              Ruolo
            </th>
            <th className="px-6 py-3 text-left text-sm font-medium text-neutral-600 dark:text-neutral-400">
              Stato
            </th>
            <th className="px-6 py-3 text-left text-sm font-medium text-neutral-600 dark:text-neutral-400">
              Registrato
            </th>
            <th className="px-6 py-3 text-right text-sm font-medium text-neutral-600 dark:text-neutral-400">
              Azioni
            </th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="border-b border-neutral-100 dark:border-neutral-800/50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gold/20 text-gold dark:bg-gold/20 dark:text-gold">
                    {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-medium text-neutral-900 dark:text-neutral-100">
                      {user.full_name || 'N/A'}
                    </div>
                    <div className="text-sm text-neutral-500">ID: {user.id}</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-neutral-900 dark:text-neutral-100">{user.email}</div>
                {user.is_verified && (
                  <div className="mt-1 text-xs text-gold">✓ Verificato</div>
                )}
              </td>
              <td className="px-6 py-4">
                <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${getRoleBadge(user.role)}`}>
                  {user.role.toUpperCase()}
                </span>
              </td>
              <td className="px-6 py-4">
                <span
                  className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                    user.is_active
                      ? 'bg-gold/10 text-gold dark:bg-gold/20 dark:text-gold'
                      : 'bg-gray-100 text-gray-700 dark:bg-[#0A0A0A]/20 dark:text-gray-400'
                  }`}
                >
                  {user.is_active ? 'Attivo' : 'Disattivo'}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-400">
                {new Date(user.created_at).toLocaleDateString('it-IT')}
              </td>
              <td className="px-6 py-4 text-right">
                <div className="flex justify-end gap-2">
                  {user.is_active ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeactivate(user.id)}
                      title="Disattiva"
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleActivate(user.id)}
                      title="Attiva"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleChangeRole(user.id, user.role)}
                    title="Cambia ruolo"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    title="Reset password"
                  >
                    <Key className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(user.id, user.email)}
                    title="Elimina"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
