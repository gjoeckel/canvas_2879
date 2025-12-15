#!/usr/bin/env node
/**
 * Map module > section > LA hierarchy using local filesystem structure
 *
 * This script:
 * 1. Reads the local filesystem structure (Module-X/Section-X-Y/LA-X-Y-Z)
 * 2. Maps each page in course-map.json to its module/section/LA position
 * 3. Updates course-map.json with hierarchy information
 */

import { readFileSync, writeFileSync, readdirSync, statSync } from 'fs';
import { join, dirname, basename } from 'path';
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
 * Extract module number from page title/id
 */
function extractModuleFromTitle(title) {
  const match = title.match(/Module\s+(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Extract section number from page title/id
 */
function extractSectionFromTitle(title) {
  const match = title.match(/Section\s+(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

/**
 * Build a map of folder structure
 */
function buildFolderMap() {
  const folderMap = {
    modules: new Map(), // moduleNum -> { folderName, sections: Map }
    sections: new Map(), // "module-section" -> { folderName, las: Map }
    las: new Map() // "module-section-la" -> { folderName }
  };

  try {
    const entries = readdirSync(BASE_DIR);

    for (const entry of entries) {
      const entryPath = join(BASE_DIR, entry);
      if (!statSync(entryPath).isDirectory()) continue;

      // Check for Module folders
      const moduleNum = extractModuleNumber(entry);
      if (moduleNum) {
        folderMap.modules.set(moduleNum, {
          folderName: entry,
          sections: new Map()
        });

        // Read sections within this module
        try {
          const sectionEntries = readdirSync(entryPath);
          for (const sectionEntry of sectionEntries) {
            const sectionPath = join(entryPath, sectionEntry);
            if (!statSync(sectionPath).isDirectory()) continue;

            const sectionNums = extractSectionNumbers(sectionEntry);
            if (sectionNums && sectionNums.module === moduleNum) {
              const key = `${moduleNum}-${sectionNums.section}`;
              folderMap.sections.set(key, {
                folderName: sectionEntry,
                module: moduleNum,
                section: sectionNums.section,
                las: new Map()
              });

              // Read LAs within this section
              try {
                const laEntries = readdirSync(sectionPath);
                for (const laEntry of laEntries) {
                  const laPath = join(sectionPath, laEntry);
                  if (!statSync(laPath).isDirectory()) continue;

                  const laNums = extractLANumbers(laEntry);
                  if (laNums && laNums.module === moduleNum && laNums.section === sectionNums.section) {
                    const laKey = `${moduleNum}-${sectionNums.section}-${laNums.la}`;
                    folderMap.las.set(laKey, {
                      folderName: laEntry,
                      module: moduleNum,
                      section: sectionNums.section,
                      la: laNums.la
                    });
                  }
                }
              } catch (err) {
                // Ignore errors reading LA folders
              }
            }
          }
        } catch (err) {
          // Ignore errors reading section folders
        }
      }
    }
  } catch (err) {
    console.error('Error building folder map:', err);
  }

  return folderMap;
}

/**
 * Determine hierarchy for a page
 */
function determineHierarchy(page, folderMap) {
  const hierarchy = {
    module: null,
    section: null,
    la: null
  };

  // If it's a module page
  if (page.metadata?.type === 'module') {
    const moduleNum = extractModuleFromTitle(page.title || page.id);
    if (moduleNum && folderMap.modules.has(moduleNum)) {
      const moduleInfo = folderMap.modules.get(moduleNum);
      hierarchy.module = {
        number: moduleNum,
        id: page.id,
        title: page.title,
        folder_id: page.box?.folder_id,
        folder_name: moduleInfo.folderName
      };
    }
    return hierarchy;
  }

  // If it's a section page
  if (page.metadata?.type === 'section') {
    // Try to extract from Box folder_id if available (Section-X-Y format)
    if (page.box?.folder_id) {
      // We'll need to match by checking if the page slug/title matches a section
      // For now, try to extract module and section from title
      const moduleNum = extractModuleFromTitle(page.title || page.id);
      const sectionNum = extractSectionFromTitle(page.title || page.id);

      // Try to find matching section in folder map
      if (moduleNum && sectionNum) {
        const sectionKey = `${moduleNum}-${sectionNum}`;
        if (folderMap.sections.has(sectionKey)) {
          const sectionInfo = folderMap.sections.get(sectionKey);
          hierarchy.module = {
            number: moduleNum,
            folder_name: `Module-${moduleNum}`
          };
          hierarchy.section = {
            number: sectionNum,
            id: page.id,
            title: page.title,
            folder_id: page.box?.folder_id,
            folder_name: sectionInfo.folderName
          };
        }
      }
    }
    return hierarchy;
  }

  // TODO: Handle LA pages
  // For now, sections are the main focus

  return hierarchy;
}

/**
 * Main function
 */
async function main() {
  console.log('📁 Building folder structure map from filesystem...');
  const folderMap = buildFolderMap();

  console.log(`\n📊 Found:`);
  console.log(`  Modules: ${folderMap.modules.size}`);
  console.log(`  Sections: ${folderMap.sections.size}`);
  console.log(`  LAs: ${folderMap.las.size}`);

  console.log('\n📖 Reading course-map.json...');
  const courseMap = JSON.parse(readFileSync(COURSE_MAP_PATH, 'utf8'));

  console.log(`\n🔍 Mapping hierarchy for ${courseMap.pages.length} pages...`);

  // Process each page
  for (let i = 0; i < courseMap.pages.length; i++) {
    const page = courseMap.pages[i];
    const hierarchy = determineHierarchy(page, folderMap);

    // Add hierarchy to page
    if (!page.hierarchy) {
      page.hierarchy = {};
    }
    page.hierarchy = hierarchy;
  }

  // Update metadata
  courseMap.metadata.last_updated = new Date().toISOString();

  // Write back to file
  console.log('\n💾 Writing updated course-map.json...');
  writeFileSync(COURSE_MAP_PATH, JSON.stringify(courseMap, null, 2), 'utf8');

  console.log('✅ Hierarchy mapping complete!');

  // Print summary
  console.log('\n📊 Summary:');
  const modules = courseMap.pages.filter(p => p.hierarchy?.module);
  const sections = courseMap.pages.filter(p => p.hierarchy?.section);
  console.log(`  Pages with module: ${modules.length}`);
  console.log(`  Pages with section: ${sections.length}`);
  console.log(`  Total pages: ${courseMap.pages.length}`);
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

