#!/bin/bash
# Quick Docker Startup Script for ETL Pipeline

set -e

echo "╔════════════════════════════════════════════╗"
echo "║   ETL Pipeline Docker Startup              ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi

echo "✓ Docker is installed"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "✓ Docker daemon is running"
echo ""

# Build images
echo "🔨 Building Docker images..."
docker-compose build --quiet

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✓ Docker build successful"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Docker start failed"
    exit 1
fi

echo "✓ Services started"
echo ""

# Wait for databases to be healthy
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Check services status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ ETL Pipeline is running!"
echo ""
echo "🌐 Access Points:"
echo "   • Source DB:  localhost:5432"
echo "   • Target DB:  localhost:5433"
echo "   • PgAdmin:    http://localhost:5050"
echo "     (admin@example.com / admin)"
echo ""
echo "📝 View Logs:"
echo "   docker-compose logs -f etl_pipeline"
echo "   docker-compose logs -f etl_scheduler"
echo ""
echo "🛑 Stop Services:"
echo "   docker-compose down"
