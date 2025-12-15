# Path Update Guide

**Purpose:** Comprehensive documentation of all path types that need updating during reorganization

---

## Path Types to Update

### 1. Python Script Imports

**Type:** `import` statements, `from ... import`

**Examples:**
```python
# OLD (if scripts import each other)
from rename_images_by_canvas_id import some_function

# NEW (after moving to scripts/core/)
from scripts.core.rename_images_by_canvas_id import some_function
# OR use relative imports within scripts/
from .core.rename_images_by_canvas_id import some_function
```

**Files to check:**
- Any Python script that imports other scripts
- Scripts that use `sys.path.append()` to add parent directories

**Search patterns:**
- `import ` (followed by script name)
- `from ` (followed by script name)
- `sys.path`
- `Path(__file__).parent`

---

### 2. File Path References (Hardcoded)

**Type:** Hardcoded file paths in Python scripts

**Examples:**
```python
# OLD
config_file = Path('config.toml')
css_file = Path('canvas-fonts.css')
reference_docx = Path('canvas-reference.docx')
downloaded_dir = Path('WINTER 25-26 COURSE UPDATES/365_Update')
html_dir = Path('WINTER-25-26-UPDATES')

# NEW
config_file = Path(__file__).parent.parent / 'config.toml'
css_file = Path(__file__).parent.parent / 'assets' / 'css' / 'canvas-fonts.css'
reference_docx = Path(__file__).parent.parent / 'assets' / 'templates' / 'canvas-reference.docx'
downloaded_dir = Path(__file__).parent.parent / 'data' / 'archive' / 'WINTER 25-26 COURSE UPDATES' / '365_Update'
html_dir = Path(__file__).parent.parent / 'data' / 'current' / 'WINTER-25-26-UPDATES'
```

**Files to check:**
- All Python scripts with `Path()` or string paths
- Scripts that reference:
  - `config.toml`
  - CSS files (`*.css`)
  - `canvas-reference.docx`
  - Data directories (`WINTER-25-26-UPDATES`, `WINTER 25-26 COURSE UPDATES`)
  - JSON config files (`*.json`)

**Search patterns:**
- `Path('`
- `Path("`
- `'config.toml'`
- `'*.css'`
- `'canvas-reference.docx'`
- `'WINTER-25-26-UPDATES'`
- `'WINTER 25-26 COURSE UPDATES'`
- `'*.json'`

---

### 3. Shell Script Paths

**Type:** Paths in shell scripts (`.sh` files)

**Examples:**
```bash
# OLD
python3 html-to-docx.py --input file.html
cd "WINTER-25-26-UPDATES"

# NEW
python3 scripts/core/html-to-docx.py --input file.html
cd "data/current/WINTER-25-26-UPDATES"
```

**Files to check:**
- `*.sh` files
- Scripts that call Python scripts
- Scripts that change directories

**Search patterns:**
- `python3 ` (followed by script name)
- `cd `
- `"WINTER-`
- `'WINTER-`

---

### 4. CSS File References in HTML

**Type:** `<link>` tags in HTML files pointing to CSS

**Examples:**
```html
<!-- OLD -->
<link href="../../canvas-fonts.css" rel="stylesheet"/>

<!-- NEW -->
<link href="../../assets/css/canvas-fonts.css" rel="stylesheet"/>
```

**Files to check:**
- All HTML files in `WINTER-25-26-UPDATES/`
- Local HTML files (`*_local.html`)
- Original HTML files

**Search patterns:**
- `href="` (followed by `*.css`)
- `href='` (followed by `*.css`)

**Note:** This is already handled by `fix-css-paths.py`, but paths will need to be updated to point to `assets/css/` instead of root.

---

### 5. JSON Config File References

**Type:** References to JSON config files

**Examples:**
```python
# OLD
with open('box-file-ids.json', 'r') as f:
with open('.box-api-config.json', 'r') as f:

# NEW
config_dir = Path(__file__).parent.parent / 'config'
with open(config_dir / 'box-file-ids.json', 'r') as f:
with open(config_dir / '.box-api-config.json', 'r') as f:
```

**Files to check:**
- Scripts that read/write JSON files
- Scripts that reference:
  - `box-file-ids.json`
  - `.box-api-config.json`
  - `canvas-page-links.json`
  - `docx-html-mapping.json`

**Search patterns:**
- `open('*.json'`
- `open("*.json"`
- `json.load(open('`
- `Path('*.json'`

---

