# GitHub Pages Deployment Guide

## ✅ What's Already Done

1. ✅ **Box File IDs Updated**: All 70 pages now have correct Box file IDs from folder `356056033736`
2. ✅ **index.html Generated**: HTML file updated with all Box file links
3. ✅ **Path Fix Applied**: "View canvas" links now use root-relative paths (`data/...` instead of `../data/...`)

## ⚠️ Critical Check: index.html Location

The `index.html` file is currently in `github-pages/index.html`.

**For GitHub Pages to work, you need to verify the source configuration:**

1. Go to: https://github.com/gjoeckel/canvas_2879/settings/pages
2. Check which source is configured:
   - **If `/` (root) is selected**: Move `index.html` to repository root
   - **If `/docs` is selected**: Move `github-pages/` folder to `docs/` and rename `github-pages/` to `docs/`
   - **If `/github-pages` is selected**: Current location is correct (unusual setup)

## 📋 Pre-Deployment Checklist

### ✅ Completed
- [x] Box file IDs updated from folder `356056033736`
- [x] All Box file links use correct IDs
- [x] Canvas edit links are correct (absolute URLs)
- [x] "View canvas" paths fixed to root-relative (`data/...` instead of `../data/...`)

### ⚠️ Required Actions

#### 1. Verify/Move index.html Location

**Option A: If GitHub Pages uses root (`/`)**
```bash
cd /Users/a00288946/Projects/canvas_2879
mv github-pages/index.html index.html
git add index.html
```

**Option B: If GitHub Pages uses `/docs` folder**
```bash
cd /Users/a00288946/Projects/canvas_2879
mv github-pages docs
git add docs/index.html
```

**Option C: If GitHub Pages uses `/github-pages` folder**
```bash
# Current location is correct, just add it
cd /Users/a00288946/Projects/canvas_2879
git add github-pages/index.html
```

#### 2. Verify Local HTML Files Exist

Ensure all the `*_local.html` files referenced in "view canvas" links actually exist:
```bash
# Check if files exist (they should be in the data folder)
ls data/current/WINTER-25-26-UPDATES/*/.*_local.html 2>/dev/null | wc -l
# Should show ~70 files
```

#### 3. Test Links (Optional but Recommended)

Before pushing, you can test locally:
```bash
cd /Users/a00288946/Projects/canvas_2879
python3 -m http.server 8000
# Then visit http://localhost:8000/github-pages/ or http://localhost:8000/
# depending on where index.html is located
```

#### 4. Commit and Push

```bash
cd /Users/a00288946/Projects/canvas_2879

# Stage the index.html file (in correct location)
git add github-pages/index.html  # or index.html or docs/index.html

# Optional: Also commit the course-map.json for reference
git add data/current/WINTER-25-26-UPDATES/course-map.json

# Commit
git commit -m "Update index.html with Box file IDs from folder 356056033736

- Updated all 70 pages with correct Box file IDs
- Fixed view canvas links to use root-relative paths
- All Box and Canvas links are now functional"

# Push
git push origin main
```

#### 5. Verify Deployment

After pushing:
1. Wait 1-2 minutes for GitHub Pages to rebuild
2. Visit: https://gjoeckel.github.io/canvas_2879/
3. Test a few links:
   - Box "view docx" links (requires Box authentication)
   - Box "edit docx" links (requires Box authentication)
   - Canvas "edit canvas" links (requires Canvas authentication)
   - "View canvas" links (should work if paths are correct)
4. Check browser console (F12) for any 404 errors

## 🔍 Link Verification

All links in the generated HTML should be:

✅ **Box View DOCX**: `https://usu.app.box.com/file/{file_id}` - Absolute URL, will work
✅ **Box Edit DOCX**: `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={file_id}&sharedAccessCode=` - Absolute URL, will work
✅ **View Canvas**: `data/current/WINTER-25-26-UPDATES/...` - Root-relative, will work if index.html is in correct location
✅ **Edit Canvas**: `https://usucourses.instructure.com/courses/2879/pages/{page_id}/edit` - Absolute URL, will work

## 📝 Notes

- The "view canvas" links require the `*_local.html` files to exist in the repository
- Box and Canvas links require user authentication (they will redirect to login if not authenticated)
- GitHub Pages typically takes 1-2 minutes to rebuild after a push
- If you see 404 errors, check that:
  - index.html is in the correct location for your GitHub Pages configuration
  - The `data/` folder structure is committed to the repository
  - Paths are root-relative (starting with `data/...` not `../data/...`)

