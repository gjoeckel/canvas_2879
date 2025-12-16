# GitHub Pages Deployment Guide

## Overview

This document outlines the steps and patterns needed to preserve all functionality validated in local testing when deploying to GitHub Pages at `https://gjoeckel.github.io/canvas_2879/`.

**Last Updated**: 2025-01-XX
**Status**: Functional in local testing, ready for GitHub Pages deployment

---

## Site Patterns Identified

### 1. File Structure Pattern

The site follows a standard static site structure optimized for GitHub Pages:

```
canvas_2879/
├── index.html                          # Main HTML file (root)
├── assets/
│   ├── css/
│   │   └── index.css                  # Main stylesheet (with cache-busting)
│   └── js/
│       ├── asana-config.js            # Asana configuration (ES module)
│       ├── asana-api.js               # Asana API client (ES module)
│       └── asana-status.js            # Status display logic (ES module)
└── data/
    └── asana-task-mapping.json        # Task ID mapping file
```

### 2. Module Import Pattern

All JavaScript uses ES6 modules with `type="module"`:

```html
<script type="module" src="assets/js/asana-config.js"></script>
<script type="module" src="assets/js/asana-api.js"></script>
<script type="module" src="assets/js/asana-status.js"></script>
```

**Dependencies** (import order matters):
- `asana-config.js` - No dependencies
- `asana-api.js` - Imports from `asana-config.js`
- `asana-status.js` - Imports from `asana-config.js` and `asana-api.js`

### 3. Relative Path Pattern

All asset references use **relative paths** from the root:

- CSS: `href="assets/css/index.css?v=1765923661"`
- JS: `src="assets/js/asana-api.js"`
- JSON: Fetched via `fetch('/data/asana-task-mapping.json')`

### 4. CORS and API Pattern

- **Client-side direct API calls** to Asana API
- Uses Personal Access Token (MVP authentication)
- Token stored in `asana-config.js` (not in HTML)
- API calls use `fetch()` with Bearer token authentication

### 5. Caching Pattern

- **CSS cache-busting**: `?v=1765923661` parameter
- **SessionStorage caching**: Field definitions cached in browser
- **JSON mapping**: Loaded fresh on each page load

---

## Critical Files and Dependencies

### Required Files

1. **index.html**
   - Root HTML file
   - Imports CSS with cache-busting
   - Imports JS modules in dependency order
   - Contains all page structure and content

2. **assets/css/index.css**
   - All styling (extracted from inline styles)
   - Includes sticky header styles
   - Includes badge styling for Asana statuses
   - Includes tabbed layout styles

3. **assets/js/asana-config.js**
   - **CRITICAL**: Contains Personal Access Token
   - Project and workspace IDs
   - Custom field GIDs mapping
   - Must be preserved exactly

4. **assets/js/asana-api.js**
   - API request functions
   - Field definition fetching and caching
   - Enum option color mapping
   - Dynamic field GID → name mapping

5. **assets/js/asana-status.js**
   - Status display logic
   - Batch loading with rate limiting
   - DOM updates for status fields
   - Refresh functionality

6. **data/asana-task-mapping.json**
   - Maps Canvas page IDs to Asana task GIDs
   - Required for status display
   - Must be accessible via `fetch()`

---

## Deployment Checklist

### Pre-Deployment Validation

- [ ] **Local testing passes**: All functionality works on `http://localhost:8000/index.html`
- [ ] **All assets present**: CSS, JS, and JSON files are in correct locations
- [ ] **Module imports correct**: All `import` statements use relative paths
- [ ] **No absolute URLs**: All internal references use relative paths
- [ ] **Token configured**: `asana-config.js` has correct Personal Access Token
- [ ] **Cache-busting updated**: CSS link has current timestamp parameter

### File Structure Verification

```bash
# Verify structure matches expected pattern
ls -la assets/css/index.css
ls -la assets/js/asana-*.js
ls -la data/asana-task-mapping.json
ls -la index.html
```

