/**
 * CustomerList Component - FULL POLISH VERSION
 *
 * Features:
 * - Theme support (dark/light)
 * - Framer Motion animations
 * - Toast notifications (sonner)
 * - Gold color scheme
 * - React Query data fetching
 * - Mobile-first responsive
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, UserPlus, Filter } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import customersApi, { CustomerListItem, CustomerFilters } from '../../../services/api/customers';

export default function CustomerList() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [filters, setFilters] = useState<CustomerFilters>({
    skip: 0,
    limit: 50,
  });

  // React Query for data fetching with caching
  const { data: customers = [], isLoading, isError } = useQuery<CustomerListItem[]>({
    queryKey: ['customers', filters],
    queryFn: () => customersApi.list(filters),
  });

  if (isError) {
    toast.error('Impossibile caricare i clienti');
  }

  const { data: total = 0 } = useQuery({
    queryKey: ['customers-count', filters],
    queryFn: () => customersApi.count(filters),
  });

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

  const handleFilterChange = (key: keyof CustomerFilters, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value, skip: 0 }));
  };

  const handlePageChange = (newSkip: number) => {
    setFilters((prev) => ({ ...prev, skip: newSkip }));
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      lead: 'bg-gold/20 text-gold dark:bg-gold/30 dark:text-gold',
      prospect: 'bg-gold/10 text-gold dark:bg-gold/20 dark:text-gold',
      active: 'bg-gold/10 text-gold dark:bg-gold/20 dark:text-gold',
      inactive: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
      churned: 'bg-gray-100 text-gray-500 dark:bg-gray-700/30 dark:text-gray-400',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="space-y-3 sm:space-y-4 p-4 sm:p-6">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className={`h-14 sm:h-16 rounded-lg sm:rounded-2xl animate-pulse ${isDark ? 'bg-white/5' : 'bg-gray-200'}`}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6 md:space-y-8">
      {/* Header - Mobile First */}
      <div className="flex flex-col gap-3 sm:gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className={`text-2xl sm:text-3xl lg:text-4xl font-bold ${textPrimary}`}>
            Clienti
          </h1>
          <p className={`text-sm sm:text-base mt-1 sm:mt-2 ${textSecondary}`}>
            Totale: {total} clienti
          </p>
        </div>
        <Link
          to="/admin/crm/customers/new"
          className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold/90 transition flex items-center justify-center gap-2 text-sm sm:text-base font-medium"
        >
          <UserPlus className="h-4 w-4 sm:h-5 sm:w-5" />
          Nuovo Cliente
        </Link>
      </div>

      {/* Filters - Mobile First */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          {/* Search */}
          <div className="relative sm:col-span-2">
            <Search className={`absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 ${textSecondary}`} />
            <input
              type="text"
              placeholder="Cerca clienti..."
              className={`w-full pl-10 sm:pl-12 pr-4 py-2.5 sm:py-3 border rounded-lg focus:outline-none focus:border-gold transition text-sm sm:text-base ${inputBg}`}
              value={filters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </div>

          {/* Status Filter */}
          <select
            className={`px-3 sm:px-4 py-2.5 sm:py-3 border rounded-lg focus:outline-none focus:border-gold text-sm sm:text-base ${inputBg}`}
            value={filters.status || ''}
            onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
          >
            <option value="">Tutti gli stati</option>
            <option value="lead">Lead</option>
            <option value="prospect">Prospect</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="churned">Churned</option>
          </select>

          {/* Type Filter */}
          <select
            className={`px-3 sm:px-4 py-2.5 sm:py-3 border rounded-lg focus:outline-none focus:border-gold text-sm sm:text-base ${inputBg}`}
            value={filters.customer_type || ''}
            onChange={(e) => handleFilterChange('customer_type', e.target.value || undefined)}
          >
            <option value="">Tutti i tipi</option>
            <option value="individual">Privato</option>
            <option value="business">Azienda</option>
            <option value="agency">Agenzia</option>
            <option value="non_profit">No-Profit</option>
          </select>
        </div>
      </div>

      {/* Table - Mobile First with Cards on Mobile */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl overflow-hidden`}>
        {/* Desktop Table */}
        <div className="hidden md:block overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-white/10">
            <thead className={isDark ? 'bg-white/5' : 'bg-gray-50'}>
              <tr>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Nome</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Azienda</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Stato</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Tipo</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>LTV</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Ultimo Contatto</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Azioni</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${isDark ? 'divide-white/10' : 'divide-gray-200'}`}>
              {customers.map((customer, index) => (
                <motion.tr
                  key={customer.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`transition ${itemBg}`}
                >
                  <td className="px-4 lg:px-6 py-3 sm:py-4">
                    <Link to={`/admin/crm/customers/${customer.id}`} className="text-gold hover:text-gold/80 font-medium">
                      {customer.name}
                    </Link>
                    <div className={`text-xs sm:text-sm ${textSecondary}`}>{customer.email}</div>
                  </td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-sm ${textPrimary}`}>{customer.company_name || '-'}</td>
                  <td className="px-4 lg:px-6 py-3 sm:py-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(customer.status)}`}>
                      {customer.status}
                    </span>
                  </td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-sm ${textPrimary}`}>{customer.customer_type}</td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-sm font-medium ${textPrimary}`}>
                    €{customer.lifetime_value.toLocaleString()}
                  </td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-xs sm:text-sm ${textSecondary}`}>
                    {customer.last_contact_date ? new Date(customer.last_contact_date).toLocaleDateString() : 'Mai'}
                  </td>
                  <td className="px-4 lg:px-6 py-3 sm:py-4 text-sm">
                    <Link to={`/admin/crm/customers/${customer.id}`} className="text-gold hover:text-gold/80">
                      Vedi
                    </Link>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile Cards */}
        <div className="md:hidden p-4 space-y-3">
          {customers.map((customer, index) => (
            <motion.div
              key={customer.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`p-4 rounded-lg transition ${itemBg}`}
            >
              <Link to={`/admin/crm/customers/${customer.id}`} className="block">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-semibold text-base ${textPrimary} truncate`}>{customer.name}</h3>
                    <p className={`text-sm ${textSecondary} truncate`}>{customer.email}</p>
                  </div>
                  <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${getStatusBadge(customer.status)}`}>
                    {customer.status}
                  </span>
                </div>
                <div className={`flex items-center justify-between text-sm ${textSecondary}`}>
                  <span>{customer.customer_type}</span>
                  <span className="font-medium text-gold">€{customer.lifetime_value.toLocaleString()}</span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Pagination - Mobile First */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4">
        <div className={`text-sm ${textSecondary}`}>
          Mostrando {filters.skip! + 1} a {Math.min(filters.skip! + filters.limit!, total)} di {total}
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <button
            onClick={() => handlePageChange(Math.max(0, filters.skip! - filters.limit!))}
            disabled={filters.skip === 0}
            className={`flex-1 sm:flex-none px-4 py-2 border rounded-lg disabled:opacity-50 transition text-sm ${
              isDark ? 'border-white/10 hover:bg-white/5' : 'border-gray-200 hover:bg-gray-50'
            } ${textPrimary}`}
          >
            Precedente
          </button>
          <button
            onClick={() => handlePageChange(filters.skip! + filters.limit!)}
            disabled={filters.skip! + filters.limit! >= total}
            className={`flex-1 sm:flex-none px-4 py-2 border rounded-lg disabled:opacity-50 transition text-sm ${
              isDark ? 'border-white/10 hover:bg-white/5' : 'border-gray-200 hover:bg-gray-50'
            } ${textPrimary}`}
          >
            Successivo
          </button>
        </div>
      </div>
    </div>
  );
}
