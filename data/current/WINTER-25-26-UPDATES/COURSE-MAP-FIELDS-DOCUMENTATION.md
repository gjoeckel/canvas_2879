# Course Map JSON Fields Documentation

This document describes all fields that should be included in the hierarchical course-map.json structure.

---

## Top-Level Structure

### `schema_version`
- **Type:** `string`
- **Format:** `"1.0"` or `"1.1"` (semantic versioning)
- **Description:** Version of the JSON schema structure
- **Required:** Yes

### `course`
- **Type:** `object`
- **Description:** Course-level metadata
- **Fields:**
  - `id` (string, required): Canvas course ID (e.g., "2879")
  - `name` (string, required): Course name (e.g., "Document Accessibility")
  - `canvas_url` (string, URI): Direct URL to Canvas course
  - `semester` (string): Semester/term information (e.g., "Winter 2025-26")
  - `instructor` (string): Instructor name

### `metadata`
- **Type:** `object`
- **Description:** Metadata about the course map itself
- **Fields:**
  - `created` (string, ISO 8601): When the course map was created
  - `last_updated` (string, ISO 8601, required): Last update timestamp
  - `last_synced` (string, ISO 8601, nullable): Last sync operation timestamp
  - `version` (string): Version of the course map content (semantic versioning)

### `repositories`
- **Type:** `object`
- **Description:** GitHub repository configurations
- **Structure:** Key-value pairs where keys are repository names (e.g., "main")
  - `url` (string, URI): GitHub repository URL
  - `branch` (string): Default branch (e.g., "main")
  - `path` (string): Base path within repository

### `box`
- **Type:** `object`
- **Description:** Base Box folder configuration
- **Fields:**
  - `folder_id` (string): Box folder ID for the root course folder
  - `folder_url` (string, URI): Direct URL to Box folder
  - `base_path` (string): Base path in Box (e.g., "/WINTER-25-26-UPDATES")

---

## Start Here Structure

### `start_here`
- **Type:** `object` or `null`
- **Description:** Special section for course orientation materials
- **Fields:**
  - `folder_name` (string): Filesystem folder name (e.g., "Start-Here")
  - `folder_id` (string): Box folder ID
  - `subfolders` (array): Array of start-here subfolders
    - Each subfolder has:
      - `folder_name` (string): e.g., "1-course-orientation"
      - `folder_id` (string): Box folder ID
      - `id` (string): Unique identifier (e.g., "course-orientation")
      - `title` (string): Display title
      - `order` (number): Display order
      - `status` (string): "published", "draft", "unpublished", "archived"
      - `canvas`: Canvas page information (see Canvas section below)
      - `github`: GitHub file paths (see GitHub section below)
      - `box`: Box file information (see Box section below)
      - `sync`: Sync tracking (see Sync section below)
      - `metadata`: Metadata (see Metadata section below)

---

## Module Structure

### `modules` (array)
- **Type:** `array` of module objects
- **Description:** Array of course modules, each containing sections

#### Module Object Fields:

##### Core Identification
- `id` (string, required): Unique identifier (e.g., "module-1-document-content")
- `title` (string, required): Display title (e.g., "Module 1  Document Content")
- `order` (number): Display order (e.g., 1, 2, 3)
- `status` (string, enum): "published", "draft", "unpublished", "archived"

##### Folder Information
- `folder_name` (string, required): Filesystem folder name (e.g., "Module-1")
- `box_folder_id` (string, required): Box folder ID where module DOCX file is stored

##### Canvas Information
- `canvas` (object): Canvas page details
  - `url` (string, URI): Canvas page URL
  - `page_id` (string): Canvas page slug/ID
  - `published` (boolean): Is page published in Canvas?
  - `published_at` (string, ISO 8601, nullable): Publication timestamp

##### GitHub Information
- `github` (object): GitHub repository paths
  - `repository` (string): Repository key (references `repositories` object)
  - `source_docx` (object): Source DOCX file path
    - `path` (string): Relative path from repo root (e.g., "pages/module-1-document-content/module-1-document-content.docx")
    - `branch` (string): Git branch (usually "main")
  - `canvas_copy` (object): Canvas HTML copy path
    - `path` (string): Relative path (e.g., "pages/module-1-document-content/canvas-copy.html")
    - `branch` (string): Git branch
  - `with_assets` (object): HTML with assets path
    - `path` (string): Relative path (e.g., "pages/module-1-document-content/index.html")
    - `branch` (string): Git branch
  - `local_html_path` (string, optional): Relative path for "view canvas" link in index.html
    - Format: `../data/current/WINTER-25-26-UPDATES/{folder_path}/{filename}_local.html`
    - Example: `../data/current/WINTER-25-26-UPDATES/Module-1/module_1_document_content_local.html`

