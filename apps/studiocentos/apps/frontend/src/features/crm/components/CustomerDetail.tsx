/**
 * CustomerDetail Component - FULL POLISH VERSION
 *
 * Features:
 * - Theme support (dark/light)
 * - Framer Motion animations
 * - Toast notifications
 * - Gold color scheme
 * - React Query with mutations
 * - Mobile-first responsive
 */

import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, FileText, TrendingUp } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import customersApi from '../../../services/api/customers';

export default function CustomerDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [activeTab, setActiveTab] = useState<'info' | 'notes' | 'interactions'>('info');
  const [newNote, setNewNote] = useState('');
  const [newInteraction, setNewInteraction] = useState({
    interaction_type: 'email',
    subject: '',
    description: '',
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
  const itemBg = isDark ? 'bg-white/5' : 'bg-gray-50';

  // React Query for customer data
  const { data: customer, isLoading } = useQuery({
    queryKey: ['customer', id],
    queryFn: () => customersApi.get(parseInt(id!)),
    enabled: !!id,
  });

  const { data: notes = [] } = useQuery({
    queryKey: ['customer-notes', id],
    queryFn: () => customersApi.getNotes(parseInt(id!)),
    enabled: !!id,
  });

  const { data: interactions = [] } = useQuery({
    queryKey: ['customer-interactions', id],
    queryFn: () => customersApi.getInteractions(parseInt(id!)),
    enabled: !!id,
  });

  // Mutations with optimistic updates
  const addNoteMutation = useMutation({
    mutationFn: (note: string) => customersApi.addNote(parseInt(id!), note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-notes', id] });
      setNewNote('');
      toast.success('Note added successfully');
    },
    onError: () => toast.error('Failed to add note'),
  });

  const logInteractionMutation = useMutation({
    mutationFn: (data: any) => customersApi.logInteraction(parseInt(id!), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-interactions', id] });
      setNewInteraction({ interaction_type: 'email', subject: '', description: '' });
      toast.success('Interaction logged successfully');
    },
    onError: () => toast.error('Failed to log interaction'),
  });

  const handleAddNote = () => {
    if (!newNote.trim()) {
      toast.error('Note cannot be empty');
      return;
    }
    addNoteMutation.mutate(newNote);
  };

  const handleLogInteraction = () => {
    if (!newInteraction.subject.trim()) {
      toast.error('Subject is required');
      return;
    }
    logInteractionMutation.mutate({
      ...newInteraction,
      completed_at: new Date().toISOString(),
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold"></div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="p-4 sm:p-6">
        <div className={`${cardBg} rounded-2xl p-6 sm:p-8 text-center`}>
          <p className={textSecondary}>Customer not found</p>
          <Link to="/admin/crm/customers" className="mt-4 inline-block text-gold hover:text-gold/80">
            Back to Customers
          </Link>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4 sm:space-y-6"
    >
      {/* Header - Mobile First */}
      <div className="flex flex-col gap-3 sm:gap-4">
        <Link
          to="/admin/crm/customers"
          className={`flex items-center gap-2 text-sm ${textSecondary} hover:text-gold transition`}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Customers
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4">
          <div className="flex-1 min-w-0">
            <h1 className={`text-2xl sm:text-3xl lg:text-4xl font-bold ${textPrimary} truncate`}>
              {customer.name}
            </h1>
            <p className={`text-sm sm:text-base ${textSecondary} mt-1`}>{customer.email}</p>
          </div>
          <div className="flex gap-2">
            <Link
              to={`/admin/crm/customers/${id}/edit`}
              className="flex-1 sm:flex-none px-4 sm:px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold/90 transition flex items-center justify-center gap-2 text-sm sm:text-base font-medium"
            >
              <Edit className="h-4 w-4 sm:h-5 sm:w-5" />
              Edit
            </Link>
            <Link
              to={`/admin/quotes/new?customer_id=${id}`}
              className="flex-1 sm:flex-none px-4 sm:px-6 py-2.5 sm:py-3 bg-gold text-white rounded-lg hover:bg-gold/90 transition flex items-center justify-center gap-2 text-sm sm:text-base font-medium"
            >
              <FileText className="h-4 w-4 sm:h-5 sm:w-5" />
              New Quote
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Cards - Mobile First Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        {[
          { label: 'Status', value: customer.status, icon: null },
          { label: 'Lifetime Value', value: `€${customer.lifetime_value.toLocaleString()}`, icon: TrendingUp },
          { label: 'Total Spent', value: `€${customer.total_spent.toLocaleString()}`, icon: null },
          { label: 'Projects', value: customer.completed_projects, icon: null },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`${cardBg} p-3 sm:p-4 lg:p-6 rounded-lg sm:rounded-2xl`}
          >
            <div className={`text-xs sm:text-sm ${textSecondary} mb-1 sm:mb-2`}>{stat.label}</div>
            <div className={`text-lg sm:text-xl lg:text-2xl font-bold ${textPrimary} capitalize flex items-center gap-2`}>
              {stat.value}
              {stat.icon && <stat.icon className="h-5 w-5 text-gold" />}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Tabs - Mobile First */}
      <div className={`${cardBg} rounded-2xl sm:rounded-3xl overflow-hidden`}>
        <div className="border-b border-gray-200 dark:border-white/10">
          <nav className="flex overflow-x-auto">
            {[
              { id: 'info', label: 'Information' },
              { id: 'notes', label: 'Notes' },
              { id: 'interactions', label: 'Interactions' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 sm:px-6 py-3 sm:py-4 font-medium text-sm sm:text-base whitespace-nowrap transition ${
                  activeTab === tab.id
                    ? 'border-b-2 border-gold text-gold'
                    : `${textSecondary} hover:text-gold`
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4 sm:p-6">
          {/* Info Tab */}
          {activeTab === 'info' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              {[
                { label: 'Email', value: customer.email },
                { label: 'Phone', value: customer.phone || '-' },
                { label: 'Company', value: customer.company_name || '-' },
                { label: 'Type', value: customer.customer_type },
                { label: 'Source', value: customer.source },
                {
                  label: 'Last Contact',
                  value: customer.last_contact_date
                    ? new Date(customer.last_contact_date).toLocaleDateString()
                    : 'Never',
                },
              ].map((field) => (
                <div key={field.label}>
                  <strong className={`text-sm ${textSecondary}`}>{field.label}:</strong>
                  <div className={`mt-1 ${textPrimary}`}>{field.value}</div>
                </div>
              ))}
            </div>
          )}

          {/* Notes Tab */}
          {activeTab === 'notes' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-2">
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Add a note..."
                  className={`flex-1 p-3 border rounded-lg focus:outline-none focus:border-gold text-sm sm:text-base ${inputBg}`}
                  rows={3}
                />
                <button
                  onClick={handleAddNote}
                  disabled={addNoteMutation.isPending}
                  className="px-4 sm:px-6 py-2.5 bg-gold text-black rounded-lg hover:bg-gold/90 transition disabled:opacity-50 font-medium whitespace-nowrap"
                >
                  {addNoteMutation.isPending ? 'Adding...' : 'Add'}
                </button>
              </div>
              <div className="space-y-2 sm:space-y-3">
                {notes.map((note, index) => (
                  <motion.div
                    key={note.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`p-3 sm:p-4 rounded-lg ${itemBg}`}
                  >
                    <p className={`text-sm sm:text-base ${textPrimary}`}>{note.note}</p>
                    <p className={`text-xs sm:text-sm ${textSecondary} mt-2`}>
                      {new Date(note.created_at).toLocaleString()}
                    </p>
                  </motion.div>
                ))}
                {notes.length === 0 && (
                  <p className={`text-center py-8 text-sm ${textSecondary}`}>No notes yet</p>
                )}
              </div>
            </div>
          )}

          {/* Interactions Tab */}
          {activeTab === 'interactions' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">
                <select
                  value={newInteraction.interaction_type}
                  onChange={(e) =>
                    setNewInteraction({ ...newInteraction, interaction_type: e.target.value })
                  }
                  className={`p-2.5 border rounded-lg focus:outline-none focus:border-gold text-sm ${inputBg}`}
                >
                  <option value="email">Email</option>
                  <option value="call">Call</option>
                  <option value="meeting">Meeting</option>
                  <option value="demo">Demo</option>
                </select>
                <input
                  type="text"
                  value={newInteraction.subject}
                  onChange={(e) => setNewInteraction({ ...newInteraction, subject: e.target.value })}
                  placeholder="Subject"
                  className={`p-2.5 border rounded-lg focus:outline-none focus:border-gold text-sm ${inputBg}`}
                />
                <button
                  onClick={handleLogInteraction}
                  disabled={logInteractionMutation.isPending}
                  className="px-4 py-2.5 bg-gold text-black rounded-lg hover:bg-gold/90 transition disabled:opacity-50 font-medium"
                >
                  {logInteractionMutation.isPending ? 'Logging...' : 'Log'}
                </button>
              </div>
              <div className="space-y-2 sm:space-y-3">
                {interactions.map((int, index) => (
                  <motion.div
                    key={int.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`p-3 sm:p-4 rounded-lg ${itemBg}`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 sm:gap-2 mb-2">
                      <strong className={`capitalize ${textPrimary}`}>{int.interaction_type}</strong>
                      <span className={`text-xs sm:text-sm ${textSecondary}`}>
                        {new Date(int.created_at).toLocaleString()}
                      </span>
                    </div>
                    {int.subject && <p className={`font-medium ${textPrimary} mb-1`}>{int.subject}</p>}
                    {int.description && <p className={`text-sm ${textSecondary}`}>{int.description}</p>}
                  </motion.div>
                ))}
                {interactions.length === 0 && (
                  <p className={`text-center py-8 text-sm ${textSecondary}`}>No interactions yet</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
