import React, { useState } from 'react';
import { Building2, Mail, Phone, MapPin, Users, Target, Tag, Euro, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/utils/cn';

interface APSRegistrationProps {
  onRegistrationComplete?: (user: any) => void;
  className?: string;
}

interface RegistrationForm {
  // Dati organizzazione
  organization_name: string;
  organization_type: string;
  fiscal_code: string;
  vat_number?: string;
  
  // Contatti
  contact_email: string;
  contact_phone?: string;
  website?: string;
  
  // Indirizzo
  address?: string;
  city?: string;
  province?: string;
  postal_code?: string;
  region: string;
  
  // Profilo
  description?: string;
  sectors: string[];
  target_groups: string[];
  keywords: string[];
  
  // Budget e capacità
  annual_budget_range?: string;
  team_size?: number;
  volunteer_count?: number;
  max_budget_interest?: number;
  geographical_scope: string;
}

const ORGANIZATION_TYPES = [
  { value: 'aps', label: 'APS - Associazione di Promozione Sociale' },
  { value: 'odv', label: 'ODV - Organizzazione di Volontariato' },
  { value: 'cooperativa', label: 'Cooperativa Sociale' },
  { value: 'fondazione', label: 'Fondazione' },
  { value: 'ong', label: 'ONG - Organizzazione Non Governativa' },
  { value: 'impresa_sociale', label: 'Impresa Sociale' },
  { value: 'altro', label: 'Altro' }
];

const SECTORS = [
  'sociale', 'cultura', 'ambiente', 'sport', 'formazione',
  'sanitario', 'ricerca', 'innovazione', 'digitale', 'turismo',
  'agricoltura', 'alimentare', 'energia', 'trasporti'
];

const TARGET_GROUPS = [
  'giovani', 'anziani', 'disabili', 'immigrati', 'donne',
  'minori', 'famiglie', 'comunità', 'studenti', 'lavoratori',
  'emarginati', 'tossicodipendenti', 'detenuti'
];

const BUDGET_RANGES = [
  '0-10k', '10k-50k', '50k-100k', '100k-500k', '500k+', 'Non specificato'
];

const PROVINCES = [
  'AV', 'BN', 'CE', 'NA', 'SA'
];

export const APSRegistration: React.FC<APSRegistrationProps> = ({ 
  onRegistrationComplete, 
  className 
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<RegistrationForm>({
    organization_name: '',
    organization_type: 'aps',
    fiscal_code: '',
    contact_email: '',
    region: 'Campania',
    geographical_scope: 'Campania',
    sectors: [],
    target_groups: [],
    keywords: []
  });

  const updateForm = (field: keyof RegistrationForm, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const toggleArrayItem = (field: 'sectors' | 'target_groups' | 'keywords', item: string) => {
    const currentArray = form[field];
    const updatedArray = currentArray.includes(item)
      ? currentArray.filter(i => i !== item)
      : [...currentArray, item];
    updateForm(field, updatedArray);
  };

  const addKeyword = (keyword: string) => {
    if (keyword.trim() && !form.keywords.includes(keyword.trim())) {
      updateForm('keywords', [...form.keywords, keyword.trim()]);
    }
  };

  const removeKeyword = (keyword: string) => {
    updateForm('keywords', form.keywords.filter(k => k !== keyword));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // TODO: Integrare con API
      const response = await fetch('/api/v1/aps-users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });

      if (response.ok) {
        const user = await response.json();
        onRegistrationComplete?.(user);
      } else {
        throw new Error('Errore registrazione');
      }
    } catch (error) {
      console.error('Errore registrazione:', error);
      alert('Errore durante la registrazione. Riprova.');
    } finally {
      setLoading(false);
    }
  };

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 1:
        return !!(form.organization_name && form.organization_type && form.fiscal_code && form.contact_email);
      case 2:
        return true; // Dati facoltativi
      case 3:
        return !!(form.sectors.length > 0);
      case 4:
        return true; // Review step
      default:
        return false;
    }
  };

  const nextStep = () => {
    if (isStepValid(currentStep) && currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className={cn("max-w-4xl mx-auto p-6", className)}>
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🏛️ Registrazione Organizzazione
        </h1>
        <p className="text-gray-600">
          Unisciti alla piattaforma ISS per accedere a bandi personalizzati e raccomandazioni AI
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex justify-center mb-8">
        <div className="flex items-center space-x-4">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold",
                currentStep >= step 
                  ? "bg-blue-600 text-white" 
                  : "bg-gray-200 text-gray-600"
              )}>
                {step}
              </div>
              {step < 4 && (
                <div className={cn(
                  "w-12 h-1 mx-2",
                  currentStep > step ? "bg-blue-600" : "bg-gray-200"
                )} />
              )}
            </div>
          ))}
        </div>
      </div>

      <Card>
        <CardContent className="p-8">
          {/* Step 1: Dati Base */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Building2 className="h-12 w-12 text-blue-600 mx-auto mb-2" />
                <h2 className="text-2xl font-semibold">Dati Organizzazione</h2>
                <p className="text-gray-600">Informazioni di base sulla tua organizzazione</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Nome Organizzazione *</label>
                  <Input
                    value={form.organization_name}
                    onChange={(e) => updateForm('organization_name', e.target.value)}
                    placeholder="es. Associazione Sviluppo Sociale Salerno"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tipo Organizzazione *</label>
                  <Select value={form.organization_type} onValueChange={(value) => updateForm('organization_type', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ORGANIZATION_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Codice Fiscale *</label>
                  <Input
                    value={form.fiscal_code}
                    onChange={(e) => updateForm('fiscal_code', e.target.value.toUpperCase())}
                    placeholder="es. 12345678901"
                    maxLength={16}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Email Contatto *</label>
                  <Input
                    type="email"
                    value={form.contact_email}
                    onChange={(e) => updateForm('contact_email', e.target.value)}
                    placeholder="info@organizzazione.it"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Telefono</label>
                  <Input
                    type="tel"
                    value={form.contact_phone || ''}
                    onChange={(e) => updateForm('contact_phone', e.target.value)}
                    placeholder="+39 089 123456"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">P.IVA (se presente)</label>
                  <Input
                    value={form.vat_number || ''}
                    onChange={(e) => updateForm('vat_number', e.target.value)}
                    placeholder="12345678901"
                    maxLength={11}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Sito Web</label>
                  <Input
                    type="url"
                    value={form.website || ''}
                    onChange={(e) => updateForm('website', e.target.value)}
                    placeholder="https://www.organizzazione.it"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Indirizzo e Localizzazione */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <MapPin className="h-12 w-12 text-blue-600 mx-auto mb-2" />
                <h2 className="text-2xl font-semibold">Localizzazione</h2>
                <p className="text-gray-600">Dove opera la tua organizzazione</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Indirizzo</label>
                  <Input
                    value={form.address || ''}
                    onChange={(e) => updateForm('address', e.target.value)}
                    placeholder="Via Roma, 123"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Città</label>
                  <Input
                    value={form.city || ''}
                    onChange={(e) => updateForm('city', e.target.value)}
                    placeholder="Salerno"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Provincia</label>
                  <Select value={form.province || ''} onValueChange={(value) => updateForm('province', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Seleziona provincia" />
                    </SelectTrigger>
                    <SelectContent>
                      {PROVINCES.map(prov => (
                        <SelectItem key={prov} value={prov}>{prov}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">CAP</label>
                  <Input
                    value={form.postal_code || ''}
                    onChange={(e) => updateForm('postal_code', e.target.value)}
                    placeholder="84100"
                    maxLength={5}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Ambito Geografico</label>
                  <Select value={form.geographical_scope} onValueChange={(value) => updateForm('geographical_scope', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Locale">Locale (Comune)</SelectItem>
                      <SelectItem value="Provinciale">Provinciale</SelectItem>
                      <SelectItem value="Campania">Campania</SelectItem>
                      <SelectItem value="Nazionale">Nazionale</SelectItem>
                      <SelectItem value="Internazionale">Internazionale</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Descrizione Organizzazione</label>
                  <Textarea
                    value={form.description || ''}
                    onChange={(e) => updateForm('description', e.target.value)}
                    placeholder="Descrivi brevemente la missione e le attività della tua organizzazione..."
                    rows={4}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Settori e Target */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <Target className="h-12 w-12 text-blue-600 mx-auto mb-2" />
                <h2 className="text-2xl font-semibold">Settori e Target</h2>
                <p className="text-gray-600">In che ambiti opera la tua organizzazione</p>
              </div>

              {/* Settori */}
              <div>
                <label className="block text-sm font-medium mb-2">Settori di Interesse *</label>
                <p className="text-sm text-gray-600 mb-3">Seleziona almeno un settore</p>
                <div className="flex flex-wrap gap-2">
                  {SECTORS.map(sector => (
                    <Badge
                      key={sector}
                      variant={form.sectors.includes(sector) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => toggleArrayItem('sectors', sector)}
                    >
                      {sector}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Target Groups */}
              <div>
                <label className="block text-sm font-medium mb-2">Gruppi Target</label>
                <p className="text-sm text-gray-600 mb-3">Chi sono i beneficiari delle vostre attività</p>
                <div className="flex flex-wrap gap-2">
                  {TARGET_GROUPS.map(group => (
                    <Badge
                      key={group}
                      variant={form.target_groups.includes(group) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => toggleArrayItem('target_groups', group)}
                    >
                      {group}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Keywords Personalizzate */}
              <div>
                <label className="block text-sm font-medium mb-2">Parole Chiave Personalizzate</label>
                <p className="text-sm text-gray-600 mb-3">Aggiungi termini specifici per la tua organizzazione</p>
                <div className="flex gap-2 mb-2">
                  <Input
                    placeholder="es. educazione ambientale, teatro sociale..."
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addKeyword(e.currentTarget.value);
                        e.currentTarget.value = '';
                      }
                    }}
                  />
                  <Button
                    size="sm"
                    onClick={() => {
                      const input = document.querySelector('input[placeholder*="educazione"]') as HTMLInputElement;
                      if (input?.value) {
                        addKeyword(input.value);
                        input.value = '';
                      }
                    }}
                  >
                    Aggiungi
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {form.keywords.map(keyword => (
                    <Badge
                      key={keyword}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() => removeKeyword(keyword)}
                    >
                      {keyword} ×
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Budget e Team */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
                <div>
                  <label className="block text-sm font-medium mb-2">Budget Annuale</label>
                  <Select value={form.annual_budget_range || ''} onValueChange={(value) => updateForm('annual_budget_range', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Seleziona..." />
                    </SelectTrigger>
                    <SelectContent>
                      {BUDGET_RANGES.map(range => (
                        <SelectItem key={range} value={range}>{range}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Team Size</label>
                  <Input
                    type="number"
                    value={form.team_size || ''}
                    onChange={(e) => updateForm('team_size', parseInt(e.target.value) || undefined)}
                    placeholder="es. 5"
                    min="1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Volontari</label>
                  <Input
                    type="number"
                    value={form.volunteer_count || ''}
                    onChange={(e) => updateForm('volunteer_count', parseInt(e.target.value) || undefined)}
                    placeholder="es. 20"
                    min="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Budget Massimo Bandi di Interesse (€)</label>
                <Input
                  type="number"
                  value={form.max_budget_interest || ''}
                  onChange={(e) => updateForm('max_budget_interest', parseFloat(e.target.value) || undefined)}
                  placeholder="es. 50000"
                  min="0"
                />
                <p className="text-sm text-gray-500 mt-1">Importo massimo dei bandi che ti interessano</p>
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-2" />
                <h2 className="text-2xl font-semibold">Conferma Registrazione</h2>
                <p className="text-gray-600">Verifica i dati inseriti prima di completare</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Dati Organizzazione</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <p><strong>Nome:</strong> {form.organization_name}</p>
                      <p><strong>Tipo:</strong> {ORGANIZATION_TYPES.find(t => t.value === form.organization_type)?.label}</p>
                      <p><strong>CF:</strong> {form.fiscal_code}</p>
                      <p><strong>Email:</strong> {form.contact_email}</p>
                      <p><strong>Città:</strong> {form.city || 'Non specificata'}</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Profilo Attività</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 text-sm">
                      <div>
                        <strong>Settori:</strong>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {form.sectors.map(sector => (
                            <Badge key={sector} variant="outline" className="text-xs">{sector}</Badge>
                          ))}
                        </div>
                      </div>
                      {form.target_groups.length > 0 && (
                        <div>
                          <strong>Target:</strong>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {form.target_groups.map(group => (
                              <Badge key={group} variant="secondary" className="text-xs">{group}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      <p><strong>Ambito:</strong> {form.geographical_scope}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">🤖 AI Personalizzata</h3>
                <p className="text-blue-800 text-sm">
                  Grazie ai dati forniti, il nostro sistema AI genererà raccomandazioni personalizzate 
                  e troverà i bandi più adatti al profilo della tua organizzazione.
                </p>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-8 border-t">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1}
            >
              Indietro
            </Button>

            {currentStep < 4 ? (
              <Button
                onClick={nextStep}
                disabled={!isStepValid(currentStep)}
              >
                Avanti
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700"
              >
                {loading ? 'Registrazione...' : 'Completa Registrazione'}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
