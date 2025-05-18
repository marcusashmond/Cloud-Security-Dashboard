#!/bin/bash
# Quick start script for the Cloud Security Dashboard

echo "========================================"
echo "Cloud Security Dashboard - Quick Start"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Navigate to docker directory
cd "$(dirname "$0")/docker"

echo "📦 Building and starting containers..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📊 Initializing database with sample data..."
docker-compose exec backend python scripts/init_db.py

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "🌐 Access the dashboard:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 Useful commands:"
echo "   Stop:    docker-compose -f docker/docker-compose.yml down"
echo "   Logs:    docker-compose -f docker/docker-compose.yml logs -f"
echo "   Restart: docker-compose -f docker/docker-compose.yml restart"
echo ""
