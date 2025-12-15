# Directory Organization Proposal

**Date:** December 11, 2025
**Current State:** 100+ files in root directory
**Goal:** Clean, logical organization for maintainability

---

## Current Problems

1. **100+ files in root directory** - Hard to navigate
2. **Mixed concerns** - Scripts, docs, configs, data all mixed together
3. **No clear structure** - Difficult to find related files
4. **Large data directories** - `WINTER 25-26 COURSE UPDATES/` (51M) and `WINTER-25-26-UPDATES/` (14M) in root

---

## Proposed Structure

```
canvas_2879/
├── README.md                          # Main project README
├── config.toml                        # Canvas API config (keep in root for easy access)
├── .gitignore
├── .nojekyll
│
├── scripts/                           # All Python scripts organized by purpose
│   ├── core/                          # Core workflow scripts (most used)
│   │   ├── html-to-docx.py
│   │   ├── rename-images-by-canvas-id.py
│   │   ├── batch-rename-images.py
│   │   ├── fix-css-paths.py
│   │   ├── map-and-copy-files.py
│   │   └── create-directory-structure.py
│   │
│   ├── canvas/                        # Canvas API scripts
│   │   ├── download-all-canvas-pages.py
│   │   ├── download-page-content.py
│   │   ├── update-canvas-api.py
│   │   ├── update-canvas-from-docx.py
│   │   └── extract-canvas-links.py
│   │
│   ├── box/                           # Box API scripts
│   │   ├── get-box-file-ids-api.py
│   │   ├── get-box-file-ids-rest.py
│   │   ├── get-box-oauth-token.py
│   │   ├── extract-box-file-ids.py
│   │   ├── add-box-office-links.py
│   │   └── test-box-reviewing-mode.py
│   │
│   ├── github/                        # GitHub Pages scripts
│   │   ├── create-github-pages.py
│   │   ├── create-github-pages-v2.py
│   │   ├── create-docx-editor-page.py
│   │   └── update-docx-editor-page.py
│   │
│   ├── mapping/                       # DOCX/HTML mapping scripts
│   │   ├── create-docx-html-mapping.py
│   │   ├── update-html-using-mapping.py
│   │   └── restructure-docx-mapping.py
│   │
│   └── utility/                      # Utility scripts
│       ├── enable-track-changes.py
│       ├── create-reference-docx.py
│       ├── add-missing-learning-modules.py
│       ├── rename-and-update-images.py
│       └── create-html-directory-structure.py
│
├── docs/                              # All documentation
│   ├── workflow/                      # Workflow guides
│   │   ├── HTML-TO-DOCX-WORKFLOW.md
│   │   ├── html-to-docx-conversion-plan.md
│   │   ├── PROCESS-GUIDE.md
│   │   └── REFACTORING-SUMMARY.md
│   │
│   ├── box/                          # Box API documentation
│   │   ├── BOX-API-SETUP.md
│   │   ├── BOX-FILE-ID-WORKFLOW.md
│   │   ├── BOX-OAUTH-SETUP.md
│   │   ├── BOX-TOKEN-SETUP.md
│   │   ├── QUICK-START-BOX-LINKS.md
│   │   └── README-BOX-LINKS.md
│   │
│   ├── canvas/                        # Canvas API documentation
│   │   ├── UPDATE-CANVAS-README.md
│   │   ├── README-PAGE-CONTENT.md
│   │   └── CANVAS-UI-HIDE-INSTRUCTIONS.md
│   │
│   ├── technical/                     # Technical documentation
│   │   ├── DOCX-HTML-MAPPING.md
│   │   ├── MAPPING-APPROACH.md
│   │   ├── IMPROVED-CONVERSION-OPTIONS.md
│   │   ├── TRACKED-CHANGES-GUIDE.md
│   │   ├── TRACKED-CHANGES-METHODS.md
│   │   └── FORMATTING-NOTES.md
│   │
│   ├── setup/                         # Setup guides
│   │   ├── DOCKER-SETUP.md
│   │   ├── LOCAL-DEVELOPMENT.md
│   │   ├── OAUTH-SETUP-INSTRUCTIONS.md
│   │   ├── QUICK-OAUTH-SETUP.md
│   │   └── FIX-REDIRECT-URI.md
│   │
│   ├── css/                          # CSS documentation
│   │   ├── CUSTOM-CSS-GUIDE.md
│   │   └── QUICK-CSS-REFERENCE.md
│   │
│   └── other/                         # Other documentation
│       ├── IMPLEMENTATION-PLAN.md
│       ├── visual-regression-testing-git-intergration.md
│       ├── add-box-office-links.md
│       └── rename-and-update-images-plan.md
│
├── assets/                            # Static assets
│   ├── css/                           # CSS files
│   │   ├── canvas-fonts.css
│   │   ├── canvas-variables.css
│   │   ├── canvas-common.css
│   │   ├── canvas-wiki-page.css
│   │   ├── canvas-custom-overrides.css
│   │   ├── canvas_global_app.css
│   │   ├── catalog_canvas_global.css
│   │   ├── webaimCatalog.css
│   │   ├── AD-365-V4.css
│   │   └── hide-canvas-ui.css
│   │
│   ├── templates/                     # Reference files
│   │   └── canvas-reference.docx
│   │
│   └── js/                            # JavaScript files
│       └── canvas-ui-hide-bookmarklet.js
│
├── config/                            # Configuration files
│   ├── .box-api-config.json           # Box API config (move from root)
│   ├── box-file-ids.json
│   ├── box-file-ids-template.json
│   ├── canvas-page-links.json
│   ├── canvas-page-links.txt
│   └── docx-html-mapping.json
│
├── data/                              # Data directories
│   ├── current/                       # Current working structure
│   │   └── WINTER-25-26-UPDATES/      # (symlink or move)
│   │
│   └── archive/                       # Archive/backup
│       └── WINTER 25-26 COURSE UPDATES/  # Original structure (backup)
│
├── github-pages/                     # GitHub Pages output (rename from docs/)
│   ├── .nojekyll
│   ├── index.html
│   └── canvas-module-1.html
│
└── docker/                            # Docker files
    ├── Dockerfile
    ├── docker-compose.yml
    └── .dockerignore
```

