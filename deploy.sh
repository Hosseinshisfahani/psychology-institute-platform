#!/bin/bash

# Deployment script for Psychology Institute Platform
# This script rebuilds the frontend and restarts all services

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="/root/psychology-institute-platform"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Service names
BACKEND_SERVICE="psychology-backend.service"
FRONTEND_SERVICE="psychology-frontend.service"
NGINX_SERVICE="nginx"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check service status
check_service_status() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        print_success "$service is running"
        systemctl status "$service" --no-pager -l | head -5
    else
        print_error "$service is not running"
        systemctl status "$service" --no-pager -l | head -10
        return 1
    fi
}

# Start deployment
echo "=========================================="
echo "  Psychology Institute Platform Deployment"
echo "=========================================="
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists npm; then
    print_error "npm is not installed"
    exit 1
fi

if ! command_exists systemctl; then
    print_error "systemctl is not available"
    exit 1
fi

print_success "Prerequisites check passed"
echo ""

# Step 1: Rebuild Frontend
print_status "Step 1: Rebuilding frontend..."
cd "$FRONTEND_DIR" || exit 1

print_status "Installing dependencies (if needed)..."
if [ ! -d "node_modules" ]; then
    npm install --legacy-peer-deps
else
    print_status "Dependencies already installed, skipping..."
fi

print_status "Building frontend (this may take a few minutes)..."
export NODE_OPTIONS="--max-old-space-size=2048"
if npm run build; then
    print_success "Frontend build completed successfully"
else
    print_error "Frontend build failed"
    exit 1
fi

echo ""

# Step 2: Restart Backend Service
print_status "Step 2: Restarting backend service ($BACKEND_SERVICE)..."
if systemctl restart "$BACKEND_SERVICE"; then
    print_success "Backend service restarted"
    sleep 2  # Give service time to start
else
    print_error "Failed to restart backend service"
    exit 1
fi
echo ""

# Step 3: Restart Frontend Service
print_status "Step 3: Restarting frontend service ($FRONTEND_SERVICE)..."
if systemctl restart "$FRONTEND_SERVICE"; then
    print_success "Frontend service restarted"
    sleep 2  # Give service time to start
else
    print_error "Failed to restart frontend service"
    exit 1
fi
echo ""

# Step 4: Restart Nginx
print_status "Step 4: Restarting nginx..."
if systemctl restart "$NGINX_SERVICE"; then
    print_success "Nginx restarted"
    sleep 1
else
    print_error "Failed to restart nginx"
    exit 1
fi
echo ""

# Step 5: Show Results
echo "=========================================="
echo "  Deployment Results"
echo "=========================================="
echo ""

print_status "Checking service statuses..."
echo ""

# Check backend service
echo "--- Backend Service Status ---"
if check_service_status "$BACKEND_SERVICE"; then
    :
else
    print_warning "Backend service may have issues"
fi
echo ""

# Check frontend service
echo "--- Frontend Service Status ---"
if check_service_status "$FRONTEND_SERVICE"; then
    :
else
    print_warning "Frontend service may have issues"
fi
echo ""

# Check nginx service
echo "--- Nginx Service Status ---"
if check_service_status "$NGINX_SERVICE"; then
    :
else
    print_warning "Nginx service may have issues"
fi
echo ""

# Show recent logs
print_status "Recent service logs (last 10 lines):"
echo ""
echo "--- Backend Logs ---"
journalctl -u "$BACKEND_SERVICE" -n 10 --no-pager || true
echo ""
echo "--- Frontend Logs ---"
journalctl -u "$FRONTEND_SERVICE" -n 10 --no-pager || true
echo ""

# Final summary
echo "=========================================="
echo "  Deployment Summary"
echo "=========================================="
echo ""

# Check all services are running
ALL_RUNNING=true

if ! systemctl is-active --quiet "$BACKEND_SERVICE"; then
    print_error "Backend service is not running"
    ALL_RUNNING=false
fi

if ! systemctl is-active --quiet "$FRONTEND_SERVICE"; then
    print_error "Frontend service is not running"
    ALL_RUNNING=false
fi

if ! systemctl is-active --quiet "$NGINX_SERVICE"; then
    print_error "Nginx service is not running"
    ALL_RUNNING=false
fi

echo ""
if [ "$ALL_RUNNING" = true ]; then
    print_success "All services are running successfully!"
    echo ""
    print_status "Deployment completed successfully at $(date)"
    exit 0
else
    print_error "Some services are not running. Please check the logs above."
    exit 1
fi

