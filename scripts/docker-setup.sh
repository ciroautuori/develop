#!/bin/bash

# ISS Docker Setup Script
# Innovazione Sociale Salernitana - Production Ready

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p data/{postgres,redis,uploads,logs,nginx-logs}
    mkdir -p config/{postgres,redis,nginx,backend}
    
    # Set proper permissions
    chmod 755 data/
    chmod -R 755 data/*/
    chmod -R 644 config/
    
    log_success "Directories created successfully"
}

# Copy environment file
setup_environment() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            log_info "Copying .env.example to .env..."
            cp .env.example .env
            log_warning "Please edit .env file with your configuration before starting services"
        else
            log_error ".env.example file not found"
            exit 1
        fi
    else
        log_info ".env file already exists"
    fi
}

# Build and start services
start_services() {
    log_info "Building and starting ISS services..."
    
    # Build images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    log_success "Services started successfully"
}

# Check service health
check_health() {
    log_info "Checking service health..."
    
    # Wait for services to be ready
    sleep 30
    
    # Check PostgreSQL
    if docker-compose exec -T postgres pg_isready -U postgres -d iss_wbs > /dev/null 2>&1; then
        log_success "PostgreSQL is healthy"
    else
        log_error "PostgreSQL is not healthy"
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis is healthy"
    else
        log_error "Redis is not healthy"
    fi
    
    # Check Backend
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend is not healthy"
    fi
    
    # Check Frontend
    if curl -f http://localhost:3001 > /dev/null 2>&1; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend is not healthy"
    fi
}

# Show service URLs
show_urls() {
    log_info "ISS Services are running at:"
    echo ""
    echo "🌐 Frontend:          http://localhost:3001"
    echo "🔧 Backend API:       http://localhost:8001"
    echo "📊 API Docs:          http://localhost:8001/docs"
    echo "🗄️  Redis Commander:  http://localhost:8082"
    echo "📧 MailHog (dev):     http://localhost:8026"
    echo ""
    log_success "ISS Platform is ready! 🚀"
}

# Main execution
main() {
    echo "🏛️  ISS - Innovazione Sociale Salernitana"
    echo "🐳 Docker Setup Script"
    echo "=================================="
    echo ""
    
    check_docker
    create_directories
    setup_environment
    start_services
    check_health
    show_urls
    
    echo ""
    log_info "To stop services: docker-compose down"
    log_info "To view logs: docker-compose logs -f"
    log_info "To restart: docker-compose restart"
}

# Run main function
main "$@"
