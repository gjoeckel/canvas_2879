#!/bin/bash
# Helper script to apply custom CSS to downloaded Canvas pages

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🎨 Custom CSS Application"
echo "========================="
echo ""
echo "Options:"
echo "1. Download Canvas CSS automatically"
echo "2. Use a custom CSS file"
echo "3. Embed CSS content directly"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📥 Downloading Canvas CSS and applying to pages..."
        source ~/.zshrc
        python3 download-page-content.py --download-canvas-css
        ;;
    2)
        read -p "Enter path to CSS file (relative to project root): " css_file
        if [ ! -f "$css_file" ]; then
            echo "❌ CSS file not found: $css_file"
            exit 1
        fi
        echo ""
        echo "📝 Applying custom CSS file to pages..."
        source ~/.zshrc
        python3 download-page-content.py --css-file "$css_file"
        ;;
    3)
        read -p "Enter CSS file path to read content from: " css_file
        if [ ! -f "$css_file" ]; then
            echo "❌ CSS file not found: $css_file"
            exit 1
        fi
        css_content=$(cat "$css_file")
        echo ""
        echo "📝 Embedding CSS content in pages..."
        source ~/.zshrc
        python3 download-page-content.py --css-content "$css_content"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"

