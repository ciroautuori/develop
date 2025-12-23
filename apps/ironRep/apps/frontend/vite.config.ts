import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { TanStackRouterVite } from "@tanstack/router-vite-plugin";
import { VitePWA } from "vite-plugin-pwa";
import { visualizer } from "rollup-plugin-visualizer";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    TanStackRouterVite(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.ico", "apple-touch-icon.png", "robots.txt"],
      manifest: {
        name: "IronRep - AI Medical Coach",
        short_name: "IronRep",
        description:
          "AI-Powered Medical Coach for CrossFit Recovery & Rehabilitation",
        theme_color: "#000000",
        background_color: "#ffffff",
        display: "standalone",
        orientation: "portrait",
        scope: "/",
        start_url: "/",
        icons: [
          {
            src: "pwa-192x192.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      workbox: {
        skipWaiting: true,
        clientsClaim: true,
        cleanupOutdatedCaches: true,
        globPatterns: ["**/*.{js,css,ico,png,svg,woff2,webmanifest}"],
        navigateFallback: "/index.html",
        maximumFileSizeToCacheInBytes: 3 * 1024 * 1024, // 3 MB limit
        globIgnores: ["**/stats.html", "**/index.html"], // Exclude stats.html + index.html from precaching
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith("/api/"),
            handler: "NetworkOnly",
            options: {
              cacheName: "api-no-cache",
            },
          },
          {
            urlPattern: /^https:\/\/api\..*/i,
            handler: "NetworkFirst",
            options: {
              cacheName: "api-cache-v2",
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60, // 1 hour
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
      },
      devOptions: {
        enabled: false, // Set to true to test PWA in dev mode
      },
    }),
    // Bundle analyzer (only in analyze mode)
    visualizer({
      filename: "./dist/stats.html",
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // Code splitting optimization
    rollupOptions: {
      output: {
        manualChunks: {
          // React core
          'vendor-react': ['react', 'react-dom'],

          // Router
          'vendor-router': ['@tanstack/react-router'],

          // Query
          'vendor-query': ['@tanstack/react-query'],

          // Charts (heavy library)
          'vendor-charts': ['recharts'],

          // Animation (heavy library)
          'vendor-animation': ['framer-motion'],

          // UI components
          'vendor-ui': [
            'lucide-react',
            '@radix-ui/react-slot',
            '@radix-ui/react-tabs',
            '@radix-ui/react-progress',
          ],

          // Forms
          'vendor-forms': [
            'react-hook-form',
            '@hookform/resolvers',
            'zod',
          ],

          // Utilities
          'vendor-utils': [
            'axios',
            'date-fns',
            'clsx',
            'tailwind-merge',
            'class-variance-authority',
          ],
        },
      },
    },

    // Chunk size warnings
    chunkSizeWarningLimit: 1000,

    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },

    // Source maps (disable in production for smaller bundles)
    sourcemap: false,
  },

  // Optimization for mobile
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@tanstack/react-router',
      '@tanstack/react-query',
    ],
  },
});
