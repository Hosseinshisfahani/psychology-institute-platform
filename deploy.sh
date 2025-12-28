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

# Stop any running development servers that might consume memory
print_status "Checking for running development servers..."
DEV_SERVER_PIDS=$(pgrep -f "react-scripts.*start" || true)
if [ -n "$DEV_SERVER_PIDS" ]; then
    print_warning "Found running development server(s). Stopping to free memory..."
    echo "$DEV_SERVER_PIDS" | xargs kill -9 2>/dev/null || true
    sleep 2
    print_success "Development server(s) stopped"
else
    print_status "No development servers running"
fi

# Also check for TypeScript checker processes
TS_CHECKER_PIDS=$(pgrep -f "fork-ts-checker-webpack-plugin" || true)
if [ -n "$TS_CHECKER_PIDS" ]; then
    print_warning "Found TypeScript checker processes. Stopping to free memory..."
    echo "$TS_CHECKER_PIDS" | xargs kill -9 2>/dev/null || true
    sleep 1
fi

print_status "Installing dependencies (if needed)..."
if [ ! -d "node_modules" ]; then
    npm install --legacy-peer-deps
else
    print_status "Dependencies already installed, skipping..."
fi

print_status "Checking system resources..."
print_status "Available memory:"
free -h
print_status "Disk space:"
df -h "$FRONTEND_DIR" | tail -1

# Check if swap is available
if swapon --show | grep -q .; then
    print_success "Swap space is available"
    swapon --show
else
    print_warning "No swap space detected. Consider adding swap for builds."
fi

# Calculate available memory and set appropriate Node.js memory limit
# Get available memory in MB (free + buffers/cache)
AVAILABLE_MEM_MB=$(free -m | awk 'NR==2{printf "%.0f", $7}')
TOTAL_MEM_MB=$(free -m | awk 'NR==2{print $2}')

# Calculate safe memory limit (use 70% of available or max 2.5GB, whichever is smaller)
# Leave some memory for system processes
if [ "$AVAILABLE_MEM_MB" -gt 2500 ]; then
    NODE_MEM_LIMIT=2500
elif [ "$AVAILABLE_MEM_MB" -gt 1500 ]; then
    # Use 70% of available memory, but cap at 2.5GB
    NODE_MEM_LIMIT=$((AVAILABLE_MEM_MB * 70 / 100))
    # Ensure minimum of 1536MB for builds
    if [ "$NODE_MEM_LIMIT" -lt 1536 ]; then
        NODE_MEM_LIMIT=1536
    fi
else
    # Very low memory - use conservative limit
    NODE_MEM_LIMIT=1536
    print_warning "Low available memory detected. Using conservative memory limit."
fi

print_status "Detected available memory: ${AVAILABLE_MEM_MB}MB (Total: ${TOTAL_MEM_MB}MB)"
print_status "Setting Node.js memory limit to ${NODE_MEM_LIMIT}MB"

# Warn if memory is very low
if [ "$AVAILABLE_MEM_MB" -lt 1000 ]; then
    print_warning "Very low available memory (${AVAILABLE_MEM_MB}MB). Build may fail."
    print_warning "Consider stopping other services or adding more swap space."
fi

# Free up memory before build
print_status "Freeing up memory before build..."
sync
# Try to drop caches (requires root, but won't fail if not possible)
if [ -w /proc/sys/vm/drop_caches ]; then
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
    print_status "System caches cleared"
else
    print_status "Cannot clear system caches (requires root), continuing anyway..."
fi
sleep 1

# Increase Node.js memory limit and disable source maps to save memory
export NODE_OPTIONS="--max-old-space-size=${NODE_MEM_LIMIT}"
export GENERATE_SOURCEMAP=false

# Set production API URL for build (CRITICAL: This ensures production uses correct backend)
export REACT_APP_API_URL=https://sarmadclinic.ir
print_status "Building with production API URL: $REACT_APP_API_URL"

# Build with increased memory and no source maps
print_status "Starting build with ${NODE_MEM_LIMIT}MB memory limit (source maps disabled)..."
print_status "This may take 5-10 minutes depending on server resources..."

if npm run build; then
    print_success "Frontend build completed successfully"
else
    BUILD_EXIT_CODE=$?
    print_error "Frontend build failed (exit code: $BUILD_EXIT_CODE)"
    echo ""
    print_warning "Build failure troubleshooting:"
    echo "  1. Check if process was killed: dmesg | grep -i 'killed process'"
    echo "  2. Check memory usage: free -h"
    echo "  3. Add swap space (if not exists):"
    echo "     sudo fallocate -l 4G /swapfile"
    echo "     sudo chmod 600 /swapfile"
    echo "     sudo mkswap /swapfile"
    echo "     sudo swapon /swapfile"
    echo "     echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab"
    echo "  4. Try building with less memory: export NODE_OPTIONS='--max-old-space-size=2048'"
    echo "  5. Build on a machine with more RAM and copy the build/ folder"
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

