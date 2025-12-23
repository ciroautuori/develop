/**
 * Contact Form Component
 */

import { Button } from '../../../shared/components/ui/button';
import { Input } from '../../../shared/components/ui/input';
import { Textarea } from '../../../shared/components/ui/textarea';
import type { ContactFormData } from '../types/landing.types';

interface ContactFormProps {
  data: ContactFormData;
  onUpdate: (field: keyof ContactFormData, value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  submitting: boolean;
  success: boolean;
  error: string | null;
}

export function ContactForm({ data, onUpdate, onSubmit, submitting, success, error }: ContactFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {success && (
        <div className="p-4 bg-primary/10 border border-primary/50 rounded-lg text-primary text-center">
          ✓ Messaggio inviato con successo! Ti risponderemo presto.
        </div>
      )}

      {error && (
        <div className="p-4 bg-destructive/10 border border-destructive/50 rounded-lg text-destructive text-center">
          ✗ {error}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        <Input
          placeholder="Nome *"
          value={data.name}
          onChange={(e) => onUpdate('name', e.target.value)}
          required
        />
        <Input
          type="email"
          placeholder="Email *"
          value={data.email}
          onChange={(e) => onUpdate('email', e.target.value)}
          required
        />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <Input
          placeholder="Azienda"
          value={data.company}
          onChange={(e) => onUpdate('company', e.target.value)}
        />
        <Input
          type="tel"
          placeholder="Telefono"
          value={data.phone}
          onChange={(e) => onUpdate('phone', e.target.value)}
        />
      </div>

      <Input
        placeholder="Oggetto *"
        value={data.subject}
        onChange={(e) => onUpdate('subject', e.target.value)}
        required
      />

      <Textarea
        placeholder="Messaggio *"
        value={data.message}
        onChange={(e) => onUpdate('message', e.target.value)}
        required
        rows={5}
      />

      <Button
        type="submit"
        disabled={submitting}
        size="lg"
        className="w-full font-medium"
      >
        {submitting ? 'Invio in corso...' : 'Invia Messaggio'}
      </Button>
    </form>
  );
}
