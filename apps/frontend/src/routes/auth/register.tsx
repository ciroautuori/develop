import { createFileRoute, Link } from '@tanstack/react-router';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Eye, 
  EyeOff, 
  UserPlus, 
  Mail, 
  Lock,
  User,
  Phone,
  Building,
  AlertCircle,
  ArrowLeft,
  CheckCircle
} from 'lucide-react';

export const Route = createFileRoute('/auth/register')({
  component: RegisterPage,
});

type UserRole = 'cittadino' | 'aps_responsabile' | 'aps_operatore' | 'volontario';
type AccessibilityNeeds = 'none' | 'visual_impairment' | 'hearing_impairment' | 'motor_impairment' | 'cognitive_impairment' | 'multiple_impairments';

function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    nome: '',
    cognome: '',
    telefono: '',
    role: 'cittadino' as UserRole,
    accessibility_needs: 'none' as AccessibilityNeeds,
    privacy_policy_accepted: false,
    newsletter_subscription: false,
    // APS fields
    aps_nome_organizzazione: '',
    aps_citta: '',
    aps_settore_attivita: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Le password non coincidono');
      setIsLoading(false);
      return;
    }

    if (!formData.privacy_policy_accepted) {
      setError('Devi accettare la Privacy Policy per continuare');
      setIsLoading(false);
      return;
    }

    try {
      const registerData = {
        email: formData.email,
        password: formData.password,
        nome: formData.nome,
        cognome: formData.cognome,
        telefono: formData.telefono || null,
        role: formData.role,
        accessibility_needs: formData.accessibility_needs,
        privacy_policy_accepted: formData.privacy_policy_accepted,
        newsletter_subscription: formData.newsletter_subscription,
        ...(formData.role.startsWith('aps') && {
          aps_nome_organizzazione: formData.aps_nome_organizzazione,
          aps_citta: formData.aps_citta,
          aps_settore_attivita: formData.aps_settore_attivita
        })
      };

      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Errore durante la registrazione');
      }

      setSuccess(true);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante la registrazione');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  if (success) {
    return (
      <div className="space-y-6">
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-iss-bordeaux-900 mb-4">
              Registrazione Completata!
            </h2>
            <p className="text-gray-600 mb-6">
              Il tuo account è stato creato con successo. Ora puoi accedere alla piattaforma ISS.
            </p>
            <Button 
              className="bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800"
              onClick={() => window.location.href = '/auth/login'}
            >
              Accedi ora
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back to Home */}
      <div className="flex items-center gap-2 text-iss-bordeaux-600 hover:text-iss-bordeaux-700 transition-colors">
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => window.location.href = '/'}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Torna alla Home
        </Button>
      </div>

      <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
        <CardHeader className="text-center pb-6">
          <CardTitle className="text-2xl font-bold text-iss-bordeaux-900 mb-2">
            Registrati gratuitamente
          </CardTitle>
          <p className="text-gray-600">
            Crea il tuo account per accedere a tutte le funzionalità ISS
          </p>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Role Selection */}
            <div className="space-y-2">
              <Label htmlFor="role" className="text-sm font-medium text-gray-700">
                Tipologia Account
              </Label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full h-12 px-3 border border-gray-200 rounded-md focus:border-iss-gold-400 focus:ring-iss-gold-400"
                required
              >
                <option value="cittadino">Cittadino</option>
                <option value="aps_responsabile">Responsabile APS</option>
                <option value="aps_operatore">Operatore APS</option>
                <option value="volontario">Volontario</option>
              </select>
            </div>

            {/* Personal Info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nome" className="text-sm font-medium text-gray-700">
                  Nome
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="nome"
                    name="nome"
                    placeholder="Mario"
                    value={formData.nome}
                    onChange={handleChange}
                    className="pl-10 h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="cognome" className="text-sm font-medium text-gray-700">
                  Cognome
                </Label>
                <Input
                  id="cognome"
                  name="cognome"
                  placeholder="Rossi"
                  value={formData.cognome}
                  onChange={handleChange}
                  className="h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="mario.rossi@aps.it"
                  value={formData.email}
                  onChange={handleChange}
                  className="pl-10 h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                  required
                />
              </div>
            </div>

            {/* Phone (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="telefono" className="text-sm font-medium text-gray-700">
                Telefono <span className="text-gray-400">(opzionale)</span>
              </Label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  id="telefono"
                  name="telefono"
                  type="tel"
                  placeholder="+39 333 123 4567"
                  value={formData.telefono}
                  onChange={handleChange}
                  className="pl-10 h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                />
              </div>
            </div>

            {/* APS Fields */}
            {formData.role.startsWith('aps') && (
              <div className="space-y-4 p-4 bg-iss-bordeaux-50 rounded-lg border border-iss-bordeaux-100">
                <h4 className="font-semibold text-iss-bordeaux-900 flex items-center gap-2">
                  <Building className="w-4 h-4" />
                  Informazioni APS
                </h4>
                
                <div className="space-y-2">
                  <Label htmlFor="aps_nome_organizzazione" className="text-sm font-medium text-gray-700">
                    Nome Organizzazione
                  </Label>
                  <Input
                    id="aps_nome_organizzazione"
                    name="aps_nome_organizzazione"
                    placeholder="APS Nuove Rotte"
                    value={formData.aps_nome_organizzazione}
                    onChange={handleChange}
                    className="h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                    required={formData.role.startsWith('aps')}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="aps_citta" className="text-sm font-medium text-gray-700">
                      Città
                    </Label>
                    <Input
                      id="aps_citta"
                      name="aps_citta"
                      placeholder="Salerno"
                      value={formData.aps_citta}
                      onChange={handleChange}
                      className="h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                      required={formData.role.startsWith('aps')}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="aps_settore_attivita" className="text-sm font-medium text-gray-700">
                      Settore
                    </Label>
                    <select
                      id="aps_settore_attivita"
                      name="aps_settore_attivita"
                      value={formData.aps_settore_attivita}
                      onChange={handleChange}
                      className="w-full h-12 px-3 border border-gray-200 rounded-md focus:border-iss-gold-400 focus:ring-iss-gold-400"
                      required={formData.role.startsWith('aps')}
                    >
                      <option value="">Seleziona settore</option>
                      <option value="sociale">Sociale</option>
                      <option value="ambiente">Ambiente</option>
                      <option value="cultura">Cultura</option>
                      <option value="sport">Sport</option>
                      <option value="educazione">Educazione</option>
                      <option value="sanitario">Sanitario</option>
                      <option value="altro">Altro</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Accessibility */}
            <div className="space-y-2">
              <Label htmlFor="accessibility_needs" className="text-sm font-medium text-gray-700">
                Esigenze di Accessibilità
              </Label>
              <select
                id="accessibility_needs"
                name="accessibility_needs"
                value={formData.accessibility_needs}
                onChange={handleChange}
                className="w-full h-12 px-3 border border-gray-200 rounded-md focus:border-iss-gold-400 focus:ring-iss-gold-400"
              >
                <option value="none">Nessuna</option>
                <option value="visual_impairment">Disabilità visiva</option>
                <option value="hearing_impairment">Disabilità uditiva</option>
                <option value="motor_impairment">Disabilità motoria</option>
                <option value="cognitive_impairment">Disabilità cognitiva</option>
                <option value="multiple_impairments">Disabilità multiple</option>
              </select>
            </div>

            {/* Passwords */}
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleChange}
                    className="pl-10 pr-10 h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                  Conferma Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="pl-10 pr-10 h-12 border-gray-200 focus:border-iss-gold-400 focus:ring-iss-gold-400"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Checkboxes */}
            <div className="space-y-3">
              <label className="flex items-start gap-3 cursor-pointer">
                <input 
                  type="checkbox" 
                  name="privacy_policy_accepted"
                  checked={formData.privacy_policy_accepted}
                  onChange={handleChange}
                  className="mt-1 rounded border-gray-300 text-iss-gold-500 focus:ring-iss-gold-400" 
                  required
                />
                <span className="text-sm text-gray-600">
                  Accetto la <a href="/privacy" className="text-iss-bordeaux-600 hover:underline">Privacy Policy</a> e i <a href="/terms" className="text-iss-bordeaux-600 hover:underline">Termini di Servizio</a>
                </span>
              </label>
              
              <label className="flex items-start gap-3 cursor-pointer">
                <input 
                  type="checkbox" 
                  name="newsletter_subscription"
                  checked={formData.newsletter_subscription}
                  onChange={handleChange}
                  className="mt-1 rounded border-gray-300 text-iss-gold-500 focus:ring-iss-gold-400" 
                />
                <span className="text-sm text-gray-600">
                  Desidero ricevere aggiornamenti sui nuovi bandi e corsi (opzionale)
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 bg-iss-bordeaux-900 hover:bg-iss-bordeaux-800 text-white font-semibold text-base"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  Registrazione in corso...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <UserPlus className="w-4 h-4" />
                  Registrati Gratuitamente
                </div>
              )}
            </Button>
          </form>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-gray-600">
              Hai già un account?{' '}
              <a 
                href="/auth/login" 
                className="text-iss-bordeaux-600 hover:text-iss-bordeaux-700 font-semibold"
              >
                Accedi qui
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