##### Box File Information
- `box` (object): Box DOCX file details
  - `file_id` (string, required): Box file ID (for "view docx" link)
  - `file_name` (string): Box file name (e.g., "Module 1_ Document Content.docx")
  - `file_url` (string, URI): Box file viewer URL (constructible from file_id)
  - `word_online_url` (string, URI): Box Word Online editor URL (for "edit docx" link)
    - Format: `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={file_id}&sharedAccessCode=`
  - `folder_id` (string): Box folder ID (same as `box_folder_id` at module level)
  - `modified_at` (string, ISO 8601, nullable): Last modification timestamp from Box
  - `version` (number): Box file version number

##### Sync Tracking
- `sync` (object): Sync operation tracking
  - `last_synced` (string, ISO 8601, nullable): Last successful sync timestamp
  - `sync_status` (string, enum): "pending", "synced", "error", "in_progress"
  - `sync_errors` (array): Array of error messages if sync failed

##### Metadata
- `metadata` (object): Additional metadata
  - `type` (string, enum): "module", "section", "la", "start_here"
  - `created` (string, ISO 8601): Creation timestamp

##### Sections
- `sections` (array, required): Array of section objects (see Section Structure below)

---

## Section Structure

### Section Object (nested within Module)
- **Type:** `object`
- **Description:** Section within a module, containing learning activities (LAs)

#### Section Fields:

Same structure as Module, except:
- `id` (string): e.g., "section-1-overview-of-document-accessibility"
- `title` (string): e.g., "Section 1  Overview of Document Accessibility"
- `folder_name` (string): e.g., "Section-1-1" (format: Section-{module}-{section})
- `box_folder_id` (string): Box folder ID for section folder
- `metadata.type` (string): "section"
- `las` (array, required): Array of LA objects (see LA Structure below) instead of `sections`

---

## LA (Learning Activity) Structure

### LA Object (nested within Section)
- **Type:** `object`
- **Description:** Individual learning activity page

#### LA Fields:

Same structure as Section, except:
- `id` (string): e.g., "overview-of-document-accessibility-part-1"
- `title` (string): e.g., "Overview Of Document Accessibility Part 1"
- `folder_name` (string): e.g., "LA-1-1-1" (format: LA-{module}-{section}-{la})
- `box_folder_id` (string): Box folder ID for LA folder
- `metadata.type` (string): "la"
- No nested arrays (LAs are leaf nodes)

---

## GitHub Paths Explained

### `github.source_docx.path`
- **Purpose:** Path to the original DOCX source file in GitHub
- **Usage:**
  - Source of truth for the document content
  - Used for version control and backup
  - May be used for downloading/uploading to Box
- **Example:** `"pages/module-1-document-content/module-1-document-content.docx"`
- **Relative to:** Repository root + `repositories[repository].path`
- **File Type:** `.docx`

### `github.canvas_copy.path`
- **Purpose:** Path to the HTML version of the Canvas page content (without assets)
- **Usage:**
  - Clean HTML copy of what's in Canvas
  - Used for version control of Canvas content
  - Typically HTML generated from DOCX or exported from Canvas
  - Does NOT include images or other assets (just HTML structure)
- **Example:** `"pages/module-1-document-content/canvas-copy.html"`
- **Relative to:** Repository root + `repositories[repository].path`
- **File Type:** `.html`
- **Content:** HTML markup only, asset references point to Canvas or external sources

### `github.with_assets.path`
- **Purpose:** Path to the HTML version with embedded/inlined assets
- **Usage:**
  - Complete standalone HTML version
  - Includes all images, CSS, and other assets
  - Can be viewed offline or served from GitHub Pages
  - Used for the "view canvas" link in the index.html file
- **Example:** `"pages/module-1-document-content/index.html"`
- **Relative to:** Repository root + `repositories[repository].path`
- **File Type:** `.html`
- **Content:** HTML with embedded images (base64 or relative paths), CSS, etc.
- **Note:** This is often the file used when generating the GitHub Pages site

### `github.local_html_path` (Special Field)
- **Purpose:** Relative path from `github-pages/index.html` to the local HTML file
- **Usage:**
  - Used specifically for the "view canvas" link in the generated index.html
  - Points to the `*_local.html` file in the local filesystem structure
- **Example:** `"../data/current/WINTER-25-26-UPDATES/Module-1/module_1_document_content_local.html"`
- **Format:** `../data/current/WINTER-25-26-UPDATES/{folder_path}/{filename}_local.html`
- **File Type:** `.html`
- **Note:** This is the file that exists in the local filesystem structure, matching the pattern seen in the HTML index file

---

## Field Relationships and Usage in HTML Links

### Four Required Links for Each Page:

1. **"view docx"** → `https://usu.app.box.com/file/{box.file_id}`
   - Uses: `box.file_id`

2. **"edit docx"** → `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={box.file_id}&sharedAccessCode=`
   - Uses: `box.file_id` or `box.word_online_url`

