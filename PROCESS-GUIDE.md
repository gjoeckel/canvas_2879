# Complete Process Guide: Canvas to GitHub

This guide walks through the complete process of downloading course materials from Canvas and pushing them to GitHub.

## Overview

**Goal:** Download all materials from Canvas course 2879 and push them to GitHub repository [canvas_2879](https://github.com/gjoeckel/canvas_2879)

**Tools Used:**
- [canvas_grab](https://github.com/skyzh/canvas_grab) - Canvas LMS downloader
- Git - Version control
- GitHub - Repository hosting

## Prerequisites

✅ Canvas API token stored as `CANVAS_TOKEN` environment variable
✅ canvas_grab installed at `/Users/a00288946/Projects/canvas_grab`
✅ GitHub repository created at `https://github.com/gjoeckel/canvas_2879`
✅ Local directory created at `/Users/a00288946/Projects/canvas_2879`

## Step-by-Step Process

### Step 1: Download Course Materials

Run the automated download script:

```bash
cd /Users/a00288946/Projects/canvas_2879
./setup-and-download.sh
```

**What this does:**
1. Verifies `CANVAS_TOKEN` is available
2. Creates `config.toml` with:
   - Canvas endpoint: `https://usucourses.instructure.com`
   - API token from environment variable
   - Course filter: Only course 2879
   - Organization: By module with links
   - Download folder: Current directory
3. Runs canvas_grab to download all materials
4. Files are organized by Canvas module structure

**Expected Output:**
- All course files downloaded to current directory
- Files organized by modules
- Links and pages included
- Progress shown during download

### Step 2: Review Downloaded Materials

After download completes, review the files:

```bash
ls -la
```

You should see:
- Course files organized by modules
- `config.toml` (contains API token - will be gitignored)
- `README.md` (this repository's documentation)
- Setup scripts

### Step 3: Initialize Git and Push to GitHub

Run the git setup script:

```bash
./setup-git.sh
```

**What this does:**
1. Initializes git repository (if not already done)
2. Creates `.gitignore` to exclude sensitive files
3. Adds all course materials
4. Creates initial commit
5. Configures remote to GitHub
6. Pushes to GitHub (with confirmation)

**Alternative Manual Process:**

If you prefer to do it manually:

```bash
# Initialize git
git init

# Create .gitignore (excludes config.toml with token)
cat > .gitignore <<EOF
config.toml
*.pyc
__pycache__/
venv/
.DS_Store
EOF

# Add files
git add .

# Commit
git commit -m "Initial course materials from Canvas course 2879"

# Add remote
git remote add origin https://github.com/gjoeckel/canvas_2879.git

# Push
git branch -M main
git push -u origin main
```

## Updating Course Materials

When course materials are updated on Canvas, repeat the process:

```bash
# Download updates
./setup-and-download.sh

# Commit and push updates
git add .
git commit -m "Update course materials"
git push
```

## Configuration Details

### config.toml Structure

```toml
[endpoint]
endpoint = "https://usucourses.instructure.com"
api_key = "YOUR_TOKEN_HERE"

[course_filter]
filter_name = "per"
[course_filter.per_filter]
course_id = [2879]

[organize_mode]
mode = "module_link"
delete_file = false

[file_filter]
file_filter = []
file_extension_filter = []

download_folder = "."
```

**Key Settings:**
- `filter_name = "per"` - Per-course filter (single course)
- `course_id = [2879]` - Only download course 2879
- `mode = "module_link"` - Organize by module, include links and pages
- `delete_file = false` - Keep local files even if deleted on Canvas
- `download_folder = "."` - Download to current directory

## Troubleshooting

### Token Not Found
```bash
# Verify token is set
source ~/.zshrc
echo $CANVAS_TOKEN

# If not set, add to ~/.zshrc
echo 'export CANVAS_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### Download Fails
- Check Canvas API token is valid
- Verify course 2879 is accessible with your account
- Check network connection
- Review canvas_grab error messages

### Git Push Fails
- Verify GitHub repository exists
- Check GitHub authentication
- Ensure remote URL is correct: `https://github.com/gjoeckel/canvas_2879.git`
- Verify you have push permissions

## Security Notes

⚠️ **Important:**
- `config.toml` contains your Canvas API token
- It's automatically excluded via `.gitignore`
- Never commit `config.toml` to version control
- The token provides access to your Canvas account

## File Organization

Files are organized by Canvas module structure:
```
.
├── Module 1/
│   ├── file1.pdf
│   ├── file2.docx
│   └── links/
├── Module 2/
│   └── ...
└── ...
```

This structure matches how materials are organized in Canvas.

## Next Steps

After initial setup:
1. ✅ Course materials are in GitHub
2. ✅ Repository is ready for collaboration
3. ✅ Updates can be synced easily
4. ✅ Materials are version controlled

## References

- [canvas_grab GitHub](https://github.com/skyzh/canvas_grab)
- [Canvas LMS API](https://canvas.instructure.com/doc/api/)
- [GitHub Repository](https://github.com/gjoeckel/canvas_2879)

