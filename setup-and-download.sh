#!/bin/bash
# Setup and download script for Canvas course 2879
# This script configures canvas_grab and downloads course materials

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📚 Canvas Course 2879 Download Setup${NC}"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Source environment to get CANVAS_TOKEN
source ~/.zshrc 2>/dev/null || true

if [ -z "$CANVAS_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  CANVAS_TOKEN not found in environment${NC}"
    echo "Please ensure the token is set in ~/.zshrc"
    exit 1
fi

echo -e "${GREEN}✅ Canvas token found${NC}"

# Path to canvas_grab
CANVAS_GRAB_DIR="/Users/a00288946/Projects/canvas_grab"

if [ ! -d "$CANVAS_GRAB_DIR" ]; then
    echo -e "${YELLOW}⚠️  canvas_grab not found at $CANVAS_GRAB_DIR${NC}"
    exit 1
fi

# Activate canvas_grab virtual environment
echo -e "${BLUE}🔧 Activating canvas_grab environment...${NC}"
source "$CANVAS_GRAB_DIR/venv/bin/activate"

# Create config.toml
echo -e "${BLUE}📝 Creating config.toml...${NC}"
cat > config.toml <<EOF
download_folder = "."

[endpoint]
endpoint = "https://usucourses.instructure.com"
api_key = "$CANVAS_TOKEN"

[course_filter]
filter_name = "per"

[course_filter.all_filter]

[course_filter.term_filter]
terms = [-1]

[course_filter.per_filter]
course_id = [2879]

[organize_mode]
mode = "module_link"
delete_file = false

[file_filter]
allowed_group = ["Image", "Document"]
allowed_extra = []
EOF

echo -e "${GREEN}✅ Configuration file created${NC}"

# Run canvas_grab
echo -e "${BLUE}📥 Starting download of course 2879...${NC}"
echo "This may take a while depending on the number of files..."
echo ""

cd "$CANVAS_GRAB_DIR"
python main.py -c "$SCRIPT_DIR/config.toml" -o "$SCRIPT_DIR" -I -k

echo ""
echo -e "${GREEN}✅ Download complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review downloaded files in: $SCRIPT_DIR"
echo "2. Initialize git repo: git init"
echo "3. Add files: git add ."
echo "4. Commit: git commit -m 'Initial course materials'"
echo "5. Add remote: git remote add origin https://github.com/gjoeckel/canvas_2879.git"
echo "6. Push: git push -u origin main"

