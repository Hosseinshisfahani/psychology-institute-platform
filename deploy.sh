#!/bin/bash

# Manual Deployment Script for Psychology Institute
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is provided
ENVIRONMENT=${1:-production}

if [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "development" ]; then
    print_error "Invalid environment. Use 'production' or 'development'"
    exit 1
fi

print_status "Starting deployment for $ENVIRONMENT environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose file exists
COMPOSE_FILE="docker-compose.yml"
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    
    # Check if production env file exists
    if [ ! -f ".env.production" ]; then
        print_warning ".env.production not found. Creating from template..."
        if [ -f "env.production.example" ]; then
            cp env.production.example .env.production
            print_warning "Please edit .env.production with your actual values before deploying!"
            print_warning "Run: nano .env.production"
            exit 1
        else
            print_error "env.production.example not found. Cannot create production environment file."
            exit 1
        fi
    fi
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p backups
mkdir -p logs

# Pull latest code (if in git repository)
if [ -d ".git" ]; then
    print_status "Pulling latest code from git..."
    git pull origin main || print_warning "Failed to pull latest code. Continuing with current code..."
fi

# Build and start services
print_status "Building and starting services..."
docker-compose -f $COMPOSE_FILE down --remove-orphans
docker-compose -f $COMPOSE_FILE build --no-cache
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check Django
if docker-compose -f $COMPOSE_FILE exec -T django python -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" 2>/dev/null; then
    print_success "Django service is healthy"
else
    print_warning "Django health check failed. Check logs with: docker-compose -f $COMPOSE_FILE logs django"
fi

# Check Frontend
if docker-compose -f $COMPOSE_FILE exec -T frontend wget --no-verbose --tries=1 --spider http://localhost/ 2>/dev/null; then
    print_success "Frontend service is healthy"
else
    print_warning "Frontend health check failed. Check logs with: docker-compose -f $COMPOSE_FILE logs frontend"
fi

# Check Nginx (production only)
if [ "$ENVIRONMENT" = "production" ]; then
    if docker-compose -f $COMPOSE_FILE exec -T nginx wget --no-verbose --tries=1 --spider http://localhost/ 2>/dev/null; then
        print_success "Nginx service is healthy"
    else
        print_warning "Nginx health check failed. Check logs with: docker-compose -f $COMPOSE_FILE logs nginx"
    fi
fi

# Create database backup (production only)
if [ "$ENVIRONMENT" = "production" ]; then
    print_status "Creating database backup..."
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
    if docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U postgres psychology_institute > $BACKUP_FILE 2>/dev/null; then
        print_success "Database backup created: $BACKUP_FILE"
        
        # Keep only last 7 backups
        cd backups && ls -t backup_*.sql | tail -n +8 | xargs -r rm && cd ..
    else
        print_warning "Database backup failed. Check database connection."
    fi
fi

# Show service status
print_status "Service status:"
docker-compose -f $COMPOSE_FILE ps

# Show access information
print_status "Deployment completed!"
echo ""
if [ "$ENVIRONMENT" = "production" ]; then
    print_success "Your application is running at:"
    echo "  - http://mrbone.ir (or your server IP)"
    echo "  - Admin: http://mrbone.ir/admin/"
    echo "  - API: http://mrbone.ir/api/"
else
    print_success "Your application is running at:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend: http://localhost:8000"
    echo "  - Admin: http://localhost:8000/admin/"
fi

echo ""
print_status "Useful commands:"
echo "  - View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "  - Stop services: docker-compose -f $COMPOSE_FILE down"
echo "  - Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "  - Access Django shell: docker-compose -f $COMPOSE_FILE exec django python manage.py shell"
echo "  - Create superuser: docker-compose -f $COMPOSE_FILE exec django python manage.py createsuperuser"

if [ "$ENVIRONMENT" = "production" ]; then
    echo "  - Database backup: docker-compose -f $COMPOSE_FILE exec postgres pg_dump -U postgres psychology_institute > backup.sql"
    echo "  - SSL setup: See README.md for Let's Encrypt setup"
fi

print_success "Deployment completed successfully!"
