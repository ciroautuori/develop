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
  LogIn, 
  Mail, 
  Lock,
  AlertCircle,
  ArrowLeft
} from 'lucide-react';

export const Route = createFileRoute('/auth/login')({
  component: LoginPage,
});

function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // TODO: Implementare chiamata API login
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Errore durante il login');
      }

      const data = await response.json();
      
      // Salva token in localStorage
      localStorage.setItem('iss_token', data.access_token);
      localStorage.setItem('iss_user', JSON.stringify(data.user));
      
      // Redirect to dashboard
      window.location.href = '/dashboard';
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante il login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

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
            Accedi al tuo account
          </CardTitle>
          <p className="text-gray-600">
            Inserisci le tue credenziali per accedere alla piattaforma ISS
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
            {/* Email Field */}
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

            {/* Password Field */}
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

            {/* Remember & Forgot */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded border-gray-300 text-iss-gold-500 focus:ring-iss-gold-400" />
                <span className="text-gray-600">Ricordami</span>
              </label>
              <a 
                href="/auth/forgot-password" 
                className="text-iss-bordeaux-600 hover:text-iss-bordeaux-700 font-medium"
              >
                Password dimenticata?
              </a>
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
                  Accesso in corso...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <LogIn className="w-4 h-4" />
                  Accedi
                </div>
              )}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">oppure</span>
            </div>
          </div>

          {/* Register Link */}
          <div className="text-center">
            <p className="text-gray-600">
              Non hai ancora un account?{' '}
              <a 
                href="/auth/register" 
                className="text-iss-bordeaux-600 hover:text-iss-bordeaux-700 font-semibold"
              >
                Registrati gratuitamente
              </a>
            </p>
          </div>

          {/* Demo Credentials */}
          <div className="bg-iss-gold-50 border border-iss-gold-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-iss-gold-800 mb-2">
              🚀 Account Demo Disponibili
            </h4>
            <div className="text-xs text-iss-gold-700 space-y-1">
              <div><strong>Admin:</strong> admin@iss.salerno.it / AdminISS2025!</div>
              <div><strong>APS:</strong> test_1758638182@example.com / TestUser2025!</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
