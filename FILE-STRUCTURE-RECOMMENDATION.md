# Recommended File Structure for GitHub Pages

## Current Situation

- **Local source files**: `data/current/WINTER-25-26-UPDATES/.../file_local.html`
- **GitHub Pages source**: `docs/` folder (served as root)
- **Issue**: Files outside `docs/` are NOT served by GitHub Pages

## Recommended Approach: Copy HTML Files to `docs/` for Deployment

### Structure

```
canvas_2879/
├── data/                          # Source files (local editing)
│   └── current/
│       └── WINTER-25-26-UPDATES/
│           ├── Module-1/
│           │   ├── module_1_document_content_local.html
│           │   └── Section-1-1/
│           │       ├── section_1_overview_of_document_accessibility_local.html
│           │       └── LA-1-1-1/
│           │           └── overview_of_document_accessibility_part_1_local.html
│           └── ...
│
├── docs/                          # GitHub Pages deployment folder
│   ├── index.html                 # Main index (served at root)
│   ├── .nojekyll                  # Disable Jekyll processing
│   └── data/                      # Mirrored HTML files
│       └── current/
│           └── WINTER-25-26-UPDATES/
│               └── ... (same structure as source)
│
└── scripts/
    └── sync-html-to-docs.js       # Script to copy HTML files to docs/
```

### Workflow

1. **Edit locally** in `data/current/WINTER-25-26-UPDATES/...`
2. **Run sync script** to copy HTML files to `docs/data/...`
3. **Commit and push** both source and docs folders

### Benefits

✅ **Separation of concerns**: Source files stay organized, docs is deployment-ready
✅ **GitHub Pages compatibility**: All files in `docs/` are served
✅ **Easy local editing**: Work with files in their natural location
✅ **Version control**: Both source and deployed versions tracked

### URLs

- Files in `docs/data/...` are accessible at:
  - `https://gjoeckel.github.io/canvas_2879/data/current/.../file.html`

Since `docs/` is the root, `docs/data/` → `/data/` in the URL.

## Alternative: GitHub Raw URLs

If you prefer not to copy files, use GitHub Raw URLs:

```
https://raw.githubusercontent.com/gjoeckel/canvas_2879/main/data/current/.../file.html
```

**Pros**:
- No file duplication
- Always serves latest from repo

**Cons**:
- Raw URLs don't preserve relative paths (images, CSS break)
- Not ideal for viewing HTML pages directly

## Recommendation

**Use the copy-to-docs approach** because:
1. HTML files often reference images/CSS with relative paths
2. GitHub Pages preserves the full file structure
3. Better user experience (clean URLs, proper HTML rendering)
4. Can use relative paths within HTML files

