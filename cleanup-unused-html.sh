#!/bin/bash
# Script to remove unused HTML files

cd /Users/a00288946/Projects/canvas_2879

# Read unused files list
if [ ! -f /tmp/unused_files.txt ]; then
    echo "Error: /tmp/unused_files.txt not found. Please run the analysis first."
    exit 1
fi

unused_count=$(wc -l < /tmp/unused_files.txt | tr -d ' ')
echo "Found $unused_count unused HTML files"
echo ""

# Show what will be removed
echo "Files that will be removed:"
cat /tmp/unused_files.txt | head -20
if [ "$unused_count" -gt 20 ]; then
    echo "... and $((unused_count - 20)) more files"
fi
echo ""

# Ask for confirmation
read -p "Remove these files? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# Remove files
removed=0
while IFS= read -r file; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "Removed: $file"
        ((removed++))
    fi
done < /tmp/unused_files.txt

echo ""
echo "Removed $removed unused HTML files"