3. **"view canvas"** → `../data/current/WINTER-25-26-UPDATES/{folder_path}/{filename}_local.html`
   - Uses: `github.local_html_path` or constructed from folder structure

4. **"edit canvas"** → `https://usucourses.instructure.com/courses/2879/pages/{canvas.page_id}/edit`
   - Uses: `canvas.page_id` or `canvas.url` + "/edit"

---

## Complete Example Structure

```json
{
  "schema_version": "1.0",
  "course": {
    "id": "2879",
    "name": "Document Accessibility",
    "canvas_url": "https://usucourses.instructure.com/courses/2879",
    "semester": "Winter 2025-26",
    "instructor": ""
  },
  "metadata": {
    "created": "2025-12-12T00:43:24.917Z",
    "last_updated": "2025-12-15T22:00:00.000Z",
    "last_synced": null,
    "version": "1.0.0"
  },
  "repositories": {
    "main": {
      "url": "https://github.com/gjoeckel/canvas_2879",
      "branch": "main",
      "path": "data/current/WINTER-25-26-UPDATES"
    }
  },
  "box": {
    "folder_id": "355471834847",
    "folder_url": "https://usu.app.box.com/folder/355471834847",
    "base_path": "/WINTER-25-26-UPDATES"
  },
  "start_here": {
    "folder_name": "Start-Here",
    "folder_id": "355472814432",
    "subfolders": [
      {
        "folder_name": "1-course-orientation",
        "folder_id": "356024870284",
        "id": "course-orientation",
        "title": "Course Orientation",
        "order": 1,
        "status": "draft",
        "canvas": { /* ... */ },
        "github": { /* ... */ },
        "box": { /* ... */ },
        "sync": { /* ... */ },
        "metadata": { /* ... */ }
      }
    ]
  },
  "modules": [
    {
      "id": "module-1-document-content",
      "title": "Module 1  Document Content",
      "folder_name": "Module-1",
      "box_folder_id": "355472828832",
      "order": 1,
      "status": "draft",
      "canvas": {
        "url": "https://usucourses.instructure.com/courses/2879/pages/module-1-document-content",
        "page_id": "module-1-document-content",
        "published": false,
        "published_at": null
      },
      "github": {
        "repository": "main",
        "source_docx": {
          "path": "pages/module-1-document-content/module-1-document-content.docx",
          "branch": "main"
        },
        "canvas_copy": {
          "path": "pages/module-1-document-content/canvas-copy.html",
          "branch": "main"
        },
        "with_assets": {
          "path": "pages/module-1-document-content/index.html",
          "branch": "main"
        },
        "local_html_path": "../data/current/WINTER-25-26-UPDATES/Module-1/module_1_document_content_local.html"
      },
      "box": {
        "file_id": "2072501663155",
        "file_name": "Module 1_ Document Content.docx",
        "file_url": "https://usu.app.box.com/file/2072501663155",
        "word_online_url": "https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2072501663155&sharedAccessCode=",
        "folder_id": "355472828832",
        "modified_at": null,
        "version": 1
      },
      "sync": {
        "last_synced": null,
        "sync_status": "pending",
        "sync_errors": []
      },
      "metadata": {
        "type": "module",
        "created": "2025-12-12T00:43:24.917Z"
      },
      "sections": [
        {
          "id": "section-1-overview-of-document-accessibility",
          "title": "Section 1  Overview of Document Accessibility",
          "folder_name": "Section-1-1",
          "box_folder_id": "355470702235",
          "order": 1,
          "status": "draft",
          "canvas": { /* ... */ },
          "github": { /* ... */ },
          "box": { /* ... */ },
          "sync": { /* ... */ },
          "metadata": {
            "type": "section",
            "created": "2025-12-12T00:43:24.917Z"
          },
          "las": [
            {
              "id": "overview-of-document-accessibility-part-1",
              "title": "Overview Of Document Accessibility Part 1",
              "folder_name": "LA-1-1-1",
              "box_folder_id": "355473801426",
              "order": 1,
              "status": "draft",
              "canvas": { /* ... */ },
              "github": { /* ... */ },
              "box": { /* ... */ },
              "sync": { /* ... */ },
              "metadata": {
                "type": "la",
                "created": "2025-12-12T00:43:24.917Z"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Summary

The JSON structure maintains a hierarchical organization:
- **Start Here** → subfolders (flat list)
- **Modules** → **Sections** → **LAs** (nested hierarchy)

Each level (except LAs which are leaf nodes) can have:
- Folder information (folder_name, box_folder_id)
- Canvas page information
- GitHub file paths (source_docx, canvas_copy, with_assets, local_html_path)
- Box file information
- Sync tracking
- Metadata

This structure supports:
1. Generating the HTML index page with all four required links
2. Tracking files across Canvas, GitHub, and Box
3. Managing sync operations
4. Maintaining hierarchical organization matching the filesystem structure

