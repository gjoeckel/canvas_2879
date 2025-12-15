#!/usr/bin/env node
/**
 * Discover all pages from filesystem and map module > section > LA hierarchy
 *
 * This script:
 * 1. Scans filesystem for all DOCX files
 * 2. Maps each file to its Module > Section > LA position
 * 3. Updates course-map.json with hierarchy for all pages
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'fs';
import { join, dirname, basename, extname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const COURSE_MAP_PATH = join(__dirname, 'course-map.json');
const BASE_DIR = __dirname;

/**
 * Extract module number from folder name (e.g., "Module-1" -> 1)
 */
function extractModuleNumber(name) {
  const match = name.match(/^Module-(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Extract section numbers from folder name (e.g., "Section-1-2" -> module: 1, section: 2)
 */
function extractSectionNumbers(name) {
  const match = name.match(/^Section-(\d+)-(\d+)/i);
  if (match) {
    return {
      module: parseInt(match[1], 10),
      section: parseInt(match[2], 10)
    };
  }
  return null;
}

/**
 * Extract LA numbers from folder name (e.g., "LA-1-2-3" -> module: 1, section: 2, la: 3)
 */
function extractLANumbers(name) {
  const match = name.match(/^LA-(\d+)-(\d+)-(\d+)/i);
  if (match) {
    return {
      module: parseInt(match[1], 10),
      section: parseInt(match[2], 10),
      la: parseInt(match[3], 10)
    };
  }
  return null;
}

/**
 * Convert filename to slug
 */
function filenameToSlug(filename) {
  return basename(filename, extname(filename))
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');
}

/**
 * Convert filename to title
 */
function filenameToTitle(filename) {
  return basename(filename, extname(filename))
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Scan directory recursively for DOCX files
 */
function scanForDocxFiles(dir, hierarchy = { module: null, section: null, la: null }) {
  const files = [];

  try {
    const entries = readdirSync(dir);

    for (const entry of entries) {
      const entryPath = join(dir, entry);

      // Skip node_modules and other non-content directories
      if (entry === 'node_modules' || entry.startsWith('.')) continue;

      if (statSync(entryPath).isDirectory()) {
        let newHierarchy = { ...hierarchy };

        // Check for Module folder
        const moduleNum = extractModuleNumber(entry);
        if (moduleNum) {
          newHierarchy.module = {
            number: moduleNum,
            folder_name: entry
          };
        }

        // Check for Section folder
        const sectionNums = extractSectionNumbers(entry);
        if (sectionNums) {
          newHierarchy.module = {
            number: sectionNums.module,
            folder_name: `Module-${sectionNums.module}`
          };
          newHierarchy.section = {
            number: sectionNums.section,
            folder_name: entry
          };
        }

        // Check for LA folder
        const laNums = extractLANumbers(entry);
        if (laNums) {
          newHierarchy.module = {
            number: laNums.module,
            folder_name: `Module-${laNums.module}`
          };
          newHierarchy.section = {
            number: laNums.section,
            folder_name: `Section-${laNums.module}-${laNums.section}`
          };
          newHierarchy.la = {
            number: laNums.la,
            folder_name: entry
          };
        }

        // Recursively scan subdirectories
        files.push(...scanForDocxFiles(entryPath, newHierarchy));
      } else if (entry.endsWith('.docx')) {
        // Found a DOCX file
        const filename = basename(entry);
        const slug = filenameToSlug(filename);
        const title = filenameToTitle(filename);

        files.push({
          filename,
          slug,
          title,
          path: entryPath,
          relative_path: entryPath.replace(BASE_DIR + '/', ''),
          hierarchy: { ...hierarchy }
        });
      }
    }
  } catch (err) {
    // Ignore permission errors
  }

  return files;
}

/**
 * Determine page type from hierarchy
 */
function determinePageType(hierarchy) {
  if (hierarchy.la) return 'la';
  if (hierarchy.section) return 'section';
  if (hierarchy.module) return 'module';
  return 'other';
}

/**
 * Find matching page in course map
 */
function findMatchingPage(pages, docxFile) {
  // Try to match by slug
  let match = pages.find(p => p.slug === docxFile.slug);
  if (match) return match;

  // Try to match by title (fuzzy)
  match = pages.find(p => {
    const pTitle = (p.title || '').toLowerCase().trim();
    const fTitle = docxFile.title.toLowerCase().trim();
    return pTitle === fTitle || pTitle.includes(fTitle) || fTitle.includes(pTitle);
  });
  if (match) return match;

  // Try to match by box file_name
  match = pages.find(p => {
    const boxFileName = (p.box?.file_name || '').toLowerCase().replace(/\.docx$/i, '');
    const fName = docxFile.filename.toLowerCase().replace(/\.docx$/i, '');
    return boxFileName === fName || boxFileName.replace(/_/g, ' ') === fName.replace(/_/g, ' ');
  });

  return match || null;
}

/**
 * Main function
 */
async function main() {
  console.log('🔍 Scanning filesystem for DOCX files...');
  const docxFiles = scanForDocxFiles(BASE_DIR);

  console.log(`\n📊 Found ${docxFiles.length} DOCX files`);
  console.log(`  Modules: ${new Set(docxFiles.map(f => f.hierarchy.module?.number).filter(Boolean)).size}`);
  console.log(`  Sections: ${new Set(docxFiles.map(f => `${f.hierarchy.module?.number}-${f.hierarchy.section?.number}`).filter(s => s.includes('-'))).size}`);
  console.log(`  LAs: ${new Set(docxFiles.map(f => f.hierarchy.la?.number).filter(Boolean)).size}`);

  console.log('\n📖 Reading course-map.json...');
  const courseMap = JSON.parse(readFileSync(COURSE_MAP_PATH, 'utf8'));

  console.log(`\n🔄 Updating hierarchy for ${courseMap.pages.length} existing pages...`);

  // Update hierarchy for existing pages
  for (const page of courseMap.pages) {
    // Try to find matching DOCX file with multiple strategies
    let matchingFile = null;

    // Strategy 1: Match by slug
    matchingFile = docxFiles.find(f => f.slug === page.slug);

    // Strategy 2: Match by normalized title
    if (!matchingFile) {
      const normalizeTitle = (title) => title.toLowerCase().replace(/[^a-z0-9]/g, '');
      const pageTitleNorm = normalizeTitle(page.title || '');
      matchingFile = docxFiles.find(f => {
        const fileTitleNorm = normalizeTitle(f.title);
        return pageTitleNorm === fileTitleNorm ||
               pageTitleNorm.includes(fileTitleNorm) ||
               fileTitleNorm.includes(pageTitleNorm);
      });
    }

    // Strategy 3: Match by box file_name
    if (!matchingFile && page.box?.file_name) {
      const normalizeFilename = (name) => name.toLowerCase().replace(/\.docx$/i, '').replace(/[^a-z0-9]/g, '');
      const boxFileNameNorm = normalizeFilename(page.box.file_name);
      matchingFile = docxFiles.find(f => {
        const fileNorm = normalizeFilename(f.filename);
        return boxFileNameNorm === fileNorm;
      });
    }

    // Strategy 4: For sections, try to match by section number and module from Box folder
    if (!matchingFile && page.metadata?.type === 'section' && page.box?.folder_id) {
      // Look for files in section folders that might match
      // This is a fallback - we'll use hierarchy from matching based on section number
    }

    if (matchingFile && matchingFile.hierarchy) {
      // Update hierarchy from filesystem
      page.hierarchy = matchingFile.hierarchy;

      // For sections, ensure we have full module info
      if (page.metadata?.type === 'section' && matchingFile.hierarchy.module && matchingFile.hierarchy.section) {
        // Find the module page to get full module details
        const modulePage = courseMap.pages.find(p =>
          p.metadata?.type === 'module' &&
          p.hierarchy?.module?.number === matchingFile.hierarchy.module.number
        );
        if (modulePage && modulePage.hierarchy?.module) {
          page.hierarchy.module = {
            number: modulePage.hierarchy.module.number,
            id: modulePage.id,
            title: modulePage.title,
            folder_id: modulePage.box?.folder_id,
            folder_name: modulePage.hierarchy.module.folder_name
          };
        } else {
          // Use what we have from filesystem
          page.hierarchy.module = {
            number: matchingFile.hierarchy.module.number,
            folder_name: matchingFile.hierarchy.module.folder_name
          };
        }
      }
    } else {
      // Try to determine hierarchy from existing metadata
      if (!page.hierarchy) {
        page.hierarchy = {
          module: null,
          section: null,
          la: null
        };
      }

      // If it's a module page
      if (page.metadata?.type === 'module') {
        const moduleMatch = page.title.match(/Module\s+(\d+)/i);
        if (moduleMatch) {
          const moduleNum = parseInt(moduleMatch[1], 10);
          page.hierarchy.module = {
            number: moduleNum,
            id: page.id,
            title: page.title,
            folder_id: page.box?.folder_id,
            folder_name: `Module-${moduleNum}`
          };
        }
      }

      // If it's a section page, try to extract module from Box folder_id name
      // Sections are in folders like "Section-1-1" where first number is module
      if (page.metadata?.type === 'section' && page.box?.folder_id) {
        // We can't easily determine from Box folder_id alone without API call
        // But we can try to match by finding a DOCX file with similar name
        const sectionMatch = page.title.match(/Section\s+(\d+)/i);
        if (sectionMatch) {
          const sectionNum = parseInt(sectionMatch[1], 10);
          page.hierarchy.section = {
            number: sectionNum,
            id: page.id,
            title: page.title,
            folder_id: page.box?.folder_id
          };
        }
      }
    }
  }

  // Update metadata
  courseMap.metadata.last_updated = new Date().toISOString();

  // Write back to file
  console.log('\n💾 Writing updated course-map.json...');
  writeFileSync(COURSE_MAP_PATH, JSON.stringify(courseMap, null, 2), 'utf8');

  console.log('✅ Hierarchy mapping complete!');

  // Print summary
  console.log('\n📊 Final Summary:');
  const withModule = courseMap.pages.filter(p => p.hierarchy?.module).length;
  const withSection = courseMap.pages.filter(p => p.hierarchy?.section).length;
  const withLA = courseMap.pages.filter(p => p.hierarchy?.la).length;
  console.log(`  Pages with module: ${withModule}`);
  console.log(`  Pages with section: ${withSection}`);
  console.log(`  Pages with LA: ${withLA}`);
  console.log(`  Total pages: ${courseMap.pages.length}`);
  console.log(`\n⚠️  Note: ${docxFiles.length} DOCX files found, but only ${courseMap.pages.length} pages in course-map.json`);
  console.log(`    Consider running a discovery script to add missing pages.`);
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

