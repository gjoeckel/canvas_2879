# Pre-Deployment Checklist for GitHub Pages

## Current Status

✅ **course-map.json** - Updated with Box file IDs from folder `356056033736`
✅ **index.html** - Generated with updated Box file IDs and links

## Critical Issues to Fix Before Pushing

### 1. ⚠️ "View Canvas" Links - Relative Path Issue

**Problem**: The "view canvas" links use relative paths that won't work on GitHub Pages:

```html
<a href="../data/current/WINTER-25-26-UPDATES/Module-1/.../file_local.html">
```

**Why this fails**:
- On GitHub Pages, `index.html` is served from the root (`/canvas_2879/`)
- The relative path `../data/...` goes up one level from root, which doesn't exist
- The `data/` folder is in the repository, but the path is wrong

**Solution Options**:

#### Option A: Use Absolute GitHub Pages Paths (Recommended)
Change relative paths to absolute paths from repository root:

```html
<!-- Before -->
<a href="../data/current/WINTER-25-26-UPDATES/Module-1/.../file_local.html">

<!-- After -->
<a href="https://gjoeckel.github.io/canvas_2879/data/current/WINTER-25-26-UPDATES/Module-1/.../file_local.html">
```

#### Option B: Use Relative Paths from Root
Change to paths relative to repository root (no `../`):

```html
<!-- Before -->
<a href="../data/current/WINTER-25-26-UPDATES/Module-1/.../file_local.html">

<!-- After -->
<a href="data/current/WINTER-25-26-UPDATES/Module-1/.../file_local.html">
```

**Recommendation**: Use **Option B** (relative from root) for simplicity and portability.

### 2. 📁 index.html Location

**Current Location**: `/Users/a00288946/Projects/canvas_2879/github-pages/index.html`

**GitHub Pages Configuration**:
- If GitHub Pages is configured for `/` (root) branch: Move `index.html` to repository root
- If GitHub Pages is configured for `/docs` folder: Keep in current location and rename folder to `docs`
- If GitHub Pages is configured for `/github-pages` folder: Current location is correct (unusual)

**Action Needed**: Verify GitHub Pages source in repository settings and move/rename accordingly.

### 3. ✅ Box File Links - Already Correct

The Box file links are correct:
- ✅ View DOCX: `https://usu.app.box.com/file/{file_id}`
- ✅ Edit DOCX: `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={file_id}&sharedAccessCode=`

These are absolute URLs and will work correctly.

### 4. ✅ Canvas Edit Links - Already Correct

Canvas edit links are correct:
- ✅ Edit Canvas: `https://usucourses.instructure.com/courses/2879/pages/{page_id}/edit`

These are absolute URLs and will work correctly.

## Required Actions

### Step 1: Fix "View Canvas" Link Paths

Update the `generate-index-html.js` script to use root-relative paths instead of `../`:

```javascript
// In generate-index-html.js, change:
const viewCanvasUrl = page.github?.local_html_path || '';

// To generate root-relative path:
// Remove the "../" prefix and use path from repository root
const viewCanvasUrl = page.github?.local_html_path
  ? page.github.local_html_path.replace(/^\.\.\//, '')
  : '';
```

Then regenerate `index.html`.

### Step 2: Verify index.html Location

Check GitHub Pages configuration:
1. Go to repository Settings → Pages
2. Check which branch/folder is configured as source
3. Ensure `index.html` is in the correct location

### Step 3: Test Links Locally

Before pushing, test that all links work:
- Box file links (requires authentication)
- Canvas edit links (requires authentication)
- View canvas links (should work if paths are fixed)

### Step 4: Commit and Push

```bash
cd /Users/a00288946/Projects/canvas_2879
git add github-pages/index.html  # or root/index.html depending on location
git commit -m "Update index.html with Box file IDs from folder 356056033736"
git push origin main  # or appropriate branch
```

### Step 5: Verify GitHub Pages Deployment

After pushing:
1. Wait 1-2 minutes for GitHub Pages to rebuild
2. Visit https://gjoeckel.github.io/canvas_2879/
3. Verify all links work correctly
4. Check browser console for any 404 errors

## Files That Should Be Committed

- ✅ `github-pages/index.html` (or root `index.html` if moved)
- ✅ `data/current/WINTER-25-26-UPDATES/course-map.json` (optional, for reference)
- ❌ Don't commit temporary scripts unless needed

## Summary

**Critical Fix Needed**: Update "view canvas" link paths from `../data/...` to `data/...` (remove `../` prefix)

**All Other Links**: Already correct and will work on GitHub Pages

