/**
 * Customer Modal - CRUD Form per gestione clienti
 * Supporta creazione, modifica e visualizzazione dettagli cliente
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Loader2, Mail, Phone, Building2, MapPin, FileText, Tag, AlertCircle } from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';

interface CustomerFormData {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  vat_number?: string;
  city?: string;
  address?: string;
  status: 'lead' | 'active' | 'inactive';
  tags?: string;
  notes?: string;
}

interface CustomerModalProps {
  isOpen: boolean;
  onClose: () => void;
  customer?: any;
  onSuccess: () => void;
  mode: 'create' | 'edit' | 'view';
}

export function CustomerModal({ isOpen, onClose, customer, onSuccess, mode }: CustomerModalProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState<CustomerFormData>({
    name: '',
    email: '',
    phone: '',
    company: '',
    vat_number: '',
    city: '',
    address: '',
    status: 'lead',
    tags: '',
    notes: '',
  });

  useEffect(() => {
    if (customer && (mode === 'edit' || mode === 'view')) {
      setFormData({
        name: customer.name || '',
        email: customer.email || '',
        phone: customer.phone || '',
        company: customer.company || '',
        vat_number: customer.vat_number || '',
        city: customer.city || '',
        address: customer.address || '',
        status: customer.status || 'lead',
        tags: customer.tags?.join(', ') || '',
        notes: customer.notes || '',
      });
    } else {
      setFormData({
        name: '',
        email: '',
        phone: '',
        company: '',
        vat_number: '',
        city: '',
        address: '',
        status: 'lead',
        tags: '',
        notes: '',
      });
    }
    setErrors({});
  }, [customer, mode, isOpen]);

  // Theme classes - UNIFIED DESIGN SYSTEM (same as BookingModal)
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

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Nome obbligatorio';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email obbligatoria';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email non valida';
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
        ? `/api/v1/admin/customers/${customer.id}`
        : '/api/v1/admin/customers';

      const payload = {
        ...formData,
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : [],
      };

      const response = await fetch(url, {
        method: mode === 'edit' ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Errore nel salvataggio');
      }

      toast.success(mode === 'edit' ? 'Cliente aggiornato!' : 'Cliente creato!');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving customer:', error);
      toast.error(error instanceof Error ? error.message : 'Errore nel salvataggio');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof CustomerFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
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
              className={cn('w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl', modalBg)}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="sticky top-0 bg-inherit border-b border-white/10 p-4 sm:p-6 flex items-center justify-between">
                <div>
                  <h2 className={`text-xl sm:text-2xl font-bold ${textPrimary}`}>
                    {mode === 'create' ? '➕ Nuovo Cliente' : mode === 'edit' ? '✏️ Modifica Cliente' : '👁️ Dettagli Cliente'}
                  </h2>
                  <p className={`text-sm ${textSecondary} mt-1`}>
                    {mode === 'create' ? 'Aggiungi un nuovo cliente al CRM' : mode === 'edit' ? 'Aggiorna le informazioni del cliente' : 'Visualizza informazioni cliente'}
                  </p>
                </div>
                <Button variant="ghost" size="sm" onClick={onClose} className="flex-shrink-0">
                  <X className="h-4 w-4 sm:h-5 sm:w-5" />
                </Button>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 sm:space-y-6">
                {/* Nome e Email */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      Nome Completo *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleChange('name', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg, errors.name && 'border-gray-500')}
                      placeholder="Mario Rossi"
                    />
                    {errors.name && (
                      <p className="text-gray-400 text-sm mt-1 flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {errors.name}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      <Mail className="inline h-4 w-4 mr-2" />
                      Email *
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg, errors.email && 'border-gray-500')}
                      placeholder="mario@example.com"
                    />
                    {errors.email && (
                      <p className="text-gray-400 text-sm mt-1 flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {errors.email}
                      </p>
                    )}
                  </div>
                </div>

                {/* Telefono e Azienda */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      <Phone className="inline h-4 w-4 mr-2" />
                      Telefono
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleChange('phone', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg)}
                      placeholder="+39 123 456 7890"
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      <Building2 className="inline h-4 w-4 mr-2" />
                      Azienda
                    </label>
                    <input
                      type="text"
                      value={formData.company}
                      onChange={(e) => handleChange('company', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg)}
                      placeholder="Acme Inc"
                    />
                  </div>
                </div>

                {/* P.IVA e Città */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      P.IVA / Codice Fiscale
                    </label>
                    <input
                      type="text"
                      value={formData.vat_number}
                      onChange={(e) => handleChange('vat_number', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg)}
                      placeholder="IT12345678901"
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      <MapPin className="inline h-4 w-4 mr-2" />
                      Città
                    </label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => handleChange('city', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg)}
                      placeholder="Milano"
                    />
                  </div>
                </div>

                {/* Indirizzo */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                    Indirizzo
                  </label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => handleChange('address', e.target.value)}
                    disabled={mode === 'view'}
                    className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg)}
                    placeholder="Via Roma 123, 20100 Milano"
                  />
                </div>

                {/* Status e Tags */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      Status
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => handleChange('status', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', selectBg)}
                    >
                      <option value="lead">📋 Lead</option>
                      <option value="active">✅ Attivo</option>
                      <option value="inactive">💤 Inattivo</option>
                    </select>
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                      <Tag className="inline h-4 w-4 mr-2" />
                      Tags (separati da virgola)
                    </label>
                    <input
                      type="text"
                      value={formData.tags}
                      onChange={(e) => handleChange('tags', e.target.value)}
                      disabled={mode === 'view'}
                      className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none', inputBg)}
                      placeholder="vip, consulenza, web"
                    />
                  </div>
                </div>

                {/* Note */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${labelText}`}>
                    <FileText className="inline h-4 w-4 mr-2" />
                    Note
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => handleChange('notes', e.target.value)}
                    disabled={mode === 'view'}
                    className={cn('w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-gold focus:outline-none resize-none', inputBg)}
                    placeholder="Note aggiuntive sul cliente..."
                    rows={4}
                  />
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
                          {mode === 'edit' ? 'Aggiorna' : 'Crea Cliente'}
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
