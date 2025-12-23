/**
 * QuoteForm Component - FULL POLISH VERSION
 * Integrated with LineItemsEditor
 *
 * Features:
 * - Theme support
 * - Toast notifications
 * - Gold color scheme
 * - React Query
 * - Real-time totals calculation
 * - Mobile-first responsive
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams, Link } from 'react-router-dom';
import { ArrowLeft, Save, Plus, X, Trash2 } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import quotesApi, { QuoteCreate, QuoteLineItem } from '../../../services/api/quotes';
import customersApi from '../../../services/api/customers';

export default function QuoteForm() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    title: '',
    customer_id: parseInt(searchParams.get('customer_id') || '0') || 0,
    valid_until: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    tax_rate: 22,
    discount_percentage: 0,
    payment_terms_days: 30,
    notes_to_customer: '',
  });

  const [lineItems, setLineItems] = useState<Omit<QuoteLineItem, 'id' | 'quote_id' | 'discount_amount' | 'subtotal'>[]>([
    { name: '', description: '', quantity: 1, unit_price: 0, discount_percentage: 0, position: 0 }
  ]);

  // Dynamic classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400';
  const itemBg = isDark ? 'bg-white/5' : 'bg-gray-50';
  const labelClass = `block text-sm font-medium mb-1.5 ${textPrimary}`;
  const inputClass = `w-full p-2.5 sm:p-3 border rounded-lg focus:outline-none focus:border-gold transition text-sm ${inputBg}`;

  // Load customers
  const { data: customers = [] } = useQuery({
    queryKey: ['customers-for-quote'],
    queryFn: () => customersApi.list({ limit: 100 }),
  });

  // Load quote for edit
  const { data: existingQuote } = useQuery({
    queryKey: ['quote', id],
    queryFn: () => quotesApi.get(parseInt(id!)),
    enabled: isEdit,
  });

  // Update form when quote data loads
  useEffect(() => {
    if (existingQuote) {
      setFormData({
        title: existingQuote.title,
        customer_id: existingQuote.customer_id,
        valid_until: existingQuote.valid_until,
        tax_rate: parseFloat(existingQuote.tax_rate.toString()),
        discount_percentage: parseFloat(existingQuote.discount_percentage.toString()),
        payment_terms_days: existingQuote.payment_terms_days,
        notes_to_customer: existingQuote.notes_to_customer || '',
      });
      setLineItems(existingQuote.line_items.map((item: any) => ({
        name: item.name,
        description: item.description,
        quantity: parseFloat(item.quantity.toString()),
        unit_price: parseFloat(item.unit_price.toString()),
        discount_percentage: parseFloat((item.discount_percentage || 0).toString()),
        position: item.position || 0,
      })));
    }
  }, [existingQuote]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: QuoteCreate) => quotesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      toast.success('Quote created successfully');
      navigate('/admin/quotes');
    },
    onError: (error: any) => toast.error(error.response?.data?.detail || 'Failed to create quote'),
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => quotesApi.update(parseInt(id!), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quote', id] });
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      toast.success('Quote updated successfully');
      navigate(`/admin/quotes/${id}`);
    },
    onError: (error: any) => toast.error(error.response?.data?.detail || 'Failed to update quote'),
  });

  const addLineItem = () => {
    setLineItems([...lineItems, { name: '', description: '', quantity: 1, unit_price: 0, discount_percentage: 0, position: lineItems.length }]);
  };

  const removeLineItem = (index: number) => {
    if (lineItems.length === 1) {
      toast.error('At least one line item is required');
      return;
    }
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const updateLineItem = (index: number, field: string, value: any) => {
    const updated = [...lineItems];
    updated[index] = { ...updated[index], [field]: value };
    setLineItems(updated);
  };

  const calculateSubtotal = () => {
    return lineItems.reduce((sum, item) => {
      const base = item.quantity * item.unit_price;
      const discount = base * ((item.discount_percentage || 0) / 100);
      return sum + (base - discount);
    }, 0);
  };

  const calculateTotal = () => {
    const subtotal = calculateSubtotal();
    const quoteDiscount = subtotal * (formData.discount_percentage / 100);
    const afterDiscount = subtotal - quoteDiscount;
    const tax = afterDiscount * (formData.tax_rate / 100);
    return afterDiscount + tax;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim()) {
      toast.error('Title is required');
      return;
    }
    if (formData.customer_id === 0) {
      toast.error('Please select a customer');
      return;
    }

    const validItems = lineItems.filter(item => item.name.trim() !== '');
    if (validItems.length === 0) {
      toast.error('At least one line item is required');
      return;
    }

    const data: QuoteCreate = {
      ...formData,
      line_items: validItems,
    };

    if (isEdit) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-6xl mx-auto space-y-4 sm:space-y-6"
    >
      {/* Header */}
      <div>
        <Link
          to="/admin/quotes"
          className={`flex items-center gap-2 text-sm ${textSecondary} hover:text-gold transition mb-3 sm:mb-4`}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Quotes
        </Link>
        <h1 className={`text-2xl sm:text-3xl lg:text-4xl font-bold ${textPrimary}`}>
          {isEdit ? 'Edit' : 'Create'} Quote
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
        {/* Basic Info */}
        <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
          <h2 className={`text-lg sm:text-xl font-semibold mb-4 ${textPrimary}`}>Quote Information</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Customer *</label>
              <select
                value={formData.customer_id}
                onChange={(e) => setFormData({...formData, customer_id: parseInt(e.target.value)})}
                required
                className={inputClass}
              >
                <option value="0">Select Customer</option>
                {customers.map(c => (
                  <option key={c.id} value={c.id}>{c.name} ({c.email})</option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                required
                className={inputClass}
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
            <div>
              <label className={labelClass}>Valid Until *</label>
              <input
                type="date"
                value={formData.valid_until}
                onChange={(e) => setFormData({...formData, valid_until: e.target.value})}
                required
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Payment Terms (days)</label>
              <input
                type="number"
                value={formData.payment_terms_days}
                onChange={(e) => setFormData({...formData, payment_terms_days: parseInt(e.target.value)})}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Tax Rate (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.tax_rate}
                onChange={(e) => setFormData({...formData, tax_rate: parseFloat(e.target.value)})}
                className={inputClass}
              />
            </div>
          </div>
        </div>

        {/* Line Items */}
        <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
            <h2 className={`text-lg sm:text-xl font-semibold ${textPrimary}`}>Line Items</h2>
            <button
              type="button"
              onClick={addLineItem}
              className="px-4 py-2 bg-gold text-black rounded-lg hover:bg-gold/90 transition flex items-center justify-center gap-2 text-sm font-medium"
            >
              <Plus className="h-4 w-4" />
              Add Item
            </button>
          </div>
          <div className="space-y-3">
            {lineItems.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 sm:p-4 rounded-lg ${itemBg}`}
              >
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-2">
                  <input
                    type="text"
                    placeholder="Item name *"
                    value={item.name}
                    onChange={(e) => updateLineItem(index, 'name', e.target.value)}
                    className={`sm:col-span-3 p-2 border rounded text-sm ${inputBg}`}
                  />
                  <input
                    type="text"
                    placeholder="Description"
                    value={item.description}
                    onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                    className={`sm:col-span-3 p-2 border rounded text-sm ${inputBg}`}
                  />
                  <input
                    type="number"
                    placeholder="Qty"
                    value={item.quantity}
                    onChange={(e) => updateLineItem(index, 'quantity', parseFloat(e.target.value) || 1)}
                    className={`sm:col-span-2 p-2 border rounded text-sm ${inputBg}`}
                  />
                  <input
                    type="number"
                    placeholder="Price"
                    value={item.unit_price}
                    onChange={(e) => updateLineItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
                    className={`sm:col-span-2 p-2 border rounded text-sm ${inputBg}`}
                  />
                  <div className={`sm:col-span-1 flex items-center justify-center text-sm font-medium ${textPrimary}`}>
                    €{(item.quantity * item.unit_price).toFixed(2)}
                  </div>
                  <button
                    type="button"
                    onClick={() => removeLineItem(index)}
                    className="sm:col-span-1 text-gray-500 dark:text-gray-400 hover:text-gray-500 dark:hover:text-gray-400 flex items-center justify-center"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Totals */}
        <div className={`${cardBg} rounded-2xl sm:rounded-3xl p-4 sm:p-6`}>
          <div className="max-w-md ml-auto space-y-2">
            <div className={`flex justify-between text-sm sm:text-base ${textPrimary}`}>
              <span>Subtotal:</span>
              <span>€{calculateSubtotal().toFixed(2)}</span>
            </div>
            <div className={`flex justify-between text-sm sm:text-base ${textPrimary}`}>
              <span>Tax ({formData.tax_rate}%):</span>
              <span>€{(calculateSubtotal() * formData.tax_rate / 100).toFixed(2)}</span>
            </div>
            <div className={`flex justify-between text-lg sm:text-xl font-bold border-t pt-2 ${textPrimary}`}>
              <span>Total:</span>
              <span className="text-gold">€{calculateTotal().toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 sm:flex-none px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold/90 transition disabled:opacity-50 flex items-center justify-center gap-2 font-medium"
          >
            <Save className="h-4 w-4 sm:h-5 sm:w-5" />
            {isLoading ? 'Saving...' : isEdit ? 'Update' : 'Create'} Quote
          </button>
          <Link
            to="/admin/quotes"
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
