# Course Map Prerequisites Checklist

**Date**: 2025-12-11
**Box Folder**: [WINTER-25-26-UPDATES](https://usu.app.box.com/folder/355471834847)

## ✅ Completed

### 1. DOCX Files Created
- ✅ All Module HTML files converted to DOCX
- ✅ All Section HTML files converted to DOCX
- ✅ Total: 16 DOCX files (5 Modules + 11 Sections)

### 2. DOCX Files Uploaded to Box
- ✅ All Module DOCX files uploaded to Box
- ✅ All Section DOCX files uploaded to Box
- ✅ Box file IDs captured for all files
- ✅ Box folder structure matches local structure

### 3. Box Folder Structure
- ✅ Root folder: `355471834847` (WINTER-25-26-UPDATES)
- ✅ Module folders exist: Module-1 through Module-5
- ✅ Section folders exist within each Module

## 📋 Required Information for Course Map

### Course Information
- [ ] **Canvas Course ID**: Required for `course.id`
- [ ] **Course Name**: Required for `course.name`
- [ ] **Canvas URL**: Optional but recommended for `course.canvas_url`
- [ ] **Semester/Term**: Optional for `course.semester`
- [ ] **Instructor**: Optional for `course.instructor`

### Box Configuration
- ✅ **Root Box Folder ID**: `355471834847`
- ✅ **Box Folder Structure**: All Module and Section folders exist
- ✅ **Box File IDs**: All DOCX files have Box file IDs

### GitHub Repository (Optional - for future sync)
- [ ] **Main Repository URL**: For `repositories.main.url`
- [ ] **Repository Branch**: Default `main`
- [ ] **Repository Path**: Base path for course files

### Page Information
- ✅ **Box File IDs**: Available from upload summary
- ✅ **File Names**: Available from local files
- ✅ **Folder Structure**: Matches Box structure
- [ ] **Page Titles**: Can be extracted from file names
- [ ] **Page Slugs**: Can be generated from file names
- [ ] **Page Order**: Need to determine module/section order

## 🔍 What We Have

### Box File IDs (from upload summary)

**Module Files**:
- Module 1: `2072501663155` (Folder: `355472828832`)
- Module 2: `2072499050156` (Folder: `355474168042`)
- Module 3: `2072500093642` (Folder: `355474585317`)
- Module 4: `2072502649975` (Folder: `355473798714`)
- Module 5: `2072501435668` (Folder: `355473710096`)

**Section Files**:
- Section 1-1: `2072505447671` (Folder: `355470702235`)
- Section 1-2: `2072505575419` (Folder: `355472944690`)
- Section 1-3: `2072498709241` (Folder: `355474103285`)
- Section 1-4: `2072494914863` (Folder: `355470493749`)
- Section 1-5: `2072501754284` (Folder: `355472847649`)
- Section 2-1: `2072499875902`
- Section 2-2: `2072501742533`
- Section 2-3: `2072494223656`
- Section 3-3: `2072500079806`
- Section 4-1: `2072501906242`
- Section 5-4: `2072501781312`

## ❓ Questions to Answer

1. **Canvas Course Information**:
   - What is the Canvas course ID?
   - What is the course name?
   - Do you have the Canvas course URL?

2. **GitHub Repository** (if planning to sync to GitHub):
   - Do you have a GitHub repository for this course?
   - What is the repository URL?
   - What branch should be used?

3. **Page Organization**:
   - Should Modules and Sections be separate pages in the course map?
   - What order should pages appear?
   - Are there any pages missing (e.g., other sections not yet converted)?

## ✅ Ready to Create Course Map

**Minimum Required**:
- ✅ Box file IDs for all DOCX files
- ✅ Box folder structure
- ✅ File names and paths

**Recommended**:
- Canvas course ID and name
- GitHub repository information (if using GitHub sync)

## Next Steps

1. **Gather Missing Information** (if needed):
   - Canvas course ID and name
   - GitHub repository URL (optional)

2. **Create Course Map Script**:
   - Use `discover-box-files.js` as reference
   - Generate course map from uploaded Box files
   - Include all Box file IDs and folder information

3. **Validate Course Map**:
   - Run schema validation
   - Verify all Box file IDs are correct
   - Check folder structure matches

4. **Upload Course Map to Box**:
   - Save course map as JSON
   - Upload to Box root folder or designated location
