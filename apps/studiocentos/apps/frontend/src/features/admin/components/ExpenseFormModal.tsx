/**
 * ExpenseFormModal - Modal per creare/modificare spese
 * Form completo con validazione e integrazione API
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X, Euro, Calendar, Building2, FileText, Save, Loader2,
  CreditCard, Tag, Percent, AlertCircle
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { Input } from '../../../shared/components/ui/input';
import { Label } from '../../../shared/components/ui/label';
import { Textarea } from '../../../shared/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../../../shared/components/ui/select';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';

// Types
interface Expense {
  id?: number;
  title: string;
  description?: string;
  category: string;
  subcategory?: string;
  amount: number;
  currency: string;
  vat_rate: number;
  due_date: string;
  frequency: string;
  supplier_name?: string;
  supplier_email?: string;
  payment_method?: string;
  tax_deductible: boolean;
  tax_percentage: number;
  status?: string;
}

interface ExpenseFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  expense?: Expense | null;
  defaultDate?: Date;
}

const CATEGORIES = [
  { value: 'infrastruttura', label: 'Infrastruttura', color: 'bg-gold' },
  { value: 'marketing', label: 'Marketing', color: 'bg-gold' },
  { value: 'formazione', label: 'Formazione', color: 'bg-gold' },
  { value: 'business', label: 'Business', color: 'bg-gold' },
  { value: 'tools', label: 'Tools & Software', color: 'bg-gray-500' },
  { value: 'legale', label: 'Legale & Consulenza', color: 'bg-gray-500' },
  { value: 'investimenti', label: 'Investimenti', color: 'bg-gold' },
];

const FREQUENCIES = [
  { value: 'one_time', label: 'Una tantum' },
  { value: 'monthly', label: 'Mensile' },
  { value: 'quarterly', label: 'Trimestrale' },
  { value: 'yearly', label: 'Annuale' },
];

const PAYMENT_METHODS = [
  { value: 'bank_transfer', label: 'Bonifico Bancario' },
  { value: 'credit_card', label: 'Carta di Credito' },
  { value: 'paypal', label: 'PayPal' },
  { value: 'stripe', label: 'Stripe' },
  { value: 'cash', label: 'Contanti' },
];

const VAT_RATES = [
  { value: '22', label: '22% (Standard)' },
  { value: '10', label: '10% (Ridotta)' },
  { value: '4', label: '4% (Super Ridotta)' },
  { value: '0', label: '0% (Esente)' },
];

export function ExpenseFormModal({
  isOpen,
  onClose,
  onSuccess,
  expense = null,
  defaultDate
}: ExpenseFormModalProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const isEdit = !!expense?.id;

  // Form state
  const [formData, setFormData] = useState<Expense>({
    title: '',
    description: '',
    category: 'business',
    subcategory: '',
    amount: 0,
    currency: 'EUR',
    vat_rate: 22,
    due_date: new Date().toISOString().split('T')[0],
    frequency: 'one_time',
    supplier_name: '',
    supplier_email: '',
    payment_method: 'bank_transfer',
    tax_deductible: true,
    tax_percentage: 100,
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Theme classes
  const modalBg = isDark
    ? 'bg-[#0A0A0A] border-white/10'
    : 'bg-white border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-gray-50 border-gray-200 text-gray-900';

  // Initialize form with expense data or defaults
  useEffect(() => {
    if (expense) {
      setFormData({
        title: expense.title || '',
        description: expense.description || '',
        category: expense.category || 'business',
        subcategory: expense.subcategory || '',
        amount: expense.amount || 0,
        currency: expense.currency || 'EUR',
        vat_rate: expense.vat_rate || 22,
        due_date: expense.due_date || new Date().toISOString().split('T')[0],
        frequency: expense.frequency || 'one_time',
        supplier_name: expense.supplier_name || '',
        supplier_email: expense.supplier_email || '',
        payment_method: expense.payment_method || 'bank_transfer',
        tax_deductible: expense.tax_deductible ?? true,
        tax_percentage: expense.tax_percentage || 100,
      });
    } else if (defaultDate) {
      setFormData(prev => ({
        ...prev,
        due_date: defaultDate.toISOString().split('T')[0]
      }));
    }
  }, [expense, defaultDate]);

  // Handle input change
  const handleChange = (field: keyof Expense, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error on change
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Il titolo è obbligatorio';
    }

    if (!formData.amount || formData.amount <= 0) {
      newErrors.amount = 'Inserisci un importo valido';
    }

    if (!formData.due_date) {
      newErrors.due_date = 'La data di scadenza è obbligatoria';
    }

    if (!formData.category) {
      newErrors.category = 'Seleziona una categoria';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const url = isEdit
        ? `/api/v1/admin/finance/expenses/${expense?.id}`
        : '/api/v1/admin/finance/expenses';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          amount: parseFloat(formData.amount.toString()),
          vat_rate: parseFloat(formData.vat_rate.toString()),
          tax_percentage: parseFloat(formData.tax_percentage.toString()),
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Errore nel salvataggio');
      }

      toast.success(isEdit ? 'Spesa aggiornata!' : 'Spesa creata!');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving expense:', error);
      toast.error(error instanceof Error ? error.message : 'Errore nel salvataggio');
    } finally {
      setLoading(false);
    }
  };

  // Calculate amounts
  const netAmount = formData.amount / (1 + formData.vat_rate / 100);
  const vatAmount = formData.amount - netAmount;
  const deductibleAmount = formData.tax_deductible
    ? (netAmount * formData.tax_percentage / 100)
    : 0;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            className={cn(
              'w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl border shadow-xl',
              modalBg
            )}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 z-10 flex items-center justify-between p-6 border-b border-white/10 bg-inherit">
              <div>
                <h2 className={cn('text-xl font-bold', textPrimary)}>
                  {isEdit ? 'Modifica Spesa' : 'Nuova Spesa'}
                </h2>
                <p className={cn('text-sm', textSecondary)}>
                  {isEdit ? 'Aggiorna i dettagli della spesa' : 'Inserisci i dettagli della nuova spesa'}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Titolo e Descrizione */}
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <Label className={textPrimary}>Titolo *</Label>
                  <Input
                    value={formData.title}
                    onChange={(e) => handleChange('title', e.target.value)}
                    placeholder="Es. Abbonamento Cloud Hosting"
                    className={cn(inputBg, errors.title && 'border-gray-500')}
                  />
                  {errors.title && (
                    <p className="text-gray-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {errors.title}
                    </p>
                  )}
                </div>

                <div>
                  <Label className={textPrimary}>Descrizione</Label>
                  <Textarea
                    value={formData.description || ''}
                    onChange={(e) => handleChange('description', e.target.value)}
                    placeholder="Dettagli aggiuntivi sulla spesa..."
                    className={cn(inputBg, 'min-h-[80px]')}
                  />
                </div>
              </div>

              {/* Categoria e Frequenza */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className={textPrimary}>Categoria *</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) => handleChange('category', value)}
                  >
                    <SelectTrigger className={cn(inputBg, errors.category && 'border-gray-500')}>
                      <SelectValue placeholder="Seleziona categoria" />
                    </SelectTrigger>
                    <SelectContent>
                      {CATEGORIES.map(cat => (
                        <SelectItem key={cat.value} value={cat.value}>
                          <div className="flex items-center gap-2">
                            <div className={cn('w-2 h-2 rounded-full', cat.color)} />
                            {cat.label}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className={textPrimary}>Frequenza</Label>
                  <Select
                    value={formData.frequency}
                    onValueChange={(value) => handleChange('frequency', value)}
                  >
                    <SelectTrigger className={inputBg}>
                      <SelectValue placeholder="Seleziona frequenza" />
                    </SelectTrigger>
                    <SelectContent>
                      {FREQUENCIES.map(freq => (
                        <SelectItem key={freq.value} value={freq.value}>
                          {freq.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Importo e IVA */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label className={textPrimary}>Importo (lordo) *</Label>
                  <div className="relative">
                    <Euro className={cn('absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4', textSecondary)} />
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={formData.amount || ''}
                      onChange={(e) => handleChange('amount', parseFloat(e.target.value) || 0)}
                      placeholder="0.00"
                      className={cn(inputBg, 'pl-10', errors.amount && 'border-gray-500')}
                    />
                  </div>
                  {errors.amount && (
                    <p className="text-gray-400 text-xs mt-1">{errors.amount}</p>
                  )}
                </div>

                <div>
                  <Label className={textPrimary}>Aliquota IVA</Label>
                  <Select
                    value={formData.vat_rate.toString()}
                    onValueChange={(value) => handleChange('vat_rate', parseFloat(value))}
                  >
                    <SelectTrigger className={inputBg}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {VAT_RATES.map(rate => (
                        <SelectItem key={rate.value} value={rate.value}>
                          {rate.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className={textPrimary}>Scadenza *</Label>
                  <div className="relative">
                    <Calendar className={cn('absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4', textSecondary)} />
                    <Input
                      type="date"
                      value={formData.due_date}
                      onChange={(e) => handleChange('due_date', e.target.value)}
                      className={cn(inputBg, 'pl-10', errors.due_date && 'border-gray-500')}
                    />
                  </div>
                </div>
              </div>

              {/* Riepilogo Importi */}
              {formData.amount > 0 && (
                <div className={cn(
                  'p-4 rounded-lg border',
                  isDark ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-gray-200'
                )}>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className={textSecondary}>Netto:</span>
                      <p className={cn('font-semibold', textPrimary)}>
                        €{netAmount.toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                    <div>
                      <span className={textSecondary}>IVA ({formData.vat_rate}%):</span>
                      <p className={cn('font-semibold', textPrimary)}>
                        €{vatAmount.toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                    {formData.tax_deductible && (
                      <div>
                        <span className={textSecondary}>Deducibile:</span>
                        <p className="font-semibold text-gold">
                          €{deductibleAmount.toLocaleString('it-IT', { minimumFractionDigits: 2 })}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Fornitore */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className={textPrimary}>Fornitore</Label>
                  <div className="relative">
                    <Building2 className={cn('absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4', textSecondary)} />
                    <Input
                      value={formData.supplier_name || ''}
                      onChange={(e) => handleChange('supplier_name', e.target.value)}
                      placeholder="Nome fornitore"
                      className={cn(inputBg, 'pl-10')}
                    />
                  </div>
                </div>

                <div>
                  <Label className={textPrimary}>Email Fornitore</Label>
                  <Input
                    type="email"
                    value={formData.supplier_email || ''}
                    onChange={(e) => handleChange('supplier_email', e.target.value)}
                    placeholder="email@fornitore.it"
                    className={inputBg}
                  />
                </div>
              </div>

              {/* Pagamento e Deducibilità */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className={textPrimary}>Metodo Pagamento</Label>
                  <Select
                    value={formData.payment_method || 'bank_transfer'}
                    onValueChange={(value) => handleChange('payment_method', value)}
                  >
                    <SelectTrigger className={inputBg}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PAYMENT_METHODS.map(method => (
                        <SelectItem key={method.value} value={method.value}>
                          {method.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className={textPrimary}>Deducibilità Fiscale (%)</Label>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.tax_deductible}
                      onChange={(e) => handleChange('tax_deductible', e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      value={formData.tax_percentage}
                      onChange={(e) => handleChange('tax_percentage', parseFloat(e.target.value) || 0)}
                      disabled={!formData.tax_deductible}
                      className={cn(inputBg, 'flex-1', !formData.tax_deductible && 'opacity-50')}
                    />
                    <span className={textSecondary}>%</span>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  disabled={loading}
                  className={isDark ? 'border-white/20' : ''}
                >
                  Annulla
                </Button>
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
                      {isEdit ? 'Aggiorna' : 'Crea Spesa'}
                    </>
                  )}
                </Button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
