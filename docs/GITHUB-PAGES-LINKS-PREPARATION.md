# GitHub Pages Links Preparation Document

**Purpose:** Prepare link structure for updating GitHub Pages with DOCX and Canvas links

**Format:** `view docx | edit docx [10px whitespace] view canvas | edit canvas`

---

## Link Structure

Each page in GitHub Pages should have the following link format:

```html
<a href="BOX_FILE_URL" target="_blank">view docx</a> |
<a href="BOX_EDIT_URL" target="_blank">edit docx</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="GITHUB_HTML_URL" target="_blank">view canvas</a> |
<a href="CANVAS_PAGE_URL" target="_blank">edit canvas</a>
```

Where:
- **view docx** = Box file URL (e.g., `https://usu.app.box.com/file/2072202817948`)
- **edit docx** = Box MS Word Online editor URL (e.g., `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2072202817948&sharedAccessCode=`)
- **view canvas** = GitHub Pages HTML file URL (connected to CSS and images in gitrepo)
- **edit canvas** = Canvas page URL (e.g., `https://usucourses.instructure.com/courses/2879/pages/course-orientation`)

---

## URL Patterns

### Box URLs

**View DOCX:**
```
https://usu.app.box.com/file/{BOX_FILE_ID}
```

**Edit DOCX (MS Word Online):**
```
https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={BOX_FILE_ID}&sharedAccessCode=
```

### GitHub Pages URLs

**View Canvas (HTML file):**
```
https://{USERNAME}.github.io/{REPO}/data/current/WINTER-25-26-UPDATES/{MODULE_PATH}/{FILENAME}_local.html
```

Example:
```
https://gjoeckel.github.io/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/course_orientation_local.html
```

### Canvas URLs

**Edit Canvas (Canvas page):**
```
https://usucourses.instructure.com/courses/2879/pages/{PAGE_SLUG}
```

Example:
```
https://usucourses.instructure.com/courses/2879/pages/course-orientation
```

---

## Implementation Steps

### Step 1: Update GitHub Pages HTML Structure

The GitHub Pages `index.html` file should be updated to include the new link format for each page entry.

### Step 2: Create Mapping Script

A script should be created to:
1. Read all DOCX files from `data/current/WINTER-25-26-UPDATES/`
2. Match DOCX files to Box file IDs from `config/box-file-ids.json`
3. Match DOCX files to Canvas URLs from `config/canvas-page-links.json`
4. Generate GitHub Pages HTML URLs based on file structure
5. Generate the link HTML for each page

### Step 3: Update GitHub Pages HTML

The generated links should be inserted into the GitHub Pages `index.html` file, replacing or updating existing link structures.

---

## File Mapping Sources

### Box File IDs
- **Location:** `config/box-file-ids.json`
- **Format:** JSON array with `file_id`, `box_url`, and `relative_path`

### Canvas Page Links
- **Location:** `config/canvas-page-links.json`
- **Format:** JSON object with `canvas_url` and `file_path`

### DOCX Files
- **Location:** `data/current/WINTER-25-26-UPDATES/`
- **Structure:** `Module-X/Section-X-Y/LA-X-Y-Z/{filename}.docx`

### Local HTML Files
- **Location:** `data/current/WINTER-25-26-UPDATES/`
- **Structure:** `Module-X/Section-X-Y/LA-X-Y-Z/{filename}_local.html`
- **Used for:** GitHub Pages "view canvas" links

---

## Example Link HTML

### Complete Example

```html
<span class="page-links">
  <a href="https://usu.app.box.com/file/2072202817948" target="_blank" rel="noopener noreferrer">view docx</a> |
  <a href="https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2072202817948&sharedAccessCode=" target="_blank" rel="noopener noreferrer">edit docx</a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://gjoeckel.github.io/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/course_orientation_local.html" target="_blank" rel="noopener noreferrer">view canvas</a> |
  <a href="https://usucourses.instructure.com/courses/2879/pages/course-orientation" target="_blank" rel="noopener noreferrer">edit canvas</a>
</span>
```

