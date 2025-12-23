# 🚀 Installation Guide - StudiocentOS

**Last Updated**: November 5, 2025  
**Version**: 1.0.0  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Automatic Installation](#automatic-installation)
3. [Manual Installation](#manual-installation)
4. [Environment Configuration](#environment-configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+, Arch Linux) or macOS
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk**: 20GB free space
- **CPU**: 4 cores minimum

### Required Software

- **Docker** 24.0+ & Docker Compose 2.0+
- **PostgreSQL** 16+
- **Redis** 7+
- **Python** 3.12+
- **Node.js** 20+

---

## ⚡ Automatic Installation

### Quick Start (Recommended)

Use the automated installation script for a complete setup:

```bash
cd /home/ciroautuori/Scrivania/studiocentos/docs/scripts
chmod +x install-all.sh
./install-all.sh
```

This script will:
- ✅ Install system dependencies (Docker, PostgreSQL, Redis)
- ✅ Configure Docker daemon
- ✅ Install UV (Python package manager)
- ✅ Install pnpm (Node package manager)
- ✅ Setup PostgreSQL database
- ✅ Setup Redis cache
- ✅ Build Docker images

**Estimated Time**: 15-20 minutes

---

## 🛠️ Manual Installation

### Step 1: Install System Dependencies

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install base dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install PostgreSQL, Redis, Make
sudo apt install -y make postgresql postgresql-contrib redis-server
```

#### Arch Linux

```bash
# Install Docker
sudo pacman -S docker docker-compose

# Install PostgreSQL, Redis, Make
sudo pacman -S postgresql redis make
```

### Step 2: Configure Docker

```bash
# Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes (or logout/login)
newgrp docker
```

### Step 3: Install UV (Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Verify installation
uv --version
```

### Step 4: Install pnpm (Node Package Manager)

```bash
# Install Node.js if not present
sudo pacman -S nodejs npm  # Arch
# or
sudo apt install -y nodejs npm  # Ubuntu

# Install pnpm globally
npm install -g pnpm

# Verify installation
pnpm --version
```

### Step 5: Setup PostgreSQL

```bash
# Initialize database (Arch Linux)
sudo -u postgres initdb -D /var/lib/postgres/data

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER studiocentos WITH PASSWORD 'studiocentos2025';
CREATE DATABASE studiocentos OWNER studiocentos;
GRANT ALL PRIVILEGES ON DATABASE studiocentos TO studiocentos;
ALTER USER studiocentos CREATEDB;
EOF
```

### Step 6: Setup Redis

```bash
# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Verify Redis is running
redis-cli ping  # Should return PONG
```

### Step 7: Clone Repository

```bash
cd /home/ciroautuori/Scrivania
git clone https://github.com/yourusername/studiocentos.git
cd studiocentos
```

---

## ⚙️ Environment Configuration

### Backend Environment Variables

Create `.env` file in `apps/backend/`:

```bash
cd apps/backend
cp .env.example .env
nano .env
```

**Minimum Required Configuration**:

```bash
# Environment
ENVIRONMENT=development
DEBUG=True

# Database
DATABASE_URL=postgresql://studiocentos:studiocentos2025@localhost:5432/studiocentos

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (Generate new key!)
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_PREFIX=/api
APP_NAME=StudiocentOS
VERSION=1.0.0
```

### AI Microservice Environment Variables

Create `.env` file in `apps/ai_microservice/`:

```bash
cd apps/ai_microservice
cp .env.example .env
nano .env
```

**Minimum Required Configuration**:

```bash
# AI Provider API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database (shared with backend)
DATABASE_URL=postgresql://studiocentos:studiocentos2025@localhost:5432/studiocentos

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Frontend Environment Variables

Create `.env` file in `apps/frontend/`:

```bash
cd apps/frontend
cp .env.example .env
nano .env
```

```bash
VITE_API_URL=http://localhost:8000
VITE_AI_SERVICE_URL=http://localhost:8001
```

---

## ✅ Verification

### Check Installations

```bash
# Docker
docker --version
docker compose version

# PostgreSQL
psql --version
sudo systemctl status postgresql

# Redis
redis-cli --version
sudo systemctl status redis

# UV
uv --version

# pnpm
pnpm --version
```

### Test Database Connection

```bash
psql -U studiocentos -d studiocentos -h localhost
# Password: studiocentos2025
```

### Test Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

---

## 🐛 Troubleshooting

### Docker Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes
newgrp docker

# Or logout and login again
```

### PostgreSQL Connection Refused

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check port
sudo netstat -tuln | grep 5432
```

### Redis Connection Refused

```bash
# Check if Redis is running
sudo systemctl status redis

# Start Redis
sudo systemctl start redis

# Check port
sudo netstat -tuln | grep 6379
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
kill -9 <PID>
```

---

## 📚 Next Steps

After successful installation:

1. **[Quick Start Guide](quick-start.md)** - Start all services
2. **[Docker Setup](docker-setup.md)** - Docker-based development
3. **[Development Guide](../guides/development.md)** - Development workflow

---

## 🆘 Need Help?

- 📖 **Documentation**: [docs/](../)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/studiocentos/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/studiocentos/discussions)
- 📧 **Email**: ciro@studiocentos.it
