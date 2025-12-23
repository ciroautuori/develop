/**
 * QuoteList Component - FULL POLISH VERSION
 *
 * Features:
 * - Theme support (dark/light)
 * - Framer Motion animations
 * - Toast notifications
 * - Gold color scheme
 * - React Query data fetching
 * - Mobile-first responsive with cards
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, FileText, Filter } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import quotesApi, { QuoteListItem, QuoteFilters } from '../../../services/api/quotes';

export default function QuoteList() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [filters, setFilters] = useState<QuoteFilters>({
    skip: 0,
    limit: 50,
    is_latest: true,
  });

  // React Query
  const { data: quotes = [], isLoading, isError } = useQuery<QuoteListItem[]>({
    queryKey: ['quotes', filters],
    queryFn: () => quotesApi.list(filters),
  });

  if (isError) {
    toast.error('Impossibile caricare i preventivi');
  }

  const { data: total = 0 } = useQuery({
    queryKey: ['quotes-count', filters],
    queryFn: () => quotesApi.count(filters),
  });

  // Dynamic classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const itemBg = isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100';

  const getStatusBadge = (status: string) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
      sent: 'bg-gold/20 text-gold dark:bg-gold/30 dark:text-gold',
      viewed: 'bg-gold/10 text-gold dark:bg-gold/20 dark:text-gold',
      accepted: 'bg-gold/10 text-gold dark:bg-gold/20 dark:text-gold',
      rejected: 'bg-gray-100 text-gray-500 dark:bg-gray-700/30 dark:text-gray-400',
      expired: 'bg-gold/10 text-gold dark:bg-gold/20 dark:text-gold',
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
      {/* Header */}
      <div className="flex flex-col gap-3 sm:gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className={`text-2xl sm:text-3xl lg:text-4xl font-bold ${textPrimary}`}>Preventivi</h1>
          <p className={`text-sm sm:text-base mt-1 sm:mt-2 ${textSecondary}`}>Totale: {total} preventivi</p>
        </div>
        <Link
          to="/admin/quotes/new"
          className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold/90 transition flex items-center justify-center gap-2 text-sm sm:text-base font-medium"
        >
          <FileText className="h-4 w-4 sm:h-5 sm:w-5" />
          Nuovo Preventivo
        </Link>
      </div>

      {/* Filters */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div className="relative sm:col-span-2">
            <Search className={`absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 ${textSecondary}`} />
            <input
              type="text"
              placeholder="Cerca preventivi..."
              className={`w-full pl-10 sm:pl-12 pr-4 py-2.5 sm:py-3 border rounded-lg focus:outline-none focus:border-gold transition text-sm sm:text-base ${inputBg}`}
              value={filters.search || ''}
              onChange={(e) => setFilters({...filters, search: e.target.value, skip: 0})}
            />
          </div>

          <select
            className={`px-3 sm:px-4 py-2.5 sm:py-3 border rounded-lg focus:outline-none focus:border-gold text-sm sm:text-base ${inputBg}`}
            value={filters.status || ''}
            onChange={(e) => setFilters({...filters, status: e.target.value || undefined, skip: 0})}
          >
            <option value="">Tutti gli stati</option>
            <option value="draft">Bozza</option>
            <option value="sent">Inviato</option>
            <option value="viewed">Visualizzato</option>
            <option value="accepted">Accettato</option>
            <option value="rejected">Rifiutato</option>
            <option value="expired">Scaduto</option>
          </select>

          <select
            className={`px-3 sm:px-4 py-2.5 sm:py-3 border rounded-lg focus:outline-none focus:border-gold text-sm sm:text-base ${inputBg}`}
            value={filters.is_latest === undefined ? '' : filters.is_latest.toString()}
            onChange={(e) => setFilters({...filters, is_latest: e.target.value === '' ? undefined : e.target.value === 'true', skip: 0})}
          >
            <option value="">Tutte le versioni</option>
            <option value="true">Solo ultima versione</option>
            <option value="false">Tutte le versioni</option>
          </select>
        </div>
      </div>

      {/* Table/Cards */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl overflow-hidden`}>
        {/* Desktop Table */}
        <div className="hidden md:block overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-white/10">
            <thead className={isDark ? 'bg-white/5' : 'bg-gray-50'}>
              <tr>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>N. Prev.</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Titolo</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Stato</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Versione</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Totale</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Valido Fino</th>
                <th className={`px-4 lg:px-6 py-3 text-left text-xs font-medium uppercase ${textSecondary}`}>Azioni</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${isDark ? 'divide-white/10' : 'divide-gray-200'}`}>
              {quotes.map((quote, index) => (
                <motion.tr
                  key={quote.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`transition ${itemBg}`}
                >
                  <td className="px-4 lg:px-6 py-3 sm:py-4">
                    <Link to={`/admin/quotes/${quote.id}`} className="text-gold hover:text-gold/80 font-medium">
                      {quote.quote_number}
                    </Link>
                  </td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-sm ${textPrimary}`}>{quote.title}</td>
                  <td className="px-4 lg:px-6 py-3 sm:py-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(quote.status)}`}>
                      {quote.status}
                    </span>
                  </td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-sm ${textPrimary}`}>
                    v{quote.version}
                    {quote.is_latest && <span className="ml-2 text-xs text-gold dark:text-gold">ultima</span>}
                  </td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-sm font-medium ${textPrimary}`}>
                    {quote.currency} {quote.total.toLocaleString()}
                  </td>
                  <td className={`px-4 lg:px-6 py-3 sm:py-4 text-xs sm:text-sm ${textSecondary}`}>
                    {new Date(quote.valid_until).toLocaleDateString()}
                  </td>
                  <td className="px-4 lg:px-6 py-3 sm:py-4 text-sm space-x-2">
                    <Link to={`/admin/quotes/${quote.id}`} className="text-gold hover:text-gold/80">Vedi</Link>
                    {quote.status === 'draft' && (
                      <Link to={`/admin/quotes/${quote.id}/edit`} className={textSecondary + ' hover:text-gold'}>Modifica</Link>
                    )}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile Cards */}
        <div className="md:hidden p-4 space-y-3">
          {quotes.map((quote, index) => (
            <motion.div
              key={quote.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`p-4 rounded-lg transition ${itemBg}`}
            >
              <Link to={`/admin/quotes/${quote.id}`} className="block">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-semibold text-sm ${textPrimary}`}>{quote.quote_number}</h3>
                    <p className={`text-sm ${textSecondary} truncate`}>{quote.title}</p>
                  </div>
                  <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${getStatusBadge(quote.status)}`}>
                    {quote.status}
                  </span>
                </div>
                <div className={`flex items-center justify-between text-sm`}>
                  <span className={textSecondary}>v{quote.version}</span>
                  <span className="font-medium text-gold">{quote.currency} {quote.total.toLocaleString()}</span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Pagination */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4">
        <div className={`text-sm ${textSecondary}`}>
          Mostrando {filters.skip! + 1} a {Math.min(filters.skip! + filters.limit!, total)} di {total}
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <button
            onClick={() => setFilters({...filters, skip: Math.max(0, filters.skip! - filters.limit!)})}
            disabled={filters.skip === 0}
            className={`flex-1 sm:flex-none px-4 py-2 border rounded-lg disabled:opacity-50 transition text-sm ${
              isDark ? 'border-white/10 hover:bg-white/5' : 'border-gray-200 hover:bg-gray-50'
            } ${textPrimary}`}
          >
            Precedente
          </button>
          <button
            onClick={() => setFilters({...filters, skip: filters.skip! + filters.limit!})}
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
