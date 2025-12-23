/**
 * Quote Modal - CRUD Form per gestione preventivi
 * Supporta creazione, modifica e visualizzazione preventivi con line items dinamici
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Loader2, Plus, Trash2, AlertCircle, Euro, Calendar, FileText } from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';

interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
}

interface QuoteFormData {
  title: string;
  customer_id: number | null;
  line_items: LineItem[];
  tax_rate: number;
  discount_amount: number;
  valid_until: string;
  notes?: string;
}

interface QuoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  quote?: any;
  onSuccess: () => void;
  mode: 'create' | 'edit' | 'view';
  customers: any[];
}

export function QuoteModal({ isOpen, onClose, quote, onSuccess, mode, customers }: QuoteModalProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const getDefaultValidUntil = () => {
    const date = new Date();
    date.setDate(date.getDate() + 30); // Default 30 giorni
    return date.toISOString().split('T')[0];
  };

  const [formData, setFormData] = useState<QuoteFormData>({
    title: '',
    customer_id: null,
    line_items: [{ description: '', quantity: 1, unit_price: 0 }],
    tax_rate: 22, // IVA default 22%
    discount_amount: 0,
    valid_until: getDefaultValidUntil(),
    notes: '',
  });

  useEffect(() => {
    if (quote && (mode === 'edit' || mode === 'view')) {
      setFormData({
        title: quote.title || '',
        customer_id: quote.customer_id || null,
        line_items: quote.line_items?.length > 0 ? quote.line_items : [{ description: '', quantity: 1, unit_price: 0 }],
        tax_rate: quote.tax_rate || 22,
        discount_amount: quote.discount_amount || 0,
        valid_until: quote.valid_until?.split('T')[0] || getDefaultValidUntil(),
        notes: quote.notes || '',
      });
    } else {
      setFormData({
        title: '',
        customer_id: null,
        line_items: [{ description: '', quantity: 1, unit_price: 0 }],
        tax_rate: 22,
        discount_amount: 0,
        valid_until: getDefaultValidUntil(),
        notes: '',
      });
    }
    setErrors({});
  }, [quote, mode, isOpen]);

  // Theme classes - UNIFIED DESIGN SYSTEM
  const modalBg = isDark
    ? 'bg-gradient-to-br from-[#0a0a0a] to-[#0a0a0a] border border-white/10'
    : 'bg-white border border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const labelText = isDark ? 'text-gray-300' : 'text-gray-700';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-500';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-300 text-gray-900';

  const calculateSubtotal = (): number => {
    return formData.line_items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  };

  const calculateTax = (): number => {
    return (calculateSubtotal() - formData.discount_amount) * (formData.tax_rate / 100);
  };

  const calculateTotal = (): number => {
    return calculateSubtotal() - formData.discount_amount + calculateTax();
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Titolo obbligatorio';
    }

    if (!formData.customer_id) {
      newErrors.customer_id = 'Seleziona un cliente';
    }

    if (formData.line_items.length === 0) {
      newErrors.line_items = 'Aggiungi almeno un articolo';
    } else {
      const invalidItems = formData.line_items.some(item => !item.description.trim() || item.unit_price <= 0);
      if (invalidItems) {
        newErrors.line_items = 'Completa tutti gli articoli (descrizione e prezzo > 0)';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (mode === 'view') {
      onClose();
      return;
    }

    if (!validateForm()) {
      toast.error('Compila i campi obbligatori');
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('admin_token');
      const url = mode === 'edit'
        ? `/api/v1/admin/quotes/${quote.id}`
        : '/api/v1/admin/quotes';

      const response = await fetch(url, {
        method: mode === 'edit' ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Errore nel salvataggio');
      }

      toast.success(mode === 'edit' ? 'Preventivo aggiornato!' : 'Preventivo creato!');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving quote:', error);
      toast.error(error instanceof Error ? error.message : 'Errore nel salvataggio');
    } finally {
      setLoading(false);
    }
  };

  const addLineItem = () => {
    setFormData(prev => ({
      ...prev,
      line_items: [...prev.line_items, { description: '', quantity: 1, unit_price: 0 }],
    }));
  };

  const removeLineItem = (index: number) => {
    if (formData.line_items.length === 1) {
      toast.error('Deve esserci almeno un articolo');
      return;
    }
    setFormData(prev => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index),
    }));
  };

  const updateLineItem = (index: number, field: keyof LineItem, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      line_items: prev.line_items.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      ),
    }));
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div
              className={cn('w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl', modalBg)}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="sticky top-0 z-10 flex items-center justify-between p-4 sm:p-6 border-b border-white/10 bg-inherit backdrop-blur-sm">
                <div>
                  <h2 className={`text-lg sm:text-xl md:text-2xl font-bold ${textPrimary}`}>
                    {mode === 'create' ? '➕ Nuovo Preventivo' : mode === 'edit' ? '✏️ Modifica Preventivo' : '👁️ Dettagli Preventivo'}
                  </h2>
                  <p className={`text-xs sm:text-sm ${textSecondary}`}>
                    {mode === 'create' ? 'Crea un nuovo preventivo per un cliente' : mode === 'edit' ? 'Aggiorna il preventivo' : 'Visualizza dettagli preventivo'}
                  </p>
                </div>
                <Button variant="ghost" size="sm" onClick={onClose} className="flex-shrink-0">
                  <X className="h-4 w-4 sm:h-5 sm:w-5" />
                </Button>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 sm:space-y-6">
                {/* Titolo e Cliente */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${textPrimary}`}>
                      Titolo Preventivo *
                    </label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-2 rounded-lg border', inputBg, errors.title && 'border-gray-500')}
                      placeholder="Sito Web Corporate"
                    />
                    {errors.title && (
                      <p className="text-gray-400 text-sm mt-1 flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {errors.title}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${textPrimary}`}>
                      Cliente *
                    </label>
                    <select
                      value={formData.customer_id || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, customer_id: Number(e.target.value) || null }))}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-2 rounded-lg border', inputBg, errors.customer_id && 'border-gray-500')}
                    >
                      <option value="">Seleziona cliente</option>
                      {customers.map(customer => (
                        <option key={customer.id} value={customer.id}>
                          {customer.name} {customer.company ? `(${customer.company})` : ''}
                        </option>
                      ))}
                    </select>
                    {errors.customer_id && (
                      <p className="text-gray-400 text-sm mt-1 flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {errors.customer_id}
                      </p>
                    )}
                  </div>
                </div>

                {/* Line Items */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <label className={`text-sm font-medium ${textPrimary}`}>
                      Articoli / Servizi *
                    </label>
                    {mode !== 'view' && (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={addLineItem}
                        className={isDark ? 'border-white/20' : ''}
                      >
                        <Plus className="h-4 w-4 mr-1" />
                        Aggiungi
                      </Button>
                    )}
                  </div>

                  <div className="space-y-3">
                    {formData.line_items.map((item, index) => (
                      <div key={index} className={cn('p-4 rounded-lg border', isDark ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-gray-200')}>
                        <div className="grid grid-cols-12 gap-3">
                          <div className="col-span-6">
                            <input
                              type="text"
                              value={item.description}
                              onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                              disabled={mode === 'view'}
                              className={cn('w-full px-3 py-2 rounded-lg border text-sm', inputBg)}
                              placeholder="Descrizione servizio/prodotto"
                            />
                          </div>
                          <div className="col-span-2">
                            <input
                              type="number"
                              value={item.quantity}
                              onChange={(e) => updateLineItem(index, 'quantity', Number(e.target.value))}
                              disabled={mode === 'view'}
                              min="1"
                              className={cn('w-full px-3 py-2 rounded-lg border text-sm', inputBg)}
                              placeholder="Qtà"
                            />
                          </div>
                          <div className="col-span-3">
                            <div className="relative">
                              <Euro className={`absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 ${textSecondary}`} />
                              <input
                                type="number"
                                value={item.unit_price}
                                onChange={(e) => updateLineItem(index, 'unit_price', Number(e.target.value))}
                                disabled={mode === 'view'}
                                min="0"
                                step="0.01"
                                className={cn('w-full pl-7 pr-3 py-2 rounded-lg border text-sm', inputBg)}
                                placeholder="Prezzo"
                              />
                            </div>
                          </div>
                          {mode !== 'view' && (
                            <div className="col-span-1 flex items-center">
                              <Button
                                type="button"
                                size="sm"
                                variant="ghost"
                                onClick={() => removeLineItem(index)}
                                disabled={formData.line_items.length === 1}
                              >
                                <Trash2 className="h-4 w-4 text-gray-400" />
                              </Button>
                            </div>
                          )}
                        </div>
                        <div className={`text-xs ${textSecondary} mt-2 text-right`}>
                          Subtotale: €{(item.quantity * item.unit_price).toFixed(2)}
                        </div>
                      </div>
                    ))}
                  </div>
                  {errors.line_items && (
                    <p className="text-gray-400 text-sm mt-2 flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {errors.line_items}
                    </p>
                  )}
                </div>

                {/* IVA, Sconto, Validità */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${textPrimary}`}>
                      IVA (%)
                    </label>
                    <input
                      type="number"
                      value={formData.tax_rate}
                      onChange={(e) => setFormData(prev => ({ ...prev, tax_rate: Number(e.target.value) }))}
                      disabled={mode === 'view'}
                      min="0"
                      max="100"
                      className={cn('w-full px-4 py-2 rounded-lg border', inputBg)}
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${textPrimary}`}>
                      Sconto (€)
                    </label>
                    <div className="relative">
                      <Euro className={`absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 ${textSecondary}`} />
                      <input
                        type="number"
                        value={formData.discount_amount}
                        onChange={(e) => setFormData(prev => ({ ...prev, discount_amount: Number(e.target.value) }))}
                        disabled={mode === 'view'}
                        min="0"
                        step="0.01"
                        className={cn('w-full pl-10 pr-4 py-2 rounded-lg border', inputBg)}
                      />
                    </div>
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${textPrimary}`}>
                      Valido fino al
                    </label>
                    <div className="relative">
                      <Calendar className={`absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 ${textSecondary}`} />
                      <input
                        type="date"
                        value={formData.valid_until}
                        onChange={(e) => setFormData(prev => ({ ...prev, valid_until: e.target.value }))}
                        disabled={mode === 'view'}
                        className={cn('w-full pl-10 pr-4 py-2 rounded-lg border', inputBg)}
                      />
                    </div>
                  </div>
                </div>

                {/* Riepilogo Totali */}
                <div className={cn('p-4 rounded-lg', isDark ? 'bg-gold/10 border border-gold/30' : 'bg-gold/10 border border-gold/30')}>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className={textSecondary}>Subtotale:</span>
                      <span className={textPrimary}>€{calculateSubtotal().toFixed(2)}</span>
                    </div>
                    {formData.discount_amount > 0 && (
                      <div className="flex justify-between text-gray-400">
                        <span>Sconto:</span>
                        <span>-€{formData.discount_amount.toFixed(2)}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className={textSecondary}>IVA ({formData.tax_rate}%):</span>
                      <span className={textPrimary}>€{calculateTax().toFixed(2)}</span>
                    </div>
                    <div className="border-t border-white/20 pt-2">
                      <div className="flex justify-between text-xl font-bold">
                        <span className={textPrimary}>TOTALE:</span>
                        <span className="text-gold">€{calculateTotal().toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Note */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${textPrimary}`}>
                    Note
                  </label>
                  <div className="relative">
                    <FileText className={`absolute left-3 top-3 h-4 w-4 ${textSecondary}`} />
                    <textarea
                      value={formData.notes}
                      onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                      disabled={mode === 'view'}
                      className={cn('w-full pl-10 pr-4 py-2 rounded-lg border resize-none', inputBg)}
                      placeholder="Note aggiuntive sul preventivo..."
                      rows={3}
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={onClose}
                    disabled={loading}
                    className={isDark ? 'border-white/20' : ''}
                  >
                    {mode === 'view' ? 'Chiudi' : 'Annulla'}
                  </Button>
                  {mode !== 'view' && (
                    <Button
                      type="submit"
                      disabled={loading}
                      className="bg-gold hover:bg-gold-dark text-black"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Salvataggio...
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4 mr-2" />
                          {mode === 'edit' ? 'Aggiorna' : 'Crea Preventivo'}
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