### In Context (GitHub Pages List Item)

```html
<li>
  <span class="page-text">1. Course Orientation</span>
  <span class="page-links">
    <a href="https://usu.app.box.com/file/2072202817948" target="_blank" rel="noopener noreferrer">view docx</a> |
    <a href="https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2072202817948&sharedAccessCode=" target="_blank" rel="noopener noreferrer">edit docx</a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://gjoeckel.github.io/canvas_2879/data/current/WINTER-25-26-UPDATES/Start-Here/course_orientation_local.html" target="_blank" rel="noopener noreferrer">view canvas</a> |
    <a href="https://usucourses.instructure.com/courses/2879/pages/course-orientation" target="_blank" rel="noopener noreferrer">edit canvas</a>
  </span>
</li>
```

### CSS Alternative (10px spacing)

Instead of using `&nbsp;` entities, you can use CSS:

```html
<style>
.page-links {
  display: inline-block;
}
.page-links .link-group {
  margin-right: 10px;
}
</style>

<span class="page-links">
  <span class="link-group">
    <a href="BOX_URL">view docx</a> |
    <a href="BOX_EDIT_URL">edit docx</a>
  </span>
  <span class="link-group">
    <a href="GITHUB_URL">view canvas</a> |
    <a href="CANVAS_URL">edit canvas</a>
  </span>
</span>
```

---

## Notes

1. **10px Whitespace:** Use `&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;` (10 non-breaking spaces) or CSS margin/padding for spacing between DOCX and Canvas link groups.

2. **GitHub Pages Base URL:** Replace `{USERNAME}` and `{REPO}` with actual GitHub username and repository name.

3. **File Matching:** DOCX file names need to be matched to Box file IDs and Canvas page slugs. This may require normalization (lowercase, replace spaces/hyphens/underscores).

4. **Missing Mappings:** Some DOCX files may not have corresponding Box file IDs or Canvas URLs. These should be flagged for manual review.

5. **Local HTML Files:** Ensure all DOCX files have corresponding `_local.html` files for the "view canvas" links to work.

---

## Generated Mappings

A JSON file with all link mappings has been generated:

**Location:** `config/github-pages-link-mappings.json`

**Summary:**
- Total DOCX files: 43
- Files with Box IDs: 39
- Files with Canvas URLs: 23
- Missing Box IDs: 4
- Missing Canvas URLs: 20

**Structure:**
```json
{
  "mappings": [
    {
      "docx_file": "Module-1/Section-1-1/LA-1-1-1/overview_of_document_accessibility_part_1.docx",
      "docx_name": "overview_of_document_accessibility_part_1",
      "box_file_id": "2071047997212",
      "box_url": "https://usu.app.box.com/file/2071047997212",
      "box_edit_url": "https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2071047997212&sharedAccessCode=",
      "canvas_url": "https://usucourses.instructure.com/courses/2879/pages/overview-of-document-accessibility-part-1",
      "github_html_path": "Module-1/Section-1-1/LA-1-1-1/overview_of_document_accessibility_part_1_local.html",
      "github_url": "https://YOUR-USERNAME.github.io/YOUR-REPO/data/current/WINTER-25-26-UPDATES/Module-1/Section-1-1/LA-1-1-1/overview_of_document_accessibility_part_1_local.html"
    }
  ],
  "summary": { ... },
  "missing_box": [ ... ],
  "missing_canvas": [ ... ]
}
```

## Next Steps

1. ✅ Create this preparation document
2. ✅ Create script to generate link mappings (`config/github-pages-link-mappings.json`)
3. ⏳ Create script to generate HTML link snippets from mappings
4. ⏳ Update GitHub Pages HTML with new link structure
5. ⏳ Resolve missing Box IDs and Canvas URLs
6. ⏳ Test all links
7. ⏳ Deploy updated GitHub Pages

---

**Created:** 2025-12-11
**Last Updated:** 2025-12-11
