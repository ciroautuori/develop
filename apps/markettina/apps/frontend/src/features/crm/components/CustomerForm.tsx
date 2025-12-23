/**
 * CustomerForm Component - FULL POLISH VERSION
 *
 * Features:
 * - Theme support
 * - Toast notifications
 * - Gold color scheme
 * - React Query mutations
 * - Mobile-first responsive
 * - Form validation
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { ArrowLeft, Save, X } from 'lucide-react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import customersApi, { CustomerCreate } from '../../../services/api/customers';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';

export default function CustomerForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const isEdit = !!id;

  const [formData, setFormData] = useState<Partial<CustomerCreate>>({
    name: '',
    email: '',
    phone: '',
    company_name: '',
    status: 'lead',
    customer_type: 'individual',
    source: 'website',
    marketing_consent: false,
  });

  // Dynamic classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400';
  const labelClass = `block text-sm font-medium mb-1.5 sm:mb-2 ${textPrimary}`;
  const inputClass = `w-full p-2.5 sm:p-3 border rounded-lg focus:outline-none focus:border-gold transition text-sm sm:text-base ${inputBg}`;

  // Load customer for edit
  const { data: existingCustomer } = useQuery({
    queryKey: ['customer', id],
    queryFn: () => customersApi.get(parseInt(id!)),
    enabled: isEdit,
  });

  // Update form when customer data loads
  useEffect(() => {
    if (existingCustomer) {
      setFormData({
        name: existingCustomer.name,
        email: existingCustomer.email,
        phone: existingCustomer.phone,
        company_name: existingCustomer.company_name,
        company_vat_id: existingCustomer.company_vat_id,
        company_website: existingCustomer.company_website,
        status: existingCustomer.status,
        customer_type: existingCustomer.customer_type,
        source: existingCustomer.source,
        marketing_consent: (existingCustomer as any).marketing_consent ?? false,
      });
    }
  }, [existingCustomer]);

  // Create/Update mutations
  const createMutation = useMutation({
    mutationFn: (data: CustomerCreate) => customersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      toast.success('Customer created successfully');
      navigate('/admin/crm/customers');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create customer');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<CustomerCreate>) => customersApi.update(parseInt(id!), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer', id] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      toast.success('Customer updated successfully');
      navigate(`/admin/crm/customers/${id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update customer');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name?.trim() || !formData.email?.trim()) {
      toast.error('Name and email are required');
      return;
    }

    if (isEdit) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData as CustomerCreate);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('max-w-4xl mx-auto', SPACING.padding.full, SPACING.lg)}
    >
      {/* Header */}
      <div>
        <Link
          to={isEdit ? `/admin/crm/customers/${id}` : '/admin/crm/customers'}
          className={`flex items-center gap-2 text-sm ${textSecondary} hover:text-gold transition mb-3 sm:mb-4`}
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Link>
        <h1 className={`text-2xl sm:text-3xl lg:text-4xl font-bold ${textPrimary}`}>
          {isEdit ? 'Edit' : 'Create'} Customer
        </h1>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6 lg:p-8 space-y-6`}>
        {/* Basic Info */}
        <div>
          <h2 className={`text-lg sm:text-xl font-semibold mb-4 ${textPrimary}`}>Basic Information</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <label className={labelClass}>Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Email *</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className={inputClass}
              />
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div>
          <h2 className={`text-lg sm:text-xl font-semibold mb-4 ${textPrimary}`}>Contact Details</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <label className={labelClass}>Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Company Name</label>
              <input
                type="text"
                name="company_name"
                value={formData.company_name}
                onChange={handleChange}
                className={inputClass}
              />
            </div>
          </div>
        </div>

        {/* CRM Fields */}
        <div>
          <h2 className={`text-lg sm:text-xl font-semibold mb-4 ${textPrimary}`}>CRM Details</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
            <div>
              <label className={labelClass}>Status</label>
              <select name="status" value={formData.status} onChange={handleChange} className={inputClass}>
                <option value="lead">Lead</option>
                <option value="prospect">Prospect</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="churned">Churned</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Type</label>
              <select
                name="customer_type"
                value={formData.customer_type}
                onChange={handleChange}
                className={inputClass}
              >
                <option value="individual">Individual</option>
                <option value="business">Business</option>
                <option value="agency">Agency</option>
                <option value="non_profit">Non-Profit</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Source</label>
              <select name="source" value={formData.source} onChange={handleChange} className={inputClass}>
                <option value="website">Website</option>
                <option value="referral">Referral</option>
                <option value="advertising">Advertising</option>
                <option value="event">Event</option>
                <option value="direct">Direct</option>
                <option value="organic">Organic</option>
              </select>
            </div>
          </div>
        </div>

        {/* GDPR */}
        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            name="marketing_consent"
            checked={formData.marketing_consent}
            onChange={handleChange}
            className="mt-1"
          />
          <label className={`text-sm ${textPrimary}`}>
            Customer consents to marketing communications (GDPR compliance)
          </label>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 pt-4">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 sm:flex-none px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold/90 transition disabled:opacity-50 flex items-center justify-center gap-2 font-medium"
          >
            <Save className="h-4 w-4 sm:h-5 sm:w-5" />
            {isLoading ? 'Saving...' : isEdit ? 'Update' : 'Create'} Customer
          </button>
          <Link
            to={isEdit ? `/admin/crm/customers/${id}` : '/admin/crm/customers'}
            className="flex-1 sm:flex-none px-6 py-2.5 sm:py-3 border border-gray-300 dark:border-white/10 rounded-lg hover:bg-gray-50 dark:hover:bg-white/5 transition flex items-center justify-center gap-2 font-medium"
          >
            <X className="h-4 w-4 sm:h-5 sm:w-5" />
            Cancel
          </Link>
        </div>
      </form>
    </motion.div>
  );
}