### GitHub Pages Specific Requirements

- [ ] **Repository settings**: GitHub Pages enabled, source branch selected
- [ ] **Branch consistency**: All files on the branch used for GitHub Pages
- [ ] **Base URL**: Site should work at `https://gjoeckel.github.io/canvas_2879/`
- [ ] **Relative paths**: All paths work from GitHub Pages base URL

### Post-Deployment Testing

1. **Initial Load**
   - [ ] Page loads without errors
   - [ ] CSS styles apply correctly
   - [ ] No console errors

2. **Asana Integration**
   - [ ] Field definitions load successfully
   - [ ] Task statuses display correctly
   - [ ] Status badges show correct colors
   - [ ] Placeholders preserved when no status selected

3. **Functionality**
   - [ ] "Refresh task" links work
   - [ ] "Open task" links work (focus URLs)
   - [ ] Rate limiting prevents 429 errors
   - [ ] Batch loading completes successfully

---

## Step-by-Step Deployment Process

### Step 1: Prepare Files for Deployment

1. **Ensure all local changes are committed**
   ```bash
   cd /Users/a00288946/Projects/canvas_2879
   git status
   git add .
   git commit -m "Update: Asana integration with field extraction"
   ```

2. **Update CSS cache-busting parameter** (if CSS changed)
   - Update `index.html` line 7: `href="assets/css/index.css?v=NEW_TIMESTAMP"`

3. **Verify `asana-config.js` has correct token**
   - Check that `ASANA_ACCESS_TOKEN` is set
   - Verify `ASANA_PROJECT_ID` and `ASANA_WORKSPACE_ID` are correct

### Step 2: Verify File Structure

Ensure these files exist and are in the correct locations:

```
✓ index.html (root)
✓ assets/css/index.css
✓ assets/js/asana-config.js
✓ assets/js/asana-api.js
✓ assets/js/asana-status.js
✓ data/asana-task-mapping.json
```

### Step 3: Test Module Imports Locally

Verify ES6 module imports work:

```bash
# Start local server
cd /Users/a00288946/Projects/canvas_2879
python3 -m http.server 8000

# Test in browser
open http://localhost:8000/index.html

# Check browser console for errors
```

### Step 4: Push to GitHub

```bash
# Push to main branch (or branch configured for GitHub Pages)
git push origin main
```

### Step 5: Verify GitHub Pages Deployment

1. Go to repository settings → Pages
2. Verify source branch is selected
3. Wait for deployment (usually 1-2 minutes)
4. Visit `https://gjoeckel.github.io/canvas_2879/`

### Step 6: Post-Deployment Testing

1. **Open browser console** (F12)
2. **Check for errors**:
   - No CORS errors
   - No module loading errors
   - No 404 errors for assets

3. **Test Asana integration**:
   - Verify status fields load
   - Check that badges display with colors
   - Test "refresh task" functionality

4. **Verify rate limiting**:
   - Check Network tab for API calls
   - Should see batching (10 requests per batch)
   - No 429 errors

---

## Common Issues and Solutions

### Issue 1: Module Import Errors

**Symptoms**: Console errors like "Failed to load module script"

**Solution**:
- Verify all `import` statements use relative paths
- Ensure `type="module"` is set on `<script>` tags
- Check file paths are correct in HTML

### Issue 2: CORS Errors

**Symptoms**: Console errors like "Access to fetch blocked by CORS policy"

**Solution**:
- Asana API supports CORS for authenticated requests
- Verify token is correct in `asana-config.js`
- Check that token has proper permissions

### Issue 3: 404 Errors for Assets

**Symptoms**: CSS/JS files not loading

**Solution**:
- Verify file structure matches GitHub Pages root
- Check relative paths are correct
- Ensure files are committed and pushed

### Issue 4: Status Fields Not Displaying

**Symptoms**: Placeholders show but no actual status values

