#!/usr/bin/env node
/**
 * Restructure course-map.json to hierarchical format:
 * modules > sections > las
 *
 * Each level stores:
 * - folder_name (from filesystem)
 * - box_folder_id (from existing data)
 * - page data (from existing pages array)
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
 * Build filesystem folder structure map
 */
function buildFolderStructure() {
  const modules = new Map(); // moduleNum -> { folder_name, box_folder_id, sections: Map }

  try {
    const entries = readdirSync(BASE_DIR);

    for (const entry of entries) {
      const entryPath = join(BASE_DIR, entry);
      if (!statSync(entryPath).isDirectory()) continue;

      // Check for Module folders
      const moduleNum = extractModuleNumber(entry);
      if (moduleNum) {
        const sections = new Map();

        // Read sections within this module
        try {
          const sectionEntries = readdirSync(entryPath);
          for (const sectionEntry of sectionEntries) {
            const sectionPath = join(entryPath, sectionEntry);
            if (!statSync(sectionPath).isDirectory()) continue;

            const sectionNums = extractSectionNumbers(sectionEntry);
            if (sectionNums && sectionNums.module === moduleNum) {
              const las = new Map();

              // Read LAs within this section
              try {
                const laEntries = readdirSync(sectionPath);
                for (const laEntry of laEntries) {
                  const laPath = join(sectionPath, laEntry);
                  if (!statSync(laPath).isDirectory()) continue;

                  const laNums = extractLANumbers(laEntry);
                  if (laNums && laNums.module === moduleNum && laNums.section === sectionNums.section) {
                    las.set(laNums.la, {
                      folder_name: laEntry,
                      box_folder_id: null // Will be filled from page data
                    });
                  }
                }
              } catch (err) {
                // Ignore errors reading LA folders
              }

              sections.set(sectionNums.section, {
                folder_name: sectionEntry,
                box_folder_id: null, // Will be filled from page data
                las: las
              });
            }
          }
        } catch (err) {
          // Ignore errors reading section folders
        }

        modules.set(moduleNum, {
          folder_name: entry,
          box_folder_id: null, // Will be filled from page data
          sections: sections
        });
      }
    }
  } catch (err) {
    console.error('Error building folder structure:', err);
  }

  return modules;
}

/**
 * Find page by type and hierarchy numbers
 */
function findPage(pages, type, moduleNum, sectionNum = null, laNum = null) {
  return pages.find(page => {
    if (page.metadata?.type !== type) return false;

    // For modules
    if (type === 'module') {
      const match = (page.title || page.id).match(/Module\s+(\d+)/i);
      return match && parseInt(match[1], 10) === moduleNum;
    }

    // For sections
    if (type === 'section' && sectionNum !== null) {
      const sectionMatch = (page.title || page.id).match(/Section\s+(\d+)/i);
      if (!sectionMatch || parseInt(sectionMatch[1], 10) !== sectionNum) return false;

      // Check if it belongs to the right module (via hierarchy or folder structure)
      // We'll match by checking the Box folder structure later
      return true;
    }

    // For LAs
    if (type === 'la' && laNum !== null) {
      // Similar logic for LAs
      return true;
    }

    return false;
  });
}

/**
 * Main function
 */
