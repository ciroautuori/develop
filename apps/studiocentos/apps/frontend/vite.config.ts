import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Pre-rendering configurato via Nginx + Prerender.io per SEO
// Vedi: /etc/nginx/conf.d/prerender.conf

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/app': path.resolve(__dirname, './src/app'),
      '@/shared': path.resolve(__dirname, './src/shared'),
      '@/features': path.resolve(__dirname, './src/features'),
      '@/components': path.resolve(__dirname, './src/shared/components'),
      '@/lib': path.resolve(__dirname, './src/shared/lib'),
      '@/hooks': path.resolve(__dirname, './src/shared/hooks'),
      '@/services': path.resolve(__dirname, './src/shared/services'),
      '@/types': path.resolve(__dirname, './src/shared/types'),
      '@/assets': path.resolve(__dirname, './src/app/assets'),
      '@/styles': path.resolve(__dirname, './src/app/assets/styles'),
    },
  },
  server: {
    port: 3000,
    host: true,
    allowedHosts: [
      'localhost',
      '.duckdns.org',
      'studiocentos.duckdns.org',
      'cv-lab.duckdns.org',
      'phoenix-ai.duckdns.org',
      '34.76.145.209',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    port: 3000,
    host: true,
  },
  build: {
    target: 'esnext',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          motion: ['framer-motion'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
          query: ['@tanstack/react-query'],
          state: ['zustand'],
          utils: ['zod', 'clsx', 'tailwind-merge'],
        },
      },
    },
  },
  optimizeDeps: {
    exclude: ['framer-motion'],
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
