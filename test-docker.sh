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
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi

if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ docker-compose.prod.yml not found"
    exit 1
fi

echo "✅ Docker Compose files found"

# Check if Dockerfiles exist
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found"
    exit 1
fi

if [ ! -f "frontend/Dockerfile" ]; then
    echo "❌ frontend/Dockerfile not found"
    exit 1
fi

echo "✅ Dockerfiles found"

# Check if nginx config exists
if [ ! -f "nginx/nginx.conf" ]; then
    echo "❌ nginx/nginx.conf not found"
    exit 1
fi

echo "✅ Nginx configuration found"

# Check if deployment script exists and is executable
if [ ! -f "deploy.sh" ]; then
    echo "❌ deploy.sh not found"
    exit 1
fi

if [ ! -x "deploy.sh" ]; then
    echo "❌ deploy.sh is not executable"
    exit 1
fi

echo "✅ Deployment script found and executable"

# Check if environment template exists
if [ ! -f "env.production.example" ]; then
    echo "❌ env.production.example not found"
    exit 1
fi

echo "✅ Environment template found"

echo ""
echo "🎉 All Docker setup files are present and ready!"
echo ""
echo "Next steps:"
echo "1. For development: docker-compose up --build"
echo "2. For production: cp env.production.example .env.production && ./deploy.sh production"
echo ""
echo "Your Docker CD setup is complete! 🚀"
