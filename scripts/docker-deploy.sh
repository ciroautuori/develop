#!/bin/bash

# ISS Docker Production Deploy Script
# Innovazione Sociale Salernitana - Production Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

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

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if .env exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env file not found. Please create it from .env.example"
        exit 1
    fi
    
    # Check if production environment
    if ! grep -q "ENVIRONMENT=production" "$ENV_FILE"; then
        log_warning "Environment is not set to production"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check Docker
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    
    log_success "Pre-deployment checks passed"
}

# Create backup
create_backup() {
    log_info "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker-compose ps postgres | grep -q "Up"; then
        log_info "Backing up PostgreSQL database..."
        docker-compose exec -T postgres pg_dump -U postgres iss_wbs > "$BACKUP_DIR/postgres_backup.sql"
        log_success "Database backup created"
    fi
    
    # Backup uploads
    if [ -d "data/uploads" ]; then
        log_info "Backing up uploads..."
        cp -r data/uploads "$BACKUP_DIR/"
        log_success "Uploads backup created"
    fi
    
    # Backup configuration
    cp -r config "$BACKUP_DIR/"
    cp "$ENV_FILE" "$BACKUP_DIR/"
    
    log_success "Backup created at $BACKUP_DIR"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest images..."
    docker-compose pull
    log_success "Images updated"
}

# Build and deploy
deploy() {
    log_info "Building and deploying services..."
    
    # Build with no cache for production
    docker-compose build --no-cache --parallel
    
    # Deploy with zero downtime using rolling update
    log_info "Performing rolling update..."
    
    # Update backend first
    docker-compose up -d --no-deps backend
    sleep 30
    
    # Update frontend
    docker-compose up -d --no-deps frontend
    sleep 15
    
    # Update other services
    docker-compose up -d
    
    log_success "Deployment completed"
}

# Health checks
health_checks() {
    log_info "Running health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        # Check backend health
        if curl -f http://localhost:8001/health > /dev/null 2>&1; then
            log_success "Backend is healthy"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Health checks failed after $max_attempts attempts"
            return 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    # Additional checks
    if docker-compose ps | grep -q "Exit"; then
        log_error "Some services have exited"
        docker-compose ps
        return 1
    fi
    
    log_success "All health checks passed"
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old ISS images (keep last 3)
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}" | \
    grep "iss-" | tail -n +4 | awk '{print $3}' | xargs -r docker rmi -f
    
    log_success "Cleanup completed"
}

# Show deployment info
show_deployment_info() {
    log_info "Deployment Information:"
    echo ""
    echo "🚀 ISS Platform - Production Deployment"
    echo "📅 Deployed: $(date)"
    echo "🔧 Environment: $(grep ENVIRONMENT $ENV_FILE | cut -d'=' -f2)"
    echo ""
    echo "🌐 Services:"
    echo "   Frontend:     http://localhost:$(grep FRONTEND_PORT $ENV_FILE | cut -d'=' -f2 | head -1)"
    echo "   Backend API:  http://localhost:$(grep BACKEND_PORT $ENV_FILE | cut -d'=' -f2 | head -1)"
    echo "   Proxy:        http://localhost:$(grep PROXY_PORT $ENV_FILE | cut -d'=' -f2 | head -1)"
    echo ""
    echo "📊 Monitoring:"
    docker-compose ps
    echo ""
    log_success "ISS Platform deployed successfully! 🎉"
}

# Rollback function
rollback() {
    log_warning "Rolling back to previous version..."
    
    if [ -z "$1" ]; then
        log_error "Please specify backup directory for rollback"
        exit 1
    fi
    
    local backup_dir="$1"
    
    if [ ! -d "$backup_dir" ]; then
        log_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    # Stop services
    docker-compose down
    
    # Restore database
    if [ -f "$backup_dir/postgres_backup.sql" ]; then
        log_info "Restoring database..."
        docker-compose up -d postgres
        sleep 30
        docker-compose exec -T postgres psql -U postgres -d iss_wbs < "$backup_dir/postgres_backup.sql"
    fi
    
    # Restore uploads
    if [ -d "$backup_dir/uploads" ]; then
        log_info "Restoring uploads..."
        rm -rf data/uploads
        cp -r "$backup_dir/uploads" data/
    fi
    
    # Restore configuration
    cp "$backup_dir/.env" .
    
    # Restart services
    docker-compose up -d
    
    log_success "Rollback completed"
}

# Main execution
main() {
    echo "🏛️  ISS - Innovazione Sociale Salernitana"
    echo "🚀 Production Deployment Script"
    echo "=================================="
    echo ""
    
    case "${1:-deploy}" in
        "deploy")
            pre_deployment_checks
            create_backup
            pull_images
            deploy
            health_checks
            cleanup
            show_deployment_info
            ;;
        "rollback")
            rollback "$2"
            ;;
        "backup")
            create_backup
            ;;
        "health")
            health_checks
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|backup|health}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full production deployment (default)"
            echo "  rollback - Rollback to specified backup"
            echo "  backup   - Create backup only"
            echo "  health   - Run health checks only"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
