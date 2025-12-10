#!/bin/bash
# Run Canvas API server in Docker for stability

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Starting Canvas API Server in Docker${NC}"
echo "=========================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed${NC}"
    echo "Please install docker-compose or use Docker Desktop"
    exit 1
fi

# Check for required config files
if [ ! -f ".box-api-config.json" ]; then
    echo -e "${YELLOW}⚠️  .box-api-config.json not found${NC}"
    echo "The API server needs Box OAuth credentials to work"
    echo "Make sure you've set up OAuth 2.0 (see OAUTH-SETUP-INSTRUCTIONS.md)"
fi

if [ ! -f "config.toml" ]; then
    echo -e "${YELLOW}⚠️  config.toml not found${NC}"
    echo "The API server needs Canvas configuration to work"
fi

# Stop existing container if running
echo -e "${BLUE}🛑 Stopping existing container (if any)...${NC}"
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Build and start the container
echo -e "${BLUE}🔨 Building Docker image...${NC}"
docker-compose build || docker compose build

echo -e "${BLUE}🚀 Starting container...${NC}"
docker-compose up -d || docker compose up -d

# Wait for container to be healthy
echo -e "${BLUE}⏳ Waiting for API server to be ready...${NC}"
sleep 5

# Check health
MAX_ATTEMPTS=12
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API server is running and healthy!${NC}"
        echo ""
        echo "📋 Server Information:"
        echo "   URL: http://localhost:5000"
        echo "   Health: http://localhost:5000/health"
        echo "   API: http://localhost:5000/update-canvas-api"
        echo ""
        echo "📊 Container Status:"
        docker-compose ps || docker compose ps
        echo ""
        echo "💡 Useful Commands:"
        echo "   View logs: docker-compose logs -f"
        echo "   Stop server: docker-compose down"
        echo "   Restart server: docker-compose restart"
        echo ""
        exit 0
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo -e "${YELLOW}   Attempt $ATTEMPT/$MAX_ATTEMPTS...${NC}"
    sleep 2
done

echo -e "${RED}❌ API server did not become healthy${NC}"
echo ""
echo "📋 Container logs:"
docker-compose logs --tail=50 || docker compose logs --tail=50
echo ""
echo "💡 Troubleshooting:"
echo "   1. Check logs: docker-compose logs -f"
echo "   2. Check container status: docker-compose ps"
echo "   3. Verify config files exist: .box-api-config.json, config.toml"
exit 1