**Solution**:
- Check browser console for API errors
- Verify `asana-task-mapping.json` is accessible
- Check that field definitions are loading
- Verify token has access to project

### Issue 5: Rate Limiting (429 Errors)

**Symptoms**: Too many API requests

**Solution**:
- Rate limiting is already implemented (10 per batch, 500ms delay)
- If still seeing errors, increase `BATCH_DELAY_MS` in `asana-status.js`

---

## GitHub Pages Specific Considerations

### Base URL Handling

GitHub Pages serves from `https://gjoeckel.github.io/canvas_2879/`, so:

- ✅ **Correct**: `href="assets/css/index.css"` (relative)
- ✅ **Correct**: `src="assets/js/asana-api.js"` (relative)
- ✅ **Correct**: `fetch('/data/asana-task-mapping.json')` (absolute from root)
- ❌ **Wrong**: `href="/assets/css/index.css"` (may not work in subdirectory)

### Module Resolution

ES6 modules resolve relative to the HTML file location:

- `import { ASANA_ACCESS_TOKEN } from './asana-config.js'` works correctly
- Modules must be in same directory or use relative paths

### JSON Loading

The task mapping JSON is loaded via `fetch()`:

```javascript
const response = await fetch('/data/asana-task-mapping.json');
```

This works because:
- Fetch uses absolute path from site root
- GitHub Pages serves `/data/` directory correctly

---

## Security Considerations

### Personal Access Token

⚠️ **IMPORTANT**: The Personal Access Token is stored in `asana-config.js` and will be visible in the browser.

**Current Approach** (MVP):
- Token is in client-side JavaScript
- Accessible via browser DevTools
- Acceptable for MVP with project access control

**Future Improvement**:
- Implement OAuth flow
- Use server-side token exchange
- Keep tokens server-side only

### Token Permissions

The token must have:
- Read access to tasks
- Read access to custom fields
- Access to the specified project and workspace

---

## Maintenance

### Updating CSS Cache-Busting

When CSS changes, update the cache-busting parameter:

1. Update `index.html` line 7:
   ```html
   <link rel="stylesheet" href="assets/css/index.css?v=NEW_TIMESTAMP">
   ```

2. Use timestamp: `Date.now()` or current Unix timestamp

### Updating Task Mapping

When `asana-task-mapping.json` changes:

1. Update the file in `data/` directory
2. Commit and push to GitHub
3. Changes are immediately available (no cache-busting needed)

### Updating JavaScript Modules

JavaScript modules are loaded fresh on each page load:

1. Update module files
2. Commit and push to GitHub
3. Users may need to hard refresh (Cmd+Shift+R / Ctrl+Shift+R)

---

## Validation Scripts

### Local Validation

```bash
# Start local server
python3 -m http.server 8000

# Open browser and test
open http://localhost:8000/index.html

# Check console for errors
```

### Structure Validation

```bash
# Verify all required files exist
python3 validate-structure.py
```

---

## Summary

### Critical Requirements

1. ✅ **File structure preserved**: All files in correct locations
2. ✅ **Relative paths**: All asset references use relative paths
3. ✅ **ES6 modules**: All JavaScript uses `type="module"`
4. ✅ **Token configured**: `asana-config.js` has correct token
5. ✅ **JSON accessible**: Task mapping file is fetchable
6. ✅ **Module dependencies**: Import order is correct

### Deployment Steps

1. Verify local testing passes
2. Update cache-busting if CSS changed
3. Commit and push all files
4. Verify GitHub Pages deployment
5. Test all functionality on live site

### Success Criteria

- ✅ Page loads without errors
- ✅ Status fields display correctly
- ✅ Badges show with correct colors
- ✅ Refresh functionality works
- ✅ No console errors
- ✅ No 429 rate limit errors

---

**Template Preservation**: The existing site at `https://gjoeckel.github.io/canvas_2879/` serves as the reference template. All patterns and structures documented here are based on this working implementation.

