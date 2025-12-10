# Three Methods for Identifying Tracked Changes in DOCX Files on Box

This document outlines three methods to identify tracked changes in the TEXT CONTENT of DOCX files stored on Box, enabling updates to local HTML Canvas files and pushing them to the course.

---

## Method 1: Python-docx with XML Parsing (Direct DOCX Analysis)

### Overview
Extract tracked changes directly from the DOCX file's internal XML structure by parsing revision elements (`w:ins`, `w:del`, `w:moveFrom`, `w:moveTo`).

### Implementation Steps

1. **Download DOCX from Box via API**
   ```python
   import requests
   from boxsdk import Client, OAuth2
   
   # Authenticate with Box
   oauth = OAuth2(client_id, client_secret, access_token)
   client = Client(oauth)
   
   # Download file
   file_content = client.file(file_id).content()
   ```

2. **Extract DOCX as ZIP and Parse XML**
   ```python
   import zipfile
   from xml.etree import ElementTree as ET
   
   # DOCX is a ZIP file
   with zipfile.ZipFile(io.BytesIO(file_content)) as docx:
       # Extract main document XML
       document_xml = docx.read('word/document.xml')
       root = ET.fromstring(document_xml)
       
       # Find all tracked changes
       namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
       
       # Find insertions (w:ins)
       insertions = root.findall('.//w:ins', namespaces)
       # Find deletions (w:del)
       deletions = root.findall('.//w:del', namespaces)
   ```

3. **Extract Text from Revision Elements**
   ```python
   def extract_revision_text(revision_element, namespaces):
       """Extract text from a revision element (insertion or deletion)."""
       text_elements = revision_element.findall('.//w:t', namespaces)
       return ' '.join([elem.text for elem in text_elements if elem.text])
   
   # Process each revision
   for ins in insertions:
       author = ins.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author')
       date = ins.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date')
       text = extract_revision_text(ins, namespaces)
       print(f"INSERTION by {author} on {date}: {text}")
   ```

### Advantages
- Direct access to all tracked changes metadata (author, date, type)
- No external dependencies beyond standard libraries
- Works with any DOCX file that has tracked changes enabled

### Limitations
- Requires understanding of DOCX XML structure
- More complex to implement
- Need to handle namespaces correctly

### Libraries Required
- `boxsdk` or `requests` (for Box API)
- `zipfile` (standard library)
- `xml.etree.ElementTree` (standard library)

---

## Method 2: python-docx with Revision Tracking Extension

### Overview
Use the `python-docx` library with custom extensions or additional libraries to extract tracked changes from DOCX files.

### Implementation Steps

1. **Download DOCX from Box**
   ```python
   import requests
   from boxsdk import Client, OAuth2
   
   oauth = OAuth2(client_id, client_secret, access_token)
   client = Client(oauth)
   file_content = client.file(file_id).content()
   ```

2. **Use python-docx with XML Access**
   ```python
   from docx import Document
   from docx.oxml import parse_xml
   from docx.oxml.ns import qn
   import io
   
   # Load document
   doc = Document(io.BytesIO(file_content))
   
   # Access underlying XML
   document_part = doc.part
   document_xml = document_part.blob
   
   # Parse XML for revisions
   from xml.etree import ElementTree as ET
   root = ET.fromstring(document_xml)
   namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
   
   # Find tracked changes
   revisions = []
   for paragraph in doc.paragraphs:
       # Check paragraph XML for revisions
       p_xml = paragraph._element
       ins_elements = p_xml.findall('.//w:ins', namespaces)
       del_elements = p_xml.findall('.//w:del', namespaces)
       
       for ins in ins_elements:
           text = ''.join([t.text for t in ins.findall('.//w:t', namespaces) if t.text])
           revisions.append({
               'type': 'insertion',
               'text': text,
               'author': ins.get(qn('w:author')),
               'date': ins.get(qn('w:date'))
           })
   ```

3. **Alternative: Use python-docx-revisions Library**
   ```python
   # If available, use specialized library
   from docx_revisions import Document
   
   doc = Document(io.BytesIO(file_content))
   revisions = doc.get_revisions()
   
   for revision in revisions:
       print(f"{revision.type}: {revision.text} by {revision.author}")
   ```

### Advantages
- Higher-level API than raw XML parsing
- Can leverage existing python-docx knowledge
- May have specialized libraries for revisions

### Limitations
- `python-docx` doesn't natively support tracked changes
- May need custom extensions or additional libraries
- Less direct access to revision metadata