### 6. Docker File Paths

**Type:** Paths in Dockerfile and docker-compose.yml

**Examples:**
```dockerfile
# OLD (Dockerfile)
COPY html-to-docx.py /app/
COPY config.toml /app/
COPY canvas-reference.docx /app/

# NEW
COPY scripts/core/html-to-docx.py /app/scripts/core/
COPY config.toml /app/
COPY assets/templates/canvas-reference.docx /app/assets/templates/
```

**Files to check:**
- `Dockerfile`
- `docker-compose.yml`

**Search patterns:**
- `COPY `
- `ADD `
- `WORKDIR `
- Volume mounts in docker-compose.yml

---

### 7. Documentation Cross-References

**Type:** Links between markdown files

**Examples:**
```markdown
<!-- OLD -->
See [HTML-TO-DOCX-WORKFLOW.md](./HTML-TO-DOCX-WORKFLOW.md)

<!-- NEW -->
See [HTML-TO-DOCX-WORKFLOW.md](../workflow/HTML-TO-DOCX-WORKFLOW.md)
```

**Files to check:**
- All `.md` files
- Links to other documentation
- Links to scripts
- Links to data files

**Search patterns:**
- `[.*](.*\.md)`
- `[.*](.*\.py)`
- `[.*](.*\.html)`

---

### 8. GitHub Pages Configuration

**Type:** Paths in GitHub Pages config files

**Examples:**
```yaml
# OLD (_config.yml)
source: docs

# NEW
source: github-pages
```

**Files to check:**
- `_config.yml`
- `.nojekyll` location
- GitHub Actions workflows (if any)

**Search patterns:**
- `source:`
- `docs/`
- References to `docs/` directory

---

### 9. Script Execution Paths

**Type:** Paths used when scripts are executed

**Examples:**
```python
# OLD
script_path = Path('rename-images-by-canvas-id.py')

# NEW
script_path = Path(__file__).parent.parent / 'scripts' / 'core' / 'rename-images-by-canvas-id.py'
```

**Files to check:**
- Scripts that call other scripts via subprocess
- Scripts that reference their own location
- `batch-rename-images.py` (calls `rename-images-by-canvas-id.py`)

**Search patterns:**
- `subprocess.run([`
- `Path(__file__).parent`
- Script names in strings

---

### 10. Relative Path Calculations

**Type:** Calculations of relative paths between files

**Examples:**
```python
# OLD
html_dir = Path('WINTER-25-26-UPDATES/Module-1')
css_file = Path('canvas-fonts.css')
rel_path = os.path.relpath(css_file, html_dir)  # Calculates: ../../canvas-fonts.css

# NEW
html_dir = Path('data/current/WINTER-25-26-UPDATES/Module-1')
css_file = Path('assets/css/canvas-fonts.css')
rel_path = os.path.relpath(css_file, html_dir)  # Calculates: ../../../../assets/css/canvas-fonts.css
```

**Files to check:**
- `fix-css-paths.py` (calculates CSS relative paths)
- `html-to-docx.py` (calculates image relative paths)
- `rename-images-by-canvas-id.py` (calculates image relative paths)

**Search patterns:**
- `os.path.relpath(`
- `Path().relative_to(`
- `calculate_relative_path(`

---

### 11. Default Arguments in Scripts

**Type:** Default values for path arguments

**Examples:**
```python
# OLD
parser.add_argument('--html-dir', default='WINTER-25-26-UPDATES')
parser.add_argument('--downloaded-dir', default='WINTER 25-26 COURSE UPDATES/365_Update')
parser.add_argument('--config', default='config.toml')

# NEW
parser.add_argument('--html-dir', default='data/current/WINTER-25-26-UPDATES')
parser.add_argument('--downloaded-dir', default='data/archive/WINTER 25-26 COURSE UPDATES/365_Update')
parser.add_argument('--config', default='config.toml')  # Still in root
```

**Files to check:**
- All scripts with `argparse` default values
- Scripts with `--html-dir`, `--downloaded-dir`, `--image-dir` arguments

**Search patterns:**
- `default=Path('`
- `default='WINTER-`
- `default="WINTER-`

---

### 12. Image Path References

**Type:** References to image files in HTML and scripts

**Examples:**
```python
# OLD
image_dir = Path('WINTER-25-26-UPDATES/Module-1/Section-1-1/LA-1-1-1')
image_path = image_dir / '1235852.png'

# NEW
image_dir = Path('data/current/WINTER-25-26-UPDATES/Module-1/Section-1-1/LA-1-1-1')
image_path = image_dir / '1235852.png'
```

