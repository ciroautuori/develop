#!/bin/bash
# 🚀 IronRep Backend Rebuild - FAST
# Usage: ./scripts/deploy/rebuild-backend.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 IRONREP BACKEND REBUILD                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"

cd "$(dirname "$0")/../.."

# 1. Build Docker image
echo ""
echo "🔨 Building backend Docker image..."
docker build -f config/docker/dockerfiles/backend.Dockerfile -t ironrep-backend:latest apps/backend

# 2. Restart container
echo ""
echo "🔄 Restarting backend container..."
cd config/docker
docker-compose -f docker-compose.prod.yml up -d backend

# 3. Wait and check health
echo ""
echo "⏳ Waiting for backend to start (30s)..."
sleep 30

if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is HEALTHY!"
    curl -s http://localhost:8000/health
    echo ""
else
    echo "❌ Backend health check failed!"
    docker logs ironrep-backend-prod --tail 50
    exit 1
fi

echo ""
echo "✅ REBUILD COMPLETE!"
