# Plan to Generate Missing Section Files

## Overview
11 Section folders are missing all 3 required files:
- Canvas HTML file (`Section*.html`)
- Local HTML file (`Section*_local.html`)
- DOCX file (`Section*.docx`)

## Missing Sections
1. Module-2/Section-2-4
2. Module-3/Section-3-1
3. Module-3/Section-3-2
4. Module-4/Section-4-2
5. Module-4/Section-4-3
6. Module-4/Section-4-4
7. Module-5/Section-5-1
8. Module-5/Section-5-2
9. Module-5/Section-5-3
10. Module-5/Section-5-5
11. Module-5/Section-5-6

---

## Phase 1: Generate Canvas HTML Files

### Purpose
Canvas HTML files are the base HTML versions downloaded from Canvas LMS.

### Steps

#### Step 1.1: Get Canvas page URLs
- **Action**: Identify Canvas URLs for each missing section
- **Method**:
  - Check `/Users/a00288946/Projects/canvas_2879/config/canvas-page-links.json`
  - Check `/Users/a00288946/Projects/canvas_2879/config/box-file-ids.json`
  - Use Canvas API if needed
- **Expected Format**: `https://usucourses.instructure.com/courses/2879/pages/section-*-*`

#### Step 1.2: Download HTML from Canvas
- **Action**: Download HTML content from Canvas pages
- **Method Options**:
  - **Option A**: Canvas API - Use Canvas API to fetch page HTML content
  - **Option B**: Web scraping - Use browser automation or requests to fetch HTML
  - **Option C**: Manual download - If API unavailable, provide instructions for manual download
- **Required CSS paths**: Update CSS links to use relative paths `../../` (for Section depth)

#### Step 1.3: Standardize HTML structure
- **Action**: Ensure all Canvas HTML files follow the same structure as existing ones
- **Template Reference**: Use existing Section HTML files (e.g., `Section 1_ Overview of Document Accessibility.html`)
- **Required Elements**:
  - Canvas CSS links (relative paths)
  - Proper HTML structure
  - Title matching Section name
  - Body content from Canvas

### Validation
- [ ] All 11 Section folders have Canvas HTML files
- [ ] HTML files are properly formatted
- [ ] CSS links use correct relative paths (`../../`)
- [ ] Content matches Canvas pages

---

## Phase 2: Generate Local HTML Files

### Purpose
Local HTML files are copies of Canvas HTML files with corrected CSS paths for local viewing.

### Steps

#### Step 2.1: Copy Canvas HTML to Local HTML
- **Action**: Create `Section*_local.html` files based on `Section*.html` files
- **Method**: Copy Canvas HTML content to new `_local.html` files

#### Step 2.2: Update CSS paths
- **Action**: Replace CSS relative paths from `../../` to `../../../../../assets/css/`
- **Method**: Use script similar to the one used for Module/Section local files
- **CSS Path Calculation**:
  - Section folders are at depth 2 (Module-X/Section-X-X)
  - Need 5 levels up: `../../../../../assets/css/`
- **Files to Update**:
  - canvas-fonts.css
  - canvas-variables.css
  - canvas-common.css
  - canvas-wiki-page.css
  - catalog_canvas_global.css
  - webaimCatalog.css
  - AD-365-V4.css
  - canvas-custom-overrides.css

#### Step 2.3: Verify CSS paths
- **Action**: Verify CSS paths resolve correctly
- **Method**: Test relative path resolution from Section folder location

### Validation
- [ ] All 11 Section folders have Local HTML files
- [ ] CSS paths are correct (`../../../../../assets/css/`)
- [ ] All 8 CSS files have correct paths
- [ ] Files are identical to Canvas HTML except for CSS paths

---

## Phase 3: Generate DOCX Files (Source Files)

### Purpose
DOCX files are the source documents. These may need to be:
- Downloaded from Box (if they exist there)
- Created from existing Canvas content
- Generated from HTML content

### Steps

#### Step 3.1: Check Box for existing DOCX files
- **Action**: Query Box API for DOCX files in Section folders
- **Method**: Use Box API to list folder contents for each Section folder
- **Expected Result**: List of existing DOCX files that can be downloaded

#### Step 3.2: Download DOCX files from Box
- **Action**: Download any found DOCX files from Box to their respective Section folders
- **Method**: Use Box MCP tools or Box SDK
- **File Pattern**: `Section*.docx` in each Section folder

#### Step 3.3: Generate DOCX from Canvas HTML (if not in Box)
- **Action**: Convert Canvas HTML to DOCX for sections without Box files
- **Method**: Use existing HTML-to-DOCX conversion scripts/tools
- **Reference**: Check `/Users/a00288946/Projects/canvas_2879/scripts/core/html-to-docx.py`
- **Dependencies**: Requires Canvas HTML files from Phase 1

### Validation
- [ ] All 11 Section folders have DOCX files
- [ ] DOCX files are properly named (matching Section folder pattern)
- [ ] Files are readable and contain expected content

---

## Implementation Order

**Execution Sequence:**
1. **Phase 1** (Canvas HTML) - Base HTML files from Canvas LMS
2. **Phase 2** (Local HTML) - Depends on Phase 1 completion
3. **Phase 3** (DOCX) - Can use Canvas HTML from Phase 1 for conversion if needed

---

## Script Requirements

### Phase 1 Script: `download-section-canvas-html.py`
- Read Canvas URLs from config files
- Download HTML from Canvas (API or scraping)
- Standardize HTML structure
- Save to Section folders with correct naming

### Phase 2 Script: `create-section-local-html.py`
- Copy Canvas HTML files to `_local.html` versions
- Update CSS paths to `../../../../../assets/css/`
- Verify file creation
- Validate CSS paths

### Phase 3 Script: `generate-section-docx-files.py`
- Check Box for existing DOCX files
- Download from Box if found
- Convert Canvas HTML to DOCX if needed
- Place files in correct Section folders

---

## Configuration Files to Check

1. `/Users/a00288946/Projects/canvas_2879/config/canvas-page-links.json`
   - Contains Canvas URLs for sections
   - Format: `"canvas_url": "https://usucourses.instructure.com/courses/2879/pages/section-*-*"`

2. `/Users/a00288946/Projects/canvas_2879/config/box-file-ids.json`
   - May contain Box file IDs for DOCX files

3. `/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/course-map.json`
   - May contain metadata about sections

---

## Notes

- **Template Files**: Use existing Section files as templates for structure
- **Naming Convention**: Match existing patterns exactly
  - Canvas HTML: `Section X_ Title.html`
  - Local HTML: `Section X_ Title_local.html`
  - DOCX: `Section X_ Title.docx`
- **CSS Paths**: Critical to get correct relative paths for proper styling
- **Dependencies**: Phase 2 depends on Phase 1, Phase 3 can use Phase 1 output for HTML-to-DOCX conversion
