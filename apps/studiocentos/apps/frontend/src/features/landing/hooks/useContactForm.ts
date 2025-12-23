/**
 * Contact Form Hook
 */

import { useState } from 'react';
import type { ContactFormData } from '../types/landing.types';

const initialFormState: ContactFormData = {
  name: '',
  email: '',
  company: '',
  phone: '',
  subject: '',
  message: '',
  request_type: 'general'
};

export function useContactForm() {
  const [formData, setFormData] = useState<ContactFormData>(initialFormState);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateField = (field: keyof ContactFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const resetForm = () => {
    setFormData(initialFormState);
    setSuccess(false);
    setError(null);
  };

  const submitForm = async () => {
    setSubmitting(true);
    setError(null);

    try {
      // Use relative API path - Nginx handles proxy to backend
      const response = await fetch('/api/v1/portfolio/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to submit contact form');
      }

      setSuccess(true);
      resetForm();

      // Auto-hide success message after 5 seconds
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      setError((err as Error).message);
      console.error('Error submitting contact form:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return {
    formData,
    updateField,
    submitForm,
    resetForm,
    submitting,
    success,
    error
  };
}
