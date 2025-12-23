# ============================================================================
# markettina FRONTEND - Multi-stage Production Dockerfile
# React 18 + TypeScript + Vite + TailwindCSS
# ============================================================================

# Stage 1: Builder - Build React app
FROM node:20-bookworm-slim AS builder

# Build arguments for Vite environment variables
ARG VITE_API_URL
ARG VITE_AI_URL

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /build

# Copy dependency files
COPY apps/frontend/package.json apps/frontend/pnpm-lock.yaml ./

# Install dependencies (allow lockfile update)
RUN pnpm install --no-frozen-lockfile

# Copy source code
COPY apps/frontend /build

# Build for production with environment variables
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_AI_URL=$VITE_AI_URL
RUN pnpm build

# Stage 2: Runtime - Serve with Nginx
FROM nginx:alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy custom nginx config
COPY config/docker/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy built app from builder
COPY --from=builder /build/dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
