#!/bin/bash
# Docker Health Check Script

echo "🔍 ETL Pipeline Docker Health Check"
echo "===================================="
echo ""

# Check Docker installation
echo "1️⃣  Docker Installation:"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "   ✓ $DOCKER_VERSION"
else
    echo "   ✗ Docker not found. Install Docker Desktop."
    exit 1
fi

echo ""
echo "2️⃣  Docker Daemon:"
if docker info &> /dev/null; then
    echo "   ✓ Docker daemon is running"
else
    echo "   ✗ Docker daemon is not running"
    exit 1
fi

echo ""
echo "3️⃣  Docker Compose:"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "   ✓ $COMPOSE_VERSION"
else
    echo "   ✗ Docker Compose not found"
    exit 1
fi

echo ""
echo "4️⃣  Service Status:"
if docker-compose ps &> /dev/null; then
    echo "   ✓ Services defined"
    echo ""
    docker-compose ps
else
    echo "   ℹ Services not started yet (this is OK)"
fi

echo ""
echo "5️⃣  Docker Images:"
docker images --filter "reference=*etl*" --filter "reference=*postgres*"

echo ""
echo "✅ Health check complete!"
echo ""
echo "📝 To get started:"
echo "   1. Run: ./docker-start.sh (Linux/Mac) or docker-start.bat (Windows)"
echo "   2. Or:  docker-compose up -d"
echo "   3. Check http://localhost:5050 for PgAdmin"
