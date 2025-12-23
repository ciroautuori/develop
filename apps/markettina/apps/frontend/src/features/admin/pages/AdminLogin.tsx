/**
 * Admin Login - STUDIOCENTOS Brand Design
 * SOLO Google OAuth - Accesso riservato a studiocentos089@gmail.com
 */
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertCircle, Shield } from 'lucide-react';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { STORAGE_KEYS, SPACING } from '../../../shared/config/constants';

export function AdminLogin() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Handle OAuth callback (token in URL)
  useEffect(() => {
    const token = searchParams.get('token');
    const adminId = searchParams.get('admin_id');
    const oauthError = searchParams.get('error');

    if (oauthError) {
      if (oauthError === 'unauthorized_account') {
        setError('Accesso non autorizzato. Solo studiocentos089@gmail.com può accedere.');
      } else {
        setError(`Errore Google: ${oauthError}`);
      }
      return;
    }

    if (token && adminId) {
      localStorage.setItem(STORAGE_KEYS.adminToken, token);
      localStorage.setItem('admin_id', adminId);
      navigate('/admin');
    }
  }, [searchParams, navigate]);

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
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-6"
          >
            <h1 className={`text-5xl font-light mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              STUDIO<span className="text-gold font-semibold">CENTOS</span>
            </h1>
            <div className="h-1 w-24 bg-gradient-to-r from-transparent via-gold to-transparent mx-auto" />
          </motion.div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className={isDark ? 'text-gray-400 text-sm' : 'text-gray-500 text-sm'}
          >
            Admin Panel
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
            {/* Security Badge */}
            <div className="flex items-center justify-center gap-2 mb-4">
              <Shield className="h-5 w-5 text-gold" />
              <span className={`text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                Accesso Riservato
              </span>
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

            {/* Google Sign In Button */}
            <motion.button
              type="button"
              onClick={handleGoogleLogin}
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 bg-gradient-to-r from-gold to-gold-light text-black font-semibold rounded-lg hover:shadow-[0_0_30px_rgba(212,175,55,0.3)] transition-all duration-300 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                  Connessione a Google...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  Accedi con Google
                </>
              )}
            </motion.button>

            {/* Info */}
            <p className={`text-center text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
              Solo account autorizzato può accedere
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
