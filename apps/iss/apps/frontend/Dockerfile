# Frontend Dockerfile for ISS - Innovazione Sociale Salernitana
# Multi-stage build ottimizzato per produzione

# Build stage
FROM node:20-alpine AS builder

# Installa dipendenze di sistema per build
RUN apk add --no-cache git python3 make g++

# Installa pnpm globalmente
RUN corepack enable && corepack prepare pnpm@9.0.0 --activate

# Set working directory
WORKDIR /app

# Copia solo i file di configurazione per cache layer
COPY package.json pnpm-lock.yaml* ./
COPY tsconfig.json tsconfig.node.json vite.config.ts tailwind.config.ts postcss.config.js ./

# Installa dipendenze (layer cacheable)
RUN pnpm install --frozen-lockfile --prefer-offline

# Crea directory public se non esiste
RUN mkdir -p public

# Copia il codice sorgente
COPY src/ ./src/
COPY index.html ./
COPY public/ ./public/

# Build ottimizzato per produzione
ENV NODE_ENV=production
ENV VITE_API_BASE_URL=/api/v1
RUN pnpm build && \
  # Rimuovi source maps per sicurezza
  find dist -name "*.map" -delete && \
  # Comprimi ulteriormente i file
  find dist -name "*.js" -exec gzip -k {} \; && \
  find dist -name "*.css" -exec gzip -k {} \;

# Production stage - Server statico leggero
FROM node:20-alpine AS production

# Installa serve globalmente
RUN npm install -g serve

# Copia build dal builder
COPY --from=builder /app/dist /app

# Crea utente non-root
RUN addgroup -g 1001 -S appuser && \
  adduser -S appuser -u 1001 -G appuser && \
  chown -R appuser:appuser /app

USER appuser
WORKDIR /app

# Esponi porta
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/index.html || exit 1

# Avvia serve con SPA fallback
CMD ["serve", "-s", ".", "-l", "3000"]