### Libraries Required
- `python-docx` (`pip install python-docx`)
- `boxsdk` or `requests` (for Box API)
- Optional: `python-docx-revisions` or similar

---

## Method 3: Box Version History Comparison

### Overview
Compare different versions of the DOCX file stored in Box to identify changes, then map those changes to tracked changes in the document.

### Implementation Steps

1. **Get File Version History from Box API**
   ```python
   import requests
   
   BOX_API_BASE = 'https://api.box.com/2.0'
   headers = {'Authorization': f'Bearer {access_token}'}
   
   # Get file versions
   versions_url = f'{BOX_API_BASE}/files/{file_id}/versions'
   response = requests.get(versions_url, headers=headers)
   versions = response.json()['entries']
   
   # Get current and previous version
   current_version = versions[0]
   previous_version = versions[1] if len(versions) > 1 else None
   ```

2. **Download Both Versions**
   ```python
   # Download current version
   current_download = requests.get(
       f'{BOX_API_BASE}/files/{file_id}/content',
       headers=headers
   )
   current_content = current_download.content
   
   # Download previous version
   if previous_version:
       prev_download = requests.get(
           f'{BOX_API_BASE}/files/{file_id}/versions/{previous_version["id"]}/content',
           headers=headers
       )
       previous_content = prev_download.content
   ```

3. **Extract Text and Compare**
   ```python
   from docx import Document
   import difflib
   import io
   
   def extract_text(docx_content):
       """Extract all text from DOCX."""
       doc = Document(io.BytesIO(docx_content))
       text = []
       for paragraph in doc.paragraphs:
           text.append(paragraph.text)
       return '\n'.join(text)
   
   # Extract text from both versions
   current_text = extract_text(current_content)
   previous_text = extract_text(previous_content) if previous_content else ''
   
   # Use difflib to find differences
   diff = difflib.unified_diff(
       previous_text.splitlines(keepends=True),
       current_text.splitlines(keepends=True),
       lineterm=''
   )
   
   # Process differences
   changes = []
   for line in diff:
       if line.startswith('+') and not line.startswith('+++'):
           changes.append({'type': 'addition', 'text': line[1:]})
       elif line.startswith('-') and not line.startswith('---'):
           changes.append({'type': 'deletion', 'text': line[1:]})
   ```

4. **Map to Tracked Changes (Optional)**
   ```python
   # Cross-reference with actual tracked changes in current version
   # to get author and date information
   # (Combine with Method 1 or 2)
   ```

### Advantages
- Works even if tracked changes aren't enabled
- Can identify all changes between versions
- Leverages Box's built-in versioning system

### Limitations
- Requires multiple file downloads
- Doesn't capture author/date metadata from tracked changes
- May miss formatting-only changes
- Less precise than direct tracked changes extraction

### Libraries Required
- `requests` (for Box API)
- `python-docx` (for text extraction)
- `difflib` (standard library, for comparison)

---

## Recommended Approach: Hybrid Method

### Combine Methods 1 and 3

1. **Use Method 1** to extract tracked changes with full metadata (author, date, type)
2. **Use Method 3** as a fallback for files without tracked changes enabled
3. **Map results** to identify which HTML files need updating

### Implementation Workflow

```python
def identify_changes(file_id, access_token):
    """Identify tracked changes in a DOCX file on Box."""
    
    # Try Method 1: Extract tracked changes directly
    tracked_changes = extract_tracked_changes_from_docx(file_id, access_token)
    
    if tracked_changes:
        return tracked_changes
    
    # Fallback to Method 3: Version comparison
    return compare_file_versions(file_id, access_token)

def update_html_from_changes(tracked_changes, html_file_path):
    """Update local HTML file based on tracked changes."""
    # Parse HTML
    # Apply changes
    # Save updated HTML

def push_to_canvas(html_file_path, canvas_page_url):
    """Push updated HTML to Canvas course."""
    # Use Canvas API to update page content
    pass
```

---

## Next Steps

1. **Choose a method** based on your needs:
   - Method 1: Most comprehensive, requires XML knowledge
   - Method 2: Easier if python-docx extensions exist
   - Method 3: Works without tracked changes, less metadata

2. **Implement the chosen method** with Box API integration

3. **Create mapping** between DOCX files and HTML files

4. **Automate the workflow** to detect changes and update Canvas

---

## References

- [Box API Documentation](https://developer.box.com/reference/)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [DOCX File Format Specification](https://www.ecma-international.org/publications-and-standards/standards/ecma-376/)
- [Canvas API Documentation](https://canvas.instructure.com/doc/api/)

