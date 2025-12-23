# ================================
# Stage 1: Dependencies - Install with pnpm
# ================================
FROM node:20-alpine as deps

# Enable pnpm (latest version for performance)
RUN corepack enable && corepack prepare pnpm@10.23.0 --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install ALL dependencies (use --no-frozen-lockfile to allow minor lockfile updates)
RUN pnpm install --no-frozen-lockfile

# ================================
# Stage 2: Builder - Build optimized application
# ================================
FROM node:20-alpine as builder

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@10.23.0 --activate

WORKDIR /app

# Copy dependencies from deps stage (layer caching)
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build arguments for environment
ARG VITE_API_URL=/api
ARG VITE_API_BASE_URL
ARG NODE_ENV=production

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV NODE_ENV=$NODE_ENV

# Build for production with optimizations
# - Bundle splitting with 9 vendor chunks
# - Minification with Ter terser
# - PWA generation with service worker
# - Image optimization
# - Tree-shaking
RUN pnpm build:prod

# Verify build output
RUN ls -la dist/

# ================================
# Stage 3: Production - Nginx with PWA + Mobile optimization
# ================================
FROM nginx:alpine

# Install tools for healthcheck
RUN apk add --no-cache curl

# Copy built files from builder
# Includes:
# - Optimized JS bundles (9 vendor chunks)
# - PWA assets (manifest, service worker, icons)
# - Static assets (images, fonts)
# - index.html with preload hints
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy optimized nginx configuration
# Includes:
# - Gzip compression
# - Brotli compression (if enabled)
# - Cache headers for static assets
# - PWA headers (manifest, service worker)
# - Security headers
# - Mobile-optimized settings
COPY nginx.prod.conf /etc/nginx/conf.d/default.conf

# Create nginx cache directories
RUN mkdir -p /var/cache/nginx/client_temp && \
    mkdir -p /var/cache/nginx/proxy_temp && \
    mkdir -p /var/cache/nginx/fastcgi_temp && \
    mkdir -p /var/cache/nginx/uwsgi_temp && \
    mkdir -p /var/cache/nginx/scgi_temp && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Optimize for production
# - Set proper permissions
# - Remove unnecessary files
RUN find /usr/share/nginx/html -type f -name "*.map" -delete && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \; && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \;

# Expose port
EXPOSE 80

# Enhanced health check for PWA
# Use nginx -t for config validation (avoids redirect issues with HTTPS)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD nginx -t 2>/dev/null || exit 1

# Labels for production tracking
LABEL maintainer="IronRep Team"
LABEL version="1.0.0"
LABEL description="IronRep Frontend - Mobile-Optimized PWA"
LABEL optimization="Bundle splitting, PWA, Offline-first"

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