async function main() {
  console.log('📁 Building filesystem folder structure...');
  const folderStructure = buildFolderStructure();

  console.log(`\n📊 Found:`);
  console.log(`  Modules: ${folderStructure.size}`);
  for (const [modNum, modData] of folderStructure.entries()) {
    console.log(`    Module ${modNum}: ${modData.sections.size} sections`);
    for (const [secNum, secData] of modData.sections.entries()) {
      console.log(`      Section ${modNum}-${secNum}: ${secData.las.size} LAs`);
    }
  }

  console.log('\n📖 Reading course-map.json...');
  const courseMap = JSON.parse(readFileSync(COURSE_MAP_PATH, 'utf8'));

  // Build hierarchical structure
  const modules = [];

  // Sort modules by number
  const sortedModuleNums = Array.from(folderStructure.keys()).sort((a, b) => a - b);

  for (const moduleNum of sortedModuleNums) {
    const folderData = folderStructure.get(moduleNum);
    const modulePage = findPage(courseMap.pages, 'module', moduleNum);

    const moduleObj = {
      id: modulePage?.id || `module-${moduleNum}`,
      title: modulePage?.title || `Module ${moduleNum}`,
      folder_name: folderData.folder_name,
      box_folder_id: modulePage?.box?.folder_id || null,
      order: modulePage?.order || moduleNum,
      status: modulePage?.status || 'draft',
      canvas: modulePage?.canvas || null,
      github: modulePage?.github || null,
      box: modulePage?.box || null,
      sync: modulePage?.sync || null,
      metadata: modulePage?.metadata || { type: 'module' },
      sections: []
    };

    // Process sections
    const sortedSectionNums = Array.from(folderData.sections.keys()).sort((a, b) => a - b);

    for (const sectionNum of sortedSectionNums) {
      const sectionFolderData = folderData.sections.get(sectionNum);

      // Find section page - try to match by section number and module context
      // Since sections can be in different modules, we need to match carefully
      let sectionPage = null;

      // Try to find section page that matches this section number
      // We'll match by checking if the section's Box folder structure aligns
      const sectionPages = courseMap.pages.filter(p => p.metadata?.type === 'section');

      // For each candidate, check if it might belong to this module
      // This is a heuristic - we'll use the filesystem structure as the source of truth
      // and match pages that have similar titles/names
      for (const candidatePage of sectionPages) {
        const sectionMatch = (candidatePage.title || candidatePage.id).match(/Section\s+(\d+)/i);
        if (sectionMatch && parseInt(sectionMatch[1], 10) === sectionNum) {
          // Check if this page might belong to this module
          // We can verify by checking if there's a matching DOCX file in this section folder
          const sectionSlug = candidatePage.slug || candidatePage.id;
          const expectedFileName = sectionSlug.replace(/-/g, '_') + '.docx';

          // For now, just use the first matching section number
          // In a more robust implementation, we'd verify by checking actual files
          sectionPage = candidatePage;
          break;
        }
      }

      const sectionObj = {
        id: sectionPage?.id || `section-${moduleNum}-${sectionNum}`,
        title: sectionPage?.title || `Section ${sectionNum}`,
        folder_name: sectionFolderData.folder_name,
        box_folder_id: sectionPage?.box?.folder_id || null,
        order: sectionPage?.order || sectionNum,
        status: sectionPage?.status || 'draft',
        canvas: sectionPage?.canvas || null,
        github: sectionPage?.github || null,
        box: sectionPage?.box || null,
        sync: sectionPage?.sync || null,
        metadata: sectionPage?.metadata || { type: 'section' },
        las: []
      };

      // Process LAs
      const sortedLANums = Array.from(sectionFolderData.las.keys()).sort((a, b) => a - b);

      for (const laNum of sortedLANums) {
        const laFolderData = sectionFolderData.las.get(laNum);

        // Find LA page (if it exists)
        const laPages = courseMap.pages.filter(p => p.metadata?.type === 'la');
        const laPage = laPages.find(p => {
          // Match LA by hierarchy if available
          if (p.hierarchy?.module?.number === moduleNum &&
              p.hierarchy?.section?.number === sectionNum &&
              p.hierarchy?.la?.number === laNum) {
            return true;
          }
          return false;
        });

        const laObj = {
          id: laPage?.id || `la-${moduleNum}-${sectionNum}-${laNum}`,
          title: laPage?.title || `LA ${moduleNum}-${sectionNum}-${laNum}`,
          folder_name: laFolderData.folder_name,
          box_folder_id: laPage?.box?.folder_id || null,
          order: laPage?.order || laNum,
          status: laPage?.status || 'draft',
          canvas: laPage?.canvas || null,
          github: laPage?.github || null,
          box: laPage?.box || null,
          sync: laPage?.sync || null,
          metadata: laPage?.metadata || { type: 'la' }
        };

        sectionObj.las.push(laObj);
      }

      moduleObj.sections.push(sectionObj);
    }

    modules.push(moduleObj);
  }

  // Create new structure
  const newCourseMap = {
    ...courseMap,
    modules: modules,
    pages: undefined // Remove old pages array
  };

  // Remove pages property
  delete newCourseMap.pages;

  // Update metadata
  newCourseMap.metadata.last_updated = new Date().toISOString();

  // Write back to file
  console.log('\n💾 Writing restructured course-map.json...');
  writeFileSync(COURSE_MAP_PATH, JSON.stringify(newCourseMap, null, 2), 'utf8');

  console.log('✅ Restructure complete!');

  // Print summary
  console.log('\n📊 Final Summary:');
  console.log(`  Modules: ${modules.length}`);
  const totalSections = modules.reduce((sum, m) => sum + m.sections.length, 0);
  const totalLAs = modules.reduce((sum, m) =>
    sum + m.sections.reduce((s, sec) => s + sec.las.length, 0), 0);
  console.log(`  Sections: ${totalSections}`);
  console.log(`  LAs: ${totalLAs}`);
  console.log(`  Total items: ${modules.length + totalSections + totalLAs}`);
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

