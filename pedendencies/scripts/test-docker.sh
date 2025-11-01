#!/bin/bash

# Test script to verify Docker setup
echo "🐳 Testing Docker setup for Psychology Institute..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose files exist
if [ ! -f "pedendencies/docker-compose.yml" ]; then
    echo "❌ pedendencies/docker-compose.yml not found"
    exit 1
fi

if [ ! -f "pedendencies/docker-compose.prod.yml" ]; then
    echo "❌ pedendencies/docker-compose.prod.yml not found"
    exit 1
fi

echo "✅ Docker Compose files found"

# Check if Dockerfiles exist
if [ ! -f "pedendencies/Dockerfile" ]; then
    echo "❌ pedendencies/Dockerfile not found"
    exit 1
fi

if [ ! -f "frontend/Dockerfile" ]; then
    echo "❌ frontend/Dockerfile not found"
    exit 1
fi

echo "✅ Dockerfiles found"

# Check if nginx config exists
if [ ! -f "pedendencies/nginx/nginx.conf" ]; then
    echo "❌ pedendencies/nginx/nginx.conf not found"
    exit 1
fi

echo "✅ Nginx configuration found"

# Check if deployment script exists and is executable
if [ ! -f "pedendencies/scripts/deploy.sh" ]; then
    echo "❌ pedendencies/scripts/deploy.sh not found"
    exit 1
fi

if [ ! -x "pedendencies/scripts/deploy.sh" ]; then
    echo "❌ pedendencies/scripts/deploy.sh is not executable"
    exit 1
fi

echo "✅ Deployment script found and executable"

# Check if environment template exists
if [ ! -f "pedendencies/env.example" ]; then
    echo "❌ pedendencies/env.example not found"
    exit 1
fi

echo "✅ Environment template found"

echo ""
echo "🎉 All Docker setup files are present and ready!"
echo ""
echo "Next steps:"
echo "1. For development: docker-compose -f pedendencies/docker-compose.yml up --build"
echo "2. For production: cp pedendencies/env.example .env.production && pedendencies/scripts/deploy.sh production"
echo ""
echo "Your Docker CD setup is complete! 🚀"
