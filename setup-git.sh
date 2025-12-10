#!/bin/bash
# Git setup and initial push script for Canvas course 2879

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Git Repository Setup${NC}"
echo "=========================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if git is already initialized
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git repository already initialized${NC}"
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${BLUE}📦 Initializing git repository...${NC}"
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
fi

# Check if files exist
if [ ! "$(ls -A . 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  No files found in directory${NC}"
    echo "Please run ./setup-and-download.sh first to download course materials"
    exit 1
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${BLUE}📝 Creating .gitignore...${NC}"
    cat > .gitignore <<EOF
# Canvas grab files
config.toml
*.pyc
__pycache__/
venv/

# macOS
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
EOF
    echo -e "${GREEN}✅ .gitignore created${NC}"
fi

# Add files
echo -e "${BLUE}📝 Adding files to git...${NC}"
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
else
    echo -e "${BLUE}💾 Creating initial commit...${NC}"
    git commit -m "Initial course materials from Canvas course 2879"
    echo -e "${GREEN}✅ Initial commit created${NC}"
fi

# Check remote
REMOTE_URL="https://github.com/gjoeckel/canvas_2879.git"
if git remote get-url origin &>/dev/null; then
    CURRENT_URL=$(git remote get-url origin)
    if [ "$CURRENT_URL" != "$REMOTE_URL" ]; then
        echo -e "${YELLOW}⚠️  Remote URL mismatch${NC}"
        echo "Current: $CURRENT_URL"
        echo "Expected: $REMOTE_URL"
        read -p "Update remote URL? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote set-url origin "$REMOTE_URL"
            echo -e "${GREEN}✅ Remote URL updated${NC}"
        fi
    else
        echo -e "${GREEN}✅ Remote already configured${NC}"
    fi
else
    echo -e "${BLUE}🔗 Adding remote repository...${NC}"
    git remote add origin "$REMOTE_URL"
    echo -e "${GREEN}✅ Remote added${NC}"
fi

# Set default branch to main
echo -e "${BLUE}🌿 Setting default branch to main...${NC}"
git branch -M main 2>/dev/null || true

# Push to GitHub
echo -e "${BLUE}🚀 Pushing to GitHub...${NC}"
echo "This will push to: $REMOTE_URL"
read -p "Continue with push? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push -u origin main
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
else
    echo -e "${YELLOW}⏭️  Push skipped. Run 'git push -u origin main' when ready${NC}"
fi

echo ""
echo -e "${GREEN}✅ Git setup complete!${NC}"
echo ""
echo "Repository: https://github.com/gjoeckel/canvas_2879"