---

## Benefits

1. **Clear separation of concerns** - Scripts, docs, configs, data all organized
2. **Easy navigation** - Related files grouped together
3. **Scalable** - Easy to add new files in appropriate locations
4. **Professional structure** - Standard project organization
5. **Maintainable** - Future developers can find files easily

---

## Migration Plan

### Phase 1: Create Structure
1. Create all new directories
2. Keep old files in place (no deletion yet)

### Phase 2: Move Files
1. Move Python scripts to `scripts/` subdirectories
2. Move documentation to `docs/` subdirectories
3. Move CSS files to `assets/css/`
4. Move JSON configs to `config/`
5. Move Docker files to `docker/`

### Phase 3: Update References
1. Update script imports/paths
2. Update documentation links
3. Update any hardcoded paths
4. Test all scripts still work

### Phase 4: Cleanup
1. Remove old empty directories
2. Update README.md with new structure
3. Verify everything works

---

## Files to Keep in Root

- `README.md` - Main project documentation
- `config.toml` - Canvas API config (needed by scripts)
- `.gitignore` - Git configuration
- `.nojekyll` - GitHub Pages config

---

## Notes

- **Script paths**: May need to update relative imports/paths after moving
- **Config paths**: Update script references to `config/` directory
- **Data directories**: Consider if `WINTER 25-26 COURSE UPDATES/` should be archived or removed
- **GitHub Pages**: Current `docs/` directory should be renamed to `github-pages/` for clarity

---

## Questions to Consider

1. Should `WINTER 25-26 COURSE UPDATES/` be archived or can it be removed?
2. Do any scripts have hardcoded paths that need updating?
3. Should we create a `scripts/__init__.py` to make it a Python package?
4. Should we add a `requirements.txt` for Python dependencies?
