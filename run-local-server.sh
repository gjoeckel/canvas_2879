#!/bin/bash
# Run local development server for testing Canvas update functionality

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Local Development Server${NC}"
echo "=========================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python 3 not found${NC}"
    exit 1
fi

# Activate canvas_grab virtual environment
CANVAS_GRAB_VENV="/Users/a00288946/Projects/canvas_grab/venv"
if [ ! -d "$CANVAS_GRAB_VENV" ]; then
    echo -e "${YELLOW}⚠️  canvas_grab virtual environment not found${NC}"
    echo "Please ensure canvas_grab is installed"
    exit 1
fi

source "$CANVAS_GRAB_VENV/bin/activate"

# Start the API server in the background
echo -e "${BLUE}📡 Starting API server on port 5000...${NC}"
python3 update-canvas-api.py &
API_PID=$!

# Wait for API server to start
sleep 3

# Check if API server is running
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API server is running${NC}"
else
    echo -e "${YELLOW}⚠️  API server may not be ready yet${NC}"
fi

# Start local web server for docs
echo -e "${BLUE}🌐 Starting local web server on port 8000...${NC}"
echo ""
echo -e "${GREEN}✅ Local development environment ready!${NC}"
echo ""
echo "📋 Access your site at:"
echo "   http://localhost:8000"
echo ""
echo "📡 API server:"
echo "   http://localhost:5000/update-canvas-api"
echo ""
echo "💡 The 'update canvas' button will now work!"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start Python HTTP server for docs
cd docs
python3 -m http.server 8000

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT

