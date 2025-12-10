# Canvas Course 2879 - Development Course Materials

This repository contains all course materials downloaded from Canvas LMS.

## Source

- **Canvas Instance:** https://usucourses.instructure.com
- **Course ID:** 2879
- **Download Tool:** [canvas_grab](https://github.com/skyzh/canvas_grab)

## Setup and Download Process

### Automated Setup

Run the setup script to download all course materials:

```bash
cd /Users/a00288946/Projects/canvas_2879
./setup-and-download.sh
```

This script will:
1. Verify Canvas token is available
2. Create `config.toml` with proper configuration
3. Download all course materials from Canvas
4. Organize files by module structure

### Manual Setup

If you prefer to configure manually:

1. **Configure canvas_grab:**
   ```bash
   cd /Users/a00288946/Projects/canvas_grab
   source venv/bin/activate
   python main.py --reconfigure
   ```
   - Endpoint: `https://usucourses.instructure.com`
   - API Key: Use the stored `CANVAS_TOKEN` environment variable
   - Select course 2879
   - Set download folder to this directory

2. **Run download:**
   ```bash
   python main.py -o /Users/a00288946/Projects/canvas_2879
   ```

## Git Workflow

After downloading materials:

```bash
# Initialize repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial course materials from Canvas"

# Add remote (if not already added)
git remote add origin https://github.com/gjoeckel/canvas_2879.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Updating Course Materials

To update materials after changes on Canvas:

```bash
./setup-and-download.sh
# or
cd /Users/a00288946/Projects/canvas_grab
source venv/bin/activate
python main.py -c /Users/a00288946/Projects/canvas_2879/config.toml -o /Users/a00288946/Projects/canvas_2879 -I
```

Then commit and push changes:

```bash
git add .
git commit -m "Update course materials"
git push
```

## Configuration

The `config.toml` file contains:
- Canvas endpoint URL
- API token (stored securely)
- Course filter (course 2879 only)
- Organization mode (by module with links)
- Download folder (current directory)

## Notes

- Files are organized by Canvas module structure
- Links and pages are included in the download
- The download can be interrupted and resumed
- Do not modify downloaded files directly - they will be overwritten on update

