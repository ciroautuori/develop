/**
 * Unified Login - MARKETTINA Brand Design
 * Single login page with role-based redirect
 * - Admin users → /admin
 * - Customer users → /dashboard
 */
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertCircle, Shield, Mail, Lock, Eye, EyeOff, Users, ShieldCheck, Sun, Moon } from 'lucide-react';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { STORAGE_KEYS, SPACING } from '../../../shared/config/constants';
import { LanguageSelector } from '../../../shared/i18n';

type LoginType = 'user' | 'admin';

export function UnifiedLogin() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginType, setLoginType] = useState<LoginType>('user');

  // Handle OAuth callback (token in URL) for admin
  useEffect(() => {
    const token = searchParams.get('token');
    const adminId = searchParams.get('admin_id');
    const oauthError = searchParams.get('error');

    if (oauthError) {
      if (oauthError === 'unauthorized_account') {
        setError('Accesso admin non autorizzato.');
      } else {
        setError(`Errore OAuth: ${oauthError}`);
      }
      return;
    }

    if (token && adminId) {
      localStorage.setItem(STORAGE_KEYS.adminToken, token);
      localStorage.setItem('admin_id', adminId);
      navigate('/admin');
    }
  }, [searchParams, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (loginType === 'admin') {
        // Admin login
        const response = await fetch('/api/v1/admin/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Credenziali admin non valide');
        }

        localStorage.setItem(STORAGE_KEYS.adminToken, data.access_token);
        localStorage.setItem('admin_id', data.admin_id?.toString() || '');
        navigate('/admin');
      } else {
        // Customer login
        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Credenziali non valide');
        }

        // Store customer token
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        // Redirect based on user role
        const userRole = data.user?.role?.toLowerCase();
        if (userRole === 'admin') {
          navigate('/admin');
        } else {
          navigate('/dashboard');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Errore di autenticazione');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch('/api/v1/admin/auth/google/login');

      if (!response.ok) {
        throw new Error('Errore di connessione');
      }

      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (err: any) {
      setError(err.message || 'Errore di connessione a Google');
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen flex items-center justify-center ${SPACING.padding.full} py-12 relative overflow-hidden ${isDark ? 'bg-neutral-950' : 'bg-gray-50'}`}>

      {/* Top Right Controls */}
      <div className="absolute top-6 right-6 z-20 flex items-center gap-4">
        <LanguageSelector />
        <button
          onClick={toggleTheme}
          className={`p-2 rounded-full transition-colors ${isDark ? 'bg-white/10 hover:bg-white/20 text-white' : 'bg-black/5 hover:bg-black/10 text-gray-900'}`}
          aria-label="Toggle Theme"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
      </div>

      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className={`absolute top-0 left-1/4 w-96 h-96 bg-gold rounded-full blur-3xl ${isDark ? 'opacity-5' : 'opacity-10'}`}
          animate={{ scale: [1, 1.2, 1], x: [0, 50, 0], y: [0, 30, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className={`absolute bottom-0 right-1/4 w-96 h-96 bg-gold rounded-full blur-3xl ${isDark ? 'opacity-5' : 'opacity-10'}`}
          animate={{ scale: [1.2, 1, 1.2], x: [0, -50, 0], y: [0, -30, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        />
      </div>

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-4 flex flex-col items-center"
          >
             {/* Logo Images */}
            <div className="flex justify-center mb-6">
               <img
                  src="/markettina-icon.png"
                  alt="Markettina Logo"
                  className="h-24 w-auto object-contain drop-shadow-xl"
               />
            </div>

            <h1 className={`text-5xl font-light mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              <span className="text-gold font-semibold">MARKETTINA</span>
            </h1>
            <div className="h-1 w-24 bg-gradient-to-r from-transparent via-gold to-transparent mx-auto" />
          </motion.div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className={isDark ? 'text-gray-400 text-sm' : 'text-gray-500 text-sm'}
          >
            Accedi alla piattaforma
          </motion.p>
        </div>

        {/* Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={`backdrop-blur-xl rounded-3xl p-8 shadow-2xl ${isDark
            ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
            : 'bg-white border border-gray-200'
            }`}
        >
          <div className="space-y-6">
            {/* Login Type Selector */}
            <div className="flex gap-2 p-1 bg-black/20 rounded-lg">
              <button
                type="button"
                onClick={() => setLoginType('user')}
                className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                  loginType === 'user'
                    ? 'bg-gold text-black'
                    : isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Users className="h-4 w-4" />
                Cliente
              </button>
              <button
                type="button"
                onClick={() => setLoginType('admin')}
                className={`flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                  loginType === 'admin'
                    ? 'bg-gold text-black'
                    : isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <ShieldCheck className="h-4 w-4" />
                Admin
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/30 rounded-lg"
              >
                <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                <p className="text-sm text-red-400">{error}</p>
              </motion.div>
            )}

            {/* Login Form */}
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Email
                </label>
                <div className="relative">
                  <Mail className={`absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={loginType === 'admin' ? 'admin@esempio.com' : 'cliente@esempio.com'}
                    required
                    className={`w-full pl-10 pr-4 py-3 rounded-lg border transition-colors ${
                      isDark
                        ? 'bg-white/5 border-white/10 text-white placeholder-gray-500 focus:border-gold'
                        : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400 focus:border-gold'
                    } focus:outline-none focus:ring-2 focus:ring-gold/20`}
                  />
                </div>
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Password
                </label>
                <div className="relative">
                  <Lock className={`absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className={`w-full pl-10 pr-12 py-3 rounded-lg border transition-colors ${
                      isDark
                        ? 'bg-white/5 border-white/10 text-white placeholder-gray-500 focus:border-gold'
                        : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400 focus:border-gold'
                    } focus:outline-none focus:ring-2 focus:ring-gold/20`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className={`absolute right-3 top-1/2 -translate-y-1/2 ${isDark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'}`}
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-4 bg-gradient-to-r from-gold to-gold-light text-black font-semibold rounded-lg hover:shadow-[0_0_30px_rgba(212,175,55,0.3)] transition-all duration-300 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                    Accesso in corso...
                  </>
                ) : (
                  'Accedi'
                )}
              </motion.button>
            </form>

            {/* Admin Google Login Option */}
            {loginType === 'admin' && (
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className={`w-full border-t ${isDark ? 'border-white/10' : 'border-gray-200'}`} />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className={`px-4 ${isDark ? 'bg-[#1a1a1a] text-gray-400' : 'bg-white text-gray-500'}`}>
                      oppure
                    </span>
                  </div>
                </div>

                <motion.button
                  type="button"
                  onClick={handleGoogleLogin}
                  disabled={loading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full py-3 rounded-lg border transition-all flex items-center justify-center gap-3 disabled:opacity-50 ${
                    isDark
                      ? 'border-white/20 text-white hover:bg-white/5'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  Accedi con Google
                </motion.button>
              </>
            )}

            {/* Info */}
            <p className={`text-center text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
              {loginType === 'admin'
                ? 'Accesso riservato al team MARKETTINA'
                : 'Accedi per gestire il tuo account'}
            </p>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className={`text-center text-sm mt-8 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}
        >
          AI-Powered Development Made in Italy
        </motion.p>
      </motion.div>
    </div>
  );
}