**Files to check:**
- `html-to-docx.py` (image path resolution)
- `rename-images-by-canvas-id.py` (image path handling)
- `map-and-copy-files.py` (image finding)

**Search patterns:**
- `*.png`
- `*.jpg`
- `*.jpeg`
- `*.gif`
- `image_dir`
- `image_path`

---

### 13. Template/Reference File Paths

**Type:** References to template files like `canvas-reference.docx`

**Examples:**
```python
# OLD
reference_docx = Path('canvas-reference.docx')

# NEW
reference_docx = Path(__file__).parent.parent / 'assets' / 'templates' / 'canvas-reference.docx'
```

**Files to check:**
- `html-to-docx.py` (uses `canvas-reference.docx`)
- Any script that references template files

**Search patterns:**
- `canvas-reference.docx`
- `reference.docx`
- `template`

---

### 14. Working Directory Assumptions

**Type:** Scripts that assume they're run from project root

**Examples:**
```python
# OLD (assumes script run from project root)
os.chdir('WINTER-25-26-UPDATES')

# NEW (should use absolute or relative to script location)
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root / 'data' / 'current' / 'WINTER-25-26-UPDATES')
```

**Files to check:**
- Scripts with `os.chdir()`
- Scripts that use relative paths without `Path(__file__).parent`

**Search patterns:**
- `os.chdir(`
- `chdir(`
- Relative paths without `__file__` reference

---

## Update Strategy

### Step 1: Identify All Path References
Use grep to find all instances:
```bash
grep -r "WINTER-25-26-UPDATES" scripts/
grep -r "WINTER 25-26 COURSE UPDATES" scripts/
grep -r "config.toml" scripts/
grep -r "\.css" scripts/
grep -r "canvas-reference.docx" scripts/
```

### Step 2: Create Helper Functions
Create a `scripts/utils/paths.py` with helper functions:
```python
from pathlib import Path

def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent.parent

def get_config_path(filename='config.toml'):
    """Get path to config file."""
    return get_project_root() / filename

def get_data_dir(subdir='current'):
    """Get path to data directory."""
    return get_project_root() / 'data' / subdir

def get_assets_dir(subdir='css'):
    """Get path to assets directory."""
    return get_project_root() / 'assets' / subdir
```

### Step 3: Update Scripts Systematically
1. Update imports first
2. Update hardcoded paths
3. Update default arguments
4. Test each script

### Step 4: Update Documentation
Update all markdown files with new paths.

---

## Testing Checklist

After reorganization, test:

- [ ] All scripts can find `config.toml`
- [ ] All scripts can find CSS files (if needed)
- [ ] All scripts can find `canvas-reference.docx`
- [ ] All scripts can access data directories
- [ ] HTML files can find CSS files (relative paths)
- [ ] Batch scripts can call other scripts
- [ ] Docker builds work with new paths
- [ ] Documentation links work

---

## Common Patterns to Replace

| Old Pattern | New Pattern |
|------------|-------------|
| `Path('config.toml')` | `get_project_root() / 'config.toml'` |
| `Path('WINTER-25-26-UPDATES')` | `get_project_root() / 'data' / 'current' / 'WINTER-25-26-UPDATES'` |
| `Path('canvas-fonts.css')` | `get_project_root() / 'assets' / 'css' / 'canvas-fonts.css'` |
| `Path('canvas-reference.docx')` | `get_project_root() / 'assets' / 'templates' / 'canvas-reference.docx'` |
| `Path('box-file-ids.json')` | `get_project_root() / 'config' / 'box-file-ids.json'` |
| `'../../canvas-fonts.css'` | `'../../../../assets/css/canvas-fonts.css'` (depends on depth) |

---

## Files Most Likely to Need Updates

**High Priority:**
1. `batch-rename-images.py` - Calls other scripts
2. `html-to-docx.py` - References CSS, reference DOCX, data dirs
3. `rename-images-by-canvas-id.py` - References data dirs, config
4. `fix-css-paths.py` - Calculates CSS relative paths
5. `map-and-copy-files.py` - References data dirs

**Medium Priority:**
6. All Box API scripts - Reference config files
7. All Canvas API scripts - Reference data dirs
8. GitHub Pages scripts - Reference docs/data

**Low Priority:**
9. Utility scripts - May have fewer path dependencies
10. Documentation - Update links
